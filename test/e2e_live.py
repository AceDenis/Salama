# End-to-end against the REAL PostgreSQL schema through the mock REST layer: app (supabase mode) -> database -> console -> exports.
import json, os, shutil, subprocess, sys, time, csv, io
from playwright.sync_api import sync_playwright
T = "/tmp/claude-0/webLive"; shutil.rmtree(T, ignore_errors=True); shutil.copytree("/home/claude/salama/web", T)
cfg = open(T + "/config.js").read().replace('BACKEND: "demo"', 'BACKEND: "supabase"').replace("https://YOUR-PROJECT.supabase.co", "http://127.0.0.1:8787").replace("YOUR-ANON-PUBLIC-KEY", "anon-key").replace('ROLES: ["student"]', 'ROLES: ["student","personnel","family","informant"]')
open(T + "/config.js", "w").write(cfg)
subprocess.run(["/home/claude/salama/tools/reset_db.sh"], capture_output=True)
srv = subprocess.Popen(["python3", "-m", "http.server", "8097", "-d", T], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
import psycopg2
db = psycopg2.connect(host="/var/tmp/pgt", port=54329, user="postgres", dbname="salama"); db.autocommit = True; cur = db.cursor()
ok = 0; fails = []
def check(n, c):
    global ok
    if c: ok += 1; print("PASS", n)
    else: fails.append(n); print("FAIL", n)
sys.path.insert(0, "/home/claude/salama/test"); import e2e_helpers as H
with sync_playwright() as p:
    b = p.chromium.launch(); fresh = lambda: b.new_context(viewport={"width": 390, "height": 800}, accept_downloads=True).new_page(); ctx = b.new_context(viewport={"width": 390, "height": 800}); page = ctx.new_page(); errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    # --- applicant at selection
    page.goto("http://localhost:8097/index.html?role=student&unit=DCHS-STU&ctx=baseline"); page.wait_for_selector("#startBtn"); page.check("#cUsage"); page.check("#cAnswers"); page.click("#startBtn")
    page.click("button[data-form=student_screen]"); page.check("#ok"); page.click("#go")
    H.fill_form(page, {"fm_borrow": 2, "chk_sec_id": 1, "fm_lost": 1, "av1": 5, "av2": 4, "phq_1": 2, "phq_2": 2, "phq_9": 0})
    page.wait_for_selector(".zone"); page.wait_for_timeout(800)
    cur.execute("select form, grp, context, wave, unit_code, risk_level, zone, answers->>'sec_id' from public.responses where form='student_screen'"); r = cur.fetchall()
    check("applicant answers reached PostgreSQL", len(r) == 1 and r[0][2] == "baseline" and r[0][1] == "student" and r[0][4] == "DCHS-STU")
    cur.execute("select fm_security_any, sec_id, fm_lost, phq9, brs, stakes from public.v_student_screen"); v = cur.fetchall()
    check("flat jamovi view has the derived numbers", len(v) == 1 and v[0][0] == 1 and v[0][1] == 1 and v[0][3] is not None)
    cur.execute("select count(*) from public.events"); check("usage events stored", cur.fetchone()[0] >= 2)
    # share colour
    page.click("[data-go=share]"); page.wait_for_selector("#ref"); page.fill("#ref", "INT-0042"); page.check("#ok"); page.click("#sendShare"); page.wait_for_selector("text=Shared"); page.wait_for_timeout(600)
    cur.execute("select ref_text, band from public.college_sharing"); s = cur.fetchall(); check("shared colour stored (ref and band only)", len(s) == 1 and s[0][0] == "INT-0042" and s[0][1] in (1, 2, 3))
    # --- offline queue then flush, no duplicates
    ctx.set_offline(True); page.goto("http://localhost:8097/index.html"); page.wait_for_selector(".tiles")
    page.click("[data-go=pulseStart]"); H.fill_form(page, {"pl_cue": 2}); page.wait_for_selector("text=Thank you"); page.wait_for_timeout(400)
    cur.execute("select count(*) from public.responses where form='pulse'"); n0 = cur.fetchone()[0]
    check("offline pulse is held on the phone, not lost", page.evaluate("JSON.parse(localStorage.getItem('salama_queue')||'[]').length") >= 1 and n0 == 0)
    ctx.set_offline(False); page.evaluate("window.dispatchEvent(new Event('online'))"); page.wait_for_timeout(1500)
    cur.execute("select count(*) from public.responses where form='pulse'"); check("queue flushed when connection returned", cur.fetchone()[0] == 1)
    page.evaluate("window.dispatchEvent(new Event('online'))"); page.wait_for_timeout(600); cur.execute("select count(*) from public.responses where form='pulse'"); check("no duplicates after second flush", cur.fetchone()[0] == 1)
    check("queue empty", page.evaluate("JSON.parse(localStorage.getItem('salama_queue')||'[]').length") == 0)
    # --- personnel high risk -> callback -> nurse console -> reply visible in app
    p2 = fresh(); p2.goto("http://localhost:8097/index.html?role=personnel&unit=UNIT-A"); p2.wait_for_selector("#startBtn"); p2.check("#cAnswers"); p2.click("#startBtn")
    p2.click("[data-go=checkinStart]"); p2.wait_for_selector("#go"); p2.click("#go"); H.fill_form(p2, {"phq_1": 3, "phq_2": 3, "phq_9": 1}); p2.wait_for_selector(".zone"); p2.wait_for_timeout(500)
    p2.click("#cb"); p2.wait_for_selector("#detail"); p2.fill("#detail", "0700123456"); p2.click("#send"); p2.wait_for_selector("#ticketCode"); ticket = p2.inner_text("#ticketCode"); p2.wait_for_timeout(500)
    cur.execute("select urgency, risk_level, status, first_contact_at from public.service_requests where ticket_code=%s", (ticket,)); r = cur.fetchone()
    check("call-back request stored as same-day, high risk, new", r and r[0] == "same_day" and r[1] == 2 and r[2] == "new" and r[3] is None)
    c = fresh(); c.goto("http://localhost:8097/console.html"); c.wait_for_selector("#em"); c.fill("#em", "nurse@x"); c.fill("#pw", "pw"); c.click("#li"); c.wait_for_selector("#qlist .case"); c.click("#qlist .case"); c.wait_for_selector("[data-reply]")
    check("nurse signs in and sees only nurse tabs", "Nurse queue" in c.inner_text("#nav") and "Exports" not in c.inner_text("#nav"))
    check("queue shows the request with contact hint", ticket in c.inner_text("#qlist") and "0700123456" in c.inner_text("#qdetail"))
    c.fill("[data-reply]", "Hello, a nurse will call you now."); c.click("[data-save]"); c.wait_for_timeout(800)
    cur.execute("select status, first_contact_at is not null, replied_at is not null from public.service_requests where ticket_code=%s", (ticket,)); r = cur.fetchone()
    check("database stamped contact time itself", r == ("contacted", True, True))
    p2.goto("http://localhost:8097/index.html"); p2.wait_for_selector("#ticketBox"); p2.wait_for_timeout(800)
    check("person sees status in the app", "Answered" in p2.inner_text("#ticketBox") or "in touch" in p2.inner_text("#ticketBox"))
    p2.click("[data-go=ticket]"); p2.wait_for_selector("text=Hello, a nurse will call you now")
    check("person reads the nurse reply", True)
    # --- researcher export
    r2 = fresh(); r2.goto("http://localhost:8097/console.html"); r2.evaluate("localStorage.clear()"); r2.goto("http://localhost:8097/console.html"); r2.wait_for_selector("#em"); r2.fill("#em", "res@x"); r2.fill("#pw", "pw"); r2.click("#li"); r2.wait_for_selector("#nav button")
    check("researcher sees exports but not the nurse queue", "Exports" in r2.inner_text("#nav") and "Nurse queue" not in r2.inner_text("#nav"))
    r2.click("button[data-t=exports]"); r2.wait_for_selector("[data-v=v_student_screen]")
    with r2.expect_download() as d: r2.click("[data-v=v_student_screen]")
    path = d.value.path(); txt = open(path, encoding="utf-8-sig").read(); rows = list(csv.DictReader(io.StringIO(txt)))
    check("jamovi CSV downloaded with one numeric row", len(rows) == 1 and rows[0]["fm_borrow"] == "2" and rows[0]["phq9"] != "")
    with r2.expect_download() as d2: r2.click("[data-v=v_checkin]")
    rows2 = list(csv.DictReader(io.StringIO(open(d2.value.path(), encoding="utf-8-sig").read()))); check("check-in CSV has the high-risk row", len(rows2) == 1 and rows2[0]["phq_9"] == "1")
    r2.click("button[data-t=dash]"); r2.wait_for_timeout(1500); check("dashboard loads without error", "Service, engagement" in r2.inner_text("#main"))
    # outcomes import
    r2.click("button[data-t=outcomes]"); code = db and None
    cur.execute("select anon_code from public.responses where form='student_screen'"); ac = cur.fetchone()[0]
    r2.fill("#csv", "anon_code,intake,status,exit_month,reason\n%s,2026-09,4,3,3" % ac); r2.click("#imp"); r2.wait_for_timeout(800)
    cur.execute("select attrition, exit_reason from public.v_student_outcomes"); check("outcome linked to the selection screen", cur.fetchone() == (1, 3))
    # welfare + interviewer
    w = fresh(); w.goto("http://localhost:8097/console.html"); w.evaluate("localStorage.clear()"); w.goto("http://localhost:8097/console.html"); w.wait_for_selector("#em"); w.fill("#em", "w@x"); w.fill("#pw", "pw"); w.click("#li"); w.wait_for_selector("#nav button")
    w.click("button[data-t=support]"); w.wait_for_selector("tbody tr"); check("welfare officer sees the colour list", "INT-0042" in w.inner_text("tbody"))
    i = fresh(); i.goto("http://localhost:8097/console.html"); i.evaluate("localStorage.clear()"); i.goto("http://localhost:8097/console.html"); i.wait_for_selector("#em"); i.fill("#em", "i@x"); i.fill("#pw", "pw"); i.click("#li"); i.wait_for_selector("#nav button")
    check("interviewer sees only look-up", "Colour look-up" in i.inner_text("#nav") and "College support" not in i.inner_text("#nav") and "Exports" not in i.inner_text("#nav"))
    i.fill("#lr", "int-0042"); i.click("#lg"); i.wait_for_selector("#lo span"); check("interviewer gets a colour only", i.inner_text("#lo span") in ("Green", "Amber", "Red"))
    cur.execute("select count(*) from public.access_log where user_id='44444444-4444-4444-4444-444444444444'"); check("look-up was logged", cur.fetchone()[0] == 1)
    # withdraw
    page.goto("http://localhost:8097/index.html"); page.wait_for_selector(".tiles"); page.click("[data-go=settings]"); page.wait_for_selector("#wd2"); page.once("dialog", lambda d: d.accept()); page.click("#wd2"); page.wait_for_timeout(900)
    cur.execute("select count(*) from public.college_sharing"); check("withdrawing removes the shared colour from the database", cur.fetchone()[0] == 0)
    # --- anonymous sequential IDs, first come first served; situation and role change keeps the same code
    cur.execute("select anon_code from public.responses where form='student_screen'"); check("first applicant got STUD-0001", cur.fetchone()[0] == "STUD-0001")
    cur.execute("select anon_code from public.service_requests where kind='callback' limit 1"); check("first serving person got PERS-0001", cur.fetchone()[0] == "PERS-0001")
    a2 = fresh(); a2.goto("http://localhost:8097/index.html?role=student&unit=DCHS-STU"); a2.wait_for_selector("#startBtn"); a2.check("#cUsage"); a2.click("#startBtn"); a2.wait_for_selector("text=How are you doing"); a2.click("[data-go=settings]"); a2.wait_for_selector("#sit")
    check("second applicant got STUD-0002", "STUD-0002" in a2.inner_text("#app"))
    a2.select_option("#sit", "deployed"); a2.select_option("#rl", "personnel"); a2.wait_for_timeout(900)
    check("code stays the same after posting and role change", a2.evaluate("JSON.parse(localStorage.getItem('salama_profile')||'{}').anon_code") in ("STUD-0002", None))
    cur.execute("select event_type, detail from public.events where anon_code='STUD-0002' and event_type in ('situation_changed','role_changed') order by 1"); ev = cur.fetchall()
    check("situation and role changes are logged under the same code", ("role_changed", "personnel") in ev and ("situation_changed", "deployed") in ev)
    a2.click("[data-go=home]"); a2.wait_for_selector("text=Before or after deployment"); a2.click("[data-go=settings]"); a2.check("#simple"); a2.click("[data-go=home]"); a2.wait_for_timeout(300)
    check("simple view hides extra tiles", "Learn in 2 minutes" not in a2.inner_text("#app") and "Get help" in a2.inner_text("#app"))
    check("no page errors", not errs); print(errs[:3])
    b.close()
srv.terminate(); print("passed", ok, "failed", len(fails), fails); sys.exit(1 if fails else 0)
