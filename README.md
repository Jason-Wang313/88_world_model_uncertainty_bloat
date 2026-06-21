# 88 World-Model Uncertainty Bloat

Submission-hardening version: v5 expanded

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

This repository contains a reproducible local evidence audit for the research bet:

> Expose cases where uncertainty mechanisms hide missing mechanics instead of repairing them.

The v5 rebuild replaces the earlier short v4 archive with a 25-page ICLR-style negative submission-readiness manuscript, a frozen CPU-only mechanics-gap audit, strong uncertainty/control/probing baselines, ablations, stress sweeps, fixed-risk deployment checks, negative cases, visual PDF QA, and bright boxed clickable citation links.

Latest audited rerun: 2026-06-21/2026-06-22. The source experiment compiled, regenerated deterministic CSV evidence, regenerated figures from frozen CSVs, rebuilt the manuscript, and validated the final PDF at `C:/Users/wangz/Downloads/88.pdf`.

Final Downloads PDF SHA256: `755790FF694B3B6ACE536AE7994CFA1DFB049F43F7A3D5912F6D185127C984EB`.

## Why This Is Archived

- On the hard aggregate, `mechanics_gap_auditor_v5` reaches `0.60642` task success.
- The strongest success reference, `robust_mpc_fallback`, reaches `0.66701`.
- The paired success lower95 for v5 versus the best success reference is `-0.07734`.
- v5 improves hidden-mechanism F1, but does not convert that diagnostic gain into a submission-grade robotics result.
- The safest reference, `robust_mpc_fallback`, has unsafe-action rate `0.04861`; v5 has `0.13768`.
- The best robust utility is `0.39872`; v5 utility is `0.23714`.
- The mechanism gate fails because ablations do not establish necessity.
- The fixed-risk deployment gate fails because strict budget `0.05` coverage collapses to zero on the hard fixed-risk splits.
- The scope gate fails because there is no real robot or accepted high-fidelity external benchmark evidence.

## Evidence Coverage

- Main rollouts: 199,680 rows.
- Dataset summary rows: 15,360.
- Main seed-metric rows: 1,040.
- Main aggregate metric rows: 1,248.
- Main paired rows: 672.
- Hard-aggregate seed rows: 130.
- Hard-aggregate metric rows: 156.
- Hard-aggregate paired rows: 84.
- Ablation rollouts: 33,600 rows.
- Stress rollouts: 302,400 rows.
- Fixed-risk rollouts: 69,120 rows.
- Negative cases: 24.
- Seeds: 0 through 9.
- Tasks: six manipulation/contact tasks.
- Splits: eight uncertainty, shift, and missing-mechanics regimes.
- Methods: thirteen main methods, including mean world-model MPC, ensemble/dropout/conformal UQ, active probing, robust MPC, residual repair, Bayesian expansion, v4, v5, and oracle references.

## Reproduce

```powershell
python -m py_compile src\run_experiment.py scripts\generate_manuscript.py scripts\validate_submission_artifacts.py
python src\run_experiment.py
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cd ..
python scripts\validate_submission_artifacts.py
```

The final numbered PDF belongs in Downloads only:

- Canonical local PDF: `C:/Users/wangz/Downloads/88.pdf`
- Visible Desktop PDF target: none.
