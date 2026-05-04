#!/usr/bin/env bash
# Scrape TN 2026 election results from ECI and generate results HTML
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE="$SCRIPT_DIR/data.json"
PARTY_DATA_FILE="$SCRIPT_DIR/partydata.json"
TRENDS_DIR="$SCRIPT_DIR/trends"

echo "=== TN Elections 2026 - Results Scraper ==="
echo ""

# Step 1: Setup trends directory and timestamp
mkdir -p "$TRENDS_DIR"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
TREND_FILE="$TRENDS_DIR/data_${TIMESTAMP}.json"
PARTY_TREND_FILE="$TRENDS_DIR/partydata_${TIMESTAMP}.json"

# Step 2: Scrape constituency-wise results (write to trends first)
echo "[1/3] Scraping constituency-wise results from ECI website..."
python3 "$SCRIPT_DIR/scrape.py" > "$TREND_FILE"
echo "  -> Saved to $TREND_FILE"

# Step 3: Scrape party-wise results (write to trends first)
echo "[2/3] Scraping party-wise results from ECI website..."
python3 "$SCRIPT_DIR/scrape_partywise.py" > "$PARTY_TREND_FILE"
echo "  -> Saved to $PARTY_TREND_FILE"

# Step 4: Copy to main files (atomic-ish update to avoid disrupting views)
echo "[3/3] Updating live files..."
cp "$TREND_FILE" "$DATA_FILE"
cp "$PARTY_TREND_FILE" "$PARTY_DATA_FILE"
echo "  -> Updated $DATA_FILE"
echo "  -> Updated $PARTY_DATA_FILE"
echo ""

echo "Done! data.json and partydata.json are ready."
echo "Trend snapshots: $(ls "$TRENDS_DIR" | wc -l | tr -d ' ') files in trends/"
