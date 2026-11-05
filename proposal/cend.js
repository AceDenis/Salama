const { p, h1, h2, h3, bullets, table, gap, D, runs } = require("./lib");
const { Paragraph, AlignmentType } = D;
const orig = require("./refs_orig.json");
const added = [
 "Birkeland, S. A., Manson, T. M., Kisamore, J. L., Brannick, M. T., & Smith, M. A. (2006). A meta-analytic investigation of job applicant faking on personality measures. International Journal of Selection and Assessment, 14(4), 317–335.",
 "Cowlishaw, S., Freijah, I., Kartal, D., Sbisa, A., Mulligan, A., Notarianni, M., Couineau, A.-L., Forbes, D., O’Donnell, M., Phelps, A., Iverson, K. M., Heber, A., O’Dwyer, C., Smith, P., & Hosseiny, F. (2022). Intimate partner violence in military and veteran populations: A systematic review of population-based surveys and population screening studies. International Journal of Environmental Research and Public Health, 19(14), 8853.",
 "Glasgow, R. E., Vogt, T. M., & Boles, S. M. (1999). Evaluating the public health impact of health promotion interventions: The RE-AIM framework. American Journal of Public Health, 89(9), 1322–1327.",
 "Kwan, J., Sparrow, K., Facer-Irwin, E., Thandi, G., Fear, N. T., & MacManus, D. (2020). Prevalence of intimate partner violence perpetration among military populations: A systematic review and meta-analysis. Aggression and Violent Behavior, 53, 101419.",
 "Mugotitsa, B., Momanyi, R., Kuria, J., Amadi, D., Masai, J., Angula, E., Tsofa, B., Greenfield, J., Todd, J., & Kiragga, A. (2025). Understanding mental health among university students in Kenya: What role do family support and age play? Frontiers in Public Health, 13, 1557058. https://doi.org/10.3389/fpubh.2025.1557058",
 "Proctor, E., Silmere, H., Raghavan, R., Hovmand, P., Aarons, G., Bunger, A., Griffey, R., & Hensley, M. (2011). Outcomes for implementation research: Conceptual distinctions, measurement challenges, and research agenda. Administration and Policy in Mental Health, 38(2), 65–76.",
 "Republic of Kenya. (2010). The Constitution of Kenya, 2010 (Articles 27 and 31). National Council for Law Reporting.",
 "Republic of Kenya. (2021). The Data Protection (General) Regulations, 2021 (Legal Notice No. 263 of 2021), regulation 26. National Council for Law Reporting.",
 "Republic of Kenya. (2022). The Mental Health (Amendment) Act, 2022. National Council for Law Reporting.",
 "Sheikoleslami, R. L., Princeton, D. M., Hansen, L. I. M., Kisa, S., & Goyal, A. R. (2025). Examining factors associated with attrition, strategies for retention among undergraduate nursing students, and identified research gaps: A scoping review. Nursing Reports, 15(6), 182.",
 "Smith, B. W., Dalen, J., Wiggins, K., Tooley, E., Christopher, P., & Bernard, J. (2008). The brief resilience scale: Assessing the ability to bounce back. International Journal of Behavioral Medicine, 15(3), 194–200.",
];
const key = s => s.replace(/[^A-Za-z]/g, "").toLowerCase();
const refs = [...orig, ...added].sort((a, b) => key(a).localeCompare(key(b)));
const hang = t => new Paragraph({ children: runs(t, { size: 22 }), alignment: AlignmentType.LEFT, spacing: { after: 100, line: 300 }, indent: { left: 567, hanging: 567 } });
module.exports = () => [
 h1("REFERENCES"),
 ...refs.map(hang),
 h1("APPENDICES"),
 h2("Appendix A: Data Collection Tools Pack"),
 p("The full, printable pack (about 40 pages) is supplied as a separate file, **Data_Collection_Tools_Pack.docx**, for the ethics committee. It has the same words that students see in the app, and a printed copy can be used by students who prefer paper."),
 table(["Part", "Content"], [
  ["A", "Your protections (shown before anything else); information sheet and consent for students"],
  ["B1–B4", "Questionnaires: DCHS student wellbeing check (with three open suggestion boxes); private check-in; weekly pulse; end-of-pilot feedback"],
  ["C", "Expert review sheet for the wording; how printed copies are handled; suggestions register"],
  ["D", "Safety protocol; colour bands and scoring; objectives-to-tools matrix; cost and service log template"],
 ], [1400, 7626]),
 gap(),
 h2("Appendix B: Objectives-to-Tools Matrix"),
 table(["Objective", "Tools", "Analysis"], [
  ["1. Adapt the service and questions to DCHS students", "Expert review sheet; testing with students; open suggestion boxes; end-of-pilot comments", "Content validity index; timing; suggestions register"],
  ["2. Run a pilot at DCHS", "Service log; engagement counts; change log", "Counts; run charts; fidelity"],
  ["3. Measure uptake, time to contact, referral completion, usability, confidentiality, help-seeking", "Usage events; call-back clock; baseline and end-of-pilot items", "Medians, proportions, SUS, paired tests"],
  ["4. Describe stressors named by students and reasons for thinking of leaving", "Money items; stressor list; stressor in own words; weekly pulse cue; thoughts-of-leaving items", "Frequencies by month and year group; thematic analysis"],
  ["5. Describe change over the pilot; explore early exit", "Student check at baseline and follow-up; consequences and honesty items; registry outcome file (if agreed)", "Paired tests; exploratory Firth regression"],
  ["6. Costed adoption plan and policy brief", "Cost log", "Cost per user and per contact; scale-up scenarios"],
 ], [3000, 3400, 2626]),
 gap(),
 h2("Appendix C: Colour Bands"),
 table(["Colour", "Meaning to the person", "Rule (summary)", "Offered"], [
  ["Green", "Coping well", "No flagged need (zone 1)", "Lessons, weekly pulse, check again in about 4 weeks"],
  ["Amber", "Feeling the strain; struggling", "Zones 2 and 3: mild or moderate symptoms, high life pressures, positive trauma or alcohol screen", "Lessons, welfare navigator, nurse call-back"],
  ["Red", "Needs care now", "Zone 4: any thought of self-harm, or severe symptoms", "Help numbers at once; same-day call-back"],
 ], [1200, 2200, 3300, 2326]),
 gap(),
 h2("Appendix D: Assumptions and Evidence Register"),
 p("This register separates what is established, what is assumed and what still has to be checked, so that the panel can see how far each statement can be trusted."),
 table(["Statement in the proposal", "Status", "Basis or action"], [
  ["Military personnel often do not seek help for mental health problems; stigma is a main barrier", "Established", "Sharp et al., 2015; Hoge et al., 2004"],
  ["Intimate partner violence and mental health conditions are common in military and student groups", "Established elsewhere; not measured in the KDF", "Cowlishaw et al., 2022; Kwan et al., 2020; Mugotitsa et al., 2025"],
  ["Suicide, family violence and debt are rising in the KDF community, and more students are leaving DCHS", "**No official figure found**; media reports and staff concerns only", "Treated as signals; the pilot measures the local picture, and the registry gives the leaving rate if it agrees"],
  ["People answer more favourably when they fear consequences", "Established for job-selection personality tests; assumed for mental health screens among students", "Birkeland et al., 2006; consequences and honesty items measure it here"],
  ["PHQ-9 and GAD-7 work in East Africa", "Established", "Gelaye et al., 2013; Mwangi et al., 2020"],
  ["Life-pressure, money, thoughts-of-leaving, consequences and readiness items", "Locally developed, not validated", "Pre-test and reliability (3.9.1); descriptive use only"],
  ["Expected share of users reaching a visit (20%)", "Assumption", "Table 3.2 gives the precision at other sample sizes"],
  ["Cost of a lost college place; nurse salary; running costs (Tables 5.2 and 5.3)", "Illustrative placeholders", "To be replaced with DCHS and hospital figures"],
  ["Time targets (8 hours, 48 hours, 7 days)", "Proposed targets", "Tested in the pilot; steering group may revise"],
  ["The platform works as described", "Tested on a local test database only", "Go or no-go list before use (3.9.2)"],
  ["Fit for deployment conditions after graduation", "Assumption", "To be tested with graduates posted to units in a later phase"],
  ["The survey can be hosted free without the college", "Standard practice for static sites and free survey tools; not yet done for this study", "Steps in the setup guide; the college is asked for support, not hosting (3.4.5)"],
 ], [3600, 2400, 3026]),
 gap(),
 h2("Appendix E: Platform and Data Package"),
 p("Supplied with this proposal: the phone app and staff console (a folder of static files); the database scripts; a setup guide (about 20 minutes); a jamovi guide with worked analyses; KoboToolbox forms with the same questions; a share link and QR code for students; and practice data with invented values. The practice data are for rehearsal only and are not findings."),
];
