#!/usr/bin/env bash
# Auto-fetch election results every 15 minutes (at :00, :15, :30, :45)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== TN Elections 2026 - Auto Fetcher ==="
echo "Will run fetch.sh at :00, :15, :30, :45 every hour."
echo "Press Ctrl+C to stop."
echo ""

while true; do
    # Get current minute
    MIN=$(date '+%M')
    # Calculate minutes until next 15-min mark
    REMAINDER=$((10#$MIN % 15))
    if [ "$REMAINDER" -eq 0 ]; then
        WAIT=0
    else
        WAIT=$((15 - REMAINDER))
    fi

    if [ "$WAIT" -gt 0 ]; then
        NEXT=$(date -v+"${WAIT}M" '+%H:%M' 2>/dev/null || date -d "+${WAIT} minutes" '+%H:%M' 2>/dev/null || echo "in ${WAIT}m")
        echo "[$(date '+%H:%M:%S')] Next fetch at $NEXT (waiting ${WAIT}m)..."
        sleep $((WAIT * 60))
    fi

    echo ""
    echo "[$(date '+%H:%M:%S')] Running fetch.sh..."
    echo "----------------------------------------"
    sh "$SCRIPT_DIR/fetch.sh"
    echo "----------------------------------------"
    echo "[$(date '+%H:%M:%S')] Fetch complete. Sleeping until next slot..."

    # Sleep 60s to avoid re-triggering in the same minute
    sleep 60
done
