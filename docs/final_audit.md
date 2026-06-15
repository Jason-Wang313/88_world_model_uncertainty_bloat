# Final Audit

1. Chosen thesis: World-Model Uncertainty Bloat explores `Expose cases where uncertainty mechanisms hide missing mechanics instead of repairing them.` for robot world-model reliability.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v4.
4. Latest rerun: 2026-06-15; `python -m py_compile src\run_experiment.py` and `python src\run_experiment.py` completed.
5. Evidence coverage: 47,040 main rollouts, 8,232 ablation rollouts, 120,960 stress rollouts, seven seeds, four tasks, five splits, eight methods, seven ablations, six stress axes, and four negative cases.
6. Main result: on combined missing mechanics, `uncertainty_bloat_audit` reaches `0.53741 +/- 0.01266` task success; `active_probe_then_plan` reaches `0.63605 +/- 0.01979`; paired task-success difference is `-0.09864 +/- 0.01937`.
7. Safety result: `robust_mpc_fallback` has unsafe-action rate `0.05697`, while the proposed audit has `0.21429`.
8. Contradictory evidence: `minus_mechanism_classifier` and `minus_repair_memory` improve success, so the full mechanism is not validated by ablation.
9. Reason: local synthetic evidence is useful for a negative audit but contradicts the ICLR-main submission claim and lacks hardware or recognized high-fidelity benchmark validation.
10. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, and `docs/hostile_reviewer_response.md`.
11. Reproducibility: local code runs and regenerates CSVs, figures, and the PDF source, but no real robot or high-fidelity benchmark is reproduced.
12. Claim-validity status: main-conference claims killed; archive memo retained.
13. Exact Downloads PDF path: `C:/Users/wangz/Downloads/88.pdf`
14. GitHub URL: https://github.com/Jason-Wang313/88_world_model_uncertainty_bloat
15. Confirmation: no visible Desktop copy was requested or made.
