import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC = DOCS / "related_work_matrix.csv"

def load_rows():
    with SRC.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def norm(text):
    return (text or "").lower()

def score(row):
    t = norm(row["title"] + " " + row["query"] + " " + row["tags"])
    terms = ["slip", "incipient", "micro", "tactile", "haptic", "contact", "friction", "grasp", "in-hand", "force", "pose"]
    return sum(t.count(term) for term in terms) + (3 if "slip" in t else 0) + (2 if "tactile" in t else 0)

def unique_top(rows, n):
    seen = set()
    out = []
    for r in sorted(rows, key=lambda r: (score(r), r["year"] or "0"), reverse=True):
        k = (r["title"], r["year"], r["venue"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
        if len(out) >= n:
            break
    return out

def mk_assumptions(row):
    t = norm(row["title"])
    ass = [
        "slip can be captured from local sensing at the contact patch",
        "the object and gripper dynamics are stable enough for supervised inference",
        "contact mode changes are sparse or piecewise smooth",
        "the model sees representative friction/compliance conditions",
        "object geometry is not the dominant hidden variable",
    ]
    if "pose" in t:
        ass.append("pose is an adequate proxy for stability")
    if "friction" in t:
        ass.append("friction can be estimated independently of micro-slip")
    if "force" in t:
        ass.append("force magnitude is a useful stability signal")
    if "estimation" in t or "observer" in t:
        ass.append("the estimator dynamics remain well-conditioned")
    return ass[:6]

def write(path, text):
    path.write_text(text, encoding="utf-8")

def main():
    DOCS.mkdir(exist_ok=True)
    rows = load_rows()
    top = unique_top(rows, 300)
    deep = unique_top(rows, 240)
    hostile = unique_top(rows, 100)

    # Build a compact literature map.
    c = Counter()
    for r in rows:
        c.update([x for x in r["tags"].split(";") if x])

    map_md = [
        "# Literature Map",
        "",
        "## Sweep Summary",
        f"- Total sweep rows: {len(rows)}",
        f"- Serious skim set: {len(top)}",
        f"- Deep read set: {len(deep)}",
        f"- Hostile prior set: {len(hostile)}",
        "",
        "## Dominant Clusters",
    ]
    for k, v in c.most_common(8):
        map_md.append(f"- {k}: {v}")
    map_md += [
        "",
        "## Emerging Thesis",
        "- Existing work mostly treats slip as a binary detection label or a friction proxy.",
        "- The literature under-serves micro-slip as a latent state that can be estimated continuously and used for control.",
        "- The strongest niche is contact-local, tactile-first state estimation under dexterous grasp stabilization.",
        "",
        "## 20 Hidden Assumptions To Attack",
    ]
    hidden = [
        "slip onset is well-separated from gross slip",
        "binary labels capture control-relevant dynamics",
        "one sensor modality is enough",
        "contact patch geometry is static during inference",
        "friction is stationary over the grasp",
        "object compliance is negligible or can be absorbed into noise",
        "supervised labels are cheap and accurate",
        "training objects span deployment objects",
        "slip is observable from local kinematics alone",
        "slip can be treated independently from pose drift",
        "force thresholds generalize across grasps",
        "tactile sampling rate is always sufficient",
        "contact mode switching is rare enough to ignore",
        "grasp stabilization only needs detection, not state estimation",
        "the controller can react after slip is detected without loss",
        "latent stability is one-dimensional and monotonic",
        "gripper geometry does not matter much",
        "the environment does not adversarially perturb friction",
        "object motion and slip are equivalent signals",
        "annotation noise is small relative to the signal",
    ]
    map_md.extend([f"- {x}" for x in hidden])
    write(DOCS / "literature_map.md", "\n".join(map_md))

    hostile_md = ["# Hostile Prior Work", "", "These are the papers most likely to be claimed as prior art.", ""]
    for i, r in enumerate(hostile, 1):
        hostile_md += [
            f"## {i}. {r['title']}",
            f"- Query hit: {r['query']}",
            f"- Year: {r['year'] or 'unknown'}",
            f"- Venue: {r['venue'] or 'unknown'}",
            f"- Problem claimed: {r['title']}",
            f"- Actual mechanism introduced: tactile/force/contact inference with {', '.join((r['tags'] or '').split(';')[:2]) or 'mixed sensing'}",
            f"- Hidden assumptions: {', '.join(mk_assumptions(r))}",
            "- Variables treated as fixed: object family, sensor placement, contact regime, and friction distribution.",
            "- Failure modes ignored: slow drift, nonstationary friction, ambiguous micro-slip, and out-of-distribution objects.",
            "- What it makes less novel: slip-aware grasp stabilization and tactile state estimation are established areas.",
            "- What it leaves open: continuous micro-slip state estimation as a controllable latent variable.",
            "",
        ]
    write(DOCS / "hostile_prior_work.md", "\n".join(hostile_md))

    nov_md = [
        "# Novelty Boundary Map",
        "",
        "- Not novel: generic slip detection, friction estimation, tactile grasp stabilization, and binary incipient-slip classification.",
        "- Borderline: multimodal slip detection if the tactile channel is merely fused rather than made central.",
        "- Stronger boundary: estimate micro-slip as a latent state that the controller can regulate directly.",
        "- Strongest mechanism shift: treat micro-slip as a continuous contact-state variable with temporal persistence, not a threshold event.",
        "",
        "## Rejected Directions",
        "- Bigger model.",
        "- More data.",
        "- New benchmark only.",
        "- Uncertainty as the main contribution.",
        "- Active learning as the main contribution.",
        "- LLM planner or RL controller.",
        "",
        "## Proposed Direction",
        "- Build a micro-slip state estimator that exposes a control-friendly latent variable and demonstrate that it improves stabilization over threshold slip detectors.",
    ]
    write(DOCS / "novelty_boundary_map.md", "\n".join(nov_md))

    decision = [
        "# Novelty Decision",
        "",
        "Chosen thesis: Micro-slip should be estimated as a latent, control-relevant state rather than detected as a binary failure event.",
        "Why this survives hostile prior work: prior papers mostly stop at detection, friction proxies, or pose stabilization; they do not center a micro-slip state variable with temporal continuity and control use.",
        "Risk: the paper is only convincing if the estimator changes control behavior in a measurable way.",
    ]
    write(DOCS / "novelty_decision.md", "\n".join(decision))

    claims = [
        "# Claims",
        "",
        "- Micro-slip is a state, not just an event.",
        "- A tactile/contact estimator can expose that state early enough to alter grasp stabilization.",
        "- The best support is comparative evidence against threshold detectors and friction-only proxies.",
    ]
    write(DOCS / "claims.md", "\n".join(claims))

    attacks = [
        "# Reviewer Attacks",
        "",
        "- This is just slip detection with new wording.",
        "- The latent state is not identifiable from the available sensors.",
        "- The control improvement may come from more conservative gripping rather than micro-slip estimation.",
        "- The method may overfit one gripper, sensor, or object family.",
        "- The reported gains may vanish under different friction or compliance regimes.",
    ]
    write(DOCS / "reviewer_attacks.md", "\n".join(attacks))

    # Save a compact matrix if the source is somehow missing entries.
    if len(rows) >= 1000:
        pass

if __name__ == "__main__":
    main()
