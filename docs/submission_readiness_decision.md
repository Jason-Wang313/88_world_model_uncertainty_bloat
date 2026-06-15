# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Submission-hardening version: v4.

Latest rerun: 2026-06-15 from `src/run_experiment.py`.

Reason: The v4 rebuild is materially stronger than the earlier template paper, but it fails the ICLR-main bar on the paper's own gates. It contains a deterministic local world-model reliability benchmark with seven seeds, 47,040 main rollouts, 8,232 ablation rollouts, 120,960 stress rollouts, strong synthetic baselines, ablations, stress sweeps, negative cases, and figures. On the combined missing-mechanics split, `uncertainty_bloat_audit` reaches `0.53741 +/- 0.01266` task success, while `active_probe_then_plan` reaches `0.63605 +/- 0.01979`. The paired task-success difference is `-0.09864 +/- 0.01937`.

Additional blockers: `robust_mpc_fallback` is far safer (`0.05697` unsafe-action rate versus `0.21429` for the proposed audit), maximum combined stress favors `robust_mpc_fallback` and `active_probe_then_plan`, and ablations that remove core components improve success (`minus_mechanism_classifier` at `0.58248`, `minus_repair_memory` at `0.57738`). The evidence remains local synthetic simulation rather than robot hardware or an accepted high-fidelity deployment benchmark.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with hardware or accepted benchmark validation, implemented learned world-model diagnostics, real competing baselines, manually synthesized related work, and deployment evidence that diagnosis improves task success and safety.
