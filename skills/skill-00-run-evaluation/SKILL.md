---
name: run-invention-evaluation
description: One-command invention evaluation from a folder of documents. Point at a folder containing PDFs, DOCX, TXT, or MD files describing an invention and the full evaluation pipeline runs automatically. Use when a user says "evaluate this invention", "run the pipeline on these files", "assess this disclosure", or provides a folder of invention documents. Handles ID detection, text extraction, submission creation, and end-to-end pipeline execution with graceful fallback on missing data or APIs.
---

# Run Invention Evaluation

## When to use
- User provides a folder of invention documents and wants an evaluation
- User says "evaluate this", "run the pipeline", "assess this invention"
- User has disclosure PDFs, attachments, or reference files

## When NOT to use
- User wants a single specific analysis (market only, novelty only) — use that phase's skill directly
- User asks about FTO/infringement — redirect to counsel
- User wants to understand the pipeline architecture — use the full orchestrator skill

## Execution

### Step 1: Identify the folder

Ask the user for the path to their invention folder, or locate it from context. The folder should contain documents describing the invention (PDFs, DOCX, TXT, or MD files).

### Step 2: Run the evaluation

The framework lives at: `{{FRAMEWORK_ROOT}}`

```bash
python3 {{FRAMEWORK_ROOT}}/run.py /path/to/invention-folder
```

Optional arguments:
- `--id US8527057` — specify the patent/invention ID manually (auto-detected if omitted)
- `--output ./my-results` — custom output directory (default: `{{FRAMEWORK_ROOT}}/evaluations/{id}-output`)

### Step 3: Report results

The command prints the output location and status. Report to the user:
1. Where the results are (output directory)
2. The execution status (COMPLETED, COMPLETED_WITH_EVIDENCE_DEBT, etc.)
3. Whether report files were generated (MD, HTML, PDF)
4. Any warnings from text extraction or missing fields

### What happens internally

The script handles everything automatically:
1. Scans the folder for PDF, DOCX, TXT, MD files (skips temp files like `~$*`)
2. Detects the invention ID from filenames or folder name (prompts user if ambiguous)
3. Extracts text from all documents using pdfplumber/docx
4. Creates a structured `submission-{id}.md` record
5. Sets up `evaluations/{id}/source/` with copies of the originals
6. Runs the full IEF pipeline (gather → analyze → landscape → novelty → literature → market → partners → compile → render)
7. Outputs all artifacts to `evaluations/{id}-output/`

### Fallback behavior (never mocked)

- **No API credentials**: Patent search lanes run without live data, producing evidence debt artifacts (valid result)
- **PDF extraction fails**: Uses what it can, warns about failed files, continues
- **ID detection fails**: Prompts the user to enter it manually
- **Partial pipeline failure**: Saves whatever artifacts were produced, reports what succeeded and what failed
- **Missing submission fields**: Flags them for manual input rather than guessing

### Output artifacts

The output directory contains:
- `report-{id}.md` / `.html` / `.pdf` — the evaluation report
- `execution-ledger.json` — every retrieval executed, timestamped
- `proposition-ledger.json` — all propositions with evidence states
- `combined-status.json` — final execution + evidence status
- `epistemic-gate-report.json` — E0-E9 gate verdicts
- `review-ledger.json` — independent review + verification records
- Plus ~20 more structured artifacts

### Error handling

If the script fails:
1. Check the error message — it will say what went wrong
2. Common issues: folder doesn't exist, no supported files, Python dependencies missing
3. Re-run setup if dependencies are missing: `bash {{FRAMEWORK_ROOT}}/setup.sh`
4. The output directory may still contain partial results — check it

## Reference

- `{{FRAMEWORK_ROOT}}/run.py` — the CLI entry point
- `{{FRAMEWORK_ROOT}}/engine_v17/pdf_parser.py` — document text extraction
- `{{FRAMEWORK_ROOT}}/engine_v17/orchestrator_autoprompt.py` — pipeline orchestrator
- `{{FRAMEWORK_ROOT}}/skills/Skill-00.md` — full pipeline documentation (all 10 phases)
