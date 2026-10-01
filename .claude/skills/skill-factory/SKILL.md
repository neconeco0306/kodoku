---
name: skill-factory
description: Turn repeated Claude Code work into the cheapest reusable mechanism. Trigger when the user asks to skillize work, make it reusable, reduce Claude usage, automate repeated instructions, create/update a skill, or when the same workflow clearly repeats.
---
# Goal

Reduce future model usage and user effort by moving repeated work to the cheapest reliable layer while keeping permanent context small.

## Decision order

1. **Script** — deterministic commands, parsing, formatting, checks, snapshots, or repeatable transformations.
2. **Hook** — work that should run automatically at a lifecycle event.
3. **Skill** — procedural judgment that still needs a model but should load only when relevant.
4. **CLAUDE.md** — only short durable rules needed almost every session.
5. **Keep manual** — one-off or highly variable work not worth productizing.

## Procedure

1. Identify the repeated unit from the current request and the smallest relevant project history.
2. Inspect only relevant existing scripts, hooks, skills, settings, and CLAUDE.md.
3. Check for overlap; extend an existing mechanism rather than creating a near-duplicate.
4. Choose the lowest-cost reliable layer from the decision order.
5. Create or update the mechanism only when recurrence or saved model work justifies maintenance.
6. Put deterministic work in scripts instead of prose.
7. Validate one positive case and one non-trigger/negative case when practical.
8. Report compactly what was automated and any remaining one-time user action.

## Guardrails

- Prefer zero-model automation over a Skill when possible.
- Do not recursively create factories or auto-install unreviewed skills.
- Do not sweep unrelated files or private history.
- Merge or remove overlapping mechanisms instead of accumulating them.
