#!/bin/sh
set -eu

repo_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$repo_dir" 2>/dev/null || exit 0

if ! command -v git >/dev/null 2>&1 || ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

branch=$(git branch --show-current 2>/dev/null || true)
head=$(git rev-parse --short HEAD 2>/dev/null || true)
status=$(git status --short 2>/dev/null | sed -n '1,12p')
commits=$(git log -3 --pretty=format:'%h %s' 2>/dev/null || true)

printf '%s\n' "PROJECT SNAPSHOT"
printf '%s\n' "branch: ${branch:-detached}"
printf '%s\n' "HEAD: ${head:-unknown}"

if [ -n "$status" ]; then
  printf '%s\n' "working tree:"
  printf '%s\n' "$status"
else
  printf '%s\n' "working tree: clean"
fi

if [ -n "$commits" ]; then
  printf '%s\n' "recent commits:"
  printf '%s\n' "$commits"
fi

for task_file in TASK.md TASKS.md TODO.md ROADMAP.md; do
  if [ -f "$task_file" ]; then
    printf '%s\n' "task file available: $task_file (read only if needed)"
    break
  fi
done
