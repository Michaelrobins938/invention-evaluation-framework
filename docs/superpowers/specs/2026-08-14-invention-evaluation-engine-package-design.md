# Design Spec — Invention Evaluation Engine: Distributable Package

**Date:** 2026-08-14
**Status:** Approved (brainstorming complete; all design sections approved 2026-08-14)
**Relates to:** invention-evaluation-framework v1.5 (see `docs/superpowers/specs/2026-08-14-invention-evaluation-framework-v15-design.md`)

## Goal

Package the Invention Evaluation Framework v1.5 so a colleague can download one archive, run one install command, and run the full nine-skill pipeline end-to-end on a sample invention. The framework's content (skills, glossary, digest, index, pipeline state) ships unchanged in substance; this spec is purely about **distribution, installation, invocation, and onboarding**.

## Locked decisions (from brainstorming)

| Decision | Choice |
|---|---|
| Delivery format | Zip archive (one download) |
| Install mechanism | One-command `install.sh` |
| Target tools | Claude Code, OpenCode, Copilot, custom path — detected or overridden |
| Model-agnostic | Engine + sub-skills are plain markdown file references; work with any LLM agent |
| Installable unit | Single folder `invention-evaluation-engine/` |
| Engine/sub-skill relationship | Engine bundles the 9 sub-skills under `skills/`; engine SKILL.md references them by relative path |
| Sample run | Include Tesla US433,700: input submission + copy-paste prompt + validated expected report |
| Configuration | None required; network access is the only prerequisite |
| License | MIT (proposal, confirmed in design review) |

## Package structure

```
invention-evaluation-engine/              ← single installable unit
├── SKILL.md                              ← engine (entry point + orchestration)
├── skills/                               ← the 9 sub-skills, bundled
│   ├── skill-01-invention-evaluation-overview/SKILL.md
│   ├── skill-02-gather-invention-submission/SKILL.md
│   ├── skill-03-analyze-technology-fundamentals/SKILL.md
│   ├── skill-04-conduct-patent-landscape/SKILL.md
│   ├── skill-05-conduct-novelty-search/SKILL.md
│   ├── skill-06-conduct-literature-search/SKILL.md
│   ├── skill-07-analyze-market-opportunity/SKILL.md
│   ├── skill-08-identify-partners/SKILL.md
│   └── skill-09-compile-report/SKILL.md
├── docs/
│   ├── DIGEST.md
│   ├── GLOSSARY.md
│   ├── INDEX.md
│   └── PIPELINE_STATE.md
└── examples/
    └── tesla-us433700/
        ├── submission.md
        ├── quickstart-prompt.md
        └── report-tesla-us433700-e2e-v15.md

install.sh
verify.sh
README.md
LICENSE
```

## Components

### 1. Engine SKILL.md

New file at `invention-evaluation-engine/SKILL.md`.

- **Frontmatter:** `name: invention-evaluation-engine`; `description` triggering on "evaluate this invention", "run the full invention evaluation pipeline", "start a commercial/patentability assessment", etc.
- **Body sections:**
  - What this is: the orchestration layer of the evidence-constrained invention reasoning engine (delegates to the sub-skills; does not perform search or analysis itself).
  - When to use / When NOT to use (FTO / infringement questions redirect — see GLOSSARY, do not run the novelty pipeline as a substitute).
  - Execution:
    1. Determine whether a structured submission record exists. If none, read and execute `skills/skill-02-gather-invention-submission/SKILL.md`.
    2. Execute sub-skills in dependency order per `docs/INDEX.md`, reading each `skills/skill-XX-*/SKILL.md` when its phase is reached.
    3. Preserve evidence grades (CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED) and coverage objects at every hand-off — never upgrade or strip them.
    4. Maintain a phase-completion checklist with explicit `blocked / needs-input` states.
    5. Compile the final report via `skills/skill-09-compile-report/SKILL.md`.
  - References to `docs/GLOSSARY.md`, `docs/INDEX.md`, `docs/DIGEST.md` by relative path.
  - Boundaries: no search, scoring, or legal/financial opinion produced by the engine itself; not a docketing system.

### 2. install.sh

Bash, POSIX-friendly, runs on macOS/Linux; Windows via Git Bash or WSL.

- **Tool detection (no args):** target `~/.claude/skills/` if it exists → Claude Code; `~/.opencode/skills/` if it exists → OpenCode; otherwise prompt interactively or require `--tool`.
- **Flags:**
  - `--tool claude|opencode|copilot|custom`
  - `--path <dir>` (custom target; used with `--tool custom` or alone)
  - `--force` (overwrite without prompting)
- **Behavior:** create target dir if missing; if `invention-evaluation-engine/` already exists at target, back it up to `invention-evaluation-engine.bak-<timestamp>` (unless `--force`); copy the folder; print next steps including the quickstart prompt.
- **Copilot note:** installs to `.github/skills/` in the colleague's project when `--tool copilot` is chosen; README documents the AGENTS.md fallback for models/tools without skill registration.

### 3. verify.sh

Bash, read-only.

- Checks: engine SKILL.md present; all 9 `skills/skill-XX-*/SKILL.md` present; `docs/` files present (DIGEST, GLOSSARY, INDEX, PIPELINE_STATE); `examples/tesla-us433700/` present (submission, quickstart-prompt, report); frontmatter `name:` and `description:` present in engine and each sub-skill.
- Prints a PASS/FAIL summary and exits non-zero on any failure.
- Prints the quickstart prompt on success.

### 4. README.md

Sections: What this is (one paragraph + pipeline line) · Requirements (an agent tool, network access, ~5 min) · Install (per tool) · Verify · Quickstart (paste prompt → report → compare with expected output) · Running on your own invention · Configuration (none needed; network only) · Troubleshooting (tool not detected, already installed, Windows/Git Bash, FTO questions) · License (MIT) · Structure map.

### 5. LICENSE

MIT, standard text, `Copyright (c) 2026`.

### 6. examples/tesla-us433700/

- `submission.md` — a structured invention submission record for Tesla US433,700 (mechanical electrical transmission of power; interposed iron-wire shield), built from the validated v1.5 report. Serves as the sample input.
- `quickstart-prompt.md` — the exact copy-paste prompt that invokes the engine with the submission.
- `report-tesla-us433700-e2e-v15.md` — copy of the existing validated output, the reference for comparison.

## Data flow

Colleague pastes quickstart prompt (or says "evaluate this invention") → agent loads `invention-evaluation-engine` → engine reads sub-skills from `skills/` in dependency order → sub-skills perform live searches (Google Patents fetches, web literature) → outputs flow forward with evidence grades intact → skill-09 compiles the report → colleague compares with the expected reference.

## Error handling

- **Install:** tool not detected → interactive prompt or `--tool`; target exists → timestamped backup (unless `--force`); missing target dir → created.
- **Pipeline:** engine carries forward `blocked / needs-input` states (existing sub-skill behavior); FTO requests redirected per existing framework rules; no network → searches produce NOT EVALUATED / coverage-gap findings per existing evidence discipline (never guesses).

## Testing / validation

1. Run `install.sh` + `verify.sh` in a temp sandbox (e.g., `/tmp/opencode/pkgtest`) targeting a custom path; assert PASS.
2. Build the zip; unpack it into a second sandbox; re-run install + verify from the unpacked tree; assert PASS.
3. Assert every relative path in the engine SKILL.md resolves against the installed tree.
4. Confirm the 9 sub-skills are byte-identical to the source framework (no content drift during packaging).

## Files to create (new) / copy (existing)

| File | Action |
|---|---|
| `invention-evaluation-engine/SKILL.md` | New |
| `invention-evaluation-engine/skills/skill-01…09/SKILL.md` | Copy from source (byte-identical) |
| `invention-evaluation-engine/docs/{DIGEST,GLOSSARY,INDEX,PIPELINE_STATE}.md` | Copy from source |
| `invention-evaluation-engine/examples/tesla-us433700/submission.md` | New (derived from report) |
| `invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md` | New |
| `invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md` | Copy from `Test-report-results/` |
| `install.sh` | New |
| `verify.sh` | New |
| `README.md` | New |
| `LICENSE` | New (MIT) |
| `invention-evaluation-framework.zip` | Built archive (the deliverable) |

## Out of scope

- Automated end-to-end test harness invoking agent CLIs (Approach 3, deferred).
- Changes to framework content (v1.5 is frozen for this packaging).
- Git repository setup (delivery is a zip per decision).
