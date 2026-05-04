#!/usr/bin/env python3
"""Download all candidate photos from ECI results website into images/candidates/."""

import json
import os
import re
import subprocess
import sys
import time
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "images", "candidates")
CONSTITUENCY_FILE = os.path.join(SCRIPT_DIR, "constituencydata.json")

BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/candidateswise-S22{}.htm"


def sanitize_name(name):
    """Clean candidate name for use as filename."""
    name = name.strip().upper()
    name = re.sub(r'[^A-Z0-9 .]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = name.strip('._')
    return name


def fetch_page(const_no):
    url = BASE_URL.format(const_no)
    result = subprocess.run(
        ["curl", "-s", "-L", "--noproxy", "*", "--max-time", "30", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def download_photo(url, filepath):
    result = subprocess.run(
        ["curl", "-s", "-L", "--noproxy", "*", "--max-time", "15", "-o", filepath, url],
        capture_output=True, text=True
    )
    return result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 500


def parse_candidates(html):
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for box in soup.select(".cand-box"):
        img = box.select_one("figure img")
        h5 = box.select_one(".nme-prty h5")
        h6 = box.select_one(".nme-prty h6")
        if not h5:
            continue
        photo_url = img["src"] if img and img.get("src") else ""
        name = h5.get_text(strip=True)
        party = h6.get_text(strip=True) if h6 else ""
        # Skip NOTA and local placeholder images
        if name == "NOTA" or not photo_url.startswith("http"):
            continue
        candidates.append({"name": name, "party": party, "photo_url": photo_url})
    return candidates


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load constituency list
    with open(CONSTITUENCY_FILE) as f:
        data = json.load(f)
    const_numbers = [r["const_no"] for r in data["results"]]

    total_downloaded = 0
    total_skipped = 0
    total_failed = 0

    for const_no in const_numbers:
        print(f"\n[{const_no}/234] Fetching constituency {const_no}...", file=sys.stderr)
        html = fetch_page(const_no)
        if not html:
            print(f"  Failed to fetch page", file=sys.stderr)
            continue

        candidates = parse_candidates(html)
        for cand in candidates:
            safe_name = sanitize_name(cand["name"])
            ext = os.path.splitext(cand["photo_url"].split("?")[0])[1] or ".jpg"
            filename = f"{const_no}_{safe_name}{ext}"
            filepath = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                total_skipped += 1
                continue

            if download_photo(cand["photo_url"], filepath):
                total_downloaded += 1
                print(f"  {filename}", file=sys.stderr)
            else:
                total_failed += 1
                print(f"  FAILED: {filename}", file=sys.stderr)

        # Small delay to be polite
        time.sleep(0.3)

    print(f"\nDone: {total_downloaded} downloaded, {total_skipped} skipped (existing), {total_failed} failed", file=sys.stderr)
    print(f"Photos saved to: {OUTPUT_DIR}/", file=sys.stderr)


if __name__ == "__main__":
    main()
