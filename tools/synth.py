#!/usr/bin/env python3
"""Make SYNTHETIC practice data (not real people) for the DCHS student pathway, load it into a database, and export it.
Purpose: let you practise the jamovi analyses in docs/JAMOVI_GUIDE.md and check the pipeline end to end.
The relationships in these data (for example, money strain predicting leaving) are INVENTED for practice. They are not findings.
Usage: python3 tools/synth.py [--n 240] [--seed 11] [--out sample_data]   (needs the test Postgres from tools/reset_db.sh)"""
import argparse, json, math, os, random, sys, uuid
import psycopg2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I

ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=240); ap.add_argument("--seed", type=int, default=11); ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data"))
ap.add_argument("--host", default="/var/tmp/pgt"); ap.add_argument("--port", type=int, default=54329)
a = ap.parse_args(); R = random.Random(a.seed)
def visible(it, ans):
    if it["show_if"] and ans.get(it["show_if"][0]) not in it["show_if"][1]: return False
    if it["gate"]:
        ids, mn = it["gate"]
        if not all(i in ans for i in ids) or sum(ans[i] for i in ids) < mn: return False
    return True
def ordinal(opts, z):                    # z ~ standard normal "load"; higher z picks later options
    k = len(opts); x = z + R.gauss(0, 0.9); idx = min(k - 1, max(0, int((x + 1.2) / 3.4 * k))); return opts[idx]
def person_answers(form, d, look_well=0.0, stakes_hi=False):
    """d = true distress. look_well lowers reported symptoms (people who feel they must look well)."""
    ans = {}; z = d - look_well; groups = {}
    borrow_p = 1 / (1 + math.exp(-(-1.6 + 0.8 * d)))
    for sec in I.FORMS[form]["sections"]:
        for it in sec["items"]:
            if not visible(it, ans): continue
            iid = it["id"]
            if it["type"] == "text":
                if iid in ("sug1", "sug2", "sug3") and R.random() < 0.12: ans[iid] = R.choice(["Add a Kiswahili option", "Please keep it anonymous", "A nurse who answers at night", "Shorter questions"])
                if iid == "sr_text" and R.random() < 0.25: ans[iid] = R.choice(["fees and upkeep", "exam pressure", "being far from home", "a loan I cannot repay", "sleep", "worried about my mother's health"])
                continue
            if it["type"] == "check":
                g = it["group"]; groups.setdefault(g, 0); lim = it["max_checks"] or 99
                p = 0.12 + 0.05 * max(d, 0)
                if iid in ("sr_fees", "sr_money") : p += 0.10 * max(d, 0)
                if groups[g] < lim and R.random() < p: ans[iid] = 1; groups[g] += 1
                else: ans[iid] = 0
                continue
            opts = [o[0] for o in it["options"]]
            if iid == "fm_borrow": ans[iid] = (R.choice([1, 2]) if R.random() < borrow_p * (0.5 if look_well else 1) else 0); continue
            if iid.startswith("brs"):
                rev = iid in ("brs2", "brs4", "brs6"); ans[iid] = ordinal(opts, (d if rev else -d) + (-look_well if rev else look_well)); continue
            if iid == "cl1": ans[iid] = ordinal(opts, d * 0.9 - 0.4); continue
            if iid == "yos": ans[iid] = R.choice([1, 1, 2, 2, 3, 4]); continue
            if iid in ("av1", "av2"): ans[iid] = ordinal(opts, 1.2 if stakes_hi else -0.8); continue
            if iid == "av3": ans[iid] = ordinal(opts, -1.0 if not stakes_hi else -0.2); continue
            if iid == "av4": ans[iid] = ordinal(opts, 0.0); continue
            if iid.startswith("rd_"): ans[iid] = ordinal(opts, -0.6 * d); continue
            if iid.startswith(("phq_", "gad_", "ac", "lp", "la", "fm_needs", "fm_effect", "ptsd_")) and it["measure"] in ("ordinal", "nominal") and len(opts) <= 5:
                if iid == "phq_9": ans[iid] = 1 if (z > 1.9 and R.random() < 0.5) else 0
                elif iid.startswith("ptsd_") : ans[iid] = 1 if R.random() < 1 / (1 + math.exp(-(-1.2 + 0.9 * z))) else 0
                else: ans[iid] = ordinal(opts, z - (0.5 if iid.startswith(("phq_", "gad_")) else 0.2))
                continue
            if 0 in opts and 1 in opts and len(opts) <= 3 and iid not in ('firstaway',): ans[iid] = 1 if R.random() < 0.06 + 0.07 * max(z, 0) else (9 if 9 in opts and R.random() < 0.05 else 0); continue
            ans[iid] = R.choice(opts)
    return ans
def scoreboard(form, ans):
    return None
con = psycopg2.connect(host=a.host, port=a.port, user="postgres", dbname="salama"); con.autocommit = True; cur = con.cursor()
cur.execute("truncate public.responses, public.cohort_outcomes, public.college_sharing cascade")
import string
def code(i): A = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"; r = random.Random(1000 + i); return "".join(r.choice(A) for _ in range(4)) + "-" + "".join(r.choice(A) for _ in range(4))
import subprocess
PENDING = []
def ins(form, grp, ctx, wave, unit, anon, ans, risk=None, zone=None):
    PENDING.append((form, grp, ctx, wave, unit, anon, ans))
def flush_pending():
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scores = json.loads(subprocess.run(["node", os.path.join(ROOT, "test", "score_batch.js")], input=json.dumps([p[6] for p in PENDING]), capture_output=True, text=True, check=True).stdout)
    for (form, grp, ctx, wave, unit, anon, ans), sc in zip(PENDING, scores): _ins(form, grp, ctx, wave, unit, anon, ans, sc["risk"], sc["zone"])
def _ins(form, grp, ctx, wave, unit, anon, ans, risk=None, zone=None):
    cur.execute("insert into public.responses (client_uuid, form, grp, wave, context, unit_code, anon_code, protocol_version, risk_level, zone, answers) values (%s,%s,%s,%s,%s,%s,%s,'P1.0',%s,%s,%s)",
                (str(uuid.uuid4()), form, grp, wave, ctx, unit, anon, risk, zone, json.dumps(ans)))
people = []
for i in range(a.n):
    d = R.gauss(0, 1); anon = code(i); people.append((anon, d))
    ins("student_screen", "student", "baseline", "baseline", "DCHS-STU", anon, person_answers("student_screen", d, look_well=0.15, stakes_hi=False))
admitted = 0
for anon, d in people:
    if R.random() < 0.70:                                        # did the follow-up check about 3 months later; real wellbeing drifts a little
        ins("student_screen", "student", "followup", "repeat", "DCHS-STU", anon, person_answers("student_screen", d + R.gauss(0.1, 0.4), look_well=0.0, stakes_hi=False))
flush_pending()
for anon, d in people:                                            # outcomes: INVENTED relationship for practice
    if R.random() < 0.85:
        cur.execute("select fm_informal, fm_strain from public.v_student_screen where anon_code=%s and context='baseline'", (anon,)); inf, st = cur.fetchone()
        logit = -2.4 + 0.55 * d + 0.5 * (st or 0) + 0.4 * (inf or 0); p = 1 / (1 + math.exp(-logit))
        if R.random() < p:
            status = R.choice([3, 4, 4, 5]); reason = R.choices([1, 2, 3, 4, 5, 6, 7, 9], [20, 8, 25, 10, 14, 4, 8, 11])[0]; ex = R.randint(1, 9)
        else: status = R.choice([1, 1, 1, 2]); reason = None; ex = None
        cur.execute("insert into public.cohort_outcomes (anon_code, intake, status, exit_month, reason) values (%s,'2026-09',%s,%s,%s)", (anon, status, ex, reason))
    else:
        cur.execute("insert into public.cohort_outcomes (anon_code, intake, status) values (%s,'2026-09',6)", (anon,))
os.makedirs(a.out, exist_ok=True)
for v in ["v_student_screen", "v_student_outcomes", "v_student_paired", "v_student_cohort"]:
    with open(os.path.join(a.out, "SYNTHETIC_" + v + ".csv"), "w", encoding="utf-8-sig", newline="") as f:
        cur.copy_expert("copy (select * from public.%s) to stdout with csv header" % v, f)
print("synthetic data written to", a.out)
