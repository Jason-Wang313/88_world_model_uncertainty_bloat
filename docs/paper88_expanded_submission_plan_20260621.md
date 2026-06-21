# Paper 88 Expanded Submission Plan - Frozen Before Execution

Paper: `88_world_model_uncertainty_bloat`

Date frozen: 2026-06-21

Target venue shape: ICLR-main-style submission audit, not a submission claim.

Terminal standard: maximize evidence quality under CPU-only and RAM-light execution. Do not optimize for pretty results. Optimize for a result that survives hostile review. Report every predefined result honestly.

## Objective

Rebuild Paper 88 from the current 6-page v4 negative audit into a 25+ page v5 submission-readiness package. The package must include new theory, stronger experiments, strong baselines, stress tests, fixed-risk deployment tests, negative cases, bright boxed clickable citations, reproducible code/results, a numbered Downloads-only PDF, child documentation, root ledger updates, and a public GitHub push.

## Non-Negotiable Artifact Rules

- Canonical PDF path: `C:/Users/wangz/Downloads/88.pdf`.
- Do not copy any PDF to the visible Desktop.
- Keep the runner CPU-only and RAM-light by streaming raw CSV rows and aggregating seed metrics in dictionaries.
- Build the manuscript from generated evidence, not hand-edited flattering prose.
- If gates fail, report `KILL_ARCHIVE`.
- If a result is mixed, emphasize the failure modes rather than burying them.

## Research Question

Do uncertainty mechanisms sometimes hide missing robot mechanics by inflating epistemic/aleatoric uncertainty instead of identifying and repairing the missing contact, friction, saturation, latency, dropout, or fixture mechanism?

The v5 mechanism claim is narrow:

> A world-model reliability system should distinguish irreducible noise from missing mechanics, actively probe when repair is plausible, and avoid safe-looking uncertainty bloat that either abstains too much or acts unsafely.

## v5 Method To Test

Name: `mechanics_gap_auditor_v5`

Core scoring terms:

- hidden-mechanism posterior over contact, friction, actuator, latency, sensor, and fixture gaps.
- uncertainty-bloat index separating predictive variance from identifiable missing-mechanism evidence.
- active probe value before repair.
- repair-memory consistency across repeated mechanisms.
- false-abstention penalty so safety is not achieved by refusing every task.
- calibrated deployment risk for fixed-risk acceptance.

No universality claim is allowed. The method is an audited local mechanism prototype.

## Frozen Main Experiment

Seeds: `0..9`.

Tasks:

- `peg_insertion_contact_mode`
- `drawer_pull_stiction`
- `block_push_patch_shift`
- `cable_routing_latent_snag`
- `suction_cup_seal_break`
- `door_latch_backlash`

Splits:

- `nominal_noise`
- `friction_contact_shift`
- `actuator_saturation_shift`
- `sensor_dropout_ambiguity`
- `latency_hysteresis_shift`
- `latent_fixture_snag_shift`
- `missing_contact_mode_shift`
- `combined_missing_mechanics`

Main methods:

- `mean_world_model_mpc`
- `ensemble_variance_gate`
- `mc_dropout_uncertainty`
- `conformal_risk_gate`
- `epistemic_ensemble_planner`
- `active_probe_then_plan`
- `robust_mpc_fallback`
- `residual_dynamics_repair`
- `bayesian_model_expansion`
- `uncertainty_bloat_audit_v4`
- `mechanics_gap_auditor_v5`
- `oracle_mechanics_repair`
- `oracle_full_state_policy`

Main rows:

- `10 seeds * 8 splits * 13 methods * 6 tasks * 32 episodes = 199,680`.

Dataset-summary rows:

- `10 seeds * 8 splits * 6 tasks * 32 episodes = 15,360`.

Metrics:

- `task_success`
- `hidden_mechanism_f1`
- `false_abstention`
- `unsafe_action`
- `repair_precision`
- `calibration_error`
- `bloat_index`
- `probe_efficiency`
- `intervention_cost`
- `oracle_regret`
- `deployment_risk`
- `robust_utility`

Hard aggregate splits:

- `latent_fixture_snag_shift`
- `missing_contact_mode_shift`
- `combined_missing_mechanics`

## Frozen Baseline Pressure

The proposed method must not be compared only with weak uncertainty baselines. The hostile comparison set includes:

- predictive-mean MPC to show whether uncertainty matters at all.
- ensemble variance and MC dropout to test standard UQ.
- conformal risk gating to test calibrated abstention.
- epistemic ensemble planning to test model-uncertainty-aware control.
- active probing to test whether explicit interaction is enough.
- robust MPC fallback to test safe conservative planning.
- residual dynamics repair to test learned local correction.
- Bayesian model expansion to test explicit latent-mechanism inference.
- v4 to show whether the new method is actually better than the archived mechanism.
- oracle references to expose remaining headroom.

## Frozen Ablation Experiment

Ablation splits:

- `missing_contact_mode_shift`
- `combined_missing_mechanics`

Ablations:

- `full_mechanics_gap_auditor_v5`
- `minus_mechanism_classifier`
- `minus_uncertainty_bloat_index`
- `minus_active_probe_value`
- `minus_repair_memory`
- `minus_false_abstention_penalty`
- `minus_calibrated_risk`
- `variance_only_bloat_score`
- `abstain_only_policy`
- `probe_without_repair_memory`

Ablation rows:

- `2 splits * 10 seeds * 10 ablations * 6 tasks * 28 episodes = 33,600`.

Mechanism gate:

- Full v5 robust utility must beat every non-full ablation by at least `0.015`.
- Full v5 must not have a joint task-success and unsafe-action reversal against any removal.
- Full v5 hidden-mechanism F1 must exceed the best uncertainty-only ablation.

## Frozen Stress Experiment

Stress axes:

- `contact_friction_shift`
- `actuator_saturation`
- `sensor_dropout`
- `latency_hysteresis`
- `hidden_fixture_rate`
- `combined`

Stress levels:

- `0.0, 0.2, 0.4, 0.6, 0.8, 1.0`

Stress methods:

- `ensemble_variance_gate`
- `conformal_risk_gate`
- `active_probe_then_plan`
- `robust_mpc_fallback`
- `residual_dynamics_repair`
- `mechanics_gap_auditor_v5`
- `oracle_mechanics_repair`

Stress rows:

- `6 axes * 6 levels * 7 methods * 10 seeds * 6 tasks * 20 episodes = 302,400`.

Stress gate:

- At maximum combined stress, v5 must not be Pareto dominated on task success, unsafe action, false abstention, bloat index, and robust utility by any non-oracle method.

## Frozen Fixed-Risk Experiment

Fixed-risk splits:

- `missing_contact_mode_shift`
- `combined_missing_mechanics`

Risk budgets:

- `0.02, 0.05, 0.10, 0.20`

Methods:

- `ensemble_variance_gate`
- `conformal_risk_gate`
- `active_probe_then_plan`
- `robust_mpc_fallback`
- `mechanics_gap_auditor_v5`
- `oracle_mechanics_repair`

Fixed-risk rows:

- `2 splits * 4 budgets * 6 methods * 10 seeds * 6 tasks * 24 episodes = 69,120`.

Fixed-risk gate:

- At budget `0.05`, v5 must have nonzero accepted coverage on both fixed-risk splits.
- Among feasible non-oracle methods, v5 must match or beat accepted success and unsafe-action rate within the predefined tolerances.
- Zero coverage is an automatic deployment failure.

## Frozen Negative Cases

Generate 24 negative cases across six families:

- aleatoric noise mistaken for missing mechanics.
- missing contact mode hidden by high variance.
- robust fallback succeeds but audit over-repairs.
- conformal gate abstains safely but uselessly.
- active probe reveals mechanism but repair memory corrupts transfer.
- sensor dropout causes a false mechanics diagnosis.

Negative cases must be summarized in `results/negative_cases.csv` and included in the manuscript appendix.

## Frozen Terminal Gates

The result is `STRONG_REVISE` only if all of the following hold:

- Hard-aggregate task success exceeds the strongest non-oracle success baseline by at least `0.030`.
- Unsafe-action rate is no worse than the safest non-oracle baseline by more than `0.010`, unless task success improves by at least `0.080` and fixed-risk passes.
- Hidden-mechanism F1 exceeds the strongest non-oracle diagnostic baseline by at least `0.030`.
- False abstention is not worse than conformal gating by more than `0.020`.
- Bloat index improves over variance and dropout baselines by at least `0.050`.
- Paired lower95 success bound against the strongest success baseline is positive.
- Paired upper95 unsafe-action bound against the safest baseline is not positive beyond tolerance.
- Mechanism gate passes.
- Stress gate passes.
- Fixed-risk gate passes.
- Scope gate passes with real robot or accepted high-fidelity external benchmark evidence.

Because this run is local synthetic-only, the scope gate is expected to fail unless external evidence already exists in the repo. If scope fails, the manuscript must say so.

## Manuscript Requirements

The generated paper must be at least 25 pages without padding. Required content:

- Abstract that states the terminal decision.
- Hostile prior-work section with bright boxed clickable citations.
- Formal setup distinguishing uncertainty from missing mechanics.
- Proposition: uncertainty variance is non-identifying without interventions.
- Proposition: abstention safety is vacuous at zero coverage.
- Proposition: repair memory can amplify stale mechanism hypotheses.
- Frozen protocol table and evidence inventory.
- Main hard-aggregate table.
- Split-level table.
- Paired seed-difference table.
- Ablation table.
- Full stress table.
- Fixed-risk and fixed-risk paired tables.
- Negative-case table.
- Prior-work boundary table from `docs/deep_read_250.csv`.
- Summary extract appendix.
- Reproducibility statement.

Citation settings must include:

- `colorlinks=false`
- `pdfborder={0 0 1.8}`
- `citebordercolor={0 1 0}`
- `linkbordercolor={1 0.55 0}`
- `urlbordercolor={0 0.45 1}`

## Validation Requirements

Add a validator that checks:

- Expected CSV row counts.
- Required summary tokens.
- Required LaTeX hyperlink settings.
- No unresolved citations or references in the final LaTeX log.
- `C:/Users/wangz/Downloads/88.pdf` exists.
- `C:/Users/wangz/Desktop/88.pdf` does not exist.
- PDF has at least 25 pages.
- PDF text includes the title, terminal decision, method name, and fixed-risk section.
- SHA256 is printed.

## Final Documentation Requirements

Update:

- `README.md`
- `child_status.md`
- `plan.md`
- `docs/claims.md`
- `docs/final_audit.md`
- `docs/submission_readiness_decision.md`
- `docs/submission_version_log.md`
- `docs/submission_readiness_audit_v5.md`
- `docs/paper88_terminal_audit_20260621.md`
- root `GLOBAL_POOL_STATUS.md`
- root `BATCH_STATUS.md`
- root `SUBMISSION_STATUS.md`
- root `MASTER_REPORT.md`
- root `MASTER_SUBMISSION_REPORT.md`
- root `SUBMISSION_AUDIT_MATRIX.csv`

## Execution Order

1. Save this plan before any v5 code changes.
2. Replace or extend the runner.
3. Run `python -m py_compile src\run_experiment.py`.
4. Run `python src\run_experiment.py`.
5. Generate manuscript and bibliography.
6. Compile LaTeX/BibTeX to a clean PDF.
7. Copy only to `Downloads/88.pdf`.
8. Run validator.
9. Render representative pages for visual QA.
10. Remove visual-QA temp files.
11. Update docs and root ledgers.
12. Commit and push public GitHub repo.
13. Verify local/remote commit match, GitHub visibility, PDF hash/pages, validator, and Desktop absence.
