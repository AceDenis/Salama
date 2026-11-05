# Analysing Salama data in jamovi

All exports are one row per submission, numbers only, with a codebook (`docs/codebook.csv`).
Open a CSV in jamovi (File > Open) or use the `.sav` made by `tools/make_sav.py`, which carries variable labels, value labels and measure types.

**Files**
| File | Use |
|---|---|
| `v_student_screen` | Every DCHS applicant or student check (selection and orientation). |
| `v_student_outcomes` | First selection-stage screen per person joined to what happened later (stayed, deferred, withdrew). |
| `v_student_paired` | Same person at selection and at orientation. |
| `v_student_cohort` | Group figures for support planning (groups under 10 hidden). |
| `v_checkin`, `v_pulse`, `v_baseline_*`, `v_informant`, `v_usability_end` | Pilot service data. |
| `v_service_requests`, `v_engagement_weekly` | Time to contact, referral and visit completion, weekly use. |

**First steps**
1. Check each variable's measure type in the Data tab (Nominal, Ordinal, Continuous). The `.sav` does this for you.
2. Blank cells are missing: not asked (skipped by design) or Prefer not to say (coded 9 for items that offer it; recode 9 to missing for analysis).
3. Totals are already calculated: `phq9`, `gad7`, `auditc`, `ptsd5`, `brs`, `stakes`, `sus`, plus positive screens (`phq9_pos`, `gad7_pos`...).
   Adaptive short forms are marked by `phq9_short` and `gad7_short`.

## Analyses matched to the objectives

**A. Describe the sample and the problem** — Analyses > Exploration > Descriptives; Frequencies. Report `phq9_pos`, `gad7_pos`, `fm_strain`, `fm_informal`, `fm_security_any`, `sr_count`.

**B. Does it matter that selection is at stake?** (`v_student_paired`) — T-Tests > Paired Samples: `phq9_orientation` vs `phq9_selection`; also `gad7`, `brs`, `auditc`. Tick Wilcoxon rank as a check, and Descriptives plot. A rise in symptoms and fall in resilience after admission, with high `stakes_selection`, means answers under selection pressure under-report. This is the evidence for why the screen must not be a gate.

**C. Does the screen predict leaving?** (`v_student_outcomes`; only rows where `attrition` is 0 or 1)
- Regression > 2 Outcomes (Binomial): dependent `attrition`; covariates `phq9`, `gad7`, `brs`; factors `fm_strain`, `fm_informal`. Report odds ratios with 95% CI.
- Keep the model small. Rule of thumb: about 10 leavers per predictor. With few leavers, use fewer predictors or pool intakes, and state it as exploratory.
- ROC curve: use a jamovi ROC module from the jamovi library (for example `psychoPDA`) or export to R. Report AUC with CI, and sensitivity and specificity at a pre-declared threshold.
- Do NOT use the result to set a cut-off for exclusion. The study asks whether the screen can *target support*, not whether it can *select out*.

**D. Which stressors matter?** Frequencies on `sr_*` ticks; Contingency Tables (chi-square) of `sr_fees` or `fm_strain` by `attrition`. Code `v_free_text` (`sr_text`) with thematic analysis (Braun and Clarke, 2006).

**E. Usability and confidentiality** (`v_usability_end`) — Descriptives on `sus` (above 68 is above average), perceived confidentiality (`pc1`-`pc4`), usefulness. Reliability: Factor > Reliability Analysis (Cronbach alpha) for `phq9`, `gad7`, `sus`, `brs`.

**F. Service performance** (`v_service_requests`) — median `hours_to_first_contact`; share `contacted_within_8h` (same-day) and `contacted_within_7d` (routine); share `visit_completed`.

**G. Before and after** (`v_prepost`, `v_checkin` by `unit_code` and `wave`) — Mixed Models (GAMLj module) for repeated check-ins within `anon_code`; compare pilot unit with comparison unit.

**H. Did changes during the pilot matter?** Add `protocol_version` as a factor and compare outcomes before and after a documented change.

## Reporting rules
Never report a cell with fewer than 10 people. Do not release adjacent groups with totals. Say plainly that the pilot shows feasibility, uptake and association, not clinical improvement or causal effect.

## Practice first
`sample_data/SYNTHETIC_*` are invented data. The links in them (for example money strain predicting leaving) were put there for practice and are **not findings**.
