# Design: Beginner Setup Scripts

## Goal

Add a beginner-friendly setup flow for macOS and Windows that installs `uv`, uses a compatible Python version for the project, and installs all dependencies from `pyproject.toml`/`uv.lock`.

## Context

This repository already uses `uv` as the package manager.
The project requires Python `>=3.12,<3.14`.
The current developer flow is based on `uv sync`, `make serve`, and `make ui`.

## Proposed Deliverables

1. `scripts/setup-mac.sh`
2. `scripts/setup-windows.ps1`
3. A short beginner setup section in `README.md`

## Recommended Approach

Use two native scripts rather than one cross-platform installer.

### Why

- Beginners can run commands that match their operating system.
- Native shell syntax stays simple and readable.
- Error messages can be written in plain language for each OS.
- The project already relies on `uv`, so the scripts should delegate dependency installation to `uv sync`.

## Script Behavior

### macOS

The macOS script should:

1. Check whether `uv` is installed.
2. If `uv` is missing, install it with the official installer.
3. Check for a compatible Python interpreter (`3.12` or `3.13`).
4. If Python is missing, print a clear message telling the user how to install it.
5. Run `uv sync`.
6. Print the next commands to launch the API and UI.

### Windows

The Windows PowerShell script should:

1. Check whether `uv` is installed.
2. If `uv` is missing, install it with the official PowerShell installer.
3. Check for a compatible Python interpreter (`3.12` or `3.13`).
4. If Python is missing, print a clear message telling the user how to install it.
5. Run `uv sync`.
6. Print the next commands to launch the API and UI.

## UX Requirements

- Keep messages short and beginner-friendly.
- Fail early with actionable instructions.
- Avoid clever shell logic that would be hard to maintain.
- Prefer explicit output over silent automation.

## Error Handling

- If `uv` installation fails, stop and ask the user to install it manually.
- If no compatible Python is found, stop and ask the user to install Python `3.12` or `3.13`.
- If `uv sync` fails, return the original command output so debugging remains possible.

## Testing

- Verify script syntax where practical.
- Confirm the README instructions match the actual script names.
- Do not add automated tests unless a simple focused check is clearly useful.

## Non-Goals

- Automatically installing Python itself on every platform.
- Hiding all setup details from the user.
- Replacing the existing `Makefile` workflow.
