# Design Spec — Invention Evaluation Framework Skill

Date: 2026-08-13

## Goal
Create a single invokeable OpenCode skill (`.opencode/skills/invention-evaluation-framework/SKILL.md`) that initiates the full 9-stage invention evaluation pipeline.

## Approach
Router-style skill that references the framework's `invention-evaluation-overview` and delegates to the 9 stage skills (01-09) in `/home/forsythe/Downloads/invention-evaluation-framework/`.

## Pipeline
Submission → Technology Profile → Patent Landscape → Novelty Search → Literature Search → Market Opportunity → Partners → Report.

## File Location
`.opencode/skills/invention-evaluation-framework/SKILL.md`

## Non-negotiables (from DIGEST.md)
- Disclosure dates captured at intake
- Novelty ≠ FTO
- Claim-element mapping mandatory
- Combination-obviousness exposure flagged explicitly (renamed from "combination novelty" in v1.4 — a combination can be novel yet obvious)
- "Insufficient evidence" is a valid output
- Every legal-adjacent statement carries "not legal advice" disclaimer
- Every quantitative claim is sourced
