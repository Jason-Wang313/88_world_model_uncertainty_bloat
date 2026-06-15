# Paper 88 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15

Paper: `88_world_model_uncertainty_bloat`

Target venue standard: ICLR main conference, evidence-first. The paper can advance only if the proposed uncertainty-bloat audit produces a real closed-loop robotics advantage over strong uncertainty, active-probing, robust-control, and oracle baselines. A diagnostic metric alone is insufficient if task success or safety regresses.

## Current State

The repository currently reports a v4 terminal decision of `KILL_ARCHIVE`. The core claim is that world-model uncertainty can become bloated: high uncertainty may hide missing mechanics instead of identifying the physical mechanism that needs repair. The prior v4 evidence found that the proposed audit loses task success to `active_probe_then_plan`, has worse unsafe-action rate than `robust_mpc_fallback`, and is contradicted by ablations where removing core components improves success.

## Execution Order

1. Verify repository hygiene before touching evidence.
   - Confirm worktree status.
   - Record current commit and remote.
   - Confirm the existing Downloads PDF and Desktop exclusion state.

2. Re-run the evidence generator from source.
   - Compile-check `src/run_experiment.py`.
   - Run `python src/run_experiment.py`.
   - Preserve generated CSVs, figures, and `results/summary.txt`.

3. Audit evidence completeness.
   - Confirm seven seeds.
   - Confirm all tasks, hidden-mechanics splits, methods, ablations, stress axes, and negative cases.
   - Confirm row counts and schemas for rollout, seed-level, aggregate, pairwise, ablation, stress, and negative-case outputs.

4. Apply the ICLR-main decision gate.
   - Require the proposed method to beat the strongest non-oracle baseline on combined-missing-mechanics task success with paired uncertainty.
   - Require hidden-mechanism F1 and bloat index to improve without increasing unsafe action or false abstention.
   - Require ablations to degrade when the mechanism classifier, probe-before-repair, false-abstention penalty, and repair memory are removed.
   - Require stress tests to preserve the same conclusion under contact-mode shift, friction/stiction shift, actuator saturation, sensor dropout, latency, and combined hidden mechanics.

5. Decide honestly.
   - If all local gates pass but evidence remains local synthetic only, mark at most `STRONG_REVISE`.
   - If active probing, robust MPC, or ablations beat the proposed method on primary criteria, preserve `KILL_ARCHIVE`.
   - Do not claim ICLR-main readiness without robot hardware, accepted high-fidelity deployment benchmarks, or external reproducibility.

6. Update child documentation and paper.
   - Align `README.md`, `child_status.md`, `plan.md`, readiness decision, final audit, hostile reviewer response, attack log, version log, and checklists with the rerun.
   - Add terminal audit docs with exact row counts, seed coverage, metric conclusions, PDF hash, and artifact-location checks.

7. Build and verify the PDF.
   - Build `paper/main.pdf` twice with LaTeX.
   - Copy only to `C:/Users/wangz/Downloads/88.pdf`.
   - Do not copy any PDF to the visible Desktop.
   - Scan the LaTeX log for warnings or errors that affect quality.

8. Update root ledgers.
   - Update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

9. Commit, push, and verify.
   - Commit only Paper 88 child-repo files inside its repo.
   - Push `main` to the public GitHub repo.
   - Verify local `HEAD` equals `origin/main`.
   - Verify `C:/Users/wangz/Downloads/88.pdf` exists and `C:/Users/wangz/Desktop/88.pdf` does not.

## Expected Outcome Risk

The likely terminal decision is `KILL_ARCHIVE`. The previous v4 evidence reports a negative paired success difference versus `active_probe_then_plan`, a safety loss against `robust_mpc_fallback`, and ablations that beat the full method. The rerun will still be performed end-to-end, and the final decision will be evidence-bound.
