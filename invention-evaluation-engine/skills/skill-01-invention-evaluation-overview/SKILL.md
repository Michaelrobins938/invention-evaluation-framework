---
name: invention-evaluation-overview
description: Orchestration layer for the nine-phase invention evaluation pipeline. Determines current phase, routes to the correct sub-skill, and tracks completion state. Does not perform search or analysis itself. Use when a user asks how to start evaluating an invention or wants the big-picture process map.
---

# Invention Evaluation Overview

## Core principle

This pipeline is an **evidence-constrained invention reasoning engine**, not a collection of research prompts. The governing rule, enforced at every stage: **nothing downstream is allowed to promote an inference into a fact.** Every proposition carries the evidence grade it was established with (see GLOSSARY.md — Evidence → Inference → Conclusion firewall). The framework's job is to separate *what the evidence establishes* from *what the analyst wants to conclude* — and to prevent the two from merging.

## When to use
- "I have an invention — how do I evaluate it?"
- "What steps should I follow for commercial assessment?"
- "Give me the big picture of the evaluation process."

## When NOT to use
- The user is asking for a specific analysis (market, patent, etc.) — route to that skill directly.

## Execution
1. Confirm whether a structured submission record already exists.
   - If no, invoke `gather-invention-submission` first.
   - If yes, determine which phase is next based on available outputs.
2. Check dependency status (see INDEX.md):
   - Hard dependencies must be satisfied before execution.
   - Soft dependencies can be bypassed with degraded capability, but note the degradation in the final report.
3. Maintain a phase-completion checklist with explicit "blocked / needs-input" states.
4. Route outputs to the next skill in the dependency chain. Each routed output must preserve its evidence grades — never strip or upgrade them at hand-off.
5. If the user asks about FTO / infringement, stop and explain the distinction (see GLOSSARY.md) — do not proceed into the novelty pipeline as a substitute.

## Boundary
- No search, no scoring, no legal or financial opinion.
- Not a substitute for docketing software or prosecution-tracking system.
