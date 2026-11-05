const fs = require("fs");
const D = require("docx");
const { Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, ImageRun, PageBreak, LevelFormat } = D;
const FONT = "Times New Roman";
const W = 9026; // A4 with 1-inch margins
function runs(text, base = {}) {
  const out = []; const re = /(\*\*[^*]+\*\*|\^\^[^^]+\^\^)/g; let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: t.slice(2, -2), italics: true, font: FONT, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}
const p = (text, o = {}) => new Paragraph({ children: runs(text, o.run || {}), alignment: o.align || AlignmentType.JUSTIFIED, spacing: { line: o.line || 360, after: o.after === undefined ? 120 : o.after, before: o.before || 0 }, indent: o.indent, keepNext: o.keepNext });
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })], pageBreakBefore: true });
const h1n = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: t, font: FONT })] });
const bullets = (items, lvl = 0) => items.map(t => new Paragraph({ numbering: { reference: "bul", level: lvl }, children: runs(t), spacing: { line: 340, after: 60 }, alignment: AlignmentType.LEFT }));
let numCount = 0; const numRefs = [];
const numbered = items => { const ref = "num" + (++numCount); numRefs.push(ref); return items.map(t => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), spacing: { line: 340, after: 60 }, alignment: AlignmentType.LEFT })); };
const border = { style: BorderStyle.SINGLE, size: 4, color: "9FB3AE" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0); const fs_ = o.size || 19;
  const cell = (t, w, head, shade) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders, margins: { top: 60, bottom: 60, left: 90, right: 90 },
    shading: head ? { fill: "0F6B63", type: ShadingType.CLEAR, color: "auto" } : shade ? { fill: shade, type: ShadingType.CLEAR, color: "auto" } : undefined,
    children: String(t).split("||").map(line => new Paragraph({ children: runs(line, { size: fs_, color: head ? "FFFFFF" : undefined, bold: head ? true : undefined }), spacing: { line: 250, after: 40 }, alignment: AlignmentType.LEFT })) });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [
    new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, widths[i], true)) }),
    ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false, ri % 2 ? "F1F6F5" : null)) }))] });
}
const gap = (n = 120) => new Paragraph({ children: [], spacing: { after: n } });
const caption = t => new Paragraph({ children: runs(t, { size: 20, bold: false }), alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200, line: 260 } });
const tcap = t => new Paragraph({ children: runs(t, { size: 20, bold: true }), alignment: AlignmentType.LEFT, spacing: { before: 160, after: 80, line: 260 }, keepNext: true });
function png(path) { const b = fs.readFileSync(path); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b }; }
function fig(path, maxW, cap) {
  const im = png(path); const w = maxW, h = Math.round(maxW * im.h / im.w);
  return [new Paragraph({ children: [new ImageRun({ type: "png", data: im.data, transformation: { width: w, height: h }, altText: { title: cap, description: cap, name: path } })], alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, keepNext: true }), caption(cap)];
}
module.exports = { D, FONT, W, runs, p, h1, h1n, h2, h3, bullets, numbered, numRefs: () => numRefs, table, gap, caption, tcap, fig };
