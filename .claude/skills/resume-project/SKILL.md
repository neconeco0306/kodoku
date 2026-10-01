---
name: resume-project
description: Resume work in an existing repository with minimal re-reading. Trigger on "continue", "pick up where we left off", "続けて", "再開", or when starting a fresh Claude Code session in a project.
---
# Goal

Resume from the smallest trustworthy context instead of rescanning the repository.

## Procedure

1. Use the SessionStart project snapshot for branch, HEAD, working-tree state, and recent commits.
2. Read only the smallest task/status file needed to understand the current step.
3. Before reopening source files, check whether the current session already established their relevant contents.
4. Inspect only files directly named by the task, failing tests, changed-file list, or a concrete dependency.
5. Start with the smallest executable next step; broaden investigation only when evidence requires it.

## Cost rules

- Do not perform broad repository scans by default.
- Do not re-open unchanged files without a specific reason.
- Do not rerun successful checks merely to regain context.
- Prefer deterministic status commands and existing reports over model-written summaries.
