#!/usr/bin/env python3
"""Check that your Supabase database is connected and safe, BEFORE you share any link.
Usage: python3 tools/check_setup.py https://YOUR-PROJECT.supabase.co YOUR_ANON_KEY
It sends one test row marked protocol_version=TEST (filter these out in jamovi), then confirms the public key can NOT read anything."""
import json, sys, uuid, urllib.request, urllib.error
url, key = sys.argv[1].rstrip("/"), sys.argv[2]
def call(method, path, body=None, extra=None):
    h = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"}; h.update(extra or {})
    r = urllib.request.Request(url + "/rest/v1/" + path, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=20) as x: return x.status, x.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  -> " + detail))
st, tx = call("POST", "responses", {"client_uuid": str(uuid.uuid4()), "form": "pulse", "grp": "personnel", "protocol_version": "TEST", "answers": {"pl_sleep": 2}}, {"Prefer": "return=minimal"})
check("test answer was stored (database reachable, tables exist)", st == 201, "%s %s" % (st, tx[:120]))
st, tx = call("GET", "responses?select=id&limit=1")
check("public key cannot read answers", st in (401, 403) or tx.strip() in ("[]", ""), "%s %s" % (st, tx[:120]))
st, tx = call("GET", "service_requests?select=id&limit=1"); check("public key cannot read the nurse queue", st in (401, 403) or tx.strip() == "[]", "%s %s" % (st, tx[:120]))
st, tx = call("GET", "college_sharing?select=id&limit=1"); check("public key cannot read shared colours", st in (401, 403) or tx.strip() == "[]", "%s %s" % (st, tx[:120]))
st, tx = call("DELETE", "responses?protocol_version=eq.TEST"); check("public key cannot delete answers", st in (401, 403, 404) or tx.strip() in ("", "[]"), "%s %s" % (st, tx[:120]))
st, tx = call("POST", "rpc/get_ticket", {"p_ticket": "T-NONEXIST"}); check("ticket look-up works", st == 200, "%s %s" % (st, tx[:120]))
print("\nALL GOOD. You can share your links." if ok else "\nSOMETHING IS WRONG. Do not share links yet. Re-run the SQL files in order, then run this again.")
sys.exit(0 if ok else 1)
