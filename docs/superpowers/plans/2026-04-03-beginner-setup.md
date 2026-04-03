# Beginner Setup Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add beginner-friendly setup scripts for macOS and Windows that install `uv`, verify a compatible Python version, and install project dependencies with `uv sync`.

**Architecture:** Keep setup logic in two native scripts under `scripts/` so each operating system gets clear, readable commands and friendly error messages. Keep project usage instructions in `README.md`, and rely on the existing `uv` + `Makefile` workflow for runtime commands.

**Tech Stack:** Bash, PowerShell, `uv`, Python 3.12/3.13, Markdown

---

### Task 1: Add the macOS setup script

**Files:**
- Create: `scripts/setup-mac.sh`

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> Chloe setup for macOS"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="python3.13"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_VERSION="$(python3 -c 'import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")')"
  case "$PYTHON_VERSION" in
    3.12|3.13) PYTHON_BIN="python3" ;;
    *) PYTHON_BIN="" ;;
  esac
else
  PYTHON_BIN=""
fi

if [ -z "${PYTHON_BIN}" ]; then
  echo "Python 3.12 or 3.13 is required."
  echo "Install it from https://www.python.org/downloads/ then run this script again."
  exit 1
fi

echo "Using Python from: ${PYTHON_BIN}"
uv sync --python "${PYTHON_BIN}"

echo ""
echo "Setup complete."
echo "Next steps:"
echo "  cp .env.example .env"
echo "  make serve"
echo "  make ui"
```

- [ ] **Step 2: Verify shell syntax**

Run: `bash -n scripts/setup-mac.sh`
Expected: no output, exit code `0`

### Task 2: Add the Windows setup script

**Files:**
- Create: `scripts/setup-windows.ps1`

- [ ] **Step 1: Write the script**

```powershell
$ErrorActionPreference = "Stop"

Write-Host "==> Chloe setup for Windows"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed. Installing uv..."
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$HOME\.local\bin;$env:Path"
}

$pythonCommand = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        py -3.13 --version *> $null
        $pythonCommand = "3.13"
    } catch {}

    if (-not $pythonCommand) {
        try {
            py -3.12 --version *> $null
            $pythonCommand = "3.12"
        } catch {}
    }
}

if (-not $pythonCommand) {
    Write-Host "Python 3.12 or 3.13 is required."
    Write-Host "Install it from https://www.python.org/downloads/windows/ then run this script again."
    exit 1
}

Write-Host "Using Python $pythonCommand"
uv sync --python $pythonCommand

Write-Host ""
Write-Host "Setup complete."
Write-Host "Next steps:"
Write-Host "  Copy-Item .env.example .env"
Write-Host "  make serve"
Write-Host "  make ui"
```

- [ ] **Step 2: Verify PowerShell syntax**

Run: `pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('scripts/setup-windows.ps1',[ref]$null,[ref]$null) | Out-Null"`
Expected: no parse error, exit code `0`

### Task 3: Document the beginner setup flow

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a short setup section**

```md
## Installation simple

### macOS
```bash
chmod +x scripts/setup-mac.sh
./scripts/setup-mac.sh
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1
```
```

- [ ] **Step 2: Verify docs consistency**

Run: manually compare `README.md` commands with the final script names
Expected: commands match exactly
