# Repo Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository employer-review ready: real CI with badge, problem-first README top, root cleanup, GitHub About metadata, curated demo links.

**Architecture:** Docs + CI-only changes; no engine code touched except none. Four suites already pass hermetically (66+38+114+63 = 281 tests). Demo artifacts are git-tracked at `evaluations/us8527057-v17(Complete-pass)/` — linked directly, no copying.

**Tech Stack:** Markdown, GitHub Actions (ubuntu-latest, Python 3.11/3.13), gh CLI.

## Global Constraints

- No engine/test code changes; docs + CI only.
- All moves via `git mv`; no history rewrites; no renames of evaluation dirs.
- CI is hermetic: no secrets, no EPO credentials required.
- Third-party deps (verified via AST scan): `pytest`, `jsonschema`, `Pillow`. System packages for renderer suite: `poppler-utils` (pdfinfo), `chromium` (PDF rendering fixtures).
- Real suite counts: engine_v17/epo_ops/tests=66, tests=38, Test-report-results/tests_v17=114, report-renderer/tests=63 → total **281**.
- Commit after each task; final push to origin/main.

---

### Task 1: Root cleanup

**Files:**
- Move: `HANDOFF-v1.9.md`, `V1.7_COMPLETION.md`, `V1.8_COMPLETION.md`, `v1.8-architectural-fix-proposal.md` → `docs/history/`

- [ ] **Step 1: Move files**

```bash
mkdir -p docs/history
git mv HANDOFF-v1.9.md V1.7_COMPLETION.md V1.8_COMPLETION.md v1.8-architectural-fix-proposal.md docs/history/
```

- [ ] **Step 2: Verify no broken references**

Run: `grep -rn "HANDOFF-v1.9\|V1.7_COMPLETION\|V1.8_COMPLETION\|v1.8-architectural" --include="*.md" --include="*.py" --include="*.sh" . | grep -v docs/history | grep -v docs/superpowers`
Expected: no matches outside moved location and spec docs.

- [ ] **Step 3: Sanity test run**

Run: `python3 -m pytest Test-report-results/tests_v17 -q`
Expected: 114 passed.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "docs: move internal working notes to docs/history/"
```

---

### Task 2: CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Verify hermetic behavior locally (creds cleared)**

```bash
env -u EPO_OPS_CLIENT_ID -u EPO_OPS_CLIENT_SECRET python3 -m pytest engine_v17/epo_ops/tests tests Test-report-results/tests_v17 -q
```
Expected: 218 passed (66+38+114). Renderer suite needs system pdfinfo/chromium — covered by apt step in CI; verified green on this machine already.

- [ ] **Step 2: Write workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.13"]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest jsonschema Pillow

      - name: Install renderer system packages
        run: |
          sudo apt-get update
          sudo apt-get install -y poppler-utils chromium-browser

      - name: Run EPO OPS unit suites
        run: python -m pytest engine_v17/epo_ops/tests -q

      - name: Run integration / failure-mode suites
        run: python -m pytest tests -q

      - name: Run v17 engine suites
        run: python -m pytest Test-report-results/tests_v17 -q

      - name: Run renderer suites
        run: python -m pytest report-renderer/tests -q
```

Note: if `chromium-browser` package name fails on the runner, use `chromium` — implementer checks the first CI run and fixes the package name in a follow-up commit.

- [ ] **Step 3: YAML sanity**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml')); print('YAML OK')"`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml && git commit -m "ci: run all four test suites on Python 3.11/3.13"
```

---

### Task 3: README restructure

**Files:**
- Modify: `README.md` (anchors below; line numbers are pre-edit references only)

- [ ] **Step 1: Replace static badge with badge row**

Replace the line matching `[![Tests](https://img.shields.io/badge/tests-214%20passing-brightgreen)](#)` with:

```markdown
[![CI](https://github.com/Michaelrobins938/invention-evaluation-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/Michaelrobins938/invention-evaluation-framework/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue)
![Tests](https://img.shields.io/badge/tests-281%20passing-brightgreen)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
```

- [ ] **Step 2: Insert pitch paragraph directly under the cover image block (after line containing `Assets/invention-evaluation-cover.png`)**

```markdown

Most AI evaluation pipelines produce confident conclusions from unverifiable reasoning.
The Invention Evaluation Framework takes the opposite stance: **an invention assessment may
only state what its gathered evidence actually supports**. A multi-agent engine decomposes an
invention into propositions, dispatches research workers against live patent and literature
sources (EPO OPS, Crossref), classifies every artifact as external or derived evidence, and
routes each conclusion through independent review and blind fresh verification before anything
reaches the reader.
```

- [ ] **Step 3: Insert 30-second proof block immediately after the pitch**

```markdown
## See It Work (30 seconds)

Real artifacts from a complete evaluation of US8527057B2 — every number in the report traces
to a logged execution:

| Artifact | What it shows |
|----------|---------------|
| [Rendered report (PDF, 29 pages)](evaluations/us8527057-v17%28Complete-pass%29/report-us8527057-v17.pdf) | Consumer-facing deliverable: recommendation, confidence, limitations |
| [Execution ledger](evaluations/us8527057-v17%28Complete-pass%29/execution-ledger.json) | Every live retrieval executed, timestamped, with result counts |
| [Report source (Markdown)](evaluations/us8527057-v17%28Complete-pass%29/report-us8527057-v17.md) | Same report, auditable text form |

Full artifact sets for additional inventions (including deliberately failed runs) live in [`evaluations/`](evaluations/).
```

Implementer verifies each relative link resolves (`test -f` on the decoded path) before committing.

- [ ] **Step 4: Relocate Quick Start**

Cut the entire `## Quick Start` section (currently lines ~439–487, ends before `## Evaluation Output Artifacts`) and paste it immediately after the proof block. Content unchanged except updating the two test-command comments:

- `# 113 existing` → `# 114 v17 engine`
- `# 63 renderer` stays; add missing suites so the block reads:

```bash
python3 -m pytest engine_v17/epo_ops/tests -q              # 66 EPO OPS
python3 -m pytest tests -q                                  # 38 integration/failure
python3 -m pytest Test-report-results/tests_v17 -q          # 114 v17 engine
python3 -m pytest report-renderer/tests -q                  # 63 renderer
```

- [ ] **Step 5: Fix remaining staleness anchors**

1. `**Tests:** 214 passed` → `**Tests:** 281 passed (66 EPO OPS + 38 integration/failure + 114 v17 engine + 63 renderer)`
2. Table row `` | 214 tests | **Passing** (11 real dispatch + 27 integration/failure + 113 IEF + 63 renderer) | `` → `` | 281 tests | **Passing** (66 EPO OPS + 38 integration/failure + 114 v17 engine + 63 renderer) | ``
3. Roadmap sentence ending `, 214 tests.` → `, 281 tests.`
4. Repository Map entry mentioning the four moved root files, if present → update paths to `docs/history/…`

- [ ] **Step 6: Verify links and structure**

```bash
grep -c "^#" README.md   # structure intact
test -f "evaluations/us8527057-v17(Complete-pass)/report-us8527057-v17.pdf" && echo LINK-OK
```

- [ ] **Step 7: Full local suite**

Run: `python3 -m pytest engine_v17/epo_ops/tests tests Test-report-results/tests_v17 report-renderer/tests -q`
Expected: 281 passed.

- [ ] **Step 8: Commit**

```bash
git add README.md && git commit -m "docs: employer-ready README — badges, pitch, demo links, quickstart relocation"
```

---

### Task 4: Publish + metadata + acceptance

- [ ] **Step 1: Push and watch CI**

```bash
git push origin main
gh run watch $(gh run list --workflow=ci.yml --limit 1 --json databaseId --jq '.[0].databaseId') --exit-status
```
If `chromium-browser` package error occurs: switch to `chromium` in ci.yml, commit, push again.

- [ ] **Step 2: GitHub About metadata**

```bash
gh repo edit --description "Evidence-governed multi-agent engine that evaluates inventions against patents and scientific literature — every conclusion traced to verifiable sources."
gh repo edit --add-topic multi-agent-systems --add-topic llm-orchestration --add-topic patent-analysis --add-topic evidence-based-reasoning --add-topic python
```

- [ ] **Step 3: Acceptance sweep**

1. Landing page first screenful: badges + pitch + proof table ✓ (inspect rendered README via `gh repo view --web` optional)
2. Root markdown files: `ls *.md` → CHANGELOG.md, IEF_EXECUTION_CONTRACT.md, README.md only
3. Badge renders green on GitHub
4. `gh repo view --json description,repositoryTopics` shows both
5. Local suite still 281 passing

---

## Self-Review Notes

- Spec coverage: README restructure (Task 3), root cleanup (Task 1), CI (Task 2), metadata (Task 4), demo curation (Task 3 Step 3 — direct links, tracked confirmed). Acceptance criteria map to Task 4 Step 3.
- Placeholders: none; all content verbatim; chromium package-name contingency has explicit fallback step.
- Consistency: counts used everywhere = 66/38/114/63 = 281 (collected via pytest --collect-only).
