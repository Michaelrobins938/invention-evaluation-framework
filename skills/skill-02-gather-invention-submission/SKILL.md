---
name: gather-invention-submission
description: Captures a complete, structured invention record — description, background, innovation claims, proof-of-concept status, IP posture, and disclosure/publication history — before any technical, patent, or market analysis begins. Use whenever a user provides raw invention information (pasted text, an uploaded disclosure form, a verbal description) or asks what information is needed to start an evaluation. Always run this before analyze-technology-fundamentals if no structured record exists yet. Critically, always use this to capture public-disclosure and sale-offer dates, since these set statutory filing deadlines.
---

# Gather Invention Submission

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- A user shares an invention description, upload, or disclosure form.
- A user asks what information you need to start an evaluation.

## When NOT to use
- A structured submission record already exists for this invention — go straight to `analyze-technology-fundamentals`.

## Fields to capture

**Mandatory**
- Invention name
- Short description (1–2 sentences)
- Detailed description
- Background / related research the inventor is aware of
- Innovation claims (what the inventor believes is new)

**Critical secondary**
- Proof-of-concept status
- Current IP status (filed, provisional, unfiled, licensed)
- Target products/services and markets
- Known competitors

**Mandatory — disclosure timing**
Capture every public talk, publication, demonstration, sale offer, or social-media post about the invention, each with a date. This is the single highest-leverage field in the entire intake: it can determine whether a filing deadline has already passed. If the inventor states there has been no disclosure, record that as "CONFIRMED ABSENT (per inventor statement)" — the bounded universe is the inventor's own statement, with `absence_basis` noted — rather than leaving the field blank; a blank field and a confirmed "none" are not the same thing for audit purposes. **Distinguish the two cases:** an inventor's direct statement of no disclosure is CONFIRMED ABSENT (bounded universe: inventor statement, single source); a search that found no disclosure is a search-result record (avenue metadata) — it establishes nothing about the world and never upgrades to CONFIRMED ABSENT. If a search-based absence is needed, it must go through the Evidence Sufficiency Gate with a bounded universe.

## Execution
1. Elicit each mandatory field; do not infer values the inventor hasn't stated.
2. Explicitly ask about disclosure timing even if not volunteered — inventors routinely underreport this.
3. Flag any missing field rather than filling it with a plausible guess.
4. Output the record as a structured table or YAML block so downstream skills can consume it directly.
5. If any disclosure date appears close to or past a jurisdiction's grace-period limit, flag this immediately for escalation rather than continuing silently through the pipeline.

## Boundary
- This skill records claims; it does not validate, search, or judge them.
- No patentability or market opinion at this stage.
