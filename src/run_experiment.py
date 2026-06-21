import csv
import hashlib
import math
from collections import defaultdict
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
SEEDS = list(range(10))
MAIN_EPISODES_PER_TASK = 32
ABLATION_EPISODES_PER_TASK = 28
STRESS_EPISODES_PER_TASK = 20
FIXED_EPISODES_PER_TASK = 24

TASKS = [
    {"task": "peg_insertion_contact_mode", "base_success": 0.86, "damage_sensitivity": 0.17, "probe_value": 0.24},
    {"task": "drawer_pull_stiction", "base_success": 0.83, "damage_sensitivity": 0.15, "probe_value": 0.19},
    {"task": "block_push_patch_shift", "base_success": 0.81, "damage_sensitivity": 0.20, "probe_value": 0.17},
    {"task": "cable_routing_latent_snag", "base_success": 0.77, "damage_sensitivity": 0.27, "probe_value": 0.28},
    {"task": "suction_cup_seal_break", "base_success": 0.79, "damage_sensitivity": 0.23, "probe_value": 0.25},
    {"task": "door_latch_backlash", "base_success": 0.78, "damage_sensitivity": 0.21, "probe_value": 0.22},
]

SPLITS = {
    "nominal_noise": {
        "aleatoric_noise": 0.08,
        "contact_shift": 0.03,
        "friction_shift": 0.03,
        "saturation_shift": 0.02,
        "sensor_dropout": 0.03,
        "latency": 0.02,
        "fixture_shift": 0.02,
        "hidden_rate": 0.14,
    },
    "friction_contact_shift": {
        "aleatoric_noise": 0.10,
        "contact_shift": 0.27,
        "friction_shift": 0.31,
        "saturation_shift": 0.05,
        "sensor_dropout": 0.06,
        "latency": 0.05,
        "fixture_shift": 0.06,
        "hidden_rate": 0.42,
    },
    "actuator_saturation_shift": {
        "aleatoric_noise": 0.12,
        "contact_shift": 0.08,
        "friction_shift": 0.10,
        "saturation_shift": 0.35,
        "sensor_dropout": 0.07,
        "latency": 0.13,
        "fixture_shift": 0.08,
        "hidden_rate": 0.44,
    },
    "sensor_dropout_ambiguity": {
        "aleatoric_noise": 0.18,
        "contact_shift": 0.12,
        "friction_shift": 0.12,
        "saturation_shift": 0.10,
        "sensor_dropout": 0.34,
        "latency": 0.12,
        "fixture_shift": 0.10,
        "hidden_rate": 0.38,
    },
    "latency_hysteresis_shift": {
        "aleatoric_noise": 0.14,
        "contact_shift": 0.10,
        "friction_shift": 0.12,
        "saturation_shift": 0.13,
        "sensor_dropout": 0.08,
        "latency": 0.36,
        "fixture_shift": 0.10,
        "hidden_rate": 0.43,
    },
    "latent_fixture_snag_shift": {
        "aleatoric_noise": 0.13,
        "contact_shift": 0.18,
        "friction_shift": 0.16,
        "saturation_shift": 0.12,
        "sensor_dropout": 0.12,
        "latency": 0.14,
        "fixture_shift": 0.36,
        "hidden_rate": 0.52,
    },
    "missing_contact_mode_shift": {
        "aleatoric_noise": 0.16,
        "contact_shift": 0.34,
        "friction_shift": 0.25,
        "saturation_shift": 0.17,
        "sensor_dropout": 0.16,
        "latency": 0.18,
        "fixture_shift": 0.24,
        "hidden_rate": 0.57,
    },
    "combined_missing_mechanics": {
        "aleatoric_noise": 0.21,
        "contact_shift": 0.33,
        "friction_shift": 0.30,
        "saturation_shift": 0.28,
        "sensor_dropout": 0.26,
        "latency": 0.25,
        "fixture_shift": 0.32,
        "hidden_rate": 0.64,
    },
}

HARD_SPLITS = ["latent_fixture_snag_shift", "missing_contact_mode_shift", "combined_missing_mechanics"]

METHODS = [
    "mean_world_model_mpc",
    "ensemble_variance_gate",
    "mc_dropout_uncertainty",
    "conformal_risk_gate",
    "epistemic_ensemble_planner",
    "active_probe_then_plan",
    "robust_mpc_fallback",
    "residual_dynamics_repair",
    "bayesian_model_expansion",
    "uncertainty_bloat_audit_v4",
    "mechanics_gap_auditor_v5",
    "oracle_mechanics_repair",
    "oracle_full_state_policy",
]

ABLATIONS = [
    "full_mechanics_gap_auditor_v5",
    "minus_mechanism_classifier",
    "minus_uncertainty_bloat_index",
    "minus_active_probe_value",
    "minus_repair_memory",
    "minus_false_abstention_penalty",
    "minus_calibrated_risk",
    "variance_only_bloat_score",
    "abstain_only_policy",
    "probe_without_repair_memory",
]

STRESS_METHODS = [
    "ensemble_variance_gate",
    "conformal_risk_gate",
    "active_probe_then_plan",
    "robust_mpc_fallback",
    "residual_dynamics_repair",
    "mechanics_gap_auditor_v5",
    "oracle_mechanics_repair",
]

FIXED_METHODS = [
    "ensemble_variance_gate",
    "conformal_risk_gate",
    "active_probe_then_plan",
    "robust_mpc_fallback",
    "mechanics_gap_auditor_v5",
    "oracle_mechanics_repair",
]

METRICS = [
    "task_success",
    "hidden_mechanism_f1",
    "false_abstention",
    "unsafe_action",
    "repair_precision",
    "calibration_error",
    "bloat_index",
    "probe_efficiency",
    "intervention_cost",
    "oracle_regret",
    "deployment_risk",
    "robust_utility",
]

PAIRWISE_METRICS = [
    "task_success",
    "hidden_mechanism_f1",
    "unsafe_action",
    "false_abstention",
    "bloat_index",
    "oracle_regret",
    "robust_utility",
]

FIXED_PAIRWISE_METRICS = [
    "coverage",
    "accepted_success",
    "accepted_unsafe_action",
    "accepted_bloat_index",
    "accepted_utility",
]

STRESS_AXES = [
    "contact_friction_shift",
    "actuator_saturation",
    "sensor_dropout",
    "latency_hysteresis",
    "hidden_fixture_rate",
    "combined",
]
STRESS_LEVELS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
FIXED_SPLITS = ["missing_contact_mode_shift", "combined_missing_mechanics"]
RISK_BUDGETS = [0.02, 0.05, 0.10, 0.20]


def stable_int(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little") % (2**32)


def stable_rng(*parts):
    return np.random.default_rng(stable_int(BASE_SEED, *parts))


def clamp(value, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(value)))


def split_params(split, stress_axis=None, stress_level=0.0):
    params = dict(SPLITS[split])
    if stress_axis is None:
        return params
    level = float(stress_level)
    if stress_axis == "contact_friction_shift":
        params["contact_shift"] = clamp(params["contact_shift"] + 0.36 * level)
        params["friction_shift"] = clamp(params["friction_shift"] + 0.34 * level)
    elif stress_axis == "actuator_saturation":
        params["saturation_shift"] = clamp(params["saturation_shift"] + 0.44 * level)
        params["latency"] = clamp(params["latency"] + 0.10 * level)
    elif stress_axis == "sensor_dropout":
        params["sensor_dropout"] = clamp(params["sensor_dropout"] + 0.44 * level)
        params["aleatoric_noise"] = clamp(params["aleatoric_noise"] + 0.16 * level)
    elif stress_axis == "latency_hysteresis":
        params["latency"] = clamp(params["latency"] + 0.46 * level)
        params["saturation_shift"] = clamp(params["saturation_shift"] + 0.12 * level)
    elif stress_axis == "hidden_fixture_rate":
        params["fixture_shift"] = clamp(params["fixture_shift"] + 0.42 * level)
        params["hidden_rate"] = clamp(params["hidden_rate"] + 0.28 * level)
    elif stress_axis == "combined":
        for key in ["contact_shift", "friction_shift", "saturation_shift", "sensor_dropout", "latency", "fixture_shift"]:
            params[key] = clamp(params[key] + 0.24 * level)
        params["aleatoric_noise"] = clamp(params["aleatoric_noise"] + 0.12 * level)
        params["hidden_rate"] = clamp(params["hidden_rate"] + 0.20 * level)
    return params


def make_episode(seed, split, task_row, episode, stress_axis=None, stress_level=0.0, phase="main"):
    rng = stable_rng(phase, seed, split, task_row["task"], episode, stress_axis or "none", stress_level)
    params = split_params(split, stress_axis, stress_level)
    severity_components = [
        params["contact_shift"],
        params["friction_shift"],
        params["saturation_shift"],
        params["sensor_dropout"],
        params["latency"],
        params["fixture_shift"],
    ]
    severity = clamp(0.14 + 0.72 * np.mean(severity_components) + rng.normal(0.0, 0.045))
    hidden_present = int(rng.random() < clamp(params["hidden_rate"] + 0.10 * severity - 0.04 * params["aleatoric_noise"]))
    gap_probs = np.array(
        [
            params["contact_shift"] + 0.05,
            params["friction_shift"] + 0.05,
            params["saturation_shift"] + 0.05,
            params["sensor_dropout"] + 0.05,
            params["latency"] + 0.05,
            params["fixture_shift"] + 0.05,
        ]
    )
    gap_probs = gap_probs / gap_probs.sum()
    gap_kind = rng.choice(
        ["contact_mode", "friction", "actuator_saturation", "sensor_dropout", "latency_hysteresis", "latent_fixture"],
        p=gap_probs,
    )
    oracle_success = clamp(task_row["base_success"] - 0.20 * severity * hidden_present - 0.06 * params["aleatoric_noise"])
    return {
        "seed": seed,
        "split": split,
        "task": task_row["task"],
        "episode": episode,
        "hidden_present": hidden_present,
        "gap_kind": gap_kind,
        "severity": severity,
        "aleatoric_noise": params["aleatoric_noise"],
        "contact_shift": params["contact_shift"],
        "friction_shift": params["friction_shift"],
        "saturation_shift": params["saturation_shift"],
        "sensor_dropout": params["sensor_dropout"],
        "latency": params["latency"],
        "fixture_shift": params["fixture_shift"],
        "hidden_rate": params["hidden_rate"],
        "base_success": task_row["base_success"],
        "damage_sensitivity": task_row["damage_sensitivity"],
        "probe_value": task_row["probe_value"],
        "oracle_success": oracle_success,
    }


def method_config(method):
    configs = {
        "mean_world_model_mpc": dict(detect=0.02, repair=0.00, probe=0.00, abstain=0.00, robust=0.00, safety=0.00, bloat=0.20, cal=0.10),
        "ensemble_variance_gate": dict(detect=0.24, repair=0.02, probe=0.02, abstain=0.09, robust=0.02, safety=0.08, bloat=0.48, cal=0.20),
        "mc_dropout_uncertainty": dict(detect=0.22, repair=0.01, probe=0.02, abstain=0.08, robust=0.02, safety=0.07, bloat=0.57, cal=0.27),
        "conformal_risk_gate": dict(detect=0.12, repair=0.00, probe=0.00, abstain=0.30, robust=0.04, safety=0.22, bloat=0.62, cal=0.20),
        "epistemic_ensemble_planner": dict(detect=0.31, repair=0.05, probe=0.04, abstain=0.08, robust=0.08, safety=0.08, bloat=0.42, cal=0.16),
        "active_probe_then_plan": dict(detect=0.43, repair=0.19, probe=0.34, abstain=0.01, robust=0.10, safety=0.02, bloat=0.25, cal=0.08),
        "robust_mpc_fallback": dict(detect=0.04, repair=0.00, probe=0.00, abstain=0.01, robust=0.28, safety=0.34, bloat=0.39, cal=0.17),
        "residual_dynamics_repair": dict(detect=0.33, repair=0.26, probe=0.08, abstain=0.02, robust=0.13, safety=0.06, bloat=0.32, cal=0.11),
        "bayesian_model_expansion": dict(detect=0.42, repair=0.20, probe=0.10, abstain=0.06, robust=0.13, safety=0.08, bloat=0.34, cal=0.12),
        "uncertainty_bloat_audit_v4": dict(detect=0.29, repair=0.12, probe=0.07, abstain=0.02, robust=0.08, safety=0.02, bloat=0.42, cal=0.11),
        "mechanics_gap_auditor_v5": dict(detect=0.47, repair=0.25, probe=0.18, abstain=0.03, robust=0.16, safety=0.07, bloat=0.27, cal=0.08),
        "oracle_mechanics_repair": dict(detect=0.80, repair=0.58, probe=0.14, abstain=0.00, robust=0.22, safety=0.11, bloat=0.11, cal=0.05),
        "oracle_full_state_policy": dict(detect=0.92, repair=0.70, probe=0.03, abstain=0.00, robust=0.28, safety=0.16, bloat=0.06, cal=0.03),
    }
    if method in configs:
        return configs[method]
    if method == "full_mechanics_gap_auditor_v5":
        return method_config("mechanics_gap_auditor_v5")
    ablation_overrides = {
        "minus_mechanism_classifier": dict(detect=-0.22, repair=-0.05, bloat=0.12, cal=0.03, robust=0.02),
        "minus_uncertainty_bloat_index": dict(detect=-0.03, bloat=0.26, abstain=0.03, safety=-0.03),
        "minus_active_probe_value": dict(probe=-0.16, detect=-0.08, repair=-0.07, cal=0.03),
        "minus_repair_memory": dict(repair=-0.13, detect=-0.02, bloat=0.03, robust=-0.01),
        "minus_false_abstention_penalty": dict(abstain=0.12, safety=0.09, robust=-0.02),
        "minus_calibrated_risk": dict(cal=0.13, safety=-0.05, bloat=0.06),
        "variance_only_bloat_score": dict(detect=-0.12, repair=-0.23, probe=-0.16, abstain=0.07, bloat=0.24, cal=0.10),
        "abstain_only_policy": dict(detect=-0.42, repair=-0.25, probe=-0.18, abstain=0.36, safety=0.18, robust=-0.12, bloat=0.34),
        "probe_without_repair_memory": dict(repair=-0.18, probe=0.04, detect=-0.02, bloat=0.08),
    }
    base = dict(method_config("mechanics_gap_auditor_v5"))
    for key, delta in ablation_overrides.get(method, {}).items():
        base[key] = base.get(key, 0.0) + delta
    return base


def simulate(method, episode, seed, context):
    rng = stable_rng("simulate", method, seed, context, episode["split"], episode["task"], episode["episode"])
    cfg = method_config(method)
    severity = episode["severity"]
    hidden = episode["hidden_present"]
    dropout = episode["sensor_dropout"]
    aleatoric = episode["aleatoric_noise"]
    probe_rate = clamp(cfg["probe"] + 0.18 * episode["probe_value"] * severity)
    probed = int(rng.random() < probe_rate)
    detect_prob = clamp(cfg["detect"] + 0.28 * hidden * severity + 0.16 * probed - 0.18 * dropout - 0.08 * aleatoric)
    hidden_detected = int(rng.random() < detect_prob)
    abstain_prob = clamp(cfg["abstain"] + 0.20 * severity * (1.0 - cfg["safety"]) + 0.10 * (cfg["bloat"] > 0.45) - 0.06 * probed)
    abstained = int(rng.random() < abstain_prob)
    false_abstention = int(abstained and (not hidden or severity < 0.45))
    repair_prob = clamp(cfg["repair"] + 0.25 * hidden_detected + 0.10 * probed - 0.10 * aleatoric)
    repair_attempted = int((not abstained) and rng.random() < repair_prob)
    repair_correct_prob = clamp(0.22 + 0.58 * detect_prob + 0.16 * probed - 0.20 * aleatoric)
    repair_correct = int(repair_attempted and hidden and rng.random() < repair_correct_prob)
    unsafe_prob = clamp(
        0.07
        + 0.54 * hidden * severity
        + 0.16 * episode["damage_sensitivity"]
        - 0.44 * cfg["safety"]
        - 0.20 * repair_correct
        - 0.12 * cfg["robust"]
        + 0.06 * (repair_attempted and not repair_correct)
    )
    unsafe_action = int((not abstained) and rng.random() < unsafe_prob)
    bloat_index = clamp(
        cfg["bloat"]
        + 0.20 * aleatoric
        + 0.15 * (hidden and not hidden_detected)
        + 0.08 * false_abstention
        - 0.14 * repair_correct
        + rng.normal(0.0, 0.025)
    )
    calibration_error = clamp(cfg["cal"] + 0.18 * abs(bloat_index - hidden * severity) + 0.05 * false_abstention + rng.normal(0.0, 0.015))
    intervention_cost = clamp(0.02 + 0.09 * probed + 0.08 * abstained + 0.06 * repair_attempted + 0.03 * cfg["robust"])
    success_prob = clamp(
        episode["base_success"]
        - 0.46 * hidden * severity
        - 0.12 * aleatoric
        - 0.12 * unsafe_prob
        + 0.25 * repair_correct
        + 0.16 * cfg["robust"]
        + 0.09 * probed
        - 0.50 * abstained
        - 0.06 * max(0.0, bloat_index - 0.42)
    )
    task_success = int((not abstained) and rng.random() < success_prob and not unsafe_action)
    oracle_regret = clamp(episode["oracle_success"] - success_prob + 0.12 * unsafe_action + 0.08 * false_abstention)
    deployment_risk = clamp(0.08 + 0.52 * unsafe_prob + 0.25 * bloat_index + 0.15 * calibration_error - 0.08 * cfg["safety"] + rng.normal(0.0, 0.015))
    robust_utility = (
        task_success
        - 1.25 * unsafe_action
        - 0.45 * false_abstention
        - 0.28 * bloat_index
        - 0.32 * intervention_cost
        - 0.45 * oracle_regret
    )
    return {
        "task_success": task_success,
        "hidden_mechanism_present": hidden,
        "hidden_mechanism_detected": hidden_detected,
        "false_abstention": false_abstention,
        "unsafe_action": unsafe_action,
        "repair_attempted": repair_attempted,
        "repair_correct": repair_correct,
        "calibration_error": calibration_error,
        "bloat_index": bloat_index,
        "probe_cost": 1.0 if probed else 0.0,
        "probe_efficiency_event": 1.0 if probed and hidden_detected else 0.0,
        "intervention_cost": intervention_cost,
        "oracle_regret": oracle_regret,
        "deployment_risk": deployment_risk,
        "robust_utility": robust_utility,
        "success_prob": success_prob,
    }


def empty_acc():
    return {
        "n": 0,
        "task_success": 0.0,
        "false_abstention": 0.0,
        "unsafe_action": 0.0,
        "calibration_error": 0.0,
        "bloat_index": 0.0,
        "probe_cost": 0.0,
        "probe_efficiency_event": 0.0,
        "intervention_cost": 0.0,
        "oracle_regret": 0.0,
        "deployment_risk": 0.0,
        "robust_utility": 0.0,
        "tp": 0.0,
        "fp": 0.0,
        "fn": 0.0,
        "repair_attempted": 0.0,
        "repair_correct": 0.0,
    }


def add_to_acc(acc, row):
    acc["n"] += 1
    for key in [
        "task_success",
        "false_abstention",
        "unsafe_action",
        "calibration_error",
        "bloat_index",
        "probe_cost",
        "probe_efficiency_event",
        "intervention_cost",
        "oracle_regret",
        "deployment_risk",
        "robust_utility",
    ]:
        acc[key] += float(row[key])
    present = int(row["hidden_mechanism_present"])
    detected = int(row["hidden_mechanism_detected"])
    acc["tp"] += float(present and detected)
    acc["fp"] += float((not present) and detected)
    acc["fn"] += float(present and not detected)
    acc["repair_attempted"] += float(row["repair_attempted"])
    acc["repair_correct"] += float(row["repair_correct"])


def acc_metrics(acc):
    n = max(1, acc["n"])
    precision = acc["tp"] / max(1.0, acc["tp"] + acc["fp"])
    recall = acc["tp"] / max(1.0, acc["tp"] + acc["fn"])
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    repair_precision = acc["repair_correct"] / max(1.0, acc["repair_attempted"])
    probe_efficiency = acc["probe_efficiency_event"] / max(1.0, acc["probe_cost"])
    return {
        "task_success": acc["task_success"] / n,
        "hidden_mechanism_f1": f1,
        "false_abstention": acc["false_abstention"] / n,
        "unsafe_action": acc["unsafe_action"] / n,
        "repair_precision": repair_precision,
        "calibration_error": acc["calibration_error"] / n,
        "bloat_index": acc["bloat_index"] / n,
        "probe_efficiency": probe_efficiency,
        "intervention_cost": acc["intervention_cost"] / n,
        "oracle_regret": acc["oracle_regret"] / n,
        "deployment_risk": acc["deployment_risk"] / n,
        "robust_utility": acc["robust_utility"] / n,
    }


def ci95(values):
    values = list(values)
    if len(values) <= 1:
        return 0.0
    return 1.96 * float(np.std(values, ddof=1)) / math.sqrt(len(values))


def write_rows(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def stream_main():
    raw_path = RESULTS / "rollouts.csv"
    dataset_path = RESULTS / "dataset_summary.csv"
    raw_fields = [
        "seed",
        "split",
        "task",
        "episode",
        "method",
        "gap_kind",
        "severity",
        "hidden_mechanism_present",
        "hidden_mechanism_detected",
        "task_success",
        "false_abstention",
        "unsafe_action",
        "repair_attempted",
        "repair_correct",
        "calibration_error",
        "bloat_index",
        "probe_cost",
        "probe_efficiency_event",
        "intervention_cost",
        "oracle_regret",
        "deployment_risk",
        "robust_utility",
    ]
    dataset_fields = [
        "seed",
        "split",
        "task",
        "episode",
        "gap_kind",
        "hidden_present",
        "severity",
        "aleatoric_noise",
        "contact_shift",
        "friction_shift",
        "saturation_shift",
        "sensor_dropout",
        "latency",
        "fixture_shift",
        "oracle_success",
    ]
    acc = defaultdict(empty_acc)
    raw_rows = 0
    dataset_rows = 0
    with raw_path.open("w", newline="", encoding="utf-8") as raw_handle, dataset_path.open("w", newline="", encoding="utf-8") as data_handle:
        raw_writer = csv.DictWriter(raw_handle, fieldnames=raw_fields)
        data_writer = csv.DictWriter(data_handle, fieldnames=dataset_fields)
        raw_writer.writeheader()
        data_writer.writeheader()
        for split in SPLITS:
            for seed in SEEDS:
                for task_row in TASKS:
                    for episode_idx in range(MAIN_EPISODES_PER_TASK):
                        ep = make_episode(seed, split, task_row, episode_idx, phase="main")
                        data_writer.writerow(
                            {
                                "seed": seed,
                                "split": split,
                                "task": ep["task"],
                                "episode": episode_idx,
                                "gap_kind": ep["gap_kind"],
                                "hidden_present": ep["hidden_present"],
                                "severity": f"{ep['severity']:.5f}",
                                "aleatoric_noise": f"{ep['aleatoric_noise']:.5f}",
                                "contact_shift": f"{ep['contact_shift']:.5f}",
                                "friction_shift": f"{ep['friction_shift']:.5f}",
                                "saturation_shift": f"{ep['saturation_shift']:.5f}",
                                "sensor_dropout": f"{ep['sensor_dropout']:.5f}",
                                "latency": f"{ep['latency']:.5f}",
                                "fixture_shift": f"{ep['fixture_shift']:.5f}",
                                "oracle_success": f"{ep['oracle_success']:.5f}",
                            }
                        )
                        dataset_rows += 1
                        for method in METHODS:
                            sim = simulate(method, ep, seed, "main")
                            row = {
                                "seed": seed,
                                "split": split,
                                "task": ep["task"],
                                "episode": episode_idx,
                                "method": method,
                                "gap_kind": ep["gap_kind"],
                                "severity": f"{ep['severity']:.5f}",
                            }
                            for key in raw_fields[7:]:
                                value = sim[key] if key in sim else sim[key.replace("hidden_mechanism_", "hidden_mechanism_")]
                                row[key] = f"{value:.5f}" if isinstance(value, float) else value
                            raw_writer.writerow(row)
                            add_to_acc(acc[(split, method, seed)], sim)
                            raw_rows += 1
                print(f"main split={split} seed={seed} rows={raw_rows}")
    seed_rows = seed_rows_from_acc(acc, ["split", "method", "seed"])
    write_rows(RESULTS / "raw_seed_metrics.csv", ["split", "method", "seed", "rows"] + METRICS, seed_rows)
    metrics = aggregate_metrics(seed_rows, ["split", "method"])
    write_rows(RESULTS / "metrics.csv", ["split", "method", "metric", "mean", "ci95", "seeds", "rows_per_seed"], metrics)
    pairwise = pairwise_stats(seed_rows, "mechanics_gap_auditor_v5", METHODS, PAIRWISE_METRICS, ["split"])
    write_rows(RESULTS / "pairwise_stats.csv", ["split", "reference", "metric", "mean_diff", "ci95_diff", "lower95_diff", "upper95_diff", "seeds"], pairwise)
    hard_seed = hard_aggregate_seed_rows(seed_rows)
    write_rows(RESULTS / "hard_aggregate_seed_metrics.csv", ["split", "method", "seed", "rows"] + METRICS, hard_seed)
    hard_metrics = aggregate_metrics(hard_seed, ["split", "method"])
    write_rows(RESULTS / "hard_aggregate_metrics.csv", ["split", "method", "metric", "mean", "ci95", "seeds", "rows_per_seed"], hard_metrics)
    hard_pairwise = pairwise_stats(hard_seed, "mechanics_gap_auditor_v5", METHODS, PAIRWISE_METRICS, ["split"])
    write_rows(RESULTS / "hard_aggregate_pairwise_stats.csv", ["split", "reference", "metric", "mean_diff", "ci95_diff", "lower95_diff", "upper95_diff", "seeds"], hard_pairwise)
    return raw_rows, dataset_rows, seed_rows, metrics, pairwise, hard_seed, hard_metrics, hard_pairwise


def seed_rows_from_acc(acc, group_names):
    rows = []
    for key in sorted(acc):
        metrics = acc_metrics(acc[key])
        row = {name: value for name, value in zip(group_names, key)}
        row["rows"] = acc[key]["n"]
        row.update({metric: f"{metrics[metric]:.5f}" for metric in METRICS})
        rows.append(row)
    return rows


def aggregate_metrics(seed_rows, group_fields):
    grouped = defaultdict(list)
    for row in seed_rows:
        group_key = tuple(row[field] for field in group_fields)
        for metric in METRICS:
            grouped[(group_key, metric)].append(float(row[metric]))
    out = []
    for (group_key, metric), values in sorted(grouped.items()):
        row = {field: value for field, value in zip(group_fields, group_key)}
        row.update(
            {
                "metric": metric,
                "mean": f"{np.mean(values):.5f}",
                "ci95": f"{ci95(values):.5f}",
                "seeds": len(values),
                "rows_per_seed": int(np.mean([int(r["rows"]) for r in seed_rows if tuple(r[field] for field in group_fields) == group_key])),
            }
        )
        out.append(row)
    return out


def pairwise_stats(seed_rows, proposal, methods, metrics, group_fields):
    by_key = {}
    for row in seed_rows:
        group_key = tuple(row[field] for field in group_fields)
        by_key[(group_key, row["method"], int(row["seed"]))] = row
    out = []
    refs = [method for method in methods if method != proposal]
    groups = sorted({tuple(row[field] for field in group_fields) for row in seed_rows})
    seeds = sorted({int(row["seed"]) for row in seed_rows})
    for group_key in groups:
        for ref in refs:
            for metric in metrics:
                diffs = []
                for seed in seeds:
                    prop_row = by_key.get((group_key, proposal, seed))
                    ref_row = by_key.get((group_key, ref, seed))
                    if prop_row and ref_row:
                        diffs.append(float(prop_row[metric]) - float(ref_row[metric]))
                if not diffs:
                    continue
                mean = float(np.mean(diffs))
                ci = ci95(diffs)
                row = {field: value for field, value in zip(group_fields, group_key)}
                row.update(
                    {
                        "reference": ref,
                        "metric": metric,
                        "mean_diff": f"{mean:.5f}",
                        "ci95_diff": f"{ci:.5f}",
                        "lower95_diff": f"{mean - ci:.5f}",
                        "upper95_diff": f"{mean + ci:.5f}",
                        "seeds": len(diffs),
                    }
                )
                out.append(row)
    return out


def hard_aggregate_seed_rows(seed_rows):
    grouped = defaultdict(lambda: defaultdict(float))
    rows_count = defaultdict(int)
    for row in seed_rows:
        if row["split"] not in HARD_SPLITS:
            continue
        key = ("hard_aggregate", row["method"], int(row["seed"]))
        rows_count[key] += int(row["rows"])
        for metric in METRICS:
            grouped[key][metric] += float(row[metric]) * int(row["rows"])
    out = []
    for key in sorted(grouped):
        n = rows_count[key]
        row = {"split": key[0], "method": key[1], "seed": key[2], "rows": n}
        for metric in METRICS:
            row[metric] = f"{grouped[key][metric] / n:.5f}"
        out.append(row)
    return out


def run_ablation():
    raw_path = RESULTS / "ablation_rollouts.csv"
    raw_fields = [
        "seed",
        "split",
        "task",
        "episode",
        "ablation",
        "gap_kind",
        "severity",
        "hidden_mechanism_present",
        "hidden_mechanism_detected",
        "task_success",
        "false_abstention",
        "unsafe_action",
        "repair_attempted",
        "repair_correct",
        "calibration_error",
        "bloat_index",
        "probe_cost",
        "probe_efficiency_event",
        "intervention_cost",
        "oracle_regret",
        "deployment_risk",
        "robust_utility",
    ]
    acc = defaultdict(empty_acc)
    raw_rows = 0
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fields)
        writer.writeheader()
        for split in ["missing_contact_mode_shift", "combined_missing_mechanics"]:
            for seed in SEEDS:
                for task_row in TASKS:
                    for episode_idx in range(ABLATION_EPISODES_PER_TASK):
                        ep = make_episode(seed, split, task_row, episode_idx, phase="ablation")
                        for ablation in ABLATIONS:
                            sim = simulate(ablation, ep, seed, "ablation")
                            row = {
                                "seed": seed,
                                "split": split,
                                "task": ep["task"],
                                "episode": episode_idx,
                                "ablation": ablation,
                                "gap_kind": ep["gap_kind"],
                                "severity": f"{ep['severity']:.5f}",
                            }
                            for key in raw_fields[7:]:
                                value = sim[key]
                                row[key] = f"{value:.5f}" if isinstance(value, float) else value
                            writer.writerow(row)
                            add_to_acc(acc[(split, ablation, seed)], sim)
                            raw_rows += 1
                print(f"ablation split={split} seed={seed} rows={raw_rows}")
    seed_rows = []
    for key in sorted(acc):
        metrics = acc_metrics(acc[key])
        row = {"split": key[0], "ablation": key[1], "seed": key[2], "rows": acc[key]["n"]}
        row.update({metric: f"{metrics[metric]:.5f}" for metric in METRICS})
        seed_rows.append(row)
    write_rows(RESULTS / "ablation_seed_metrics.csv", ["split", "ablation", "seed", "rows"] + METRICS, seed_rows)
    metric_rows = []
    metric_long = []
    for split in ["missing_contact_mode_shift", "combined_missing_mechanics"]:
        for ablation in ABLATIONS:
            rows = [row for row in seed_rows if row["split"] == split and row["ablation"] == ablation]
            out = {"split": split, "ablation": ablation}
            for metric in METRICS:
                values = [float(row[metric]) for row in rows]
                out[metric] = f"{np.mean(values):.5f}"
                out[f"{metric}_ci95"] = f"{ci95(values):.5f}"
                metric_long.append(
                    {
                        "split": split,
                        "ablation": ablation,
                        "metric": metric,
                        "mean": f"{np.mean(values):.5f}",
                        "ci95": f"{ci95(values):.5f}",
                        "seeds": len(values),
                    }
                )
            metric_rows.append(out)
    ablation_fields = ["split", "ablation"] + [item for metric in METRICS for item in (metric, f"{metric}_ci95")]
    write_rows(RESULTS / "ablation_metrics.csv", ablation_fields, metric_rows)
    write_rows(RESULTS / "ablation_metric_long.csv", ["split", "ablation", "metric", "mean", "ci95", "seeds"], metric_long)
    return raw_rows, seed_rows, metric_rows


def run_stress():
    raw_path = RESULTS / "stress_sweep_raw.csv"
    raw_fields = [
        "stress_axis",
        "stress_level",
        "seed",
        "task",
        "episode",
        "method",
        "gap_kind",
        "severity",
        "hidden_mechanism_present",
        "hidden_mechanism_detected",
        "task_success",
        "false_abstention",
        "unsafe_action",
        "repair_attempted",
        "repair_correct",
        "calibration_error",
        "bloat_index",
        "probe_cost",
        "probe_efficiency_event",
        "intervention_cost",
        "oracle_regret",
        "deployment_risk",
        "robust_utility",
    ]
    acc = defaultdict(empty_acc)
    raw_rows = 0
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fields)
        writer.writeheader()
        for axis in STRESS_AXES:
            for level in STRESS_LEVELS:
                for seed in SEEDS:
                    for task_row in TASKS:
                        for episode_idx in range(STRESS_EPISODES_PER_TASK):
                            ep = make_episode(seed, "combined_missing_mechanics", task_row, episode_idx, stress_axis=axis, stress_level=level, phase="stress")
                            for method in STRESS_METHODS:
                                sim = simulate(method, ep, seed, f"stress-{axis}-{level}")
                                row = {
                                    "stress_axis": axis,
                                    "stress_level": f"{level:.1f}",
                                    "seed": seed,
                                    "task": ep["task"],
                                    "episode": episode_idx,
                                    "method": method,
                                    "gap_kind": ep["gap_kind"],
                                    "severity": f"{ep['severity']:.5f}",
                                }
                                for key in raw_fields[8:]:
                                    value = sim[key]
                                    row[key] = f"{value:.5f}" if isinstance(value, float) else value
                                writer.writerow(row)
                                add_to_acc(acc[(axis, f"{level:.1f}", method, seed)], sim)
                                raw_rows += 1
                print(f"stress axis={axis} level={level:.1f} rows={raw_rows}")
    seed_rows = []
    for key in sorted(acc):
        metrics = acc_metrics(acc[key])
        row = {"stress_axis": key[0], "stress_level": key[1], "method": key[2], "seed": key[3], "rows": acc[key]["n"]}
        row.update({metric: f"{metrics[metric]:.5f}" for metric in METRICS})
        seed_rows.append(row)
    write_rows(RESULTS / "stress_sweep_seed_metrics.csv", ["stress_axis", "stress_level", "method", "seed", "rows"] + METRICS, seed_rows)
    metric_rows = []
    metric_long = []
    for axis in STRESS_AXES:
        for level in [f"{x:.1f}" for x in STRESS_LEVELS]:
            for method in STRESS_METHODS:
                rows = [row for row in seed_rows if row["stress_axis"] == axis and row["stress_level"] == level and row["method"] == method]
                out = {"stress_axis": axis, "stress_level": level, "method": method}
                for metric in METRICS:
                    values = [float(row[metric]) for row in rows]
                    out[metric] = f"{np.mean(values):.5f}"
                    out[f"{metric}_ci95"] = f"{ci95(values):.5f}"
                    metric_long.append({"stress_axis": axis, "stress_level": level, "method": method, "metric": metric, "mean": f"{np.mean(values):.5f}", "ci95": f"{ci95(values):.5f}", "seeds": len(values)})
                metric_rows.append(out)
    stress_fields = ["stress_axis", "stress_level", "method"] + [item for metric in METRICS for item in (metric, f"{metric}_ci95")]
    write_rows(RESULTS / "stress_sweep.csv", stress_fields, metric_rows)
    write_rows(RESULTS / "stress_sweep_metric_long.csv", ["stress_axis", "stress_level", "method", "metric", "mean", "ci95", "seeds"], metric_long)
    return raw_rows, seed_rows, metric_rows


def run_fixed_risk():
    raw_path = RESULTS / "fixed_risk_raw.csv"
    raw_fields = [
        "split",
        "risk_budget",
        "seed",
        "task",
        "episode",
        "method",
        "gap_kind",
        "severity",
        "accepted",
        "task_success",
        "false_abstention",
        "unsafe_action",
        "bloat_index",
        "deployment_risk",
        "robust_utility",
    ]
    acc = defaultdict(lambda: defaultdict(float))
    raw_rows = 0
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fields)
        writer.writeheader()
        for split in FIXED_SPLITS:
            for seed in SEEDS:
                for task_row in TASKS:
                    for episode_idx in range(FIXED_EPISODES_PER_TASK):
                        ep = make_episode(seed, split, task_row, episode_idx, phase="fixed")
                        for budget in RISK_BUDGETS:
                            for method in FIXED_METHODS:
                                sim = simulate(method, ep, seed, f"fixed-{budget}")
                                accepted = int(sim["deployment_risk"] <= budget)
                                key = (split, f"{budget:.2f}", method, seed)
                                acc[key]["n"] += 1
                                acc[key]["accepted"] += accepted
                                acc[key]["mean_risk"] += sim["deployment_risk"]
                                if accepted:
                                    for metric in ["task_success", "false_abstention", "unsafe_action", "bloat_index", "robust_utility"]:
                                        acc[key][metric] += sim[metric]
                                row = {
                                    "split": split,
                                    "risk_budget": f"{budget:.2f}",
                                    "seed": seed,
                                    "task": ep["task"],
                                    "episode": episode_idx,
                                    "method": method,
                                    "gap_kind": ep["gap_kind"],
                                    "severity": f"{ep['severity']:.5f}",
                                    "accepted": accepted,
                                    "task_success": sim["task_success"],
                                    "false_abstention": sim["false_abstention"],
                                    "unsafe_action": sim["unsafe_action"],
                                    "bloat_index": f"{sim['bloat_index']:.5f}",
                                    "deployment_risk": f"{sim['deployment_risk']:.5f}",
                                    "robust_utility": f"{sim['robust_utility']:.5f}",
                                }
                                writer.writerow(row)
                                raw_rows += 1
                print(f"fixed-risk split={split} seed={seed} rows={raw_rows}")
    seed_rows = []
    for key in sorted(acc):
        n = max(1.0, acc[key]["n"])
        accepted = acc[key]["accepted"]
        row = {
            "split": key[0],
            "risk_budget": key[1],
            "method": key[2],
            "seed": key[3],
            "rows": int(n),
            "coverage": f"{accepted / n:.5f}",
            "accepted_success": f"{acc[key]['task_success'] / max(1.0, accepted):.5f}",
            "accepted_false_abstention": f"{acc[key]['false_abstention'] / max(1.0, accepted):.5f}",
            "accepted_unsafe_action": f"{acc[key]['unsafe_action'] / max(1.0, accepted):.5f}",
            "accepted_bloat_index": f"{acc[key]['bloat_index'] / max(1.0, accepted):.5f}",
            "accepted_utility": f"{acc[key]['robust_utility'] / max(1.0, accepted):.5f}",
            "mean_risk": f"{acc[key]['mean_risk'] / n:.5f}",
        }
        seed_rows.append(row)
    fixed_seed_fields = ["split", "risk_budget", "method", "seed", "rows", "coverage", "accepted_success", "accepted_false_abstention", "accepted_unsafe_action", "accepted_bloat_index", "accepted_utility", "mean_risk"]
    write_rows(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed_fields, seed_rows)
    metric_rows = []
    for split in FIXED_SPLITS:
        for budget in [f"{b:.2f}" for b in RISK_BUDGETS]:
            for method in FIXED_METHODS:
                rows = [row for row in seed_rows if row["split"] == split and row["risk_budget"] == budget and row["method"] == method]
                out = {"split": split, "risk_budget": budget, "method": method, "seeds": len(rows), "rows_per_seed": int(np.mean([int(r["rows"]) for r in rows]))}
                for metric in ["coverage", "accepted_success", "accepted_false_abstention", "accepted_unsafe_action", "accepted_bloat_index", "accepted_utility", "mean_risk"]:
                    values = [float(row[metric]) for row in rows]
                    out[metric] = f"{np.mean(values):.5f}"
                    out[f"{metric}_ci95"] = f"{ci95(values):.5f}"
                metric_rows.append(out)
    fields = ["split", "risk_budget", "method", "seeds", "rows_per_seed"] + [item for metric in ["coverage", "accepted_success", "accepted_false_abstention", "accepted_unsafe_action", "accepted_bloat_index", "accepted_utility", "mean_risk"] for item in (metric, f"{metric}_ci95")]
    write_rows(RESULTS / "fixed_risk_metrics.csv", fields, metric_rows)
    pairwise = fixed_pairwise(seed_rows)
    write_rows(RESULTS / "fixed_risk_pairwise.csv", ["split", "risk_budget", "reference", "metric", "mean_diff", "ci95_diff", "lower95_diff", "upper95_diff", "seeds"], pairwise)
    return raw_rows, seed_rows, metric_rows, pairwise


def fixed_pairwise(seed_rows):
    proposal = "mechanics_gap_auditor_v5"
    refs = [m for m in FIXED_METHODS if m != proposal]
    by_key = {(r["split"], r["risk_budget"], r["method"], int(r["seed"])): r for r in seed_rows}
    out = []
    for split in FIXED_SPLITS:
        for budget in [f"{b:.2f}" for b in RISK_BUDGETS]:
            for ref in refs:
                for metric in FIXED_PAIRWISE_METRICS:
                    diffs = []
                    for seed in SEEDS:
                        prop = by_key.get((split, budget, proposal, seed))
                        base = by_key.get((split, budget, ref, seed))
                        if prop and base:
                            diffs.append(float(prop[metric]) - float(base[metric]))
                    mean = float(np.mean(diffs))
                    ci = ci95(diffs)
                    out.append({"split": split, "risk_budget": budget, "reference": ref, "metric": metric, "mean_diff": f"{mean:.5f}", "ci95_diff": f"{ci:.5f}", "lower95_diff": f"{mean - ci:.5f}", "upper95_diff": f"{mean + ci:.5f}", "seeds": len(diffs)})
    return out


def write_negative_cases():
    families = [
        ("aleatoric_noise_as_mechanics", "variance should not become a false missing-mechanics diagnosis", "noise inflated as hidden contact gap", "separate aleatoric noise from repairable structure"),
        ("hidden_contact_mode_bloat", "high variance should trigger mode identification", "uncertainty gate abstains without repair", "probe for contact mode rather than only abstaining"),
        ("robust_fallback_overrepair", "robust fallback may safely solve the case", "audit repairs a mechanism that robust MPC absorbs", "repair must beat conservative control"),
        ("conformal_zero_coverage", "safety without useful coverage is not deployable", "conformal gate rejects every hard episode", "report coverage with accepted safety"),
        ("stale_repair_memory", "repair memory should not transfer stale mechanisms", "old fixture repair corrupts new task", "mechanism memory needs expiry"),
        ("dropout_false_gap", "sensor dropout should not imply physical gap", "missing pixels become missing mechanics", "diagnosis needs observation-quality state"),
    ]
    rows = []
    for family, expected, failure, lesson in families:
        for idx in range(4):
            rows.append({"case_id": f"{family}_{idx}", "case_family": family, "expected_behavior": expected, "observed_failure_mode": f"variant {idx}: {failure}", "terminal_lesson": lesson})
    write_rows(RESULTS / "negative_cases.csv", ["case_id", "case_family", "expected_behavior", "observed_failure_mode", "terminal_lesson"], rows)
    return rows


def metric_value(rows, split, method, metric):
    for row in rows:
        if row.get("split") == split and row.get("method") == method and row.get("metric") == metric:
            return float(row["mean"]), float(row["ci95"])
    raise KeyError((split, method, metric))


def pair_value(rows, reference, metric):
    for row in rows:
        if row["split"] == "hard_aggregate" and row["reference"] == reference and row["metric"] == metric:
            return float(row["mean_diff"]), float(row["ci95_diff"]), float(row["lower95_diff"]), float(row["upper95_diff"])
    raise KeyError((reference, metric))


def terminal_decision(hard_metrics, hard_pairs, ablation_metrics, stress_metrics, fixed_metrics):
    proposal = "mechanics_gap_auditor_v5"
    non_oracle = [m for m in METHODS if not m.startswith("oracle") and m != proposal]
    prop_success = metric_value(hard_metrics, "hard_aggregate", proposal, "task_success")
    best_success_ref = max(non_oracle, key=lambda m: metric_value(hard_metrics, "hard_aggregate", m, "task_success")[0])
    best_f1_ref = max(non_oracle, key=lambda m: metric_value(hard_metrics, "hard_aggregate", m, "hidden_mechanism_f1")[0])
    safest_ref = min(non_oracle, key=lambda m: metric_value(hard_metrics, "hard_aggregate", m, "unsafe_action")[0])
    lowest_abstain_ref = min(non_oracle, key=lambda m: metric_value(hard_metrics, "hard_aggregate", m, "false_abstention")[0])
    lowest_bloat_ref = min(non_oracle, key=lambda m: metric_value(hard_metrics, "hard_aggregate", m, "bloat_index")[0])
    best_utility_ref = max(non_oracle, key=lambda m: metric_value(hard_metrics, "hard_aggregate", m, "robust_utility")[0])
    paired_success = pair_value(hard_pairs, best_success_ref, "task_success")
    paired_unsafe = pair_value(hard_pairs, safest_ref, "unsafe_action")
    prop_f1 = metric_value(hard_metrics, "hard_aggregate", proposal, "hidden_mechanism_f1")
    prop_unsafe = metric_value(hard_metrics, "hard_aggregate", proposal, "unsafe_action")
    prop_abstain = metric_value(hard_metrics, "hard_aggregate", proposal, "false_abstention")
    prop_bloat = metric_value(hard_metrics, "hard_aggregate", proposal, "bloat_index")
    prop_utility = metric_value(hard_metrics, "hard_aggregate", proposal, "robust_utility")
    best_success = metric_value(hard_metrics, "hard_aggregate", best_success_ref, "task_success")
    best_f1 = metric_value(hard_metrics, "hard_aggregate", best_f1_ref, "hidden_mechanism_f1")
    safest = metric_value(hard_metrics, "hard_aggregate", safest_ref, "unsafe_action")
    lowest_abstain = metric_value(hard_metrics, "hard_aggregate", lowest_abstain_ref, "false_abstention")
    lowest_bloat = metric_value(hard_metrics, "hard_aggregate", lowest_bloat_ref, "bloat_index")
    best_utility = metric_value(hard_metrics, "hard_aggregate", best_utility_ref, "robust_utility")
    full_rows = [r for r in ablation_metrics if r["ablation"] == "full_mechanics_gap_auditor_v5"]
    mechanism_pass = True
    for split in ["missing_contact_mode_shift", "combined_missing_mechanics"]:
        full = [r for r in full_rows if r["split"] == split][0]
        full_utility = float(full["robust_utility"])
        for row in [r for r in ablation_metrics if r["split"] == split and r["ablation"] != "full_mechanics_gap_auditor_v5"]:
            if full_utility - float(row["robust_utility"]) < 0.015:
                mechanism_pass = False
            if float(row["task_success"]) > float(full["task_success"]) and float(row["unsafe_action"]) <= float(full["unsafe_action"]):
                mechanism_pass = False
    max_combined = [r for r in stress_metrics if r["stress_axis"] == "combined" and r["stress_level"] == "1.0"]
    prop_stress = [r for r in max_combined if r["method"] == proposal][0]
    dominated_by = []
    for row in max_combined:
        if row["method"] == proposal or row["method"].startswith("oracle"):
            continue
        better_or_equal = (
            float(row["task_success"]) >= float(prop_stress["task_success"])
            and float(row["unsafe_action"]) <= float(prop_stress["unsafe_action"])
            and float(row["false_abstention"]) <= float(prop_stress["false_abstention"])
            and float(row["bloat_index"]) <= float(prop_stress["bloat_index"])
            and float(row["robust_utility"]) >= float(prop_stress["robust_utility"])
        )
        strictly = (
            float(row["task_success"]) > float(prop_stress["task_success"])
            or float(row["unsafe_action"]) < float(prop_stress["unsafe_action"])
            or float(row["false_abstention"]) < float(prop_stress["false_abstention"])
            or float(row["bloat_index"]) < float(prop_stress["bloat_index"])
            or float(row["robust_utility"]) > float(prop_stress["robust_utility"])
        )
        if better_or_equal and strictly:
            dominated_by.append(row["method"])
    stress_gate = not dominated_by
    fixed_gate = True
    fixed_notes = []
    for split in FIXED_SPLITS:
        rows = [r for r in fixed_metrics if r["split"] == split and r["risk_budget"] == "0.05"]
        prop = [r for r in rows if r["method"] == proposal][0]
        feasible = [r for r in rows if float(r["coverage"]) > 0.0 and not r["method"].startswith("oracle")]
        best_cov = max([float(r["coverage"]) for r in feasible], default=0.0)
        best_success_feasible = max([float(r["accepted_success"]) for r in feasible], default=0.0)
        best_safe_feasible = min([float(r["accepted_unsafe_action"]) for r in feasible], default=1.0)
        if float(prop["coverage"]) <= 0.0:
            fixed_gate = False
        if feasible and float(prop["coverage"]) + 1e-9 < best_cov:
            fixed_gate = False
        if feasible and float(prop["accepted_success"]) + 0.02 < best_success_feasible:
            fixed_gate = False
        if feasible and float(prop["accepted_unsafe_action"]) > best_safe_feasible + 0.01:
            fixed_gate = False
        fixed_notes.append(
            f"{split}: v5_coverage={float(prop['coverage']):.5f}, best_feasible_coverage={best_cov:.5f}, "
            f"v5_success={float(prop['accepted_success']):.5f}, best_feasible_success={best_success_feasible:.5f}, "
            f"v5_unsafe={float(prop['accepted_unsafe_action']):.5f}, best_feasible_unsafe={best_safe_feasible:.5f}"
        )
    main_gate = (
        prop_success[0] - best_success[0] >= 0.030
        and prop_f1[0] - best_f1[0] >= 0.030
        and prop_unsafe[0] <= safest[0] + 0.010
        and prop_abstain[0] <= lowest_abstain[0] + 0.020
        and lowest_bloat[0] - prop_bloat[0] >= 0.050
        and paired_success[2] > 0.0
        and paired_unsafe[3] <= 0.010
    )
    scope_gate = False
    terminal = "STRONG_REVISE" if all([main_gate, mechanism_pass, stress_gate, fixed_gate, scope_gate]) else "KILL_ARCHIVE"
    return {
        "terminal": terminal,
        "best_success_reference": best_success_ref,
        "best_f1_reference": best_f1_ref,
        "safest_reference": safest_ref,
        "lowest_abstain_reference": lowest_abstain_ref,
        "lowest_bloat_reference": lowest_bloat_ref,
        "best_utility_reference": best_utility_ref,
        "proposal_success": prop_success[0],
        "best_success": best_success[0],
        "proposal_f1": prop_f1[0],
        "best_f1": best_f1[0],
        "proposal_unsafe": prop_unsafe[0],
        "safest_unsafe": safest[0],
        "proposal_abstain": prop_abstain[0],
        "lowest_abstain": lowest_abstain[0],
        "proposal_bloat": prop_bloat[0],
        "lowest_bloat": lowest_bloat[0],
        "proposal_utility": prop_utility[0],
        "best_utility": best_utility[0],
        "paired_success_lower95": paired_success[2],
        "paired_unsafe_upper95": paired_unsafe[3],
        "main_gate": main_gate,
        "mechanism_gate": mechanism_pass,
        "stress_gate": stress_gate,
        "stress_dominated_by": ",".join(sorted(set(dominated_by))) if dominated_by else "none",
        "fixed_risk_gate": fixed_gate,
        "scope_gate": scope_gate,
        "fixed_notes": " | ".join(fixed_notes),
    }


def plot_results(hard_metrics, ablation_metrics, stress_metrics, fixed_metrics):
    hard = [r for r in hard_metrics if r["split"] == "hard_aggregate" and r["metric"] == "task_success"]
    labels = [r["method"].replace("_", "\n") for r in hard]
    values = [float(r["mean"]) for r in hard]
    colors = ["#c94b3b" if r["method"] == "mechanics_gap_auditor_v5" else "#46789c" for r in hard]
    colors = ["#4c8c57" if r["method"].startswith("oracle") else c for r, c in zip(hard, colors)]
    plt.figure(figsize=(12, 4))
    plt.bar(range(len(values)), values, color=colors)
    plt.xticks(range(len(values)), labels, rotation=45, ha="right", fontsize=7)
    plt.ylabel("Hard aggregate task success")
    plt.title("World-model uncertainty bloat hard aggregate")
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_hard_success_v5.png", dpi=180)
    plt.close()

    focus = ["ensemble_variance_gate", "conformal_risk_gate", "active_probe_then_plan", "robust_mpc_fallback", "residual_dynamics_repair", "mechanics_gap_auditor_v5", "oracle_mechanics_repair"]
    metrics = ["unsafe_action", "false_abstention", "bloat_index"]
    x = np.arange(len(focus))
    width = 0.25
    plt.figure(figsize=(11, 4))
    for idx, metric in enumerate(metrics):
        vals = [metric_value(hard_metrics, "hard_aggregate", method, metric)[0] for method in focus]
        plt.bar(x + (idx - 1) * width, vals, width=width, label=metric)
    plt.xticks(x, [m.replace("_", "\n") for m in focus], rotation=35, ha="right", fontsize=7)
    plt.legend(fontsize=8)
    plt.title("Unsafe action, false abstention, and bloat")
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_failures_v5.png", dpi=180)
    plt.close()

    full_rows = [r for r in ablation_metrics if r["split"] == "combined_missing_mechanics"]
    plt.figure(figsize=(10, 4))
    plt.bar([r["ablation"].replace("_", "\n") for r in full_rows], [float(r["robust_utility"]) for r in full_rows], color="#9a6b3f")
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.ylabel("Robust utility")
    plt.title("Combined missing-mechanics ablation utility")
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_ablation_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 5))
    for method in STRESS_METHODS:
        rows = [r for r in stress_metrics if r["stress_axis"] == "combined" and r["method"] == method]
        rows = sorted(rows, key=lambda r: float(r["stress_level"]))
        plt.plot([float(r["stress_level"]) for r in rows], [float(r["task_success"]) for r in rows], marker="o", label=method.replace("_", " "))
    plt.xlabel("Combined stress level")
    plt.ylabel("Task success")
    plt.title("Combined stress sweep")
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_stress_sweep_v5.png", dpi=180)
    plt.close()

    with (FIGURES / "stress_curve_data_v5.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(stress_metrics[0].keys()))
        writer.writeheader()
        writer.writerows(stress_metrics)

    rows = [r for r in fixed_metrics if r["split"] == "combined_missing_mechanics"]
    plt.figure(figsize=(10, 4))
    for method in FIXED_METHODS:
        vals = [r for r in rows if r["method"] == method]
        vals = sorted(vals, key=lambda r: float(r["risk_budget"]))
        plt.plot([float(r["risk_budget"]) for r in vals], [float(r["coverage"]) for r in vals], marker="o", label=method.replace("_", " "))
    plt.xlabel("Risk budget")
    plt.ylabel("Accepted coverage")
    plt.title("Fixed-risk coverage on combined missing mechanics")
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_fixed_risk_v5.png", dpi=180)
    plt.close()

    pareto_labels = {
        "ensemble_variance_gate": "ensemble",
        "conformal_risk_gate": "conformal",
        "active_probe_then_plan": "active probe",
        "robust_mpc_fallback": "robust MPC",
        "residual_dynamics_repair": "residual repair",
        "mechanics_gap_auditor_v5": "mechanics gap v5",
        "oracle_mechanics_repair": "oracle repair",
    }
    pareto_offsets = {
        "ensemble_variance_gate": (8, 0),
        "conformal_risk_gate": (-58, -6),
        "active_probe_then_plan": (-70, 12),
        "robust_mpc_fallback": (8, 8),
        "residual_dynamics_repair": (8, -15),
        "mechanics_gap_auditor_v5": (-72, -14),
        "oracle_mechanics_repair": (8, 6),
    }
    plt.figure(figsize=(7, 5))
    for method in focus:
        success = metric_value(hard_metrics, "hard_aggregate", method, "task_success")[0]
        failure = metric_value(hard_metrics, "hard_aggregate", method, "unsafe_action")[0] + metric_value(hard_metrics, "hard_aggregate", method, "bloat_index")[0]
        plt.scatter(failure, success, s=70)
        plt.annotate(
            pareto_labels.get(method, method.replace("_", " ")),
            xy=(failure, success),
            xytext=pareto_offsets.get(method, (8, 0)),
            textcoords="offset points",
            fontsize=7,
            bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "0.75", "lw": 0.4, "alpha": 0.88},
        )
    plt.xlabel("Unsafe + bloat")
    plt.ylabel("Hard aggregate success")
    plt.title("Success-validity-bloat Pareto view")
    plt.tight_layout()
    plt.savefig(FIGURES / "uncertainty_bloat_pareto_v5.png", dpi=180)
    plt.close()


def expected_counts():
    return {
        "rollouts.csv": 199680,
        "dataset_summary.csv": 15360,
        "raw_seed_metrics.csv": 1040,
        "metrics.csv": 1248,
        "pairwise_stats.csv": 672,
        "hard_aggregate_seed_metrics.csv": 130,
        "hard_aggregate_metrics.csv": 156,
        "hard_aggregate_pairwise_stats.csv": 84,
        "ablation_rollouts.csv": 33600,
        "ablation_seed_metrics.csv": 200,
        "ablation_metrics.csv": 20,
        "ablation_metric_long.csv": 240,
        "stress_sweep_raw.csv": 302400,
        "stress_sweep_seed_metrics.csv": 2520,
        "stress_sweep.csv": 252,
        "stress_sweep_metric_long.csv": 3024,
        "fixed_risk_raw.csv": 69120,
        "fixed_risk_seed_metrics.csv": 480,
        "fixed_risk_metrics.csv": 48,
        "fixed_risk_pairwise.csv": 200,
        "negative_cases.csv": 24,
    }


def write_summary(decision, counts, hard_metrics, hard_pairs, ablation_metrics, stress_metrics, fixed_metrics, negative_count):
    lines = [
        "Paper 88 world_model_uncertainty_bloat v5 expanded audit",
        f"Terminal recommendation: {decision['terminal']}",
        "ICLR main ready: no",
        "Reason: expanded CPU-only world-model uncertainty-bloat audit adds stronger UQ, conformal, active-probe, robust-MPC, residual-repair, Bayesian-expansion, ablation, stress, and fixed-risk tests, but no real robot or accepted high-fidelity deployment benchmark evidence exists.",
    ]
    labels = {
        "rollouts.csv": "Main rollout rows",
        "dataset_summary.csv": "Dataset summary rows",
        "raw_seed_metrics.csv": "Main seed-metric rows",
        "metrics.csv": "Main metric rows",
        "pairwise_stats.csv": "Main pairwise rows",
        "hard_aggregate_seed_metrics.csv": "Hard aggregate seed rows",
        "hard_aggregate_metrics.csv": "Hard aggregate metric rows",
        "hard_aggregate_pairwise_stats.csv": "Hard aggregate pairwise rows",
        "ablation_rollouts.csv": "Ablation rollout rows",
        "ablation_seed_metrics.csv": "Ablation seed rows",
        "ablation_metrics.csv": "Ablation metric rows",
        "stress_sweep_raw.csv": "Stress raw rows",
        "stress_sweep_seed_metrics.csv": "Stress seed rows",
        "stress_sweep.csv": "Stress metric rows",
        "fixed_risk_raw.csv": "Fixed-risk raw rows",
        "fixed_risk_seed_metrics.csv": "Fixed-risk seed rows",
        "fixed_risk_metrics.csv": "Fixed-risk metric rows",
        "fixed_risk_pairwise.csv": "Fixed-risk pairwise rows",
    }
    for name, label in labels.items():
        lines.append(f"{label}: {counts[name]}")
    lines.append(f"Negative cases: {negative_count}")
    lines.extend(
        [
            "",
            "Frozen hard-aggregate gate:",
            f"best_success_reference={decision['best_success_reference']}",
            f"best_f1_reference={decision['best_f1_reference']}",
            f"safest_reference={decision['safest_reference']}",
            f"lowest_abstain_reference={decision['lowest_abstain_reference']}",
            f"lowest_bloat_reference={decision['lowest_bloat_reference']}",
            f"best_utility_reference={decision['best_utility_reference']}",
            f"proposal_success={decision['proposal_success']:.5f}",
            f"best_success={decision['best_success']:.5f}",
            f"proposal_f1={decision['proposal_f1']:.5f}",
            f"best_f1={decision['best_f1']:.5f}",
            f"proposal_unsafe={decision['proposal_unsafe']:.5f}",
            f"safest_unsafe={decision['safest_unsafe']:.5f}",
            f"proposal_abstain={decision['proposal_abstain']:.5f}",
            f"lowest_abstain={decision['lowest_abstain']:.5f}",
            f"proposal_bloat={decision['proposal_bloat']:.5f}",
            f"lowest_bloat={decision['lowest_bloat']:.5f}",
            f"proposal_utility={decision['proposal_utility']:.5f}",
            f"best_utility={decision['best_utility']:.5f}",
            f"paired_success_lower95={decision['paired_success_lower95']:.5f}",
            f"paired_unsafe_upper95={decision['paired_unsafe_upper95']:.5f}",
            f"main_gate={decision['main_gate']}",
            f"mechanism_gate={decision['mechanism_gate']}",
            f"stress_gate={decision['stress_gate']}",
            f"stress_dominated_by={decision['stress_dominated_by']}",
            f"fixed_risk_gate={decision['fixed_risk_gate']}",
            f"scope_gate={decision['scope_gate']}",
            decision["fixed_notes"],
            "",
            "Hard aggregate metrics:",
        ]
    )
    for method in METHODS:
        vals = {metric: metric_value(hard_metrics, "hard_aggregate", method, metric)[0] for metric in ["task_success", "hidden_mechanism_f1", "unsafe_action", "false_abstention", "bloat_index", "robust_utility"]}
        ci = metric_value(hard_metrics, "hard_aggregate", method, "task_success")[1]
        lines.append(
            f"{method} task_success={vals['task_success']:.5f} ci95={ci:.5f} f1={vals['hidden_mechanism_f1']:.5f} unsafe={vals['unsafe_action']:.5f} false_abstention={vals['false_abstention']:.5f} bloat={vals['bloat_index']:.5f} utility={vals['robust_utility']:.5f}"
        )
    lines.append("")
    lines.append("Key paired hard-aggregate differences:")
    for ref in [decision["best_success_reference"], decision["best_f1_reference"], decision["safest_reference"], "uncertainty_bloat_audit_v4", "robust_mpc_fallback", "active_probe_then_plan"]:
        for metric in ["task_success", "hidden_mechanism_f1", "unsafe_action", "bloat_index", "robust_utility"]:
            try:
                mean, ci, lo, hi = pair_value(hard_pairs, ref, metric)
            except KeyError:
                continue
            lines.append(f"v5_minus_{ref} {metric}: mean={mean:.5f} ci95={ci:.5f} lower95={lo:.5f} upper95={hi:.5f}")
    lines.append("")
    lines.append("Ablation utility:")
    for row in ablation_metrics:
        if row["split"] == "combined_missing_mechanics":
            lines.append(
                f"{row['ablation']} success={float(row['task_success']):.5f} f1={float(row['hidden_mechanism_f1']):.5f} unsafe={float(row['unsafe_action']):.5f} bloat={float(row['bloat_index']):.5f} utility={float(row['robust_utility']):.5f}"
            )
    lines.append("")
    lines.append("Maximum combined stress:")
    for row in stress_metrics:
        if row["stress_axis"] == "combined" and row["stress_level"] == "1.0":
            lines.append(
                f"{row['method']} task_success={float(row['task_success']):.5f} f1={float(row['hidden_mechanism_f1']):.5f} unsafe={float(row['unsafe_action']):.5f} abstain={float(row['false_abstention']):.5f} bloat={float(row['bloat_index']):.5f} utility={float(row['robust_utility']):.5f}"
            )
    lines.append("")
    lines.append("Fixed-risk budget 0.05:")
    for row in fixed_metrics:
        if row["risk_budget"] == "0.05":
            lines.append(
                f"{row['split']} {row['method']} coverage={float(row['coverage']):.5f} accepted_success={float(row['accepted_success']):.5f} accepted_unsafe={float(row['accepted_unsafe_action']):.5f} accepted_bloat={float(row['accepted_bloat_index']):.5f}"
            )
    lines.append("")
    lines.append(f"Negative cases: {negative_count}")
    lines.append(f"terminal={decision['terminal']}")
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def csv_count(name):
    with (RESULTS / name).open("r", newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main():
    main_raw, dataset_rows, seed_rows, metrics, pairwise, hard_seed, hard_metrics, hard_pairwise = stream_main()
    ablation_raw, ablation_seed, ablation_metrics = run_ablation()
    stress_raw, stress_seed, stress_metrics = run_stress()
    fixed_raw, fixed_seed, fixed_metrics, fixed_pairwise_rows = run_fixed_risk()
    negative = write_negative_cases()
    decision = terminal_decision(hard_metrics, hard_pairwise, ablation_metrics, stress_metrics, fixed_metrics)
    plot_results(hard_metrics, ablation_metrics, stress_metrics, fixed_metrics)
    counts = {name: csv_count(name) for name in expected_counts()}
    write_summary(decision, counts, hard_metrics, hard_pairwise, ablation_metrics, stress_metrics, fixed_metrics, len(negative))
    print(f"terminal={decision['terminal']}")
    print(f"main_rows={main_raw} stress_rows={stress_raw} fixed_rows={fixed_raw}")
    for name, expected in expected_counts().items():
        observed = counts[name]
        if observed != expected:
            raise SystemExit(f"row-count mismatch {name}: expected {expected}, observed {observed}")


if __name__ == "__main__":
    main()
