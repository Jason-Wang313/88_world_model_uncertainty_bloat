# Paper 88 Terminal Audit

Date: 2026-06-15

Paper: `88_world_model_uncertainty_bloat`

Decision: `KILL_ARCHIVE`

## Reproduction

- `python -m py_compile src\run_experiment.py`: passed.
- `python src\run_experiment.py`: passed.
- PDF target: `C:/Users/wangz/Downloads/88.pdf`.
- Visible Desktop copy: not allowed.

## Evidence Files

- `results/rollouts.csv`: 47,040 rows.
- `results/raw_seed_metrics.csv`: 280 rows.
- `results/metrics.csv`: 360 rows.
- `results/pairwise_stats.csv`: 315 rows.
- `results/ablation_rollouts.csv`: 8,232 rows.
- `results/ablation_seed_metrics.csv`: 49 rows.
- `results/ablation_metrics.csv`: 7 rows.
- `results/stress_sweep_raw.csv`: 120,960 rows.
- `results/stress_sweep.csv`: 216 rows.
- `results/negative_cases.csv`: 4 rows.

## Coverage

- Seeds: 0 through 6.
- Tasks: `peg_insertion_contact_mode`, `drawer_pull_stiction`, `block_push_patch_shift`, `cable_routing_latent_snag`.
- Splits: `nominal_noise`, `friction_contact_shift`, `actuator_saturation_shift`, `sensor_dropout_ambiguity`, `combined_missing_mechanics`.
- Methods: `mean_world_model_mpc`, `ensemble_variance_gate`, `mc_dropout_uncertainty`, `conformal_risk_gate`, `active_probe_then_plan`, `robust_mpc_fallback`, `uncertainty_bloat_audit`, `oracle_mechanics_repair`.
- Ablations: `full_uncertainty_bloat_audit`, `minus_mechanism_classifier`, `minus_probe_before_repair`, `minus_false_abstention_penalty`, `minus_repair_memory`, `variance_only_bloat_score`, `abstain_only_policy`.
- Stress axes: `contact_mode_shift`, `friction_stiction_shift`, `actuator_saturation`, `sensor_dropout`, `latency`, `combined`.

## Key Results

Combined missing mechanics:

- `uncertainty_bloat_audit`: task success `0.53741 +/- 0.01266`, hidden-mechanism F1 `0.14569`, unsafe action `0.21429`, bloat index `0.40966`.
- `active_probe_then_plan`: task success `0.63605 +/- 0.01979`, unsafe action `0.19898`, bloat index `0.22499`.
- `robust_mpc_fallback`: task success `0.60799 +/- 0.02711`, unsafe action `0.05697`.
- Paired task-success difference versus `active_probe_then_plan`: `-0.09864 +/- 0.01937`.

Ablation:

- Full method task success: `0.53741`.
- `minus_mechanism_classifier` task success: `0.58248`.
- `minus_repair_memory` task success: `0.57738`.
- `variance_only_bloat_score` hidden-mechanism F1: `0.26842`, above the full method's `0.14569`.

Maximum combined stress:

- `uncertainty_bloat_audit` task success: `0.37500`.
- `active_probe_then_plan` task success: `0.50714`.
- `robust_mpc_fallback` task success: `0.51250`.
- `oracle_mechanics_repair` task success: `0.67143`.

## Terminal Reason

The local benchmark is useful and reproducible, but the proposed audit fails the primary closed-loop success gate, loses the safety comparison, is contradicted by ablations, and has no robot hardware or accepted high-fidelity benchmark evidence. The only honest ICLR-main decision is `KILL_ARCHIVE`.

## PDF Verification

- Build command: two-pass `pdflatex -interaction=nonstopmode -halt-on-error main.tex`.
- Canonical PDF: `C:/Users/wangz/Downloads/88.pdf`.
- PDF SHA256: `8027C9F079704ED705C0050D1068E178FE2D45ADEF40B7697C66A7F0C3F793C4`.
- PDF size: 637,829 bytes.
- LaTeX log scan: no document warnings/errors requiring action after the second pass.
- Desktop copy: absent.
