# Child Status 88

Current stage: ICLR main v4 evidence audit terminal
Last update: 2026-06-15 10:37:20 +01:00
PDF: C:/Users/wangz/Downloads/88.pdf
GitHub: https://github.com/Jason-Wang313/88_world_model_uncertainty_bloat
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Latest rerun: `python -m py_compile src\run_experiment.py` and `python src\run_experiment.py` completed on 2026-06-15.

Evidence inventory: 47,040 main rollouts, 8,232 ablation rollouts, 120,960 stress rollouts, seven seeds, four tasks, five hidden-mechanics splits, eight methods, seven ablations, six stress axes, and four negative cases.

Reason: the repo contains a deterministic local world-model reliability benchmark with baselines, ablations, stress sweeps, negative cases, and figures. The proposed uncertainty-bloat audit loses task success to active probing (`0.53741` vs `0.63605`; paired difference `-0.09864 +/- 0.01937`), is less safe than robust MPC (`0.21429` vs `0.05697` unsafe-action rate), loses at maximum combined stress, and is contradicted by ablations that improve success after removing core components. No robot hardware or accepted high-fidelity deployment benchmark is available.
