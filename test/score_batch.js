// Reads a JSON list of answer objects on stdin and prints [{risk, zone}] using the app's own scoring code (tools/shared.js).
const fs = require("fs"), vm = require("vm");
const instr = JSON.parse(fs.readFileSync(__dirname + "/instr.json", "utf8"));
const ctx = { window: { addEventListener() {}, SALAMA_CONFIG: {} }, localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} }, crypto: globalThis.crypto, console, INSTRUMENT: instr.INSTRUMENT, SCALES: instr.SCALES };
vm.createContext(ctx); vm.runInContext(fs.readFileSync(__dirname + "/../tools/shared.js", "utf8") + "\n;this.scoreCheckin=scoreCheckin;", ctx);
const rows = JSON.parse(fs.readFileSync(0, "utf8")); process.stdout.write(JSON.stringify(rows.map(a => { const s = ctx.scoreCheckin(a); return { risk: s.risk, zone: s.zone }; })));
