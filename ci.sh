#!/usr/bin/env bash
# Build & test pipeline for Linux/macOS: venv -> deps -> pytest -> PyInstaller -> smoke test.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV="$ROOT/.venv"
BUILD="$ROOT/build"

echo "==> [1/5] $("$PYTHON" --version)"

echo "==> [2/5] Creating virtual environment in .venv and installing dependencies"
"$PYTHON" -m venv "$VENV"
if [ -f "$VENV/Scripts/python.exe" ]; then   # Git Bash on Windows
  VPY="$VENV/Scripts/python.exe"; EXE="$BUILD/bin/hello.exe"
else
  VPY="$VENV/bin/python"; EXE="$BUILD/bin/hello"
fi
"$VPY" -m pip install --disable-pip-version-check -q -r requirements-dev.txt

echo "==> [3/5] Running unit tests (pytest)"
mkdir -p "$BUILD/test-results"
"$VPY" -m pytest --junitxml="$BUILD/test-results/junit.xml"

echo "==> [4/5] Building executable build/bin/hello (PyInstaller)"
"$VPY" -m PyInstaller --noconfirm --clean --log-level WARN --onefile --name hello \
  --paths "$ROOT/src" --distpath "$BUILD/bin" --workpath "$BUILD/work" --specpath "$BUILD" \
  "$ROOT/src/hello/__main__.py"

echo "==> [5/5] Smoke test of the executable"
OUTPUT="$("$EXE" | tr -d '\r')"
echo "$OUTPUT"
if [ "$OUTPUT" != "Hello, World!" ]; then
  echo "ERROR: unexpected output from $EXE" >&2
  exit 1
fi

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  echo "### $(uname -s): tests passed, executable \`build/bin/$(basename "$EXE")\` built and prints \`$OUTPUT\`" >> "$GITHUB_STEP_SUMMARY"
fi
echo "CI: SUCCESS"
