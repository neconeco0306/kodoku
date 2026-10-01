# Claude Code operating rules

- Conserve Claude usage: prefer targeted reads/searches over broad repository scans and reuse facts already established in the session.
- The SessionStart hook injects a compact project snapshot. Use it instead of rediscovering branch, HEAD, working-tree state, and recent commits.
- When resuming work, use the `resume-project` skill and inspect only files directly required by the current task or failing checks.
- When repeated work appears, use `skill-factory` to move it to the cheapest reliable layer: script first, then hook, then Skill.
- Prefer deterministic commands and existing tests over model narration.
- Start with the smallest viable implementation and targeted checks. Expand only when evidence requires it.
- After two failed attempts with the same approach, change strategy instead of repeating similar exploration.
- Do not proactively refactor or inspect unrelated code while completing a bounded task.
