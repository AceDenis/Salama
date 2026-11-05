"""Text of consent forms, interview guides, safety protocol and templates for the printable Data Collection Tools Pack.
Edit the bracketed [ ] items before submission to the ethics committee."""

CONTACTS = ["Principal investigator: WEDAH, BSc Nursing with Military Health student, Defence College of Health Sciences (DCHS), NDU-Kenya. Phone/email: [to be added].",
            "Supervisor: [name, title, phone, email].",
            "Ethics committee: [name of the committee that reviews this study, address, phone, email]. Approval number: [to be added].",
            "NACOSTI research licence number: [to be added]."]

def common_voluntary(extra=""):
    return ["Taking part is voluntary. You may say no, skip any question, or stop at any time, without giving a reason, and nothing will happen to you because of it." + extra]

CONSENTS = {
"student": dict(
    title="Information sheet and consent: DCHS student wellbeing check",
    who="For students aged 18 or older who are enrolled in any programme at the Defence College of Health Sciences (DCHS).",
    sections=[
     ("What is this study about?", ["Many students find a health-sciences programme with military discipline hard: a heavy workload, clinical placements, exams, money worries and time away from home. Asking for help early often makes the difference between staying and leaving. This study tests a short, private wellbeing check on your phone, with a nurse call-back and short lessons, to see whether it is easy to use, trusted, and useful in getting help early.",
       "**This is not an assessment.** It does not affect your marks, progression, discipline, sponsorship, posting or place."]),
     ("What will I be asked to do?", ["Answer questions on your phone (or on paper) about your mood, worry, stress, sleep, alcohol, money, thoughts about the course, and coping. It takes about 12 minutes. You will see a result that only you can read, with ideas for what to do next. You may be invited to repeat it about every four weeks and to answer a one-minute weekly pulse. At the end you may give feedback on how the service worked.",
       "There are three places where you can write your own suggestions. They are optional and help improve the service. Please do not write names or details that could identify anyone.",
       "**Optional choice 1.** You may choose to share one colour (green, amber or red) with the DCHS student-support office, so that they can offer help early. Only the colour is shared, never your scores or answers. You will see what would be shared before you decide, and you can withdraw it later.",
       "**Optional choice 2.** You may agree that the college registry's designated officer tells the research team, using your private code only, whether you stayed in the programme. This is used to see whether early support helps students stay."]),
     ("Is it voluntary?", ["Yes. You can decline, skip any question or stop at any time, and nothing will happen to you. Lecturers, examiners and commanders do not recruit you and do not see who took part. The college has given a written undertaking that results will not be used for marks, progression or discipline. [Attach the signed DCHS letter of support.]"]),
     ("What are the risks?", ["Some questions are about mood, frightening events, alcohol, money and loans, and home. They may make you feel uncomfortable. You can choose Prefer not to say where it is shown, and you can stop at any time. Help numbers are on every result screen. If your answers suggest you may be in danger, the phone shows help numbers straight away. Nobody is told unless you choose to ask a nurse to contact you.",
       "Money questions ask whether you have borrowed from an informal lender and whether anything was kept as security. We do not ask for a lender's name or place. You never have to answer these questions."]),
     ("What are the benefits?", ["You see your own result and get ideas for support. You can ask a nurse to contact you, ask a question without giving your name, and use short lessons on sleep, stress, exams and money. Your answers will help the college design better support for students."]),
     ("How will my information be kept private?", ["No name, admission number or phone number is stored with your answers. You get a private code (for example STUD-0001) that is the next number in order of joining and is linked to no name. Your answers are stored in a secure database that only the research team can read. Results are reported as group findings only; groups smaller than 10 are not reported.",
       "The college sees nothing about you unless you choose to share a colour.",
       "**Limits of confidentiality.** If you ask a nurse to contact you and tell the nurse that you are at immediate risk of serious harm to yourself or someone else, the nurse may need to take steps to keep you or others safe, and will explain this to you. Answers already sent cannot be traced back to you, so they cannot be removed one by one.",
       "Data are handled under the Data Protection Act, 2019. Anonymous research data will be kept for [number] years after the study and then deleted. Phone numbers given for a call-back are deleted [30] days after your request is closed."]),
     ("Who can I contact?", CONTACTS),
    ],
    statements=["I am 18 years or older and enrolled at DCHS.", "I have read this information (or it has been read to me) and I have had a chance to ask questions.",
                "I understand that taking part is voluntary, that it is not an assessment, and that I can stop at any time without anything happening to me.",
                "I agree to answer the wellbeing check, and for my anonymous answers to be used for research."],
    optional=["OPTIONAL: I may choose, at the end, to share one colour with the DCHS student-support office. (Yes / No)",
              "OPTIONAL: I agree that the college registry's designated officer may tell the research team whether I stayed in the programme, using my private code. (Yes / No)"]),
"personnel": dict(
    title="Information sheet and consent: serving personnel",
    who="For serving members of the Kenya Defence Forces aged 18 or older in the pilot units.",
    sections=[
     ("What is this study about?", ["Many people in uniform have stress, low mood, worry, drinking, money problems or problems at home, and many do not ask for help because they fear being seen as weak or fear that their commander will find out. This study tests a private wellbeing check on your phone with a nurse call-back, a welfare navigator and short lessons, to see whether it is easy to use, trusted, and helps people reach help sooner."]),
     ("What will I be asked to do?", ["Use the app for about three months as you wish: a private check (about 8 minutes), a one-minute weekly pulse, lessons, an anonymous question to a nurse, and a call-back request if you want one. You may also answer a short baseline survey (about 7 minutes) and an end-of-pilot feedback form (about 9 minutes). You may be asked to join a short interview."]),
     ("Is it voluntary?", ["Yes. Using the app or answering any question is your choice. Nothing you do or do not do will affect your service, posting, promotion, pay, care or family. Your commander will not know whether you took part."]),
     ("What are the risks?", ["Some questions are about mood, frightening events, alcohol, money and loans, and home. They may be uncomfortable. You can choose Prefer not to say where shown, skip other questions, or stop. Help numbers are always on screen. If your answers suggest danger, the phone shows help numbers immediately. Nobody is told unless you ask a nurse to contact you.",
       "Money questions ask about informal borrowing and anything kept as security (for example an ID card). We never ask for a lender's name. Nothing you answer is reported to a commander or used for discipline. [Describe here the written no-penalty route agreed with the Medical Services and Ministry of Defence, or state that none has been agreed and the questions are switched off.]"]),
     ("What are the benefits?", ["A result only you can read, practical next steps, and a real nurse call-back within [8 hours for urgent requests, 7 days for routine]. Your answers help design better services for personnel and families."]),
     ("How will my information be kept private?", ["No name, service number or unit detail that identifies you is stored with answers. You get a random private code. Individual answers are seen only by the research team. Commanders and supervisors receive only anonymous group figures, and never for groups of fewer than 10 people.",
       "**Limits of confidentiality.** If you ask a nurse to contact you and tell the nurse that you are at immediate risk of serious harm to yourself or others, the nurse may need to act to keep you or others safe, and will explain this to you. Data are handled under the Data Protection Act, 2019, and kept for [number] years. Phone numbers for call-backs are deleted [30] days after the request is closed."]),
     ("Who can I contact?", CONTACTS),
    ],
    statements=["I am 18 years or older and a serving member of the KDF.", "I have read this information (or it has been read to me) and I have had a chance to ask questions.",
                "I understand that taking part is voluntary and that I can stop at any time without any effect on my service or care.",
                "I agree that my anonymous answers may be used for research."], optional=[]),
"family": dict(
    title="Information sheet and consent: family members of serving personnel",
    who="For spouses, partners, parents and other adult family members (18 or older).",
    sections=[
     ("What is this study about?", ["Families see stress, money worries and problems at home first, yet often have nowhere confidential to turn. This study tests a private phone service with a nurse call-back and a welfare navigator, and asks families what would make it useful and safe."]),
     ("What will I be asked to do?", ["Answer a short survey (about 7 minutes) and, if you wish, use the private check, lessons and the ask-the-nurse box. You may be invited to a small group discussion of about 8 people (about 90 minutes)."]),
     ("Is it voluntary?", ["Yes. Your choice to take part, or not, will not affect your family member's service, pay, posting or care, and they will not be told whether you took part."]),
     ("What are the risks?", ["Some questions are about stress, money, and safety at home. They may be upsetting. You can skip any question or stop. The app has a Quick exit button that leaves the page at once. Help numbers, including the free gender violence helpline 1195 and the police 999 or 112, are always on screen. If you are in danger, please call for help first. Please use a phone and a place where you feel safe."]),
     ("What are the benefits?", ["A private result, practical next steps and a nurse call-back. Your views will shape a better service."]),
     ("How will my information be kept private?", ["No names are stored with answers. In group discussions, we ask everyone to keep what is said private, but we cannot guarantee that others will do so. **Limits of confidentiality:** if you tell a nurse or the researcher that a child or an adult is in immediate danger of serious harm, we may need to act to protect them, and will tell you first where possible. Data are handled under the Data Protection Act, 2019."]),
     ("Who can I contact?", CONTACTS),
    ],
    statements=["I am 18 years or older.", "I have read this information (or it has been read to me) and have had a chance to ask questions.",
                "I understand that taking part is voluntary and that I can stop at any time.", "I agree that my anonymous answers may be used for research."],
    optional=["For group discussions only: I agree to the discussion being audio recorded. (Yes / No)"]),
"informant": dict(
    title="Information sheet and consent: key informants, experts and Delphi panellists",
    who="For clinicians, chaplains, welfare officers, commanders and administrators, legal, ethics and data-protection experts, ICT staff, and DCHS lecturers, counsellors and registry staff.",
    sections=[
     ("What is this study about?", ["The study will design and test a confidential wellbeing check and nurse call-back service for KDF personnel, families and DCHS students. We are asking people who work in this area what is changing, what is needed, and what rules and safeguards would make such a service safe, trusted and worth adopting."]),
     ("What will I be asked to do?", ["Complete a questionnaire (about 14 minutes), and/or take part in an interview of about 45 minutes (audio recorded only with your permission), and/or rate statements in a Delphi panel of two or three short rounds (about 15 minutes each)."]),
     ("Is it voluntary?", ["Yes. You may skip any question, decline recording, or withdraw at any time. Your decision will not affect your work."]),
     ("What are the risks and benefits?", ["There is little risk. Some topics (suicide, violence, debt and held ID cards) are sensitive. Please speak in general terms and from your own role. **Do not give names, service numbers or any detail that could identify a person.** If you do, we will remove it. Benefits: your views will shape the service and its safeguards."]),
     ("How will my information be kept private?", ["Your answers are stored without your name. In reports, quotations will be anonymised and your role will be described only broadly (for example, \"a clinician\"). Interview recordings are typed up, then deleted, and transcripts are stored securely. Data are handled under the Data Protection Act, 2019. If you tell us about a person who is at immediate risk of serious harm, we may need to act to protect them."]),
     ("Who can I contact?", CONTACTS),
    ],
    statements=["I have read this information (or it has been read to me) and have had a chance to ask questions.", "I understand that taking part is voluntary and that I can stop at any time.",
                "I agree to take part."], optional=["I agree to the interview being audio recorded. (Yes / No)", "I agree that anonymised quotations may be used in reports. (Yes / No)"]),
}

KII_INTRO = ["Thank you for your time. I am WEDAH, a BSc Nursing with Military Health student at DCHS. I am studying how a confidential wellbeing check and nurse call-back service could work for personnel, families and DCHS students.",
             "This is voluntary. You can skip any question or stop. Please speak generally and do not give names, service numbers or details that could identify a person. May I record this? (Check consent form.)"]
KII_CORE = [
 "What is your role, and how does it bring you into contact with mental health, family or money problems among personnel, families or students?",
 "Over the last two years, what has changed? What are you seeing more of, less of, or newly? (Probe: suicide and self-harm, alcohol, anger and violence at home, bereavement, relationship breakdown, after deployment.)",
 "What do you think stops people coming forward early? (Probe: stigma, fear of commanders, doubts about records, discipline, distance, tempo.)",
 "What is in place today when someone is struggling, and how well does it work? What is missing?",
 "Money: what do you see about borrowing, informal lenders, cards or ID kept as security, harassment by lenders, or salary deductions? How does it affect people's wellbeing and behaviour? (Probe in general terms only; no names.)",
 "What would make someone come forward about a loan or a card held by a lender? What would stop them? What rule or route would help?",
 "Here is the idea: a private check on the phone, a colour result only the person sees, a nurse who calls back within a set time, a welfare navigator, short lessons, and an anonymous question box. What would make it useful? What could go wrong?",
 "What would a safe response look like for someone whose answers suggest high risk? What is the longest acceptable time before first contact?",
 "Who should see what? (Probe: the person only; the nurse; the welfare officer; group figures to commanders; never individuals.) What would break trust?",
 "What would you need to see to support a three-month pilot in one or two units? What approvals are needed? Could a nurse answer call-backs within the agreed time?",
 "If the service were found to work, what would it take, and what would it cost, for the Medical Services or the college to adopt it?",
 "What are the top three changes that would most improve mental health care for personnel and families?",
 "Is there anything I have not asked that I should have?"]
KII_PROBES = [
 ("Clinicians, psychiatrists, counsellors and nurses", ["How do people present, and how late? What risk assessment and follow-up steps should the call-back follow? How many call-backs could a nurse take in a week? What should the written safety protocol say? Which numbers and referral routes should be on screen?"]),
 ("Chaplains and faith leaders", ["What do people bring to you that they do not bring to a clinic? What do you hear about debt, lenders and cards? How could you and the nurse work together, with consent, on referral?"]),
 ("Welfare officers and social workers", ["What money, housing and family problems do you see, and what can you actually offer? What would the navigator need to say to be useful? What would a no-penalty route for held cards need to include? Who decides?"]),
 ("Commanders and administrators", ["What do you need to know as a commander, and what must you not know? What group figures would help you act? How could protected time be given while answers stay private? What would worry you?"]),
 ("Military police, legal and gender-violence desks", ["How are cases of violence at home, harassment by lenders and false loss reports handled now? What are the legal limits of confidentiality and duties to report? What should the service say to a person who discloses these?"]),
 ("DCHS lecturers, counsellors, registrar and admissions staff", ["What reasons do students give for deferring, withdrawing or being discontinued, and when do you first notice trouble? How are students supported now? What are the legal and fairness risks of any wellbeing check around selection? What firewall between the check and admission decisions would be credible? Should interviewers see anything? (Probe the colour-only option and its risks.) What would a written undertaking need to say?"]),
 ("ICT, records and data-protection staff", ["Where should data be hosted (Kenya, free cloud, hospital server)? What registrations and assessments are needed? How should access be controlled and logged? How would the service connect to existing records later?"]),
]
FGD_FAMILY = [
 "Warm-up: please introduce yourself by first name only, or a name you choose. (Ground rules: keep what is said here private; no real names of other people; you may leave or pass at any time.)",
 "What worries do families of serving members have most today? (Probe: long absences, safety, money, children, loneliness, tension at home.)",
 "Where do families go for help now? What gets in the way?",
 "What do you hear about debt, loans and lenders in service families? How does it affect homes? (General terms only.)",
 "If a private phone service existed for families, what would you want from it? What would make you trust it? What would make you avoid it?",
 "What would make it safe for someone worried about violence at home to use it? (Probe: quick exit, no messages left on the phone, call-back timing.)",
 "Who else should be involved: a chaplain, a welfare officer, peers? In what way?",
 "What should we change in the questions or the app before it is tested?",
 "Closing: what is the one thing you most want the Medical Services and the college to hear?"]
FGD_STUDENTS = [
 "Ground rules, then: how did you feel when you first started, or when you applied?",
 "What makes it hard to stay in the programme? (Probe: workload, placements, discipline, fees, family, homesickness, debt.)",
 "Where do students go for help, and what stops them going? Would you talk to someone at the college? Who?",
 "How would you feel about an online wellbeing check at application? After admission? Who should see the result? What would make you answer honestly? What would make you answer in a way that looks good?",
 "What would you want the college to do with a colour result (green, amber or red)? What would you not want?",
 "What should we change in the app or the questions?"]

SAFETY = [
 ("When the service must act", ["**Red band or any thought of self-harm (PHQ-9 item 9 above zero):** the phone shows help numbers at once and offers a same-day call-back. **Same-day call-back requests:** the nurse aims to make first contact within [8] hours. **Routine requests:** within [7] days. **Anonymous questions:** reply within [2] working days."]),
 ("Who is on call, and when", ["**Cover hours:** [07:00 to 21:00, every day], by a rota of [two] trained nurses with the nurse lead as back-up. The times in this protocol are counted from when a request is received during cover hours. A request received outside cover hours is counted from the start of the next cover period.",
   "**Outside cover hours:** the phone says so and shows the duty medical officer, the emergency number and the national lines. A red-band result or any thought of self-harm also sends a flag to the duty medical officer by the route agreed with the hospital [to be confirmed]. The study does not promise overnight nurse cover. If no after-hours route is agreed, the pilot runs on the cover hours above and the information sheet says so.",
   "**Load check:** at every steering group meeting the nurse lead compares requests per week with nurse minutes. If the rota cannot meet the targets, enrolment is paused until it can."]),
 ("What the nurse does", ["1. Introduce yourself, confirm it is a safe time to talk, and say what is private and the limits of confidentiality.",
   "2. Ask directly and calmly about thoughts of suicide, plans, means and intent. Asking does not put the idea in a person's head.",
   "3. Ask about safety at home and about threats from lenders. Keep messages and call logs as evidence when the person agrees.",
   "4. Agree a safety plan: who to call, where to go, what to remove or hand over, what to do tonight. Give the numbers on the card.",
   "5. Arrange a visit (target within [48] hours for high risk) with the medical officer or psychiatrist, and book it before the call ends. Record the time of first contact and of the visit.",
   "6. Follow up within [72] hours, and again after the visit. Close the request only when the person is linked to care or declines care."]),
 ("If the person cannot be reached", ["Call [3] times over [2] hours and send one neutral message (no mention of the service name if the phone may be shared). For red or same-day requests, tell the duty medical officer, who decides on a welfare check by the agreed route. The consent form tells people that this may happen. Record every attempt."]),
 ("Imminent danger", ["If the person is in danger now: stay on the line, call the duty medical officer and the police (999 or 112), and arrange transport to the nearest health facility. Do not leave the person alone."]),
 ("After the call", ["Debrief with the clinical supervisor the same day. Nurses who take red-band calls have access to supervision and rest. The ethics focal person is told of every serious event within [24 hours], with no identifying detail."]),
 ("Numbers on the card (confirm before go-live)", ["Nurse on call (07:00 to 21:00) +2547xxxxxxxx [placeholder] · Duty medical officer (after hours) +2547xxxxxxxx [placeholder] · DCHS student support office +2547xxxxxxxx [placeholder] · Police and emergency 999 or 112 · Gender violence helpline 1195 · Kenya Red Cross counselling 1199 · National mental health line 1190 · Befrienders Kenya +254 722 178 177 · Local nurse line [add] · Duty medical officer [add] · Chaplain [add] · Welfare officer [add]."]),
]
BANDS = [
 ("Green: Coping well", "Zone 1", "No flagged support need. PHQ-9 and GAD-7 below 5 and life pressures below the high level.", "Lessons, weekly pulse, check again in about 4 weeks."),
 ("Amber: Feeling the strain", "Zone 2", "PHQ-9 or GAD-7 of 5 or more, or a high life-pressure load, with no moderate or high-risk flag.", "Small steps, lessons, ask the nurse, welfare navigator."),
 ("Amber: Struggling", "Zone 3", "Moderate flag: PHQ-9 10 to 19, GAD-7 10 or more, PC-PTSD-5 positive (3 or more), AUDIT-C 4 or more, unsafe at home, or worry that own anger or drinking affects home.", "Nurse call-back offered within 7 days."),
 ("Red: Needs care now", "Zone 4", "High flag: any thought of being better off dead or of self-harm; PHQ-9 of 20 or more; or PHQ-9 of 15 or more with GAD-7 10 or more or a positive trauma screen.", "Same-day call-back offered (target 8 hours), help numbers shown, safety protocol."),
]
BAND_NOTE = "Money items (informal borrowing, security held, lost-card report, threats) do not change the band. They trigger money and welfare help. The colour band shared with the college support office is: Green = zone 1; Amber = zones 2 and 3; Red = zone 4."

MATRIX = [
 ("1. Adapt the service and questions to DCHS students", "Expert review sheet (five DCHS staff); testing with 10 to 15 students; three open suggestion boxes; comment box in the end-of-pilot form", "Content validity index; reading and timing results; suggestions register (themes and decisions)"),
 ("2. Run a pilot at DCHS (4 weeks to 3 months)", "Service log recorded by the database: requests, status times, visits; weekly engagement counts; change log", "Counts and proportions; run charts; fidelity to the protocol"),
 ("3. Measure uptake, time to contact, referral completion, usability, perceived confidentiality, help-seeking intention", "Usage events; call-back clock (database); baseline and end-of-pilot help-seeking and confidentiality items; end-of-pilot form with System Usability Scale and acceptance (UTAUT) items", "Median hours to first contact and proportion within target; proportion of requests reaching a visit; SUS mean (68 benchmark); paired comparison of intention and confidentiality"),
 ("4. Describe stressors students name, including money, loans and reasons for thinking of leaving", "Money, loans and bills items; tick-up-to-3 stressor list; stressor in own words; weekly pulse cue; thoughts-of-leaving items", "Frequencies by month and year group; cross-tabulation with colour band; thematic analysis of own-words text"),
 ("5. Describe change over the pilot; explore links between baseline signals and early exit (support, not exclusion)", "Student check at baseline and follow-up; thoughts-of-leaving items; perceived consequences and honesty items; registry outcome file (code, status, month, reason) if agreed", "Paired t-test or Wilcoxon on PHQ-9, GAD-7, AUDIT-C and resilience; exploratory Firth logistic regression for early exit"),
 ("6. Costed adoption plan and policy brief", "Cost log (nurse minutes, training, airtime and data, hosting)", "Cost per active user and per contact; scale-up scenarios; policy brief"),
]

PROTECTIONS = [
 ("You choose.", "You can say no, skip any question, or stop at any time. Nothing will happen to you."),
 ("This is not an assessment.", "It does not affect your marks, progression, discipline, sponsorship, posting or place."),
 ("No name.", "No name, admission number, service number or phone number is stored with your answers. You get a private code."),
 ("Staff cannot see you.", "Lecturers, commanders and college managers never see individual answers. Results are reported for groups of 10 or more only."),
 ("Your result is yours.", "Only you see it. A colour goes to the support office only if you choose to share it, and you can withdraw it."),
 ("Help is close.", "Help numbers are on every result. A nurse can contact you if you ask."),
 ("Approved and supervised.", "Ethics approval number: [to be added]. Researcher: WEDAH, BSc Nursing with Military Health, DCHS. Supervisor and ethics committee contacts: [to be added]. The study follows the Data Protection Act, 2019."),
 ("One limit.", "If you tell a nurse that you or someone else is in immediate danger, the nurse may need to act to keep people safe."),
]

SUGGESTIONS_LOG = [("Date", "Source (box 1, 2, 3, end-of-pilot, expert sheet)", "Suggestion (no names)", "Theme", "Decision (adopt now / adopt later / decline)", "Reason", "Protocol version if adopted")]

PRINT_PROCEDURE = [
 "Printed copies are for students without a smartphone, or who prefer paper. The printed form has no name or number field.",
 "Hand out the information sheet first and let the student read the protections. Consent is by tick-box. No signature is taken, so no name is recorded.",
 "Students complete the form alone and drop it into a sealed box. No lecturer, examiner or commander is present at the box.",
 "The researcher opens the box in the presence of the supervisor or a witness, counts the forms, and types them into the same questionnaire (KoboToolbox data-entry form) on a laptop. Each paper form is given the next number (P-001, P-002) written in the corner, and the paper forms are then kept locked until the end of the study and destroyed as the ethics committee directs.",
 "Printed forms cannot show a colour result or offer a call-back by themselves, so the back page carries help numbers (placeholders +2547xxxxxxxx until adopted) and a tear-off slip: 'I would like a nurse to contact me' with a number to call.",
]

COSTLOG = [("Date", "Staff member (role)", "Activity (call-back, visit, training, supervision, admin)", "Minutes", "Airtime or data (KES)", "Other cost (KES, describe)")]
