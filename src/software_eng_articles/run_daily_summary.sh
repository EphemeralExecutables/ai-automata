#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Parse --section argument
SECTION=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --section|-s)
            SECTION="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $(basename "$0") --section <name>"
            exit 1
            ;;
    esac
done

if [ -z "$SECTION" ]; then
    echo "Error: --section <name> is required."
    echo "Usage: $(basename "$0") --section <name>"
    echo "Available sections are defined in prompts.toml at the repo root."
    exit 1
fi

# Find virtual environment by searching upwards for .venv/bin/activate
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_ACTIVATED=false
while [ "$DIR" != "/" ]; do
    if [ -f "$DIR/.venv/bin/activate" ]; then
        source "$DIR/.venv/bin/activate"
        VENV_ACTIVATED=true
        break
    fi
    DIR="$(dirname "$DIR")"
done

if [ "$VENV_ACTIVATED" = false ]; then
    echo "Error: Could not locate virtual environment (.venv) containing bin/activate in this directory or any parent directories."
    exit 1
fi

# Check for the newest wheel in the script folder.
# sort -V sorts by version number, tail -n 1 picks the highest.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WHL_FILE=$(find "$SCRIPT_DIR" -maxdepth 1 -name "*.whl" | sort -V | tail -n 1)

if [ -n "$WHL_FILE" ]; then
    # Extract version from wheel filename: ai_automata-0.3.0-py3-none-any.whl -> 0.3.0
    WHL_VERSION=$(basename "$WHL_FILE" | cut -d'-' -f2)
    INSTALLED_VERSION=$(pip show ai-automata 2>/dev/null | grep "^Version:" | cut -d' ' -f2)

    if [ "$WHL_VERSION" = "$INSTALLED_VERSION" ]; then
        echo "ai-automata v$INSTALLED_VERSION already installed — skipping reinstall."
    else
        echo "Installing wheel: $(basename "$WHL_FILE") (installed: ${INSTALLED_VERSION:-none})..."
        pip install --force-reinstall "$WHL_FILE"
    fi
elif ! command -v daily-summary &> /dev/null; then
    echo "Error: daily-summary command not found, and no wheel file (*.whl) was found in $SCRIPT_DIR to install."
    exit 1
fi



# Find the directory containing prompts.toml by searching upward from SCRIPT_DIR.
# This works whether the script is deployed flat (at repo root) or in a subdirectory
# like src/software_eng_articles/.
REPO_ROOT=""
SEARCH_DIR="$SCRIPT_DIR"
while [ "$SEARCH_DIR" != "/" ]; do
    if [ -f "$SEARCH_DIR/prompts.toml" ]; then
        REPO_ROOT="$SEARCH_DIR"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Could not find prompts.toml in $SCRIPT_DIR or any parent directory."
    exit 1
fi

cd "$REPO_ROOT"

# Execute the daily summary pipeline for the requested section
daily-summary --section "$SECTION"
