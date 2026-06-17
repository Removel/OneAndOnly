#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

find_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    echo "$PYTHON_BIN"
    return
  fi

  for candidate in python3.13 /opt/homebrew/bin/python3.13 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return
    fi
  done
}

PYTHON="$(find_python)"
if [[ -z "$PYTHON" ]]; then
  echo "Python 3.13+ is required, but no python executable was found."
  exit 1
fi

"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 13):
    raise SystemExit(f"Python 3.13+ is required, got {sys.version.split()[0]}")
PY

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is required. Install pnpm 9.x first, for example: npm install -g pnpm@9.14.0"
  exit 1
fi

echo "Using Python: $("$PYTHON" --version)"
echo "Using pnpm: $(pnpm --version)"

if [[ ! -d ".venv" ]]; then
  echo "Creating Python virtual environment..."
  "$PYTHON" -m venv .venv
else
  echo "Python virtual environment already exists."
fi

echo "Installing backend dependencies..."
"$ROOT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$ROOT_DIR/.venv/bin/python" -m pip install -r requirements.txt

echo "Installing frontend dependencies..."
(
  cd frontend
  pnpm install
)

echo "Initialization complete."
echo "Run ./dev.sh to start the project."
