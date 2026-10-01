# Claude Code operating rules

- Use the SessionStart snapshot instead of rediscovering branch, HEAD, working-tree state, or recent commits.
- Use `resume-project` for continuation. Inspect only files directly required by the task, changed-file list, failing checks, or a concrete dependency.
- Prefer targeted reads/searches and reuse facts already established in the session. Do not reopen unchanged files without a reason.
- After ordinary local source edits, run `.claude/scripts/check-changed.sh` before choosing broader tests.
- For material completion or cross-cutting changes, run `.claude/scripts/verify-project.sh`; do not rediscover the full-test command each session.
- When repeated work appears, use `skill-factory` and prefer script → hook → Skill over more permanent instructions.
- On usage/session/rate limits, use `quota-guard`; do not retry, start duplicate sessions, or rerun already-successful work.
- At a real session/model boundary, use `handoff-report`; keep continuation state compact.
- Start with the smallest viable implementation. After two failed attempts with the same approach, change strategy.
- Do not proactively refactor or inspect unrelated code while completing a bounded task.
- Prefer deterministic evidence and tests over model narration.
