---
name: conduct-literature-search
description: Searches academic and technical literature to capture non-patent prior art, technical background, and state-of-the-art benchmarks relevant to an invention. Use whenever the user wants academic papers on a topic, wants to know the state of research, or when a novelty assessment needs non-patent prior art coverage in addition to conduct-novelty-search's patent-only results. Do not use for patent-specific prior art searches — that's conduct-novelty-search.
---

# Conduct Literature Search

## When to use
- "Find papers on X."
- "What's the state of research on Y?"
- Complementing a novelty search with non-patent prior art.

## When NOT to use
- The question is specifically about patents — use `conduct-novelty-search`.

## Execution
1. Derive search terms from the idea description produced by `analyze-technology-fundamentals`, plus modifiers for adjacent technical approaches.
2. Run 3–5 queries spanning broad-field and specific-mechanism searches.
3. **Abstract triage, 30–90 seconds per paper:** title → abstract first sentence → abstract last sentence → keywords if still uncertain. Classify as Irrelevant / Background / Supporting / Potentially Conflicting / Prior Art Risk.
4. For flagged items, capture title, date, key finding, and a relevance note stating specifically which element of the invention it touches — a generic "seems related" note is not usable downstream.
5. Treat any dated non-patent disclosure (conference talk, preprint, thesis) with the same rigor as a patent reference for prior-art and filing-deadline purposes.
6. Summarize the literature landscape in terms the patentability opinion can use directly — e.g., state plainly if a combination the invention relies on for novelty is already independently reported in the literature.
7. **Evidence-state discipline:** Apply the ontology:
   - CONFIRMED PRESENT: Verified in source
   - CONFIRMED ABSENT: Within a defined and sufficiently complete evidence universe, the target was specifically tested for and found absent (requires bounded universe + coverage object)
   - NOT OBSERVED: Searched sources contain no instance, but coverage is insufficient to establish historical absence — **the default for negative historical claims** (requires coverage object)
   - NOT IDENTIFIED: Searched, not found (requires coverage object)
   - NOT EVALUATED: Search not performed
   - INFERRED: Derived by reasoning, not directly observed
   - CONTESTED: Sources conflict
8. **Coverage on every negative finding.** Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries a coverage object: scope, temporal scope, source domains (databases searched), search depth, completeness (LOW / MEDIUM / HIGH / EXHAUSTIVE), and known limitations. Coverage is metadata, not evidence — it never upgrades a negative state to CONFIRMED ABSENT automatically, and LOW coverage + CONFIRMED ABSENT is prohibited. State the databases and date ranges actually searched (e.g., "IEEE Xplore 1880–1900, Google Scholar full range, domain: electrical engineering history").
8. **Known principle ≠ obvious application.** If the literature confirms a background principle (e.g., "magnetic saturation was known") but does not disclose the specific engineering application (e.g., "an interposed iron-wire shield used as a controllable phase-delay mechanism in an AC motor"), record the principle as CONFIRMED PRESENT and the application as NOT OBSERVED/NOT IDENTIFIED. Do not let the confirmed principle carry the application's evidentiary weight.

## Boundary
- One database (e.g., Google Scholar) is not exhaustive; supplement with domain-specific sources (PubMed, IEEE Xplore, etc.) where the field warrants it.
- If a flagged paper requires technical background beyond your domain orientation to assess, say so and flag for escalation rather than guessing at its significance.
