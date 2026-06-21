# Child Status 88

Current stage: ICLR main v5 expanded evidence audit terminal
Last update: 2026-06-22 02:04:30 +08:00
PDF: C:/Users/wangz/Downloads/88.pdf
PDF SHA256: 755790FF694B3B6ACE536AE7994CFA1DFB049F43F7A3D5912F6D185127C984EB
PDF pages: 25
GitHub: https://github.com/Jason-Wang313/88_world_model_uncertainty_bloat
Submission-hardening version: v5 expanded
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Latest rerun: `python -m py_compile src\run_experiment.py scripts\generate_manuscript.py scripts\validate_submission_artifacts.py`, `python src\run_experiment.py`, manuscript generation, full BibTeX/PDF rebuild, validator, and visual PDF QA completed on 2026-06-21/2026-06-22.

Evidence inventory: 199,680 main rollouts, 15,360 dataset summary rows, 1,040 main seed-metric rows, 1,248 main aggregate metric rows, 672 main paired rows, 130 hard-aggregate seed rows, 156 hard-aggregate metric rows, 84 hard-aggregate paired rows, 33,600 ablation rollouts, 302,400 stress rows, 69,120 fixed-risk rows, ten seeds, six tasks, eight splits, thirteen main methods, ten ablations, six stress axes, four risk budgets, and 24 negative cases.

Reason: the expanded v5 mechanics-gap auditor improves diagnostic F1 over several uncertainty-only methods and clearly improves over the old v4 audit, but it fails the frozen submission gates. Hard-aggregate task success is `0.60642`, below `0.66701` for `robust_mpc_fallback`, with paired success lower95 `-0.07734`; unsafe-action rate is `0.13768`, worse than the safest reference at `0.04861`; robust utility is `0.23714`, below the best utility `0.39872`; ablations do not prove mechanism necessity; fixed-risk coverage at budget `0.05` collapses on the hard missing-mechanics splits; and no real robot or accepted high-fidelity external benchmark is present.
