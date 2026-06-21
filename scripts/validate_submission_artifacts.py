import csv
import hashlib
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOWNLOADS_PDF = Path.home() / "Downloads" / "88.pdf"
DESKTOP_PDF = Path.home() / "Desktop" / "88.pdf"

EXPECTED_ROWS = {
    "rollouts.csv": 199680,
    "dataset_summary.csv": 15360,
    "raw_seed_metrics.csv": 1040,
    "metrics.csv": 1248,
    "pairwise_stats.csv": 672,
    "hard_aggregate_seed_metrics.csv": 130,
    "hard_aggregate_metrics.csv": 156,
    "hard_aggregate_pairwise_stats.csv": 84,
    "ablation_rollouts.csv": 33600,
    "ablation_seed_metrics.csv": 200,
    "ablation_metrics.csv": 20,
    "ablation_metric_long.csv": 240,
    "stress_sweep_raw.csv": 302400,
    "stress_sweep_seed_metrics.csv": 2520,
    "stress_sweep.csv": 252,
    "stress_sweep_metric_long.csv": 3024,
    "fixed_risk_raw.csv": 69120,
    "fixed_risk_seed_metrics.csv": 480,
    "fixed_risk_metrics.csv": 48,
    "fixed_risk_pairwise.csv": 200,
    "negative_cases.csv": 24,
}


def csv_count(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path):
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(path)).pages)
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader

        return len(PdfReader(str(path)).pages)
    except Exception:
        pass
    proc = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True)
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.MULTILINE)
    if not match:
        raise RuntimeError("could not determine PDF page count")
    return int(match.group(1))


def pdf_text_contains(path, tokens):
    try:
        from pypdf import PdfReader

        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages[:10])
    except Exception:
        try:
            from PyPDF2 import PdfReader

            text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages[:10])
        except Exception:
            return
    normalized_text = re.sub(r"[^A-Za-z0-9]+", "", text).upper()
    for token in tokens:
        normalized_token = re.sub(r"[^A-Za-z0-9]+", "", token).upper()
        if token not in text and normalized_token not in normalized_text:
            raise SystemExit(f"PDF text missing token: {token}")


def main():
    for name, expected in EXPECTED_ROWS.items():
        path = RESULTS / name
        if not path.exists():
            raise SystemExit(f"missing expected CSV: {path}")
        observed = csv_count(path)
        if observed != expected:
            raise SystemExit(f"row-count mismatch for {name}: expected {expected}, observed {observed}")

    summary = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    required_summary = [
        "Terminal recommendation: KILL_ARCHIVE",
        "ICLR main ready: no",
        "Main rollout rows: 199680",
        "Dataset summary rows: 15360",
        "Ablation rollout rows: 33600",
        "Stress raw rows: 302400",
        "Fixed-risk raw rows: 69120",
        "Negative cases: 24",
        "best_success_reference=robust_mpc_fallback",
        "best_f1_reference=active_probe_then_plan",
        "safest_reference=robust_mpc_fallback",
        "lowest_bloat_reference=active_probe_then_plan",
        "proposal_success=0.60642",
        "best_success=0.66701",
        "proposal_f1=0.58903",
        "best_f1=0.56956",
        "proposal_unsafe=0.13768",
        "safest_unsafe=0.04861",
        "proposal_bloat=0.33433",
        "lowest_bloat=0.31471",
        "proposal_utility=0.23714",
        "best_utility=0.39872",
        "paired_success_lower95=-0.07734",
        "paired_unsafe_upper95=0.10347",
        "main_gate=False",
        "mechanism_gate=False",
        "stress_gate=True",
        "fixed_risk_gate=False",
        "scope_gate=False",
    ]
    for token in required_summary:
        if token not in summary:
            raise SystemExit(f"missing summary token: {token}")

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    required_tex = [
        r"colorlinks=false",
        r"pdfborder={0 0 1.8}",
        r"citebordercolor={0 1 0}",
        r"linkbordercolor={1 0.55 0}",
        r"urlbordercolor={0 0.45 1}",
        r"\bibliography{references}",
        r"\nocite{*}",
        "KILL/ARCHIVE",
        "mechanics gap auditor v5",
    ]
    for token in required_tex:
        if token not in tex:
            raise SystemExit(f"missing LaTeX token: {token}")

    if not (PAPER / "references.bib").exists():
        raise SystemExit("missing references.bib")

    log_path = PAPER / "main.log"
    if not log_path.exists():
        raise SystemExit("missing LaTeX log")
    log = log_path.read_text(encoding="utf-8", errors="ignore")
    forbidden = [
        "Citation `",
        "Reference `",
        "undefined references",
        "Rerun to get cross-references right",
        "Package natbib Warning",
        "LaTeX Error",
    ]
    for token in forbidden:
        if token in log:
            raise SystemExit(f"LaTeX log still contains forbidden token: {token}")

    if not DOWNLOADS_PDF.exists():
        raise SystemExit(f"missing Downloads PDF: {DOWNLOADS_PDF}")
    if DESKTOP_PDF.exists():
        raise SystemExit(f"Desktop PDF is forbidden: {DESKTOP_PDF}")
    pages = pdf_pages(DOWNLOADS_PDF)
    if pages < 25:
        raise SystemExit(f"PDF too short: expected at least 25 pages, observed {pages}")

    pdf_text_contains(
        DOWNLOADS_PDF,
        [
            "World-Model Uncertainty Bloat",
            "KILL/ARCHIVE",
            "mechanics gap auditor v5",
            "Fixed-risk deployment",
        ],
    )
    print(f"validated Paper 88 artifacts: pages={pages}, sha256={sha256(DOWNLOADS_PDF)}")


if __name__ == "__main__":
    main()
