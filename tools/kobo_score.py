#!/usr/bin/env python3
"""Add scale totals to a KoboToolbox CSV export so it can be opened in jamovi.
Usage: python3 kobo_score.py kobo_export.csv scored.csv
Export from Kobo with: CSV, 'Show choices as XML values' (numbers), group names removed.
Adds: phq9, gad7, ptsd5, auditc, lifestress, lifestress_a, brs, sus, stakes (where the columns exist) and phq9_pos, gad7_pos, ptsd5_pos, auditc_pos.
Adaptive short forms: if the later PHQ-9/GAD-7 items were skipped by design, phq9/gad7 hold the short total (items 1, 2 and 9 for the PHQ; items 1 and 2 for the GAD) and phq9_short/gad7_short = 1. This is the same rule the app and database use."""
import csv, sys
import instrument as I
src, dst = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
if not rows: sys.exit("empty file")
def clean(h): return h.split("/")[-1].strip()
rows = [{clean(k): v for k, v in r.items()} for r in rows]
def val(r, k):
    v = (r.get(k) or "").strip()
    try: return float(v)
    except ValueError: return None
add = []
for r in rows:
    out = {}
    for sc, d in I.SCALES.items():
        items = d["items"]
        if not all(i in r for i in items): continue
        v = [val(r, i) for i in items]
        z = d.get("zero_if")
        if z and z[0] in r and val(r, z[0]) == z[1]: out[sc] = 0; continue
        if all(x is not None for x in v):
            if d.get("sus"): out[sc] = sum((x - 1) if n % 2 else (5 - x) for n, x in enumerate(v, 1)) * 2.5
            else: out[sc] = sum((6 - x) if x_id in d.get("rev", []) else x for x_id, x in zip(items, v))
        elif d.get("short") and all(val(r, i) is not None for i in d["short"]):
            out[sc] = sum(val(r, i) for i in d["short"]); out[sc + "_short"] = 1
    for sc, cut in (("phq9", 10), ("gad7", 10), ("ptsd5", 3), ("auditc", 4)):
        t = out.get(sc)
        if t is not None: out[sc + "_pos"] = 1 if t >= cut else 0
    add.append(out)
cols = list(rows[0]); extra = sorted({k for a in add for k in a} - set(cols))
with open(dst, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols + extra); w.writeheader()
    for r, a in zip(rows, add): w.writerow({**r, **a})
print("wrote", dst, "added", extra)
