# Plan

Build and audit paper 88 `world_model_uncertainty_bloat` under the ICLR-main evidence gate. The paper is terminal only after a paper-specific frozen plan, CPU-only evidence rerun, hostile baseline/stress/ablation/fixed-risk audit, honest readiness decision, 25+ page rebuilt PDF in Downloads only, public GitHub push, and root ledger update.

## Current Decision

Terminal decision: `KILL_ARCHIVE`.

The 2026-06-21/2026-06-22 v5 expanded pass confirms that world-model uncertainty bloat is a useful failure concept, but the proposed mechanics-gap auditor is not a submission-ready solution. It detects hidden mechanisms better than older uncertainty-bloat variants, but it loses hard-aggregate task success to `robust_mpc_fallback`, does not beat `active_probe_then_plan` decisively, is less safe than robust MPC, fails mechanism and fixed-risk gates, and lacks real robot or accepted high-fidelity external validation.

## Required Local Commands

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

Canonical PDF target: `C:/Users/wangz/Downloads/88.pdf`.

Visible Desktop PDF target: none.
