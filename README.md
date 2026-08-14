# Invention Evaluation Engine

An evidence-constrained invention reasoning engine: a nine-phase pipeline that
takes an invention submission and produces a structured evaluation report —
technology profile, patent landscape, novelty search, literature search, market
opportunity, partner identification, and a compiled final report. Every finding
carries an explicit evidence grade; nothing downstream may promote an inference
into a fact. v1.6 enforces an evidence-sufficiency architecture: propositions
enter the report only through the Evidence Sufficiency Gate, searches escalate
through deterministic avenue checklists, and unestablished propositions are
excluded from factual findings (see
`docs/superpowers/specs/2026-08-14-invention-evaluation-framework-v16-design.md`).

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
./install.shs
```

(Or point your model at this directory and tell it to install and configure to your .config/.skills directory 


The installer auto-detects your tool (Claude Code → `~/.claude/skills/`,
OpenCode → `~/.opencode/skills/`). To force a target:

```bash
./install.sh --tool ruclaude      # Claude Code
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