#!/usr/bin/env python3
"""Build the Salama platform from tools/instrument.py.

Outputs
  web/index.html          respondent app (installable on a phone, works offline)
  web/console.html        nurse queue, service metrics, early warning and research exports
  database/02_views.sql   flat, jamovi-ready views generated from the instrument
  docs/codebook.csv       every variable, label, measure type and value labels
"""
import csv, io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import instrument as I  # noqa: E402

VIEW = {"baseline_personnel": "v_baseline_personnel", "baseline_family": "v_baseline_family", "checkin": "v_checkin",
        "pulse": "v_pulse", "informant": "v_informant", "usability_end": "v_usability_end",
        "student_screen": "v_student_screen", "delphi": "v_delphi"}
META = [("response_id", "Response ID", "nominal"), ("submitted_at", "Date and time submitted", "scale"),
        ("grp", "Respondent group", "nominal"), ("wave", "Wave", "nominal"), ("context", "Check-in context", "nominal"),
        ("unit_code", "Unit group code", "nominal"), ("anon_code", "Private code (links baseline, check-ins, pulses, feedback)", "nominal"),
        ("protocol_version", "Protocol version live when collected", "nominal"),
        ("risk_level", "Risk level shown by the app (0 low, 1 moderate, 2 high)", "ordinal"),
        ("zone", "Wellness zone shown by the app (1 green, 2 yellow, 3 orange, 4 red)", "ordinal")]
META_VALUES = {"risk_level": [(0, "Low"), (1, "Moderate"), (2, "High")],
               "zone": [(1, "Coping well"), (2, "Feeling the strain"), (3, "Struggling"), (4, "Needs care now")]}


def form_items(k):
    return [it for s in I.FORMS[k]["sections"] for it in s["items"]]


def flat_items(k):
    return [it for it in form_items(k) if it["type"] != "text"]


def derived_cols(k):
    ids = {i["id"] for i in form_items(k)}
    out = [s for s, d in I.SCALES.items() if all(x in ids for x in d["items"])]
    if k in ("checkin", "student_screen"):
        out += ["phq9_short", "gad7_short", "phq9_pos", "gad7_pos", "ptsd5_pos", "auditc_pos"]
    if k == "checkin":
        out += ["lifestress_high"]
    if "fm_borrow" in ids:
        out += ["fm_informal", "fm_security_any", "fm_strain"]
    if any(i.startswith("sr_") and i != "sr_text" for i in ids):
        out += ["sr_count"]
    if k == "pulse":
        out += ["pl_poor_sleep", "pl_high_stress", "pl_money_worry"]
    return out


DERIVED_LABEL = {**{k: v["label"] for k, v in I.SCALES.items()},
                 "phq9_short": "PHQ-9 answered as adaptive short form (1 = items 3 to 8 not asked, scored 0)",
                 "gad7_short": "GAD-7 answered as adaptive short form (1 = items 3 to 7 not asked, scored 0)",
                 "phq9_pos": "PHQ-9 screen positive (total 10 or more)", "gad7_pos": "GAD-7 screen positive (total 10 or more)",
                 "ptsd5_pos": "PC-PTSD-5 screen positive (total 3 or more)", "auditc_pos": "AUDIT-C above low risk (total 4 or more)",
                 "lifestress_high": "High life-pressure load (total 8 or more)",
                 "fm_informal": "Borrowed from an informal lender in last 3 months (1 yes, 0 no, blank = not answered or prefer not to say)",
                 "fm_security_any": "A lender held at least one item as security (1 yes, 0 no)",
                 "fm_strain": "Money strain: ran out of money several times or more than a quarter of pay on repayments (1 yes, 0 no)",
                 "sr_count": "Number of stressors ticked (0 to 3)",
                 "pl_poor_sleep": "Poor or very poor sleep this week", "pl_high_stress": "Very or extremely stressed this week",
                 "pl_money_worry": "Quite a lot or very worried about money or debt this week"}
BINARY = {"phq9_short", "gad7_short", "phq9_pos", "gad7_pos", "ptsd5_pos", "auditc_pos", "lifestress_high", "fm_informal",
          "fm_security_any", "fm_strain", "pl_poor_sleep", "pl_high_stress", "pl_money_worry"}


def nn(items):
    return " and ".join("t.%s is not null" % x for x in items)


def short_expr(sc):
    d = I.SCALES[sc]; gated = [x for x in d["items"] if x not in d["short"]]
    return "case when %s then (case when %s then 1 else 0 end) end" % (nn(d["short"]), " and ".join("t.%s is null" % x for x in gated))


def total_expr(sc):
    d = I.SCALES[sc]; full = " + ".join("t.%s" % x for x in d["items"])
    if d.get("rev"):
        full = " + ".join(("(6 - t.%s)" if x in d["rev"] else "t.%s") % x for x in d["items"])
    if d.get("short"):
        sh = " + ".join("t.%s" % x for x in d["short"])
        return "case when (%s) = 1 then %s when %s then %s end" % (short_expr(sc), sh, nn(d["items"]), full)
    if d.get("sus"):
        parts = [("(t.%s - 1)" if (n % 2 == 1) else "(5 - t.%s)") % it for n, it in enumerate(d["items"], 1)]
        return "case when %s then (%s) * 2.5 end" % (nn(d["items"]), " + ".join(parts))
    if d.get("zero_if"):
        g, v = d["zero_if"]
        return "case when t.%s = %d then 0 when %s then %s end" % (g, v, nn(d["items"]), full)
    return "case when %s then %s end" % (nn(d["items"]), full)


def derived_expr(col, k="checkin"):
    if col in ("phq9_short", "gad7_short"):
        return short_expr("phq9" if col.startswith("phq") else "gad7")
    if col in I.SCALES:
        return total_expr(col)
    base = {"phq9_pos": ("phq9", ">= 10"), "gad7_pos": ("gad7", ">= 10"), "ptsd5_pos": ("ptsd5", ">= 3"),
            "auditc_pos": ("auditc", ">= 4"), "lifestress_high": ("lifestress", ">= 8")}
    if col in base:
        e = total_expr(base[col][0])
        return "case when (%s) is null then null when (%s) %s then 1 else 0 end" % (e, e, base[col][1])
    if col == "fm_informal":
        return "case when t.fm_borrow in (1,2) then 1 when t.fm_borrow = 0 then 0 end"
    if col == "fm_security_any":
        s = "coalesce(t.sec_atm,0) + coalesce(t.sec_phone,0) + coalesce(t.sec_id,0) + coalesce(t.sec_doc,0) + coalesce(t.sec_item,0)"
        return "case when t.fm_borrow in (1,2) then (case when %s > 0 then 1 else 0 end) when t.fm_borrow = 0 then 0 end" % s
    if col == "fm_strain":
        return ("case when t.fm_needs is null and (t.fm_share is null or t.fm_share = 9) then null "
                "when coalesce(t.fm_needs,0) >= 2 or coalesce(t.fm_share,0) between 2 and 3 then 1 else 0 end")
    if col == "sr_count":
        ids = [i["id"] for i in form_items(k) if i["id"].startswith("sr_") and i["type"] == "check"]
        return "case when %s then %s end" % (" or ".join("t.%s is not null" % x for x in ids), " + ".join("coalesce(t.%s,0)" % x for x in ids))
    if col == "pl_poor_sleep":
        return "case when t.pl_sleep is null then null when t.pl_sleep >= 3 then 1 else 0 end"
    if col == "pl_high_stress":
        return "case when t.pl_stress is null then null when t.pl_stress >= 4 then 1 else 0 end"
    if col == "pl_money_worry":
        return "case when t.pl_money is null then null when t.pl_money >= 3 then 1 else 0 end"
    raise KeyError(col)


def views_sql():
    out = ["-- GENERATED by tools/build.py from tools/instrument.py. Do not edit by hand.",
           "-- Flat, numeric-coded views ready to export to CSV and open in jamovi. Free text is in v_free_text.",
           "-- Each view runs with the caller's rights (security_invoker), so only researchers and admins see rows.", ""]
    out.append("drop view if exists public.v_free_text;")
    for k, view in VIEW.items():
        cols = ["r.id as response_id", "coalesce(r.client_time, r.created_at) as submitted_at", "r.grp", "r.wave", "r.context",
                "r.unit_code", "r.anon_code", "r.protocol_version", "r.risk_level", "r.zone"]
        for it in flat_items(k):
            cols.append("(r.answers->>'%s')::int as %s" % (it["id"], it["id"]))
        outer = ["t.*"] + ["%s as %s" % (derived_expr(c, k), c) for c in derived_cols(k)]
        out.append("drop view if exists public.%s cascade;" % view)
        out.append("create view public.%s with (security_invoker = true) as\nselect\n  %s\nfrom (\n  select\n    %s\n  from public.responses r\n  where r.form = '%s'\n) t;"
                   % (view, ",\n  ".join(outer), ",\n    ".join(cols), k))
        out.append("revoke all on public.%s from anon, authenticated, public;" % view)
        out.append("grant select on public.%s to authenticated;\n" % view)
    parts = []
    for k in VIEW:
        for it in form_items(k):
            if it["type"] == "text":
                parts.append("select r.id as response_id, coalesce(r.client_time, r.created_at) as submitted_at, r.form, r.grp, r.unit_code, r.protocol_version, "
                             "'%s'::text as item_id, r.answers->>'%s' as response_text from public.responses r where r.form = '%s' and coalesce(r.answers->>'%s','') <> ''"
                             % (it["id"], it["id"], k, it["id"]))
    out.append("-- Free-text answers in long format, for qualitative coding. Remove any identifying detail before quoting.")
    out.append("create view public.v_free_text with (security_invoker = true) as\n" + "\nunion all\n".join(parts) + ";")
    out.append("revoke all on public.v_free_text from anon, authenticated, public;\ngrant select on public.v_free_text to authenticated;\n")
    ids = [i for _, items in I.DELPHI for i, _ in items]
    vals = ",\n      ".join("('%s', d.%s)" % (i, i) for i in ids)
    out.append("-- Delphi consensus by round: share rating 7 to 9 and median. Consensus rule in this study: 70% or more rate 7 to 9.")
    out.append("drop view if exists public.v_delphi_consensus;")
    out.append("create view public.v_delphi_consensus with (security_invoker = true) as\nselect d.dl_round as round, s.statement, count(s.score) as ratings,\n       round(100.0 * avg(case when s.score >= 7 then 1 else 0 end) filter (where s.score is not null), 1) as pct_7_to_9,\n       (percentile_cont(0.5) within group (order by s.score))::numeric(4,1) as median_score,\n       (round(100.0 * avg(case when s.score >= 7 then 1 else 0 end) filter (where s.score is not null), 1) >= 70) as consensus_reached\nfrom public.v_delphi d\ncross join lateral (values\n      %s\n    ) as s(statement, score)\ngroup by 1, 2;" % vals)
    out.append("revoke all on public.v_delphi_consensus from anon, authenticated, public;\ngrant select on public.v_delphi_consensus to authenticated;\n")
    out.append("-- Stressors people tick themselves, by unit and month (units with fewer than 10 people that month are hidden).")
    out.append("drop view if exists public.v_stressor_monthly;")
    vals = ",\n      ".join("('%s', c.sr_%s)" % (lab.replace("'", "''"), k) for k, lab in I.STRESSORS)
    out.append("create view public.v_stressor_monthly with (security_invoker = true) as\n"
               "select coalesce(c.unit_code,'none') as unit_code, date_trunc('month', c.submitted_at)::date as month, s.stressor,\n"
               "       count(distinct c.anon_code) filter (where s.ticked = 1) as people_ticking, count(*) filter (where s.ticked = 1) as times_ticked,\n"
               "       round(100.0 * avg(s.ticked), 1) as pct_of_checkins\n"
               "from public.v_checkin c\n"
               "cross join lateral (values\n      %s\n    ) as s(stressor, ticked)\n"
               "where c.sr_money is not null\n"
               "group by 1, 2, 3\n"
               "having count(distinct c.anon_code) >= 10;" % vals)
    out.append("revoke all on public.v_stressor_monthly from anon, authenticated, public;\ngrant select on public.v_stressor_monthly to authenticated;\n")
    return "\n".join(out)


def codebook_rows():
    rows = []
    for k in VIEW:
        for c, lab, m in META:
            vals = "; ".join("%s=%s" % (a, b) for a, b in META_VALUES.get(c, []))
            rows.append([k, c, lab, m, vals, "", "meta", ""])
        for it in form_items(k):
            vals = "; ".join("%s=%s" % (a, b) for a, b in it["options"]) if it["type"] == "choice" else ("1=Ticked; 0=Not ticked" if it["type"] == "check" else "(free text, see v_free_text)")
            q = it["text"] + (" [%s]" % it["group"] if it.get("group") else "")
            note = []
            if it["show_if"]:
                note.append("asked only if %s in %s" % (it["show_if"][0], it["show_if"][1]))
            if it.get("gate"):
                note.append("adaptive: asked only if %s add to %d or more" % ("+".join(it["gate"][0]), it["gate"][1]))
            if it.get("sensitive"):
                note.append("sensitive item, can be switched off in web/config.js")
            if it["type"] == "text":
                note.append("not in the flat view")
            rows.append([k, it["id"], it["label"], it["measure"], vals, q, "item" if it["type"] != "text" else "text", "; ".join(note)])
        for c in derived_cols(k):
            m = "nominal" if c in BINARY else "scale"
            rows.append([k, c, DERIVED_LABEL[c], m, "1=Yes; 0=No" if c in BINARY else "", "", "derived", "calculated in the database view"])
    return rows


def main():
    instr = {k: dict(title=v["title"], minutes=v["minutes"], groups=v["groups"], sections=v["sections"]) for k, v in I.FORMS.items()}
    inject = "const INSTRUMENT = %s;\nconst SCALES = %s;\nconst CONTENT = %s;" % (
        json.dumps(instr, ensure_ascii=False), json.dumps(I.SCALES, ensure_ascii=False), json.dumps(I.CONTENT, ensure_ascii=False))
    shared = open(os.path.join(ROOT, "tools", "shared.js"), encoding="utf-8").read()
    buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n")
    w.writerow(["form", "variable", "label", "measure", "values", "question_text", "kind", "note"]); w.writerows(codebook_rows())
    codebook = buf.getvalue()
    for src, dst in (("app_template.html", "index.html"), ("console_template.html", "console.html"), ("portal_template.html", "portal.html")):
        p = os.path.join(ROOT, "tools", src)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        t = t.replace("/*__INJECT__*/", inject).replace("/*__SHARED__*/", shared).replace('/*__CODEBOOK__*/""', json.dumps(codebook, ensure_ascii=False))
        open(os.path.join(ROOT, "web", dst), "w", encoding="utf-8").write(t)
    sys.path.insert(0, os.path.join(ROOT, "tools", "i18n"))
    import build_dict
    js, d = build_dict.build()
    open(os.path.join(ROOT, "web", "lang_sw.js"), "w", encoding="utf-8").write(js)
    open(os.path.join(ROOT, "web", "lang.js"), "w", encoding="utf-8").write(open(os.path.join(ROOT, "tools", "lang.js"), encoding="utf-8").read())
    import shutil; shutil.copy(os.path.join(ROOT, "tools", "vendor", "qrcode.js"), os.path.join(ROOT, "web", "qrcode.js"))
    print("kiswahili dictionary:", len(d), "entries")
    open(os.path.join(ROOT, "database", "02_views.sql"), "w", encoding="utf-8").write(views_sql())
    open(os.path.join(ROOT, "docs", "codebook.csv"), "w", encoding="utf-8-sig", newline="").write(codebook)
    print("built; items per form:", {k: len(form_items(k)) for k in VIEW}, "| codebook rows:", len(codebook_rows()))


if __name__ == "__main__":
    main()
