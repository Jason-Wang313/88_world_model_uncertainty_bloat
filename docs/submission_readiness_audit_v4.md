# Submission Readiness Audit v4

Date: 2026-06-15

Paper: 88 World-Model Uncertainty Bloat

Terminal decision: KILL_ARCHIVE

## Commands Run

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
```

Both commands completed. The experiment regenerated the result CSVs, figures, and summary from source.

## Evidence Coverage

- Main rollouts: 47,040 rows.
- Main seed metrics: 280 rows.
- Main aggregate metrics: 360 rows.
- Pairwise statistics: 315 rows.
- Ablation rollouts: 8,232 rows.
- Ablation seed metrics: 49 rows.
- Ablation aggregate metrics: 7 rows.
- Stress rollouts: 120,960 rows.
- Stress aggregates: 216 rows.
- Negative cases: 4 rows.
- Seeds: 0, 1, 2, 3, 4, 5, 6.
- Tasks: `peg_insertion_contact_mode`, `drawer_pull_stiction`, `block_push_patch_shift`, `cable_routing_latent_snag`.
- Splits: `nominal_noise`, `friction_contact_shift`, `actuator_saturation_shift`, `sensor_dropout_ambiguity`, `combined_missing_mechanics`.
- Methods: `mean_world_model_mpc`, `ensemble_variance_gate`, `mc_dropout_uncertainty`, `conformal_risk_gate`, `active_probe_then_plan`, `robust_mpc_fallback`, `uncertainty_bloat_audit`, `oracle_mechanics_repair`.

## Main Gate

On the combined missing-mechanics split, `uncertainty_bloat_audit` reaches `0.53741 +/- 0.01266` task success. The strongest non-oracle success baseline, `active_probe_then_plan`, reaches `0.63605 +/- 0.01979`. The paired task-success difference is `-0.09864 +/- 0.01937`, which directly fails the primary gate.

## Contradictory Evidence

- `robust_mpc_fallback` has unsafe-action rate `0.05697`, while the proposed audit has `0.21429`.
- `minus_mechanism_classifier` improves task success to `0.58248`.
- `minus_repair_memory` improves task success to `0.57738`.
- At maximum combined stress, `uncertainty_bloat_audit` reaches `0.37500` task success, below `robust_mpc_fallback` at `0.51250` and `active_probe_then_plan` at `0.50714`.

## Readiness Judgment

The paper is reproducible as a local negative evidence audit, but not submission-ready for ICLR main. It lacks robot hardware, accepted high-fidelity deployment benchmark validation, externally comparable learned baselines, and any decisive closed-loop advantage over strong local baselines.

## Terminal Action

Keep `KILL_ARCHIVE`. Do not submit this paper to ICLR main in the current form.
