import json, sys, psycopg2, psycopg2.extras
sys.path.insert(0, "/home/claude/salama/tools")
import build
data = json.load(open("/home/claude/salama/test/parity.json"))
con = psycopg2.connect(host="/var/tmp/pgt", port=54329, user="postgres", dbname="salama"); con.autocommit = True
cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute("truncate public.responses cascade")
for d in data:
    r = d["row"]
    cur.execute("insert into public.responses (id, client_uuid, client_time, form, grp, wave, context, unit_code, anon_code, protocol_version, risk_level, zone, answers) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (r["id"], r["id"], r["client_time"], d["form"], r["grp"], r["wave"], r["context"], r["unit_code"], r["anon_code"], r["protocol_version"], r["risk_level"], r["zone"], json.dumps(r["answers"])))
bad = 0; checked = 0; per = {}
for form, view in build.VIEW.items():
    cur.execute("select * from public.%s" % view); rows = {str(x["response_id"]): x for x in cur.fetchall()}
    for d in [x for x in data if x["form"] == form]:
        sql = rows[d["row"]["id"]]
        for col, js in d["flat"].items():
            if col in ("response_id", "submitted_at"): continue
            sv = sql.get(col, "MISSING")
            if sv == "MISSING": print("missing column in view", view, col); bad += 1; continue
            jv = None if js == "" or js is None else js
            if sv is not None and not isinstance(sv, str): sv = float(sv)
            if jv is not None and not isinstance(jv, str): jv = float(jv)
            checked += 1; per[form] = per.get(form, 0) + 1
            if sv != jv:
                bad += 1
                if bad < 15: print("MISMATCH", view, col, "sql=", sv, "js=", jv, d["row"]["id"][:8])
        extra = set(sql) - set(d["flat"]) 
        if extra: print("view has extra columns not in app export", view, sorted(extra)[:6]); break
print("cells checked", checked, "mismatches", bad, per)
sys.exit(1 if bad else 0)
