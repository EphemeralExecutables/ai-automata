#!/bin/bash
set -e

# Resolve the repo root (two levels up from src/software_eng_articles/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "==> Repo root: $REPO_ROOT"

# 1. Check for Python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# 2. Create virtual environment at repo root if it doesn't already exist
VENV_DIR="$REPO_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "==> Virtual environment already exists at $VENV_DIR — skipping creation."
fi

# 3. Activate the virtual environment
source "$VENV_DIR/bin/activate"

# 4. Upgrade pip
echo "==> Upgrading pip..."
pip install --upgrade pip --quiet

# 5. Install the package:
#    Prefer a wheel in the script directory (pre-built for deployment),
#    otherwise install in editable mode from the repo root (dev/source tree).
WHL_FILE=$(find "$SCRIPT_DIR" -maxdepth 1 -name "*.whl" | head -n 1)
if [ -n "$WHL_FILE" ]; then
    echo "==> Installing wheel: $(basename "$WHL_FILE")..."
    pip install --force-reinstall "$WHL_FILE"
else
    echo "==> No wheel found. Installing package in editable mode from repo root..."
    pip install -e "$REPO_ROOT"
fi

echo ""
echo "==> Setup completed successfully! Virtual environment is fully configured."
echo "    Activate it with: source $VENV_DIR/bin/activate"
