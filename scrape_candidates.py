#!/usr/bin/env python3
"""Scrape constituency-wise candidate results from ECI table view and output JSON."""

import json
import re
import subprocess
import sys
from bs4 import BeautifulSoup

BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseS22{}.htm"
CONSTITUENCIES = range(1, 235)  # 1 through 234


def fetch_page(const_no):
    url = BASE_URL.format(const_no)
    print(f"Fetching constituency {const_no}: {url}", file=sys.stderr)
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "30", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  curl failed for constituency {const_no}: {result.stderr}", file=sys.stderr)
        return ""
    return result.stdout


def parse_constituency(html):
    soup = BeautifulSoup(html, "html.parser")

    # Constituency name and number from header
    h2 = soup.select_one("h2")
    const_name = ""
    const_no = None
    if h2:
        span = h2.find("span")
        if span:
            text = span.get_text(strip=True)
            # e.g. "61 - HARUR (Tamil Nadu)"
            m = re.match(r"(\d+)\s*-\s*(.+?)(?:\s*\(.*\))?$", text)
            if m:
                const_no = int(m.group(1))
                const_name = m.group(2).strip()

    # Round info
    round_status = ""
    round_div = soup.select_one(".round-status")
    if round_div:
        round_status = round_div.get_text(strip=True)

    # Parse the table
    candidates = []
    table = soup.select_one("table.table-striped.table-bordered")
    if table:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 7:
                continue
            sn = cells[0].get_text(strip=True)
            if not sn.isdigit():
                continue
            candidate = {
                "sn": int(sn),
                "name": cells[1].get_text(strip=True),
                "party": cells[2].get_text(strip=True),
                "evm_votes": int(cells[3].get_text(strip=True).replace(",", "") or 0),
                "postal_votes": int(cells[4].get_text(strip=True).replace(",", "") or 0),
                "total_votes": int(cells[5].get_text(strip=True).replace(",", "") or 0),
                "vote_percent": float(cells[6].get_text(strip=True) or 0),
            }
            candidates.append(candidate)

    return {
        "const_no": const_no,
        "constituency": const_name,
        "round_status": round_status,
        "candidates": candidates,
    }


def parse_last_updated(html):
    soup = BeautifulSoup(html, "html.parser")
    foot = soup.select_one(".foot-content")
    if foot:
        return foot.get_text(strip=True)
    return ""


def main():
    all_constituencies = []

    first_html = fetch_page(1)
    last_updated = parse_last_updated(first_html)
    result = parse_constituency(first_html)
    if result["const_no"] is not None:
        all_constituencies.append(result)

    for const_no in range(2, 235):
        html = fetch_page(const_no)
        if not html:
            continue
        result = parse_constituency(html)
        if result["const_no"] is not None:
            all_constituencies.append(result)

    all_constituencies.sort(key=lambda x: x["const_no"] or 0)

    output = {
        "last_updated": last_updated,
        "total_constituencies": len(all_constituencies),
        "constituencies": all_constituencies,
    }

    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    print()
    print(f"Total constituencies scraped: {len(all_constituencies)}", file=sys.stderr)


if __name__ == "__main__":
    main()
