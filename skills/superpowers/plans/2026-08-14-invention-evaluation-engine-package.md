# Invention Evaluation Engine — Distributable Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the Invention Evaluation Framework v1.5 as a zip deliverable: one installable `invention-evaluation-engine/` folder (engine SKILL.md + 9 bundled sub-skills + docs + Tesla sample), one-command `install.sh`, a `verify.sh`, README, and MIT LICENSE.

**Architecture:** The engine skill is the single entry point; it references the 9 sub-skills and docs by relative path inside its own folder, so it works in any agent tool (Claude Code, OpenCode, Copilot, or a bare LLM). `install.sh` detects the target tool and copies the folder; `verify.sh` statically confirms the install. The zip is built from the project root with `invention-evaluation-framework/` as the archive root.

**Tech Stack:** Bash (POSIX, macOS/Linux; Windows via Git Bash/WSL), Markdown, `zip`/`unzip`, `diff`.

## Global Constraints

- Sub-skill files and docs are copied **byte-identical** from source — no content edits during packaging (v1.5 is frozen).
- Engine SKILL.md must reference sub-skills as `skills/skill-XX-*/SKILL.md` and docs as `docs/*.md` (relative paths only).
- `install.sh` must support `--tool claude|opencode|copilot|custom`, `--path`, `--force`, and auto-detection.
- `verify.sh` must be read-only and exit non-zero on any failure.
- No git repo exists and none will be created (delivery is a zip per spec). Replace "commit" steps with verification steps.
- Deliverable zip: `/home/forsythe/Downloads/invention-evaluation-framework.zip` (replaces the stale Aug-13 zip), archive root `invention-evaluation-framework/`.
- Working directory for all tasks: `/home/forsythe/Downloads/invention-evaluation-framework`.

---

### Task 1: Scaffold package tree and copy framework content byte-identical

**Files:**
- Create: `invention-evaluation-engine/skills/` (9 sub-skill dirs)
- Create: `invention-evaluation-engine/docs/`
- Create: `invention-evaluation-engine/examples/tesla-us433700/`
- Copy: `skill-01…09/*/SKILL.md` → `invention-evaluation-engine/skills/skill-XX-*/SKILL.md`
- Copy: `DIGEST.md`, `GLOSSARY.md`, `INDEX.md`, `PIPELINE_STATE.md` → `invention-evaluation-engine/docs/`
- Copy: `Test-report-results/report-tesla-us433700-e2e-v15.md` → `invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md`

**Interfaces:**
- Consumes: source framework files at project root.
- Produces: `invention-evaluation-engine/` tree that Tasks 2–3 fill in and Tasks 4–5 verify.

- [ ] **Step 1: Create the directory skeleton**

```bash
mkdir -p invention-evaluation-engine/skills invention-evaluation-engine/docs invention-evaluation-engine/examples/tesla-us433700
```

- [ ] **Step 2: Copy the 9 sub-skills byte-identical**

```bash
for d in skill-01-invention-evaluation-overview skill-02-gather-invention-submission skill-03-analyze-technology-fundamentals skill-04-conduct-patent-landscape skill-05-conduct-novelty-search skill-06-conduct-literature-search skill-07-analyze-market-opportunity skill-08-identify-partners skill-09-compile-report; do
  mkdir -p "invention-evaluation-engine/skills/$d"
  cp "$d/SKILL.md" "invention-evaluation-engine/skills/$d/SKILL.md"
done
```

- [ ] **Step 3: Copy docs and the reference report**

```bash
cp DIGEST.md GLOSSARY.md INDEX.md PIPELINE_STATE.md invention-evaluation-engine/docs/
cp Test-report-results/report-tesla-us433700-e2e-v15.md invention-evaluation-engine/examples/tesla-us433700/
```

- [ ] **Step 4: Verify byte-identity**

Run: `diff -r skill-01-invention-evaluation-overview invention-evaluation-engine/skills/skill-01-invention-evaluation-overview && diff -r skill-05-conduct-novelty-search invention-evaluation-engine/skills/skill-05-conduct-novelty-search && diff DIGEST.md invention-evaluation-engine/docs/DIGEST.md && diff Test-report-results/report-tesla-us433700-e2e-v15.md invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md`
Expected: no output (all identical). Repeat the `diff -r` pattern for the remaining 7 sub-skills.

---

### Task 2: Write the engine SKILL.md

**Files:**
- Create: `invention-evaluation-engine/SKILL.md`

**Interfaces:**
- Consumes: the tree from Task 1.
- Produces: the single entry point that Tasks 3–6 document and Task 7–9 test.

- [ ] **Step 1: Write the engine skill**

Write `invention-evaluation-engine/SKILL.md` with exactly this content:

```markdown
---
name: invention-evaluation-engine
description: One-skill entry point for the full nine-phase invention evaluation pipeline (submission capture, technology profile, patent landscape, novelty search, literature search, market opportunity, partner identification, report compilation). Use when the user asks to evaluate an invention, run the full evaluation pipeline, or start a patentability/commercial assessment. Delegates to the bundled sub-skills in skills/ and enforces evidence-grade preservation across hand-offs. Not for FTO/infringement questions — redirect those to counsel.
---

# Invention Evaluation Engine

## What this is

The orchestration layer of an **evidence-constrained invention reasoning engine**. This skill does not perform search or analysis itself — it routes through the nine sub-skills bundled in `skills/` and enforces the framework's governing rule at every hand-off: **nothing downstream may promote an inference into a fact.** Every proposition carries the evidence grade it was established with (see `docs/GLOSSARY.md`).

## When to use
- "Evaluate this invention" / "run the full evaluation pipeline"
- "Is my invention patentable and commercially viable?"
- "Start a full commercial + patentability assessment"

## When NOT to use — redirect instead
- FTO / infringement ("can I sell this without being sued?") — stop and explain the novelty-vs-FTO distinction (see `docs/GLOSSARY.md`); scope it as a separate engagement with counsel. Do not run the novelty pipeline as a substitute.
- A single specific analysis (market only, novelty only) — route directly to the relevant sub-skill instead of the full pipeline.

## Execution

1. **Submission record.** Determine whether a structured submission record exists (user-provided, or `examples/tesla-us433700/submission.md` for the sample run).
   - If none: read `skills/skill-02-gather-invention-submission/SKILL.md` and execute it to capture one. Disclosure and sale-offer dates are mandatory at intake — always capture, even a confirmed "none."
2. **Dependency order.** Execute sub-skills in dependency order per `docs/INDEX.md`, reading each `skills/skill-XX-*/SKILL.md` when its phase is reached:
   - 01 overview → 02 gather-submission → 03 technology-fundamentals → 04 patent-landscape → 05 novelty-search → 06 literature-search → 07 market-opportunity → 08 identify-partners → 09 compile-report
   - Hard dependencies must be satisfied before a phase runs; soft dependencies may be bypassed with degraded capability, noted in the final report.
3. **Evidence-grade preservation.** At every hand-off, carry each proposition with the evidence grade it was established with (CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED) plus any coverage objects. Never upgrade or strip grades.
4. **Phase checklist.** Maintain a phase-completion checklist with explicit `blocked / needs-input` states. If a phase is blocked, say so — do not guess.
5. **Report.** Compile the final report via `skills/skill-09-compile-report/SKILL.md`, including the reproducible query log and the "not legal advice" disclaimers.

## Reference docs (relative to this skill's folder)

- `docs/DIGEST.md` — 5-minute read; the non-negotiables
- `docs/GLOSSARY.md` — full terminology, evidence ontology, decision matrix
- `docs/INDEX.md` — dependency graph, entry points, dependency types
- `docs/PIPELINE_STATE.md` — version and validation record

## Boundaries

- No search, no scoring, no legal or financial opinion produced by this skill itself.
- Not a substitute for docketing software or prosecution-tracking.
- Every legal-adjacent statement in outputs carries a "not legal advice" disclaimer.
```

- [ ] **Step 2: Verify frontmatter and relative paths**

Run:
```bash
head -3 invention-evaluation-engine/SKILL.md
for p in skills/skill-01-invention-evaluation-overview/SKILL.md skills/skill-09-compile-report/SKILL.md docs/GLOSSARY.md docs/INDEX.md docs/DIGEST.md docs/PIPELINE_STATE.md examples/tesla-us433700/report-tesla-us433700-e2e-v15.md; do test -f "invention-evaluation-engine/$p" && echo "OK $p" || echo "MISSING $p"; done
```
Expected: frontmatter shows `name:` and `description:`; every referenced path prints `OK`.

---

### Task 3: Write the Tesla sample submission and quickstart prompt

**Files:**
- Create: `invention-evaluation-engine/examples/tesla-us433700/submission.md`
- Create: `invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md`

**Interfaces:**
- Consumes: `Test-report-results/report-tesla-us433700-e2e-v15.md` (source of invention facts).
- Produces: the sample input + invocation prompt that README (Task 6) and verify.sh (Task 5) reference.

- [ ] **Step 1: Read the reference report to extract invention facts**

Run: `sed -n '1,120p' Test-report-results/report-tesla-us433700-e2e-v15.md`
Extract: invention title, inventor, filing/grant dates, the technical description (mechanical electrical transmission of power; alternating-current motor; interposed iron-wire shield between coil and core as a phase-retardation mechanism), the innovation claims, and any proof-of-concept / IP-posture / disclosure-history statements the report records.

- [ ] **Step 2: Write submission.md**

Write `invention-evaluation-engine/examples/tesla-us433700/submission.md` with this structure (facts filled from Step 1; mark anything the report does not record as "Not recorded" — do not invent):

```markdown
# Invention Submission — Sample Case

> This is the sample input for the quickstart run. It mirrors the fields
> `skill-02-gather-invention-submission` captures. Facts are drawn from the
> validated v1.5 report (`report-tesla-us433700-e2e-v15.md`).

## 1. Inventor and date
- Inventor: [from report]
- Submission date: [today's date]
- Earliest filing date (if known): [from report]

## 2. Title and field
- Title: [from report]
- Technical field: [from report]

## 3. Description of the invention
[Plain-language description extracted from the report: what it is, how it works,
the interposed-shield mechanism, and what it achieves.]

## 4. Background / problem being solved
[From report: the problem with prior alternating-current motor phase control.]

## 5. Innovation claims
- [Claim 1…n as the report states them, including the interposed iron-wire shield limitation.]

## 6. Proof-of-concept status
[From report, or "Not recorded".]

## 7. IP posture
- Patents filed / granted: [from report]
- Assignee: [from report]

## 8. Public disclosure / sale-offer history
- Public disclosure date: [from report, or "None recorded"]
- Sale offer date: [from report, or "None recorded"]
```

- [ ] **Step 3: Write quickstart-prompt.md**

Write `invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md` with exactly this content:

```markdown
# Quickstart prompt

After installing the skill, copy-paste this into your agent tool:

---

Evaluate this invention using the invention-evaluation-engine skill.

The invention submission is in the file `examples/tesla-us433700/submission.md`
inside the installed `invention-evaluation-engine` skill folder. Read it, then
run the complete nine-phase pipeline and produce the final report.

---

When the run finishes, compare the output with
`examples/tesla-us433700/report-tesla-us433700-e2e-v15.md` (the validated
reference report). The pipeline performs live web searches, so the run takes
several minutes and needs network access.
```

- [ ] **Step 4: Verify both files exist and are non-empty**

Run: `wc -l invention-evaluation-engine/examples/tesla-us433700/submission.md invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md`
Expected: both files present, submission.md ≥ 20 lines, quickstart-prompt.md ≥ 10 lines.

---

### Task 4: Write install.sh

**Files:**
- Create: `install.sh` (project root, executable)

**Interfaces:**
- Consumes: `invention-evaluation-engine/` folder (Tasks 1–3).
- Produces: `install.sh` — the one-command installer that Task 7 executes and README documents.

- [ ] **Step 1: Write install.sh**

Write `install.sh` with exactly this content, then `chmod +x install.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Invention Evaluation Engine — installer
# Usage:
#   ./install.sh                          # auto-detect target tool
#   ./install.sh --tool claude            # force Claude Code
#   ./install.sh --tool opencode          # force OpenCode
#   ./install.sh --tool copilot           # install into .github/skills/ (run from project root)
#   ./install.sh --tool custom --path /some/dir
#   ./install.sh --force                  # overwrite existing install without backup prompt

PKG_DIR="invention-evaluation-engine"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/$PKG_DIR"

detect_tool() {
  if [ -d "$HOME/.claude/skills" ]; then echo "claude"; return 0; fi
  if [ -d "$HOME/.opencode/skills" ]; then echo "opencode"; return 0; fi
  echo "unknown"
}

TOOL=""
PATH_ARG=""
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --path) PATH_ARG="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [ -z "$TOOL" ]; then
  TOOL="$(detect_tool)"
fi

case "$TOOL" in
  claude)   DEST="$HOME/.claude/skills" ;;
  opencode) DEST="$HOME/.opencode/skills" ;;
  copilot)  DEST="$(pwd)/.github/skills" ;;
  custom)   DEST="${PATH_ARG:?--path is required with --tool custom}" ;;
  unknown)  echo "No supported tool detected. Use --tool claude|opencode|copilot|custom (with --path)." >&2; exit 1 ;;
  *) echo "Unknown tool: $TOOL (expected claude|opencode|copilot|custom)" >&2; exit 1 ;;
esac

if [ ! -d "$SRC" ]; then
  echo "ERROR: $SRC not found. Run this script from the package root." >&2
  exit 1
fi

mkdir -p "$DEST"
TARGET="$DEST/$PKG_DIR"

if [ -d "$TARGET" ]; then
  if [ "$FORCE" -eq 1 ]; then
    rm -rf "$TARGET"
    echo "Removed existing install at $TARGET (--force)."
  else
    BAK="$TARGET.bak-$(date +%Y%m%d-%H%M%S)"
    mv "$TARGET" "$BAK"
    echo "Existing install backed up to $BAK"
  fi
fi

cp -R "$SRC" "$TARGET"
echo ""
echo "Installed invention-evaluation-engine to: $TARGET"
echo ""
echo "Next steps:"
echo "  1. Restart your agent tool (or reload skills)."
echo "  2. Run the sample: paste the prompt from"
echo "     $PKG_DIR/examples/tesla-us433700/quickstart-prompt.md"
echo "  3. Compare the output with"
echo "     $PKG_DIR/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md"
```

- [ ] **Step 2: Syntax-check and dry-run the help path**

Run: `bash -n install.sh && ./install.sh --tool bogus 2>&1; echo "exit=$?"`
Expected: `bash -n` silent; `--tool bogus` prints `Unknown tool: bogus (expected claude|opencode|copilot|custom)` and exits 1.

---

### Task 5: Write verify.sh

**Files:**
- Create: `verify.sh` (project root, executable)

**Interfaces:**
- Consumes: an installed `invention-evaluation-engine/` tree (default: the one in the package root).
- Produces: `verify.sh` — the static install checker that Tasks 7–8 run and README documents.

- [ ] **Step 1: Write verify.sh**

Write `verify.sh` with exactly this content, then `chmod +x verify.sh`:

```bash
#!/usr/bin/env bash
set -uo pipefail

# Invention Evaluation Engine — install verifier
# Usage: ./verify.sh [--path /path/to/invention-evaluation-engine]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$SCRIPT_DIR/invention-evaluation-engine"

if [ "${1:-}" = "--path" ]; then
  TARGET="${2:?--path requires a directory argument}"
fi

FAIL=0
check() {
  local desc="$1" file="$2"
  if [ -f "$file" ]; then
    echo "  [PASS] $desc"
  else
    echo "  [FAIL] $desc — missing: $file"
    FAIL=1
  fi
}

echo "Verifying invention-evaluation-engine at: $TARGET"
echo ""

check "engine SKILL.md" "$TARGET/SKILL.md"
check "sub-skill 01" "$TARGET/skills/skill-01-invention-evaluation-overview/SKILL.md"
check "sub-skill 02" "$TARGET/skills/skill-02-gather-invention-submission/SKILL.md"
check "sub-skill 03" "$TARGET/skills/skill-03-analyze-technology-fundamentals/SKILL.md"
check "sub-skill 04" "$TARGET/skills/skill-04-conduct-patent-landscape/SKILL.md"
check "sub-skill 05" "$TARGET/skills/skill-05-conduct-novelty-search/SKILL.md"
check "sub-skill 06" "$TARGET/skills/skill-06-conduct-literature-search/SKILL.md"
check "sub-skill 07" "$TARGET/skills/skill-07-analyze-market-opportunity/SKILL.md"
check "sub-skill 08" "$TARGET/skills/skill-08-identify-partners/SKILL.md"
check "sub-skill 09" "$TARGET/skills/skill-09-compile-report/SKILL.md"
check "docs/DIGEST.md" "$TARGET/docs/DIGEST.md"
check "docs/GLOSSARY.md" "$TARGET/docs/GLOSSARY.md"
check "docs/INDEX.md" "$TARGET/docs/INDEX.md"
check "docs/PIPELINE_STATE.md" "$TARGET/docs/PIPELINE_STATE.md"
check "example submission" "$TARGET/examples/tesla-us433700/submission.md"
check "example quickstart prompt" "$TARGET/examples/tesla-us433700/quickstart-prompt.md"
check "example report" "$TARGET/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md"

for f in "$TARGET/SKILL.md" "$TARGET"/skills/skill-*/SKILL.md; do
  if [ -f "$f" ]; then
    if ! grep -q '^name:' "$f" || ! grep -q '^description:' "$f"; then
      echo "  [FAIL] frontmatter missing name/description in $f"
      FAIL=1
    fi
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  echo ""
  echo "Quickstart: paste the prompt from"
  echo "  $TARGET/examples/tesla-us433700/quickstart-prompt.md"
  exit 0
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
```

- [ ] **Step 2: Syntax-check and run against the package**

Run: `bash -n verify.sh && ./verify.sh`
Expected: `bash -n` silent; every line prints `[PASS]`; final line `ALL CHECKS PASSED`; exit 0.

---

### Task 6: Write README.md and LICENSE

**Files:**
- Create: `README.md` (project root)
- Create: `LICENSE` (project root)

**Interfaces:**
- Consumes: everything from Tasks 1–5 (structure, prompts, script usage).
- Produces: the onboarding docs that ship in the zip.

- [ ] **Step 1: Write README.md**

Write `README.md` with exactly this content:

```markdown
# Invention Evaluation Engine

An evidence-constrained invention reasoning engine: a nine-phase pipeline that
takes an invention submission and produces a structured evaluation report —
technology profile, patent landscape, novelty search, literature search, market
opportunity, partner identification, and a compiled final report. Every finding
carries an explicit evidence grade; nothing downstream may promote an inference
into a fact.

Pipeline: Submission → Technology Profile → Patent Landscape → Novelty Search →
Literature Search → Market Opportunity → Partners → Report.

## Requirements

- An agent tool that can read files and search the web (Claude Code, OpenCode,
  GitHub Copilot, or any LLM agent — the skills are plain markdown).
- Network access (the pipeline performs live searches).
- macOS, Linux, or Windows with Git Bash / WSL.
- About 5 minutes to install; the sample run takes several minutes.

## Install

Unzip the archive, then from the `invention-evaluation-framework/` folder run:

```bash
./install.sh
```

The installer auto-detects your tool (Claude Code → `~/.claude/skills/`,
OpenCode → `~/.opencode/skills/`). To force a target:

```bash
./install.sh --tool claude      # Claude Code
./install.sh --tool opencode    # OpenCode
./install.sh --tool copilot     # GitHub Copilot (installs to .github/skills/ in the current project)
./install.sh --tool custom --path /any/dir
```

An existing install is backed up automatically (timestamped `.bak`); use
`--force` to overwrite without a backup. Then restart your agent tool (or
reload skills).

## Verify

```bash
./verify.sh
```

Prints PASS/FAIL for the engine skill, all 9 sub-skills, docs, and the sample
case. Exit code 0 = all good.

## Quickstart — sample run

1. Paste the prompt from
   `invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md`
   into your agent tool.
2. The engine runs the full pipeline on the Tesla US433,700 sample submission
   (live searches — this takes several minutes).
3. Compare the output with
   `invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md`
   (the validated reference report).

## Running on your own invention

Say "evaluate this invention" and describe it, or paste a disclosure. The engine
captures a structured submission first (disclosure/sale-offer dates are
mandatory at intake), then runs the pipeline. For a single analysis (market
only, novelty only), the engine routes to the relevant sub-skill directly.

## Configuration

None. Network access is the only prerequisite. The pipeline's searches use
public sources (e.g., Google Patents, web literature).

## Troubleshooting

| Problem | Fix |
|---|---|
| "No supported tool detected" | Use `--tool` explicitly, or `--tool custom --path <dir>` |
| "Existing install backed up" unexpectedly | Expected — re-run with `--force` to skip the backup |
| Windows | Use Git Bash or WSL; run `bash install.sh` if needed |
| FTO / "can I sell this?" questions | The engine redirects these: FTO requires a separate search and counsel — it is not a novelty search |
| Sample run produces no report | Check network access; the pipeline reports NOT EVALUATED rather than guessing |
| Copilot doesn't pick up the skill | Copilot reads skills from `.github/skills/` in your project; alternatively point the agent at `invention-evaluation-engine/SKILL.md` directly, or paste its contents |

## License

MIT — see `LICENSE`.

## Structure

```
invention-evaluation-engine/   ← the installed skill
├── SKILL.md                   ← engine entry point (orchestration)
├── skills/                    ← the 9 sub-skills
├── docs/                      ← DIGEST, GLOSSARY, INDEX, PIPELINE_STATE
└── examples/tesla-us433700/   ← sample submission, prompt, reference report
install.sh                     ← one-command installer
verify.sh                      ← install checker
README.md                      ← this file
LICENSE                        ← MIT
```
```

- [ ] **Step 2: Write LICENSE**

Write `LICENSE` with exactly this content:

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Verify both files exist**

Run: `test -s README.md && test -s LICENSE && echo OK`
Expected: `OK`.

---

### Task 7: Sandbox install + verify test

**Files:**
- Test only — no new files in the package.

**Interfaces:**
- Consumes: `install.sh`, `verify.sh`, `invention-evaluation-engine/` from Tasks 1–6.
- Produces: proof that a clean install works (spec §Testing item 1).

- [ ] **Step 1: Install into a sandbox**

Run:
```bash
rm -rf /tmp/opencode/pkgtest && mkdir -p /tmp/opencode/pkgtest
./install.sh --tool custom --path /tmp/opencode/pkgtest/install
```
Expected: prints `Installed invention-evaluation-engine to: /tmp/opencode/pkgtest/install/invention-evaluation-engine`.

- [ ] **Step 2: Verify the sandbox install**

Run: `./verify.sh --path /tmp/opencode/pkgtest/install/invention-evaluation-engine`
Expected: `ALL CHECKS PASSED`, exit 0.

- [ ] **Step 3: Test the backup path**

Run:
```bash
./install.sh --tool custom --path /tmp/opencode/pkgtest/install
ls /tmp/opencode/pkgtest/install/
```
Expected: second install prints `Existing install backed up to ...bak-<timestamp>`; the directory contains `invention-evaluation-engine/` and one `invention-evaluation-engine.bak-*`.

- [ ] **Step 4: Test --force**

Run:
```bash
./install.sh --tool custom --path /tmp/opencode/pkgtest/install --force
ls /tmp/opencode/pkgtest/install/
```
Expected: prints `Removed existing install ... (--force)`; only `invention-evaluation-engine/` remains (no `.bak`).

---

### Task 8: Build the zip and re-verify from the unpacked tree

**Files:**
- Create: `/home/forsythe/Downloads/invention-evaluation-framework.zip` (replaces the stale Aug-13 zip)

**Interfaces:**
- Consumes: the complete package root (Tasks 1–6).
- Produces: the deliverable archive (spec §Testing items 2–3).

- [ ] **Step 1: Build the zip**

Run:
```bash
cd /home/forsythe/Downloads
rm -f invention-evaluation-framework.zip
zip -r invention-evaluation-framework.zip invention-evaluation-framework -x "invention-evaluation-framework/invention-evaluation-framework.zip"
```
Expected: zip created; archive root is `invention-evaluation-framework/`; no nested zip inside.

- [ ] **Step 2: Unpack into a fresh sandbox**

Run:
```bash
rm -rf /tmp/opencode/pkgtest/unpacked && mkdir -p /tmp/opencode/pkgtest/unpacked
cd /tmp/opencode/pkgtest/unpacked && unzip -q /home/forsythe/Downloads/invention-evaluation-framework.zip
```

- [ ] **Step 3: Install + verify from the unpacked tree**

Run:
```bash
cd /tmp/opencode/pkgtest/unpacked/invention-evaluation-framework
./install.sh --tool custom --path /tmp/opencode/pkgtest/unpacked/install
./verify.sh --path /tmp/opencode/pkgtest/unpacked/install/invention-evaluation-engine
```
Expected: install succeeds; `ALL CHECKS PASSED`, exit 0.

- [ ] **Step 4: Confirm the engine's relative paths resolve in the installed tree**

Run:
```bash
cd /tmp/opencode/pkgtest/unpacked/install/invention-evaluation-engine
for p in skills/skill-01-invention-evaluation-overview/SKILL.md skills/skill-09-compile-report/SKILL.md docs/GLOSSARY.md docs/INDEX.md docs/DIGEST.md docs/PIPELINE_STATE.md examples/tesla-us433700/submission.md examples/tesla-us433700/quickstart-prompt.md examples/tesla-us433700/report-tesla-us433700-e2e-v15.md; do test -f "$p" && echo "OK $p" || echo "MISSING $p"; done
```
Expected: every path prints `OK`.

---

### Task 9: Final integrity checks

**Files:**
- None (verification only).

**Interfaces:**
- Consumes: source framework + packaged tree + zip.
- Produces: the final deliverable confirmation (spec §Testing item 4).

- [ ] **Step 1: Byte-identity of all 9 sub-skills and docs**

Run:
```bash
for d in skill-01-invention-evaluation-overview skill-02-gather-invention-submission skill-03-analyze-technology-fundamentals skill-04-conduct-patent-landscape skill-05-conduct-novelty-search skill-06-conduct-literature-search skill-07-analyze-market-opportunity skill-08-identify-partners skill-09-compile-report; do
  diff -r "$d" "invention-evaluation-engine/skills/$d" >/dev/null && echo "IDENTICAL $d" || echo "DRIFT $d"
done
for f in DIGEST.md GLOSSARY.md INDEX.md PIPELINE_STATE.md; do
  diff "$f" "invention-evaluation-engine/docs/$f" >/dev/null && echo "IDENTICAL $f" || echo "DRIFT $f"
done
```
Expected: all lines print `IDENTICAL`.

- [ ] **Step 2: Confirm the deliverable**

Run: `ls -la /home/forsythe/Downloads/invention-evaluation-framework.zip && unzip -l /home/forsythe/Downloads/invention-evaluation-framework.zip | tail -3`
Expected: zip exists with a recent timestamp; listing ends with `install.sh`, `verify.sh`, `README.md`, `LICENSE` entries.

- [ ] **Step 3: Report to the user**

Summarize: deliverable path, what's inside, install/verify commands, quickstart prompt location, and the sandbox test results.