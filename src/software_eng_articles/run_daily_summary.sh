#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Find project root by searching upwards for pyproject.toml
DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT=""
while [ "$DIR" != "/" ]; do
    if [ -f "$DIR/pyproject.toml" ]; then
        PROJECT_ROOT="$DIR"
        break
    fi
    DIR="$(dirname "$DIR")"
done

if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Could not locate project root containing pyproject.toml"
    exit 1
fi

# 1. Activate the virtual environment from the resolved project root
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "Error: Virtual environment (.venv) not found at $PROJECT_ROOT/.venv"
    exit 1
fi

# 2. Check if the package is already installed. If not, check for a wheel in the script folder and install it.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v daily-summary &> /dev/null; then
    WHL_FILE=$(find "$SCRIPT_DIR" -maxdepth 1 -name "*.whl" | head -n 1)

    if [ -n "$WHL_FILE" ]; then
        echo "daily-summary not found in venv. Installing wheel: $(basename "$WHL_FILE")..."
        pip install --no-deps --force-reinstall "$WHL_FILE"
    else
        echo "Error: daily-summary command not found, and no wheel file (*.whl) was found in $SCRIPT_DIR to install."
        exit 1
    fi
fi

# 3. Make sure we execute from the directory where this script resides
# This ensures that any relative outputs (like morning_summary.md) are written to the execution folder
cd "$SCRIPT_DIR"

# 4. Execute the daily summary pipeline
daily-summary
