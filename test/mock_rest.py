#!/usr/bin/env python3
"""A small stand-in for Supabase (PostgREST + auth) for testing against the real PostgreSQL schema, roles and RLS.
Supports the subset of the REST API that the app and console use. Run: python3 test/mock_rest.py 8787"""
import csv, io, json, re, sys, urllib.parse, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import psycopg2, psycopg2.extras
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
ANON = "anon-key"; USERS = {"nurse@x": ("11111111-1111-1111-1111-111111111111", "pw"), "res@x": ("22222222-2222-2222-2222-222222222222", "pw"),
                           "w@x": ("33333333-3333-3333-3333-333333333333", "pw"), "i@x": ("44444444-4444-4444-4444-444444444444", "pw"), "a@x": ("55555555-5555-5555-5555-555555555555", "pw")}
TOKENS = {}
def conn():
    c = psycopg2.connect(host="/var/tmp/pgt", port=54329, user="postgres", dbname="salama"); c.autocommit = True; return c
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body="", ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self): self._send(204)
    def _who(self):
        t = (self.headers.get("Authorization") or "").replace("Bearer ", "")
        if t in TOKENS: return "authenticated", TOKENS[t]
        return "anon", ""
    def _run(self, method):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query, keep_blank_values=True); n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or "null") if n else None
        if u.path == "/auth/v1/token":
            if q.get("grant_type") == ["password"]:
                e = body.get("email"); 
                if e in USERS and USERS[e][1] == body.get("password"):
                    tok = "tok-" + uuid.uuid4().hex; TOKENS[tok] = USERS[e][0]; return self._send(200, json.dumps({"access_token": tok, "refresh_token": "r", "expires_in": 3600}))
                return self._send(400, json.dumps({"error": "invalid"}))
        if not u.path.startswith("/rest/v1/"): return self._send(404, "{}")
        role, uid = self._who(); name = u.path[len("/rest/v1/"):]
        c = conn(); cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("set role %s" % role); cur.execute("select set_config('test.uid', %s, false)", (uid,))
            if name.startswith("rpc/"):
                fn = name[4:]; args = body or {}; keys = list(args)
                cur.execute("select * from public.%s(%s)" % (fn, ",".join("%s => %%s" % k for k in keys)), [args[k] for k in keys])
                rows_ = cur.fetchall(); return self._send(200, json.dumps(rows_[0][list(rows_[0])[0]] if (len(rows_) == 1 and len(rows_[0]) == 1) else rows_, default=str))
            if method == "POST":
                rows = body if isinstance(body, list) else [body]
                for r in rows:
                    cols = list(r); vals = [json.dumps(r[k]) if isinstance(r[k], (dict, list)) else r[k] for k in cols]
                    sql = "insert into public.%s (%s) values (%s)" % (name, ",".join(cols), ",".join(["%s"] * len(cols)))
                    if q.get("on_conflict"):
                        k = q["on_conflict"][0]; sql += " on conflict (%s) do update set %s" % (k, ",".join("%s = excluded.%s" % (x, x) for x in cols if x != k))
                    cur.execute(sql, vals)
                return self._send(201)
            filt = []; vals = []
            for k, v in q.items():
                if k in ("select", "order", "limit", "on_conflict"): continue
                m = re.match(r"eq\.(.*)", v[0]); filt.append("%s = %%s" % k); vals.append(m.group(1))
            where = (" where " + " and ".join(filt)) if filt else ""
            if method == "PATCH":
                cols = list(body); cur.execute("update public.%s set %s%s returning 1" % (name, ",".join("%s = %%s" % k for k in cols), where), [body[k] for k in cols] + vals); return self._send(204)
            if method == "DELETE":
                cur.execute("delete from public.%s%s" % (name, where), vals); return self._send(204)
            order = ""
            if "order" in q: col, _, d = q["order"][0].partition("."); order = " order by %s %s" % (col, "desc" if d == "desc" else "asc")
            lim = " limit %d" % int(q["limit"][0]) if "limit" in q else ""
            cur.execute("select * from public.%s%s%s%s" % (name, where, order, lim), vals); rows = cur.fetchall()
            if "text/csv" in (self.headers.get("Accept") or ""):
                if not rows: return self._send(200, "", "text/csv")
                buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(rows[0])); w.writeheader(); [w.writerow({k: ("" if v is None else v) for k, v in r.items()}) for r in rows]; return self._send(200, buf.getvalue(), "text/csv")
            return self._send(200, json.dumps(rows, default=str))
        except psycopg2.errors.InsufficientPrivilege as e: return self._send(401 if role == "anon" else 403, json.dumps({"message": str(e).strip()}))
        except psycopg2.errors.UniqueViolation as e: return self._send(409, json.dumps({"message": str(e).strip()}))
        except psycopg2.errors.RaiseException as e: return self._send(400, json.dumps({"message": str(e).strip()}))
        except psycopg2.Error as e: return self._send(403 if "row-level security" in str(e) else 400, json.dumps({"message": str(e).strip()}))
        finally: c.close()
    def do_GET(self): self._run("GET")
    def do_POST(self): self._run("POST")
    def do_PATCH(self): self._run("PATCH")
    def do_DELETE(self): self._run("DELETE")
ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
