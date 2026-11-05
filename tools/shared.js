/* ===== Shared code: configuration, storage, offline queue, backends, scoring ===== */
const CFG = Object.assign({
  BACKEND: "demo", SUPABASE_URL: "", SUPABASE_ANON_KEY: "",
  APP_VERSION: "1.0.0", PROTOCOL_VERSION: "P1.0", STUDY_NAME: "Salama Check-In pilot",
  UNITS: [{ code: "UNIT-A", label: "Pilot unit A" }, { code: "OTHER", label: "Other or not sure" }],
  COVER_NOTE: "A nurse takes requests from 07:00 to 21:00. If you need help outside those hours, use the numbers on the Get help page. Your request will be seen first when cover starts.", CALLBACK_HOURS_HIGH: 8, CALLBACK_DAYS_ROUTINE: 7, DISABLED_ITEMS: [], INTERVIEWER_COLOUR: false, AI_ENDPOINT: "", NURSE_SMS: "", ROLES: ["student"], ETHICS_REF: "Ethics approval number: [to be added]", CONTACT_TEXT: "Supervisor and ethics committee contacts: [to be added]", REFERRALS: [],
  LOCAL_CONTACTS: [], NATIONAL_LINES: []
}, window.SALAMA_CONFIG || {});

const Store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { } }
};

const Util = {
  uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    const b = new Uint8Array(16); crypto.getRandomValues(b); b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
    const h = [...b].map(x => x.toString(16).padStart(2, "0")).join("");
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  },
  code(len, sep) {
    const A = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"; const b = new Uint8Array(len); crypto.getRandomValues(b);
    let s = ""; for (let i = 0; i < len; i++) { s += A[b[i] % A.length]; if (sep && i === sep - 1 && len > sep) s += "-"; } return s;
  },
  esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); },
  /* tells a page that is showing this app inside a frame (the portal) what the app just stored or sent. Never carries answers. */
  emit(kind, text) { try { if (window.parent && window.parent !== window) window.parent.postMessage({ salama: 1, kind, text: String(text), t: Date.now() }, "*"); } catch (e) { } },
  hoursBetween(a, b) { return (new Date(b) - new Date(a)) / 36e5; }
};

/* Colour band shared with the college: green, amber or red. Zones 2 and 3 both map to amber. */
function bandOf(zone) { return zone <= 1 ? 1 : zone <= 3 ? 2 : 3; }
const BAND_NAME = { 1: "Green", 2: "Amber", 3: "Red" };

/* ---------- scoring (mirrors the SQL views; tested against them) ---------- */
function sumItems(a, ids, zeroIf) {
  if (zeroIf && a[zeroIf[0]] === zeroIf[1]) return 0;
  let t = 0; for (const id of ids) { const v = a[id]; if (v === undefined || v === null || v === "") return null; t += Number(v); } return t;
}
/* PHQ-9 and GAD-7 can be answered in adaptive form: if the later items were never asked (all missing) and the short items are present,
   the total is the sum of the short items (later items count as 0). Otherwise every item must be present. */
function isShort(a, key) {
  const sc = SCALES[key]; if (!sc.short) return null;
  if (!sc.short.every(i => a[i] !== undefined && a[i] !== null)) return null;
  const gated = sc.items.filter(i => !sc.short.includes(i));
  return gated.every(i => a[i] === undefined || a[i] === null) ? 1 : 0;
}
function sumScale(a, key) {
  const sc = SCALES[key];
  if (isShort(a, key) === 1) return sc.short.reduce((t, i) => t + Number(a[i]), 0);
  return sumItems(a, sc.items, sc.zero_if);
}
function susScore(a) {
  let t = 0; for (let i = 1; i <= 10; i++) { const v = a["sus" + i]; if (v == null) return null; t += (i % 2 === 1) ? v - 1 : 5 - v; } return t * 2.5;
}
function moneyDerived(a) {
  const n = x => (a[x] === undefined || a[x] === null) ? 0 : Number(a[x]);
  const informal = a.fm_borrow === undefined || a.fm_borrow === null ? null : ([1, 2].includes(a.fm_borrow) ? 1 : a.fm_borrow === 0 ? 0 : null);
  let secAny = null;
  if ([1, 2].includes(a.fm_borrow)) secAny = (n("sec_atm") + n("sec_phone") + n("sec_id") + n("sec_doc") + n("sec_item")) > 0 ? 1 : 0;
  else if (a.fm_borrow === 0) secAny = 0;
  const share = a.fm_share;
  const strain = (a.fm_needs == null && (share == null || share === 9)) ? null :
    ((n("fm_needs") >= 2 || (share != null && share >= 2 && share <= 3)) ? 1 : 0);
  return { fm_informal: informal, fm_security_any: secAny, fm_strain: strain };
}
function srCount(a) { let t = 0, any = false; for (const k of Object.keys(a)) if (k.startsWith("sr_") && k !== "sr_text") { any = true; t += Number(a[k]) || 0; } return any ? t : null; }
function scoreCheckin(a) {
  const phq9 = sumScale(a, "phq9"), gad7 = sumScale(a, "gad7");
  const ptsd5 = sumItems(a, SCALES.ptsd5.items, SCALES.ptsd5.zero_if), auditc = sumItems(a, SCALES.auditc.items, SCALES.auditc.zero_if);
  const life = sumItems(a, SCALES.lifestress.items), lifeA = SCALES.lifestress_a ? sumItems(a, SCALES.lifestress_a.items) : null;
  const item9 = a.phq_9 || 0; const reasons = [];
  let high = false, mod = false;
  if (item9 > 0) { high = true; reasons.push("thoughts of being better off dead or of self-harm"); }
  if (phq9 !== null && phq9 >= 20) { high = true; reasons.push("severe low mood"); }
  if (phq9 !== null && phq9 >= 15 && ((gad7 !== null && gad7 >= 10) || (ptsd5 !== null && ptsd5 >= 3))) { high = true; reasons.push("low mood together with anxiety or trauma symptoms"); }
  if (phq9 !== null && phq9 >= 10 && phq9 < 20) { mod = true; reasons.push("low mood"); }
  if (gad7 !== null && gad7 >= 10) { mod = true; reasons.push("anxiety"); }
  if (ptsd5 !== null && ptsd5 >= 3) { mod = true; reasons.push("trauma reactions"); }
  if (auditc !== null && auditc >= 4) { mod = true; reasons.push("drinking above low-risk levels"); }
  const homeSafety = a.h2 === 1, homeHarm = a.h3 === 1;
  if (homeSafety) { mod = true; reasons.push("safety at home"); }
  if (homeHarm) { mod = true; reasons.push("worry that anger or drinking is affecting home"); }
  const m = moneyDerived(a);
  const moneyHelp = m.fm_strain === 1 || m.fm_informal === 1 || a.fm_effect >= 2 || a.lp1 === 2 || a.la1 === 2;
  const lender = a.fm_threat === 1, heldId = a.sec_id === 1;
  const risk = high ? 2 : mod ? 1 : 0;
  const mild = (phq9 !== null && phq9 >= 5) || (gad7 !== null && gad7 >= 5) || (life !== null && life >= 8) || (lifeA !== null && lifeA >= 6);
  const zone = risk === 2 ? 4 : risk === 1 ? 3 : mild ? 2 : 1;
  return { phq9, gad7, ptsd5, auditc, life: life !== null ? life : lifeA, lifeMax: life !== null ? 20 : 16, item9, risk, zone, reasons, homeSafety, homeHarm, moneyHelp, lender, heldId };
}

/* ---------- flatten answers to the same columns the SQL views produce ---------- */
function formItems(formKey) { const out = []; for (const s of INSTRUMENT[formKey].sections) for (const it of s.items) out.push(it); return out; }
function flatItems(formKey) { return formItems(formKey).filter(i => i.type !== "text"); }
function derivedColumns(formKey) {
  const ids = new Set(formItems(formKey).map(i => i.id)); const out = [];
  for (const [k, sc] of Object.entries(SCALES)) if (sc.items.every(i => ids.has(i))) out.push(k);
  if (formKey === "checkin" || formKey === "student_screen") out.push("phq9_short", "gad7_short", "phq9_pos", "gad7_pos", "ptsd5_pos", "auditc_pos");
  if (formKey === "checkin") out.push("lifestress_high");
  if (ids.has("fm_borrow")) out.push("fm_informal", "fm_security_any", "fm_strain");
  if ([...ids].some(i => i.startsWith("sr_") && i !== "sr_text")) out.push("sr_count");
  if (formKey === "pulse") out.push("pl_poor_sleep", "pl_high_stress", "pl_money_worry");
  return out;
}
function derivedValue(k, a) {
  switch (k) {
    case "phq9": case "gad7": return sumScale(a, k);
    case "ptsd5": case "auditc": case "lifestress": case "lifestress_a": case "stakes": return sumItems(a, SCALES[k].items, SCALES[k].zero_if);
    case "brs": { let t = 0; for (const id of SCALES.brs.items) { const v = a[id]; if (v == null) return null; t += SCALES.brs.rev.includes(id) ? 6 - v : v; } return t; }
    case "phq9_short": return isShort(a, "phq9"); case "gad7_short": return isShort(a, "gad7");
    case "sus": return susScore(a);
    case "phq9_pos": { const v = sumScale(a, "phq9"); return v === null ? null : +(v >= 10); }
    case "gad7_pos": { const v = sumScale(a, "gad7"); return v === null ? null : +(v >= 10); }
    case "ptsd5_pos": { const v = sumItems(a, SCALES.ptsd5.items, SCALES.ptsd5.zero_if); return v === null ? null : +(v >= 3); }
    case "auditc_pos": { const v = sumItems(a, SCALES.auditc.items, SCALES.auditc.zero_if); return v === null ? null : +(v >= 4); }
    case "lifestress_high": { const v = sumItems(a, SCALES.lifestress.items); return v === null ? null : +(v >= 8); }
    case "fm_informal": case "fm_security_any": case "fm_strain": return moneyDerived(a)[k];
    case "sr_count": return srCount(a);
    case "pl_poor_sleep": return a.pl_sleep == null ? null : +(a.pl_sleep >= 3);
    case "pl_high_stress": return a.pl_stress == null ? null : +(a.pl_stress >= 4);
    case "pl_money_worry": return a.pl_money == null ? null : +(a.pl_money >= 3);
  }
}
const META_COLS = ["response_id", "submitted_at", "grp", "wave", "context", "unit_code", "anon_code", "protocol_version", "risk_level", "zone"];
function flattenRow(formKey, r) {
  const row = { response_id: r.id, submitted_at: r.client_time || r.created_at, grp: r.grp, wave: r.wave, context: r.context,
    unit_code: r.unit_code, anon_code: r.anon_code, protocol_version: r.protocol_version, risk_level: r.risk_level, zone: r.zone };
  const a = r.answers || {};
  for (const it of flatItems(formKey)) row[it.id] = a[it.id] === undefined ? "" : a[it.id];
  for (const k of derivedColumns(formKey)) { const v = derivedValue(k, a); row[k] = v === null || v === undefined ? "" : v; }
  return row;
}
function toCSV(rows, cols) {
  const q = v => { if (v === null || v === undefined) return ""; const s = String(v); return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  return "﻿" + cols.join(",") + "\r\n" + rows.map(r => cols.map(c => q(r[c])).join(",")).join("\r\n") + "\r\n";
}
function download(name, text, type) {
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], { type: type || "text/csv;charset=utf-8" }));
  a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
}

/* ---------- backends: demo (this browser only) and supabase ---------- */
const Demo = {
  db() { const d = Store.get("salama_demo_db", {}); for (const k of ["responses", "events", "service_requests", "college_sharing"]) d[k] = d[k] || []; return d; },
  save(d) { Store.set("salama_demo_db", d); }
};

const Api = {
  queue() { return Store.get("salama_queue", []); },
  pending() { return this.queue().length; },
  /* Add a row to the outgoing queue, then try to send straight away. Returns true if everything was sent. */
  async insert(table, row) {
    row = Object.assign({ client_uuid: Util.uuid() }, row);
    const q = this.queue(); q.push({ table, row }); Store.set("salama_queue", q);
    Util.emit("queued", table === "responses" ? row.form + " answers coded as numbers, waiting to send" : table);
    return this.flush();
  },
  async flush() {
    if (this._flushing) { this._again = true; return this.queue().length === 0; } this._flushing = true;
    try {
      const tried = new Set();
      do {
        this._again = false;
        for (const job of this.queue()) {
          if (tried.has(job.row.client_uuid)) continue; tried.add(job.row.client_uuid);
          let res = "retry"; try { res = await this._send(job.table, job.row); } catch (e) { res = "retry"; }
          if (res !== "retry") Store.set("salama_queue", this.queue().filter(j => j.row.client_uuid !== job.row.client_uuid));
          Util.emit(res === "ok" ? "sent" : res === "drop" ? "dropped" : "waiting", job.table === "responses" ? `${job.row.form}: code ${job.row.anon_code || "none"}, colour zone ${job.row.zone == null ? "n/a" : job.row.zone}, risk ${job.row.risk_level == null ? "n/a" : job.row.risk_level}, ${Object.keys(job.row.answers || {}).length} coded answers` : job.table === "service_requests" ? "a call-back or question request" : job.table === "events" ? "usage count: " + (job.row.event_type || "") : job.table);   // re-read, so items added meanwhile are never lost
        }
      } while (this._again || this.queue().some(j => !tried.has(j.row.client_uuid)));
      return this.queue().length === 0;
    } finally { this._flushing = false; }
  },
  /* returns "ok" | "drop" | "retry" */
  async _send(table, row) {
    if (CFG.BACKEND === "demo") {
      const d = Demo.db();
      if (!d[table].some(r => r.client_uuid === row.client_uuid))
        d[table].push(Object.assign({ id: Util.uuid(), created_at: new Date().toISOString() }, table === "service_requests" ? { status: "new" } : {}, row));
      Demo.save(d); return "ok";
    }
    if (CFG.BACKEND === "supabase") {
      if (!navigator.onLine) return "retry";
      const r = await fetch(`${CFG.SUPABASE_URL}/rest/v1/${table}`, {
        method: "POST", headers: { apikey: CFG.SUPABASE_ANON_KEY, Authorization: "Bearer " + CFG.SUPABASE_ANON_KEY, "Content-Type": "application/json", Prefer: "return=minimal" },
        body: JSON.stringify(row) });
      if (r.status === 201 || r.status === 409) return "ok";                    // 409 = already stored (safe retry)
      if (r.status >= 400 && r.status < 500) { console.warn("Rejected by database", r.status, await r.text()); return "drop"; }
      return "retry";
    }
    return "drop";
  },
  async event(type, detail) {
    const p = Store.get(window.PROFILE_KEY || "salama_profile", {}); if (!p.consentUsage) return;
    return this.insert("events", { anon_code: p.anon_code || null, unit_code: p.unit_code || null, event_type: type, detail: detail == null ? null : String(detail).slice(0, 40) });
  },
  async issueId(grp) {          // anonymous sequential participant ID, first come first served; null if offline or full (phone then makes a random one)
    try {
      if (CFG.BACKEND === "demo") { const d = Demo.db(); d.seq = d.seq || {}; const pf = { personnel: "PERS", family: "FAMI", student: "STUD" }[grp]; if (!pf) return null; d.seq[pf] = (d.seq[pf] || 0) + 1; Demo.save(d); return d.seq[pf] > 9999 ? null : pf + "-" + String(d.seq[pf]).padStart(4, "0"); }
      if (!navigator.onLine) return null;
      const ctl = new AbortController(), tm = setTimeout(() => ctl.abort(), 4000);
      const r = await fetch(`${CFG.SUPABASE_URL}/rest/v1/rpc/issue_participant_id`, { method: "POST", signal: ctl.signal, headers: { apikey: CFG.SUPABASE_ANON_KEY, Authorization: "Bearer " + CFG.SUPABASE_ANON_KEY, "Content-Type": "application/json" }, body: JSON.stringify({ p_grp: grp }) });
      clearTimeout(tm); if (!r.ok) return null; const v = await r.json(); return typeof v === "string" && /^[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(v) ? v : null;
    } catch (e) { return null; }
  },
  async withdrawShare(uuid) {
    try {
      if (CFG.BACKEND === "demo") { const d = Demo.db(); const n = d.college_sharing.length; d.college_sharing = d.college_sharing.filter(x => x.client_uuid !== uuid); Demo.save(d); return d.college_sharing.length < n; }
      if (!navigator.onLine) return undefined;
      const r = await fetch(`${CFG.SUPABASE_URL}/rest/v1/rpc/withdraw_share`, { method: "POST", headers: { apikey: CFG.SUPABASE_ANON_KEY, Authorization: "Bearer " + CFG.SUPABASE_ANON_KEY, "Content-Type": "application/json" }, body: JSON.stringify({ p_client_uuid: uuid }) });
      return r.ok ? await r.json() : undefined;
    } catch (e) { return undefined; }
  },
  async getTicket(ticket) {
    try {
      if (CFG.BACKEND === "demo") {
        const r = Demo.db().service_requests.find(x => x.ticket_code === ticket);
        return r ? { status: r.status, nurse_reply: r.nurse_reply || null, replied_at: r.replied_at || null } : null;
      }
      if (!navigator.onLine) return undefined;
      const r = await fetch(`${CFG.SUPABASE_URL}/rest/v1/rpc/get_ticket`, { method: "POST",
        headers: { apikey: CFG.SUPABASE_ANON_KEY, Authorization: "Bearer " + CFG.SUPABASE_ANON_KEY, "Content-Type": "application/json" }, body: JSON.stringify({ p_ticket: ticket }) });
      if (!r.ok) return undefined; const j = await r.json(); return Array.isArray(j) ? (j[0] || null) : j;
    } catch (e) { return undefined; }
  }
};
window.addEventListener("online", () => Api.flush());
