# Paper 88 Rebuild Plan

Last update: 2026-06-14 13:16:29 +01:00

## Target Claim

World-model uncertainty can become bloated: it may hide missing mechanics behind large predictive variance, causing conservative abstention or broad risk penalties without identifying what physical mechanism is missing. A useful method must separate harmless noise from missing mechanics, expose the missing mechanism, and improve closed-loop control rather than merely reporting high uncertainty.

## Hostile Prior-Work Pressure

The local hostile set includes uncertainty-calibrated safety gating, zero-shot uncertainty-aware sim-to-real deployment, Bayesian controller fusion, failure-aware VLA systems, diagnostic world-model benchmarks, and deployment-time reliability work. The v4 rebuild must not claim novelty from generic uncertainty, conformal gating, ensemble disagreement, or abstention. It must test whether the proposed bloat audit changes what the planner can diagnose and repair.

## Evidence To Build

Replace the shared probability scaffold with a deterministic local world-model reliability benchmark. Each episode should generate a true physical transition error from noise, friction shift, contact-mode error, saturation, latency, sensor dropout, or combined missing mechanics. Candidate planners then choose whether to act, abstain, probe, repair, or use robust fallback.

### Tasks

- peg insertion under hidden contact-mode shift.
- drawer pull under friction and stiction changes.
- block pushing under contact patch and mass distribution shift.
- cable routing under latent snag and compliance changes.

### Splits

- `nominal_noise`
- `friction_contact_shift`
- `actuator_saturation_shift`
- `sensor_dropout_ambiguity`
- `combined_missing_mechanics`

### Methods

- `mean_world_model_mpc`
- `ensemble_variance_gate`
- `mc_dropout_uncertainty`
- `conformal_risk_gate`
- `active_probe_then_plan`
- `robust_mpc_fallback`
- `uncertainty_bloat_audit` (proposed)
- `oracle_mechanics_repair`

### Metrics

- task success.
- hidden-mechanism F1.
- false abstention rate.
- unsafe action rate.
- repair precision.
- uncertainty calibration error.
- bloat index: high uncertainty without useful diagnosis.
- intervention/probe cost.
- oracle regret.

### Ablations

- full uncertainty-bloat audit.
- minus mechanism classifier.
- minus probe-before-repair.
- minus false-abstention penalty.
- minus repair memory.
- variance-only bloat score.
- abstain-only policy.

### Stress Tests

- contact-mode shift.
- friction/stiction shift.
- actuator saturation.
- sensor dropout.
- latency.
- combined hidden mechanics.

### Terminal Gate

Mark `STRONG_REVISE` only if the proposed method beats the strongest non-oracle baseline on combined-missing-mechanics task success, hidden-mechanism F1, and bloat index while avoiding worse unsafe-action rate and while ablations degrade the mechanism. Otherwise mark `KILL_ARCHIVE`.

Even a `STRONG_REVISE` outcome is not ICLR-main ready without hardware, an accepted high-fidelity robot benchmark, or external deployment evidence.
