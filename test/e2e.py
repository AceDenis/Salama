import json, subprocess, time, sys, shutil
T = "/tmp/claude-0/webDemo"; shutil.rmtree(T, ignore_errors=True); shutil.copytree("/home/claude/salama/web", T)
_c = open(T + "/config.js").read().replace('ROLES: ["student"]', 'ROLES: ["student","personnel","family","informant"]'); open(T + "/config.js", "w").write(_c)
from playwright.sync_api import sync_playwright
srv = subprocess.Popen(["python3", "-m", "http.server", "8099", "-d", T], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
ok = 0; fails = []
def check(name, cond):
    global ok
    if cond: ok += 1; print("PASS", name)
    else: fails.append(name); print("FAIL", name)
def fill_form(page, overrides=None, max_sections=20):
    overrides = overrides or {}
    for _ in range(max_sections):
        page.wait_for_selector("#wNext")
        # answer every visible unanswered radio group: first option, unless overridden
        page.evaluate("""(ov) => {
          document.querySelectorAll('#wForm fieldset:not([hidden])[data-id]').forEach(fs => {
            const id = fs.dataset.id; const radios = [...fs.querySelectorAll('input[type=radio]')];
            if (!radios.length || radios.some(r => r.checked)) { if (!(id in ov)) return; }
            const want = id in ov ? String(ov[id]) : radios[0].value; const r = radios.find(x => x.value === want) || radios[0]; r.click();
          });
          Object.entries(ov).forEach(([k, v]) => { if (k.startsWith('chk_')) { const c = document.querySelector(`[data-check=${k.slice(4)}]`); if (c && !c.checked) c.click(); } });
          document.querySelectorAll('#wForm fieldset:not([hidden])[data-id]').forEach(fs => { const id = fs.dataset.id; const radios=[...fs.querySelectorAll('input[type=radio]')]; if (radios.length && !radios.some(r=>r.checked)) radios[0].click(); });
        }""", overrides)
        page.wait_for_timeout(60)
        # repeat once: newly revealed gated items
        page.evaluate("""() => document.querySelectorAll('#wForm fieldset:not([hidden])[data-id]').forEach(fs => { const radios=[...fs.querySelectorAll('input[type=radio]')]; if (radios.length && !radios.some(r=>r.checked)) radios[0].click(); })""")
        txt = page.inner_text("#wNext"); page.click("#wNext"); page.wait_for_timeout(120)
        if page.locator("#cont").count(): page.click("#cont"); page.wait_for_timeout(80)
        if txt.strip() == "Finish": return
    raise Exception("form did not finish")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 390, "height": 800}); page = ctx.new_page(); errs = []
    page.on("pageerror", lambda e: errs.append(str(e))); page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    # ---------- applicant pathway
    page.goto("http://localhost:8099/index.html?role=student&unit=DCHS-APP&ctx=selection"); page.wait_for_selector("#startBtn")
    check("student role preselected", page.locator("input[value=student]").is_checked())
    check("protections shown before consent", "Your protections" in page.inner_text("#app") and "Ethics approval number" in page.inner_text("#app"))
    check("applicant note visible", page.locator("#apNote").is_visible())
    page.check("#cUsage"); page.check("#cAnswers"); page.click("#startBtn"); page.wait_for_selector("text=DCHS wellbeing check")
    check("applicant home tile", page.locator("button[data-form=student_screen]").count() == 1)
    check("no deployment button for applicants", page.locator("text=Before or after deployment").count() == 0)
    page.click("button[data-form=student_screen]"); page.wait_for_selector("#ok")
    check("consent says it is not an assessment", "not an assessment" in page.inner_text("#app"))
    check("consent says interviewers do not see it (flag off)", "do not see it" in page.inner_text("#app"))
    page.check("#ok"); page.click("#go")
    fill_form(page, {"fm_borrow": 2, "chk_sec_id": 1, "fm_lost": 1, "av1": 5, "av2": 4, "av3": 4, "av4": 2, "phq_1": 2, "phq_2": 2, "phq_9": 0})
    page.wait_for_selector(".zone"); page.wait_for_timeout(400)
    check("result shown for applicant", page.locator(".zone").count() == 1)
    check("money card with held ID advice", "holding your ID" in page.inner_text("#app"))
    check("share card offered, nothing shared by default", page.locator("text=Want the college support office to know?").count() == 1)
    db = page.evaluate("JSON.parse(localStorage.getItem('salama_demo_db')||'{}')")
    app_rows = [r for r in db.get("responses", []) if r["form"] == "student_screen"]
    check("applicant response stored with context selection", len(app_rows) == 1 and app_rows[0]["context"] == "selection" and app_rows[0]["grp"] == "student")
    check("nothing in college_sharing before opt-in", len(db.get("college_sharing", [])) == 0)
    check("held ID answer captured", app_rows[0]["answers"].get("sec_id") == 1 and app_rows[0]["answers"].get("fm_lost") == 1)
    zone = app_rows[0]["zone"]
    page.click("[data-go=share]"); page.wait_for_selector("#ref")
    check("share preview shows only colour", "no scores, no answers" in page.inner_text("#app").lower())
    page.click("#sendShare"); check("share needs identifier+consent", page.locator("#se").is_visible())
    page.fill("#ref", "INT-0042"); page.check("#ok"); page.click("#sendShare"); page.wait_for_selector("text=Shared"); page.wait_for_timeout(300)
    db = page.evaluate("JSON.parse(localStorage.getItem('salama_demo_db')||'{}')")
    cs = db.get("college_sharing", [])
    band = 1 if zone <= 1 else 2 if zone <= 3 else 3
    check("college_sharing has colour band only", len(cs) == 1 and cs[0]["band"] == band and set(cs[0]).isdisjoint({"answers", "phq9", "scores"}))
    # console lookup in same origin
    c2 = ctx.new_page(); c2.goto("http://localhost:8099/console.html"); c2.wait_for_selector("#nav button")
    names = c2.inner_text("#nav"); check("console shows college support and look-up tabs", "College support" in names and "Colour look-up" in names)
    c2.click("button[data-t=lookup]"); c2.fill("#lr", "int-0042"); c2.click("#lg"); c2.wait_for_selector("#lo span")
    check("interviewer look-up returns colour", c2.inner_text("#lo span") in ("Green", "Amber", "Red"))
    c2.fill("#lr", "NOPE-1"); c2.click("#lg"); c2.wait_for_timeout(200)
    check("look-up for non-sharer says nothing about the person", "tells you nothing" in c2.inner_text("#lo"))
    c2.click("button[data-t=support]"); c2.wait_for_selector("tbody tr")
    check("support list shows ref", "INT-0042" in c2.inner_text("tbody"))
    # withdraw
    page.goto("http://localhost:8099/index.html"); page.wait_for_selector(".tiles")
    page.click("[data-go=settings]"); page.wait_for_selector("#wd2"); page.once("dialog", lambda d: d.accept()); page.click("#wd2"); page.wait_for_selector(".tiles")
    db = page.evaluate("JSON.parse(localStorage.getItem('salama_demo_db')||'{}')"); check("withdraw removes the shared colour", len(db.get("college_sharing", [])) == 0)
    # ---------- get help hub and guide
    page.click("[data-go=helpHub]"); page.wait_for_selector("text=Talk to a person")
    check("help hub lists national lines", "1195" in page.inner_text("#app") and "Befrienders" in page.inner_text("#app"))
    check("help hub has tel links", page.locator("a[href^='tel:']").count() >= 4)
    page.click("[data-go=guide]"); page.wait_for_selector("#gi")
    check("guide says nothing leaves phone", "Nothing you type leaves it" in page.inner_text("#app"))
    page.fill("#gi", "I owe a shylock and he holds my ID card"); page.press("#gi", "Enter"); page.wait_for_timeout(300)
    check("guide routes money to lessons", page.locator("button[data-id=money], button[data-id=idcard]").count() >= 1)
    page.fill("#gi", "I want to kill myself"); page.press("#gi", "Enter"); page.wait_for_timeout(300)
    check("guide crisis shows safety block and nurse button", page.locator(".safety").count() >= 1 and "glad you said that" in page.inner_text("#chat"))
    page.fill("#gi", "he beats me at home"); page.press("#gi", "Enter"); page.wait_for_timeout(300)
    check("guide danger wording shows safety", "safety comes first" in page.inner_text("#chat").lower())
    # ---------- personnel check-in with money items
    page.evaluate("localStorage.clear()"); page.goto("http://localhost:8099/index.html?role=personnel&unit=UNIT-A"); page.wait_for_selector("#startBtn"); page.check("#cAnswers"); page.click("#startBtn"); page.wait_for_selector(".tiles")
    page.click("[data-go=checkinStart]"); page.wait_for_selector("#go"); page.click("#go")
    fill_form(page, {"phq_1": 3, "phq_2": 3, "phq_9": 1, "fm_borrow": 2, "chk_sec_id": 1, "fm_lost": 1, "fm_threat": 1, "h2": 1})
    page.wait_for_selector(".zone"); page.wait_for_timeout(400); txt = page.inner_text("#app")
    check("high risk zone for item 9", "Needs care now" in txt); check("safety block shown", page.locator(".safety").count() >= 1)
    check("lender threat advice", "threatening or shaming" in txt)
    db = page.evaluate("JSON.parse(localStorage.getItem('salama_demo_db')||'{}')"); r = [x for x in db["responses"] if x["form"] == "checkin"][0]
    check("check-in stored with risk 2", r["risk_level"] == 2 and r["zone"] == 4)
    page.click("#cb"); page.wait_for_selector("#detail"); page.fill("#detail", "0700000000"); page.click("#send"); page.wait_for_selector("#ticketCode")
    check("callback ticket created", page.inner_text("#ticketCode").startswith("T-"))
    c2.goto("http://localhost:8099/console.html"); c2.wait_for_selector("#nav button"); c2.click("button[data-t=queue]"); c2.wait_for_selector("#qlist .case"); c2.click("#qlist .case"); c2.wait_for_selector("#qdetail h2"); c2.wait_for_timeout(300)
    check("nurse queue shows same-day high risk", "HIGH" in c2.inner_text("#qlist") and "same" in c2.inner_text("#qdetail").lower())
    check("no page errors", not errs)
    if errs: print(errs[:5])
    b.close()
srv.terminate()
print("passed", ok, "failed", len(fails), fails); sys.exit(1 if fails else 0)
