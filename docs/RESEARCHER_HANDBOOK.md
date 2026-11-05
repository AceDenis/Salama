---
title: "Salama Check-In: Researcher's Handbook"
subtitle: "How the project works, how to put the survey online, how to collect your data, and how to defend it"
author: "For WEDAH, BSc Nursing with Military Health, DCHS"
---

# 1. The project in one page

**Problem.** Students at DCHS carry pressures that are rising and changing: heavy workload and exams, clinical placements, money problems (including informal loans and ID cards held as security), family problems and violence at home, and the strain of military routine. Some leave the course. The students who drop out are **already enrolled**, and most people who need help do not ask for it, mainly because of stigma and doubt about confidentiality. DCHS has no routine, confidential way to see strain early.

**What you propose.** *Salama Check-In*: a private check on a phone (or paper) that gives a green, amber or red result **only the student sees**, with one-tap help (a nurse call-back within stated cover hours, an anonymous question to the nurse, a money and welfare navigator, short lessons, a guide) and a weekly pulse that lets the service **adapt** and warn of group-level strain without naming anyone.

**Who takes part.** All enrolled DCHS students (any programme and year), aged 18 or older. Applicants, serving units and family members are **later phases** (the app already supports them; they need their own agreements and an ethics amendment).

**What the study does (6 objectives).**

1. Adapt the service and questions to DCHS students (short expert review, testing with 10 to 15 students, open suggestion boxes). **No Delphi panel, interviews or group discussions.**
2. Run a pilot at DCHS (4 weeks, up to 3 months) with a nurse on call in stated cover hours.
3. Measure uptake, time to first contact, referral completion, usability, perceived confidentiality and help-seeking intention.
4. Describe the stressors students name themselves (money, loans, held ID cards) and the reasons they give for thinking of leaving.
5. Describe change over the pilot, and explore links between baseline signals and early exit (support, never exclusion).
6. Produce a costed adoption plan and policy brief.

**The honest claim.** The pilot shows *uptake and feasibility*, not clinical improvement. It cannot prove that suicides were prevented. It can show that students used it, trusted it, and were reached **faster**.

**Cost.** About KES 154,000 for the whole pilot (estimate); hosting costs KES 0 on free services.

# 2. The question you asked: must the college host the survey?

**No.** The college is asked for *support*, not hosting: a letter of support, permission to brief students and put up the poster, nurse time, and later a decision on hosting a Kenyan copy if the service is adopted.

**Why my earlier link did not work for you.** The address I gave you pointed to a temporary folder in my workspace. It only exists there, and nobody else can open it. To get a link that works on any phone, the files must be placed on a free web service (below). You do this once. After that the link works for everyone.

## Which route to choose

| Route | Effort | What students get | What you get | Choose it when |
|---|---|---|---|---|
| **1. KoboToolbox** (easiest) | 15 minutes, no hosting, no coding | The same questions in a web form; works offline in the Kobo app; protections shown first | A link and QR code at once; data as CSV/Excel for jamovi (add scale totals with `kobo_score.py`) | You want data collection running quickly, or hosting is delayed |
| **2. GitHub Pages + Supabase** (full service) | About 40 minutes, once | The full app: colour result, nurse call-back, lessons, guide, weekly pulse, anonymous ID, offline use | Staff console and one-click CSV/.sav exports for jamovi | You have the nurse and approvals, and want the real service |
| **3. Paper + Kobo data entry** | Printing and typing | Printed form, sealed box | You type forms into the Kobo form on your laptop | Students without smartphones |

The proposal (section 3.4.5) names Route 2 as the main route, Route 1 and paper as fallbacks, and shows hosting as free in the budget. If you prefer to start with Route 1, say so in your defence: it is the same questionnaire.

**Ethics comes first.** Whatever route you use, do not enrol real students before ethics approval, the NACOSTI licence and the DCHS letter of support are in hand. Until then, use the demo with invented answers.

## Route 1: KoboToolbox, step by step

1. Create a free account at kobotoolbox.org.
2. Click **New project, Upload an XLSForm** and choose `kobo/salama_student_screen.xlsx` from the project folder. Repeat later for `salama_checkin`, `salama_pulse` and `salama_usability_end`.
3. Click **Deploy**. Open **Share**, switch on **Anyone can submit data**, and copy the **web form link**. Make a QR code from it (any free QR site, or Kobo shows one).
4. Send the link in the class messaging group, and print the QR code on a poster.
5. **Data > Downloads**: CSV, *Values and headers*, *Show choices as: XML values*, *Split select multiples: yes*. Run `python3 tools/kobo_score.py export.csv scored.csv` and open `scored.csv` in jamovi.
6. Kobo gives each submission a sequential number (`_id`), which is your first-come-first-served anonymous ID. The form also shows each student a private code at the end.
7. Kobo's free servers are outside Kenya. Use this route for anonymous survey answers only, with ethics approval. It does not collect phone numbers or offer a nurse call-back; the last page shows help numbers.

## Route 2: GitHub Pages + Supabase, step by step

*A. Put the app online (about 10 minutes).*

1. Make a free account at github.com. Click **New repository**, name it `salama`, choose **Public**, tick *Add a README*, and **Create**.
2. Unzip `Salama_Web_App.zip`. In the repository click **Add file > Upload files** and drag in **the files inside the folder** (index.html, console.html, config.js, sw.js, content.json, manifest.webmanifest, icon.svg), not the folder itself. Click **Commit changes**.
3. Click **Settings > Pages**. Under *Branch* choose `main` and `/ (root)`, then **Save**. After one or two minutes the page shows your address: `https://YOUR-USERNAME.github.io/salama/`.
4. **Your student link** is that address plus `index.html?role=student&unit=DCHS-STU`. Open it on your phone to test. (If you prefer, Netlify Drop at app.netlify.com/drop lets you drag the folder and get a link at once; make a free account to keep it.)

*B. Connect the database (about 20 minutes).* Follow `docs/SETUP_GUIDE.md` sections 2 and 3: create a free Supabase project, run `01_schema.sql`, `02_views.sql`, `03_reports.sql`, add yourself as `researcher` with `04_make_staff.sql`, then paste the Project URL and anon key into `config.js` (on GitHub click the file, then the pencil icon) and set `BACKEND: "supabase"`.

*C. Check and share.* Run `python3 tools/check_setup.py <url> <anon-key>`, then `python3 tools/make_links.py https://YOUR-USERNAME.github.io/salama/` for the link list and QR code. Open the console, sign in, submit a test answer, and export it.

*Why the public key is safe.* It can only add answers. It cannot read, change or delete anything.

## Route 3: paper

Print the questionnaire from the Tools Pack (Part B). Students tick, then drop the form into a sealed box. You open the box with a witness, number each form (P-001, P-002) and type it into the Kobo form. A tear-off slip on the back lets a student ask for a nurse call-back.

## Rehearsal on your laptop (no accounts, 10 minutes)

Unzip the web app and double-click `START_DEMO_WINDOWS.bat`. Open `http://localhost:8080/index.html`, answer as different students, then open `http://localhost:8080/console.html` in the same browser and download a CSV for jamovi. Demo answers stay in that browser, so this is for practice and for showing your supervisor how the chain works.

# 3. How the system fits together

| Piece | What it is | Who uses it |
|---|---|---|
| Phone app (`index.html`) | Installs like an app, works offline, scores answers on the phone, queues and sends when there is signal | Students |
| Database (Supabase) | Stores answers, requests, events; the public key can only insert | Behind the scenes |
| Staff console (`console.html`) | Role-based: nurse queue, support-office list, researcher exports, change log, audit | Staff |
| KoboToolbox forms (`kobo/`) | The same questions as importable forms | You |
| Tools Pack (`Data_Collection_Tools_Pack.docx`) | Protections, information sheet, questionnaires, expert review sheet, protocol, matrix | Ethics committee |

**Privacy rules to quote.** No names, admission numbers or phone numbers with answers. Lecturers, examiners and commanders see nothing individual and do not recruit. Group figures only (groups of 10 or more). The support office sees a colour only if the student chooses to share it. Money questions never change the colour.

# 4. Anonymous IDs

* The first time a student taps *Continue*, the database issues the **next number in order of joining**: `STUD-0001`, `STUD-0002`. It is not linked to a name, phone or admission number.
* If there is no signal, the phone makes a random code and carries on.
* The same code links one student's baseline, weekly pulses and follow-up checks, which is what the change analyses need. A student who loses the phone starts again with a new code.
* You see every code in your data but never who holds it.

# 5. What the student sees

* **The protections come first**, on the first screen, before consent: you choose; not an assessment; no name; staff cannot see you; your result is yours; help is close; approved and supervised (ethics number and contacts); one limit (immediate danger).
* Only what applies: follow-up questions appear only if an earlier answer calls for them (for example money follow-ups if the student has borrowed). Sensitive questions can always be skipped.
* **Simple view** in Settings shows only: check, weekly pulse, get help, ask the nurse, money help.
* **Three open suggestion boxes** and a comment box at the end give room for opinions; every comment is entered in the suggestions register with a decision and a reason (this replaces the Delphi panel and interviews).
* Nurse numbers are placeholders (**+2547xxxxxxxx**) until the service is adopted.

# 6. After college

The same code goes with the graduate. In *Settings* they record a change of situation (in barracks, deployed, back from deployment, on leave) and keep their history. The app opens with no signal after the first load, holds requests until a connection returns, and can offer a prepared text to the nurse phone (`NURSE_SMS`). This is an assumption to test with graduates in a later phase; it is not claimed as a result.

# 7. Early intervention in time

Tier 0 self-help; Tier 1 early cue: offer of a nurse, call-back within 24 hours if asked; Tier 2 struggling: contact within 24 hours, visit within 7 days; Tier 3 red or any thought of self-harm: contact within 8 hours, visit within 48 hours; Tier 4 imminent danger: duty medical officer and emergency services at once. All times are counted within nurse cover hours (07:00 to 21:00, to be confirmed); after hours the phone shows the duty officer and national lines. A group of 10 or more that rises 10 points above its previous four-period average triggers a group alert within a week. The key measure is **lead time**.

# 8. Checklist before you start collecting

1. Ethics approval, NACOSTI licence and DCHS letter of support in hand.
2. `config.js`: ethics approval number and contacts (`ETHICS_REF`, `CONTACT_TEXT`), nurse and officer numbers (placeholders until adoption), national lines confirmed.
3. Nurse and back-up named and briefed; safety protocol printed.
4. Test the link on one Android and one iPhone.
5. Run `check_setup.py`; submit a test; see it in the console; export; open it in jamovi.
6. Brief class representatives on what is private. Lecturers do not recruit.
7. Back up after day one, then weekly.

# 9. Likely questions and short answers

1. **Is this an assessment or a screen for who may stay?** No. It never affects marks, progression, discipline or sponsorship, and staff cannot see answers. The college letter says so.
2. **Why enrolled students only?** Those who drop out are enrolled. Applicants, units and families are later phases.
3. **Why no Delphi or interviews?** Cost and scope. Wording is checked by five staff and 10 to 15 students, and suggestion boxes carry opinions into a suggestions register.
4. **Must the college host it?** No. Free services host it (GitHub Pages and Supabase, or Kobo). The college is asked for support and, later, to host a Kenyan copy of the call-back service.
5. **How is privacy kept?** No names, a sequential anonymous code, scores on the phone, insert-only public key, role-based staff access, groups under 10 hidden.
6. **What if a student is in danger?** Help numbers at once; same-day call-back in cover hours; duty officer after hours; the single limit of confidentiality is told up front.
7. **Can you prove it reduces dropout or suicide?** No. The proposal claims uptake, trust, time to help and feasibility, and says so.
8. **Why trust self-reports?** They are screens, not diagnoses. The study asks students about perceived consequences and honesty to measure the effect.
9. **What about loans and ID cards?** Optional, no lender details, never change the colour, used only to guide welfare help; a no-penalty route must be agreed first or the items are switched off.
10. **Where is the data?** Free cloud for anonymous survey answers, with approval. The call-back service with phone numbers must run in Kenya.
11. **How big a sample?** All enrolled students are invited. The ideal for a 5-point margin depends on the number enrolled (Table 3.1); the minimum is 100; below that, counts only.
12. **How was it tested?** 34 browser flows in demo mode, 31 on a test database, 24 privacy and role checks, 34,980 score comparisons with no mismatches. It has not yet been run on a live Supabase project, security-reviewed, or used on real phones.
13. **Why a student as researcher?** Supervised; no teaching, marking or selection role; no access to identities.
14. **Cost?** About KES 154,000; hosting KES 0.

# 10. What is yours to fill in

Registration number and supervisor; ethics committee name and approval number; NACOSTI number; real phone numbers (replace +2547xxxxxxxx when adopted); the number of enrolled students (for the sample table); the college's cost of a lost place (for the break-even table); retention period; the letter of support from DCHS; and the Kiswahili translation.
