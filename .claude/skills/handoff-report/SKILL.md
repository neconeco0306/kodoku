---
name: handoff-report
description: Preserve compact continuation state when finishing work, switching sessions/models, or approaching a quota limit. Trigger on handoff, session switch, quota guard, 制限, 引き継ぎ, or end-of-work reporting.
---
# Goal

Preserve only what the next session needs, without spending tokens on project-history narration.

## Procedure

1. Run `.claude/scripts/handoff-snapshot.sh` first and reuse its deterministic facts.
2. Add only facts the script cannot know:
   - Task ID/current objective when one exists;
   - checks run and exact outcomes;
   - unresolved blocker/risk;
   - one next executable action.
3. Do not restate architecture, durable rules, or completed history.
4. Do not paste long diffs, logs, or file contents.
5. If the project has a dedicated handoff channel, post the compact report once; do not retry repeatedly on failure.

## Format

Keep to roughly 8–12 lines when possible:
- task/status
- branch/HEAD
- changed files
- checks
- blocker/risk
- next action
