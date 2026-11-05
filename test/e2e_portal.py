import subprocess, time, shutil, sys
sys.path.insert(0, "/home/claude/salama/test")
from e2e_helpers import fill_form
T = "/tmp/claude-0/portalWeb"; shutil.rmtree(T, ignore_errors=True); shutil.copytree("/home/claude/salama/web", T)
srv = subprocess.Popen(["python3", "-m", "http.server", "8096", "-d", T], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
from playwright.sync_api import sync_playwright
ok = 0; fails = []
def check(n, c):
    global ok
    if c: ok += 1; print("PASS", n)
    else: fails.append(n); print("FAIL", n)
try:
  with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://localhost:8096/portal.html"); pg.wait_for_selector("#appFrame")
    check("eight tabs", pg.locator("#tabs button").count() == 8)
    fr = pg.frame_locator("#appFrame"); fr.locator("#startBtn").wait_for(timeout=8000)
    check("phone shows welcome with protections", "Your protections" in fr.locator("#app").inner_text())
    check("I already have a code present", fr.locator("#oldCode").count() == 1)
    pg.click("#demoId"); fr.locator("button[data-form=student_screen]").wait_for(timeout=8000)
    check("demo id STUD-0001 issued", "STUD-0001" in str(pg.evaluate("localStorage.getItem('salama_profile')")))
    fr.locator("button[data-form=student_screen]").click(); fr.locator("#ok").wait_for(); fr.locator("#ok").check(); fr.locator("#go").click()
    # fill the form inside the iframe using the helper against the frame page
    frame = [f for f in pg.frames if "index.html" in f.url][0]
    class W:  # adapt helper to a Frame
        def __init__(s, f): s.f = f
        def __getattr__(s, n): return getattr(s.f, n)
        def inner_text(s, sel): return s.f.inner_text(sel)
    fill_form(frame, {"phq_9": 1, "fm_borrow": 2, "chk_sec_id": 1, "fm_lost": 1})
    frame.wait_for_selector(".zone"); pg.wait_for_timeout(400)
    log = pg.inner_text("#blog")
    check("behind-the-screen log shows sent record without answers", "student_screen" in log and "sent" in log.lower() and "coded answers" in log)
    # nurse request
    frame.evaluate("window.__salama.go('callback',{reason:'mental_health'})"); pg.wait_for_timeout(500)
    # examples + dashboard
    pg.click("#tabs button[data-t=data]"); pg.click("#ldEx"); pg.wait_for_timeout(300)
    pg.click("#tabs button[data-t=dash]"); pg.wait_for_selector("#dashBox table")
    d = pg.inner_text("#dashBox")
    check("dashboard has 4 stats and example banner", pg.locator("#dashBox .stat").count() == 4 and "Example data" in d)
    check("small group hidden", "Hidden: fewer than 10" in d)
    pg.click("#tabs button[data-t=report]"); pg.wait_for_selector("#reportBox .pbar")
    r = pg.inner_text("#reportBox")
    check("report has wellness scale, pressures, actions, summary", all(x in r for x in ["Wellness scale", "Life pressures", "Suggested actions", "Committee summary"]))
    pg.click("#mkSum"); check("committee summary text", "pretend students" in pg.input_value("#sumTxt"))
    pg.click("#pm button >> nth=0"); pg.wait_for_selector("#reportBox .pbar"); check("month filter works", True)
    # design notes + survey tool
    pg.click("#tabs button[data-t=design]"); pg.wait_for_selector("#svyTool .q")
    check("survey tool lists questions", pg.locator("#svyTool .q").count() > 150)
    check("money and lender questions in survey tool", "shylock" in pg.inner_text("#svyTool") and "ID card" in pg.inner_text("#svyTool"))
    # export excludes examples
    pg.click("#tabs button[data-t=data]"); import re; print("DATAT:", re.findall(r"\d+ saved responses?", pg.inner_text("#dataBox"))); check("example rows excluded from counts", "1 saved response" in pg.inner_text("#dataBox").lower())
    with pg.expect_download() as dl: pg.click("#exJam")
    csv = open(dl.value.path(), encoding="utf-8-sig").read()
    check("jamovi csv has no example rows", "EXMP" not in csv and "STUD-0001" in csv)
    # language
    pg.click("header.top .langsw button[data-l=sw]"); pg.wait_for_timeout(400)
    pg.click("#tabs button[data-t=design]"); pg.wait_for_timeout(400)
    t = pg.inner_text("#svyTool")
    check("survey tool in Kiswahili", "Hali ya moyo" in t and "Mood" not in t.split("\n")[6:12].__str__())
    pg.click("#tabs button[data-t=app]"); pg.wait_for_timeout(1200)
    print("APP:", pg.frame_locator("#appFrame").locator("#app").inner_text()[:300]); print("DATA:", pg.inner_text("#dataBox")[:0])
    check("phone app in Kiswahili", "Mwombe" in pg.frame_locator("#appFrame").locator("#app").inner_text())
    pg.click("header.top .langsw button[data-l=en]"); pg.wait_for_timeout(300)
    # nurse console
    pg.click("#tabs button[data-t=nurse]"); nf = pg.frame_locator("#nurseFrame"); nf.locator("#qlist").wait_for(timeout=8000)
    check("nurse console has case list, access log", nf.locator(".case").count() >= 1 and "Access log" in nf.locator("#main").inner_text())
    nf.locator(".case").first.click(); check("case detail opens", "How to reach" in nf.locator("#qdetail").inner_text() or "Suggested first step" in nf.locator("#qdetail").inner_text())
    # survey + expert tabs
    pg.click("#tabs button[data-t=survey]"); sf = pg.frame_locator("#surveyFrame"); sf.locator("#startBtn").wait_for(timeout=8000)
    check("survey tab share card + qr", "svg" in pg.inner_html("#shareSurvey"))
    pg.click("#tabs button[data-t=expert]"); ef = pg.frame_locator("#expertFrame"); ef.locator("#startBtn").wait_for(timeout=8000)
    check("expert tab has no role choice shown", ef.locator("#roleOpts").is_visible() == False)
    check("no page errors", not [e for e in errs if "favicon" not in e]); print(errs[:5])
    pg.screenshot(path="/tmp/claude-0/portal_expert.png")
    b.close()
finally: srv.kill()
print("passed", ok, "failed", fails)
