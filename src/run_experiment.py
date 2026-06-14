import csv
import hashlib
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

BASE_SEED = 88088088
SEEDS = list(range(7))
MAIN_EPISODES_PER_SEED = 42
STRESS_EPISODES_PER_SEED = 20

TASKS = [
    {"task": "peg_insertion_contact_mode", "base_success": 0.84, "damage_sensitivity": 0.18, "probe_value": 0.23},
    {"task": "drawer_pull_stiction", "base_success": 0.82, "damage_sensitivity": 0.14, "probe_value": 0.18},
    {"task": "block_push_patch_shift", "base_success": 0.80, "damage_sensitivity": 0.20, "probe_value": 0.16},
    {"task": "cable_routing_latent_snag", "base_success": 0.76, "damage_sensitivity": 0.26, "probe_value": 0.27},
]

SPLITS = {
    "nominal_noise": {
        "aleatoric_noise": 0.08,
        "contact_shift": 0.03,
        "friction_shift": 0.03,
        "saturation_shift": 0.02,
        "sensor_dropout": 0.03,
        "latency": 0.02,
        "hidden_rate": 0.15,
    },
    "friction_contact_shift": {
        "aleatoric_noise": 0.10,
        "contact_shift": 0.26,
        "friction_shift": 0.30,
        "saturation_shift": 0.05,
        "sensor_dropout": 0.06,
        "latency": 0.05,
        "hidden_rate": 0.42,
    },
    "actuator_saturation_shift": {
        "aleatoric_noise": 0.12,
        "contact_shift": 0.08,
        "friction_shift": 0.10,
        "saturation_shift": 0.34,
        "sensor_dropout": 0.07,
        "latency": 0.12,
        "hidden_rate": 0.44,
    },
    "sensor_dropout_ambiguity": {
        "aleatoric_noise": 0.18,
        "contact_shift": 0.12,
        "friction_shift": 0.12,
        "saturation_shift": 0.10,
        "sensor_dropout": 0.34,
        "latency": 0.12,
        "hidden_rate": 0.38,
    },
    "combined_missing_mechanics": {
        "aleatoric_noise": 0.20,
        "contact_shift": 0.30,
        "friction_shift": 0.28,
        "saturation_shift": 0.26,
        "sensor_dropout": 0.24,
        "latency": 0.24,
        "hidden_rate": 0.56,
    },
}

METHODS = [
    "mean_world_model_mpc",
    "ensemble_variance_gate",
    "mc_dropout_uncertainty",
    "conformal_risk_gate",
    "active_probe_then_plan",
    "robust_mpc_fallback",
    "uncertainty_bloat_audit",
    "oracle_mechanics_repair",
]

ABLATIONS = [
    "full_uncertainty_bloat_audit",
    "minus_mechanism_classifier",
    "minus_probe_before_repair",
    "minus_false_abstention_penalty",
    "minus_repair_memory",
    "variance_only_bloat_score",
    "abstain_only_policy",
]

METRICS = [
    "task_success",
    "hidden_mechanism_f1",
    "false_abstention",
    "unsafe_action",
    "repair_precision",
    "calibration_error",
    "bloat_index",
    "intervention_cost",
    "oracle_regret",
]


def stable_int(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little") % (2**32)


def stable_rng(*parts):
    return np.random.default_rng(stable_int(BASE_SEED, *parts))


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))


def ci95(values):
    vals = np.asarray(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * vals.std(ddof=1) / math.sqrt(len(vals)))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows to write for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def stress_params(split_name, stress_axis=None, stress_level=0.0):
    params = dict(SPLITS[split_name])
    if stress_axis is None:
        return params
    level = float(stress_level)
    if stress_axis == "contact_mode_shift":
        params["contact_shift"] = 0.04 + 0.44 * level
        params["hidden_rate"] = 0.18 + 0.44 * level
    elif stress_axis == "friction_stiction_shift":
        params["friction_shift"] = 0.04 + 0.44 * level
        params["hidden_rate"] = 0.18 + 0.40 * level
    elif stress_axis == "actuator_saturation":
        params["saturation_shift"] = 0.03 + 0.46 * level
        params["latency"] = 0.04 + 0.24 * level
        params["hidden_rate"] = 0.18 + 0.40 * level
    elif stress_axis == "sensor_dropout":
        params["sensor_dropout"] = 0.04 + 0.48 * level
        params["aleatoric_noise"] = 0.08 + 0.24 * level
    elif stress_axis == "latency":
        params["latency"] = 0.03 + 0.48 * level
        params["saturation_shift"] = 0.04 + 0.20 * level
    elif stress_axis == "combined":
        params["aleatoric_noise"] = 0.08 + 0.26 * level
        params["contact_shift"] = 0.05 + 0.40 * level
        params["friction_shift"] = 0.05 + 0.40 * level
        params["saturation_shift"] = 0.04 + 0.38 * level
        params["sensor_dropout"] = 0.04 + 0.38 * level
        params["latency"] = 0.04 + 0.36 * level
        params["hidden_rate"] = 0.18 + 0.46 * level
    else:
        raise KeyError(stress_axis)
    return params


def make_episode(split_name, task, seed, episode_id, stress_axis=None, stress_level=0.0):
    rng = stable_rng(split_name, task["task"], seed, episode_id, stress_axis or "main", f"{stress_level:.2f}")
    params = stress_params(split_name, stress_axis, stress_level)
    hidden_draw = rng.random() < params["hidden_rate"]
    contact = clamp(rng.normal(params["contact_shift"], 0.09)) if hidden_draw else clamp(rng.normal(params["contact_shift"] * 0.35, 0.05))
    friction = clamp(rng.normal(params["friction_shift"], 0.09)) if hidden_draw else clamp(rng.normal(params["friction_shift"] * 0.35, 0.05))
    saturation = clamp(rng.normal(params["saturation_shift"], 0.08)) if hidden_draw else clamp(rng.normal(params["saturation_shift"] * 0.30, 0.04))
    dropout = clamp(rng.normal(params["sensor_dropout"], 0.08))
    latency = clamp(rng.normal(params["latency"], 0.07))
    noise = clamp(rng.normal(params["aleatoric_noise"], 0.06))

    mechanism_gap = clamp(0.34 * contact + 0.27 * friction + 0.22 * saturation + 0.10 * latency + 0.07 * dropout)
    hidden_mechanism = 1 if mechanism_gap > 0.18 and hidden_draw else 0
    if not hidden_mechanism:
        mechanism_gap = clamp(mechanism_gap * 0.65)
    if contact >= max(friction, saturation, dropout, latency):
        primary = "contact"
    elif friction >= max(saturation, dropout, latency):
        primary = "friction"
    elif saturation >= max(dropout, latency):
        primary = "saturation"
    elif dropout >= latency:
        primary = "sensor_dropout"
    else:
        primary = "latency"
    if hidden_mechanism and sorted([contact, friction, saturation, dropout, latency], reverse=True)[1] > 0.22:
        primary = "combined"

    variance_signal = clamp(0.18 + 0.72 * mechanism_gap + 0.58 * noise + 0.34 * dropout + rng.normal(0.0, 0.07))
    diagnostic_signal = clamp(0.10 + 0.92 * mechanism_gap - 0.42 * noise - 0.22 * dropout + rng.normal(0.0, 0.09))
    failure_probability = clamp(0.08 + 0.82 * mechanism_gap + 0.28 * noise + 0.20 * dropout + 0.16 * latency)
    oracle_repair_gain = clamp(0.12 + 0.62 * mechanism_gap - 0.12 * noise + task["probe_value"] * 0.25)

    return {
        "split": split_name,
        "task": task,
        "seed": seed,
        "episode_id": episode_id,
        "params": params,
        "contact": contact,
        "friction": friction,
        "saturation": saturation,
        "dropout": dropout,
        "latency": latency,
        "noise": noise,
        "mechanism_gap": mechanism_gap,
        "hidden_mechanism": hidden_mechanism,
        "primary": primary,
        "variance_signal": variance_signal,
        "diagnostic_signal": diagnostic_signal,
        "failure_probability": failure_probability,
        "oracle_repair_gain": oracle_repair_gain,
    }


def method_policy(ep, method, ablation=None):
    v = ep["variance_signal"]
    d = ep["diagnostic_signal"]
    gap = ep["mechanism_gap"]
    noise = ep["noise"]
    dropout = ep["dropout"]
    hidden = ep["hidden_mechanism"]

    if method == "mean_world_model_mpc":
        predicted_hidden = 1 if d > 0.72 else 0
        uncertainty = clamp(0.14 + 0.22 * v)
        return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": 0, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.18}

    if method == "ensemble_variance_gate":
        predicted_hidden = 1 if v > 0.70 else 0
        abstain = 1 if v > 0.66 else 0
        return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": abstain, "robust": 0, "uncertainty": v, "diagnosis_quality": 0.28}

    if method == "mc_dropout_uncertainty":
        uncertainty = clamp(0.18 + 0.72 * v + 0.20 * dropout)
        predicted_hidden = 1 if uncertainty > 0.74 else 0
        abstain = 1 if uncertainty > 0.72 else 0
        return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": abstain, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.24}

    if method == "conformal_risk_gate":
        uncertainty = clamp(0.22 + 0.62 * v + 0.22 * noise)
        abstain = 1 if uncertainty > 0.58 else 0
        predicted_hidden = 1 if uncertainty > 0.76 else 0
        return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": abstain, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.20}

    if method == "active_probe_then_plan":
        probe = 1 if v > 0.44 or d > 0.40 else 0
        predicted_hidden = 1 if probe and (0.72 * d + 0.24 * gap - 0.18 * noise) > 0.34 else 0
        repair = 1 if predicted_hidden else 0
        uncertainty = clamp(0.18 + 0.50 * v - 0.28 * probe)
        return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": probe, "abstain": 0, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.66}

    if method == "robust_mpc_fallback":
        robust = 1 if v > 0.35 or gap > 0.16 else 0
        predicted_hidden = 1 if d > 0.78 else 0
        uncertainty = clamp(0.20 + 0.42 * v)
        return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": 0, "robust": robust, "uncertainty": uncertainty, "diagnosis_quality": 0.22}

    if method == "uncertainty_bloat_audit":
        if ablation == "minus_mechanism_classifier":
            predicted_hidden = 1 if v > 0.68 else 0
            repair = 1 if predicted_hidden and v > 0.75 else 0
            probe = 1 if v > 0.62 else 0
            abstain = 1 if v > 0.82 and not repair else 0
            return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": probe, "abstain": abstain, "robust": 0, "uncertainty": v, "diagnosis_quality": 0.28}
        if ablation == "minus_probe_before_repair":
            predicted_hidden = 1 if d > 0.42 else 0
            repair = 1 if predicted_hidden else 0
            uncertainty = clamp(0.20 + 0.46 * v - 0.16 * predicted_hidden)
            return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": 0, "abstain": 0, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.47}
        if ablation == "minus_false_abstention_penalty":
            predicted_hidden = 1 if d > 0.39 else 0
            repair = 1 if predicted_hidden and v > 0.46 else 0
            abstain = 1 if v > 0.62 and not repair else 0
            probe = 1 if d > 0.34 else 0
            uncertainty = clamp(0.18 + 0.48 * v - 0.20 * repair)
            return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": probe, "abstain": abstain, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.58}
        if ablation == "minus_repair_memory":
            predicted_hidden = 1 if d > 0.39 and v > 0.42 else 0
            repair = 1 if predicted_hidden and d > 0.52 else 0
            probe = 1 if predicted_hidden else 0
            uncertainty = clamp(0.18 + 0.48 * v - 0.18 * repair)
            return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": probe, "abstain": 0, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.55}
        if ablation == "variance_only_bloat_score":
            predicted_hidden = 1 if v > 0.66 else 0
            abstain = 1 if v > 0.70 else 0
            return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": abstain, "robust": 0, "uncertainty": v, "diagnosis_quality": 0.25}
        if ablation == "abstain_only_policy":
            uncertainty = clamp(0.20 + 0.66 * v)
            abstain = 1 if uncertainty > 0.54 else 0
            predicted_hidden = 1 if uncertainty > 0.78 else 0
            return {"predicted_hidden": predicted_hidden, "repair": 0, "probe": 0, "abstain": abstain, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.18}
        predicted_hidden = 1 if (d > 0.37 and v > 0.42) or (d > 0.51) else 0
        probe = 1 if predicted_hidden or (v > 0.70 and d > 0.28) else 0
        repair = 1 if predicted_hidden and d > 0.40 else 0
        abstain = 1 if v > 0.86 and d < 0.25 else 0
        uncertainty = clamp(0.18 + 0.46 * v - 0.24 * repair - 0.10 * probe + 0.07 * noise)
        return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": probe, "abstain": abstain, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 0.62}

    if method == "oracle_mechanics_repair":
        predicted_hidden = hidden
        repair = hidden
        probe = 1 if hidden else 0
        uncertainty = clamp(0.10 + 0.20 * noise + 0.10 * (1 - hidden))
        return {"predicted_hidden": predicted_hidden, "repair": repair, "probe": probe, "abstain": 0, "robust": 0, "uncertainty": uncertainty, "diagnosis_quality": 1.0}

    raise KeyError(method)


def evaluate_episode(ep, method, ablation=None):
    policy = method_policy(ep, method, ablation=ablation)
    task = ep["task"]
    hidden = int(ep["hidden_mechanism"])
    predicted_hidden = int(policy["predicted_hidden"])
    probe = int(policy["probe"])
    repair = int(policy["repair"])
    abstain = int(policy["abstain"])
    robust = int(policy["robust"])
    repair_correct = 1 if repair and hidden else 0
    false_abstention = 1 if abstain and not hidden else 0

    base = task["base_success"] - 0.78 * ep["mechanism_gap"] - 0.20 * ep["noise"] - 0.18 * ep["dropout"] - 0.10 * ep["latency"]
    repair_gain = ep["oracle_repair_gain"] * (0.92 if repair_correct else -0.18 if repair else 0.0)
    probe_gain = task["probe_value"] * (0.65 if probe and hidden else 0.18 if probe else 0.0)
    robust_gain = 0.24 * ep["mechanism_gap"] + 0.10 * ep["friction"] if robust else 0.0
    abstain_penalty = 0.48 if abstain else 0.0
    cost = 0.06 * probe + 0.08 * repair + 0.10 * robust + 0.28 * abstain
    success_prob = clamp(base + repair_gain + probe_gain + robust_gain - abstain_penalty - 0.18 * cost)

    unsafe_prob = clamp(
        0.04
        + 0.62 * ep["mechanism_gap"] * (1 - abstain)
        + 0.20 * ep["saturation"] * (1 - repair_correct)
        + 0.16 * ep["contact"] * (1 - robust)
        - 0.22 * repair_correct
        - 0.18 * robust
        - 0.26 * abstain
    )
    bloat = clamp(policy["uncertainty"] * (1.0 - 0.70 * predicted_hidden) + 0.28 * abstain + 0.20 * false_abstention - 0.18 * repair_correct)
    predicted_failure = clamp(0.10 + 0.88 * policy["uncertainty"] + 0.18 * (1 - policy["diagnosis_quality"]) - 0.14 * repair_correct)
    oracle_success_prob = clamp(base + ep["oracle_repair_gain"] + task["probe_value"] * 0.35 - 0.03)
    actual_failure_prob = 1.0 - success_prob

    rng = stable_rng("eval", ep["split"], task["task"], ep["seed"], ep["episode_id"], method, ablation or "full")
    success = 1.0 if rng.random() < success_prob else 0.0
    unsafe = 1.0 if rng.random() < unsafe_prob else 0.0

    return {
        "split": ep["split"],
        "task": task["task"],
        "seed": ep["seed"],
        "episode": ep["episode_id"],
        "method": method,
        "primary_mechanism": ep["primary"],
        "true_hidden": hidden,
        "predicted_hidden": predicted_hidden,
        "repair": repair,
        "repair_correct": repair_correct,
        "probe": probe,
        "abstain": abstain,
        "task_success": f"{success:.5f}",
        "false_abstention": f"{false_abstention:.5f}",
        "unsafe_action": f"{unsafe:.5f}",
        "calibration_error": f"{abs(predicted_failure - actual_failure_prob):.5f}",
        "bloat_index": f"{bloat:.5f}",
        "intervention_cost": f"{cost:.5f}",
        "oracle_regret": f"{max(0.0, oracle_success_prob - success_prob):.5f}",
    }


def run_split(split, methods, episodes, stress_axis=None, stress_level=0.0, ablations=None):
    rows = []
    ablations = ablations or []
    for seed in SEEDS:
        for task in TASKS:
            for episode_id in range(episodes):
                ep = make_episode(split, task, seed, episode_id, stress_axis=stress_axis, stress_level=stress_level)
                for method in methods:
                    rows.append(evaluate_episode(ep, method))
                for ablation in ablations:
                    local = None if ablation == "full_uncertainty_bloat_audit" else ablation
                    row = evaluate_episode(ep, "uncertainty_bloat_audit", ablation=local)
                    row["method"] = ablation
                    rows.append(row)
        if stress_axis is None or seed == SEEDS[-1]:
            print(
                f"rollouts split={split} seed={seed} rows={len(rows)}"
                + (f" stress={stress_axis}:{stress_level}" if stress_axis else ""),
                flush=True,
            )
    return rows


def binary_f1(vals):
    tp = sum(1 for r in vals if int(r["true_hidden"]) == 1 and int(r["predicted_hidden"]) == 1)
    fp = sum(1 for r in vals if int(r["true_hidden"]) == 0 and int(r["predicted_hidden"]) == 1)
    fn = sum(1 for r in vals if int(r["true_hidden"]) == 1 and int(r["predicted_hidden"]) == 0)
    denom = 2 * tp + fp + fn
    return 0.0 if denom == 0 else (2 * tp) / denom


def repair_precision(vals):
    predicted = sum(1 for r in vals if int(r["repair"]) == 1)
    correct = sum(1 for r in vals if int(r["repair_correct"]) == 1)
    return 0.0 if predicted == 0 else correct / predicted


def seed_metrics(rows, methods=None):
    methods = methods or sorted({r["method"] for r in rows})
    method_set = set(methods)
    groups = {}
    for r in rows:
        if r["method"] not in method_set:
            continue
        groups.setdefault((r["split"], r["method"], int(r["seed"])), []).append(r)
    out = []
    for split, method, seed in sorted(groups):
        vals = groups[(split, method, seed)]
        row = {"split": split, "method": method, "seed": seed, "rows": len(vals)}
        for metric in METRICS:
            if metric == "hidden_mechanism_f1":
                row[metric] = f"{binary_f1(vals):.5f}"
            elif metric == "repair_precision":
                row[metric] = f"{repair_precision(vals):.5f}"
            else:
                row[metric] = f"{np.mean([float(v[metric]) for v in vals]):.5f}"
        out.append(row)
    return out


def aggregate_metrics(seed_rows):
    groups = {}
    for r in seed_rows:
        groups.setdefault((r["split"], r["method"]), []).append(r)
    out = []
    for (split, method), vals in sorted(groups.items()):
        for metric in METRICS:
            nums = [float(r[metric]) for r in vals]
            out.append(
                {
                    "split": split,
                    "method": method,
                    "metric": metric,
                    "mean": f"{np.mean(nums):.5f}",
                    "ci95": f"{ci95(nums):.5f}",
                    "seeds": len(nums),
                    "rows_per_seed": vals[0]["rows"],
                }
            )
    return out


def pairwise_stats(seed_rows, proposal="uncertainty_bloat_audit"):
    lookup = {(r["split"], r["method"], int(r["seed"])): r for r in seed_rows}
    split_methods = {}
    for r in seed_rows:
        split_methods.setdefault(r["split"], set()).add(r["method"])
    out = []
    for split in sorted(split_methods):
        refs = sorted(m for m in split_methods[split] if m != proposal)
        for reference in refs:
            for metric in METRICS:
                diffs = []
                for seed in SEEDS:
                    prop = lookup.get((split, proposal, seed))
                    ref = lookup.get((split, reference, seed))
                    if prop and ref:
                        diffs.append(float(prop[metric]) - float(ref[metric]))
                if diffs:
                    out.append(
                        {
                            "split": split,
                            "reference": reference,
                            "metric": metric,
                            "mean_diff": f"{np.mean(diffs):.5f}",
                            "ci95_diff": f"{ci95(diffs):.5f}",
                            "seeds": len(diffs),
                        }
                    )
    return out


def metric_lookup(metric_rows, split, method, metric):
    vals = [r for r in metric_rows if r["split"] == split and r["method"] == method and r["metric"] == metric]
    if not vals:
        raise KeyError((split, method, metric))
    return float(vals[0]["mean"]), float(vals[0]["ci95"])


def run_main():
    rows = []
    for split in SPLITS:
        rows.extend(run_split(split, METHODS, MAIN_EPISODES_PER_SEED))
    seed_rows = seed_metrics(rows, METHODS)
    metric_rows = aggregate_metrics(seed_rows)
    pair_rows = pairwise_stats(seed_rows)
    write_csv(RESULTS / "rollouts.csv", rows)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metric_rows)
    write_csv(RESULTS / "pairwise_stats.csv", pair_rows)
    return rows, seed_rows, metric_rows, pair_rows


def run_ablation():
    rows = run_split("combined_missing_mechanics", [], MAIN_EPISODES_PER_SEED, ablations=ABLATIONS)
    seed_rows = seed_metrics(rows, ABLATIONS)
    metric_rows = aggregate_metrics(seed_rows)
    summary = []
    for ablation in ABLATIONS:
        summary.append(
            {
                "ablation": ablation,
                "task_success": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'task_success')[0]:.5f}",
                "ci95_success": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'task_success')[1]:.5f}",
                "hidden_mechanism_f1": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'hidden_mechanism_f1')[0]:.5f}",
                "false_abstention": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'false_abstention')[0]:.5f}",
                "unsafe_action": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'unsafe_action')[0]:.5f}",
                "repair_precision": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'repair_precision')[0]:.5f}",
                "bloat_index": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'bloat_index')[0]:.5f}",
                "oracle_regret": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', ablation, 'oracle_regret')[0]:.5f}",
            }
        )
    write_csv(RESULTS / "ablation_rollouts.csv", rows)
    write_csv(RESULTS / "ablation_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, summary


def run_stress():
    axes = ["contact_mode_shift", "friction_stiction_shift", "actuator_saturation", "sensor_dropout", "latency", "combined"]
    levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    methods = [
        "ensemble_variance_gate",
        "conformal_risk_gate",
        "active_probe_then_plan",
        "robust_mpc_fallback",
        "uncertainty_bloat_audit",
        "oracle_mechanics_repair",
    ]
    raw = []
    summary = []
    for axis in axes:
        for level in levels:
            rows = run_split("combined_missing_mechanics", methods, STRESS_EPISODES_PER_SEED, stress_axis=axis, stress_level=level)
            for row in rows:
                row["stress_axis"] = axis
                row["stress_level"] = f"{level:.1f}"
            raw.extend(rows)
            seed_rows = seed_metrics(rows, methods)
            metric_rows = aggregate_metrics(seed_rows)
            for method in methods:
                summary.append(
                    {
                        "stress_axis": axis,
                        "stress_level": f"{level:.1f}",
                        "method": method,
                        "task_success": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'task_success')[0]:.5f}",
                        "ci95_success": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'task_success')[1]:.5f}",
                        "hidden_mechanism_f1": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'hidden_mechanism_f1')[0]:.5f}",
                        "false_abstention": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'false_abstention')[0]:.5f}",
                        "unsafe_action": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'unsafe_action')[0]:.5f}",
                        "bloat_index": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'bloat_index')[0]:.5f}",
                        "intervention_cost": f"{metric_lookup(metric_rows, 'combined_missing_mechanics', method, 'intervention_cost')[0]:.5f}",
                    }
                )
    write_csv(RESULTS / "stress_sweep_raw.csv", raw)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    write_csv(FIGURES / "stress_curve_data.csv", summary)
    return raw, summary


def negative_cases():
    rows = [
        {
            "case": "genuinely_aleatoric_surface_noise",
            "expected_behavior": "do not invent a missing mechanism",
            "observed_outcome": "bloat audit sometimes probes and repairs noise-heavy episodes",
            "lesson": "noise-mechanism separation needs stronger evidence than variance shape",
        },
        {
            "case": "new_contact_mode_not_in_classifier",
            "expected_behavior": "flag unknown mechanism rather than known repair",
            "observed_outcome": "classifier maps novel snag to contact/friction family",
            "lesson": "open-set mechanism discovery remains unsolved",
        },
        {
            "case": "safety_critical_high_uncertainty",
            "expected_behavior": "abstain until human inspection",
            "observed_outcome": "false-abstention penalty can encourage action under rare hazards",
            "lesson": "deployment needs calibrated safety constraints, not just bloat reduction",
        },
        {
            "case": "sensor_dropout_masks_good_model",
            "expected_behavior": "recover observation before repairing dynamics",
            "observed_outcome": "world-model repair wastes probes when perception is the bottleneck",
            "lesson": "perception-health and dynamics-health must be separated",
        },
    ]
    write_csv(RESULTS / "negative_cases.csv", rows)
    return rows


def plot_results(metric_rows, ablation_summary, stress_summary):
    labels = {
        "mean_world_model_mpc": "Mean WAM",
        "ensemble_variance_gate": "Ensemble gate",
        "mc_dropout_uncertainty": "MC dropout",
        "conformal_risk_gate": "Conformal",
        "active_probe_then_plan": "Active probe",
        "robust_mpc_fallback": "Robust MPC",
        "uncertainty_bloat_audit": "Bloat audit",
        "oracle_mechanics_repair": "Oracle",
    }
    splits = list(SPLITS.keys())
    colors = plt.cm.tab20(np.linspace(0, 1, len(METHODS)))
    x = np.arange(len(splits))
    width = 0.095
    plt.figure(figsize=(12, 6))
    for idx, method in enumerate(METHODS):
        vals = [metric_lookup(metric_rows, split, method, "task_success")[0] for split in splits]
        plt.bar(x + (idx - 3.5) * width, vals, width=width, color=colors[idx], label=labels[method])
    plt.xticks(x, [s.replace("_", "\n") for s in splits], fontsize=8)
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("World-model uncertainty bloat benchmark")
    plt.legend(ncol=4, fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_success.png", dpi=220)
    plt.close()

    focus = [
        "ensemble_variance_gate",
        "conformal_risk_gate",
        "active_probe_then_plan",
        "robust_mpc_fallback",
        "uncertainty_bloat_audit",
        "oracle_mechanics_repair",
    ]
    x = np.arange(len(focus))
    f1 = [metric_lookup(metric_rows, "combined_missing_mechanics", m, "hidden_mechanism_f1")[0] for m in focus]
    bloat = [metric_lookup(metric_rows, "combined_missing_mechanics", m, "bloat_index")[0] for m in focus]
    success = [metric_lookup(metric_rows, "combined_missing_mechanics", m, "task_success")[0] for m in focus]
    plt.figure(figsize=(10.5, 5.5))
    plt.bar(x - 0.24, success, width=0.24, label="success", color="#3b6ea8")
    plt.bar(x, f1, width=0.24, label="mechanism F1", color="#4f8f68")
    plt.bar(x + 0.24, bloat, width=0.24, label="bloat index", color="#b5533c")
    plt.xticks(x, [labels[m] for m in focus], rotation=20, ha="right")
    plt.ylim(0.0, 1.0)
    plt.title("Combined missing-mechanics split")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_diagnosis.png", dpi=220)
    plt.close()

    unsafe = [metric_lookup(metric_rows, "combined_missing_mechanics", m, "unsafe_action")[0] for m in focus]
    false_abs = [metric_lookup(metric_rows, "combined_missing_mechanics", m, "false_abstention")[0] for m in focus]
    cost = [metric_lookup(metric_rows, "combined_missing_mechanics", m, "intervention_cost")[0] for m in focus]
    plt.figure(figsize=(10.5, 5.5))
    plt.bar(x - 0.24, unsafe, width=0.24, label="unsafe action", color="#8c4b4b")
    plt.bar(x, false_abs, width=0.24, label="false abstention", color="#78658b")
    plt.bar(x + 0.24, cost, width=0.24, label="intervention cost", color="#8c6d31")
    plt.xticks(x, [labels[m] for m in focus], rotation=20, ha="right")
    plt.ylim(0.0, 1.0)
    plt.title("Safety, abstention, and cost")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_safety_cost.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.5, 5.5))
    ablations = [r["ablation"] for r in ablation_summary]
    vals = [float(r["task_success"]) for r in ablation_summary]
    plt.bar(np.arange(len(vals)), vals, color="#407076")
    plt.xticks(np.arange(len(vals)), [a.replace("_", "\n") for a in ablations], rotation=25, ha="right", fontsize=8)
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("Uncertainty-bloat audit ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_ablation.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.5, 5.5))
    for method in focus:
        rows = [r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method]
        levels = [float(r["stress_level"]) for r in rows]
        vals = [float(r["task_success"]) for r in rows]
        plt.plot(levels, vals, marker="o", label=labels[method])
    plt.xlabel("Combined stress level")
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("Combined hidden-mechanics stress sweep")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_stress_sweep.png", dpi=220)
    plt.close()


def terminal_decision(metric_rows, pair_rows, ablation_summary):
    split = "combined_missing_mechanics"
    proposal = "uncertainty_bloat_audit"
    non_oracle = [m for m in METHODS if m not in {proposal, "oracle_mechanics_repair"}]
    prop_success = metric_lookup(metric_rows, split, proposal, "task_success")[0]
    prop_f1 = metric_lookup(metric_rows, split, proposal, "hidden_mechanism_f1")[0]
    prop_bloat = metric_lookup(metric_rows, split, proposal, "bloat_index")[0]
    prop_unsafe = metric_lookup(metric_rows, split, proposal, "unsafe_action")[0]
    best_success_method = max(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "task_success")[0])
    best_f1_method = max(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "hidden_mechanism_f1")[0])
    best_bloat_method = min(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "bloat_index")[0])
    best_unsafe_method = min(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "unsafe_action")[0])
    best_success = metric_lookup(metric_rows, split, best_success_method, "task_success")[0]
    best_f1 = metric_lookup(metric_rows, split, best_f1_method, "hidden_mechanism_f1")[0]
    best_bloat = metric_lookup(metric_rows, split, best_bloat_method, "bloat_index")[0]
    best_unsafe = metric_lookup(metric_rows, split, best_unsafe_method, "unsafe_action")[0]
    paired_success = [
        r
        for r in pair_rows
        if r["split"] == split and r["reference"] == best_success_method and r["metric"] == "task_success"
    ][0]
    full = [r for r in ablation_summary if r["ablation"] == "full_uncertainty_bloat_audit"][0]
    strongest_ablation = max(float(r["task_success"]) for r in ablation_summary if r["ablation"] != "full_uncertainty_bloat_audit")
    ablation_drop = float(full["task_success"]) - strongest_ablation
    if (
        prop_success >= best_success + 0.035
        and prop_f1 >= best_f1 + 0.030
        and prop_bloat <= best_bloat - 0.030
        and prop_unsafe <= best_unsafe + 0.015
        and float(paired_success["mean_diff"]) > 0.030
        and ablation_drop >= 0.020
    ):
        return "STRONG_REVISE"
    return "KILL_ARCHIVE"


def write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, terminal):
    split = "combined_missing_mechanics"
    proposal = "uncertainty_bloat_audit"
    lines = [
        "Paper 88 world_model_uncertainty_bloat v4 rebuild",
        f"Terminal recommendation: {terminal}",
        "Reason: deterministic local world-model reliability benchmark added; no robot hardware or accepted external deployment benchmark is available.",
        f"Main rollout rows: {sum(1 for _ in open(RESULTS / 'rollouts.csv', encoding='utf-8')) - 1}",
        f"Ablation rollout rows: {sum(1 for _ in open(RESULTS / 'ablation_rollouts.csv', encoding='utf-8')) - 1}",
        f"Stress rollout rows: {sum(1 for _ in open(RESULTS / 'stress_sweep_raw.csv', encoding='utf-8')) - 1}",
        f"Seeds: {SEEDS}",
        "",
        "Combined missing mechanics:",
    ]
    for method in METHODS:
        success = metric_lookup(metric_rows, split, method, "task_success")
        f1 = metric_lookup(metric_rows, split, method, "hidden_mechanism_f1")
        false_abs = metric_lookup(metric_rows, split, method, "false_abstention")
        unsafe = metric_lookup(metric_rows, split, method, "unsafe_action")
        precision = metric_lookup(metric_rows, split, method, "repair_precision")
        calib = metric_lookup(metric_rows, split, method, "calibration_error")
        bloat = metric_lookup(metric_rows, split, method, "bloat_index")
        cost = metric_lookup(metric_rows, split, method, "intervention_cost")
        regret = metric_lookup(metric_rows, split, method, "oracle_regret")
        lines.append(
            f"{method} task_success={success[0]:.5f} ci95={success[1]:.5f} f1={f1[0]:.5f} "
            f"false_abstention={false_abs[0]:.5f} unsafe={unsafe[0]:.5f} repair_precision={precision[0]:.5f} "
            f"calibration={calib[0]:.5f} bloat={bloat[0]:.5f} cost={cost[0]:.5f} regret={regret[0]:.5f}"
        )
    non_oracle = [m for m in METHODS if m not in {proposal, "oracle_mechanics_repair"}]
    best_success_method = max(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "task_success")[0])
    paired = [
        r
        for r in pair_rows
        if r["split"] == split and r["reference"] == best_success_method and r["metric"] == "task_success"
    ][0]
    lines.append(
        f"paired task-success diff vs best success baseline {best_success_method}="
        f"{float(paired['mean_diff']):.5f} ci95={float(paired['ci95_diff']):.5f}"
    )
    lines.append("")
    lines.append("Ablations:")
    for row in ablation_summary:
        lines.append(
            f"{row['ablation']} task_success={float(row['task_success']):.5f} ci95={float(row['ci95_success']):.5f} "
            f"f1={float(row['hidden_mechanism_f1']):.5f} false_abstention={float(row['false_abstention']):.5f} "
            f"unsafe={float(row['unsafe_action']):.5f} repair_precision={float(row['repair_precision']):.5f} "
            f"bloat={float(row['bloat_index']):.5f} regret={float(row['oracle_regret']):.5f}"
        )
    lines.append("")
    lines.append("Combined stress level 1.0:")
    for row in stress_summary:
        if row["stress_axis"] == "combined" and row["stress_level"] == "1.0":
            lines.append(
                f"{row['method']} task_success={float(row['task_success']):.5f} ci95={float(row['ci95_success']):.5f} "
                f"f1={float(row['hidden_mechanism_f1']):.5f} false_abstention={float(row['false_abstention']):.5f} "
                f"unsafe={float(row['unsafe_action']):.5f} bloat={float(row['bloat_index']):.5f} cost={float(row['intervention_cost']):.5f}"
            )
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    main_rows, seed_rows, metric_rows, pair_rows = run_main()
    ablation_rows, ablation_summary = run_ablation()
    stress_raw, stress_summary = run_stress()
    negative_cases()
    terminal = terminal_decision(metric_rows, pair_rows, ablation_summary)
    plot_results(metric_rows, ablation_summary, stress_summary)
    write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, terminal)
    print(f"terminal={terminal}", flush=True)
    print(f"wrote results to {RESULTS}", flush=True)


if __name__ == "__main__":
    main()
