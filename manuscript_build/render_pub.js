// Renders content_pub.json in the AJSE camera-ready layout (A4, 0.75" margins, two columns).
// node render_pub.js clean|tracked OUT.docx
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType, SectionType,
        BorderStyle, ShadingType, ExternalHyperlink, UnderlineType, LineRuleType, TabStopType, HighlightColor, VerticalAlign, InsertedTextRun, DeletedTextRun } = require("docx");
const C = JSON.parse(fs.readFileSync(require("path").join(__dirname, "output", "content_pub.json"), "utf8"));
const MODE = process.argv[2] || "clean", OUT = process.argv[3];
const TR = MODE === "tracked";
// Page geometry and type sizes follow the AJSE template (AJSE_Template_2020-OTH): US Letter, margins 0.65 in (left/right) and
// 0.70 in (top/bottom), two columns 0.2 in apart (3.5 in each); Text 10 pt (line 1.05, first-line indent 0.14 in); title 24 pt;
// authors 11 pt; abstract and index terms 9 pt bold; headings 10 pt (level 1 small caps, centred; level 2 italic, lettered A., B.);
// table titles 8 pt small caps above the table; figure captions 8 pt below; references 8 pt; biographies 8 pt, photo 1 x 1.25 in.
const FONT = "Times New Roman", PW = 12240, PH = 15840, MLR = 936, MTB = 1008, GAP = 288, FULL = PW - 2 * MLR, COL = Math.floor((FULL - GAP) / 2);
const BODY = 20, LINE = 252, FIGCOL = 3.45, FIGWIDE = 7.0;
const AUTHOR = "Authors (correction)", DATE = "2026-11-04T00:00:00Z"; let RID = 1;

function runs(text, base = {}, kind = "=") {
  const out = []; let i = 0, buf = "", st = { b: false, i: false };
  const mk = (t, extra = {}) => {
    if (!t) return;
    const o = { text: t, font: FONT, bold: st.b || base.bold, italics: st.i || base.italics, smallCaps: base.smallCaps, size: base.size || BODY, ...extra };
    if (kind === "+") out.push(new InsertedTextRun({ ...o, id: RID++, author: AUTHOR, date: DATE }));
    else if (kind === "-") out.push(new DeletedTextRun({ ...o, id: RID++, author: AUTHOR, date: DATE }));
    else out.push(new TextRun(o));
  };
  while (i < text.length) {
    if (text.startsWith("**", i)) { mk(buf); buf = ""; st.b = !st.b; i += 2; continue; }
    if ((text.startsWith("_{", i) || text.startsWith("^{", i)) && text.indexOf("}", i) > 0) {
      const j = text.indexOf("}", i); mk(buf); buf = ""; mk(text.slice(i + 2, j), text[i] === "_" ? { subScript: true } : { superScript: true }); i = j + 1; continue; }
    if (text[i] === "⟦" && text.indexOf("⟧", i) > 0) { const j = text.indexOf("⟧", i); mk(buf); buf = ""; mk(text.slice(i, j + 1), { highlight: HighlightColor.YELLOW, bold: true }); i = j + 1; continue; }
    buf += text[i]; i++;
  }
  mk(buf); return out;
}
// clean text or tracked segments
function body(b, base) {
  if (TR && b.segs) return b.segs.flatMap(([k, t]) => runs(t, base, k));
  return runs(b.text !== undefined ? b.text : b.cap, base);
}
// line spacing is proportional (lineRule auto): 240 = single, 252 = 1.05 (template Text style)
const SP = (s) => (s && s.line ? { ...s, lineRule: LineRuleType.AUTO } : s);
const P = (children, o = {}) => new Paragraph({ children, alignment: o.align || AlignmentType.JUSTIFIED, indent: o.indent, spacing: SP(o.spacing || { after: 0, line: LINE }), keepNext: o.keepNext, tabStops: o.tabStops });
const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" }, none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function table(tb, width) {
  const sum = tb.w.reduce((a, b) => a + b, 0); const w = tb.w.map(x => Math.floor(x * width / sum)); w[w.length - 1] += width - w.reduce((a, b) => a + b, 0);
  const sz = 16;                                   // template: table text 8 pt
  const cell = (txt, j, head, last, section, keep) => new TableCell({ width: { size: w[j], type: WidthType.DXA }, margins: { top: 20, bottom: 20, left: 50, right: 50 }, verticalAlign: VerticalAlign.CENTER,
    shading: section ? { type: ShadingType.CLEAR, fill: "EEEEEE", color: "auto" } : undefined,
    borders: { top: head ? border : none, bottom: (head || last) ? border : none, left: none, right: none },
    children: [new Paragraph({ keepNext: head || keep, alignment: (j === 0 || (j === 1 && tb.head.length === 4 && tb.head[1].startsWith("Definition"))) ? AlignmentType.LEFT : AlignmentType.CENTER, children: runs(String(txt), { size: sz, bold: head || section }) })] });
  const rows = [new TableRow({ tableHeader: true, children: tb.head.map((h, j) => cell(h, j, true, false)) })];
  tb.rows.forEach((r, k) => { const section = r.slice(1).every(x => x === "") && /LAYER/.test(r[0]); rows.push(new TableRow({ cantSplit: true, children: r.map((c, j) => cell(c, j, false, k === tb.rows.length - 1, section, k < tb.rows.length - 1)) })); });
  const capB = { ...tb }; capB.text = undefined;
  const out = [...tableTitle(tb),
               new Table({ width: { size: width, type: WidthType.DXA }, columnWidths: w, rows })];
  out.push(P(tb.note ? runs(tb.note, { size: 16 }) : [], { spacing: { before: 30, after: 120, line: 220 } }));
  return out;
}
// "TABLE I" on its own line, then the title in small caps (template "Table Title" style, 8 pt, centred, above the table)
function tableTitle(tb) {
  const m = /^(TABLE [IVX]+)\.\s*/.exec(tb.cap); const opt = { align: AlignmentType.CENTER, keepNext: true };
  if (!m || (TR && tb.segs && tb.segs.some(([k]) => k !== "="))) {          // tracked and changed: keep the diff runs in one line
    return [P(body({ ...tb, text: tb.cap, segs: tb.segs }, { size: 16, smallCaps: true }), { ...opt, spacing: { before: 160, after: 60 } })]; }
  return [P(runs(m[1], { size: 16 }), { ...opt, spacing: { before: 160, after: 0 } }),
          P(runs(tb.cap.slice(m[0].length).replace(/\.$/, ""), { size: 16, smallCaps: true }), { ...opt, spacing: { after: 60 } })];
}
function figure(f, widthIn) {
  const buf = fs.readFileSync(f.path); const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20); const px = Math.round(widthIn * 96);
  return [P([new ImageRun({ type: "png", data: buf, transformation: { width: px, height: Math.round(px * h / w) } })], { align: AlignmentType.CENTER, spacing: { before: 100, after: 40 }, keepNext: true }),
          P(body({ cap: f.cap, segs: f.segs }, { size: 16 }), { spacing: { after: 160, line: 220 } })];
}
const page = { size: { width: PW, height: PH }, margin: { top: MTB, bottom: MTB, left: MLR, right: MLR, header: 432, footer: 0 } };
const two = { type: SectionType.CONTINUOUS, column: { count: 2, space: GAP, equalWidth: true } }, one = { type: SectionType.CONTINUOUS, column: { count: 1 } };
const sections = []; let cur = [];
const flush = (props) => { if (cur.length) { sections.push({ properties: { ...props, page }, children: cur }); cur = []; } };
const m = C.meta;
cur.push(P(runs(m.title, { size: 48 }), { align: AlignmentType.CENTER, spacing: { after: 200, line: 240 } }));
cur.push(P(runs(m.authors, { size: 22 }), { align: AlignmentType.CENTER, spacing: { after: 320, line: 240 } }));
cur.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 120 }, shading: { type: ShadingType.CLEAR, fill: "EEF2F8", color: "auto" },
  border: { top: border, bottom: border, left: border, right: border }, children: runs((TR ? "TRACKED-CHANGES VERSION against the published article (AJSE 25(2):231–243). " : "") + m.notice, { size: 16, italics: true }) }));
const absRuns = TR ? C.abstract_segs.flatMap(([k, t]) => runs(t, { size: 18, bold: true }, k)) : runs(m.abstract, { size: 18, bold: true });
cur.push(P([...runs("Abstract—", { size: 18, bold: true, italics: true }), ...absRuns], { indent: { firstLine: 202 }, spacing: { before: 20, after: 120, line: 240 } }));
cur.push(P([...runs("Index Terms—", { size: 18, bold: true, italics: true }), ...runs(m.index, { size: 18, bold: true })], { indent: { firstLine: 202 }, spacing: { after: 160, line: 240 } }));
m.affil.forEach(a => cur.push(P(runs(a, { size: 16 }), { indent: { firstLine: 202 }, spacing: { after: 0, line: 220 } })));   // template first-page footnote text: 8 pt
cur.push(P([], { spacing: { after: 120 } }));
flush({ column: { count: 1 } });
let H2N = 0;
for (const b of C.blocks) {
  if (b.t === "del") { if (TR && b.segs.length) cur.push(P(b.segs.flatMap(([k, t]) => runs(t, { size: BODY }, k)))); continue; }
  if (b.t === "h1") { H2N = 0; cur.push(P(body(b, { size: BODY, smallCaps: true }), { align: AlignmentType.CENTER, spacing: { before: 240, after: 80, line: 240 }, keepNext: true })); }
  else if (b.t === "h2") cur.push(P([new TextRun({ text: `${"ABCDEFGHIJKLMNOP"[H2N++]}. `, font: FONT, size: BODY, italics: true }), ...body(b, { size: BODY, italics: true })],
      { align: AlignmentType.LEFT, spacing: { before: 120, after: 60, line: 240 }, keepNext: true }));
  else if (b.t === "p") cur.push(P(body(b, { size: BODY }), { indent: b.noindent ? undefined : { firstLine: 202 } }));
  else if (b.t === "url") { const o = { text: b.text, font: FONT, size: 16, color: "0563C1", underline: { type: UnderlineType.SINGLE } };
    const r = TR ? new InsertedTextRun({ ...o, id: RID++, author: AUTHOR, date: DATE }) : new TextRun(o);
    cur.push(P([new ExternalHyperlink({ link: b.text, children: [r] })], { align: AlignmentType.CENTER, spacing: { before: 20, after: 40, line: 228 } })); }
  else if (b.t === "eq") cur.push(P([new TextRun({ text: "\t", font: FONT }), ...body(b, { size: BODY }), new TextRun({ text: `\t(${b.num})`, font: FONT, size: BODY })],
      { tabStops: [{ type: TabStopType.CENTER, position: Math.floor(COL / 2) }, { type: TabStopType.RIGHT, position: COL - 20 }], spacing: { before: 60, after: 60 } }));
  else if (b.t === "fig") { if (b.wide) { flush(two); cur.push(...figure(b, FIGWIDE)); flush(one); } else cur.push(...figure(b, FIGCOL)); }
  else if (b.t === "tab") { if (b.wide) { flush(two); cur.push(...table(b, FULL)); flush(one); } else cur.push(...table(b, COL)); }
}
cur.push(P(runs("References", { size: BODY, smallCaps: true }), { align: AlignmentType.CENTER, spacing: { before: 240, after: 80, line: 240 }, keepNext: true }));   // template "Reference Head"
C.refs.forEach((r, k) => {
  const rr = TR ? C.ref_segs[k].flatMap(([kk, t]) => runs(t, { size: 16 }, kk)) : runs(r, { size: 16 });
  cur.push(P([new TextRun({ text: `[${k + 1}]\t`, font: FONT, size: 16 }), ...rr], { indent: { left: 400, hanging: 400 }, spacing: { after: 0, line: 220 }, tabStops: [{ type: TabStopType.LEFT, position: 400 }] }));
});
cur.push(P(runs("Author Biographies", { size: BODY, smallCaps: true }), { align: AlignmentType.CENTER, spacing: { before: 240, after: 80, line: 240 }, keepNext: true }));
C.bios.forEach((bio, k) => {
  const img = fs.readFileSync(C.photos[k]); const isPng = C.photos[k].endsWith(".png");
  const PH_W = 1600;                                   // photo cell: 1.0 x 1.25 in photo (template) + 0.11 in gap
  cur.push(new Table({ width: { size: COL, type: WidthType.DXA }, columnWidths: [PH_W, COL - PH_W], rows: [new TableRow({ cantSplit: true, children: [
    new TableCell({ width: { size: PH_W, type: WidthType.DXA }, borders: { top: none, bottom: none, left: none, right: none },
      children: [new Paragraph({ children: [new ImageRun({ type: isPng ? "png" : "jpg", data: img, transformation: { width: 96, height: 120 } })] })] }),
    new TableCell({ width: { size: COL - PH_W, type: WidthType.DXA }, borders: { top: none, bottom: none, left: none, right: none },
      children: [P(runs(bio, { size: 16 }), { spacing: { after: 0, line: 220 } })] })] })] }));
  cur.push(P([], { spacing: { after: 80 } }));
});
flush(two);
const doc = new Document({ creator: "Authors", title: m.title, styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  features: { trackRevisions: TR }, sections });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log("wrote", OUT, sections.length, "sections"); });
