#!/bin/sh
set -eu

repo_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$repo_dir"

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

{
  git diff --name-only --diff-filter=ACMRT HEAD 2>/dev/null || true
  git diff --cached --name-only --diff-filter=ACMRT 2>/dev/null || true
  git ls-files --others --exclude-standard 2>/dev/null || true
} | awk 'NF && !seen[$0]++' > "$tmp"

if [ ! -s "$tmp" ]; then
  printf '%s\n' "check-changed: no changed/untracked files"
  exit 0
fi

checked=0
skipped=0

while IFS= read -r file; do
  [ -f "$file" ] || continue

  case "$file" in
    *.js|*.mjs|*.cjs)
      if command -v node >/dev/null 2>&1; then
        printf '%s\n' "node --check $file"
        node --check "$file"
        checked=$((checked + 1))
      else
        skipped=$((skipped + 1))
      fi
      ;;
    *.py)
      if command -v python3 >/dev/null 2>&1; then
        printf '%s\n' "python3 -m py_compile $file"
        python3 -m py_compile "$file"
        checked=$((checked + 1))
      else
        skipped=$((skipped + 1))
      fi
      ;;
    *.json)
      if command -v python3 >/dev/null 2>&1; then
        printf '%s\n' "json parse $file"
        python3 -m json.tool "$file" >/dev/null
        checked=$((checked + 1))
      else
        skipped=$((skipped + 1))
      fi
      ;;
    *.sh|*.command)
      printf '%s\n' "sh -n $file"
      sh -n "$file"
      checked=$((checked + 1))
      ;;
    *)
      skipped=$((skipped + 1))
      ;;
  esac
done < "$tmp"

printf '%s\n' "check-changed: PASS (checked=$checked skipped=$skipped)"
