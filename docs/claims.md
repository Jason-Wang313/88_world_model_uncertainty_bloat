# Claims

- Mechanism claim tested: world-model uncertainty bloat can hide missing physical mechanics unless the robot separates aleatoric noise, epistemic uncertainty, missing contact/friction/actuation/latency/fixture mechanisms, probe value, and repair memory.
- Evidence claim supported: the v5 audit is a substantially stronger local negative study than v4, with 199,680 main rollouts, 33,600 ablation rows, 302,400 stress rows, 69,120 fixed-risk rows, 24 negative cases, and bright boxed citation links in a 25-page PDF.
- Diagnostic claim partially supported: `mechanics_gap_auditor_v5` improves hidden-mechanism F1 relative to robust MPC and the old v4 audit.
- Submission claim rejected: v5 is not ICLR-main ready because hard-aggregate success, safety, robust utility, ablation necessity, fixed-risk coverage, and external-validation gates fail.
- Scope claim: results support a reproducible local negative audit, not real-robot deployment or SOTA robot policy performance.
- Unsupported claim explicitly avoided: no claim of ICLR-main-ready robotics performance, hardware validity, recognized benchmark transfer, or state-of-the-art world-model reliability.
