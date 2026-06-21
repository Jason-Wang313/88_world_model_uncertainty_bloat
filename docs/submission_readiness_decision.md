# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Submission-hardening version: v5 expanded.

Latest rerun: 2026-06-21/2026-06-22 from `src/run_experiment.py`, with manuscript generation and validated 25-page PDF artifact.

Reason: The v5 rebuild is materially stronger than the v4 archive. It uses a frozen hostile protocol with ten seeds, six tasks, eight splits, thirteen main methods, ten ablations, six stress axes, four fixed-risk budgets, 24 negative cases, 199,680 main rollouts, 33,600 ablation rollouts, 302,400 stress rows, 69,120 fixed-risk rows, bright boxed citation links, and visual PDF QA. However, it fails the paper's own ICLR-main gates.

Primary blocker: `mechanics_gap_auditor_v5` reaches hard-aggregate success `0.60642`, while `robust_mpc_fallback` reaches `0.66701`; paired success lower95 is `-0.07734`. The method improves hidden-mechanism F1, but the improvement is not enough because unsafe action is `0.13768` versus `0.04861` for the safest reference, and robust utility is `0.23714` versus best utility `0.39872`.

Additional blockers: the mechanism ablation gate fails, fixed-risk deployment at budget `0.05` has zero accepted coverage on hard splits, and the scope gate fails because there is no real robot hardware or accepted high-fidelity benchmark validation.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with hardware or accepted benchmark validation, implemented learned world-model diagnostics, released model/checkpoint artifacts, real competing baselines, manually synthesized related work, and deployment evidence that diagnosis improves both task success and safety.
