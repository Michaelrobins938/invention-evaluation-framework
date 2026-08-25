# Design: Employer-Review Repository Enrichment

**Date:** 2026-08-25
**Status:** Approved
**Goal:** Make the invention-evaluation-framework repo maximally presentable and professional for employer review, telling a problem-first story while preserving all technical depth.

## Audience & Narrative

Employer reviewers (engineering managers, senior engineers) scanning the repo landing page. Narrative: problem-first balanced — lead with the problem (invention evaluation demands conclusions that evidence actually supports; LLM pipelines hallucinate confidence), then showcase the differentiator (evidence-governed multi-agent architecture with epistemic gates), with patent/IP as the demonstration domain.

## Components

### 1. README restructure (top-of-funnel rebuild)

Order after the change:

1. Cover image (kept, line 13)
2. Badge row: CI status (`main` workflow), Python `3.11 | 3.13`, tests count, MIT license
3. Three-sentence pitch paragraph (problem-first, no hype)
4. **30-second proof block** — direct links to real committed artifacts from the US8527057B2 Complete-pass run: rendered report PDF, execution-ledger.json, epistemic-gate-report.json (paths verified during planning; if not git-tracked, commit curated copies under `docs/demo/`)
5. Quick Start (moved up from line ~439)
6. Existing deep-dive sections preserved in current order (Architecture → … → Roadmap)

Staleness fixes: test-count references 214 → 281 (and suite breakdown), status table updated where it contradicts current reality. No section deletions.

### 2. Root cleanup

`git mv` to `docs/history/`:
- `HANDOFF-v1.9.md`
- `V1.7_COMPLETION.md`
- `V1.8_COMPLETION.md`
- `v1.8-architectural-fix-proposal.md`

Root keeps: README.md, LICENSE, CHANGELOG.md, IEF_EXECUTION_CONTRACT.md. Grep repo for links referencing the moved files and update them.

### 3. CI workflow — `.github/workflows/ci.yml`

- Trigger: push to `main` + pull_request
- Matrix: Python 3.11 and 3.13 (ubuntu-latest)
- Steps: checkout → setup-python → pip install pytest (+ minimal runtime deps discovered from imports during planning) → run all four suites: `engine_v17/epo_ops/tests tests Test-report-results/tests_v17 report-renderer/tests`
- If renderer tests require system packages (chromium/poppler), add apt install step; verified by inspecting renderer test imports before finalizing
- Suite must pass without EPO credentials (all HTTP mocked/hermetic) — verified locally by running suites with env vars cleared

Badge: `https://github.com/Michaelrobins938/invention-evaluation-framework/actions/workflows/ci.yml/badge.svg`

### 4. GitHub About metadata (gh CLI)

- Description: "Evidence-governed multi-agent engine that evaluates inventions against patents and scientific literature — every conclusion traced to verifiable sources."
- Topics: `multi-agent-systems`, `llm-orchestration`, `patent-analysis`, `evidence-based-reasoning`, `python`
- Homepage: none (no deployed site)

### 5. Demo curation

Verify tracked status of `evaluations/us8527057-v17(Complete-pass)/report-us8527057-v17.pdf` and `.html`. If tracked → link directly. If untracked/ignored → copy report PDF + HTML + execution-ledger.json into `docs/demo/us8527057b2/` and link those.

## Error handling

- All file moves via `git mv` (history preserved); broken-reference grep before commit.
- CI designed hermetic: no secrets required at any step.
- gh metadata failures (auth/scopes) reported, never block the code changes.

## Out of scope

- Git history rewrites; renaming evaluation directories; CONTRIBUTING.md / issue templates / releases.

## Acceptance criteria

1. Landing page shows badges, pitch, and working demo links within the first screenful.
2. Root contains only README/LICENSE/CHANGELOG/IEF_EXECUTION_CONTRACT.md among markdown files.
3. CI workflow exists, is hermetic, and passes on push; badge renders green.
4. GitHub About shows description + topics.
5. All referenced docs resolve; full test suite still green (281).
