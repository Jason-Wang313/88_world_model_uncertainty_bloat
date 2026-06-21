# Paper 88 Submission-Readiness Audit v5

Date: 2026-06-21/2026-06-22

Decision: KILL_ARCHIVE

ICLR main ready: no

## Frozen Protocol

- CPU-only and RAM-light.
- Do not optimize for pretty results.
- Use strong baselines and stress tests to expose weaknesses.
- Freeze the final protocol before reporting.
- Report all predefined results honestly.
- Keep successful numbered PDF artifacts in Downloads only.
- Do not copy PDFs to the visible Desktop.

## Evidence Inventory

- Main rollouts: 199,680.
- Dataset summaries: 15,360.
- Main seed metrics: 1,040.
- Main aggregate metrics: 1,248.
- Main paired comparisons: 672.
- Hard-aggregate seed metrics: 130.
- Hard-aggregate aggregate metrics: 156.
- Hard-aggregate paired comparisons: 84.
- Ablation rollouts: 33,600.
- Stress rows: 302,400.
- Fixed-risk rows: 69,120.
- Negative cases: 24.

## Gate Results

- Main gate: false.
- Mechanism gate: false.
- Stress gate: true.
- Fixed-risk gate: false.
- Scope gate: false.

## Key Numbers

- Proposal hard-aggregate success: `0.60642`.
- Best hard-aggregate success: `0.66701` from `robust_mpc_fallback`.
- Paired success lower95: `-0.07734`.
- Proposal hidden-mechanism F1: `0.58903`.
- Best hidden-mechanism F1: `0.56956` from `active_probe_then_plan`.
- Proposal unsafe action: `0.13768`.
- Safest unsafe action: `0.04861` from `robust_mpc_fallback`.
- Proposal robust utility: `0.23714`.
- Best robust utility: `0.39872` from `robust_mpc_fallback`.

## Artifact Verification

- PDF: `C:/Users/wangz/Downloads/88.pdf`
- Pages: 25.
- SHA256: `755790FF694B3B6ACE536AE7994CFA1DFB049F43F7A3D5912F6D185127C984EB`
- Desktop copy: absent.
- Validator: passed.
- Visual QA: passed after table and figure cleanup.

## Terminal Reason

The paper became a stronger negative archive, not a plausible ICLR-main submission. The proposed v5 auditor improves diagnostic F1 but loses success and utility to robust MPC, is less safe than the safest reference, fails the ablation and fixed-risk gates, and lacks real robot or accepted high-fidelity external evidence.
