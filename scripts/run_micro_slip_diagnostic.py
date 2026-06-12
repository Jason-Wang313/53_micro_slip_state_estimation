import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FIGS = ROOT / "paper" / "figures"
OUT = DOCS / "micro_slip_diagnostic.csv"
TXT = DOCS / "micro_slip_diagnostic_summary.txt"

def kalman_step(mu, var, y, a=1.0, q=0.02, r=0.08):
    # One-dimensional latent-slip filter.
    pred_mu = mu
    pred_var = var + q
    k = pred_var * a / (a * a * pred_var + r)
    mu2 = pred_mu + k * (y - a * pred_mu)
    var2 = (1 - k * a) * pred_var
    return mu2, var2

def simulate(seed=7, n=600):
    random.seed(seed)
    rows = []
    mu = 0.0
    var = 0.5
    latent = 0.0
    detector_score = 0.0
    latent_regret = 0.0
    threshold_regret = 0.0
    for t in range(n):
        # Micro-slip grows when commanded force is too low and friction drifts.
        friction = 0.55 + 0.15 * math.sin(t / 47.0) + random.gauss(0, 0.03)
        command = 0.7 + 0.12 * math.sin(t / 19.0)
        latent = max(0.0, 0.82 * latent + 0.3 * (friction - command) + random.gauss(0, 0.025))
        tactile = 1.6 * latent + 0.35 * friction + random.gauss(0, 0.12)
        force = command + random.gauss(0, 0.04)
        mu, var = kalman_step(mu, var, tactile)
        detector = 1.0 if tactile > 0.55 else 0.0
        est_action = 0.64 + 0.55 * mu
        # Binary detection reacts too late and then over-corrects.
        thresh_action = 0.64 + 0.88 * detector
        target = 0.64 + 0.55 * latent
        # Regret is the squared gap to the ideal stabilizing action.
        latent_regret += (est_action - target) ** 2
        threshold_regret += (thresh_action - target) ** 2
        detector_score += detector
        rows.append({
            "t": t,
            "friction": friction,
            "command": command,
            "latent_slip": latent,
            "tactile": tactile,
            "force": force,
            "latent_est": mu,
            "detector": detector,
            "target_action": target,
            "latent_action": est_action,
            "threshold_action": thresh_action,
        })
    return rows, latent_regret / n, threshold_regret / n, detector_score / n

def main():
    DOCS.mkdir(exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    rows, latent_err, thresh_err, avg_det = simulate()
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    TXT.write_text(
        "\n".join([
            f"rows={len(rows)}",
            f"latent_policy_mse={latent_err:.5f}",
            f"threshold_policy_mse={thresh_err:.5f}",
            f"avg_detector_activation={avg_det:.5f}",
        ]),
        encoding="utf-8",
    )
    try:
        import matplotlib.pyplot as plt
        ts = [r["t"] for r in rows]
        latent = [r["latent_slip"] for r in rows]
        est = [r["latent_est"] for r in rows]
        det = [r["detector"] for r in rows]
        targ = [r["target_action"] for r in rows]
        latact = [r["latent_action"] for r in rows]
        thact = [r["threshold_action"] for r in rows]
        fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        ax[0].plot(ts, latent, label="true micro-slip", linewidth=2)
        ax[0].plot(ts, est, label="estimated latent slip", linewidth=2)
        ax[0].plot(ts, det, label="threshold detector", alpha=0.8)
        ax[0].set_ylabel("state / detector")
        ax[0].legend(loc="upper right")
        ax[1].plot(ts, targ, label="ideal stabilizing action", linewidth=2)
        ax[1].plot(ts, latact, label="latent-state policy", linewidth=2)
        ax[1].plot(ts, thact, label="threshold policy", alpha=0.8)
        ax[1].set_ylabel("control action")
        ax[1].set_xlabel("time step")
        ax[1].legend(loc="upper right")
        fig.tight_layout()
        fig.savefig(FIGS / "micro_slip_diagnostic.png", dpi=180)
    except Exception:
        pass

if __name__ == "__main__":
    main()
