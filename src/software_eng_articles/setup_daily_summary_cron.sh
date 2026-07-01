#!/bin/bash
set -e

# Resolve the folder where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_SCRIPT="$SCRIPT_DIR/run_daily_summary.sh"

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: Target execution script not found at $TARGET_SCRIPT"
    exit 1
fi

if [ "$1" == "--uninstall" ]; then
    echo "Uninstalling cron job..."
    (crontab -l 2>/dev/null | grep -v "$TARGET_SCRIPT") | crontab -
    echo "Cron job successfully removed!"
    exit 0
fi

# Default installation (daily at 8:00 AM)
CRON_SCHEDULE="0 8 * * *"
CRON_CMD="$CRON_SCHEDULE $TARGET_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

# Safely read existing crontab, remove any existing entry for this script, 
# and write the new cron entry back
(crontab -l 2>/dev/null | grep -v "$TARGET_SCRIPT" ; echo "$CRON_CMD") | crontab -

echo "Cron job successfully registered!"
echo "Schedule: Daily at 8:00 AM ($CRON_SCHEDULE)"
echo "Command:  $CRON_CMD"
