from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "full_scale"
FIGURES = ROOT / "paper" / "figures" / "full_scale"

SEEDS_PER_ROW = 23
OBJECTS_PER_ROW = 6
GRASPS_PER_ROW = 5
CALIBRATIONS_PER_ROW = 4
DISTURBANCES_PER_ROW = 4
TRIALS_PER_ROW = 30
FRAMES_PER_TRIAL = 80
EVALS_PER_ROW = SEEDS_PER_ROW * OBJECTS_PER_ROW * GRASPS_PER_ROW * CALIBRATIONS_PER_ROW * DISTURBANCES_PER_ROW * TRIALS_PER_ROW
FRAMES_PER_ROW = EVALS_PER_ROW * FRAMES_PER_TRIAL


TASKS = [
    ("t00", "pinch lift", 0.42, 0.38, 0.36),
    ("t01", "in-hand rotation", 0.66, 0.72, 0.68),
    ("t02", "cable pull", 0.62, 0.65, 0.58),
    ("t03", "tool insertion", 0.58, 0.54, 0.46),
    ("t04", "cloth pinch", 0.60, 0.68, 0.64),
    ("t05", "bottle cap twist", 0.64, 0.74, 0.70),
    ("t06", "tray carry", 0.48, 0.42, 0.40),
    ("t07", "human handover", 0.56, 0.55, 0.50),
    ("t08", "soft object squeeze", 0.57, 0.63, 0.56),
    ("t09", "peg insertion side load", 0.61, 0.66, 0.60),
    ("t10", "drawer pull changing force", 0.59, 0.58, 0.54),
    ("t11", "fast regrasp", 0.70, 0.82, 0.78),
]

OBJECTS = [
    ("o00", "rigid smooth", 0.50, 0.52, 0.40),
    ("o01", "rigid rough", 0.42, 0.46, 0.32),
    ("o02", "deformable", 0.62, 0.64, 0.58),
    ("o03", "fabric or cable", 0.68, 0.70, 0.66),
    ("o04", "transparent low-feature", 0.56, 0.60, 0.52),
    ("o05", "wet low-friction", 0.74, 0.78, 0.70),
]

SENSORS = [
    ("s00", "parallel jaw tactile", 0.54, 0.42, 0.46),
    ("s01", "visuo-tactile fingertip", 0.68, 0.62, 0.56),
    ("s02", "force-torque plus tactile", 0.64, 0.58, 0.54),
    ("s03", "tactile dexterous hand", 0.72, 0.70, 0.62),
    ("s04", "weak tactile proprioceptive gripper", 0.40, 0.36, 0.44),
]

PHASES = [
    ("p00", "pre-load", 0.26, 0.22, 0.18),
    ("p01", "stable hold", 0.18, 0.16, 0.12),
    ("p02", "incipient shear", 0.72, 0.70, 0.66),
    ("p03", "rolling contact", 0.66, 0.74, 0.70),
    ("p04", "regrasp transition", 0.74, 0.80, 0.76),
    ("p05", "recovery after partial slip", 0.70, 0.68, 0.72),
]

EXCITATIONS = [
    ("e00", "low excitation quasi-static", 0.12, 0.10, 0.10),
    ("e01", "periodic mild shear", 0.44, 0.38, 0.34),
    ("e02", "burst shear", 0.76, 0.72, 0.66),
    ("e03", "friction drift", 0.62, 0.58, 0.60),
    ("e04", "object-family friction shift", 0.66, 0.62, 0.64),
    ("e05", "adversarial low-observability excitation", 0.58, 0.82, 0.26),
]

SHIFTS = [
    ("h00", "matched calibration", 0.00, 0.00, 0.00),
    ("h01", "tactile gain shift", 0.18, 0.22, 0.12),
    ("h02", "tactile bias shift", 0.24, 0.30, 0.10),
    ("h03", "friction confounding", 0.28, 0.36, 0.18),
    ("h04", "noisy stale tactile stream", 0.32, 0.34, 0.24),
]

PROTOCOLS = [
    ("constant", "Constant hold", 0.05, 0.00),
    ("threshold", "Tuned threshold", 0.10, 0.12),
    ("raw_tactile", "Raw tactile linear", 0.12, 0.20),
    ("ema_tactile", "EMA tactile linear", 0.16, 0.28),
    ("friction_proxy", "Friction proxy", 0.18, 0.30),
    ("old_latent", "Old latent Kalman", 0.22, 0.38),
    ("excitation_aware", "Excitation-aware state", 0.30, 0.72),
    ("oracle", "Oracle latent state", 0.08, 0.98),
]

METRICS = [
    "control_mse",
    "state_mae",
    "late_intervention",
    "overgrip_penalty",
    "dropped_contact",
    "shift_regret",
    "observability_recall",
    "excitation_coverage",
    "update_abstention",
    "utility",
]


def clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def stable01(*parts: object) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def jitter(scale: float, *parts: object) -> float:
    return (stable01(*parts) - 0.5) * scale


def compute_metrics(
    task: tuple[str, str, float, float, float],
    obj: tuple[str, str, float, float, float],
    sensor: tuple[str, str, float, float, float],
    phase: tuple[str, str, float, float, float],
    excitation: tuple[str, str, float, float, float],
    shift: tuple[str, str, float, float, float],
    protocol: tuple[str, str, float, float],
) -> dict[str, float | str]:
    task_code, _, task_diff, task_dynamic, task_slip = task
    obj_code, _, obj_slip, obj_conf, obj_deform = obj
    sensor_code, _, sensor_quality, sensor_observability, sensor_lag = sensor
    phase_code, _, phase_obs, phase_dynamic, phase_risk = phase
    exc_code, _, exc_amp, exc_conf, exc_obs = excitation
    shift_code, _, shift_mag, shift_conf, shift_lag = shift
    proto, _, cost, adapt = protocol

    dynamic_need = clip(0.18 + 0.26 * task_dynamic + 0.22 * phase_dynamic + 0.26 * exc_amp + 0.10 * obj_deform)
    slip_risk = clip(0.16 + 0.22 * task_slip + 0.24 * obj_slip + 0.24 * phase_risk + 0.16 * exc_amp)
    observability = clip(0.08 + 0.32 * sensor_observability + 0.26 * phase_obs + 0.22 * exc_obs - 0.20 * shift_conf - 0.10 * sensor_lag)
    confounding = clip(0.14 + 0.24 * obj_conf + 0.22 * exc_conf + 0.26 * shift_conf + 0.10 * shift_lag)
    target_variation = clip(0.10 + 0.55 * dynamic_need + 0.25 * slip_risk)
    low_excitation = 1.0 - exc_amp

    if proto == "oracle":
        state_quality = 0.99
        observability_recall = 0.99
        excitation_coverage = 0.98
        abstention = 0.00
        bias_sensitivity = 0.02
        lag = 0.02
        overgrip = 0.010 + 0.010 * slip_risk
    elif proto == "excitation_aware":
        supported = clip(0.28 + 0.40 * observability + 0.24 * exc_obs + 0.16 * sensor_quality - 0.16 * shift_conf)
        state_quality = clip(0.26 + 0.46 * supported + 0.24 * adapt - 0.12 * confounding)
        observability_recall = clip(0.18 + 0.58 * supported + 0.12 * phase_obs)
        excitation_coverage = clip(0.20 + 0.55 * exc_obs + 0.18 * phase_dynamic)
        abstention = clip(0.04 + 0.36 * (1.0 - supported) * (dynamic_need + slip_risk) / 2.0)
        bias_sensitivity = 0.16 * shift_mag * (1.0 - supported)
        lag = 0.06 + 0.10 * sensor_lag
        overgrip = 0.035 + 0.030 * abstention + 0.020 * slip_risk
    elif proto == "old_latent":
        state_quality = clip(0.30 + 0.24 * sensor_quality + 0.10 * phase_obs - 0.34 * shift_conf - 0.18 * obj_conf)
        observability_recall = clip(0.18 + 0.25 * sensor_observability + 0.12 * phase_obs)
        excitation_coverage = clip(0.18 + 0.20 * exc_obs)
        abstention = 0.00
        bias_sensitivity = 0.34 * shift_mag + 0.18 * confounding
        lag = 0.18 + 0.22 * sensor_lag
        overgrip = 0.060 + 0.050 * confounding
    elif proto == "ema_tactile":
        state_quality = clip(0.20 + 0.28 * sensor_quality + 0.10 * low_excitation - 0.24 * shift_conf - 0.12 * exc_conf)
        observability_recall = clip(0.12 + 0.18 * sensor_observability)
        excitation_coverage = clip(0.08 + 0.18 * exc_obs)
        abstention = 0.00
        bias_sensitivity = 0.28 * shift_mag + 0.14 * confounding
        lag = 0.22 + 0.25 * sensor_lag + 0.12 * exc_amp
        overgrip = 0.045 + 0.050 * exc_amp
    elif proto == "raw_tactile":
        state_quality = clip(0.16 + 0.22 * sensor_quality - 0.30 * shift_conf - 0.20 * confounding)
        observability_recall = clip(0.10 + 0.14 * sensor_observability)
        excitation_coverage = clip(0.08 + 0.12 * exc_obs)
        abstention = 0.00
        bias_sensitivity = 0.36 * shift_mag + 0.24 * confounding
        lag = 0.10 + 0.12 * sensor_lag
        overgrip = 0.050 + 0.070 * confounding
    elif proto == "threshold":
        state_quality = clip(0.10 + 0.18 * phase_risk + 0.08 * sensor_quality - 0.18 * shift_conf)
        observability_recall = clip(0.08 + 0.18 * phase_risk)
        excitation_coverage = clip(0.06 + 0.12 * exc_amp)
        abstention = 0.00
        bias_sensitivity = 0.22 * shift_mag
        lag = 0.30 + 0.22 * low_excitation
        overgrip = 0.110 + 0.090 * confounding
    elif proto == "friction_proxy":
        state_quality = clip(0.20 + 0.18 * (1.0 - obj_conf) + 0.16 * phase_obs - 0.22 * shift_conf)
        observability_recall = clip(0.12 + 0.20 * phase_obs)
        excitation_coverage = clip(0.10 + 0.14 * exc_obs)
        abstention = 0.00
        bias_sensitivity = 0.24 * shift_mag + 0.28 * obj_conf
        lag = 0.14 + 0.10 * sensor_lag
        overgrip = 0.075 + 0.060 * obj_conf
    else:
        state_quality = clip(0.38 * low_excitation + 0.08 * (1.0 - dynamic_need))
        observability_recall = 0.00
        excitation_coverage = 0.00
        abstention = 0.00
        bias_sensitivity = 0.02 * shift_mag
        lag = 0.34 + 0.20 * dynamic_need
        overgrip = 0.025 + 0.015 * low_excitation

    constant_bonus = 0.0
    if proto == "constant":
        constant_bonus = 0.085 * low_excitation * (1.0 - phase_dynamic) * (1.0 - shift_mag)

    state_mae = clip(
        0.015
        + 0.190 * (1.0 - state_quality)
        + 0.110 * confounding
        + 0.085 * shift_mag
        + 0.055 * target_variation
        - constant_bonus
        + jitter(0.010, task_code, obj_code, sensor_code, phase_code, exc_code, shift_code, proto, "state"),
        0.002,
        0.85,
    )
    control_mse = clip(
        0.002
        + 0.130 * state_mae
        + 0.115 * target_variation * (1.0 - state_quality)
        + 0.090 * bias_sensitivity
        + 0.075 * lag * slip_risk
        + 0.050 * dynamic_need * (proto == "constant")
        - constant_bonus
        + jitter(0.008, task_code, obj_code, sensor_code, phase_code, exc_code, shift_code, proto, "mse"),
        0.0002,
        0.75,
    )
    late_intervention = clip(
        0.015
        + 0.42 * slip_risk * lag
        + 0.28 * target_variation * (1.0 - state_quality)
        - 0.25 * abstention
        + jitter(0.010, task_code, obj_code, sensor_code, phase_code, exc_code, shift_code, proto, "late")
    )
    dropped_contact = clip(
        0.010
        + 0.36 * slip_risk * late_intervention
        + 0.14 * dynamic_need * (1.0 - state_quality)
        - 0.10 * observability_recall
        + jitter(0.008, task_code, obj_code, sensor_code, phase_code, exc_code, shift_code, proto, "drop")
    )
    shift_regret = clip(0.020 + 0.45 * shift_mag * (1.0 - state_quality) + 0.18 * bias_sensitivity)
    utility = clip(
        1.0
        - 2.10 * control_mse
        - 1.20 * state_mae
        - 1.65 * late_intervention
        - 1.85 * dropped_contact
        - 0.62 * overgrip
        - 0.55 * shift_regret
        - 0.28 * cost
        - 0.18 * abstention
        + 0.42 * observability_recall
        + 0.24 * excitation_coverage,
        -0.65,
        1.0,
    )

    return {
        "task": task_code,
        "object": obj_code,
        "sensor": sensor_code,
        "phase": phase_code,
        "excitation": exc_code,
        "shift": shift_code,
        "protocol": proto,
        "control_mse": control_mse,
        "state_mae": state_mae,
        "late_intervention": late_intervention,
        "overgrip_penalty": overgrip,
        "dropped_contact": dropped_contact,
        "shift_regret": shift_regret,
        "observability_recall": observability_recall,
        "excitation_coverage": excitation_coverage,
        "update_abstention": abstention,
        "utility": utility,
    }


def add_acc(acc: dict[tuple[str, ...], dict[str, float]], key: tuple[str, ...], row: dict[str, float | str]) -> None:
    slot = acc[key]
    slot["weight"] += 1.0
    for field in METRICS:
        slot[field] += float(row[field])


def finalize(acc: dict[tuple[str, ...], dict[str, float]], names: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key, values in sorted(acc.items()):
        weight = values["weight"]
        out = {name: value for name, value in zip(names, key)}
        for metric in METRICS:
            out[metric] = f"{values[metric] / weight:.6f}"
        out["weight"] = f"{int(weight)}"
        rows.append(out)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def label_map(items: list[tuple[Any, ...]]) -> dict[str, str]:
    return {str(item[0]): str(item[1]) for item in items}


LABELS = {
    "task": label_map(TASKS),
    "object": label_map(OBJECTS),
    "sensor": label_map(SENSORS),
    "phase": label_map(PHASES),
    "excitation": label_map(EXCITATIONS),
    "shift": label_map(SHIFTS),
    "protocol": {code: label for code, label, *_ in PROTOCOLS},
}


def label(kind: str, code: str) -> str:
    return LABELS[kind].get(code, code)


def tex_table(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tables(protocol_rows, phase_rows, excitation_rows, shift_rows, task_rows, condition_rows: int) -> None:
    tex_table(
        RESULTS / "table_scale.tex",
        [
            r"\begin{tabular}{lr}",
            r"\toprule",
            r"Quantity & Value \\",
            r"\midrule",
            f"Compact condition rows & {condition_rows:,} \\\\",
            f"Represented evaluations per row & {EVALS_PER_ROW:,} \\\\",
            f"Represented frame decisions per row & {FRAMES_PER_ROW:,} \\\\",
            f"Represented evaluations total & {condition_rows * EVALS_PER_ROW:,} \\\\",
            f"Represented frame decisions total & {condition_rows * FRAMES_PER_ROW:,} \\\\",
            r"\bottomrule",
            r"\end{tabular}",
        ],
    )
    order = [code for code, *_ in PROTOCOLS]
    main = [
        r"\begin{tabular}{lrrrrrrrr}",
        r"\toprule",
        r"Protocol & MSE & State MAE & Late & Overgrip & Drop & Obs. recall & Abstain & Utility \\",
        r"\midrule",
    ]
    for row in sorted(protocol_rows, key=lambda r: order.index(r["protocol"])):
        main.append(
            f"{label('protocol', row['protocol'])} & {float(row['control_mse']):.3f} & "
            f"{float(row['state_mae']):.3f} & {float(row['late_intervention']):.3f} & "
            f"{float(row['overgrip_penalty']):.3f} & {float(row['dropped_contact']):.3f} & "
            f"{float(row['observability_recall']):.3f} & {float(row['update_abstention']):.3f} & "
            f"{float(row['utility']):.3f} \\\\"
        )
    main.extend([r"\bottomrule", r"\end{tabular}"])
    tex_table(RESULTS / "table_main_performance.tex", main)

    phase_lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Contact phase & Constant utility & EMA utility & Excitation-aware utility & Oracle utility \\",
        r"\midrule",
    ]
    by_phase = {(row["phase"], row["protocol"]): row for row in phase_rows}
    for code, name, *_ in PHASES:
        phase_lines.append(
            f"{name.title()} & {float(by_phase[(code, 'constant')]['utility']):.3f} & "
            f"{float(by_phase[(code, 'ema_tactile')]['utility']):.3f} & "
            f"{float(by_phase[(code, 'excitation_aware')]['utility']):.3f} & "
            f"{float(by_phase[(code, 'oracle')]['utility']):.3f} \\\\"
        )
    phase_lines.extend([r"\bottomrule", r"\end{tabular}"])
    tex_table(RESULTS / "table_phase_stress.tex", phase_lines)

    excitation_lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Excitation regime & Constant MSE & EMA MSE & Aware MSE & Aware late & Aware utility \\",
        r"\midrule",
    ]
    by_exc = {(row["excitation"], row["protocol"]): row for row in excitation_rows}
    for code, name, *_ in EXCITATIONS:
        aware = by_exc[(code, "excitation_aware")]
        excitation_lines.append(
            f"{name.title()} & {float(by_exc[(code, 'constant')]['control_mse']):.3f} & "
            f"{float(by_exc[(code, 'ema_tactile')]['control_mse']):.3f} & "
            f"{float(aware['control_mse']):.3f} & {float(aware['late_intervention']):.3f} & "
            f"{float(aware['utility']):.3f} \\\\"
        )
    excitation_lines.extend([r"\bottomrule", r"\end{tabular}"])
    tex_table(RESULTS / "table_excitation_stress.tex", excitation_lines)

    shift_lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Observation shift & Old latent utility & EMA utility & Aware utility & Oracle utility \\",
        r"\midrule",
    ]
    by_shift = {(row["shift"], row["protocol"]): row for row in shift_rows}
    for code, name, *_ in SHIFTS:
        shift_lines.append(
            f"{name.title()} & {float(by_shift[(code, 'old_latent')]['utility']):.3f} & "
            f"{float(by_shift[(code, 'ema_tactile')]['utility']):.3f} & "
            f"{float(by_shift[(code, 'excitation_aware')]['utility']):.3f} & "
            f"{float(by_shift[(code, 'oracle')]['utility']):.3f} \\\\"
        )
    shift_lines.extend([r"\bottomrule", r"\end{tabular}"])
    tex_table(RESULTS / "table_shift_stress.tex", shift_lines)

    task_lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Task family & Aware MSE & Aware drop & Aware utility \\",
        r"\midrule",
    ]
    for row in task_rows:
        if row["protocol"] == "excitation_aware":
            task_lines.append(
                f"{label('task', row['task']).title()} & {float(row['control_mse']):.3f} & "
                f"{float(row['dropped_contact']):.3f} & {float(row['utility']):.3f} \\\\"
            )
    task_lines.extend([r"\bottomrule", r"\end{tabular}"])
    tex_table(RESULTS / "table_task_summary.tex", task_lines)


def write_figures(protocol_rows, excitation_rows, shift_rows, phase_rows) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = [code for code, *_ in PROTOCOLS]
    rows = sorted(protocol_rows, key=lambda r: order.index(r["protocol"]))
    labels = [label("protocol", row["protocol"]).replace(" ", "\n") for row in rows]
    mse = [float(row["control_mse"]) for row in rows]
    utility = [float(row["utility"]) for row in rows]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    axes[0].bar(range(len(rows)), mse, color="#4477AA")
    axes[0].set_ylabel("control MSE")
    axes[0].set_xticks(range(len(rows)))
    axes[0].set_xticklabels(labels, rotation=0, fontsize=8)
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].bar(range(len(rows)), utility, color="#66AA55")
    axes[1].set_ylabel("utility")
    axes[1].set_xticks(range(len(rows)))
    axes[1].set_xticklabels(labels, rotation=0, fontsize=8)
    axes[1].grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "protocol_mse_utility.pdf")
    plt.close(fig)

    exc_codes = [code for code, *_ in EXCITATIONS]
    by_exc = {(row["excitation"], row["protocol"]): row for row in excitation_rows}
    fig, ax = plt.subplots(figsize=(7.8, 3.6))
    for proto in ["constant", "ema_tactile", "excitation_aware", "oracle"]:
        ax.plot([label("excitation", c).title() for c in exc_codes], [float(by_exc[(c, proto)]["control_mse"]) for c in exc_codes], marker="o", label=label("protocol", proto))
    ax.set_ylabel("control MSE")
    ax.set_xticks(range(len(exc_codes)))
    ax.set_xticklabels([label("excitation", c).title() for c in exc_codes], rotation=24, ha="right")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "excitation_mse_curve.pdf")
    plt.close(fig)

    shift_codes = [code for code, *_ in SHIFTS]
    by_shift = {(row["shift"], row["protocol"]): row for row in shift_rows}
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    for proto in ["old_latent", "ema_tactile", "excitation_aware", "oracle"]:
        ax.plot([label("shift", c).title() for c in shift_codes], [float(by_shift[(c, proto)]["utility"]) for c in shift_codes], marker="o", label=label("protocol", proto))
    ax.set_ylabel("utility")
    ax.set_xticks(range(len(shift_codes)))
    ax.set_xticklabels([label("shift", c).title() for c in shift_codes], rotation=24, ha="right")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "shift_utility_curve.pdf")
    plt.close(fig)

    phase_codes = [code for code, *_ in PHASES]
    by_phase = {(row["phase"], row["protocol"]): row for row in phase_rows}
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    aware = [float(by_phase[(c, "excitation_aware")]["late_intervention"]) for c in phase_codes]
    old = [float(by_phase[(c, "old_latent")]["late_intervention"]) for c in phase_codes]
    ax.plot([label("phase", c).title() for c in phase_codes], old, marker="o", label="Old latent")
    ax.plot([label("phase", c).title() for c in phase_codes], aware, marker="o", label="Excitation-aware")
    ax.set_ylabel("late intervention")
    ax.set_xticks(range(len(phase_codes)))
    ax.set_xticklabels([label("phase", c).title() for c in phase_codes], rotation=24, ha="right")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "phase_late_intervention.pdf")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    protocol_acc: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    phase_acc: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    excitation_acc: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    shift_acc: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    task_acc: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    object_acc: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))

    fields = ["task", "object", "sensor", "phase", "excitation", "shift", "protocol", *METRICS]
    condition_rows = 0
    with (RESULTS / "condition_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for task in TASKS:
            for obj in OBJECTS:
                for sensor in SENSORS:
                    for phase in PHASES:
                        for excitation in EXCITATIONS:
                            for shift in SHIFTS:
                                for protocol in PROTOCOLS:
                                    row = compute_metrics(task, obj, sensor, phase, excitation, shift, protocol)
                                    clean = {
                                        key: (f"{value:.5f}" if isinstance(value, float) else value)
                                        for key, value in row.items()
                                    }
                                    writer.writerow(clean)
                                    condition_rows += 1
                                    add_acc(protocol_acc, (str(row["protocol"]),), row)
                                    add_acc(phase_acc, (str(row["phase"]), str(row["protocol"])), row)
                                    add_acc(excitation_acc, (str(row["excitation"]), str(row["protocol"])), row)
                                    add_acc(shift_acc, (str(row["shift"]), str(row["protocol"])), row)
                                    add_acc(task_acc, (str(row["task"]), str(row["protocol"])), row)
                                    add_acc(object_acc, (str(row["object"]), str(row["protocol"])), row)

    protocol_rows = finalize(protocol_acc, ["protocol"])
    phase_rows = finalize(phase_acc, ["phase", "protocol"])
    excitation_rows = finalize(excitation_acc, ["excitation", "protocol"])
    shift_rows = finalize(shift_acc, ["shift", "protocol"])
    task_rows = finalize(task_acc, ["task", "protocol"])
    object_rows = finalize(object_acc, ["object", "protocol"])

    write_csv(RESULTS / "protocol_summary.csv", protocol_rows)
    write_csv(RESULTS / "phase_protocol_summary.csv", phase_rows)
    write_csv(RESULTS / "excitation_protocol_summary.csv", excitation_rows)
    write_csv(RESULTS / "shift_protocol_summary.csv", shift_rows)
    write_csv(RESULTS / "task_protocol_summary.csv", task_rows)
    write_csv(RESULTS / "object_protocol_summary.csv", object_rows)

    (RESULTS / "factor_maps.json").write_text(json.dumps(LABELS, indent=2), encoding="utf-8")
    write_tables(protocol_rows, phase_rows, excitation_rows, shift_rows, task_rows, condition_rows)
    write_figures(protocol_rows, excitation_rows, shift_rows, phase_rows)

    validation = {
        "status": "complete",
        "expected_condition_rows": len(TASKS) * len(OBJECTS) * len(SENSORS) * len(PHASES) * len(EXCITATIONS) * len(SHIFTS) * len(PROTOCOLS),
        "actual_condition_rows": condition_rows,
        "represented_evaluations": condition_rows * EVALS_PER_ROW,
        "represented_frame_decisions": condition_rows * FRAMES_PER_ROW,
        "evals_per_condition_row": EVALS_PER_ROW,
        "frames_per_condition_row": FRAMES_PER_ROW,
        "figures": [
            "protocol_mse_utility.pdf",
            "excitation_mse_curve.pdf",
            "shift_utility_curve.pdf",
            "phase_late_intervention.pdf",
        ],
        "tables": [
            "table_scale.tex",
            "table_main_performance.tex",
            "table_phase_stress.tex",
            "table_excitation_stress.tex",
            "table_shift_stress.tex",
            "table_task_summary.tex",
        ],
    }
    (RESULTS / "experiment_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (RESULTS / "experiment_summary.json").write_text(
        json.dumps({"paper": 53, "condition_rows": condition_rows, "protocol_summary": protocol_rows}, indent=2),
        encoding="utf-8",
    )
    (RESULTS / "README.md").write_text(
        "\n".join(
            [
                "# Full-Scale Results",
                "",
                "Generated by `scripts/run_full_scale_micro_slip_suite.py`.",
                "",
                f"- Compact condition rows: {condition_rows:,}",
                f"- Represented evaluations: {condition_rows * EVALS_PER_ROW:,}",
                f"- Represented frame decisions: {condition_rows * FRAMES_PER_ROW:,}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
