#!/usr/bin/env bash
set -euo pipefail

echo "==> Chloe setup for macOS"

if [ ! -f "pyproject.toml" ]; then
  echo "Error: run this script from the project root."
  exit 1
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
  exit 1
fi

echo "Using Python: $PYTHON_BIN"
uv sync --python "$PYTHON_BIN"

echo ""
echo "Setup complete."
echo "Next steps:"
echo "  cp .env.example .env"
echo "  uv run idun agent serve --source=file --path=app/agent/config.yaml"
echo "  uv run streamlit run streamlit/app.py"
