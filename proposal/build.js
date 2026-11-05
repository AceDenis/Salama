const fs = require("fs");
const { D, FONT, numRefs } = require("./lib");
const { Document, Packer, Paragraph, TextRun, AlignmentType, Footer, Header, PageNumber, TableOfContents, LevelFormat, HeadingLevel } = D;
const body = [...require("./c1")(), ...require("./c2")(), ...require("./c3")(), ...require("./c4")(), ...require("./c5")(), ...require("./cend")()];
const C = (t, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: o.after || 200 }, children: [new TextRun({ text: t, font: FONT, size: o.size || 26, bold: o.bold })] });
const title = [
  C("", { after: 1200 }),
  C("NATIONAL DEFENCE UNIVERSITY–KENYA", { bold: true, size: 28 }),
  C("DEFENCE COLLEGE OF HEALTH SCIENCES", { bold: true, size: 28, after: 600 }),
  C("RESEARCH PROPOSAL", { bold: true, size: 32, after: 400 }),
  C("SALAMA CHECK-IN: AN ADAPTIVE, CONFIDENTIAL DIGITAL MENTAL HEALTH SERVICE WITH NURSE CALL-BACK AND EARLY WARNING FOR THE KENYA DEFENCE FORCES COMMUNITY AND THE DEFENCE COLLEGE OF HEALTH SCIENCES: CO-DESIGN, THREE-MONTH PILOT AND COSTED ADOPTION PLAN", { bold: true, size: 28, after: 700 }),
  C("Submitted by: WEDAH", { size: 26 }),
  C("Registration number: [to be added]", { size: 24 }),
  C("BSc Nursing with Military Health", { size: 24 }),
  C("Supervisor: [to be added]", { size: 24, after: 500 }),
  C("A proposal submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Nursing with Military Health", { size: 22, after: 400 }),
  C("October 2026", { size: 24 }),
  new Paragraph({ children: [new D.PageBreak()] }),
  new Paragraph({ children: [new TextRun({ text: "TABLE OF CONTENTS", bold: true, font: FONT, size: 28 })], alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
  new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-3" }),
];
const num = numRefs().map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }));
const doc = new Document({
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, font: FONT, color: "0F3D3A" }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: FONT, color: "0F6B63" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, italics: true, font: FONT, color: "333333" }, paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2, keepNext: true } },
    ] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }, { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }] }, ...num] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Salama Check-In · Research proposal · WEDAH", font: FONT, size: 18, color: "666666" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children: [...title, ...body],
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("../Research_Proposal_Salama_CheckIn.docx", b); console.log("built"); });
