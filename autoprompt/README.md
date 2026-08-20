# Autoprompt Integration for IEF

This directory holds **IEF-specific Autoprompt configuration**, not a copy of the Autoprompt skill itself.

## What lives where

| Path | Authority | Purpose |
|------|-----------|---------|
| `~/.config/opencode/skills/autoprompt/SKILL.md` | Autoprompt (execution OS) | Installed skill, do not edit |
| `~/.config/opencode/agents/ap-*.md` | Autoprompt | 25 worker personas |
| `~/.config/opencode/autoprompt.opencode.json` | Autoprompt | Activation profile (inherited-only) |
| `autoprompt/ief.json` (this repo) | IEF | IEF mission/DAG/skill-path/run-state configuration |
| `schemas/*` | IEF | Typed contracts (mission, skill, evidence) |
| `engine_v17/autoprompt_adapter.py` | Adapter | Mission ↔ execution translation |
| `IEF_EXECUTION_CONTRACT.md` | IEF | Human-readable contract |

## Transient state

Governance artifacts `PROMPTS.txt`, `ROADMAP.md`, `GATELOG.md` live at `~/.ief-runs/<evaluation-id>/` (or `.ief-runs/<evaluation-id>/` if home unavailable). They **never** appear in the target working tree diff. Evaluation artifacts live in `evaluations/<normalized-id>/`.

## No recursive orchestration

Autoprompt is the top-level execution authority. IEF orchestrator is the domain-policy router. Workers do not spawn new top-level Autoprompt runs. The recursion brake is enforced by `permission: { task: { "*": "deny", "ap-*": "allow" } }` and `skill: deny` on every persona.
