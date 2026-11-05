# Study portal and languages

Open `portal.html` (same folder as `index.html`). Eight tabs: Student app, Nurse console, Dashboard, Monthly report, Design notes, Research survey, Expert input, Data & export. Switch EN / SW at the top; the choice carries to every tab.

## Scope (pragmatic)
Core: the enrolled-student survey and check-in, weekly pulse, nurse call-back, dashboard, monthly report. Extras (expert review, applicants, family/personnel forms) are optional and never delay the core.

## What the survey covers (a soldier's whole life)
Work and course, family and home, money / loans / shylocks / held IDs, health (PHQ-9, GAD-7, PC-PTSD-5, AUDIT-C), safety, belonging, and contact with civilian police (new: anonymous, optional, "Prefer not to say"; switch off with `DISABLED_ITEMS` in config.js, ids po1 to po5).

## Kiswahili
Kiswahili text is a DRAFT. Before real use: translator check, independent back-translation, and use validated Kiswahili wording where one exists (e.g. PHQ-9). Words live in `tools/i18n/` (`en_instrument.json` + `sw_instrument_*.txt` for questions, `sw_ui.py` and `sw_portal.py` for screens). Run `python3 tools/build.py` after edits. New questions are translated in `sw_portal.py`.

## Demo vs live
Demo mode keeps everything in the browser; use "Load example data" on Data & export to see the dashboard and report. Live mode reads the database views (run `database/03_reports.sql`). Groups under 10 are hidden. Set `EXPECTED_PARTICIPANTS` in config.js for a participation rate.

## Tested
`test/run_all.sh`: parity, roles/privacy, app (34), live chain on a local test database (31), portal (21). Not yet run against a real Supabase project or with real students.
