#!/bin/sh
set -eu
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

printf '%s\n' "HANDOFF SNAPSHOT"
printf '%s\n' "branch: $(git branch --show-current 2>/dev/null || printf detached)"
printf '%s\n' "HEAD: $(git rev-parse --short HEAD 2>/dev/null || printf unknown)"

if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  printf '%s\n' "working tree:"
  git status --short
  printf '%s\n' "diff stat:"
  git diff --stat HEAD 2>/dev/null || true
else
  printf '%s\n' "working tree: clean"
fi

printf '%s\n' "last commit:"
git log -1 --pretty=format:'%h %s' 2>/dev/null || true
printf '\n'
