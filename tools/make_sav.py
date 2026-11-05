#!/usr/bin/env python3
"""Turn an exported CSV into an SPSS .sav file that jamovi opens WITH variable labels, value labels and measure types.
Usage: python3 tools/make_sav.py exported.csv student_screen [out.sav]
       (second argument = the form the file came from: checkin, pulse, student_screen, informant, usability_end,
        baseline_personnel, baseline_family; or one of: student_outcomes, student_paired)
Needs:  pip install pandas pyreadstat"""
import csv, os, re, sys
import pandas as pd, pyreadstat
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path, form = sys.argv[1], sys.argv[2]; out = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(csv_path)[0] + ".sav"
base_form = "student_screen" if form.startswith("student_") else form
cb = {}
for r in csv.DictReader(open(os.path.join(ROOT, "docs", "codebook.csv"), encoding="utf-8-sig")):
    if r["form"] == base_form: cb[r["variable"]] = r
EXTRA = {"intake": ("Intake month (YYYY-MM)", "nominal", ""), "outcome_status": ("Outcome status at follow-up", "nominal", "1=Enrolled and continuing; 2=Completed the period; 3=Deferred; 4=Withdrew; 5=Discontinued; 6=Not admitted"),
         "exit_month": ("Months after start when the person left", "scale", ""), "exit_reason": ("Broad reason for leaving", "nominal", "1=Mental health; 2=Other health; 3=Money or fees; 4=Family; 5=Academic; 6=Discipline; 7=Changed plans; 9=Unknown or not stated"),
         "attrition": ("Left the programme (deferred, withdrew or discontinued)", "nominal", "1=Left; 0=Stayed or completed"), "month": ("Month", "nominal", ""), "people": ("People in group", "scale", "")}
for k in ("phq9", "gad7", "auditc", "brs", "stakes"):
    for suf, lab in (("t1", "at first check"), ("t2", "at latest later check"), ("change", "change (later minus first)")):
        EXTRA["%s_%s" % (k, suf)] = ("%s %s" % ({"phq9": "PHQ-9", "gad7": "GAD-7", "auditc": "AUDIT-C", "brs": "Resilience (BRS sum)", "stakes": "Perceived consequences"}[k], lab), "scale", "")
for k, lab in (("borrow", "Informal borrowing"), ("strain", "Money strain"), ("honest", "Answered honestly (1-5)"), ("zone", "Wellness zone")):
    for suf in ("t1", "t2"): EXTRA["%s_%s" % (k, suf)] = ("%s, %s" % (lab, suf), "ordinal" if k in ("honest", "zone") else "nominal", "1=Yes; 0=No" if k in ("borrow", "strain") else "")
df = pd.read_csv(csv_path, encoding="utf-8-sig")
labels, values, measure = {}, {}, {}
for c in df.columns:
    info = cb.get(c); 
    if info: lab, m, vals = info["label"], info["measure"], info["values"]
    elif c in EXTRA: lab, m, vals = EXTRA[c]
    else: lab, m, vals = c, "nominal", ""
    labels[c] = lab[:250]; measure[c] = {"nominal": "nominal", "ordinal": "ordinal", "scale": "scale"}.get(m, "nominal")
    d = {}
    for part in [x for x in vals.split("; ") if "=" in x]:
        k, v = part.split("=", 1)
        try: d[float(k)] = v
        except ValueError: pass
    if d and not (c in ("submitted_at",)): values[c] = d
    if c in ("response_id", "submitted_at", "anon_code", "unit_code", "grp", "wave", "context", "protocol_version", "intake") : df[c] = df[c].astype(str)
pyreadstat.write_sav(df, out, column_labels=[labels[c] for c in df.columns], variable_value_labels=values, variable_measure=measure)
print("wrote", out, "-", len(df), "rows,", len(df.columns), "variables,", len(values), "with value labels")
