"""Build the printable Data Collection Tools Pack (docx) from instrument.py + pack_text.py.
Usage: python3 make_tools_pack.py [out.docx]"""
import sys, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import instrument as I, pack_text as P

OUT = sys.argv[1] if len(sys.argv) > 1 else "../Data_Collection_Tools_Pack.docx"
d = Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("left_margin", "right_margin"): setattr(sec, m, Cm(2.2))
sec.top_margin = sec.bottom_margin = Cm(2.0)
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(4)
for n, sz in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
    h = d.styles[n]; h.font.name = "Times New Roman"; h.font.size = Pt(sz); h.font.bold = True
    h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

def runs(p, text, size=None, italic=False):
    for i, part in enumerate(re.split(r"\*\*", text)):
        if not part: continue
        r = p.add_run(part); r.bold = bool(i % 2); r.italic = italic
        if size: r.font.size = Pt(size)
    return p
def para(text="", size=None, italic=False, align=None, after=None, indent=None):
    p = d.add_paragraph(); runs(p, text, size, italic)
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if indent: p.paragraph_format.left_indent = Cm(indent)
    return p
def bullet(text, indent=0.6):
    p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(indent + .5)
    p.paragraph_format.first_line_indent = Cm(-.5); runs(p, "•  " + text); return p
def pb(): d.add_page_break()
def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), fill); tcPr.append(s)
def table(rows, widths, header=True, size=9.5):
    t = d.add_table(rows=len(rows), cols=len(widths)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j,w in enumerate(widths): t.columns[j].width = Cm(w)
    for i, row in enumerate(rows):
        for j, txt in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ""
            runs(c.paragraphs[0], str(txt), size)
            c.paragraphs[0].paragraph_format.space_after = Pt(1)
            if header and i == 0:
                shade(c, "DCE6F1")
                for r in c.paragraphs[0].runs: r.bold = True
        if header and i == 0:
            trPr = t.rows[0]._tr.get_or_add_trPr(); e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); trPr.append(e)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t
def sigline(label):
    para(f"{label}: ______________________________    Date: ____ / ____ / ________", after=10)

# footer with page number
def footer():
    p = sec.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Salama Wellbeing Check · Data Collection Tools Pack · Page "); r.font.size = Pt(9)
    for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        run = p.add_run(); run.font.size = Pt(9)
        if t:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), t); run._r.append(f)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; run._r.append(it)
footer()

# ---------- cover ----------
for _ in range(5): para("")
para("**DATA COLLECTION TOOLS PACK**", 24, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
para("For review by the ethics committee", 14, align=WD_ALIGN_PARAGRAPH.CENTER, after=24)
para("**A confidential wellbeing check with nurse call-back and early warning for enrolled students of the Defence College of Health Sciences (DCHS), NDU-Kenya**", 13, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
para("Principal investigator: WEDAH", 12, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para("BSc Nursing with Military Health, Defence College of Health Sciences (DCHS), National Defence University-Kenya", 11, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para("Registration number: [to be added]    Supervisor: [to be added]", 11, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para("October 2026", 11, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
para("Items in [square brackets] are to be completed before submission. The questionnaires in Part B are generated from the same file that runs the phone app, so what you read here is exactly what respondents see.", 10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
pb()

# ---------- contents ----------
FORMS_ORDER = [("student_screen", "B1", "DCHS student wellbeing check", "Enrolled DCHS students, any programme and year"),
               ("checkin", "B2", "Private check-in (repeat about every four weeks)", "Enrolled DCHS students"),
               ("pulse", "B3", "Weekly pulse", "Enrolled DCHS students, weekly"),
               ("usability_end", "B4", "End-of-pilot feedback", "Students who used the service")]
para("**Contents**", 16, after=8)
for a, b in [("Part A", "Your protections (read first); information sheet and consent for students"),
             ("Part B", "Questionnaires (as shown on the phone): " + "; ".join(f"{k} {t}" for _, k, t, _ in FORMS_ORDER)),
             ("Part C", "Expert review sheet for the wording of the questions; how printed copies are handled; suggestions register"),
             ("Part D", "Safety protocol; colour bands and scoring; objectives-to-tools matrix; cost and service log template"),
             ("Annex", "Tools for later phases that are NOT used in this study (serving personnel, family members, key informants, Delphi) are available on request and need an ethics amendment")]:
    para(f"**{a}.** {b}", after=6)
para("")
para("**How to read the questionnaires.** Every question is numbered. ☐ marks a tick-box answer. “Ask only if…” shows when a question appears. “Adaptive” shows questions that appear only when earlier answers are above a set level (this shortens the check for most people). “Sensitive” marks questions that always include “Prefer not to say”. Students never type a name, admission number or phone number into a questionnaire. Three open suggestion boxes are included so that students can say what should change.", 10.5)
para("**Readability.** The questions were written in plain English at about a Grade 6 to 7 reading level. A Kiswahili version of the crisis and help messages is built into the app; a full Kiswahili translation of the questionnaires, with back-translation, is planned after approval.", 10.5)
para("**Placeholders.** Phone numbers shown as +2547xxxxxxxx are placeholders to be replaced with real nurse, duty officer and support-office numbers when the service is adopted.", 10.5)
pb()

# ---------- Part A ----------
d.add_heading("PART A. YOUR PROTECTIONS, INFORMATION SHEET AND CONSENT", 1)
d.add_heading("Your protections (read this before you decide)", 2)
para("Before you are asked to agree to anything, these are the promises made to you.", italic=True)
for i, (h, t) in enumerate(P.PROTECTIONS, 1): para(f"**{i}. {h}** {t}", 11)
para("")
para("Study contacts (shown on every sheet):", after=2)
for c in P.CONTACTS: bullet(c)
pb()
c = P.CONSENTS["student"]
d.add_heading(c["title"], 2)
para(c["who"], italic=True)
for h, paras in c["sections"]:
    d.add_heading(h, 3)
    for t in paras: para(t)
d.add_heading("Consent statements (tick each box)", 3)
for s_ in c["statements"]: para("☐  " + s_, indent=0.4)
for s_ in c.get("optional", []): para("☐  " + s_, indent=0.4)
para("")
para("No name or signature is asked for. Ticking the boxes is your agreement. On the phone, the same statements appear on screen and you tap to agree; the app stores only the version number and time of consent, not a name.", 10, italic=True)
pb()

# ---------- Part B ----------
d.add_heading("PART B. QUESTIONNAIRES", 1)
para("Each questionnaire below is printed exactly as it appears in the app. Where a question has two versions, both are shown.", 10.5)

LETTERS = "abcdefghijklmnopqrstuvwxyz"
def render_form(key, code, ftitle, who):
    f = I.FORMS[key]
    d.add_heading(f"{code}. {ftitle}", 2)
    para(f"**For:** {who}.  **Time:** about {f['minutes']} minute(s).", 10.5)
    def blocks(sec):                     # tick-box items that share a heading are one question with several boxes
        out = []
        for it in sec["items"]:
            if it["type"] == "check" and out and out[-1][0] == "grp" and out[-1][1][0]["group"] == it["group"]: out[-1][1].append(it)
            elif it["type"] == "check": out.append(("grp", [it]))
            else: out.append(("q", [it]))
        return out
    idx, n = {}, 0
    for s in f["sections"]:
        for kind, its in blocks(s):
            n += 1
            for it in its: idx[it["id"]] = n
    n = 0
    for s in f["sections"]:
        d.add_heading(s["title"], 3)
        if s.get("intro"): para(s["intro"], 10.5, italic=True)
        for kind, its in blocks(s):
            it = its[0]; n += 1
            heading = it["text"] if kind == "q" else (it["group"] or it["text"])
            p = para(f"**{n}.** {heading}", 10.5, after=1)
            p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
            p.paragraph_format.keep_with_next = True
            notes = []
            if it.get("show_if"):
                qid, vals = it["show_if"]
                if qid in idx:
                    ref = next((x for sx in f["sections"] for x in sx["items"] if x["id"] == qid), None)
                    labs = {v: l for v, l in (ref["options"] if ref else [])}
                    shown = " or ".join('"%s"' % labs.get(v, v) for v in vals) if ref and ref["type"] != "check" else "ticked"
                    notes.append(f"Ask only if the answer to Q{idx[qid]} is {shown}")
            if it.get("gate"):
                ids, thr = it["gate"]
                qs = ", ".join(f"Q{idx[i]}" for i in ids if i in idx)
                notes.append(f"Adaptive: asked only if the score on {qs} is {thr} or more")
            if kind == "grp" and not it.get("max_checks") and "tick" not in heading.lower(): notes.append("Tick all that apply")
            if it.get("sensitive"): notes.append("Sensitive: may be skipped")
            if it.get("text_family"): notes.append("Family wording: " + it["text_family"])
            if notes:
                np_ = para("[" + "; ".join(notes) + "]", 9, italic=True, indent=0.8, after=1); np_.paragraph_format.keep_with_next = True
            if it["type"] == "text":
                para("_" * 70, indent=0.8, after=1); para("_" * 70, indent=0.8, after=4)
            elif kind == "grp":
                for g in its: para("☐  " + g["text"], 10, indent=1.0, after=0).paragraph_format.keep_with_next = True
                para("", after=3)
            else:
                for v, lab in it["options"]: para("☐  " + str(lab), 10, indent=1.0, after=0).paragraph_format.keep_with_next = True
                para("", after=3)
    para(f"End of {code}. Thank you.", 10, italic=True)

for fi_, (key, code, t, who) in enumerate(FORMS_ORDER):
    if fi_: pb()
    render_form(key, code, t, who)
pb()

# ---------- Part C ----------
d.add_heading("PART C. EXPERT REVIEW, PRINTED COPIES AND SUGGESTIONS", 1)
d.add_heading("C1. Expert review sheet (five DCHS staff)", 2)
para("Please rate each question for **clarity** (1 = not clear, 4 = very clear) and **relevance to DCHS students** (1 = not relevant, 4 = very relevant), and add a comment if you would change the wording. Do not write your name. The content validity index for each question is the share of reviewers who give a 3 or 4.", 10.5)
rows = [("Q", "Question (B1: DCHS student wellbeing check)", "Clarity 1-4", "Relevance 1-4", "Comment")]
n = 0; prevg = None
for s_ in I.FORMS["student_screen"]["sections"]:
    for it in s_["items"]:
        if it["type"] == "check":
            if it["group"] == prevg: continue
            prevg = it["group"]; txt = it["group"] or it["text"]
        else:
            prevg = None; txt = it["text"]
        n += 1; rows.append((str(n), txt if len(txt) < 150 else txt[:147] + "...", "", "", ""))
table(rows, [0.9, 8.0, 1.8, 2.0, 3.7], size=8.5)
d.add_heading("C2. How printed copies are handled", 2)
for t in P.PRINT_PROCEDURE: bullet(t)
d.add_heading("C3. Suggestions register (kept by the researcher)", 2)
para("Every comment from the three suggestion boxes, the end-of-pilot form and the expert sheets is entered here, coded into a theme, and given a decision with a reason. Adopted changes are recorded in the change log with a new protocol version.", 10.5)
table([P.SUGGESTIONS_LOG[0]] + [("",) * 7 for _ in range(8)], [1.8, 2.6, 4.2, 1.8, 2.6, 2.2, 1.4], size=8)
pb()

# ---------- Part D ----------
d.add_heading("PART D. PROTOCOLS, SCORING AND TEMPLATES", 1)
d.add_heading("D1. Safety protocol for the nurse call-back", 2)
for h, items in P.SAFETY:
    d.add_heading(h, 3)
    for t in items: para(t, 10.5)
d.add_heading("D2. Colour bands and what happens next", 2)
table([("Band", "Zone", "How it is reached", "What the person is offered")] + [tuple(b) for b in P.BANDS], [3.2, 1.6, 6.4, 5.2])
para(P.BAND_NOTE, 10)
para("**Use of the colour.** The colour is a prompt to offer support early. It is never a pass or fail, never used to select or exclude, and is shared with the college support office only if the person chooses. The selection panel does not see answers or scores.", 10.5)
d.add_heading("D3. Objectives-to-tools matrix", 2)
table([("Objective", "Tools that collect the data", "Main analysis")] + [tuple(m) for m in P.MATRIX], [4.2, 6.6, 5.6])
d.add_heading("D4. Cost and service log template (completed weekly by the nurse lead)", 2)
rows = [P.COSTLOG[0]] + [("",) * 6 for _ in range(14)]
table(rows, [2.2, 2.6, 4.6, 1.6, 2.6, 2.8], size=9)
d.save(OUT); print("saved", OUT)
