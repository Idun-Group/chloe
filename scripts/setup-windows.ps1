$ErrorActionPreference = "Stop"

Write-Host "==> Chloe setup for Windows"

if (-not (Test-Path "pyproject.toml")) {
    Write-Host "Error: run this script from the project root."
    exit 1
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed. Installing uv..."
    irm https://astral.sh/uv/install.ps1 | iex
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

$pythonVersion = $null

if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        py -3.13 --version *> $null
        $pythonVersion = "3.13"
    } catch {}

    if (-not $pythonVersion) {
        try {
            py -3.12 --version *> $null
            $pythonVersion = "3.12"
        } catch {}
    }
}

if (-not $pythonVersion) {
    Write-Host "Python 3.12 or 3.13 is required."
    Write-Host "Install it from https://www.python.org/downloads/windows/ and run this script again."
    exit 1
}

Write-Host "Using Python $pythonVersion"
Write-Host "Creating virtual environment in .venv..."
uv venv --python $pythonVersion .venv

Write-Host "Installing project dependencies..."
uv sync --python $pythonVersion

Write-Host "Activating .venv..."
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Setup complete. Your Python environment is active in this terminal."
Write-Host "Next steps:"
Write-Host "  Copy-Item .env.example .env"
Write-Host "  uv run idun agent serve --source=file --path=app/agent/config.yaml"
Write-Host "  uv run streamlit run streamlit/app.py"
Write-Host ""
Write-Host "Tip: run this script with '. .\scripts\setup-windows.ps1' to keep .venv active in your current PowerShell session."
