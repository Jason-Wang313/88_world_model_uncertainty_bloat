# Hostile Reviewer Response

Paper: 88 World-Model Uncertainty Bloat

## Strongest Technical Threats
- An Investigation into Uncertainty Quantification of Shallow Foundation Failure Mechanisms in Horizontally Stratified Layered Soil Strata (2026)
- VLS: Steering Pretrained Robot Policies via Vision-Language Models (2026)
- Uncertainty-Calibrated Safety Gating for Vision-Language- Action Manipulation Under Domain Shift: Reliability Gains and Intervention-Efficiency Trade-Offs (2026)
- Zero-Shot Uncertainty-Aware Deployment of Simulation Trained Policies on Real-World Robots (2021)
- Bayesian Controller Fusion: Leveraging Control Priors in Deep Reinforcement Learning for Robotics (2021)
- WorldBench: Disambiguating Physics for Diagnostic Evaluation of World Models (2026)
- ReconVLA: An Uncertainty-Guided and Failure-Aware Vision-Language-Action Framework for Robotic Control (2026)
- Benchmarking Robust Machine Learning Models Under Data Imperfections in Real-World Data Science Scenarios (2026)

## ICLR Main Response
A hostile ICLR reviewer would be correct to reject this as a main-conference submission. The v4 paper is no longer a toy single-seed scaffold: it has seven seeds, strong local baselines, ablations, stress sweeps, negative cases, and figures. Even so, the proposed audit loses combined-missing-mechanics success to `active_probe_then_plan` by `-0.09864 +/- 0.01937`, is less safe than `robust_mpc_fallback`, and is contradicted by ablations that improve success after removing core components. The paper also lacks robot hardware or an accepted high-fidelity deployment benchmark.

## Honest Action
The paper is marked `KILL_ARCHIVE`. This avoids converting a useful negative audit into an overstated main-conference claim.

## What Would Be Needed To Revive
- Real robot or accepted high-fidelity benchmark experiments.
- Implemented learned diagnostic world model and real competing baselines.
- Manual full-paper related-work audit.
- Paper-specific qualitative rollout analysis.
- Evidence that the core mechanism improves both task success and safety under deployment shift.
