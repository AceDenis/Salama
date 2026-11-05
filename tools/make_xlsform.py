"""Generate KoboToolbox / ODK XLSForm files from instrument.py (the same questions as the app).
Usage: python3 make_xlsform.py [outdir]   -> one .xlsx per questionnaire; import each into KoboToolbox (free)."""
import sys, os, re
from openpyxl import Workbook
import instrument as I, pack_text as P

OUT = sys.argv[1] if len(sys.argv) > 1 else "../kobo"
os.makedirs(OUT, exist_ok=True)

CORE = ["student_screen", "checkin", "pulse", "usability_end"]       # forms used in this study
INFO = {  # which consent sheet goes with which form
 "student_screen": "student", "baseline_personnel": "personnel", "baseline_family": "family", "checkin": "student",
 "pulse": "student", "usability_end": "student", "informant": "informant", "delphi": "informant"}

def clean(t): return re.sub(r"\*\*", "", t or "")
def num(q): return f"if(${{{q}}}='',0,number(${{{q}}}))"

def build(form_key, family=False):
    f = I.FORMS[form_key]; cons = P.CONSENTS[INFO[form_key] if not (family and form_key == "checkin") else "family"]
    items = {it["id"]: it for s in f["sections"] for it in s["items"]}
    survey, choices, lists, gm = [], [], {}, {}
    def listname(opts):
        key = tuple((str(v), l) for v, l in opts)
        if key not in lists:
            ln = f"l{len(lists)+1}"; lists[key] = ln
            for v, l in key: choices.append([ln, v, l])
        return lists[key]
    R = lambda **k: survey.append([k.get(c, "") for c in ("type", "name", "label", "hint", "required", "relevant", "appearance", "constraint", "constraint_message", "calculation")])
    R(type="start", name="start"); R(type="end", name="end")
    R(type="begin_group", name="g_info", label="About this questionnaire")
    R(type="note", name="n_title", label=f["title"])
    if INFO[form_key] == "student":
        R(type="note", name="n_protect", label="YOUR PROTECTIONS. " + " ".join(f"{i}. {h} {t}" for i, (h, t) in enumerate(P.PROTECTIONS, 1)))
    R(type="note", name="n_who", label=clean(cons["who"]) + " It takes about %d minutes." % f["minutes"])
    for i, (h, paras) in enumerate(cons["sections"]):
        R(type="note", name=f"n_info{i}", label=clean(h) + ": " + " ".join(clean(x) for x in paras)[:1400])
    R(type="note", name="n_noname", label="Do not type your name, service number or phone number anywhere in this form.")
    R(type="end_group", name="g_info_end")
    R(type="select_one yn", name="consent", label=" / ".join(clean(x) for x in cons["statements"][:1] + cons["statements"][2:4])[:600] or "I agree to take part.", required="yes")
    R(type="text", name="prev_code", label="If you have answered before, type your private code from last time. If this is your first time, leave this blank.", required="no", relevant="${consent}='1'")
    R(type="begin_group", name="g_all", label="Questions", relevant="${consent}='1'")
    for s in f["sections"]:
        gname = "g_" + s["id"] if s["id"] in items else s["id"]
        R(type="begin_group", name=gname, label=s["title"])
        if s.get("intro"): R(type="note", name="n_" + s["id"], label=clean(s["intro"]))
        blocks = []
        for it in s["items"]:
            if it["type"] == "check" and blocks and blocks[-1][0] == "grp" and blocks[-1][1][0]["group"] == it["group"]: blocks[-1][1].append(it)
            elif it["type"] == "check": blocks.append(("grp", [it]))
            else: blocks.append(("q", [it]))
        for kind, its in blocks:
            it = its[0]; q = it["id"] if kind == "q" else "grp_" + it["id"]; gm[it["id"]] = q
            for g in its: gm[g["id"]] = q
            text = (it.get("text_family") if family and it.get("text_family") else it["text"])
            if kind == "grp": text = it["group"] or it["text"]
            def refx(rid, vals):
                ri = items[rid]
                if ri["type"] == "check": return "(" + " or ".join(f"selected(${{{gm[rid]}}},'{rid}')" for v in vals if str(v) == "1") + ")"
                return "(" + " or ".join(f"${{{rid}}}='{v}'" for v in vals) + ")"
            rel = []
            if it.get("show_if"):
                rid, vals = it["show_if"]
                if rid in items: rel.append(refx(rid, vals))
            if it.get("gate"):
                ids, thr = it["gate"]; rel.append("(" + " + ".join(num(x) for x in ids) + f" >= {thr})")
            hint = "Optional. You may skip this question." if it.get("optional") or it.get("sensitive") else ""
            if it["type"] == "text":
                R(type="text", name=q, label=clean(text), hint=hint, required="no", relevant=" and ".join(rel), appearance="multiline")
            elif kind == "grp":
                ln = f"g{len(lists)+1}"; lists[(ln,)] = ln
                for g in its: choices.append([ln, g["id"], g["text"]])
                mx = it.get("max_checks"); con = f"count-selected(.)<={mx}" if mx else ""
                h2 = ("" if mx or "tick" in text.lower() else "Tick all that apply. ") + hint
                R(type=f"select_multiple {ln}", name=q, label=clean(text), hint=h2.strip(), required="no", relevant=" and ".join(rel), constraint=con, constraint_message=("Please choose no more than %s." % mx) if mx else "")
            else:
                ln = listname(it["options"])
                R(type=f"select_one {ln}", name=q, label=clean(text), hint=hint, required="no" if (it.get("optional") or it.get("sensitive")) else "yes", relevant=" and ".join(rel))
        R(type="end_group", name=gname + "_end")
    R(type="end_group", name="g_all_end")
    R(type="calculate", name="pcode", calculation="once(concat('K-', substr(uuid(), 1, 8)))", relevant="")
    R(type="note", name="n_done", label="Thank you. Your private code is ${pcode}. Write it down only if you want to answer again later. It is not your name. If you feel unsafe, call 999 or 112, or the gender violence helpline 1195. Help numbers: ask your unit nurse or welfare officer.", relevant="${consent}='1'")
    choices.insert(0, ["yn", "1", "Yes, I agree"]); choices.insert(1, ["yn", "0", "No, I do not agree"])
    wb = Workbook(); ws = wb.active; ws.title = "survey"
    ws.append(["type", "name", "label", "hint", "required", "relevant", "appearance", "constraint", "constraint_message", "calculation"])
    for r in survey: ws.append(r)
    wc = wb.create_sheet("choices"); wc.append(["list_name", "name", "label"]); [wc.append(r) for r in choices]
    wsx = wb.create_sheet("settings"); wsx.append(["form_title", "form_id", "version", "default_language"])
    fid = "salama_" + form_key + ("_family" if family else ""); wsx.append([f["title"] + (" (family wording)" if family else ""), fid, "1", "English (en)"])
    path = os.path.join(OUT, fid + ".xlsx"); wb.save(path); return path, len(survey)

out = []
for k in I.FORMS:
    later = k not in CORE
    OUTD = os.path.join(OUT, "later_phases") if later else OUT
    os.makedirs(OUTD, exist_ok=True)
    globals()["OUT"] = OUTD
    out.append(build(k))
    if k == "checkin": pass
    globals()["OUT"] = sys.argv[1] if len(sys.argv) > 1 else "../kobo"
for p, n in out: print(os.path.relpath(p, os.path.dirname(OUT) or "."), n, "rows")
