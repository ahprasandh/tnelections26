#!/usr/bin/env python3
"""Generate trends/index.json listing all available trend snapshots."""
import os, json, re, glob

TRENDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trends')

# Find all unique timestamps from filenames like constituencydata_2026-05-04_09-48-27.json
timestamps = set()
for f in glob.glob(os.path.join(TRENDS_DIR, 'constituencydata_*.json')):
    m = re.search(r'constituencydata_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.json', f)
    if m:
        ts = m.group(1)
        # Only include if all 3 files exist for this timestamp
        cand = os.path.join(TRENDS_DIR, f'candidatedata_{ts}.json')
        party = os.path.join(TRENDS_DIR, f'partydata_{ts}.json')
        if os.path.exists(cand) and os.path.exists(party):
            timestamps.add(ts)

# Sort reverse chronologically (latest first)
sorted_ts = sorted(timestamps, reverse=True)

# Build index with human-readable labels
entries = []
for ts in sorted_ts:
    # 2026-05-04_09-48-27 -> "09:48:27 AM" or "May 04, 09:48"
    date_part, time_part = ts.split('_')
    h, m, s = time_part.split('-')
    hour = int(h)
    ampm = 'AM' if hour < 12 else 'PM'
    h12 = hour % 12 or 12
    label = f"{date_part} {h12}:{m}:{s} {ampm}"
    entries.append({"timestamp": ts, "label": label})

index = {"snapshots": entries}
out_path = os.path.join(TRENDS_DIR, 'index.json')
with open(out_path, 'w') as f:
    json.dump(index, f, indent=2)
print(f"Wrote {len(entries)} snapshots to {out_path}")
