#!/usr/bin/env python3
"""Scrape TN 2026 party-wise election results from ECI website and output JSON."""

import json
import subprocess
import sys
from bs4 import BeautifulSoup

URL = "https://results.eci.gov.in/ResultAcGenMay2026/partywiseresult-S22.htm"


def fetch_page():
    print(f"Fetching: {URL}", file=sys.stderr)
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "30", URL],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_party_table(html):
    """Parse the 'Party Wise Results' table: Party, Won, Leading, Total."""
    soup = BeautifulSoup(html, "html.parser")
    parties = []

    # Find the card with "Party Wise Results" header
    for card in soup.select(".card.custom-card"):
        header = card.select_one(".card-header")
        if not header:
            continue
        header_text = header.get_text(strip=True)
        if "Party Wise Results" not in header_text:
            continue

        table = card.select_one("table.table")
        if not table:
            continue

        tbody = table.find("tbody")
        if not tbody:
            continue

        for row in tbody.find_all("tr", class_="tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            party_text = cells[0].get_text(strip=True)
            # Split "Full Name - ABBR" format
            if " - " in party_text:
                party_name, party_abbr = party_text.rsplit(" - ", 1)
            else:
                party_name = party_text
                party_abbr = party_text

            won = cells[1].get_text(strip=True)
            leading = cells[2].get_text(strip=True)
            total = cells[3].get_text(strip=True)

            parties.append({
                "party": party_abbr.strip(),
                "party_name": party_name.strip(),
                "won": int(won) if won.isdigit() else 0,
                "leading": int(leading) if leading.isdigit() else 0,
                "total": int(total) if total.isdigit() else 0,
            })

        # Parse footer totals
        tfoot = table.find("tfoot")
        if tfoot:
            th_cells = tfoot.find_all("th")
            if len(th_cells) >= 4:
                total_won = th_cells[1].get_text(strip=True)
                total_leading = th_cells[2].get_text(strip=True)
                total_total = th_cells[3].get_text(strip=True)
                return parties, {
                    "won": int(total_won) if total_won.isdigit() else 0,
                    "leading": int(total_leading) if total_leading.isdigit() else 0,
                    "total": int(total_total) if total_total.isdigit() else 0,
                }

        break

    return parties, {}


def parse_last_updated(html):
    soup = BeautifulSoup(html, "html.parser")
    foot = soup.select_one(".foot-content")
    if foot:
        return foot.get_text(strip=True)
    return ""


def main():
    html = fetch_page()
    parties, totals = parse_party_table(html)
    last_updated = parse_last_updated(html)

    # Sort by total seats descending
    parties.sort(key=lambda x: x["total"], reverse=True)

    output = {
        "last_updated": last_updated,
        "totals": totals,
        "parties": parties,
    }

    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    print()
    print(f"Total parties scraped: {len(parties)}", file=sys.stderr)


if __name__ == "__main__":
    main()
