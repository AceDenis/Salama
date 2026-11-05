# Salama Check-In: setup guide (free hosting)

Everything here uses free tiers. Check each provider's current free limits and terms before you start, because they change.
**Important rule:** use the free cloud for development, training and the anonymous research survey. The live nurse call-back service
holds contact numbers and is health data: before it goes live, get ethics, DCHS and Medical Services approval and decide where it is
hosted (see "Where the data lives" below).

## What you have

| Folder | What it is |
|---|---|
| `web/` | The phone app (`index.html`), the staff console (`console.html`), and settings (`config.js`). Static files, no server needed. |
| `database/` | SQL for the database: `01_schema.sql`, `02_views.sql`, `03_reports.sql`, `04_make_staff.sql`. `edge_ai_guide.ts` is optional. |
| `tools/` | `instrument.py` (every question, the single source of truth), `build.py`, `make_sav.py`, `synth.py`. |
| `docs/` | `codebook.csv` (every variable), this guide, the jamovi guide. |
| `sample_data/` | SYNTHETIC practice data (invented, not real people) as CSV and .sav. |

## 1. Try it in 2 minutes (no account)
Open `web/index.html` in a browser (or serve the `web` folder with any static host). It starts in **demo mode**: answers stay in that browser.
Open `web/console.html` in the same browser to see the nurse queue and exports.

## 2. Database (Supabase, free plan)
1. Create a project at supabase.com. Choose the region closest to Kenya that is offered, and note it for your ethics form.
2. Open **SQL editor**. Paste and run, in order: `01_schema.sql`, `02_views.sql`, `03_reports.sql`.
3. **Authentication > Users > Add user** for each staff member (email and password, tick *Auto confirm*). Then edit and run `04_make_staff.sql`.
   Roles: `nurse` (queue), `researcher` (answers, exports), `welfare` (college support office), `interviewer` (colour look-up only), `admin`.
   Grant `interviewer` only with ethics committee and DCHS governance approval.
4. **Project settings > API**: copy the Project URL and the `anon` public key.
5. Turn on **email sign-in only**, turn off public sign-ups (Authentication > Providers/Settings), and enable **MFA** for staff if available.
6. Free projects can be paused after a period of inactivity. Open the console weekly during the pilot and keep a dated backup (step 5).

## 3. Put the app online (any free static host)
Pick one: GitHub Pages, Cloudflare Pages or Netlify. Upload the contents of `web/`.
Edit `web/config.js` first:
```
BACKEND: "supabase",
SUPABASE_URL: "https://xxxx.supabase.co",
SUPABASE_ANON_KEY: "your anon public key",
```
The anon key is meant to be public. It can only **insert** rows (the database enforces this). It cannot read anything.
Fill in `LOCAL_CONTACTS`, `REFERRALS` and confirm every number in `NATIONAL_LINES` before go-live.
Share links such as `https://your-site/index.html?role=student&unit=DCHS-APP&ctx=selection` (applicants) and `...?role=student&unit=DCHS-STU&ctx=orientation` (after admission).
Phones can "Add to home screen"; the app then works offline and sends answers when a connection returns.

## 4. Export for jamovi
Console > **Exports for jamovi** > Download. Each file is flat and numeric. Then see `docs/JAMOVI_GUIDE.md`.
For labelled .sav files: `pip install pandas pyreadstat`, then `python3 tools/make_sav.py v_student_outcomes.csv applicant_outcomes`.

## 5. Back up
Supabase dashboard > Database > Backups, or run `pg_dump` with the connection string. Keep one copy on an encrypted drive held by the PI.

## 6. Change a question
Edit `tools/instrument.py`, run `python3 tools/build.py`, copy the new `web/` files to your host and re-run `database/02_views.sql`.
Then change `PROTOCOL_VERSION` in `web/config.js` and add a line in the console **Change log** (trigger, change, who approved).
Every response is stamped with the protocol version, so you can analyse before and after.

## 7. Optional AI guide
By default the guide runs on the phone and sends nothing. To use an AI model, deploy `database/edge_ai_guide.ts` as a Supabase Edge Function,
set the provider key as a secret, and put the function URL in `AI_ENDPOINT`. Do this only with ethics and data-protection approval,
because what people type leaves the phone. Crisis wording never goes to the AI: the app shows help numbers and the nurse button first.

## Where the data lives (important)
Health data is sensitive personal data under the Data Protection Act, 2019. The Data Protection (General) Regulations, 2021
(Regulation 26) require certain processing for health purposes to happen in Kenya or through a serving copy in Kenya.
Plain PostgreSQL means you can later move to a Kenyan server with a dump and restore. Until then, keep free-cloud use to dummy data and
the anonymous survey, subject to your ethics committee's decision. Register as a data controller with the ODPC and complete a DPIA
before real use.

## Tests that come with the project
`test/parity.py` (database scores equal the app's scores), `test/e2e.py` (browser flows), `test/rls.sh` (who can see what).


## 8. Anonymous participant IDs
The first time someone taps Continue, the database issues the next number for their group (`APPL-0001`, `PERS-0001`, `FAMI-0001`), first come first served. No name or phone is linked. If the phone is offline at that moment it makes a random code instead. Informants get none. The public key cannot read the ID table.

## 9. KoboToolbox route (no hosting)
`kobo/*.xlsx` are the same questionnaires as importable forms (validated with pyxform / ODK Validate). Import one at a time in KoboToolbox, deploy, share the link, download CSV with numeric values, then run `python3 tools/kobo_score.py export.csv scored.csv` to add the scale totals. Regenerate after any question change with `python3 tools/make_xlsform.py kobo`.

## 10. Go live in 20 minutes: checklist
1. Supabase project and the three SQL files (section 2). 2. Your staff account (`04_make_staff.sql`). 3. URL and anon key in `web/config.js`. 4. Upload `web/` to a free static host. 5. `python3 tools/check_setup.py <url> <anon-key>`. 6. `python3 tools/make_links.py https://your-site/` for links and QR codes. 7. Submit a test response and export it. 8. Fill in contacts and confirm every national number. Do not start with real participants until ethics approval and the DCHS and Medical Services agreement are in place.
