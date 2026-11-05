#!/usr/bin/env python3
"""Make your share links and printable QR codes.
Usage: python3 tools/make_links.py https://your-site.example/ [out_folder]
Needs: pip install segno python-docx
Produces: links.csv, one QR PNG per link, and Share_Links_and_QR_Codes.docx (print and pin up, or paste into WhatsApp)."""
import csv, os, sys
import segno
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
base = sys.argv[1].rstrip("/") + "/"; out = sys.argv[2] if len(sys.argv) > 2 else "share_links"; os.makedirs(out, exist_ok=True)
L = [
 ("DCHS students: the wellbeing check (all programmes and years)", "Enrolled DCHS students, 18 or older. Share this one link and QR code with everyone.", "index.html?role=student&unit=DCHS-STU"),
 ("Staff console", "Nurses, welfare officer, researcher. Sign-in required. Do not share with students.", "console.html"),
 ("Study portal (eight tabs, English and Kiswahili)", "Researcher and committee view: student app, nurse console, dashboard, monthly report, design notes, survey, expert input, data export. Staff only.", "portal.html"),
]
rows = []
for i, (name, who, path) in enumerate(L, 1):
    url = base + path; png = os.path.join(out, "%02d_%s.png" % (i, "".join(c if c.isalnum() else "_" for c in name)[:40]))
    segno.make(url, error="m").save(png, scale=8, border=2); rows.append((name, who, url, png))
with open(os.path.join(out, "links.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["name", "for", "link"]); [w.writerow(r[:3]) for r in rows]
d = Document(); s = d.styles["Normal"]; s.font.name = "Arial"; s.font.size = Pt(10)
d.add_heading("Share links and QR codes", 0); d.add_paragraph("Print this page, paste the links into WhatsApp or email, or print a QR code on a poster. Participants open the link on a phone. Nothing needs installing, and the page can be added to the home screen.")
for name, who, url, png in rows:
    if name.startswith("Staff"): continue
    t = d.add_table(rows=1, cols=2); t.autofit = False; t.columns[0].width = Cm(4.2); t.columns[1].width = Cm(12)
    t.cell(0, 0).paragraphs[0].add_run().add_picture(png, width=Cm(3.6))
    c = t.cell(0, 1); c.paragraphs[0].add_run(name).bold = True; c.add_paragraph(who); c.add_paragraph(url)
    d.add_paragraph()
d.add_heading("For the study team only", 1); d.add_paragraph("Staff console: " + base + "console.html (sign-in required). Do not share this with participants.")
d.save(os.path.join(out, "Share_Links_and_QR_Codes.docx")); print("written to", out); [print(r[0], "->", r[2]) for r in rows]
