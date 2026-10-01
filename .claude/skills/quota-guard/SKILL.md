---
name: quota-guard
description: Conserve Claude quota when a usage limit, session limit, rate limit, or quota warning appears. Trigger on "Usage limit reached", "session limit", "rate limit", "quota", repeated 429s, or when preserving work before a model limit reset.
---
# Goal

Avoid wasting the remaining or newly reset quota on retries, duplicate sessions, rediscovery, or repeated successful checks.

## On a limit signal

1. Stop launching new Claude sessions, subagents, Council roles, or model retries.
2. Do not rerun a command/test that already succeeded in the current work package.
3. Gather only deterministic continuation state:
   - branch and HEAD;
   - working-tree status;
   - files changed;
   - last check that passed/failed;
   - exact unfinished next action.
4. Use `handoff-report` when available; otherwise keep the handoff under roughly 12 lines.
5. Do not turn a quota error into a code bug unless independent evidence shows a code failure.
6. Stop. Do not poll the quota or repeatedly test whether it reset.

## After quota resets

1. Resume the existing session when supported instead of creating new roles/sessions.
2. Use `resume-project` or the SessionStart snapshot; do not rescan the repository.
3. Skip all already-successful steps unless code changed afterward.
4. Continue from the exact unfinished action.
5. If the same operation hits the limit again, hand off and stop rather than looping.

## Expensive workflow rule

For multi-role workflows (Council, independent solver/judges, agent panels), start them only when there is enough quota to finish the bounded cycle. Never leave avoidable half-runs that must be replayed after reset.
