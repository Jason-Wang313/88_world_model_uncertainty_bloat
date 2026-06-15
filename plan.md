# Plan

Build and audit paper 88 `world_model_uncertainty_bloat` under the ICLR-main evidence gate. The paper is terminal only after a paper-specific plan, source rerun, evidence audit, honest readiness decision, rebuilt PDF in Downloads only, public GitHub push, and root ledger update.

## Current Decision

Terminal decision: `KILL_ARCHIVE`.

The 2026-06-15 rerun confirms that world-model uncertainty bloat is a useful failure concept, but the proposed audit is not a submission-ready solution. It loses combined-missing-mechanics task success to `active_probe_then_plan`, has a much worse unsafe-action rate than `robust_mpc_fallback`, degrades faster under maximum combined stress, and is contradicted by ablations where removing the mechanism classifier or repair memory improves success.

## Required Local Commands

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical PDF target: `C:/Users/wangz/Downloads/88.pdf`.

Visible Desktop PDF target: none.
