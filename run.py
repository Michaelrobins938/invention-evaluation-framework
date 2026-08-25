#!/usr/bin/env python3
"""One-command invention evaluation.

Point this at a folder of invention documents (PDFs, DOCX, TXT, MD)
and it runs the full evaluation pipeline end-to-end.

Usage:
    python run.py /path/to/invention-folder
    python run.py /path/to/invention-folder --id US8527057
    python run.py /path/to/invention-folder --output ./my-results
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
import warnings
from pathlib import Path

# Ensure engine_v17 is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine_v17.pdf_parser import (
    extract_all,
    detect_id_from_filenames,
    detect_id_from_text,
)


# ---------------------------------------------------------------------------
# Folder scanning
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
SKIP_PREFIXES = ("~$", ".", "Thumbs", "desktop")


def scan_folder(folder: Path) -> list[Path]:
    """Return supported document files in *folder*, sorted, skipping junk."""
    files = []
    for p in sorted(folder.iterdir()):
        if p.is_dir():
            continue
        if any(p.name.startswith(skip) for skip in SKIP_PREFIXES):
            continue
        if p.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(p)
    return files


# ---------------------------------------------------------------------------
# ID detection
# ---------------------------------------------------------------------------

def resolve_invention_id(folder: Path, files: list[Path], explicit_id: str | None) -> str:
    """Determine the invention/patent ID.  Prompt user as last resort."""
    if explicit_id:
        normalized = re.sub(r"[^A-Za-z0-9]+", "", explicit_id).upper()
        if normalized:
            return normalized
        print("  Warning: --id value contained no alphanumeric characters, prompting user.")

    # 1. Try filenames
    detected = detect_id_from_filenames(folder)
    if detected:
        return detected

    # 2. Try document content (first 2 pages of each PDF, full text for small files)
    for f in files:
        if f.suffix.lower() == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(f) as pdf:
                    text = ""
                    for page in pdf.pages[:2]:
                        t = page.extract_text()
                        if t:
                            text += t + "\n"
                    detected = detect_id_from_text(text)
                    if detected:
                        return detected
            except Exception:
                pass
        elif f.suffix.lower() in (".txt", ".md"):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")[:2000]
                detected = detect_id_from_text(text)
                if detected:
                    return detected
            except Exception:
                pass

    # 3. Prompt
    print()
    print("  Could not auto-detect an invention/patent ID from the files.")
    print("  Examples: US8527057, 8530, WO2020123456")
    while True:
        user_id = input("  Enter invention/patent ID: ").strip()
        if user_id:
            normalized = re.sub(r"[^A-Za-z0-9]+", "", user_id).upper()
            if normalized:
                return normalized
            print("  Please enter a valid ID (letters and numbers).")


# ---------------------------------------------------------------------------
# Document parsing → submission
# ---------------------------------------------------------------------------

SUBMISSION_TEMPLATE = """\
# Submission — {invention_id}

**Source files:** {file_list}
**Auto-extracted:** {timestamp}
**Note:** This submission was auto-extracted from source documents. \
Fields should be verified by the inventor or evaluator.

## Invention Name
{name}

## Description
{description}

## Background
{background}

## Innovation Claims
{claims}

## Proof of Concept Status
{poc}

## IP Status
{ip_status}

## Target Markets
{markets}

## Known Competitors
{competitors}

## Disclosure Timing
{disclosure}

---

*Extracted from: {file_names}*
*Extraction warnings: {warnings_list}*
"""


def build_submission(
    invention_id: str,
    extracted: dict[Path, str],
) -> tuple[str, list[str]]:
    """Build a submission markdown string from extracted document text.

    Returns (submission_text, list_of_warnings).
    """
    warnings_list = []
    combined_text = "\n\n".join(extracted.values())
    file_names = ", ".join(p.name for p in extracted)

    # Best-effort extraction of structured fields from combined text
    name = _field(extracted, "invention name", "title", "name of invention")
    description = _field(extracted, "description", "summary", "abstract", "overview")
    background = _field(extracted, "background", "prior art", "related work", "context")
    claims = _field(extracted, "claim", "innovation", "novelty", "what is new")
    poc = _field(extracted, "proof of concept", "prototype", "poc", "demonstration")
    ip_status = _field(extracted, "ip status", "patent status", "intellectual property", "filing status")
    markets = _field(extracted, "market", "target market", "application", "use case")
    competitors = _field(extracted, "competitor", "competition", "alternative")
    disclosure = _field(extracted, "disclosure", "publication", "public disclosure", "sale offer")

    # If most fields are empty, use combined text as description fallback
    if not description and combined_text.strip():
        description = combined_text[:3000]
        warnings_list.append("No structured description found; using raw document text (truncated to 3000 chars)")

    if not name:
        name = f"Invention {invention_id}"
        warnings_list.append("Invention name not detected; using ID as placeholder")

    for field_name, value in [
        ("description", description), ("background", background),
        ("claims", claims), ("disclosure", disclosure),
    ]:
        if not value:
            warnings_list.append(f"Field '{field_name}' could not be auto-extracted; requires manual input")

    submission = SUBMISSION_TEMPLATE.format(
        invention_id=invention_id,
        file_list=file_names,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        name=name,
        description=description or "_Not auto-extracted — requires manual input._",
        background=background or "_Not auto-extracted._",
        claims=claims or "_Not auto-extracted — requires manual input._",
        poc=poc or "_Not auto-extracted._",
        ip_status=ip_status or "_Not auto-extracted._",
        markets=markets or "_Not auto-extracted._",
        competitors=competitors or "_Not auto-extracted._",
        disclosure=disclosure or "_Not auto-extracted — critical field, requires inventor input._",
        file_names=file_names,
        warnings_list="; ".join(warnings_list) if warnings_list else "none",
    )

    return submission, warnings_list


def _field(extracted: dict[Path, str], *keywords: str) -> str:
    """Try to find a section or sentence matching any of the keywords."""
    combined = "\n\n".join(extracted.values())
    lower = combined.lower()

    for kw in keywords:
        # Look for a section header containing the keyword
        pattern = rf"(?:^|\n)#+\s*.*?{re.escape(kw)}.*?\n(.*?)(?=\n#|\n$|\Z)"
        match = re.search(pattern, combined, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            if len(text) > 20:
                return text[:2000]

        # Look for a sentence containing the keyword
        sentences = re.split(r"[.!?\n]", combined)
        for sent in sentences:
            if kw in sent.lower() and len(sent.strip()) > 30:
                return sent.strip()[:2000]

    return ""


# ---------------------------------------------------------------------------
# Evaluation directory setup
# ---------------------------------------------------------------------------

def setup_evaluation_dir(
    invention_id: str,
    source_folder: Path,
    files: list[Path],
) -> Path:
    """Create evaluations/{id}/ and copy source files into source/."""
    eval_dir = Path("evaluations") / invention_id.lower()
    source_dir = eval_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)

    for f in files:
        dest = source_dir / f.name
        if not dest.exists():
            shutil.copy2(f, dest)

    return eval_dir


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(
    invention_id: str,
    submission_path: Path,
    output_dir: Path,
    evaluation_dir: Path,
    evaluation_files: list[Path],
) -> dict:
    """Run the full IEF pipeline with graceful fallback on any error."""
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt

    # The target is the first source file (or submission if no source)
    target = str(submission_path)
    if evaluation_files:
        target = str(evaluation_files[0])

    return run_with_autoprompt(
        evaluation_id=invention_id,
        target=target,
        output_dir=output_dir,
        evaluation_dir=evaluation_dir,
        hermetic=False,
        execution_mode="REAL_AUTOPROMPT",
        epistemic_mode="FULL_CONTROLLER",
        review_mode="INDEPENDENT",
        verification_mode="BLIND_FRESH",
    )


# ---------------------------------------------------------------------------
# Result printing
# ---------------------------------------------------------------------------

def print_result(result: dict, warnings_list: list[str]) -> None:
    """Print a clear summary of the evaluation run."""
    output_dir = result.get("output_dir", "?")
    status = result.get("combined_status", {})
    exec_status = status.get("execution", "?")
    evidence = status.get("evidence", "?")
    mode = result.get("execution_mode", "?")

    print()
    print("=" * 60)
    print("  EVALUATION COMPLETE")
    print("=" * 60)
    print()
    print(f"  Output:      {output_dir}")
    print(f"  Execution:   {exec_status}")
    print(f"  Evidence:    {evidence}")
    print(f"  Mode:        {mode}")

    # Count artifacts
    out_path = Path(output_dir)
    if out_path.exists():
        artifacts = list(out_path.iterdir())
        print(f"  Artifacts:   {len(artifacts)} files")

        # Check for report
        reports = [p for p in artifacts if p.name.startswith("report-")]
        if reports:
            for r in reports:
                print(f"  Report:      {r}")

    if warnings_list:
        print()
        print("  Warnings:")
        for w in warnings_list:
            print(f"    - {w}")

    # API credential status
    env_path = Path(".env")
    has_creds = False
    if env_path.exists():
        try:
            content = env_path.read_text()
            has_creds = "EPO_OPS_CLIENT_ID" in content and "EPO_OPS_CLIENT_SECRET" in content
        except Exception:
            pass

    if not has_creds:
        print()
        print("  NOTE: No EPO OPS API credentials found in .env")
        print("  Patent search lanes ran without live API access.")
        print("  To enable live patent searches, add credentials from https://developers.epo.org")
        print("  to .env (see .env.example)")

    print()
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate an invention from a folder of documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py ./8530
  python run.py ./8530 --id US8527057
  python run.py ./my-invention --output ./results
        """,
    )
    parser.add_argument("folder", help="Path to folder containing invention documents (PDF, DOCX, TXT, MD)")
    parser.add_argument("--id", help="Patent/invention ID (auto-detected from filenames/content if omitted)")
    parser.add_argument("--output", help="Output directory (default: evaluations/{id}-output)")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory.")
        return 1

    # Step 1: Scan
    print(f"\nScanning {folder.name}/ ...")
    files = scan_folder(folder)
    if not files:
        print(f"Error: No supported files found in {folder}")
        print(f"  Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        return 1
    print(f"  Found {len(files)} file(s): {', '.join(f.name for f in files)}")

    # Step 2: Detect ID
    invention_id = resolve_invention_id(folder, files, args.id)
    print(f"  Invention ID: {invention_id}")

    # Step 3: Parse documents
    print("\nExtracting text from documents ...")
    extracted = extract_all(folder)
    if not extracted:
        print("Warning: Could not extract text from any files.")
        print("  The pipeline will run with minimal intake data.")
        print("  Consider providing a structured submission manually.")
    else:
        total_chars = sum(len(t) for t in extracted.values())
        print(f"  Extracted {total_chars:,} characters from {len(extracted)} file(s)")

    # Step 4: Create submission
    print("\nCreating submission record ...")
    submission_text, warnings_list = build_submission(invention_id, extracted)

    # Step 5: Set up evaluation directory
    eval_dir = setup_evaluation_dir(invention_id, folder, files)
    submission_path = eval_dir / f"submission-{invention_id.lower()}.md"
    submission_path.write_text(submission_text, encoding="utf-8")
    print(f"  Evaluation dir: {eval_dir}")
    print(f"  Submission: {submission_path.name}")

    # Step 6: Run pipeline
    output_dir = Path(args.output) if args.output else Path(f"evaluations/{invention_id.lower()}-output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nRunning evaluation pipeline ...")
    print(f"  Output dir: {output_dir}")
    print()

    try:
        result = run_pipeline(invention_id, submission_path, output_dir, eval_dir, files)
    except Exception as e:
        print(f"\n  Pipeline error: {e}")
        print("  The evaluation may have partially completed.")
        print(f"  Check {output_dir} for any artifacts produced.")

        # Still try to give useful output
        if output_dir.exists():
            artifacts = list(output_dir.iterdir())
            if artifacts:
                print(f"  {len(artifacts)} artifact(s) were produced before the error.")
                print_result({"output_dir": str(output_dir), "combined_status": {"execution": "FAILED", "evidence": "INSUFFICIENT"}, "execution_mode": "REAL_AUTOPROMPT"}, warnings_list)
                return 0
        return 1

    # Step 7: Print result
    print_result(result, warnings_list)
    return 0


if __name__ == "__main__":
    sys.exit(main())
