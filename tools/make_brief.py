"""Two-page executive brief for DCHS leadership (python-docx)."""
import sys, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
out = sys.argv[1] if len(sys.argv) > 1 else "../Executive_Brief_DCHS.docx"
d = Document(); s = d.sections[0]
s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = Cm(1.9); s.top_margin = Cm(1.5); s.bottom_margin = Cm(1.4)
n = d.styles["Normal"]; n.font.name = "Calibri"; n.font.size = Pt(10); n.paragraph_format.space_after = Pt(3)
n.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
TEAL = RGBColor(0x0F, 0x3D, 0x3A); RUST = RGBColor(0xB4, 0x49, 0x1F)
def runs(p, t, size=None, color=None):
    for i, part in enumerate(re.split(r"\*\*", t)):
        if part:
            r = p.add_run(part); r.bold = bool(i % 2)
            if size: r.font.size = Pt(size)
            if color: r.font.color.rgb = color
def P(t, size=None, color=None, after=3, align=None):
    p = d.add_paragraph(); runs(p, t, size, color); p.paragraph_format.space_after = Pt(after)
    if align: p.alignment = align
    return p
def H(t):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(12); r.font.color.rgb = TEAL
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2); p.paragraph_format.keep_with_next = True
def B(t):
    p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(0.55); p.paragraph_format.first_line_indent = Cm(-0.4); p.paragraph_format.space_after = Pt(1.5)
    runs(p, "•  " + t)
def shade(c, fill):
    pr = c._tc.get_or_add_tcPr(); e = OxmlElement("w:shd"); e.set(qn("w:val"), "clear"); e.set(qn("w:color"), "auto"); e.set(qn("w:fill"), fill); pr.append(e)
def table(rows, widths, size=9):
    t = d.add_table(rows=len(rows), cols=len(widths)); t.style = "Table Grid"; t.autofit = False
    for j, w in enumerate(widths): t.columns[j].width = Cm(w)
    for i, r in enumerate(rows):
        for j, x in enumerate(r):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ""; runs(c.paragraphs[0], x, size); c.paragraphs[0].paragraph_format.space_after = Pt(1)
            if i == 0:
                shade(c, "DCE9E6")
                for rr in c.paragraphs[0].runs: rr.bold = True
    d.add_paragraph().paragraph_format.space_after = Pt(1)

P("**Salama Check-In**", 22, TEAL, 0)
P("Executive brief for the Defence College of Health Sciences (DCHS), NDU-Kenya, and the Medical Services", 11, RUST, 2)
P("From: WEDAH, BSc Nursing with Military Health · Supervisor: [to be added] · October 2026", 9, None, 4)

H("The problem")
P("Mental health problems, money worries and pressures at home are common in military and student populations, and most people do not ask for help because they fear being judged or fear that their record will not stay private. Studies elsewhere find that about six in ten military personnel with a mental health problem do not seek help (Sharp et al., 2015), that 30.9% of Kenyan university students had at least one mental health condition (Mugotitsa et al., 2025), and that nursing programmes often lose 10% to 30% or more of students (Sheikoleslami et al., 2025). **No official KDF or DCHS figures were found**, so the college cannot yet see its own picture. The students who leave are already enrolled.")
H("The proposal")
P("A **private wellbeing check** on a student’s phone that gives a **green, amber or red result only the student sees**, with one-tap help: a **nurse call-back** with a stated time, an anonymous question to the nurse, a money and welfare navigator, short lessons, and a weekly one-minute pulse. If a group of ten or more shows a rise in strain, the welfare lead receives a **group alert, never with names**. A working prototype exists; it has been tested on a local test database and is ready for a pilot once approvals are in place.")
H("What students are promised before they take part")
B("They choose: they may say no, skip any question or stop at any time. It is **not an assessment** and has no effect on marks, progression, discipline, sponsorship, posting or place.")
B("No name, admission number, service number or phone number is stored with answers. Lecturers, commanders and managers never see individual answers. Groups under ten are hidden.")
B("Help numbers on every worrying result, a Quick Exit button, and the ethics approval number and contacts shown before consent.")
H("What the pilot will do")
table([("Item", "Plan"),
       ("Who", "All enrolled DCHS students invited (a census). Applicants, serving units and families only later, if agreed."),
       ("How long", "Eight months in total; live pilot of at least four weeks (up to three months)."),
       ("Measures", "Uptake, time to first contact, referrals that reached a visit, usability, perceived confidentiality; PHQ-9, GAD-7, money and loans, thoughts of leaving; open suggestions."),
       ("Methods", "Online or printed questionnaires only, analysed in jamovi. No Delphi panel, interviews or focus groups."),
       ("Covers", "Work, family, money (loans, shylocks, held IDs), betting, health, safety, belonging and contact with civilian police. English and Kiswahili (Kiswahili checked by a translator and back-translated before use)."),
       ("Approvals", "Department, supervisor, university ethics, KDF-ISERC (no fee), DCHS, NACOSTI, data protection."),
       ("Early help", "Amber: nurse contact within 24 hours, visit within 7 days. Red: contact within 8 hours, visit within 48 hours (all within nurse cover hours; after hours, numbers and the duty medical officer).")],
      [2.6, 14.6])
H("Cost and hosting")
P("**Estimated pilot cost: about KES 154,000**, including 10% contingency (the largest items are the nurse on-call honorarium if not provided in kind, ethics and NACOSTI fees (KDF-ISERC approval carries no fee), airtime, and printing). The survey is hosted on **free services** (GitHub Pages and a free Supabase plan, or KoboToolbox), so **DCHS does not need to host anything** for the pilot. If the pilot succeeds, a Kenyan copy of the call-back service should be hosted on a college or Medical Services server to meet data-protection rules.")
H("What the pilot can and cannot show")
P("It can show whether students use the service, trust it, and reach a nurse and a visit quickly. It **cannot** show that mental health improved or that suicides were prevented. These limits are stated in the proposal. If the college wishes to use results for admission or discipline, the study advises against it on legal grounds (Constitution Article 27; Mental Health (Amendment) Act, 2022) and because fear of consequences would reduce honest answers and use.")
H("Why it may pay for itself (illustrative)")
P("Using placeholder figures, a running cost of about KES 784,000 a year (nurse time, supervision, hosting, airtime, peer champions, analyst) is covered if the college keeps about two additional students a year, when a retained place is worth KES 500,000. **Both figures are placeholders** until DCHS provides its own.")
H("What we ask")
B("A **letter of support** and a written undertaking that results are not used for marks, progression or discipline.")
B("A **named nurse and back-up** on a cover-hours rota, and an agreed after-hours route.")
B("Permission to **invite all enrolled students**, through a gatekeeper outside the teaching and discipline side.")
B("Real contact numbers and the cost of a lost place, to replace the placeholders (currently +2547xxxxxxxx).")
P("Study site: DCHS, Nairobi (S 1.3124°, E 36.8043°). Contact: WEDAH, [phone and email to be added]. Full proposal, printable tools pack and researcher handbook are available on request.", 8.5, None, 0)
d.save(out); print("saved", out)
