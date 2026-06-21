# Final Audit

1. Chosen thesis: World-Model Uncertainty Bloat explores `Expose cases where uncertainty mechanisms hide missing mechanics instead of repairing them.` for robot world-model reliability.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v5 expanded.
4. Latest rerun: 2026-06-21/2026-06-22; code compilation, full deterministic experiment, figure regeneration, manuscript generation, BibTeX/PDF compilation, artifact validation, and visual PDF QA completed.
5. Evidence coverage: 199,680 main rollouts, 15,360 dataset summary rows, 1,040 main seed rows, 1,248 aggregate metric rows, 672 paired rows, 130 hard-aggregate seed rows, 156 hard-aggregate metric rows, 84 hard-aggregate paired rows, 33,600 ablation rollouts, 302,400 stress rows, 69,120 fixed-risk rows, ten seeds, six tasks, eight splits, thirteen methods, ten ablations, six stress axes, four fixed-risk budgets, and 24 negative cases.
6. Main result: on the hard aggregate, `mechanics_gap_auditor_v5` reaches `0.60642` task success; `robust_mpc_fallback` reaches `0.66701`; paired success lower95 is `-0.07734`.
7. Diagnostic result: v5 improves hidden-mechanism F1 (`0.58903`) over `robust_mpc_fallback` (`0.14463`) and over the old v4 audit (`0.44907`), but this diagnostic win does not produce a submission-grade robotics result.
8. Safety result: `robust_mpc_fallback` has unsafe-action rate `0.04861`, while v5 has `0.13768`.
9. Utility result: best robust utility is `0.39872`; v5 utility is `0.23714`.
10. Mechanism gate: failed because ablations do not prove every core component is necessary.
11. Fixed-risk gate: failed because strict budget `0.05` coverage collapses on hard fixed-risk splits.
12. Stress gate: passed the frozen non-domination check, but this alone cannot rescue the paper.
13. Scope gate: failed because no real robot or accepted high-fidelity external benchmark validation exists.
14. Closest hostile prior work: drawn from `docs/deep_read_250.csv` and rendered into bright boxed clickable citation links and bibliography entries.
15. Reproducibility: local code regenerates CSVs, figures, manuscript source, and the validated PDF.
16. Claim-validity status: main-conference claims killed; negative archive retained.
17. Exact Downloads PDF path: `C:/Users/wangz/Downloads/88.pdf`
18. Exact PDF SHA256: `755790FF694B3B6ACE536AE7994CFA1DFB049F43F7A3D5912F6D185127C984EB`
19. PDF pages: 25.
20. GitHub URL: https://github.com/Jason-Wang313/88_world_model_uncertainty_bloat
21. Confirmation: no visible Desktop copy was requested or made.
