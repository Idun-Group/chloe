#!/usr/bin/env bash
set -euo pipefail

is_sourced=0
if [ "${BASH_SOURCE[0]}" != "$0" ]; then
  is_sourced=1
fi

stop_script() {
  local code="$1"
  if [ "$is_sourced" -eq 1 ]; then
    return "$code"
  fi
  exit "$code"
}

echo "==> Chloe setup for macOS"

if [ ! -f "pyproject.toml" ]; then
  echo "Error: run this script from the project root."
  stop_script 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

PYTHON_BIN=""

if command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="python3.13"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  case "$PYTHON_VERSION" in
    3.12|3.13) PYTHON_BIN="python3" ;;
  esac
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3.12 or 3.13 is required."
  echo "Install it from https://www.python.org/downloads/ and run this script again."
  stop_script 1
fi

echo "Using Python: $PYTHON_BIN"
echo "Creating virtual environment in .venv..."
uv venv --python "$PYTHON_BIN" .venv

echo "Installing project dependencies..."
uv sync --python "$PYTHON_BIN"

echo "Activating .venv..."
# shellcheck disable=SC1091
source ".venv/bin/activate"

echo ""
echo "Setup complete. Your Python environment is active in this terminal."
echo "Next steps:"
echo "  cp .env.example .env"
echo "  uv run idun agent serve --source=file --path=app/agent/config.yaml"
echo "  uv run streamlit run streamlit/app.py"

if [ "$is_sourced" -eq 0 ]; then
  echo ""
  echo "Tip: use 'source scripts/setup-mac.sh' next time to keep .venv active after the script ends."
fi
