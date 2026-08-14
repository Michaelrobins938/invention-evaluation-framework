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
