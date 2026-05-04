#!/usr/bin/env python3
"""Download party flags and election symbols from Wikipedia into images/ folder."""

import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")

# All known image URLs mapped by party abbreviation
# Sources: https://en.wikipedia.org/wiki/List_of_political_parties_in_Tamil_Nadu
#          https://en.wikipedia.org/wiki/Tamilaga_Vettri_Kazhagam (for TVK)
#          Individual party Wikipedia pages for missing items
PARTY_IMAGES = {
    "TVK": {
        "flag": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Tamilaga_Vettri_Kazhagam_Flag.jpeg/200px-Tamilaga_Vettri_Kazhagam_Flag.jpeg",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Indian_Election_Symbol_Whistle.png/200px-Indian_Election_Symbol_Whistle.png",
    },
    "ADMK": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/AIADMK_Flag.svg/200px-AIADMK_Flag.svg.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Indian_election_symbol_two_leaves.svg/200px-Indian_election_symbol_two_leaves.svg.png",
    },
    "DMK": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Flag_DMK.svg/200px-Flag_DMK.svg.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Indian_election_symbol_rising_sun.svg/200px-Indian_election_symbol_rising_sun.svg.png",
    },
    "INC": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Indian_National_Congress_Flag.svg/200px-Indian_National_Congress_Flag.svg.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Hand_INC.svg/200px-Hand_INC.svg.png",
    },
    "BJP": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/BJP_Flag.svg/200px-BJP_Flag.svg.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Lotus_flower_symbol.svg/200px-Lotus_flower_symbol.svg.png",
    },
    "PMK": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/PMK.svg/200px-PMK.svg.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Pattali_Makkal_Katchi_Ripe_Mango_Symbol.png/200px-Pattali_Makkal_Katchi_Ripe_Mango_Symbol.png",
    },
    "CPI": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/CPI-banner.svg/200px-CPI-banner.svg.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Indian_Election_Symbol_Ears_of_Corn_and_Sickle.png/200px-Indian_Election_Symbol_Ears_of_Corn_and_Sickle.png",
    },
    "DMDK": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Flag_DMDK.png/200px-Flag_DMDK.png",
        "symbol": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Indian_Election_Symbol_Nagara.svg/200px-Indian_Election_Symbol_Nagara.svg.png",
    },
    "AMMKMNKZ": {
        # No flag/symbol available on Wikipedia
    },
    "PT": {
        "flag": "https://upload.wikimedia.org/wikipedia/commons/a/ac/Puthiya_Tamilagam_Party_Flag.jpg",
        # No symbol available on Wikipedia
    },
}


def get_extension(url):
    """Extract file extension from URL."""
    # Get the filename part after the last /
    filename = url.split("/")[-1].split("?")[0]
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"):
        return ext
    return ".png"


def download_image(url, filepath):
    """Download an image using curl."""
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "30",
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
         "-o", filepath, url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr}", file=sys.stderr)
        return False
    # Check file size
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return True
    print(f"  FAILED: empty file", file=sys.stderr)
    return False


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    success = 0
    failed = 0
    skipped = 0

    for party, images in PARTY_IMAGES.items():
        for img_type in ("flag", "symbol"):
            url = images.get(img_type)
            if not url:
                print(f"  {party}_{img_type}: no URL available, skipping")
                skipped += 1
                continue

            ext = get_extension(url)
            filename = f"{party}_{img_type}{ext}"
            filepath = os.path.join(IMAGES_DIR, filename)

            print(f"  Downloading {filename}...", end=" ")
            if download_image(url, filepath):
                size = os.path.getsize(filepath)
                print(f"OK ({size:,} bytes)")
                success += 1
            else:
                print("FAILED")
                failed += 1

    print(f"\nDone: {success} downloaded, {failed} failed, {skipped} skipped (no URL)")
    print(f"Images saved to: {IMAGES_DIR}/")


if __name__ == "__main__":
    main()
