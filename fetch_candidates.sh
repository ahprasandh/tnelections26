#!/usr/bin/env bash
# Scrape candidate-wise TN 2026 election results from ECI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE="$SCRIPT_DIR/candidatedata.json"
TRENDS_DIR="$SCRIPT_DIR/trends"

echo "=== TN Elections 2026 - Candidate-wise Scraper ==="
echo ""

echo "[1/1] Scraping candidate-wise results from ECI website..."
python3 "$SCRIPT_DIR/scrape_candidates.py" > "$DATA_FILE"
echo "  -> Saved to $DATA_FILE"

# Archive to trends folder with timestamp
mkdir -p "$TRENDS_DIR"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
TREND_FILE="$TRENDS_DIR/candidatedata_${TIMESTAMP}.json"
cp "$DATA_FILE" "$TREND_FILE"
echo "  -> Archived to $TREND_FILE"

echo ""
echo "Done! candidatedata.json is ready."
echo "Trend snapshots: $(ls "$TRENDS_DIR"/candidatedata_* 2>/dev/null | wc -l | tr -d ' ') candidate files in trends/"
