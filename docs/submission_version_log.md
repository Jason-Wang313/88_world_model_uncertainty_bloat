# Submission Version Log

## v1 - Generated Draft
- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening
- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Recompiled canonical PDF at `C:/Users/wangz/Downloads/88.pdf`.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive
- Applied the stricter ICLR-main-conference standard.
- Re-read local paper, docs, experiments, prior-work artifacts, PDF state, and repo state.
- Determined that missing real-robot/high-fidelity evidence, template-generated experiments, and unresolved novelty threats are not recoverable from local artifacts.
- Recompiled the canonical PDF with `Submission-hardening version: v3`.
- Terminal decision: KILL_ARCHIVE.

## v4 - Paper-Specific World-Model Reliability Rebuild
- Replaced the generic archive framing with a deterministic world-model uncertainty-bloat benchmark.
- Added four manipulation tasks, five hidden-mechanics splits, eight methods, seven seeds, ablations, stress sweeps, negative cases, and figures.
- Reported 47,040 main rollouts, 8,232 ablation rollouts, and 120,960 stress rollouts.
- Found that the proposed audit loses task success to active probing, loses safety to robust MPC, and is contradicted by ablations.
- Terminal decision: KILL_ARCHIVE.

## v4.1 - 2026-06-15 Rerun Audit
- Re-ran `python -m py_compile src\run_experiment.py` and `python src\run_experiment.py`.
- Confirmed the paired task-success difference versus `active_probe_then_plan` is `-0.09864 +/- 0.01937`.
- Confirmed `robust_mpc_fallback` has much lower unsafe-action rate than the proposed audit.
- Confirmed `minus_mechanism_classifier` and `minus_repair_memory` improve success over the full method.
- Updated child docs and paper source to keep the v4 KILL_ARCHIVE decision evidence-bound.

## v5 - Expanded Submission-Readiness Audit
- Froze a paper-specific hostile-review plan before execution.
- Rebuilt the evidence suite with ten seeds, six tasks, eight splits, thirteen main methods, ten ablations, six stress axes, four fixed-risk budgets, and 24 negative cases.
- Generated 199,680 main rollout rows, 15,360 dataset summary rows, 1,040 main seed-metric rows, 1,248 aggregate metric rows, 672 paired rows, 130 hard-aggregate seed rows, 156 hard-aggregate metric rows, 84 hard-aggregate paired rows, 33,600 ablation rows, 302,400 stress rows, and 69,120 fixed-risk rows.
- Generated a 25-page ICLR-style negative archive manuscript with bright boxed clickable citation links.
- Validated the canonical Downloads-only PDF at `C:/Users/wangz/Downloads/88.pdf` with SHA256 `755790FF694B3B6ACE536AE7994CFA1DFB049F43F7A3D5912F6D185127C984EB`.
- Visual PDF QA passed after cleaning the negative-case table and appendix Pareto labels.
- Terminal decision: KILL_ARCHIVE.
