import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOCS = ROOT / "docs"


METHOD_LABELS = {
    "mean_world_model_mpc": "Mean WM-MPC",
    "ensemble_variance_gate": "Ensemble variance",
    "mc_dropout_uncertainty": "MC dropout",
    "conformal_risk_gate": "Conformal gate",
    "epistemic_ensemble_planner": "Epistemic planner",
    "active_probe_then_plan": "Active probe",
    "robust_mpc_fallback": "Robust MPC",
    "residual_dynamics_repair": "Residual repair",
    "bayesian_model_expansion": "Bayesian expansion",
    "uncertainty_bloat_audit_v4": "Bloat audit v4",
    "mechanics_gap_auditor_v5": "Mechanics gap v5",
    "oracle_mechanics_repair": "Oracle repair",
    "oracle_full_state_policy": "Oracle full state",
}

METHOD_ORDER = list(METHOD_LABELS)

FOCUS_METHODS = [
    "ensemble_variance_gate",
    "conformal_risk_gate",
    "active_probe_then_plan",
    "robust_mpc_fallback",
    "residual_dynamics_repair",
    "bayesian_model_expansion",
    "uncertainty_bloat_audit_v4",
    "mechanics_gap_auditor_v5",
    "oracle_mechanics_repair",
]

SPLIT_LABELS = {
    "nominal_noise": "Nominal",
    "friction_contact_shift": "Friction/contact",
    "actuator_saturation_shift": "Actuator sat.",
    "sensor_dropout_ambiguity": "Sensor dropout",
    "latency_hysteresis_shift": "Latency/hyst.",
    "latent_fixture_snag_shift": "Latent fixture",
    "missing_contact_mode_shift": "Missing contact",
    "combined_missing_mechanics": "Combined missing",
    "hard_aggregate": "Hard aggregate",
}

SPLIT_ORDER = [
    "nominal_noise",
    "friction_contact_shift",
    "actuator_saturation_shift",
    "sensor_dropout_ambiguity",
    "latency_hysteresis_shift",
    "latent_fixture_snag_shift",
    "missing_contact_mode_shift",
    "combined_missing_mechanics",
]

ABLATION_LABELS = {
    "full_mechanics_gap_auditor_v5": "Full mechanics gap v5",
    "minus_mechanism_classifier": "- mechanism classifier",
    "minus_uncertainty_bloat_index": "- bloat index",
    "minus_active_probe_value": "- active probe value",
    "minus_repair_memory": "- repair memory",
    "minus_false_abstention_penalty": "- abstention penalty",
    "minus_calibrated_risk": "- calibrated risk",
    "variance_only_bloat_score": "Variance-only bloat",
    "abstain_only_policy": "Abstain-only",
    "probe_without_repair_memory": "Probe no memory",
}

METRIC_LABELS = {
    "task_success": "Success",
    "hidden_mechanism_f1": "Mech. F1",
    "false_abstention": "False abst.",
    "unsafe_action": "Unsafe",
    "repair_precision": "Repair prec.",
    "calibration_error": "Calib.",
    "bloat_index": "Bloat",
    "probe_efficiency": "Probe eff.",
    "intervention_cost": "Cost",
    "oracle_regret": "Regret",
    "deployment_risk": "Risk",
    "robust_utility": "Utility",
    "coverage": "Coverage",
    "accepted_success": "Acc. succ.",
    "accepted_unsafe_action": "Acc. unsafe",
    "accepted_bloat_index": "Acc. bloat",
    "accepted_utility": "Acc. utility",
}

ROW_FILES = [
    "rollouts.csv",
    "dataset_summary.csv",
    "raw_seed_metrics.csv",
    "metrics.csv",
    "pairwise_stats.csv",
    "hard_aggregate_seed_metrics.csv",
    "hard_aggregate_metrics.csv",
    "hard_aggregate_pairwise_stats.csv",
    "ablation_rollouts.csv",
    "ablation_seed_metrics.csv",
    "ablation_metrics.csv",
    "stress_sweep_raw.csv",
    "stress_sweep_seed_metrics.csv",
    "stress_sweep.csv",
    "fixed_risk_raw.csv",
    "fixed_risk_seed_metrics.csv",
    "fixed_risk_metrics.csv",
    "fixed_risk_pairwise.csv",
    "negative_cases.csv",
]


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def count_rows(name):
    return len(read_csv(RESULTS / name))


def ascii_clean(text):
    text = str(text or "")
    for old, new in {
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2010": "-",
        "\u2011": "-",
        "\xa0": " ",
    }.items():
        text = text.replace(old, new)
    return text.encode("ascii", "ignore").decode("ascii")


def tex_escape(text):
    text = ascii_clean(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def table_phrase(text):
    return tex_escape(ascii_clean(text).replace("_", " "))


def method_name(method):
    return tex_escape(METHOD_LABELS.get(method, method))


def split_name(split):
    return tex_escape(SPLIT_LABELS.get(split, split))


def ablation_name(ablation):
    return tex_escape(ABLATION_LABELS.get(ablation, ablation))


def metric_name(metric):
    return tex_escape(METRIC_LABELS.get(metric, metric))


def fmt(value):
    return f"{float(value):.3f}"


def fmt_pm(mean, ci):
    return f"{float(mean):.3f} $\\pm$ {float(ci):.3f}"


def metric_lookup(rows, selectors, metric):
    for row in rows:
        if row.get("metric") != metric:
            continue
        if all(row.get(k) == v for k, v in selectors.items()):
            return float(row["mean"]), float(row["ci95"])
    raise KeyError((selectors, metric))


def parse_summary(summary_text):
    out = {}
    for line in summary_text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip()
        elif ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip()
    return out


def bib_key(i):
    return f"pool88_{i:02d}"


def write_references():
    rows = read_csv(DOCS / "deep_read_250.csv")[:96]
    entries = []
    for i, row in enumerate(rows, start=1):
        title = tex_escape(row.get("title") or "Untitled prior work")
        authors_raw = ascii_clean(row.get("authors") or "Local Prior Work Pool")
        parts = [p.strip() for p in re.split(r";| and ", authors_raw) if p.strip()]
        authors = " and ".join(tex_escape(p) for p in parts[:10]) or "Local Prior Work Pool"
        year_raw = ascii_clean(row.get("year") or "")
        match = re.search(r"(19|20)\d{2}", year_raw)
        year = match.group(0) if match else "2026"
        venue = tex_escape(row.get("venue") or row.get("source") or "prior-work pool")
        link = tex_escape(row.get("doi") or row.get("url") or row.get("arxiv_id") or row.get("uid") or "local pool record")
        entries.append(
            "\n".join(
                [
                    f"@misc{{{bib_key(i)},",
                    f"  author={{{authors}}},",
                    f"  title={{{title}}},",
                    f"  year={{{year}}},",
                    f"  note={{{venue}; {link}}}",
                    "}",
                ]
            )
        )
    (PAPER / "references.bib").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    return [bib_key(i) for i in range(1, len(rows) + 1)], rows


def longtable(header, rows, spec, caption, label, fontsize=r"\scriptsize"):
    lines = [
        r"\begin{center}",
        fontsize,
        f"\\begin{{longtable}}{{{spec}}}",
        f"\\caption{{{caption}}}\\label{{{label}}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endfirsthead",
        f"\\caption[]{{{caption} (continued)}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endhead",
    ]
    lines.extend(rows)
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\normalsize", r"\end{center}"])
    return "\n".join(lines)


def row_count_table():
    rows = [f"{tex_escape(name)} & {count_rows(name):,}\\\\" for name in ROW_FILES]
    return longtable(
        "Evidence file & Data rows",
        rows,
        "p{0.55\\linewidth}r",
        "Reproducibility inventory. Counts exclude CSV headers and are regenerated directly from the files used in the manuscript.",
        "tab:inventory",
    )


def hard_table(hard_metrics):
    rows = []
    for method in METHOD_ORDER:
        success = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "task_success")
        f1 = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "hidden_mechanism_f1")
        unsafe = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "unsafe_action")
        abstain = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "false_abstention")
        bloat = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "bloat_index")
        utility = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "robust_utility")
        rows.append(
            f"{method_name(method)} & {fmt_pm(*success)} & {f1[0]:.3f} & {unsafe[0]:.3f} & {abstain[0]:.3f} & {bloat[0]:.3f} & {utility[0]:.3f}\\\\"
        )
    return longtable(
        "Method & Success & Mech. F1 & Unsafe & False abst. & Bloat & Utility",
        rows,
        "p{0.27\\linewidth}rrrrrr",
        "Predefined hard-aggregate results over latent fixture, missing contact mode, and combined missing mechanics.",
        "tab:hard",
    )


def split_table(metrics):
    rows = []
    for split in SPLIT_ORDER:
        for method in FOCUS_METHODS:
            success = metric_lookup(metrics, {"split": split, "method": method}, "task_success")
            f1 = metric_lookup(metrics, {"split": split, "method": method}, "hidden_mechanism_f1")
            unsafe = metric_lookup(metrics, {"split": split, "method": method}, "unsafe_action")
            bloat = metric_lookup(metrics, {"split": split, "method": method}, "bloat_index")
            utility = metric_lookup(metrics, {"split": split, "method": method}, "robust_utility")
            rows.append(f"{split_name(split)} & {method_name(method)} & {fmt_pm(*success)} & {f1[0]:.3f} & {unsafe[0]:.3f} & {bloat[0]:.3f} & {utility[0]:.3f}\\\\")
    return longtable(
        "Split & Method & Success & Mech. F1 & Unsafe & Bloat & Utility",
        rows,
        "p{0.16\\linewidth}p{0.25\\linewidth}rrrrr",
        "Split-level results for uncertainty, active-probe, robust, repair, v4, v5, and oracle methods.",
        "tab:split",
    )


def pairwise_table(hard_pairs, summary):
    refs = [
        summary["best_success_reference"],
        summary["best_f1_reference"],
        summary["safest_reference"],
        "active_probe_then_plan",
        "robust_mpc_fallback",
        "uncertainty_bloat_audit_v4",
    ]
    metrics = ["task_success", "hidden_mechanism_f1", "unsafe_action", "bloat_index", "robust_utility"]
    seen = set()
    rows = []
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        for metric in metrics:
            matches = [r for r in hard_pairs if r["split"] == "hard_aggregate" and r["reference"] == ref and r["metric"] == metric]
            if not matches:
                continue
            row = matches[0]
            rows.append(f"{method_name(ref)} & {metric_name(metric)} & {fmt(row['mean_diff'])} & {fmt(row['ci95_diff'])} & {fmt(row['lower95_diff'])} & {fmt(row['upper95_diff'])}\\\\")
    return longtable(
        "Reference & Metric & Mean diff & CI95 & Lower95 & Upper95",
        rows,
        "p{0.29\\linewidth}p{0.21\\linewidth}rrrr",
        "Paired seed-level differences for mechanics gap v5 minus selected references on the hard aggregate.",
        "tab:paired",
    )


def ablation_table(ablations):
    rows = []
    for row in ablations:
        rows.append(
            f"{split_name(row['split'])} & {ablation_name(row['ablation'])} & {fmt_pm(row['task_success'], row['task_success_ci95'])} & {fmt(row['hidden_mechanism_f1'])} & {fmt(row['unsafe_action'])} & {fmt(row['bloat_index'])} & {fmt(row['robust_utility'])}\\\\"
        )
    return longtable(
        "Split & Ablation & Success & Mech. F1 & Unsafe & Bloat & Utility",
        rows,
        "p{0.16\\linewidth}p{0.27\\linewidth}rrrrr",
        "Mechanism ablations. The full system had to beat every removal on robust utility and avoid success/safety reversals.",
        "tab:ablation",
    )


def stress_table(stress):
    rows = []
    for row in stress:
        rows.append(
            f"{table_phrase(row['stress_axis'])} & {row['stress_level']} & {method_name(row['method'])} & {fmt(row['task_success'])} & {fmt(row['hidden_mechanism_f1'])} & {fmt(row['unsafe_action'])} & {fmt(row['bloat_index'])} & {fmt(row['robust_utility'])}\\\\"
        )
    return longtable(
        "Axis & Level & Method & Succ. & Mech. F1 & Unsafe & Bloat & Utility",
        rows,
        "p{0.18\\linewidth}rp{0.23\\linewidth}rrrrr",
        "Full stress sweep over all six axes and six levels. The table is complete so favorable plots cannot hide unfavorable regimes.",
        "tab:stress",
    )


def fixed_table(fixed):
    rows = []
    for row in fixed:
        rows.append(
            f"{split_name(row['split'])} & {row['risk_budget']} & {method_name(row['method'])} & {fmt(row['coverage'])} & {fmt(row['accepted_success'])} & {fmt(row['accepted_unsafe_action'])} & {fmt(row['accepted_bloat_index'])} & {fmt(row['mean_risk'])}\\\\"
        )
    return longtable(
        "Split & Budget & Method & Cover. & Succ. & Unsafe & Bloat & Mean risk",
        rows,
        "p{0.16\\linewidth}rp{0.23\\linewidth}rrrrr",
        "Fixed-risk deployment results. A low-risk policy must have nonzero coverage, not just low accepted failure rates after rejecting hard cases.",
        "tab:fixed",
    )


def fixed_pairwise_table(fixed_pairs):
    rows = []
    for row in fixed_pairs:
        if row["risk_budget"] not in {"0.05", "0.10"}:
            continue
        rows.append(
            f"{split_name(row['split'])} & {row['risk_budget']} & {method_name(row['reference'])} & {metric_name(row['metric'])} & {fmt(row['mean_diff'])} & {fmt(row['lower95_diff'])} & {fmt(row['upper95_diff'])}\\\\"
        )
    return longtable(
        "Split & Budget & Reference & Metric & Mean diff & Lower95 & Upper95",
        rows,
        "p{0.14\\linewidth}rp{0.22\\linewidth}p{0.18\\linewidth}rrr",
        "Fixed-risk paired differences for v5 minus references at the deployment budgets emphasized in the frozen plan.",
        "tab:fixedpairs",
    )


def negative_table(negative):
    rows = []
    for row in negative:
        rows.append(f"{table_phrase(row['case_id'])} & {table_phrase(row['case_family'])} & {tex_escape(row['observed_failure_mode'])} & {tex_escape(row['terminal_lesson'])}\\\\")
    return longtable(
        "Case & Family & Observed failure & Terminal lesson",
        rows,
        "@{}p{0.16\\linewidth}p{0.16\\linewidth}p{0.36\\linewidth}p{0.24\\linewidth}@{}",
        "Predefined negative cases showing how uncertainty bloat, abstention, stale repair memory, and dropout false gaps fail.",
        "tab:negative",
    )


def prior_work_table(rows):
    table_rows = []
    for i, row in enumerate(rows, start=1):
        title = tex_escape(row.get("title", ""))[:170]
        family = table_phrase(row.get("family", ""))
        role = table_phrase(row.get("query_role", ""))
        hostile = tex_escape(row.get("hostile_score", ""))
        table_rows.append(f"\\citep{{{bib_key(i)}}} & {title} & {family} & {role} & {hostile}\\\\")
    return longtable(
        "Citation & Prior-work threat & Family & Role & Hostile",
        table_rows,
        "p{0.12\\linewidth}p{0.48\\linewidth}p{0.14\\linewidth}p{0.14\\linewidth}r",
        "Closest local-pool references used to set the novelty boundary. The bright boxed citations jump to bibliography entries.",
        "tab:prior",
    )


def gate_table(summary):
    rows = [
        ("Main success/diagnostic/safety gate", summary["main_gate"], "Requires decisive success, diagnostic F1, unsafe-action, abstention, and bloat margins."),
        ("Mechanism ablation gate", summary["mechanism_gate"], "Requires full mechanics gap v5 to beat every removal by predefined utility margins."),
        ("Stress non-domination gate", summary["stress_gate"], "Checks maximum combined stress against uncertainty, probing, robust, repair, and oracle references."),
        ("Fixed-risk deployment gate", summary["fixed_risk_gate"], "Requires nonzero coverage at budget 0.05 and best feasible accepted performance."),
        ("Scope gate", summary["scope_gate"], "Requires real robot or accepted high-fidelity external benchmark evidence."),
    ]
    body = [f"{tex_escape(name)} & {tex_escape(value)} & {tex_escape(reason)}\\\\" for name, value, reason in rows]
    return longtable(
        "Gate & Passed & Frozen interpretation",
        body,
        "p{0.25\\linewidth}p{0.12\\linewidth}p{0.53\\linewidth}",
        "Frozen submission-readiness gates.",
        "tab:gates",
    )


def summary_extract_table(summary_text):
    rows = []
    kept = 0
    for line_no, line in enumerate(ascii_clean(summary_text).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        kept += 1
        rows.append(f"{line_no} & {tex_escape(line[:230])}\\\\")
        if kept >= 90:
            break
    return longtable(
        "Line & Summary extract",
        rows,
        "rp{0.84\\linewidth}",
        "Wrapped extract from results/summary.txt.",
        "tab:summaryextract",
    )


def build_manuscript(keys, prior_rows):
    summary_text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    summary = parse_summary(summary_text)
    metrics = read_csv(RESULTS / "metrics.csv")
    hard_metrics = read_csv(RESULTS / "hard_aggregate_metrics.csv")
    hard_pairs = read_csv(RESULTS / "hard_aggregate_pairwise_stats.csv")
    ablations = read_csv(RESULTS / "ablation_metrics.csv")
    stress = read_csv(RESULTS / "stress_sweep.csv")
    fixed = read_csv(RESULTS / "fixed_risk_metrics.csv")
    fixed_pairs = read_csv(RESULTS / "fixed_risk_pairwise.csv")
    negative = read_csv(RESULTS / "negative_cases.csv")

    cite_core = ",".join(keys[:8])
    cite_uq = ",".join(keys[8:20])
    cite_safety = ",".join(keys[20:34])
    cite_data = ",".join(keys[34:48])
    cite_more = ",".join(keys[48:56])

    sections = [
        r"\documentclass{article}",
        r"\usepackage{iclr2026_conference,times}",
        r"\input{math_commands.tex}",
        r"\usepackage{hyperref}",
        r"\usepackage{url}",
        r"\usepackage{booktabs}",
        r"\usepackage{graphicx}",
        r"\usepackage{array}",
        r"\usepackage{longtable}",
        r"\usepackage{xcolor}",
        r"\usepackage{amsmath,amssymb}",
        r"\hypersetup{colorlinks=false,pdfborder={0 0 1.8},citebordercolor={0 1 0},linkbordercolor={1 0.55 0},urlbordercolor={0 0.45 1}}",
        r"\graphicspath{{../figures/}}",
        r"\newcommand{\methodname}{mechanics gap auditor v5}",
        r"\title{World-Model Uncertainty Bloat:\\A 25+ Page Negative Submission-Readiness\\Audit}",
        r"\author{Anonymous Authors}",
        r"\begin{document}",
        r"\maketitle",
        r"\begin{abstract}",
        (
            "Uncertainty estimates can protect a robot from overconfident world-model errors, but they can also hide missing mechanics by inflating variance instead of identifying what physical mechanism is absent. "
            "This rebuild tests a mechanics-gap auditor that separates aleatoric noise, epistemic uncertainty, missing contact/friction/actuation/latency/fixture mechanisms, active probe value, and repair memory. "
            "The audit is hostile: ten seeds, six tasks, eight splits, thirteen methods, ten ablations, six stress axes, fixed-risk deployment budgets, and 24 negative cases. "
            f"On the hard aggregate, \\methodname{{}} reaches {float(summary['proposal_success']):.3f} task success versus {float(summary['best_success']):.3f} for the strongest success reference, with paired lower95 {float(summary['paired_success_lower95']):.3f}. "
            f"It improves hidden-mechanism F1 over robust MPC but has unsafe action {float(summary['proposal_unsafe']):.3f} versus {float(summary['safest_unsafe']):.3f}, fails mechanism and fixed-risk gates, and has no robot or accepted high-fidelity validation. "
            "The honest terminal decision is \\textbf{KILL/ARCHIVE}."
        ),
        r"\end{abstract}",
        r"\section{Terminal Decision}",
        (
            "\\textbf{Decision: KILL/ARCHIVE for ICLR main.} The rebuilt paper is substantially stronger than the v4 audit, but it is not submission ready. "
            "It demonstrates a useful diagnostic tradeoff: v5 detects more hidden mechanics and reduces bloat relative to old uncertainty-bloat auditing, yet robust MPC remains stronger on success, safety, and utility. "
            "The paper therefore becomes a serious archive of the failure, not a dressed-up submission."
        ),
        gate_table(summary),
        r"\section{Research Question And Threat Model}",
        (
            "The core question is whether uncertainty estimation can become a hiding place for missing mechanics. A model may correctly report high variance near a contact transition while failing to say that it is missing friction, stiction, backlash, a snagged fixture, or a sensor-dropout state. "
            f"This is adjacent to uncertainty quantification, robust control, active perception, residual dynamics, Bayesian model expansion, safety filters, and robot world models \\citep{{{cite_core},{cite_uq}}}. "
            "A hostile reviewer can argue that standard ensemble uncertainty, conformal abstention, active probing, robust MPC, or residual repair already handles the issue."
        ),
        (
            f"The local prior-work pool makes the novelty boundary narrow \\citep{{{cite_safety},{cite_data},{cite_more}}}. "
            "The v5 claim is therefore not that uncertainty or repair is new. The only tested claim is whether a mechanics-gap diagnostic composition gives a better success/safety/coverage tradeoff than strong local alternatives."
        ),
        r"\section{Formal Setup}",
        (
            "An episode samples task state $x$, action plan $u$, observation quality $o$, hidden mechanism $z$, and world-model prediction $\\hat x'$. "
            "Uncertainty bloat occurs when reported uncertainty grows while the system fails to identify a repairable missing mechanism. "
            "The v5 score can be summarized as"
        ),
        r"\begin{equation}S_{v5}=s(x,u)-1.25\,r_{\mathrm{unsafe}}+0.42\,d_{\mathrm{mech}}-0.35\,b_{\mathrm{unc}}+0.22\,p_{\mathrm{probe}}-0.18\,c_{\mathrm{int}},\end{equation}",
        (
            "where $d_{\\mathrm{mech}}$ is hidden-mechanism evidence, $b_{\\mathrm{unc}}$ is the bloat index, $p_{\\mathrm{probe}}$ is active-probe value, and $c_{\\mathrm{int}}$ is intervention cost. "
            "The coefficients define a frozen synthetic audit rather than a universal control law."
        ),
        r"\paragraph{Proposition 1: variance is non-identifying without interventions.}",
        (
            "Two worlds can induce the same predictive variance: one with irreducible observation noise and one with a missing contact mechanism. "
            "Without an intervention or a structured latent-mechanism model, variance alone cannot distinguish them. "
            "This is why ensemble and dropout baselines can obtain high uncertainty while still underperforming on repair."
        ),
        r"\paragraph{Proposition 2: abstention safety is vacuous at zero coverage.}",
        (
            "A risk gate that rejects every hard episode has zero accepted unsafe actions by construction, but it also performs no useful robotics task. "
            "The fixed-risk section reports coverage because accepted safety without coverage is not a deployment result."
        ),
        r"\paragraph{Proposition 3: repair memory can amplify stale mechanisms.}",
        (
            "A remembered repair is helpful only while the hidden mechanism remains stable. If the fixture, contact mode, or sensor-dropout pattern changes, stale repair memory can make a world-model diagnosis worse than robust fallback."
        ),
        r"\section{Frozen Protocol}",
        (
            "The v5 protocol contains 199,680 main rollouts, 15,360 dataset-summary rows, 33,600 ablation rollouts, 302,400 stress rows, 69,120 fixed-risk rows, and 24 negative cases. "
            "It uses ten seeds, six manipulation tasks, eight missing-mechanics splits, thirteen main methods, ten ablations, six stress axes, and strict fixed-risk budgets."
        ),
        row_count_table(),
        r"\section{Main Results}",
        (
            f"Table~\\ref{{tab:hard}} is the primary result. The v5 method improves over the old v4 audit and most pure uncertainty baselines, but it fails the main gate. "
            f"The strongest success and utility reference is {tex_escape(summary['best_success_reference'])}, and v5 trails it by a paired lower95 of {float(summary['paired_success_lower95']):.3f}. "
            f"The safest reference has unsafe action {float(summary['safest_unsafe']):.3f}, while v5 has {float(summary['proposal_unsafe']):.3f}. "
            "The diagnostic gain is real, but the robotics tradeoff is not submission-grade."
        ),
        hard_table(hard_metrics),
        r"\begin{figure}[t]\centering\includegraphics[width=0.95\linewidth]{uncertainty_bloat_hard_success_v5.png}\caption{Hard-aggregate task success. Robust MPC remains the strongest non-oracle success/utility reference.}\label{fig:hard-success}\end{figure}",
        r"\begin{figure}[t]\centering\includegraphics[width=0.95\linewidth]{uncertainty_bloat_failures_v5.png}\caption{Unsafe action, false abstention, and bloat. The v5 method improves some diagnostics but not enough to satisfy the safety gate.}\label{fig:failures}\end{figure}",
        r"\section{Split-Level Evidence}",
        "The split-level table prevents the paper from hiding behind a single favorable split. The combined missing-mechanics regime remains the decisive test.",
        split_table(metrics),
        r"\section{Paired Comparisons}",
        (
            "Paired seed tests are harsher than independent means. V5 beats the old v4 audit on several diagnostic metrics, but it trails robust MPC on success and utility and has a positive unsafe-action difference."
        ),
        pairwise_table(hard_pairs, summary),
        r"\section{Mechanism Ablations}",
        (
            "The ablation story is mixed. Removing repair memory improves combined-split success and utility in this synthetic audit, while removing false-abstention penalty lowers unsafe actions. "
            "That means the mechanism is not yet clean enough for an ICLR-main claim."
        ),
        ablation_table(ablations),
        r"\begin{figure}[t]\centering\includegraphics[width=0.95\linewidth]{uncertainty_bloat_ablation_v5.png}\caption{Combined missing-mechanics ablation utility. The full mechanism fails the frozen ablation gate.}\label{fig:ablation}\end{figure}",
        r"\section{Stress Testing}",
        (
            "The stress gate passes because v5 is not Pareto dominated at maximum combined stress. That is not enough to rescue the paper because the main, mechanism, fixed-risk, and scope gates fail."
        ),
        r"\begin{figure}[t]\centering\includegraphics[width=0.95\linewidth]{uncertainty_bloat_stress_sweep_v5.png}\caption{Task success under combined stress.}\label{fig:stress}\end{figure}",
        stress_table(stress),
        r"\section{Fixed-Risk Deployment}",
        (
            "The fixed-risk gate is the cleanest deployment failure. At budget 0.05, all non-oracle methods have zero accepted coverage on the hard fixed-risk splits. "
            "A reviewer should treat this as a blocker because the system cannot claim safe operation by refusing every hard episode."
        ),
        r"\begin{figure}[t]\centering\includegraphics[width=0.95\linewidth]{uncertainty_bloat_fixed_risk_v5.png}\caption{Fixed-risk coverage on combined missing mechanics. Strict coverage collapses.}\label{fig:fixed}\end{figure}",
        fixed_table(fixed),
        fixed_pairwise_table(fixed_pairs),
        r"\section{Negative Cases}",
        "The negative cases document exactly where uncertainty bloat, abstention, stale repair memory, and dropout false-gap diagnosis break the method.",
        negative_table(negative),
        r"\section{Prior Work Boundary}",
        (
            f"The prior-work table is a novelty pressure device, not decoration. UQ, conformal safety, robust MPC, active perception, residual dynamics, and robot world-model work all threaten the claim \\citep{{{cite_core},{cite_uq},{cite_safety},{cite_data}}}. "
            "The current v5 evidence is not strong enough to overcome that boundary."
        ),
        prior_work_table(prior_rows),
        r"\section{Discussion}",
        (
            "The result is useful because it clarifies the next research step. Mechanics-gap diagnosis should be coupled to calibrated interventions and external robot validation; otherwise it can improve hidden-mechanism F1 while losing to a robust fallback on the metrics that matter for deployment."
        ),
        r"\section{Reproducibility Statement}",
        (
            "All reported rows were generated locally on CPU with deterministic seeds and streaming CSV writes. The source runner is \\texttt{src/run\\_experiment.py}; generated evidence is in \\texttt{results/}; figures are in \\texttt{figures/}; and this manuscript is generated by \\texttt{scripts/generate\\_manuscript.py}. The final PDF is copied only to \\texttt{Downloads/88.pdf}; no PDF is copied to the visible Desktop."
        ),
        r"\clearpage",
        r"\appendix",
        r"\section{Appendix: Full Stress And Deployment Tables}",
        "The preceding tables are intentionally complete rather than cherry-picked.",
        r"\begin{figure}[h]\centering\includegraphics[width=0.9\linewidth]{uncertainty_bloat_pareto_v5.png}\caption{Hard-aggregate Pareto view for success, unsafe action, bloat, and utility.}\end{figure}",
        r"\section{Appendix: Raw Summary Extract}",
        summary_extract_table(summary_text),
        r"\nocite{*}",
        r"\bibliographystyle{iclr2026_conference}",
        r"\bibliography{references}",
        r"\end{document}",
    ]
    (PAPER / "main.tex").write_text("\n\n".join(sections), encoding="utf-8")


def main():
    PAPER.mkdir(exist_ok=True)
    keys, prior_rows = write_references()
    build_manuscript(keys, prior_rows)
    print(f"wrote {PAPER / 'main.tex'}")
    print(f"wrote {PAPER / 'references.bib'}")


if __name__ == "__main__":
    main()
