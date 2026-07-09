#!/bin/bash
set -e

# Resolve the folder where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_SCRIPT="$SCRIPT_DIR/run_daily_summary.sh"

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: Target execution script not found at $TARGET_SCRIPT"
    exit 1
fi

# Parse arguments
SECTION=""
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --section|-s)
            SECTION="$2"
            shift 2
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $(basename "$0") --section <name> [--uninstall]"
            exit 1
            ;;
    esac
done

if [ "$UNINSTALL" = true ]; then
    echo "Uninstalling cron job..."
    (crontab -l 2>/dev/null | grep -v "$TARGET_SCRIPT") | crontab -
    echo "Cron job successfully removed!"
    exit 0
fi

if [ -z "$SECTION" ]; then
    echo "Error: --section <name> is required."
    echo "Usage: $(basename "$0") --section <name> [--uninstall]"
    echo "Available sections are defined in prompts.toml at the repo root."
    exit 1
fi

# Default installation (daily at 8:00 AM)
CRON_SCHEDULE="0 8 * * *"
CRON_CMD="$CRON_SCHEDULE $TARGET_SCRIPT --section $SECTION >> $SCRIPT_DIR/cron_${SECTION}.log 2>&1"

# Safely read existing crontab, remove any existing entry for this script+section,
# and write the new cron entry back
(crontab -l 2>/dev/null | grep -v "$TARGET_SCRIPT --section $SECTION" ; echo "$CRON_CMD") | crontab -

echo "Cron job successfully registered!"
echo "Schedule: Daily at 8:00 AM ($CRON_SCHEDULE)"
echo "Section:  [$SECTION]"
echo "Command:  $CRON_CMD"
