#!/bin/sh
set -eu
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests -v
printf '%s\n' "verify-project: PASS"
