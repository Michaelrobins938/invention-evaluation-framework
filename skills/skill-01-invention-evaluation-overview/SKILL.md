---
name: invention-evaluation-overview
description: Orchestration layer for the ten-phase invention evaluation pipeline. Determines current phase, routes to the correct sub-skill, and tracks completion state. Does not perform search or analysis itself. Use when a user asks how to start evaluating an invention or wants the big-picture process map.
---

# Invention Evaluation Overview

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## Core principle

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

This pipeline is an **evidence-constrained invention reasoning engine**, not a collection of research prompts. The governing rule, enforced at every stage: **nothing downstream is allowed to promote an inference into a fact, and no proposition enters the report except through the Evidence Sufficiency Gate.** Every proposition carries a stable `proposition_id` + `proposition_version` and the evidence state it was established with (see GLOSSARY.md — Epistemic Architecture). The framework's job is to separate *what the evidence establishes* from *what the analyst wants to conclude* — and to prevent the two from merging.

## When to use
- "I have an invention — how do I evaluate it?"
- "What steps should I follow for commercial assessment?"
- "Give me the big picture of the evaluation process."

## When NOT to use
- The user is asking for a specific analysis (market, patent, etc.) — route to that skill directly.

## Execution
0. **Run initialization.** Resolve the normalized patent identifier and initialize `/home/forsythe/Desktop/tools/invention-evaluation-framework/evaluations/<normalized-patent-number>/`. Create the run manifest and execution ledger before any phase action. A manually written phase artifact never proves execution; only a ledger-backed action does.
1. Confirm whether a structured submission record already exists.
   - If no, invoke `gather-invention-submission` first.
   - If yes, determine which phase is next based on available outputs.
2. Check dependency status (see INDEX.md):
   - Hard dependencies must be satisfied before execution.
   - Soft dependencies can be bypassed with degraded capability, but note the degradation in the final report.
3. Maintain a phase-completion checklist with explicit "blocked / needs-input" states.
4. Route outputs to the next skill in the dependency chain. Each routed output must preserve proposition identity: `proposition_id` + `proposition_version` + evidence state. Never strip, upgrade, or silently re-scope a proposition at hand-off; any refinement requires a version increment.
5. If the user asks about FTO / infringement, stop and explain the distinction (see GLOSSARY.md) — do not proceed into the novelty pipeline as a substitute.
6. **Final deliverable is the styled report.** After `compile-report` produces the report MD, ALWAYS render the branded "inventionevaluator" deliverable via `render-report` (Phase 10). Every end-to-end run ends with the styled HTML + A4 PDF — clean cover (wordmark + metadata block), TOC with accurate physical page numbers, running footer with page counters, CONFIDENTIAL watermark, gauges, SWOT, section dividers, search boxes. The renderer is presentation-only: it never invents metrics, and every gauge/bar value must exist in the per-run scores manifest with a basis proposition_id.
7. **Delivery gate.** Do not declare the run complete until the run manifest, source provenance, proposition ledger, execution ledger, avenue ledger, evidence graph, evidence debt, constraint report, scores manifest, compiled Markdown, HTML, PDF, and delivery manifest exist and are non-empty. Report `COMPLETED_WITH_EVIDENCE_DEBT` when artifacts are delivered but propositions remain unresolved.

## Boundary
- No search, no scoring, no legal or financial opinion.
- Unestablished propositions are work-queue items, not findings. See GLOSSARY.md — Evidence Sufficiency Gate.
- Not a substitute for docketing software or prosecution-tracking system.
