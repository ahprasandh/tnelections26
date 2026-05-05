#!/usr/bin/env python3
"""Scrape round-wise EVM vote data for all 234 TN constituencies from ECI.
Stores each round as rounds/{const_no}/r{N}.json"""
import subprocess, re, json, sys, time, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUNDS_DIR = os.path.join(SCRIPT_DIR, 'rounds')

def fetch(url):
    result = subprocess.run(['curl', '-sk', url], capture_output=True, text=True, timeout=30)
    return result.stdout

def parse_rounds(html, ac_no):
    """Parse all round tabs from the HTML for one constituency."""
    # Get constituency name
    name_m = re.search(r'Assembly Constituency \d+ - ([^<(]+)', html)
    const_name = name_m.group(1).strip() if name_m else f'AC {ac_no}'
    
    # Get total rounds from status line: "Status of EVM Round: 33/33"
    status_m = re.search(r'Status of EVM Round:\s*(\d+)/(\d+)', html)
    completed = int(status_m.group(1)) if status_m else 0
    total = int(status_m.group(2)) if status_m else 0
    
    # Count round buttons
    round_buttons = re.findall(r"openCity\(event, 'tab(\d+)'\)", html)
    num_rounds = len(round_buttons)
    
    # Parse each tab's table
    rounds = []
    for r in range(1, num_rounds + 1):
        # Find tab content: <div id='tabN' ...> ... </table>
        tab_pattern = rf"id='tab{r}'(.*?)</table>"
        tab_m = re.search(tab_pattern, html, re.DOTALL)
        if not tab_m:
            continue
        tab_html = tab_m.group(0)
        
        # Extract candidate rows: <td>NAME</td><td>PARTY</td><td>EVM</td><td>Postal</td><td>Total</td>
        rows = re.findall(
            r'<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*([^<]+?)\s*</td>',
            tab_html
        )
        
        candidates = []
        for name, party, evm, postal, total_votes in rows:
            name = name.strip()
            party = party.strip()
            if not name or name == '&nbsp;':
                continue
            try:
                evm_v = int(evm.strip().replace(',', ''))
            except:
                evm_v = 0
            try:
                postal_v = int(postal.strip().replace(',', ''))
            except:
                postal_v = 0
            try:
                total_v = int(total_votes.strip().replace(',', ''))
            except:
                total_v = 0
            candidates.append({
                "name": name,
                "party": party,
                "evm_votes": evm_v,
                "postal_votes": postal_v,
                "total_votes": total_v
            })
        
        if candidates:
            rounds.append({
                "round": r,
                "candidates": candidates
            })
    
    return {
        "const_no": ac_no,
        "constituency": const_name,
        "rounds_completed": completed,
        "total_rounds": total,
        "rounds": rounds
    }

# Scrape all 234 constituencies
for ac in range(1, 235):
    url = f'https://results.eci.gov.in/ResultAcGenMay2026/RoundwiseS22{ac}.htm?ac={ac}'
    sys.stderr.write(f'\rScraping AC {ac}/234...')
    sys.stderr.flush()
    try:
        html = fetch(url)
        data = parse_rounds(html, ac)
        # Create directory for this constituency
        ac_dir = os.path.join(ROUNDS_DIR, str(ac))
        os.makedirs(ac_dir, exist_ok=True)
        # Write each round as separate file
        for rd in data['rounds']:
            rfile = os.path.join(ac_dir, f'r{rd["round"]}.json')
            with open(rfile, 'w') as f:
                json.dump(rd, f, indent=2, ensure_ascii=False)
        # Write summary (without round details)
        summary = {k: v for k, v in data.items() if k != 'rounds'}
        summary['num_rounds'] = len(data['rounds'])
        with open(os.path.join(ac_dir, 'info.json'), 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        sys.stderr.write(f' -> {len(data["rounds"])} rounds')
    except Exception as e:
        sys.stderr.write(f'\n  Error AC {ac}: {e}\n')
    time.sleep(0.1)

sys.stderr.write('\nDone!\n')
