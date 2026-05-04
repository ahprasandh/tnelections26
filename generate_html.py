#!/usr/bin/env python3
"""Generate an HTML results page from scraped JSON data."""

import json
import sys
from html import escape


def generate_html(data):
    summary = escape(data.get("summary", ""))
    last_updated = escape(data.get("last_updated", ""))
    total = data.get("total_constituencies", 0)
    results = data.get("results", [])

    # Count stats
    declared = sum(1 for r in results if r["status"] in ("Result Declared", "Won"))
    leading = {r["leading_party"] for r in results if r["leading_party"]}

    # Party-wise tally
    party_tally = {}
    for r in results:
        party = r.get("leading_party", "")
        if not party:
            continue
        status = r.get("status", "")
        if party not in party_tally:
            party_tally[party] = {"won": 0, "leading": 0, "total": 0}
        if status in ("Result Declared", "Won"):
            party_tally[party]["won"] += 1
        elif status in ("Trailing", "Leading", "Result in Progress") and r.get("leading_candidate"):
            party_tally[party]["leading"] += 1
        party_tally[party]["total"] = party_tally[party]["won"] + party_tally[party]["leading"]

    # Sort parties by total descending
    sorted_parties = sorted(party_tally.items(), key=lambda x: x[1]["total"], reverse=True)

    # Party colors
    party_colors = {
        "DMK": "#e30613",
        "AIADMK": "#00a651",
        "BJP": "#ff9933",
        "INC": "#19aaed",
        "PMK": "#ffcc00",
        "MDMK": "#8b0000",
        "TMC(M)": "#006400",
        "NTK": "#ff4500",
        "DMDK": "#ffd700",
        "IND": "#808080",
        "VCK": "#0000ff",
        "CPI": "#ff0000",
        "CPI(M)": "#cc0000",
        "AMMK": "#228b22",
    }

    def get_color(party):
        return party_colors.get(party, "#6c757d")

    # Status badge
    def status_badge(status):
        if status in ("Result Declared", "Won"):
            return f'<span class="badge bg-success">{escape(status)}</span>'
        elif status == "Leading":
            return f'<span class="badge bg-primary">{escape(status)}</span>'
        elif status == "Trailing":
            return f'<span class="badge bg-warning text-dark">{escape(status)}</span>'
        else:
            return f'<span class="badge bg-secondary">{escape(status)}</span>'

    # Build party summary rows
    party_rows = ""
    for party, counts in sorted_parties:
        color = get_color(party)
        party_rows += f"""
            <tr>
                <td><span class="party-badge" style="background:{color}">{escape(party)}</span></td>
                <td class="text-center fw-bold">{counts['won']}</td>
                <td class="text-center">{counts['leading']}</td>
                <td class="text-center fw-bold">{counts['total']}</td>
            </tr>"""

    # Build constituency rows
    const_rows = ""
    for r in results:
        lp_color = get_color(r["leading_party"]) if r["leading_party"] else "#ccc"
        tp_color = get_color(r["trailing_party"]) if r["trailing_party"] else "#ccc"

        leading_party_html = f'<span class="party-badge" style="background:{lp_color}">{escape(r["leading_party"])}</span>' if r["leading_party"] else "-"
        trailing_party_html = f'<span class="party-badge" style="background:{tp_color}">{escape(r["trailing_party"])}</span>' if r["trailing_party"] else "-"

        const_rows += f"""
            <tr>
                <td class="text-center">{r['const_no']}</td>
                <td class="fw-bold">{escape(r['constituency'])}</td>
                <td>{escape(r['leading_candidate']) or '-'}</td>
                <td>{leading_party_html}</td>
                <td>{escape(r['trailing_candidate']) or '-'}</td>
                <td>{trailing_party_html}</td>
                <td class="text-center fw-bold">{escape(r['margin'])}</td>
                <td class="text-center">{escape(r['round'])}</td>
                <td class="text-center">{status_badge(r['status'])}</td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TN Elections 2026 - Results</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 1.5rem 2rem; text-align: center; }}
        .header h1 {{ font-size: 1.6rem; margin-bottom: 0.3rem; }}
        .header p {{ opacity: 0.8; font-size: 0.9rem; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 1rem; }}
        .summary-bar {{ display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }}
        .summary-card {{ background: white; border-radius: 10px; padding: 1rem 1.5rem; flex: 1; min-width: 200px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }}
        .summary-card .number {{ font-size: 2rem; font-weight: 700; color: #1a1a2e; }}
        .summary-card .label {{ font-size: 0.85rem; color: #666; margin-top: 0.2rem; }}
        .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem; overflow: hidden; }}
        .card-header {{ padding: 1rem 1.5rem; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid #eee; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
        th {{ background: #f8f9fa; padding: 0.6rem 0.8rem; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; position: sticky; top: 0; }}
        td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee; }}
        tr:hover td {{ background: #f8f9fa; }}
        .party-badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; color: white; font-size: 0.75rem; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
        .bg-success {{ background: #28a745; color: white; }}
        .bg-primary {{ background: #007bff; color: white; }}
        .bg-warning {{ background: #ffc107; }}
        .bg-secondary {{ background: #6c757d; color: white; }}
        .text-center {{ text-align: center; }}
        .text-dark {{ color: #333; }}
        .fw-bold {{ font-weight: 600; }}
        .search-box {{ padding: 1rem 1.5rem; border-bottom: 1px solid #eee; }}
        .search-box input {{ width: 100%; padding: 0.5rem 1rem; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem; }}
        .results-scroll {{ max-height: 70vh; overflow-y: auto; }}
        .footer {{ text-align: center; padding: 1rem; color: #888; font-size: 0.8rem; }}
        @media (max-width: 768px) {{
            .summary-bar {{ flex-direction: column; }}
            table {{ font-size: 0.75rem; }}
            td, th {{ padding: 0.4rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Tamil Nadu Assembly Elections 2026</h1>
        <p>{escape(summary)} &bull; {escape(last_updated)}</p>
    </div>
    <div class="container">
        <div class="summary-bar">
            <div class="summary-card">
                <div class="number">{total}</div>
                <div class="label">Total Constituencies</div>
            </div>
            <div class="summary-card">
                <div class="number">{declared}</div>
                <div class="label">Results Declared</div>
            </div>
            <div class="summary-card">
                <div class="number">{len(sorted_parties)}</div>
                <div class="label">Parties Leading/Won</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">Party-wise Summary</div>
            <table>
                <thead>
                    <tr>
                        <th>Party</th>
                        <th class="text-center">Won</th>
                        <th class="text-center">Leading</th>
                        <th class="text-center">Total</th>
                    </tr>
                </thead>
                <tbody>{party_rows}
                </tbody>
            </table>
        </div>

        <div class="card">
            <div class="card-header">Constituency-wise Results</div>
            <div class="search-box">
                <input type="text" id="search" placeholder="Search constituency or candidate..." onkeyup="filterTable()">
            </div>
            <div class="results-scroll">
                <table id="results-table">
                    <thead>
                        <tr>
                            <th class="text-center">No.</th>
                            <th>Constituency</th>
                            <th>Leading Candidate</th>
                            <th>Leading Party</th>
                            <th>Trailing Candidate</th>
                            <th>Trailing Party</th>
                            <th class="text-center">Margin</th>
                            <th class="text-center">Round</th>
                            <th class="text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody>{const_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="footer">
        Data source: Election Commission of India &bull; {escape(last_updated)}
    </div>
    <script>
        function filterTable() {{
            const query = document.getElementById('search').value.toLowerCase();
            const rows = document.querySelectorAll('#results-table tbody tr');
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_html.py <constituencydata.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        data = json.load(f)

    print(generate_html(data))


if __name__ == "__main__":
    main()
