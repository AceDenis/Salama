"""
Single source of truth for every question in the Salama Check-In platform.

tools/build.py reads this file and generates
  - the questionnaires inside web/index.html
  - the flat, jamovi-ready SQL views (database/02_views.sql)
  - the codebook (docs/codebook.csv)

Change a question here, run `python3 tools/build.py`, and the app, the database
views and the codebook all stay in step.
"""

# ------------------------------------------------------------------ scales ---
AGREE5 = [(1, "Strongly disagree"), (2, "Disagree"), (3, "Neutral"), (4, "Agree"), (5, "Strongly agree")]
LIKELY5 = [(1, "Very unlikely"), (2, "Unlikely"), (3, "Unsure"), (4, "Likely"), (5, "Very likely")]
FREQ4 = [(0, "Not at all"), (1, "Several days"), (2, "More than half the days"), (3, "Nearly every day")]
YESNO = [(1, "Yes"), (0, "No")]
YESNOPNS = [(1, "Yes"), (0, "No"), (9, "Prefer not to say")]
PROBLEM3 = [(0, "Not a problem"), (1, "A bit of a problem"), (2, "A big problem")]
TREND5 = [(1, "Decreased a lot"), (2, "Decreased a little"), (3, "About the same"),
          (4, "Increased a little"), (5, "Increased a lot"), (9, "Do not know")]
IMPORTANCE5 = [(1, "Not important"), (2, "Slightly important"), (3, "Moderately important"),
               (4, "Very important"), (5, "Essential")]
ADEQUACY5 = [(1, "Very poor"), (2, "Poor"), (3, "Fair"), (4, "Good"), (5, "Very good"), (9, "Do not know")]
NPS11 = [(i, str(i)) for i in range(0, 11)]
AWARE3 = [(1, "Yes"), (2, "A little"), (3, "No")]


def item(id, text, options=None, type="choice", measure=None, optional=False, show_if=None, label=None,
         group=None, text_family=None, gate=None, sensitive=False, max_checks=None):
    """One question.
    type        choice (one answer) | check (tick = 1, untick = 0) | text (free text)
    measure     nominal | ordinal | scale   (jamovi measure type)
    show_if     (item_id, [values])   only asked when that answer is one of the values
    gate        ([item_ids], minimum) adaptive branching: only asked when the sum of those answers >= minimum
    text_family replacement wording for family members
    sensitive   True = can be switched off in web/config.js (DISABLED_ITEMS) if ethics or legal advice requires
    max_checks  for a tick group: the most boxes a person may tick
    """
    if measure is None:
        measure = "nominal"
    return dict(id=id, text=text, options=options or [], type=type, measure=measure, optional=optional,
                show_if=show_if, label=label or text[:80], group=group, text_family=text_family,
                gate=gate, sensitive=sensitive, max_checks=max_checks)


def sec(id, title, items, intro=None, scale=None):
    return dict(id=id, title=title, intro=intro, items=items, scale=scale)


# ------------------------------------------------------ shared question sets ---
def helpseeking_section():
    sources = [("friend", "A friend or buddy"), ("family", "Family"), ("chaplain", "Chaplain"),
               ("welfare", "Welfare officer"), ("nurse", "Nurse"), ("doctor", "Doctor"),
               ("psych", "Psychologist or counsellor"), ("cmdr", "Commander or supervisor"),
               ("faith", "Faith or traditional healer outside the unit"), ("other", "Someone else")]
    reasons = [("weak", "I was afraid of being seen as weak"),
               ("cmdr", "I was afraid my commander would treat me differently"),
               ("conf", "I was afraid my record would not stay confidential"),
               ("where", "I did not know where to go"), ("time", "No time because of duty"),
               ("pass", "I thought it would pass by itself"), ("staff", "No trained staff close to me"),
               ("cost", "Cost or transport")]
    items = [
        item("need12", "In the last 12 months, did you feel you needed help for stress, low mood, anxiety, sleep, anger, money worries or alcohol use?",
             YESNOPNS, label="Needed help in last 12 months"),
        item("sought12", "Did you seek help?", YESNO, show_if=("need12", [1]), label="Sought help in last 12 months"),
    ]
    for k, t in sources:
        items.append(item("src_" + k, t, type="check", show_if=("sought12", [1]),
                          group="Who did you go to? (tick all that apply)", label="Help source: " + t, optional=True))
    for k, t in reasons:
        items.append(item("why_" + k, t, type="check", show_if=("sought12", [0]),
                          group="Why did you not seek help? (tick all that apply)", label="Reason no help: " + t, optional=True))
    items.append(item("firstgo", "If you needed help today, where would you go first?",
                      [(0, "Nobody"), (1, "A friend or buddy"), (2, "Family"), (3, "Chaplain"), (4, "Welfare officer"),
                       (5, "Nurse"), (6, "Doctor"), (7, "Psychologist or counsellor"), (8, "A phone app or website"),
                       (9, "Alcohol or something else")], label="First choice of help today"))
    return sec("helpseek", "Getting help", items)


def stigma_section():
    items = [
        item("st1", "Seeking help would make me look weak.", AGREE5, measure="ordinal", label="Stigma: look weak",
             text_family="Seeking help would make our family look weak."),
        item("st2", "My commander would treat me differently if I sought help.", AGREE5, measure="ordinal",
             label="Stigma: commander treats differently",
             text_family="My family member's commander would treat them differently if we sought help."),
        item("st3", "My records would not stay confidential.", AGREE5, measure="ordinal", label="Stigma: records not confidential",
             text_family="Our records would not stay confidential."),
        item("st4", "Seeking help would harm my career (promotion, postings or deployment).", AGREE5, measure="ordinal",
             label="Stigma: harm career", text_family="Seeking help would harm my family member's career."),
        item("st5", "My colleagues would think less of me.", AGREE5, measure="ordinal", label="Stigma: colleagues think less",
             text_family="Other families in the unit would think less of us."),
        item("co1", "I worry that a screening result could reach my commander.", AGREE5, measure="ordinal",
             label="Confidentiality fear: result reaches commander",
             text_family="I worry that a screening result could reach my family member's commander."),
        item("co2", "I would prefer to get a first check privately on my phone.", AGREE5, measure="ordinal", label="Prefer private phone check"),
        item("co3", "I would trust a phone service more if only a nurse could see my result.", AGREE5, measure="ordinal",
             label="Trust more if only nurse sees"),
        item("co4", "I would be more likely to use a service that a trusted buddy or peer champion recommends.", AGREE5,
             measure="ordinal", label="More likely if buddy recommends"),
        item("co5", "I would be afraid to admit a money problem (such as a loan or a held ID card) because of discipline.", AGREE5,
             measure="ordinal", label="Fear of discipline if money problem admitted",
             text_family="My family member would be afraid to admit a money problem (such as a loan or a held ID card) because of discipline."),
    ]
    return sec("stigma", "What you think about getting help", items,
               intro="There are no right or wrong answers. Choose the answer closest to what you honestly think.")


def intention_items(prefix_ids=None):
    return [
        item("hsi_nurse", "How likely would you be to talk to a nurse?", LIKELY5, measure="ordinal", label="Intention: nurse"),
        item("hsi_chaplain", "How likely would you be to talk to a chaplain?", LIKELY5, measure="ordinal", label="Intention: chaplain"),
        item("hsi_welfare", "How likely would you be to talk to a welfare officer?", LIKELY5, measure="ordinal", label="Intention: welfare officer"),
        item("hsi_buddy", "How likely would you be to talk to a buddy or friend in the unit?", LIKELY5, measure="ordinal", label="Intention: buddy"),
        item("hsi_cmdr", "How likely would you be to talk to your commander?", LIKELY5, measure="ordinal", label="Intention: commander"),
        item("hsi_app", "How likely would you be to use a private phone service?", LIKELY5, measure="ordinal", label="Intention: phone service"),
        item("hsi_none", "How likely would you be to talk to nobody at all?", LIKELY5, measure="ordinal", label="Intention: nobody"),
    ]


def intention_section():
    return sec("intent", "If you had a personal or emotional problem", intention_items(),
               intro="Choose how likely you would be to do each of the following.")


def awareness_section():
    return sec("aware", "Knowing where to go", [
        item("aw_support", "Do you know where to get mental health support in your unit or garrison?", AWARE3, measure="ordinal",
             label="Aware of mental health support"),
        item("aw_gbv", "Do you know where to get help if there is violence or fear at home?", AWARE3, measure="ordinal",
             label="Aware of help for violence at home"),
    ])


def digital_section():
    return sec("digital", "Your phone", [
        item("phone", "Do you have a smartphone?", [(1, "Yes, my own"), (2, "Shared with others"), (3, "No")], label="Smartphone access"),
        item("data", "How often can you use mobile data or Wi-Fi?", [(1, "Regularly"), (2, "Sometimes"), (3, "Rarely")],
             measure="ordinal", label="Data access"),
        item("appcomfort", "How comfortable are you using phone apps?",
             [(1, "Not comfortable"), (2, "A little"), (3, "Fairly"), (4, "Comfortable"), (5, "Very comfortable")],
             measure="ordinal", label="App comfort"),
    ])


# ---- money, loans and held cards -------------------------------------------------
# Wording is neutral, anonymous and non-judgemental. Nothing asks for a lender's name, a place or a service number.
STRESSORS = [("money", "Money or debt"), ("lender", "Pressure from a lender or someone I owe"), ("posting", "Posting, deployment or being away"),
             ("homefight", "Conflict or tension at home"), ("kids", "Children, school fees or family needs"), ("health", "My health or illness"),
             ("work", "Work, leadership, discipline or workload"), ("loss", "A loss or bereavement"), ("online", "Things I see online or in the news"),
             ("lonely", "Loneliness"), ("alcohol", "Alcohol"), ("safety", "Fear for safety (on duty or at home)"),
             ("career", "Career, promotion or discharge"), ("other", "Something else")]


def money_section(family=False, applicant=False):
    sec_ = _money_section(family)
    if applicant:
        for it in sec_["items"]:
            if it["id"] == "sec_id":
                it["text"] = "An ID card (national, student or military)"
            if it["id"] == "fm_share":
                it["text"] = "About what share of your money or allowance each month goes on repaying loans?"
            if it["id"] == "fm_needs":
                it["text"] = "Over the last month, how often did you run out of money for basic needs (food, rent, fees, transport) before the next money came in?"
            if it["id"] == "fm_know":
                it["text"] = "Do you know where to get safe, confidential money help (college welfare, your sponsor, a SACCO or a financial counsellor)?"
    return sec_


def _money_section(family=False):
    f = family
    return sec("money", "Money, loans and bills", [
        item("fm_needs", "Over the last month, how often did you run out of money for basic needs (food, rent, school fees, transport) before the next pay day?",
             [(0, "Never"), (1, "Once or twice"), (2, "Several times"), (3, "Most of the month")], measure="ordinal",
             label="Ran out of money for basic needs",
             text_family="Over the last month, how often did your household run out of money for basic needs (food, rent, school fees, transport) before the next pay day?"),
        item("fm_share", "About what share of your pay each month goes on repaying loans and deductions?",
             [(0, "None"), (1, "Less than a quarter"), (2, "A quarter to a half"), (3, "More than half"), (9, "Prefer not to say")],
             label="Share of pay on repayments and deductions",
             text_family="About what share of the household income each month goes on repaying loans and deductions?"),
        item("fm_borrow", "In the last 3 months, did you borrow money from a lender who is not a bank, SACCO or welfare scheme? "
             "For example, a daily, weekly or monthly lender ('shylock') who calls or messages you for repayment.",
             [(0, "No"), (1, "Yes, once or twice"), (2, "Yes, several times"), (9, "Prefer not to say")],
             label="Borrowed from informal lender in last 3 months", sensitive=True,
             text_family="In the last 3 months, did anyone in your household borrow money from a lender who is not a bank, SACCO or welfare scheme? "
                         "For example, a daily, weekly or monthly lender ('shylock')."),
        item("fm_cost", "Did you have to repay much more than you borrowed (for example 30% or more extra within a month)?",
             [(1, "Yes"), (0, "No"), (2, "Not sure")], show_if=("fm_borrow", [1, 2]), label="Repayment much higher than borrowed", sensitive=True,
             text_family="Did your household have to repay much more than was borrowed (for example 30% or more extra within a month)?"),
        item("sec_atm", "A bank or ATM card", type="check", show_if=("fm_borrow", [1, 2]), optional=True, sensitive=True,
             group="Did a lender keep anything as security? (tick all that apply)", label="Security held: ATM or bank card"),
        item("sec_phone", "A phone", type="check", show_if=("fm_borrow", [1, 2]), optional=True, sensitive=True,
             group="Did a lender keep anything as security? (tick all that apply)", label="Security held: phone"),
        item("sec_id", "A military ID card", type="check", show_if=("fm_borrow", [1, 2]), optional=True, sensitive=True,
             group="Did a lender keep anything as security? (tick all that apply)", label="Security held: military ID card",
             text_family="A military ID card (of a family member)"),
        item("sec_doc", "Other documents (for example a title deed or logbook)", type="check", show_if=("fm_borrow", [1, 2]), optional=True, sensitive=True,
             group="Did a lender keep anything as security? (tick all that apply)", label="Security held: other documents"),
        item("sec_item", "Other belongings", type="check", show_if=("fm_borrow", [1, 2]), optional=True, sensitive=True,
             group="Did a lender keep anything as security? (tick all that apply)", label="Security held: other belongings"),
        item("sec_none", "Nothing", type="check", show_if=("fm_borrow", [1, 2]), optional=True, sensitive=True,
             group="Did a lender keep anything as security? (tick all that apply)", label="Security held: nothing"),
        item("fm_lost", "Have you reported a card or ID as lost, or asked for a replacement, when it was actually being held by a lender?",
             YESNOPNS, show_if=("sec_id", [1]), label="Reported ID/card lost while held by lender", sensitive=True,
             text_family="Has a family member reported a card or ID as lost, or asked for a replacement, when it was actually being held by a lender?"),
        item("fm_threat", "Has a lender or someone you owe threatened, shamed or harassed you or your family (calls, messages to your contacts, visits)?",
             YESNOPNS, show_if=("fm_borrow", [1, 2]), label="Threatened or harassed by lender", sensitive=True,
             text_family="Has a lender or someone you owe threatened, shamed or harassed your household (calls, messages to contacts, visits)?"),
        item("fm_effect", "How much have money worries affected your sleep, mood or home life this month?",
             [(0, "Not at all"), (1, "A little"), (2, "A lot"), (3, "Extremely")], measure="ordinal", label="Effect of money worries on sleep, mood, home"),
        item("fm_know", "Do you know where to get safe, confidential money help (welfare officer, SACCO, financial counselling)?",
             AWARE3, measure="ordinal", label="Knows where to get money help"),
    ], intro="These questions are anonymous. No lender's name, place or service number is asked for or kept. "
             "Nothing you answer here is reported to a commander. You can choose Prefer not to say.")


def betting_section():
    """Betting and gambling. Anonymous, optional. Items bt2 and bt3 follow the published Lie/Bet screen (to be checked against the source)."""
    return sec("betting", "Betting", [
        item("bt1", "In the last 3 months, how often have you bet money (sports betting, casino, lottery or betting apps)?",
             [(0, "Never"), (1, "Monthly or less"), (2, "Weekly"), (3, "Most days"), (9, "Prefer not to say")], measure="ordinal",
             label="Betting frequency, last 3 months", sensitive=True),
        item("bt2", "Have you ever felt the need to bet more and more money?", YESNOPNS, show_if=("bt1", [1, 2, 3]),
             label="Lie/Bet: need to bet more", sensitive=True),
        item("bt3", "Have you ever had to lie to people important to you about how much you bet?", YESNOPNS, show_if=("bt1", [1, 2, 3]),
             label="Lie/Bet: lied about betting", sensitive=True),
        item("bt4", "Has betting led you to borrow money, including from an informal lender?", YESNOPNS, show_if=("bt1", [1, 2, 3]),
             label="Betting led to borrowing", sensitive=True),
    ], intro="These questions are anonymous and optional. Nothing you answer here is reported to a commander. You can choose Prefer not to say.")


def police_section(student=False):
    """Contact with civilian police and discipline. Anonymous, optional, no names, places or details are asked."""
    return sec("police", "Contact with civilian police", [
        item("po1", "In the last 12 months, have you had an argument, confrontation or physical altercation with a civilian police officer (for example at a roadblock, on patrol, in a bar or in a dispute with a civilian)?",
             [(0, "No"), (1, "Yes, once"), (2, "Yes, more than once"), (9, "Prefer not to say")], measure="ordinal",
             label="Altercation with civilian police, last 12 months", sensitive=True),
        item("po2", "What was the main setting?",
             [(1, "Traffic or a roadblock"), (2, "A bar, club or social place"), (3, "A dispute with a civilian (money, neighbour, relationship)"),
              (4, "A debt or loan matter"), (5, "While off duty or on leave"), (6, "Something else"), (9, "Prefer not to say")],
             show_if=("po1", [1, 2]), label="Setting of police altercation", sensitive=True),
        item("po3", "Was alcohol involved?", YESNOPNS, show_if=("po1", [1, 2]), label="Alcohol involved in police altercation", sensitive=True),
        item("po4", "What happened afterwards?",
             [(1, "Sorted out on the spot"), (2, "Detained for a short time"), (3, "Charged or taken to court"), (4, "Reported to my unit or college"), (9, "Prefer not to say")],
             show_if=("po1", [1, 2]), label="Outcome of police altercation", sensitive=True),
        item("po5", "Did you get help afterwards (welfare, legal officer, a senior or a friend)?",
             [(1, "Yes"), (0, "No"), (2, "I did not know who to ask"), (9, "Prefer not to say")],
             show_if=("po1", [1, 2]), label="Got help after police altercation", sensitive=True),
        item("po6", "When I am off duty, I feel civilian police treat me fairly.", AGREE5, measure="ordinal", label="Feels fairly treated by civilian police"),
        item("po7", "I worry that a small incident with civilian police could become a discipline or legal case that harms my career.", AGREE5,
             measure="ordinal", label="Worry small police incident becomes discipline case"),
        item("po8", "Do you know who to contact (legal officer, welfare officer or military police liaison) if you are held by civilian police?",
             AWARE3, measure="ordinal", label="Knows who to contact if held by police"),
    ], intro="These questions are anonymous and optional. No names, places, dates or service numbers are asked. "
             "Nothing you answer here is reported to a commander or to the police. You can choose Prefer not to say.")


STRESSORS_STUDENT = [("fees", "Fees, upkeep or money"), ("lender", "Pressure from a lender or someone I owe"), ("exams", "Exams, grades or fear of failing"),
                       ("away", "Being far from family or home"), ("homefight", "Conflict or tension at home"), ("health", "My health or illness"),
                       ("future", "Worry about the future or about my progress on the course"), ("loss", "A loss or bereavement"), ("online", "Things I see online or in the news"),
                       ("lonely", "Loneliness or fitting in"), ("alcohol", "Alcohol or drugs"), ("safety", "Fear for my safety"), ("other", "Something else")]


def stressor_section(applicant=False):
    return sec("stressors", "In your own words", [
        item("sr_" + k, t, type="check", optional=True, max_checks=3,
             group="What are the biggest things weighing on you now? (tick up to 3)", label="Stressor ticked: " + t)
        for k, t in (STRESSORS_STUDENT if applicant else STRESSORS)
    ] + [
        item("sr_text", "In your own words, what is weighing on you most right now? Please do not write names, lender details, service numbers or places.",
             type="text", optional=True, label="Stressor in own words"),
    ], intro="This helps the pilot understand pressures in the way people themselves describe them.")


# ------------------------------------------------------------------ FORMS ---
FORMS = {}

BG_P = [
    item("age", "Age group", [(1, "18 to 24"), (2, "25 to 34"), (3, "35 to 44"), (4, "45 to 54"), (5, "55 or older")], measure="ordinal", label="Age group"),
    item("sex", "Sex", [(1, "Male"), (2, "Female"), (3, "Prefer not to say")], label="Sex"),
    item("rank", "Rank category", [(1, "Officer"), (2, "Other rank")], label="Rank category"),
    item("yos", "Years of service", [(1, "Under 5"), (2, "5 to 9"), (3, "10 to 19"), (4, "20 or more")], measure="ordinal", label="Years of service"),
    item("service", "Service", [(1, "Army"), (2, "Navy"), (3, "Air Force"), (4, "Other or prefer not to say")], label="Service"),
    item("marital", "Family situation", [(1, "Single"), (2, "Married or partnered"), (3, "Separated, divorced or widowed")], label="Family situation"),
    item("apart", "In the last 12 months, were you apart from your family for more than 3 months because of a posting or deployment?", YESNO, label="Apart from family >3 months"),
    item("deploy", "How many times have you been deployed on operations?", [(0, "Never"), (1, "Once"), (2, "More than once")], measure="ordinal", label="Deployments"),
    item("deploy_recent", "How long since you last returned from deployment?", [(1, "Under 6 months"), (2, "6 to 12 months"), (3, "More than a year")],
         measure="ordinal", show_if=("deploy", [1, 2]), label="Time since deployment"),
]
BG_F = [
    item("age", "Age group", [(1, "18 to 24"), (2, "25 to 34"), (3, "35 to 44"), (4, "45 to 54"), (5, "55 or older")], measure="ordinal", label="Age group"),
    item("sex", "Sex", [(1, "Male"), (2, "Female"), (3, "Prefer not to say")], label="Sex"),
    item("relation", "Your relationship to the serving member", [(1, "Spouse or partner"), (2, "Parent"), (3, "Adult child or sibling"),
                                                                 (4, "Widow, widower or bereaved relative"), (5, "Other")], label="Relationship to serving member"),
    item("fyears", "How long has your family been connected to the forces?", [(1, "Under 5 years"), (2, "5 to 9 years"), (3, "10 to 19 years"), (4, "20 years or more")],
         measure="ordinal", label="Years in military family"),
    item("children", "Do you have children living with you?", YESNO, label="Children at home"),
    item("living", "Where do you live?", [(1, "Barracks or garrison housing"), (2, "Own or rented home near the unit"), (3, "Home area away from the unit")], label="Living situation"),
    item("apart", "In the last 12 months, was your family member away on posting or deployment for more than 3 months?", YESNO, label="Member away >3 months"),
]

FORMS["baseline_personnel"] = dict(
    title="Short baseline questions (serving personnel)", minutes=7, groups=["personnel"],
    sections=[sec("bg", "About you", BG_P), helpseeking_section(), stigma_section(), intention_section(), awareness_section(),
              money_section(), betting_section(), police_section(), digital_section()])
FORMS["baseline_family"] = dict(
    title="Short baseline questions (family members)", minutes=7, groups=["family"],
    sections=[sec("bg", "About you", BG_F), helpseeking_section(), stigma_section(), intention_section(), awareness_section(),
              money_section(True), digital_section()])

# ---- check-in ---------------------------------------------------------------------
PHQ9_TEXT = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself, or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading or watching television",
    "Moving or speaking so slowly that other people could have noticed, or being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead, or of hurting yourself in some way",
]
GAD7_TEXT = [
    "Feeling nervous, anxious or on edge", "Not being able to stop or control worrying", "Worrying too much about different things",
    "Trouble relaxing", "Being so restless that it is hard to sit still", "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen",
]
PTSD_TEXT = [
    "Had nightmares about the event(s) or thought about the event(s) when you did not want to?",
    "Tried hard not to think about the event(s) or went out of your way to avoid situations that reminded you of the event(s)?",
    "Been constantly on guard, watchful or easily startled?",
    "Felt numb or detached from other people, activities or your surroundings?",
    "Felt guilty or unable to stop blaming yourself or others for the event(s) or any problems the event(s) may have caused?",
]
LP = [("lp1", "Money or debt", None), ("lp2", "Being away from family or long postings", "Your family member being away or long postings"),
      ("lp3", "Conflict at home", None), ("lp4", "Housing or family welfare", None),
      ("lp5", "Workload and rest", "Workload, rest and managing the home"), ("lp6", "Treatment by superiors or colleagues", "How the unit or community treats you"),
      ("lp7", "Fear for safety on duty", "Worry about your family member's safety on duty"), ("lp8", "Bereavement or loss", None),
      ("lp9", "Worry about career or discharge", "Worry about your family member's career, income or discharge"), ("lp10", "Loneliness", None)]

FORMS["checkin"] = dict(
    title="Private check-in", minutes=8, groups=["personnel", "family", "student"],
    sections=[
        # Adaptive short form: PHQ-9 items 3 to 8 are asked only if items 1 and 2 add to 2 or more. Item 9 is ALWAYS asked.
        sec("phq9", "Mood", [item("phq_%d" % (i + 1), t, FREQ4, measure="ordinal", label="PHQ-9 item %d" % (i + 1),
                                  gate=(["phq_1", "phq_2"], 2) if 3 <= i + 1 <= 8 else None) for i, t in enumerate(PHQ9_TEXT)],
            intro="Over the last 2 weeks, how often have you been bothered by any of the following problems?"),
        sec("gad7", "Worry and nerves", [item("gad_%d" % (i + 1), t, FREQ4, measure="ordinal", label="GAD-7 item %d" % (i + 1),
                                              gate=(["gad_1", "gad_2"], 2) if i + 1 >= 3 else None) for i, t in enumerate(GAD7_TEXT)],
            intro="Over the last 2 weeks, how often have you been bothered by the following problems?"),
        sec("ptsd", "Frightening or traumatic events", [
            item("ptsd_gate", "Sometimes things happen to people that are unusually or especially frightening, horrible or traumatic. "
                 "For example: a serious accident or fire; a physical or sexual assault or abuse; a disaster; a war or attack; "
                 "seeing someone be killed or seriously injured; or having a loved one die through homicide or suicide. "
                 "Have you ever experienced this kind of event?", YESNO, label="PC-PTSD-5 exposure"),
        ] + [item("ptsd_%d" % (i + 1), t, YESNO, show_if=("ptsd_gate", [1]), label="PC-PTSD-5 item %d" % (i + 1)) for i, t in enumerate(PTSD_TEXT)],
            intro="Some of the next questions are only asked if you answer yes to the first one. In the past month, have you..."),
        sec("alc", "Alcohol", [
            item("ac1", "How often do you have a drink containing alcohol?",
                 [(0, "Never"), (1, "Monthly or less"), (2, "2 to 4 times a month"), (3, "2 to 3 times a week"), (4, "4 or more times a week")],
                 measure="ordinal", label="AUDIT-C item 1"),
            item("ac2", "How many drinks do you have on a typical day when you are drinking? (One drink is about one 330 ml bottle of beer, one small glass of wine or one tot of spirits.)",
                 [(0, "1 or 2"), (1, "3 or 4"), (2, "5 or 6"), (3, "7 to 9"), (4, "10 or more")], measure="ordinal",
                 show_if=("ac1", [1, 2, 3, 4]), label="AUDIT-C item 2"),
            item("ac3", "How often do you have six or more drinks on one occasion?",
                 [(0, "Never"), (1, "Less than monthly"), (2, "Monthly"), (3, "Weekly"), (4, "Daily or almost daily")],
                 measure="ordinal", show_if=("ac1", [1, 2, 3, 4]), label="AUDIT-C item 3"),
        ]),
        sec("pressures", "Life pressures", [item(i, t, PROBLEM3, measure="ordinal", label="Life pressure: " + t, text_family=tf) for i, t, tf in LP],
            intro="Over the last month, how much of a problem has each of these been for you?"),
        money_section(),
        stressor_section(),
        sec("home", "Home and family (you can skip any question)", [
            item("h1", "Over the last 12 months, have arguments or tension at home become better or worse?",
                 [(1, "Much better"), (2, "A little better"), (3, "About the same"), (4, "A little worse"), (5, "Much worse"), (9, "Prefer not to say")],
                 label="Home tension trend"),
            item("h2", "In the last 12 months, has anyone at home hurt, threatened or frightened you?", YESNOPNS, label="Hurt or frightened at home"),
            item("h3", "Have you worried that your own anger or drinking has hurt or frightened someone at home?", YESNOPNS,
                 label="Worry own anger or drinking harms home"),
        ], intro="These questions are private. Only you see your answers unless you choose to ask a nurse to contact you."),
    ],
)

# ---- weekly pulse (about a minute) ----------------------------------------------------------
PULSE_CUES = [(0, "Nothing in particular"), (1, "Money or pay"), (2, "Debt, a loan or a lender"),
              (3, "News about operations, deployment or postings"), (4, "Family or home"),
              (5, "Things I see online or on social media"), (6, "A loss or bad news in my unit or family"),
              (7, "My health or illness"), (8, "Work, leadership or discipline"), (9, "Something else")]
FORMS["pulse"] = dict(
    title="Weekly pulse", minutes=1, groups=["personnel", "family", "student"],
    sections=[sec("pulse", "This week", [
        item("pl_sleep", "How has your sleep been this week?", [(1, "Good"), (2, "Fair"), (3, "Poor"), (4, "Very poor")], measure="ordinal", label="Pulse: sleep"),
        item("pl_stress", "How stressed do you feel this week?", [(1, "Not at all"), (2, "A little"), (3, "Moderately"), (4, "Very"), (5, "Extremely")],
             measure="ordinal", label="Pulse: stress"),
        item("pl_money", "How worried have you been about money or debt this week?", [(1, "Not at all"), (2, "A little"), (3, "Quite a lot"), (4, "Very worried")],
             measure="ordinal", label="Pulse: worry about money or debt"),
        item("pl_cue", "What is weighing on you most this week?", PULSE_CUES, label="Pulse: main pressure this week"),
        item("pl_news", "Has something that happened recently (in the news, your unit or your community) affected how you feel?",
             [(2, "Yes, a lot"), (1, "A little"), (0, "No")], measure="ordinal", label="Pulse: affected by recent events"),
        item("pl_home", "How calm and safe has home been this week?",
             [(1, "Very tense or unsafe"), (2, "Tense"), (3, "Mixed"), (4, "Calm"), (5, "Very calm"), (9, "Prefer not to say")], label="Pulse: home calm and safe"),
        item("pl_buddy", "Did you check on a colleague, or did someone check on you?",
             [(0, "Neither"), (1, "I checked on someone"), (2, "Someone checked on me"), (3, "Both")], label="Pulse: buddy contact"),
        item("pl_text", "In your own words, anything else weighing on you? Please do not write names, lender details, service numbers or places.",
             type="text", optional=True, label="Pulse: own words"),
    ], intro="One minute. Your answers help the pilot notice what is weighing on people this week, so help can be shaped to it.")],
)

# ---- key informants and experts ------------------------------------------------------------------
PROBLEMS_P = [
    ("depr", "Depression or low mood"), ("anx", "Anxiety and stress reactions"), ("ptsd", "Post-traumatic stress symptoms"),
    ("sui_t", "Suicidal thoughts or attempts"), ("sui_d", "Deaths by suicide"), ("alc", "Harmful alcohol or drug use"),
    ("anger", "Anger, aggression or discipline problems linked to mental health"),
    ("fv_perp", "Personnel reported as perpetrators of violence at home"), ("rel", "Relationship breakdown or separation"),
    ("fin", "Money and debt distress"), ("shy", "Borrowing from informal lenders (shylocks)"),
    ("pledge", "Leaving ID cards, bank cards or phones with lenders as security"),
    ("lostcard", "ID or bank cards reported lost while actually held by a lender"),
    ("harass", "Harassment or threats by lenders (including calls to relatives and colleagues)"),
    ("deduct", "Salary deductions leaving little take-home pay"),
    ("trans", "Problems around discharge or retirement"),
]
PROBLEMS_F = [
    ("f_distress", "Distress, depression or anxiety among spouses or partners"),
    ("f_fv", "Spouses, partners or children reported as victims of violence at home"),
    ("f_child", "Emotional or behavioural problems in children"),
    ("f_isol", "Isolation of families during deployments or postings"),
    ("f_debt", "Families in debt to informal lenders"),
    ("f_bereave", "Unmet psychosocial needs of bereaved families"),
]
BARRIERS = [
    ("b_stigma", "Stigma and fear of being seen as weak"), ("b_cmdr", "Fear that commanders will find out or react badly"),
    ("b_records", "Doubts about confidentiality of records"), ("b_staff", "Too few trained mental health staff"),
    ("b_dist", "Distance from services during postings"), ("b_tempo", "Operational tempo and no protected time"),
    ("b_family", "Little help available for families"), ("b_aware", "Low awareness of what is available"),
    ("b_alc", "Alcohol used to cope or cover problems"),
    ("b_discipline", "Fear of discipline over a pledged, held or 'lost' ID card"),
    ("b_credit", "Few safe credit, savings and financial counselling options"),
]
ADEQ = [
    ("a_screen", "Screening before and after deployment"), ("a_counsel", "Access to counselling"),
    ("a_crisis", "Response to a person at risk of suicide"), ("a_family", "Support for families"),
    ("a_gbv", "Response to violence at home"), ("a_civ", "Links to civilian services and hospitals"),
    ("a_fin", "Financial counselling and safe credit"), ("a_idcard", "Procedure when an ID card is lost or held by a lender"),
]
FEATURES = [
    ("f1", "Private check-in with a result the person can use"), ("f2", "Nurse call-back within a set time"),
    ("f3", "Anonymous 'ask the nurse' box"), ("f4", "Welfare navigator for money, housing and family problems"),
    ("f5", "Pre- and post-deployment check-ins"), ("f6", "Buddy-check reminders and peer champions"),
    ("f7", "A version for spouses and family members"), ("f8", "Anonymous unit-level reports"),
    ("f9", "Sleep and stress micro-lessons"),
    ("f10", "Debt help: one-page debt plan and route to the welfare officer or SACCO"),
    ("f11", "A written no-penalty route for personnel who come forward about a held ID card"),
]
REASONS = [("emerg", "Emergencies and medical bills"), ("fees", "School fees"), ("delay", "Delays in pay or allowances"),
           ("repay", "Repaying other loans or deductions"), ("life", "Lifestyle and social pressure"), ("bet", "Betting or gambling"),
           ("biz", "Business or side income"), ("family", "Family and extended-family obligations"), ("alc", "Alcohol"), ("other", "Other")]

FORMS["informant"] = dict(
    title="Key informant and expert questionnaire", minutes=14, groups=["informant"],
    sections=[
        sec("role", "About you", [
            item("i_role", "Your main role",
                 [(1, "Psychiatrist, psychologist or counsellor"), (2, "Mental health or general nurse"), (3, "Medical officer or clinician"),
                  (4, "Chaplain or faith leader"), (5, "Welfare officer or social worker"), (6, "Commander or administrator"),
                  (7, "Military police, legal or gender-violence desk"), (8, "ICT or records officer"), (9, "Public health, finance or policy"),
                  (10, "Other"), (11, "DCHS lecturer, student counsellor, registrar or admissions officer")], label="Informant role"),
            item("i_years", "Years in this kind of work", [(1, "Under 2"), (2, "2 to 5"), (3, "6 to 10"), (4, "More than 10")], measure="ordinal", label="Years in role"),
            item("i_org", "Where do you mainly work?", [(1, "Military health facility"), (2, "Unit or garrison"), (3, "Ministry of Defence or headquarters"),
                                                        (4, "Civilian health or social service"), (5, "Other"), (6, "Defence College of Health Sciences or NDU-Kenya")], label="Organisation type"),
            item("i_basis_cases", "Cases I have handled", type="check", group="What are your answers based on? (tick all that apply)", label="Basis: own cases", optional=True),
            item("i_basis_records", "Records or reports I can see", type="check", group="What are your answers based on? (tick all that apply)", label="Basis: records", optional=True),
            item("i_basis_talk", "What colleagues and personnel tell me", type="check", group="What are your answers based on? (tick all that apply)", label="Basis: conversations", optional=True),
        ]),
        sec("trend_p", "Serving personnel: what has changed?", [item("t_" + k, t, TREND5, measure="ordinal", label="Trend (personnel): " + t) for k, t in PROBLEMS_P],
            intro="Over the last 2 years, how has each of these changed among serving personnel you know of?"),
        sec("trend_f", "Families: what has changed?", [item("t_" + k, t, TREND5, measure="ordinal", label="Trend (families): " + t) for k, t in PROBLEMS_F],
            intro="Over the last 2 years, how has each of these changed among families of personnel?"),
        sec("debt", "Debt, informal lenders and held cards", [
            item("d_share", "In your estimate, what share of personnel you know of have an informal (non-bank, non-SACCO) loan at any time in a year?",
                 [(1, "Almost none"), (2, "Under a quarter"), (3, "A quarter to a half"), (4, "More than half"), (9, "Do not know")], measure="ordinal", label="Estimated share with informal loans"),
            item("d_lost", "Of ID or bank cards reported lost, how many do you think were actually held by a lender?",
                 [(1, "Almost none"), (2, "A few"), (3, "About half"), (4, "Most"), (9, "Do not know")], measure="ordinal", label="Share of lost cards actually held by lender", sensitive=True),
            item("d_know", "How well does the unit or Medical Services know about this problem today?", ADEQUACY5, measure="ordinal", label="How well the problem is known"),
        ] + [item("d_why_" + k, t, type="check", optional=True, group="Main reasons personnel borrow from informal lenders (tick up to 3)", max_checks=3,
                  label="Reason for borrowing: " + t) for k, t in REASONS]
          + [item("d_text", "What would make personnel come forward about a loan or a held card? (No names or details that could identify a person.)", type="text", optional=True,
                  label="What would make personnel come forward")],
            intro="Informal lending, cards left as security and cards reported lost are reported to the researcher as concerns. Answer from your own knowledge, with no names."),
        sec("emerging", "Emerging concerns", [
            item("em_new", "Have you seen a new or unusual pattern of mental health problems, money problems or violence at home in the last 2 years?",
                 [(1, "Yes"), (0, "No"), (2, "Not sure")], label="New pattern noticed"),
            item("em_text", "If yes, briefly describe it. Do not include names, service numbers or anything that could identify a person.",
                 type="text", optional=True, show_if=("em_new", [1]), label="Describe new pattern"),
            item("em_early", "What share of personnel with a problem do you think seek help early?",
                 [(1, "Almost none"), (2, "A few"), (3, "About half"), (4, "Most"), (9, "Do not know")], measure="ordinal", label="Share who seek help early"),
        ]),
        sec("dchs", "Students of the Defence College of Health Sciences (DCHS)", [
            item("ds_know", "Do you know enough about DCHS students to answer the next questions?", [(1, "Yes"), (0, "No, skip this part")], label="Knows DCHS students well enough"),
            item("ds_trend", "Over the last 2 years, has the number of DCHS students leaving or deferring for health or personal reasons changed?", TREND5, measure="ordinal",
                 show_if=("ds_know", [1]), label="Trend: students leaving or deferring"),
            *[item("ds_why_" + k, t, type="check", optional=True, show_if=("ds_know", [1]), group="Main reasons students leave or defer (tick up to 3)", max_checks=3,
                   label="Reason students leave: " + t) for k, t in [("mh", "Stress, low mood or anxiety"), ("fees", "Fees or money problems"), ("debt", "Debt or informal loans"), ("family", "Family or home problems"),
                   ("acad", "Academic difficulty"), ("disc", "Discipline or the demands of military life"), ("phys", "Physical illness"), ("mind", "Changed plans or career choice"), ("alc", "Alcohol or drugs")]],
            item("ds_adeq", "How good is the support now available to DCHS students for stress, mood, money and family problems?", ADEQUACY5, measure="ordinal",
                 show_if=("ds_know", [1]), label="Adequacy of current student support"),
            item("ds_early", "When are students in difficulty usually first noticed?", [(1, "Before their studies suffer"), (2, "When their grades fall"), (3, "When they stop attending"), (4, "Only when they leave or defer"), (9, "Do not know")],
                 measure="ordinal", show_if=("ds_know", [1]), label="When struggling students are first noticed"),
            item("ds_gate", "An online wellbeing check should NOT be used to decide who is admitted.", AGREE5, measure="ordinal", show_if=("ds_know", [1]), label="Agree: check not used for admission"),
            item("ds_useful", "A voluntary online wellbeing check for applicants and students would be useful.", AGREE5, measure="ordinal",
                 show_if=("ds_know", [1]), label="Agree: voluntary support-only check useful"),
            item("ds_share", "A student should be able to choose to share a colour (green, amber or red) with the student-support office.", AGREE5, measure="ordinal",
                 show_if=("ds_know", [1]), label="Agree: student may share colour with support office"),
            item("ds_interv", "An interviewer on the selection panel should be able to see an applicant's colour.", AGREE5, measure="ordinal",
                 show_if=("ds_know", [1]), label="Agree: interviewer may see colour"),
            item("ds_when", "When would an online check help most?", [(1, "At application, before the interview"), (2, "After the admission offer"), (3, "At orientation"), (4, "Each term"), (5, "Before exams or clinical placements")],
                 show_if=("ds_know", [1]), label="Best time for an online check"),
            item("ds_text", "What would make students trust and use an online wellbeing check? (Do not include names or details that could identify anyone.)", type="text", optional=True,
                 show_if=("ds_know", [1]), label="What would make students trust the check"),
        ], intro="Skip this part if you do not work with DCHS students."),
        sec("barriers", "What stops people getting help?", [item(k, t, IMPORTANCE5, measure="ordinal", label="Barrier: " + t) for k, t in BARRIERS],
            intro="How important is each of these in your experience?"),
        sec("adequacy", "What exists now", [item(k, t, ADEQUACY5, measure="ordinal", label="Current adequacy: " + t) for k, t in ADEQ],
            intro="How good is the current arrangement for each of these?"),
        sec("features", "What a new service should include", [item(k, t, IMPORTANCE5, measure="ordinal", label="Feature priority: " + t) for k, t in FEATURES],
            intro="How important is each feature for a small service run by nurses in one or two units?"),
        sec("governance", "Safety and rules", [
            item("g_time", "For a person at high risk, what is the longest acceptable time before a nurse or clinician makes first contact?",
                 [(1, "Within 1 hour"), (2, "Within 4 hours"), (3, "Within 8 hours"), (4, "Within 24 hours"), (5, "Within 3 days")], measure="ordinal", label="Acceptable time to contact (high risk)"),
            item("g_notify", "Commanders should receive anonymous group figures only (no individual information).", AGREE5, measure="ordinal", label="Commanders see group figures only"),
            item("g_mand", "Check-ins should be:", [(1, "Voluntary only"), (2, "Voluntary but encouraged with protected time"), (3, "Required, with private results")],
                 measure="ordinal", label="Voluntary vs required"),
            item("g_family", "Spouses and family members should be able to use the service.", AGREE5, measure="ordinal", label="Family access agreed"),
            item("g_safe", "During the pilot, personnel who come forward on their own about a held ID card should be offered a written no-penalty route to recover it.", AGREE5,
                 measure="ordinal", label="Agree no-penalty route for held ID cards", sensitive=True),
            item("g_host", "Where should the pilot data be kept?", [(1, "On a free cloud service, anonymous data only"), (2, "On a hospital or Ministry server only"), (3, "Not sure")],
                 label="Data hosting preference"),
        ]),
        sec("adopt", "Support for a pilot", [
            item("ad_support", "I would support a 3-month pilot in one or two units.", AGREE5, measure="ordinal", label="Support pilot"),
            item("ad_nurse", "Can a nurse be made available to answer call-backs within the agreed time?", [(1, "Yes"), (2, "Maybe, with support"), (0, "No")], label="Nurse on call possible"),
            item("ad_approve", "Who must approve before the pilot can start?", type="text", optional=True, label="Approvals needed"),
            item("ad_top3", "What are the top three changes that would most improve mental health care for personnel and families?", type="text", optional=True, label="Top three changes"),
            item("ad_stop", "What would make you stop supporting a service like this?", type="text", optional=True, label="Reasons to stop supporting"),
        ], intro="Free-text answers are optional. Please do not include any names or details that could identify a person."),
    ],
)

# ---- Delphi panel (rounds 1 to 3) -------------------------------------------------------------
RATE9 = [(i, "%d" % i if i not in (1, 9) else ("1 Not important" if i == 1 else "9 Essential")) for i in range(1, 10)]
DELPHI = [
    ("A. Service design", [("dl1", "A private first check on the phone, with a result that only the person sees."), ("dl2", "A nurse call-back within a set time after a request."),
        ("dl3", "Same-day contact for a person whose answers suggest high risk."), ("dl4", "An anonymous ask-the-nurse box."),
        ("dl5", "A welfare navigator for money, housing and family problems."), ("dl6", "Short sleep, stress and money lessons in the app."),
        ("dl7", "Peer champions who introduce the service to others."), ("dl8", "A version for spouses and adult family members.")]),
    ("B. Safety and rules", [("dl9", "A written safety protocol for thoughts of suicide or self-harm."), ("dl10", "The limits of confidentiality explained before the check starts."),
        ("dl11", "Commanders receive anonymous group figures only, never individual results."), ("dl12", "Protected time to do the check, with answers staying private."),
        ("dl13", "A written no-penalty route for people who come forward about a loan where a lender holds their card."),
        ("dl14", "Regular review of the service by an ethics focal person, with every change recorded.")]),
    ("C. Use at the Defence College of Health Sciences", [("dl15", "A voluntary wellbeing check for applicants, offered to help them get support."),
        ("dl16", "The check has no effect on admission decisions."), ("dl17", "An applicant can choose to share only a colour (green, amber or red) with the student-support office."),
        ("dl18", "The check is repeated at orientation, when nothing depends on the answers."),
        ("dl19", "The college tracks, without names, whether students who left had contact with support."),
        ("dl20", "A written agreement that results will not be used for admission or discipline.")]),
    ("D. Content and measurement", [("dl21", "Asking about informal borrowing and cards held as security."), ("dl22", "Letting people name their own stressors in their own words."),
        ("dl23", "A one-minute weekly pulse to spot changes early."), ("dl24", "Group-level early warning that triggers a pre-agreed response.")]),
]
FORMS["delphi"] = dict(
    title="Expert panel (Delphi) rating form", minutes=15, groups=["informant"],
    sections=[sec("dl_about", "About you and this round", [
        item("dl_round", "Which round is this?", [(1, "Round 1"), (2, "Round 2"), (3, "Round 3")], measure="ordinal", label="Delphi round"),
        item("dl_role", "Your main role", [(1, "Psychiatrist, psychologist or counsellor"), (2, "Mental health or general nurse"), (3, "Medical officer or clinician"),
              (4, "Chaplain or faith leader"), (5, "Welfare officer or social worker"), (6, "Commander or administrator"), (7, "Legal, ethics or data-protection expert"),
              (8, "ICT or records officer"), (9, "DCHS lecturer, student counsellor, registrar or admissions officer"), (10, "Student or family representative"), (11, "Other")], label="Delphi panellist role")],
        intro="Experts rate each statement from 1 (not important) to 9 (essential). Do not write names.")] +
        [sec("dl_" + t[0][0].lower(), t[0], [item(i, s, RATE9, measure="ordinal", label="Delphi: " + s[:70]) for i, s in t[1]], intro="How important is it that this is part of the service? 1 = not important, 9 = essential.") for t in DELPHI] +
        [sec("dl_text", "Your suggestions", [item("dl_add", "What important feature, rule or safeguard is missing?", type="text", optional=True, label="Delphi: suggested addition"),
                                              item("dl_remove", "What should be removed or changed, and why?", type="text", optional=True, label="Delphi: suggested removal")],
             intro="Optional. Please do not include names or details that could identify a person.")])

# ---- end-of-pilot feedback ---------------------------------------------------------------------
SUS = ["I think that I would like to use this app frequently.", "I found the app unnecessarily complex.", "I thought the app was easy to use.",
       "I think that I would need the support of a technical person to be able to use this app.", "I found the various functions in this app were well integrated.",
       "I thought there was too much inconsistency in this app.", "I would imagine that most people would learn to use this app very quickly.",
       "I found the app very cumbersome to use.", "I felt very confident using the app.", "I needed to learn a lot of things before I could get going with this app."]
ACCEPT = [("pe1", "Using the app helps me get help sooner."), ("pe2", "Using the app helps me find the right kind of help."),
          ("ee1", "Learning to use the app was easy for me."), ("si1", "People who matter to me (buddy, chaplain, commander) support my use of the app."),
          ("si2", "Other people in my unit use or recommend the app."), ("fc1", "I had what I needed (phone, data and time) to use the app."),
          ("fc2", "I could reach a nurse when I needed to."), ("bi1", "I intend to keep using the app."),
          ("bi2", "I would recommend the app to a colleague or family member.")]
CONF = [("pc1", "I believe my commander cannot see my answers."), ("pc2", "I felt safe answering honestly."),
        ("pc3", "I worried that my answers could be traced back to me."), ("pc4", "I trust that only the nurse can see what I choose to share.")]
USED = [("u_lesson", "Micro-lessons (sleep, stress, money)"), ("u_ask", "Ask the nurse"), ("u_welfare", "Welfare navigator and debt help"),
        ("u_buddy", "Buddy check reminders"), ("u_callback", "Nurse call-back"), ("u_deploy", "Pre- or post-deployment check-in")]

FORMS["usability_end"] = dict(
    title="End-of-pilot feedback", minutes=9, groups=["personnel", "family", "staff"],
    sections=[
        sec("who", "About you", [
            item("u_role", "Who are you?", [(1, "Serving member"), (2, "Family member"), (3, "Nurse or clinician"),
                                             (4, "Chaplain, welfare officer or peer champion"), (5, "Other")], label="Role in pilot"),
            item("u_weeks", "About how many weeks did you use the app?", [(1, "Under 2"), (2, "2 to 4"), (3, "5 to 8"), (4, "9 or more")], measure="ordinal", label="Weeks of use"),
        ]),
        sec("sus", "Using the app", [item("sus%d" % (i + 1), t, AGREE5, measure="ordinal", label="SUS item %d" % (i + 1)) for i, t in enumerate(SUS)],
            intro="Choose the answer that best matches your experience."),
        sec("accept", "Usefulness and support", [item(k, t, AGREE5, measure="ordinal", label="Acceptability: " + t) for k, t in ACCEPT]),
        sec("conf", "Privacy and trust", [item(k, t, AGREE5, measure="ordinal", label="Confidentiality: " + t) for k, t in CONF]),
        sec("used", "Which parts did you use?", [item(k, t, [(1, "Used and helpful"), (2, "Used, not helpful"), (0, "Did not use")], measure="ordinal",
                                                     label="Feature use: " + t) for k, t in USED]),
        sec("after", "Help-seeking after using the app",
            intention_items() + [i for i in stigma_section()["items"] if i["id"] in ("st1", "st2", "st3", "co1", "co5")],
            intro="Please answer these again so we can see whether anything changed."),
        sec("nps", "Overall", [
            item("nps", "How likely are you to recommend this app to a colleague? (0 = not at all, 10 = extremely)", NPS11, measure="scale", label="Likelihood to recommend (0-10)"),
            item("u_text", "What one change would make the app better? (Do not include names or details that could identify anyone.)", type="text", optional=True, label="One change"),
        ]),
    ],
)


# ---- DCHS applicant wellbeing and readiness check ---------------------------------------------
# Used at interview selection and again at orientation (no stakes). Answers never go to the selection panel.
def _sec(form, sid):
    return next(x for x in FORMS[form]["sections"] if x["id"] == sid)


AP_LA = [("la1", "Money: fees, upkeep or debt"), ("la2", "Being far from family or home"), ("la3", "Conflict or problems at home"),
         ("la4", "Accommodation or housing"), ("la5", "Pressure to succeed or fear of failing"), ("la6", "Your health"),
         ("la7", "Loneliness or fitting in"), ("la8", "Bereavement or loss")]
BRS = ["I tend to bounce back quickly after hard times.", "I have a hard time making it through stressful events.",
       "It does not take me long to recover from a stressful event.", "It is hard for me to snap back when something bad happens.",
       "I usually come through difficult times with little trouble.", "I tend to take a long time to get over setbacks in my life."]
AP_BG = [
    item("age", "Age group", [(1, "18 to 19"), (2, "20 to 24"), (3, "25 to 34"), (4, "35 or older")], measure="ordinal", label="Age group"),
    item("sex", "Sex", [(1, "Male"), (2, "Female"), (3, "Prefer not to say")], label="Sex"),
    item("prog", "Which DCHS programme are you in (or applying for)?", [(1, "BSc Nursing with Military Health"), (2, "Another DCHS programme"), (3, "Not sure yet")],
         label="Programme"),
    item("yos", "Which year of study are you in?", [(1, "Year 1"), (2, "Year 2"), (3, "Year 3"), (4, "Year 4 or later"), (5, "I am an applicant and have not started")],
         measure="ordinal", label="Year of study"),
    item("apptype", "How did you come to the programme?", [(1, "From school"), (2, "From civilian work or earlier study"), (3, "As a serving member of the forces"), (4, "As a former member of the forces")],
         label="Entry route"),
    item("firstaway", "Is this the first time you have lived away from your family home for months at a time?", YESNO, label="First time living away from home"),
    item("prior_care", "Have you ever had counselling or treatment for your emotional or mental health? (This is for the study only. It is never shared with the college, your lecturers or any discipline office.)",
         YESNOPNS, sensitive=True, label="Previous counselling or treatment"),
    item("fam_loss", "In the last 12 months, has someone close to you died or been seriously ill?", YESNOPNS, label="Recent bereavement or serious illness in family"),
]
AP_READY = [item("brs%d" % (i + 1), t, AGREE5, measure="ordinal", label="Resilience item %d" % (i + 1)) for i, t in enumerate(BRS)] + [
    item("rd_talk", "I have at least one person I can talk to openly when I have a problem.", AGREE5, measure="ordinal", label="Has someone to talk to"),
    item("rd_family", "My family supports my being on this programme.", AGREE5, measure="ordinal", label="Family support for the programme"),
    item("rd_know", "The demands of the programme (workload, discipline, clinical placements and time away) are what I expected.", AGREE5, measure="ordinal", label="Demands as expected"),
    item("rd_conf", "I am confident I can complete the programme.", AGREE5, measure="ordinal", label="Confident of completing programme"),
    item("rd_help", "If I were struggling at the college, I would ask for help early.", AGREE5, measure="ordinal", label="Would ask for help early"),
]
LEAVE_WHY = [("workload", "Workload or exams"), ("money", "Money or fees"), ("health", "My health or wellbeing"), ("family", "Problems in my family"),
             ("discipline", "Military discipline or routine"), ("away", "Time away from home"), ("clinical", "What I experienced on clinical placement"),
             ("treat", "The way I am treated by others"), ("wrong", "I think I chose the wrong course"), ("other", "Something else")]
AP_COURSE = [
    item("cl1", "In the last 3 months, have you thought about leaving or deferring your programme?", [(0, "Never"), (1, "Once or twice"), (2, "Sometimes"), (3, "Often")],
         measure="ordinal", label="Thought of leaving or deferring"),
] + [item("cl_" + k, t, type="check", optional=True, max_checks=3, show_if=("cl1", [1, 2, 3]), sensitive=(k == "treat"),
          group="What made you think about it? (tick up to 3)", label="Reason for thinking of leaving: " + t) for k, t in LEAVE_WHY]
AP_IDEAS = [
    item("sug1", "What would make this service more useful to you? (You may leave this blank.)", type="text", optional=True, label="Suggestion: service"),
    item("sug2", "Is there anything about the college, or about this study, that you would like to suggest or change? (You may leave this blank.)", type="text", optional=True, label="Suggestion: college or study"),
    item("sug3", "Is there a question we should have asked, or one that was hard to understand? (You may leave this blank.)", type="text", optional=True, label="Suggestion: questions"),
]
AP_VALID = [
    item("av1", "While answering, I worried my answers might affect my place or progress on the course.", AGREE5, measure="ordinal", label="Worried answers affect place or progress"),
    item("av2", "While answering, I felt I should answer so that I look well.", AGREE5, measure="ordinal", label="Felt should look well"),
    item("av3", "I answered these questions honestly.", AGREE5, measure="ordinal", label="Answered honestly"),
    item("av4", "I believe the college staff who teach, mark or discipline me cannot see my individual answers.", AGREE5, measure="ordinal", label="Believes college staff cannot see answers"),
]
def student_intention():
    its = intention_items()
    for it in its:
        if it["id"] == "hsi_buddy": it["text"] = "How likely would you be to talk to a friend or classmate?"
        if it["id"] == "hsi_cmdr": it["text"] = "How likely would you be to talk to a lecturer, course leader or commander?"
        if it["id"] == "hsi_chaplain": it["text"] = "How likely would you be to talk to a chaplain or counsellor?"
    return sec("intent", "If you had a personal or emotional problem", its, intro="Choose how likely you would be to do each of the following.")
FORMS["student_screen"] = dict(
    title="DCHS student wellbeing check", minutes=12, groups=["student"],
    sections=[
        sec("bg", "About you", AP_BG),
        _sec("checkin", "phq9"), _sec("checkin", "gad7"), _sec("checkin", "ptsd"), _sec("checkin", "alc"),
        sec("pressures_a", "Life pressures", [item(i, t, PROBLEM3, measure="ordinal", label="Pressure: " + t) for i, t in AP_LA],
            intro="Over the last month, how much of a problem has each of these been for you?"),
        money_section(applicant=True), betting_section(), police_section(True), stressor_section(applicant=True),
        sec("course", "Your programme", AP_COURSE, intro="Many students think about leaving at some point. Your honest answers help the college offer help earlier."),
        sec("ready", "Coping and support", AP_READY, intro="How much do you agree with each statement?"),
        student_intention(),
        _sec("checkin", "home"),
        sec("ideas", "Your ideas", AP_IDEAS, intro="These open questions help us improve the service. Please do not write names or service numbers."),
        sec("valid", "About answering these questions", AP_VALID, intro="The last few questions help us understand how it felt to answer."),
    ])

# ------------------------------------------------------------- derived scores ---
# short = items always asked when the form is adaptive; the rest are asked only if the short items sum to 2 or more.
SCALES = {
    "phq9": dict(items=["phq_%d" % i for i in range(1, 10)], label="PHQ-9 total (0-27)", short=["phq_1", "phq_2", "phq_9"]),
    "gad7": dict(items=["gad_%d" % i for i in range(1, 8)], label="GAD-7 total (0-21)", short=["gad_1", "gad_2"]),
    "ptsd5": dict(items=["ptsd_%d" % i for i in range(1, 6)], zero_if=("ptsd_gate", 0), label="PC-PTSD-5 total (0-5)"),
    "auditc": dict(items=["ac1", "ac2", "ac3"], zero_if=("ac1", 0), label="AUDIT-C total (0-12)"),
    "lifestress": dict(items=["lp%d" % i for i in range(1, 11)], label="Life stress total (0-20)"),
    "sus": dict(items=["sus%d" % i for i in range(1, 11)], label="SUS score (0-100)", sus=True),
}

SCALES["lifestress_a"] = dict(items=[i for i, _ in AP_LA], label="Student life pressure total (0-16)")
SCALES["brs"] = dict(items=["brs%d" % i for i in range(1, 7)], rev=["brs2", "brs4", "brs6"], label="Brief Resilience Scale sum (6-30; divide by 6 for the usual 1-5 mean)")
SCALES["stakes"] = dict(items=["av1", "av2"], label="Perceived consequences: worry that answers affect place or progress plus pressure to look well (2-10)")

# ------------------------------------------------------------------ content ---
CONTENT = dict(
    lessons=[
        dict(id="sleep", title="Sleep when your schedule is not yours", minutes=2, body=[
            "Short, steady sleep beats long, broken sleep. Aim for the same wake-up time as often as duty allows.",
            "Wind down for 20 minutes before sleep: dim your phone, put it face down, and slow your breathing (in for 4, out for 6).",
            "Limit caffeine after midday and avoid alcohol as a sleep aid. It helps you fall asleep but breaks up sleep later in the night.",
            "If you cannot sleep after 20 minutes, get up, sit somewhere dim and do something dull until you feel sleepy.",
            "Worry about money is a common reason for lost sleep. Write the worry and one next step on paper before bed.",
            "Trouble sleeping for more than 2 weeks, or nightmares that keep returning, is a good reason to talk to a nurse."]),
        dict(id="stress", title="Reset in 90 seconds", minutes=2, body=[
            "When stress spikes, slow your breathing: in through the nose for 4 counts, out through the mouth for 6. Repeat for 90 seconds.",
            "Name five things you can see, four you can touch, three you can hear. This pulls attention back to the present.",
            "Stress that is building for weeks needs a plan, not willpower: pick one problem, one person to tell and one next step.",
            "A reaction to a bad event is normal. If it is not easing after a month, or it is getting in the way of duty or home, ask a nurse."]),
        dict(id="money", title="Debt: a one-page plan", minutes=3, body=[
            "Debt feels heavier when it stays in your head. On one page, list who you owe, how much, the cost (interest or fees) and the due date.",
            "Put the most costly and most threatening debts first. Do not borrow from one lender to pay another. It usually makes the total grow faster.",
            "Ask the welfare officer, your SACCO or a financial counsellor about restructuring, stopping extra charges or a salary deduction plan. Say it before you miss a payment.",
            "Before you borrow, ask whether the lender is licensed or registered. Since December 2024 the Central Bank of Kenya oversees lenders that do not take deposits. Unregistered lenders are a warning sign.",
            "Keep every message, call log and receipt. If someone threatens you, shames you or contacts your relatives and colleagues, keep the evidence and report it to the police.",
            "Money worry is a health issue too. If it is affecting your sleep, mood or home, a nurse can help with that part."]),
        dict(id="idcard", title="If a lender is holding your card", minutes=3, body=[
            "A lender who holds your military ID, bank card or phone as security has power over you. You are not the first person this has happened to.",
            "Do not report a card as lost when a lender has it. A false report can turn a money problem into a discipline or criminal case, and the lender often still has the card.",
            "Do not give anyone your PIN or phone password. If a bank card is held, tell your bank at once so it can be blocked.",
            "Talk early to the welfare officer, the chaplain or the pilot nurse about how to get the card back safely and what rule applies in your unit.",
            "The pilot team has asked the Medical Services and the Ministry of Defence for a written no-penalty route for people who come forward on their own. Ask what is in force where you are. Do not assume it exists.",
            "If someone threatens you or your family, call the police and keep the messages."]),
        dict(id="anger", title="Cooling off before home gets hurt", minutes=2, body=[
            "Anger is a signal, not a command. The early signs are heat in the face, a tight jaw, a fast heartbeat and short answers.",
            "Agree a time-out word with your partner. Saying it means: I am leaving the room for 20 minutes and I will come back.",
            "Do not talk through a fight while drinking. Wait until you are sober and calm.",
            "Money fights are among the most common. Pick a calm time to look at the one-page debt plan together.",
            "If your anger or drinking has hurt or frightened someone at home, you can get help, and asking early protects your family.",
            "Anyone in danger at home should call the police (999 or 112) or the free gender-violence line 1195."]),
        dict(id="alcohol", title="Drinking less, step by step", minutes=2, body=[
            "Drinking to sleep, to switch off or to cope is a sign to cut back and get support.",
            "Set a limit before you start, alternate with water and skip rounds. Plan at least 2 drink-free days each week.",
            "If you cannot stop, or you have shaking, sweating or anxiety when you do, speak to a nurse. Do not stop suddenly without advice if you drink heavily every day."]),
        dict(id="family", title="Staying close while you are apart", minutes=2, body=[
            "A short, regular message beats a long, rare one. Pick a time that is realistic for both of you.",
            "Share small, real things from your day, not only the problems.",
            "Agree beforehand who handles money, school fees and emergencies while you are away.",
            "Returning home is also an adjustment. Give each other a few weeks and avoid big decisions in the first days."]),
        dict(id="online", title="When the news or social media gets under your skin", minutes=2, body=[
            "Reports of attacks, losses and scandals can hit harder when they are close to your own unit or family.",
            "Choose two times a day to check the news, and put the phone away outside them.",
            "Talk about what you saw with a buddy. A reaction shared is usually lighter.",
            "If the images or stories keep coming back at night, tell a nurse."]),
        dict(id="loss", title="After a loss in your unit or family", minutes=2, body=[
            "Grief can show up as anger, numbness, poor sleep or drinking. None of these means you are weak.",
            "Do not carry it alone: a chaplain, a buddy or a nurse can sit with you.",
            "Keep simple routines: food, sleep, a short walk, a message to someone.",
            "If a death was by suicide, the people around it need support too. Ask a nurse or the chaplain."]),
        dict(id="dchs_start", title="Starting at DCHS: what helps", minutes=3, body=[
            "Starting a health-sciences programme with military discipline is a big change: early mornings, a heavy workload, clinical placements, and months away from home. Feeling the strain at the start is normal and common.",
            "Build three habits in the first two weeks: a steady sleep time, one person you talk to every week, and one hour that is only yours.",
            "Ask for help early. A short chat with a nurse, a chaplain or a lecturer in week three is far easier than a crisis in week twelve.",
            "Money problems are a common reason people leave. Tell the welfare office before you miss a payment, and do not borrow from lenders who keep your cards or ID.",
            "If you ever feel like leaving, talk to someone first. Many students who think of leaving stay once the problem is named and a plan is made."]),
        dict(id="exams", title="Exam and placement stress", minutes=2, body=[
            "Plan in blocks of 45 minutes with a 10 minute break. Sleep before a test helps more than another late hour of study.",
            "Before a clinical placement, ask your preceptor what a normal day looks like. Not knowing is a big part of the fear.",
            "A bad result is information, not a verdict. Ask the lecturer what to change and book the next step the same week.",
            "Racing heart, blank mind or constant dread before exams for more than two weeks is a good reason to talk to a nurse."]),
        dict(id="homeplan", title="A safety plan for home", minutes=3, body=[
            "A plan made on a calm day helps on a bad one. Decide where you can go, who you can call and what you would take.",
            "If you are afraid at home: keep important documents and a little money where you can reach them, and tell one trusted person.",
            "If you are worried you may hurt someone: agree a time-out word, leave the room before it builds, and ask a nurse for help early.",
            "In danger now: police 999 or 112; free gender-violence line 1195."]),
    ],
    buddy=dict(title="Check on a buddy", steps=[
        "Look for changes: withdrawn, short-tempered, not sleeping, drinking more, giving things away, talking as if nothing matters, avoiding calls, suddenly short of money.",
        "Ask directly and privately: 'I have noticed you are not yourself. How are you really doing?'",
        "Listen without fixing. You do not need the right answer. You only need to stay.",
        "If they talk about suicide, ask plainly: 'Are you thinking of ending your life?' Asking does not put the idea in their head.",
        "If money is the weight, offer to go with them to the welfare officer. Do not lend more than you can lose, and do not take their cards.",
        "Do not leave them alone if they are in danger. Take them to the nurse or call for help straight away.",
        "Follow up in a few days. A second check matters as much as the first."]),
    navigator=[
        dict(id="money", title="Money or debt", who="Welfare officer or SACCO", detail="Ask about welfare funds, restructuring, stopping extra charges and salary deduction problems. Try the one-page debt plan lesson.", lesson="money"),
        dict(id="lender", title="A lender is pressuring or threatening me", who="Police and welfare officer", detail="Keep messages and call logs. Threats and shaming are reportable. A welfare officer can help you plan repayment.", lesson="money"),
        dict(id="idcard", title="A lender is holding my ID or bank card", who="Welfare officer, chaplain or pilot nurse", detail="Do not report it lost if it is not. Tell your bank to block a bank card. Ask what no-penalty route applies in your unit.", lesson="idcard"),
        dict(id="housing", title="Housing or family welfare", who="Welfare officer", detail="Ask about housing allocation, school fees support and family welfare schemes."),
        dict(id="home", title="Conflict at home", who="Chaplain or nurse counsellor", detail="A chaplain or counsellor can speak with you, or with both of you, in confidence.", lesson="homeplan"),
        dict(id="safety", title="Safety at home", who="Emergency lines", detail="If someone is in danger now: police 999 or 112. Free gender-violence line 1195. You can also go to the nearest health facility.", lesson="homeplan"),
        dict(id="grief", title="Bereavement or loss", who="Chaplain", detail="A chaplain can support you and your family, and can link you to the welfare office for entitlements.", lesson="loss"),
        dict(id="career", title="Career, posting or discharge", who="Welfare officer or human resources", detail="Ask about transition and resettlement programmes before discharge."),
        dict(id="alcohol", title="Alcohol", who="Nurse", detail="Ask the nurse for a confidential check. You can also try the alcohol lesson first.", lesson="alcohol"),
        dict(id="sleep", title="Sleep or stress", who="Nurse", detail="Try the sleep and stress lessons first. If it lasts more than 2 weeks, ask a nurse.", lesson="sleep"),
        dict(id="fees", title="Fees, upkeep or sponsor problems", who="College welfare office or registrar", detail="Ask about payment plans, bursaries and sponsor delays before you miss a deadline. Do not borrow from lenders who keep your ID or bank card.", lesson="money"),
        dict(id="lonely", title="Loneliness", who="Buddy or chaplain", detail="Pick one person to message today. A short check-in counts."),
    ],
    # what the pulse suggests for each main pressure: (screen, id, label)
    cue_actions={"1": ["lesson", "money", "Debt: a one-page plan"], "2": ["lesson", "idcard", "If a lender is holding your card"],
                 "3": ["lesson", "stress", "Reset in 90 seconds"], "4": ["lesson", "homeplan", "A safety plan for home"],
                 "5": ["lesson", "online", "When the news or social media gets under your skin"], "6": ["lesson", "loss", "After a loss in your unit or family"],
                 "7": ["ask", None, "Ask the nurse about your health"], "8": ["navigator", None, "Welfare navigator"]},
)
