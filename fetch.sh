#!/usr/bin/env bash
# Scrape all TN 2026 election results from ECI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TRENDS_DIR="$SCRIPT_DIR/trends"

# Live files
CONSTITUENCY_FILE="$SCRIPT_DIR/constituencydata.json"
PARTY_FILE="$SCRIPT_DIR/partydata.json"
CANDIDATE_FILE="$SCRIPT_DIR/candidatedata.json"

# Temporary download files (live files are not touched during scraping)
DL_CONSTITUENCY="$SCRIPT_DIR/download_constituencydata.json"
DL_PARTY="$SCRIPT_DIR/download_partydata.json"
DL_CANDIDATE="$SCRIPT_DIR/download_candidatedata.json"

echo "=== TN Elections 2026 - Results Scraper ==="
echo ""

# Step 1: Scrape into download_* files (live files untouched)
echo "[1/3] Scraping constituency-wise results from ECI website..."
python3 "$SCRIPT_DIR/scrape.py" > "$DL_CONSTITUENCY"
echo "  -> Saved to $DL_CONSTITUENCY"

echo "[2/3] Scraping party-wise results from ECI website..."
python3 "$SCRIPT_DIR/scrape_partywise.py" > "$DL_PARTY"
echo "  -> Saved to $DL_PARTY"

echo "[3/3] Scraping candidate-wise results from ECI website..."
python3 "$SCRIPT_DIR/scrape_candidates.py" > "$DL_CANDIDATE"
echo "  -> Saved to $DL_CANDIDATE"

# Step 2: Archive to trends folder with timestamp
echo ""
echo "Archiving to trends..."
mkdir -p "$TRENDS_DIR"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
cp "$DL_CONSTITUENCY" "$TRENDS_DIR/constituencydata_${TIMESTAMP}.json"
cp "$DL_PARTY" "$TRENDS_DIR/partydata_${TIMESTAMP}.json"
cp "$DL_CANDIDATE" "$TRENDS_DIR/candidatedata_${TIMESTAMP}.json"
echo "  -> Archived with timestamp $TIMESTAMP"

# Step 3: Remove old live files and rename download files to live
echo "Updating live files..."
rm -f "$CONSTITUENCY_FILE" "$PARTY_FILE" "$CANDIDATE_FILE"
mv "$DL_CONSTITUENCY" "$CONSTITUENCY_FILE"
mv "$DL_PARTY" "$PARTY_FILE"
mv "$DL_CANDIDATE" "$CANDIDATE_FILE"
echo "  -> Live files updated"

# Rebuild trends index
python3 "$SCRIPT_DIR/build_trends_index.py"

echo ""
echo "Done! constituencydata.json, partydata.json, and candidatedata.json are ready."
echo "Trend snapshots: $(ls "$TRENDS_DIR" | wc -l | tr -d ' ') files in trends/"
