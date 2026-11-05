"""Lists on-screen text that has no Kiswahili yet. Usage: python3 test/crawl_missing.py"""
import subprocess, time, shutil, json, sys
sys.path.insert(0, "/home/claude/salama/test")
from e2e_helpers import fill_form
T = "/tmp/claude-0/crawl/web"; shutil.rmtree(T, ignore_errors=True); shutil.copytree("/home/claude/salama/web", T)
srv = subprocess.Popen(["python3", "-m", "http.server", "8097", "-d", T], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
from playwright.sync_api import sync_playwright
miss = set()
def grab(page):
    for s in page.evaluate("Lang.missing()"): miss.add(s)
try:
  with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 390, "height": 800}); page = ctx.new_page()
    page.add_init_script("localStorage.setItem('salama_lang','\"sw\"')")
    page.goto("http://localhost:8097/index.html"); page.wait_for_selector("#startBtn"); grab(page)
    page.check("#cUsage"); page.check("#cAnswers"); page.click("#startBtn"); page.wait_for_selector("#app button"); page.wait_for_timeout(300); grab(page)
    def G(v, **k):
        try: page.evaluate("([v,k])=>window.__salama.go(v,k)", [v, k])
        except Exception as e: print("skip", v, str(e)[:80])
    for v in ["settings", "helpHub", "safety", "guide", "callback", "ask", "navigator", "lessons", "buddy", "studyConsent", "pulseStart"]:
        G(v); page.wait_for_timeout(250); grab(page)
        if v == "guide":
            page.fill("#app input[type=text], #app textarea", "I cannot sleep"); 
            try: page.click("#app button:has-text('Tuma'), #app button:has-text('Send')"); page.wait_for_timeout(500); grab(page)
            except Exception as e: pass
    G("lesson", id="sleep"); page.wait_for_timeout(250); grab(page)
    G("lesson", id="idcard"); page.wait_for_timeout(250); grab(page)
    # pulse form
    G("pulseStart"); fill_form(page); page.wait_for_timeout(400); grab(page)
    for ctx_ in ("routine",):
        G("checkinStart"); page.wait_for_timeout(300); grab(page)
    page.evaluate("window.__salama.go('home')"); page.wait_for_timeout(300); grab(page)
    # run student form to result
    G("home"); 
    page.click("button[data-form=student_screen]"); page.wait_for_selector("#ok"); page.wait_for_timeout(200); grab(page)
    page.check("#ok"); page.click("#go")
    grab(page); fill_form(page, {"fm_borrow": 2, "chk_sec_id": 1, "fm_lost": 1, "phq_1": 2, "phq_2": 2, "phq_9": 1, "ptsd_1":1, "ptsd_2":1,"ptsd_3":1})
    page.wait_for_selector(".zone"); page.wait_for_timeout(400); grab(page)
    for sel in ["button:has-text('See what would be shared')", "button:has-text('Ask a nurse')"]:
        pass
    G("share"); page.wait_for_timeout(300); grab(page)
    G("callback", reason="x"); page.wait_for_timeout(300); grab(page)
    G("ticket", id="x"); page.wait_for_timeout(300); grab(page)
    b.close()
finally:
    srv.kill()
json.dump(sorted(miss), open("/tmp/claude-0/crawl/missing.json", "w"), ensure_ascii=False, indent=0)
print(len(miss))
