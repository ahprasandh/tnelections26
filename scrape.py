#!/usr/bin/env python3
"""Scrape TN 2026 election results from ECI website and output JSON."""

import json
import os
import re
import subprocess
import sys
from bs4 import BeautifulSoup

BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/statewiseS22{}.htm"
PAGES = range(1, 13)  # Pages 1 through 12


def fetch_page(page_num):
    url = BASE_URL.format(page_num)
    print(f"Fetching page {page_num}: {url}", file=sys.stderr)
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "30", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  curl failed for page {page_num}: {result.stderr}", file=sys.stderr)
        return ""
    return result.stdout


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    table = soup.select_one("table.table-striped.table-bordered")
    if not table:
        return results

    tbody = table.find("tbody")
    if not tbody:
        return results

    for row in tbody.find_all("tr", recursive=False):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 9:
            continue

        constituency = cells[0].get_text(strip=True)
        const_no = cells[1].get_text(strip=True)

        # Leading candidate name
        leading_candidate = cells[2].get_text(strip=True)

        # Leading party - nested table, get first td text
        leading_party_td = cells[3]
        leading_party_inner = leading_party_td.find("td", align="left")
        leading_party = leading_party_inner.get_text(strip=True) if leading_party_inner else ""

        # Trailing candidate name
        trailing_candidate = cells[4].get_text(strip=True)

        # Trailing party - nested table
        trailing_party_td = cells[5]
        trailing_party_inner = trailing_party_td.find("td", align="left")
        trailing_party = trailing_party_inner.get_text(strip=True) if trailing_party_inner else ""

        margin = cells[6].get_text(strip=True)
        round_no = cells[7].get_text(strip=True)
        status = cells[8].get_text(strip=True)

        results.append({
            "constituency": constituency,
            "const_no": int(const_no) if const_no.isdigit() else const_no,
            "leading_candidate": leading_candidate,
            "leading_party": leading_party,
            "trailing_candidate": trailing_candidate,
            "trailing_party": trailing_party,
            "margin": margin,
            "round": round_no,
            "status": status,
        })

    return results


def parse_summary(html):
    """Parse the summary header: 'Status Known For X out of Y Constituencies'."""
    soup = BeautifulSoup(html, "html.parser")
    th = soup.find("th", colspan="9")
    if th:
        return th.get_text(strip=True)
    return ""


def parse_last_updated(html):
    """Parse the 'Last Updated at ...' footer."""
    soup = BeautifulSoup(html, "html.parser")
    foot = soup.select_one(".foot-content")
    if foot:
        return foot.get_text(strip=True)
    return ""


def main():
    all_results = []

    # Fetch first page to get summary info
    first_html = fetch_page(1)
    summary = parse_summary(first_html)
    last_updated = parse_last_updated(first_html)
    all_results.extend(parse_page(first_html))

    # Fetch remaining pages
    for page_num in range(2, 13):
        html = fetch_page(page_num)
        all_results.extend(parse_page(html))

    # Sort by constituency number
    all_results.sort(key=lambda x: x["const_no"] if isinstance(x["const_no"], int) else 0)

    output = {
        "summary": summary,
        "last_updated": last_updated,
        "total_constituencies": len(all_results),
        "results": all_results,
    }

    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline
    print(f"Total constituencies scraped: {len(all_results)}", file=sys.stderr)


if __name__ == "__main__":
    main()
