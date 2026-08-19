---
name: invention-evaluation-engine
description: One-skill entry point for the full ten-phase invention evaluation pipeline (submission capture, technology profile, patent landscape, novelty search, literature search, market opportunity, partner identification, report compilation, styled report rendering). Use when the user asks to evaluate an invention, run the full evaluation pipeline, or start a patentability/commercial assessment. Delegates to the bundled sub-skills in skills/ and enforces evidence-grade preservation across hand-offs. Not for FTO/infringement questions — redirect those to counsel.
---

# Invention Evaluation Engine

## What this is

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

The orchestration layer of an **evidence-constrained invention reasoning engine**. This skill does not perform search or analysis itself — it routes through the ten sub-skills bundled in `skills/` and enforces the framework's governing rule at every hand-off: **nothing downstream may promote an inference into a fact.** Every proposition carries a stable `proposition_id` + `proposition_version` and the evidence state it was established with (see `docs/GLOSSARY.md` — Epistemic Architecture). Nothing enters the final report except through the Evidence Sufficiency Gate.

## When to use
- "Evaluate this invention" / "run the full evaluation pipeline"
- "Is my invention patentable and commercially viable?"
- "Start a full commercial + patentability assessment"

## When NOT to use — redirect instead
- FTO / infringement ("can I sell this without being sued?") — stop and explain the novelty-vs-FTO distinction (see `docs/GLOSSARY.md`); scope it as a separate engagement with counsel. Do not run the novelty pipeline as a substitute.
- A single specific analysis (market only, novelty only) — route directly to the relevant sub-skill instead of the full pipeline.

## Execution

0. **Artifact destination gate — mandatory before analysis.** Resolve the output
   directory before running any phase. For this framework, the default destination
   is the repository's `evaluations/<normalized-invention-id>/` directory. If the
   user names a folder (for example `Desktop/tools/...`), that path takes
   precedence. Create the run directory only after verifying its parent exists.
   The run is not complete until the compiled Markdown report, submission record,
   proposition ledger, avenue ledger, scores manifest, and (for a full run) styled
   HTML/PDF are physically present in that directory. A chat response is not a
   deliverable and must never be treated as a substitute for saved artifacts.

   Before claiming completion, run a filesystem existence check against every
   required artifact and report the absolute paths. If the destination cannot be
   resolved or written, stop with `BLOCKED: artifact_destination` rather than
   continuing and presenting an unsaved report.

1. **Submission record.** Determine whether a structured submission record exists (user-provided, or `examples/tesla-us433700/submission.md` for the sample run).
   - If none: read `skills/skill-02-gather-invention-submission/SKILL.md` and execute it to capture one. Disclosure and sale-offer dates are mandatory at intake — always capture, even a confirmed "none."
2. **Dependency order.** Execute sub-skills in dependency order per `docs/INDEX.md`, reading each `skills/skill-XX-*/SKILL.md` when its phase is reached:
   - 01 overview → 02 gather-submission → 03 technology-fundamentals → 04 patent-landscape → 05 novelty-search → 06 literature-search → 07 market-opportunity → 08 identify-partners → 09 compile-report → 10 render-report
   - Hard dependencies must be satisfied before a phase runs; soft dependencies may be bypassed with degraded capability, noted in the final report.
3. **Evidence-grade preservation.** At every hand-off, carry each proposition with its `proposition_id`, `proposition_version`, and evidence state (CONFIRMED PRESENT / CONFIRMED ABSENT) plus its avenue records. Never upgrade, strip, or re-scope a proposition at hand-off; any refinement requires a version increment. Unestablished propositions remain in the work queue with their search records.
4. **Phase checklist.** Maintain a phase-completion checklist with explicit `blocked / needs-input` states. If a phase is blocked, say so — do not guess.
5. **Report.** Compile the final report via `skills/skill-09-compile-report/SKILL.md`, including the reproducible query log and the "not legal advice" disclaimers.
6. **Save and verify.** Write every phase artifact to the resolved run directory,
   run the renderer, then verify file existence, non-zero size, and path parity.
   The final response must include a delivery manifest with absolute paths and
   must distinguish `SAVED`, `BLOCKED`, and `NOT RUN`; never imply that prose in
   the response was saved when it was not.

7. **Source extraction completeness gate.** Opening or fetching a source is not
   evidence that its contents were processed. For every source page, extract all
   decision-relevant structured sections before moving on: citations (including
   examiner/third-party markers), forward citations, family members and each
   member's status, assignments/rights events, prosecution metadata, and the
   source's own disclaimers. A source may not generate an `ESCALATION_REQUIRED`
   item for information visible on the already-open source until the relevant
   table or section has been parsed and dispositioned.

8. **Bidirectional evidence-flow gate.** New facts discovered in any later phase
   must trigger an impact review of earlier outputs. Ownership changes must
   update assignee charts and rights conclusions; family members must receive
   individual status checks; business-failure evidence must update market and
   commercialization analysis; newly recovered prior art must update novelty
   mappings. Record the backward edges in the avenue ledger.

9. **Internal-consistency gate.** Before compilation, compare every narrative
   query, chart footnote, source locator, date range, classification code, and
   denominator. A mismatch blocks delivery until reconciled. Never present a
   precise count when its query is blocked, its source is unavailable, or its
   footnote describes a different query.

10. **Temporal-normalization gate.** Normalize filing counts by the duration of
    each time bucket. A partial final bucket cannot be interpreted as a trend
    without an explicit normalization or a `PARTIAL_BUCKET` label. Truncated or
    incomplete data must not feed a market score, threat, or conclusion.

11. **Escalation-closure gate.** An escalation item is a work instruction, not a
    deliverable. If the requested classification, business-history check, family
    status check, or bounded model can be answered from public sources already
    within the run's scope, execute it before compiling. If it cannot be answered,
    record the exact blocker, attempted avenues, and decision impact. Do not ship
    scaffolding formulas or generic queues as if they were completed analysis.
6. **Styled deliverable (mandatory, every run).** Render the compiled report into the branded "inventionevaluator" format via `skills/skill-10-render-report/SKILL.md` using `invention-evaluation-engine/report-renderer/render_report.py`. The styled HTML + A4 PDF (clean cover, TOC with accurate physical page numbers, running footer, watermark, gauges, SWOT, section dividers, search boxes) IS the final deliverable of every end-to-end run — not an optional extra. The renderer never invents metrics: all gauge/bar values come from the per-run scores manifest, each with a basis proposition_id; charts without established data render labeled placeholder frames.

## Reference docs (relative to this skill's folder)

- `docs/DIGEST.md` — 5-minute read; the non-negotiables
- `docs/GLOSSARY.md` — full terminology, three-layer epistemic architecture, sufficiency gate, escalation protocol, schema registry
- `docs/INDEX.md` — dependency graph, entry points, dependency types
- `docs/PIPELINE_STATE.md` — version and validation record

## v1.7 Evidence Recovery Controller

Unresolved propositions are workflow states, not stopping points. Classify missingness,
calculate evidence leverage, select a phase-specific recovery policy, execute its
escalation ladder, attach a research exhaustion proof, and propagate resulting
constraints before compiling conclusions. Active states are `ESCALATION_REQUIRED`,
`SEARCH_EXHAUSTED`, and `BLOCKED`; legacy `EXHAUSTED` requires migration review.
No downstream conclusion or recommendation may be stronger than its weakest unresolved
material dependency.

## Boundaries

- No search, no scoring, no legal or financial opinion produced by this skill itself.
- Not a substitute for docketing software or prosecution-tracking.
- Every legal-adjacent statement in outputs carries a "not legal advice" disclaimer.
