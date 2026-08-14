---
name: analyze-technology-fundamentals
description: Converts a captured invention record into a technology profile — plain-language description, feature-to-benefit map, innovation assessment, regulatory burden estimate, development-stage classification, and an initial IPC/CPC classification candidate set. Use after gather-invention-submission whenever the next step is understanding what the invention actually is and does before searching or sizing it. Also use for rapid technical orientation in an unfamiliar domain. Do not use for the patent or literature searches themselves — this skill only prepares the inputs they need.
---

# Analyze Technology Fundamentals

## When to use
- A structured submission record exists and the next step is characterizing the technology.
- The user asks for a feature-benefit table, an innovation assessment, or a regulatory-burden estimate.

## When NOT to use
- The user is asking you to run a patent or literature search — that consumes this skill's output but is a separate skill (`conduct-patent-landscape`, `conduct-novelty-search`, `conduct-literature-search`).

## Execution
1. **Idea description.** Write one plain-language paragraph. This seeds every downstream search-term list.
2. **Rapid domain orientation (30-minute cap).** Read a review article or high-level reference for the field; extract 5–10 terms practitioners actually use; explicitly note what you don't yet understand. The goal is "search-competent," not subject-matter expertise.
3. **Feature-benefit map.** Every feature row must resolve to a stated user-facing benefit — a feature with no benefit is incomplete.
4. **Innovation assessment — answer explicitly:**
   - What differs from known approaches?
   - Is any part of the novelty a *combination* of known elements? (Flag this as **combination-obviousness exposure**, not "combination novelty" — a combination can be completely novel while still being obvious. The operative question is derivation risk: how readily can the combination be reconstructed from prior-art components with a demonstrated motivation to combine? This is the weakest basis for an inventive-step argument absent an unexpected result.)
   - What specific technical elements are claimed as unique?
   - **Design-space position:** does the inventor appear to be exploring multiple physical implementations of the same higher-level architecture (sibling filings, alternative mechanisms)? Note where this invention sits in that exploration.
5. **Unexpected-result gate.** Does the claimed combination produce a demonstrable unexpected technical result? (CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED). If NOT IDENTIFIED, flag it as an evidence gap in the final report.
6. **Regulatory burden.** Estimate Low/Med/High per relevant jurisdiction, with the governing body cited.
7. **Development stage.** Classify Concept → Prototype → Validation → Pilot → Commercialization; if pre-prototype, list concrete next milestones with rough timelines.
8. **Classification seed.** Derive an initial IPC/CPC candidate set from the idea description — this feeds `conduct-patent-landscape` and `conduct-novelty-search` directly.
9. **Mandatory output: "what I still don't understand."** This list drives later escalation decisions — don't omit it even if short.

## Boundary
- No search is performed here.
- Regulatory output is scoping-level, not a substitute for regulatory counsel.
- Development-stage timelines are estimates pending expert review.
