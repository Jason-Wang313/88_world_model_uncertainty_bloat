# 88 World-Model Uncertainty Bloat

Submission-hardening version: v4

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

This repository contains a reproducible local evidence audit for the research bet:

> Expose cases where uncertainty mechanisms hide missing mechanics instead of repairing them.

The v4 rebuild replaces the template scaffold with a deterministic world-model reliability benchmark over four manipulation tasks, five hidden-mechanics splits, eight methods, ablations, stress sweeps, and negative cases.

## Why This Is Archived

- On the combined missing-mechanics split, `uncertainty_bloat_audit` reaches `0.53741 +/- 0.01266` task success.
- The strongest success baseline, `active_probe_then_plan`, reaches `0.63605 +/- 0.01979`.
- The paired task-success difference is `-0.09864 +/- 0.01937`.
- `robust_mpc_fallback` has much lower unsafe-action rate (`0.05697`) than the proposed audit (`0.21429`).
- Several ablations beat the full method on success, including `minus_mechanism_classifier` (`0.58248`) and `minus_repair_memory` (`0.57738`).
- The evidence is local and synthetic, not hardware or accepted high-fidelity benchmark validation.

## Reproduce

```powershell
python src\run_experiment.py
```

The runner writes:

- `results/rollouts.csv`
- `results/raw_seed_metrics.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/ablation_rollouts.csv`
- `results/ablation_seed_metrics.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep_raw.csv`
- `results/stress_sweep.csv`
- `results/negative_cases.csv`
- `results/summary.txt`
- `figures/uncertainty_bloat_*.png`

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/88.pdf`
