// Generates random but valid answer sets for each form (respecting show_if, gate, max_checks) and computes the app's own flattened row.
const fs = require("fs"), vm = require("vm");
const instr = JSON.parse(fs.readFileSync(__dirname + "/instr.json", "utf8"));
const shared = fs.readFileSync(__dirname + "/../tools/shared.js", "utf8");
const ctx = { window: { addEventListener() {}, SALAMA_CONFIG: {} }, localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} }, crypto: globalThis.crypto, console };
ctx.INSTRUMENT = instr.INSTRUMENT; ctx.SCALES = instr.SCALES;
vm.createContext(ctx);
vm.runInContext(shared + "\n;this.flattenRow=flattenRow;this.scoreCheckin=scoreCheckin;this.formItems=formItems;this.flatItems=flatItems;this.derivedColumns=derivedColumns;", ctx);
let seed = Number(process.argv[3] || 7); const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
const pick = a => a[Math.floor(rnd() * a.length)];
function visible(it, a) {
  if (it.show_if && !it.show_if[1].includes(a[it.show_if[0]])) return false;
  if (it.gate) { const [ids, min] = it.gate; if (!ids.every(i => a[i] !== undefined)) return false; if (ids.reduce((t, i) => t + a[i], 0) < min) return false; }
  return true;
}
function make(form) {
  const a = {}, groups = {};
  const bias = rnd();                                   // so some people score high, some low
  for (const sec of instr.INSTRUMENT[form].sections) for (const it of sec.items) {
    if (!visible(it, a)) continue;
    if (it.type === "text") { if (rnd() < 0.3) a[it.id] = "free text " + Math.floor(rnd() * 100); continue; }
    if (it.type === "check") { const g = it.group; groups[g] = groups[g] || 0; const lim = it.max_checks || 99; if (groups[g] < lim && rnd() < 0.3) { a[it.id] = 1; groups[g]++; } else a[it.id] = 0; continue; }
    const opts = it.options.map(o => o[0]);
    const ord = it.measure === "ordinal" && opts.length <= 6 && !opts.includes(9);
    a[it.id] = ord ? opts[Math.min(opts.length - 1, Math.floor(Math.pow(rnd(), 1 + 2 * (1 - bias)) * opts.length))] : pick(opts);
  }
  return a;
}
const out = [], N = Number(process.argv[2] || 60);
const FORMS = ["checkin", "student_screen", "pulse", "baseline_personnel", "baseline_family", "informant", "usability_end", "delphi"];
const CTX = { checkin: ["routine", "pre_deploy", "post_deploy"], student_screen: ["baseline", "followup", "selection", "orientation"], pulse: [null], baseline_personnel: [null], baseline_family: [null], informant: [null], usability_end: [null], delphi: [null] };
const GRP = { checkin: ["personnel", "family"], student_screen: ["student"], pulse: ["personnel"], baseline_personnel: ["personnel"], baseline_family: ["family"], informant: ["informant"], usability_end: ["personnel"], delphi: ["informant"] };
for (let i = 0; i < N; i++) for (const f of FORMS) {
  const a = make(f); const r = { id: require("crypto").randomUUID(), created_at: new Date().toISOString(), client_time: null, grp: pick(GRP[f]), wave: null, context: pick(CTX[f]),
    unit_code: pick(["UNIT-A", "UNIT-B", "DCHS-APP"]), anon_code: "AB" + String(i % 40).padStart(2, "0") + "-" + "XY" + String(i % 40).padStart(2, "0"), protocol_version: "P1.0", risk_level: null, zone: null, answers: a };
  if (f === "checkin" || f === "student_screen") { const sc = ctx.scoreCheckin(a); r.risk_level = sc.risk; r.zone = sc.zone; }
  out.push({ form: f, row: r, flat: ctx.flattenRow(f, r) });
}
fs.writeFileSync(process.argv[4] || __dirname + "/parity.json", JSON.stringify(out));
console.log("generated", out.length);
