---
name: conduct-literature-search
description: Searches academic and technical literature to capture non-patent prior art, technical background, and state-of-the-art benchmarks relevant to an invention. Use whenever the user wants academic papers on a topic, wants to know the state of research, or when a novelty assessment needs non-patent prior art coverage in addition to conduct-novelty-search's patent-only results. Do not use for patent-specific prior art searches — that's conduct-novelty-search.
---

# Conduct Literature Search

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- "Find papers on X."
- "What's the state of research on Y?"
- Complementing a novelty search with non-patent prior art.

## When NOT to use
- The question is specifically about patents — use `conduct-novelty-search`.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

1. Derive search terms from the idea description produced by `analyze-technology-fundamentals`, plus modifiers for adjacent technical approaches.
2. Run 3–5 queries spanning broad-field and specific-mechanism searches.
3. **Abstract triage, 30–90 seconds per paper:** title → abstract first sentence → abstract last sentence → keywords if still uncertain. Classify as Irrelevant / Background / Supporting / Potentially Conflicting / Prior Art Risk.
4. For flagged items, capture the full `literature_disclosure` schema from GLOSSARY.md: authors, title, venue, date, DOI/report number, URL, experimental system, cooling/technology, application, what was actually demonstrated, and a relevance note stating specifically which element of the invention it touches. A row without publication identity (authors, title, venue, date, DOI) does not exist. A generic "seems related" note is not usable downstream.
5. Treat any dated non-patent disclosure (conference talk, preprint, thesis) with the same rigor as a patent reference for prior-art and filing-deadline purposes.
6. Summarize the literature landscape in terms the patentability opinion can use directly — e.g., state plainly if a combination the invention relies on for novelty is already independently reported in the literature.
7. **Evidence-state discipline (v1.6).** Evidence layer: CONFIRMED PRESENT / CONFIRMED ABSENT only. Work layer: SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED (avenue) / EXHAUSTED (proposition). A search that returns nothing is avenue metadata, not evidence. CONFIRMED ABSENT requires a bounded universe + absence_basis. See GLOSSARY.md — Epistemic Architecture.
8. **Negative literature findings go through the escalation protocol.** If a proposition (e.g., "no pre-filing publication discloses the claimed mechanism") is not established, run the skill's avenue checklist (A1 primary source search → A2 classification search → A3 citation expansion → A4 terminology expansion → A5 alternate database → A6 organizational records → A7 jurisdiction-specific sources → A8 independent corroboration), logging each avenue_record. Only when every required avenue is dispositioned may the proposition be marked EXHAUSTED — and EXHAUSTED is not evidence: the proposition is excluded from factual findings and recorded in the Operational Audit with barrier_type. State the databases and date ranges actually searched in each avenue record (e.g., "IEEE Xplore 1880–1900, Google Scholar full range, domain: electrical engineering history").
9. **Known principle ≠ obvious application.** If the literature confirms a background principle (e.g., "magnetic saturation was known") but does not disclose the specific engineering application (e.g., "an interposed iron-wire shield used as a controllable phase-delay mechanism in an AC motor"), record the principle as CONFIRMED PRESENT and the application as NOT ESTABLISHED (avenue record); the application proposition escalates through the avenue checklist if it matters to a conclusion. Do not let the confirmed principle carry the application's evidentiary weight.

## Boundary

## v1.7 recovery escalation

Literature gaps trigger recovery rather than immediate termination. For implantable
medical devices, escalate from invention-specific papers to engineering validation,
hermetic packaging, feedthrough reliability, electrode degradation, inflammation,
wireless power, and long-term encapsulation literature. Search both supporting and
contradicting evidence. If a technical database or full text is unavailable, record the
query, source, result, and alternate path before assigning `SEARCH_EXHAUSTED`.
- One database (e.g., Google Scholar) is not exhaustive; supplement with domain-specific sources (PubMed, IEEE Xplore, etc.) where the field warrants it.
- If a flagged paper requires technical background beyond your domain orientation to assess, say so and flag for escalation rather than guessing at its significance.
