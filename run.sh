#!/usr/bin/env bash
# Launch Hello World from source inside the project's virtual environment.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"

if [ ! -d "$ROOT/.venv" ]; then
  "$PYTHON" -m venv "$ROOT/.venv"
fi
if [ -f "$ROOT/.venv/Scripts/python.exe" ]; then
  VPY="$ROOT/.venv/Scripts/python.exe"
else
  VPY="$ROOT/.venv/bin/python"
fi

cd "$ROOT/src"
exec "$VPY" -m hello "$@"
