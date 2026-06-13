import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPER = ROOT / "paper"
OUT_CSV = DOCS / "v2_tuned_baseline_stress_summary.csv"
OUT_JSON = DOCS / "v2_tuned_baseline_stress.json"
OUT_TEX = PAPER / "v2_tuned_baseline_table.tex"


def simulate(
    seed=7,
    n=600,
    tactile_gain=1.6,
    tactile_bias=0.0,
    tactile_noise=0.12,
    friction_term=0.35,
    phase=0.0,
):
    random.seed(seed)
    rows = []
    latent = 0.0
    for t in range(n):
        friction = 0.55 + 0.15 * math.sin((t + phase) / 47.0) + random.gauss(0, 0.03)
        command = 0.7 + 0.12 * math.sin((t + phase) / 19.0)
        latent = max(0.0, 0.82 * latent + 0.3 * (friction - command) + random.gauss(0, 0.025))
        tactile = tactile_bias + tactile_gain * latent + friction_term * friction + random.gauss(0, tactile_noise)
        target = 0.64 + 0.55 * latent
        rows.append(
            {
                "t": t,
                "friction": friction,
                "command": command,
                "latent_slip": latent,
                "tactile": tactile,
                "target_action": target,
            }
        )
    return rows


def mse(predictions, rows):
    return sum((p - r["target_action"]) ** 2 for p, r in zip(predictions, rows)) / len(rows)


def latent_filter_policy(rows, a=1.0, q=0.02, r=0.08):
    mu = 0.0
    var = 0.5
    predictions = []
    for row in rows:
        y = row["tactile"]
        pred_var = var + q
        k = pred_var * a / (a * a * pred_var + r)
        mu = mu + k * (y - a * mu)
        var = (1 - k * a) * pred_var
        predictions.append(0.64 + 0.55 * mu)
    return predictions


def constant_policy(rows, action):
    return [action for _ in rows]


def fit_constant(rows):
    return sum(r["target_action"] for r in rows) / len(rows)


def fit_threshold(rows):
    values = [r["tactile"] for r in rows]
    lo, hi = min(values), max(values)
    best = (float("inf"), None)
    for i in range(25):
        threshold = lo + (hi - lo) * i / 24.0
        for gain_step in range(0, 101, 2):
            gain = gain_step / 100.0
            predictions = [0.64 + gain * (1.0 if r["tactile"] > threshold else 0.0) for r in rows]
            score = mse(predictions, rows)
            if score < best[0]:
                best = (score, (threshold, gain))
    return best[1]


def threshold_policy(rows, params):
    threshold, gain = params
    return [0.64 + gain * (1.0 if r["tactile"] > threshold else 0.0) for r in rows]


def tactile_series(rows, beta=None):
    if beta is None:
        return [r["tactile"] for r in rows]
    ema = 0.0
    values = []
    for row in rows:
        ema = beta * ema + (1 - beta) * row["tactile"]
        values.append(ema)
    return values


def fit_linear(xs, ys):
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denom = sum((x - mean_x) ** 2 for x in xs)
    slope = 0.0 if denom == 0.0 else sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
    intercept = mean_y - slope * mean_x
    return intercept, slope


def linear_policy(rows, params, beta=None):
    intercept, slope = params
    return [intercept + slope * x for x in tactile_series(rows, beta=beta)]


def train_rows():
    rows = []
    for seed in range(100, 108):
        rows.extend(simulate(seed=seed))
    return rows


def eval_rows(scenario):
    rows = []
    for seed in range(200, 206):
        rows.extend(simulate(seed=seed, **scenario["kwargs"]))
    return rows


def main():
    DOCS.mkdir(exist_ok=True)
    PAPER.mkdir(exist_ok=True)
    train = train_rows()
    train_targets = [r["target_action"] for r in train]

    constant_action = fit_constant(train)
    threshold_params = fit_threshold(train)
    raw_params = fit_linear(tactile_series(train), train_targets)

    best_ema = (float("inf"), None, None)
    for beta in [0.0, 0.25, 0.5, 0.7, 0.85, 0.95]:
        params = fit_linear(tactile_series(train, beta=beta), train_targets)
        score = mse(linear_policy(train, params, beta=beta), train)
        if score < best_ema[0]:
            best_ema = (score, beta, params)

    scenarios = [
        {"name": "matched_generator", "kwargs": {}},
        {"name": "low_tactile_gain", "kwargs": {"tactile_gain": 0.8}},
        {"name": "tactile_bias_shift", "kwargs": {"tactile_bias": 0.25}},
        {"name": "friction_confound", "kwargs": {"friction_term": 0.7}},
        {"name": "noisy_tactile", "kwargs": {"tactile_noise": 0.24}},
    ]

    results = []
    for scenario in scenarios:
        rows = eval_rows(scenario)
        scores = {
            "latent_filter_mse": mse(latent_filter_policy(rows), rows),
            "constant_hold_mse": mse(constant_policy(rows, constant_action), rows),
            "tuned_threshold_mse": mse(threshold_policy(rows, threshold_params), rows),
            "raw_tactile_linear_mse": mse(linear_policy(rows, raw_params), rows),
            "ema_tactile_linear_mse": mse(linear_policy(rows, best_ema[2], beta=best_ema[1]), rows),
        }
        best_name = min(scores, key=scores.get)
        results.append(
            {
                "scenario": scenario["name"],
                **scores,
                "best_baseline": best_name,
                "latent_filter_minus_best": scores["latent_filter_mse"] - scores[best_name],
            }
        )

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    OUT_JSON.write_text(
        json.dumps(
            {
                "decision": "kill/archive",
                "reason": "The original latent-filter result collapses against tuned constant, threshold, and tactile-smoothing baselines.",
                "training": {
                    "seeds": list(range(100, 108)),
                    "constant_action": constant_action,
                    "threshold": threshold_params[0],
                    "threshold_gain": threshold_params[1],
                    "raw_tactile_linear": raw_params,
                    "ema_beta": best_ema[1],
                    "ema_tactile_linear": best_ema[2],
                },
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    rows_for_table = [r for r in results if r["scenario"] in {"matched_generator", "tactile_bias_shift", "friction_confound"}]
    OUT_TEX.write_text(
        "\n".join(
            [
                r"\begin{tabular}{lrrrr}",
                r"\toprule",
                r"Scenario & Latent filter & Constant hold & Tuned threshold & EMA tactile \\",
                r"\midrule",
                *[
                    (
                        f"{r['scenario'].replace('_', ' ')} & "
                        f"{r['latent_filter_mse']:.5f} & "
                        f"{r['constant_hold_mse']:.5f} & "
                        f"{r['tuned_threshold_mse']:.5f} & "
                        f"{r['ema_tactile_linear_mse']:.5f} \\\\"
                    )
                    for r in rows_for_table
                ],
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for r in results:
        print(
            r["scenario"],
            f"latent={r['latent_filter_mse']:.5f}",
            f"constant={r['constant_hold_mse']:.5f}",
            f"threshold={r['tuned_threshold_mse']:.5f}",
            f"ema={r['ema_tactile_linear_mse']:.5f}",
            f"best={r['best_baseline']}",
        )


if __name__ == "__main__":
    main()
