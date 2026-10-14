/*
 * VShark — PowerPoint version of the company presentation.
 * Run through  python collateral/build_collateral.py  (it pipes the deck content in as JSON):
 *   node collateral/build_pptx.js out.pptx  < deck.json
 * Needs pptxgenjs (npm install pptxgenjs, or NODE_PATH pointing at a node_modules that has it).
 * Native, editable slides: brand theme colours, slide layouts with title placeholders, sections
 * and speaker notes. Fonts are Century Gothic (headings) and Calibri (body) — both ship with Office.
 */
let pptxgen;
try { pptxgen = require('pptxgenjs'); } catch (e) { console.error('pptxgenjs not found'); process.exit(3); }
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2];
const D = JSON.parse(fs.readFileSync(0, 'utf8'));
const HERE = __dirname;

const THEME = {
  name: 'VShark',
  headFontFace: 'Century Gothic',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '1C2125', lt1: 'FFFFFF', dk2: '15191C', lt2: 'F5F6F8',
    accent1: '991B2E', accent2: '828B94', accent3: '616B6F', accent4: 'E0566B', accent5: 'ECEEF1', accent6: '3D454A',
    hlink: '991B2E', folHlink: '616B6F',
  },
};
const MONO = 'Consolas';
const LINE_HEX = 'DADDE1';   // hex-only options (table borders) — matches lt2/accent5 family

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                 // 13.333 × 7.5 in — same as the 1280 × 720 HTML slides
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = 'VShark Solutions';
pres.company = 'VShark Solutions Private Limited';
pres.title = 'VShark Solutions — Company Presentation';
const C = pres.SchemeColor;
const INK = C.text2, BG = C.background2, WHITE = C.background1, FG = C.text1,
      BRAND = C.accent1, STEEL = C.accent2, MUTED = C.accent3, BRAND_LT = C.accent4, FG2 = C.accent6;

const W = 13.333, M = 0.667, CW = W - 2 * M;
const file = p => path.join(HERE, p);
const LOGO_AR = (() => { const [w, h] = D.dims[D.logo]; return w / h; })();

// ---------------------------------------------------------------- helpers
// Image cropped (cover) or fitted (contain) to a box, keeping its proportions.
function pic(slide, p, x, y, w, h, type = 'cover', name) {
  const [iw, ih] = D.dims[p];
  const s = type === 'cover' ? Math.max(w / iw, h / ih) : Math.min(w / iw, h / ih);
  const o = { path: file(p), x, y, w: iw * s, h: ih * s, sizing: { type, w, h }, objectName: name || path.basename(p) };
  if (type === 'contain') { o.x = x + (w - iw * s) / 2; o.y = y + (h - ih * s) / 2; delete o.sizing; }
  slide.addImage(o);
}
function txt(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, margin: 0, valign: 'top', color: FG, fontSize: 12 }, o));
}
function mono(slide, text, o) {
  txt(slide, String(text).toUpperCase(), Object.assign({ fontFace: MONO, fontSize: 10, charSpacing: 1, color: MUTED }, o));
}
function box(slide, x, y, w, h, o = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ x, y, w, h, rectRadius: 0.08,
    fill: { color: WHITE }, line: { color: C.accent5, width: 0.75 } }, o));
}
function tag(slide, text, x, y, fill) {          // small label chip laid over an image
  const w = 0.2 + text.length * 0.075;
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h: 0.26, fill: { color: fill || INK, transparency: fill ? 0 : 15 }, line: { type: 'none' } });
  mono(slide, text, { x, y, w, h: 0.26, color: WHITE, fontSize: 9, align: 'center', valign: 'middle' });
}
function chips(slide, items, x, y, maxW, o = {}) { // pill row that wraps; returns the y below it
  let cx = x, cy = y; const h = 0.3, gap = 0.08;
  for (const t of items) {
    const w = 0.28 + t.length * 0.072;
    if (cx + w > x + maxW) { cx = x; cy += h + gap; }
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cy, w, h, rectRadius: 0.15,
      fill: o.outline ? { color: BG } : { color: WHITE }, line: { color: o.outline ? STEEL : C.accent5, width: 0.75 } });
    txt(slide, t, { x: cx, y: cy, w, h, fontSize: 10, color: o.outline ? MUTED : FG2, align: 'center', valign: 'middle' });
    cx += w + gap;
  }
  return cy + h;
}
const two = (a, b) => [{ text: a, options: {} }, { text: b, options: { color: BRAND } }];   // "Title <accent>"

// ---------------------------------------------------------------- layouts
const footer = (logo, color) => [
  { image: { path: file(logo), x: M, y: 6.98, h: 0.19, w: 0.19 * LOGO_AR } },
  { text: { text: D.site.toUpperCase(), options: { x: 4.67, y: 6.98, w: 4, h: 0.2, fontFace: MONO, fontSize: 9, charSpacing: 1, color, align: 'center', margin: 0 } } },
];
pres.defineSlideMaster({
  title: 'VShark Content',
  background: { color: BG },
  objects: [
    ...footer(D.logo, STEEL),
    { placeholder: { options: { name: 'kicker', type: 'body', x: M, y: 0.6, w: 8, h: 0.3, fontFace: MONO, fontSize: 10, color: BRAND, margin: 0, valign: 'top' }, text: '' } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.9, w: 8.2, h: 0.8, fontFace: THEME.headFontFace, fontSize: 32, color: FG, margin: 0, valign: 'top', align: 'left' }, text: '' } },
  ],
  slideNumber: { x: 12.17, y: 6.98, w: 0.5, h: 0.2, fontFace: MONO, fontSize: 9, color: STEEL, align: 'right' },
});
pres.defineSlideMaster({
  title: 'VShark Service',
  background: { color: BG },
  objects: [
    ...footer(D.logo, STEEL),
    { placeholder: { options: { name: 'kicker', type: 'body', x: 6.35, y: 0.6, w: 6.3, h: 0.3, fontFace: MONO, fontSize: 10, color: BRAND, margin: 0, valign: 'top' }, text: '' } },
    { placeholder: { options: { name: 'title', type: 'title', x: 6.35, y: 0.9, w: 6.3, h: 0.7, fontFace: THEME.headFontFace, fontSize: 32, color: FG, margin: 0, valign: 'top', align: 'left' }, text: '' } },
  ],
  slideNumber: { x: 12.17, y: 6.98, w: 0.5, h: 0.2, fontFace: MONO, fontSize: 9, color: STEEL, align: 'right' },
});
pres.defineSlideMaster({
  title: 'VShark Dark',
  background: { color: INK },
  objects: [
    { image: { path: file(D.logoWhite), x: M, y: 0.75, h: 0.46, w: 0.46 * LOGO_AR } },
    { placeholder: { options: { name: 'kicker', type: 'body', x: M, y: 1.75, w: 6, h: 0.3, fontFace: MONO, fontSize: 10, color: BRAND_LT, margin: 0, valign: 'top' }, text: '' } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 2.1, w: 6.5, h: 1.5, fontFace: THEME.headFontFace, fontSize: 40, color: WHITE, margin: 0, valign: 'top', align: 'left' }, text: '' } },
  ],
  slideNumber: { x: 12.17, y: 6.98, w: 0.5, h: 0.2, fontFace: MONO, fontSize: 9, color: STEEL, align: 'right' },
});

function slide(master, section, kicker, title, notes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(kicker.toUpperCase(), { placeholder: 'kicker' });
  s.addText(title, { placeholder: 'title' });
  if (notes) s.addNotes(notes);
  return s;
}
const CONTENT = 'VShark Content', SERVICE = 'VShark Service', DARK = 'VShark Dark';
const lead = (s, text, o = {}) => txt(s, text, Object.assign({ x: 8.9, y: 0.95, w: 3.77, h: 0.8, fontSize: 12, color: FG2 }, o));

// ================================================================ 1 · Cover
pres.addSection({ title: 'Introduction' });
let s = slide(DARK, 'Introduction', '3D scanning & 3D design services',
  [{ text: 'We capture reality.', options: { breakLine: true } }, { text: 'Then we engineer it.', options: { color: BRAND_LT } }],
  'Opening: VShark captures physical parts, products and spaces as digital data, then engineers that data into whatever the customer needs.');
txt(s, 'Precise 3D scanning and innovative 3D design that transform physical parts, products and spaces into digital models — and back into physical prototypes.',
  { x: M, y: 3.95, w: 6.2, h: 0.9, fontSize: 14, color: STEEL });
[['Email', D.contact.email], ...D.contact.phones.map(p => [p.label, p.display])].forEach(([l, v], i) => {
  const x = M + [0, 2.55, 4.3][i];
  mono(s, l, { x, y: 5.85, w: 2.4, h: 0.22, fontSize: 9, color: STEEL });
  txt(s, v, { x, y: 6.1, w: 2.5, h: 0.3, fontSize: 13, color: WHITE, bold: true });
});
pic(s, D.cover.scan, 7.33, 0.75, 5.33, 2.9, 'cover', 'Cover scan');
pic(s, D.cover.cad, 7.33, 3.8, 5.33, 2.9, 'cover', 'Cover CAD');
tag(s, '01 · Scan', 7.48, 0.9); tag(s, '02 · CAD', 7.48, 3.95, BRAND);

// ================================================================ 2 · About
s = slide(CONTENT, 'Introduction', '( 01 ) — Who we are', two('From physical to digital ', 'and back'),
  'Who we are: one partner from the physical object to the finished digital deliverable.');
txt(s, D.about.map((t, i) => ({ text: t, options: { breakLine: i < D.about.length - 1, paraSpaceAfter: 10 } })),
  { x: M, y: 2.2, w: 6.1, h: 3.2, fontSize: 16, color: FG2, lineSpacingMultiple: 1.15 });
D.stats.forEach(([a, u, l], i) => {
  const x = 7.33 + (i % 2) * 2.7, y = 2.0 + Math.floor(i / 2) * 2.05;
  box(s, x, y, 2.6, 1.9, { objectName: 'Stat ' + l });
  txt(s, [{ text: a, options: {} }, { text: /^[a-z]/i.test(u) ? ' ' + u : u, options: { fontSize: 20, color: BRAND } }],
    { x: x + 0.25, y: y + 0.35, w: 2.2, h: 0.75, fontFace: THEME.headFontFace, fontSize: 44, valign: 'bottom' });
  mono(s, l, { x: x + 0.25, y: y + 1.25, w: 2.2, h: 0.45, fontSize: 10 });
});

// ================================================================ 3 · Services overview
pres.addSection({ title: 'Services' });
s = slide(CONTENT, 'Services', '( 02 ) — Services', two('Seven services, ', 'one partner'),
  'Seven services. Customers can use one on its own, or hand VShark the whole job from first scan to final file.');
lead(s, 'Use one service on its own, or hand us the whole job — from first scan to final file.');
const cw = (CW - 3 * 0.2) / 4, ch = 2.35;
D.services.forEach((v, i) => {
  const x = M + (i % 4) * (cw + 0.2), y = 1.95 + Math.floor(i / 4) * (ch + 0.2);
  box(s, x, y, cw, ch, { objectName: 'Service card ' + v.name });
  pic(s, v.image, x, y, cw, 1.05, 'cover', v.name);
  mono(s, String(i + 1).padStart(2, '0'), { x: x + 0.18, y: y + 1.17, w: 1, h: 0.2, fontSize: 9, color: BRAND });
  txt(s, v.name, { x: x + 0.18, y: y + 1.38, w: cw - 0.36, h: 0.3, fontFace: THEME.headFontFace, fontSize: 14, bold: true });
  txt(s, v.tagline, { x: x + 0.18, y: y + 1.7, w: cw - 0.36, h: 0.55, fontSize: 11, color: MUTED });
});
{
  const x = M + 3 * (cw + 0.2), y = 1.95 + ch + 0.2;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: BRAND }, line: { type: 'none' }, objectName: 'End-to-end card' });
  txt(s, 'End-to-end delivery', { x: x + 0.22, y: y + 1.05, w: cw - 0.44, h: 0.4, fontFace: THEME.headFontFace, fontSize: 17, bold: true, color: WHITE });
  txt(s, 'Scan, engineer, inspect, print and render — under one roof, with one point of contact.', { x: x + 0.22, y: y + 1.5, w: cw - 0.44, h: 0.7, fontSize: 11, color: WHITE });
}

// ================================================================ 4 · Process
s = slide(CONTENT, 'Services', '( 03 ) — How we work', two('Four steps — ', 'scan to solution'),
  'The process: capture, process, engineer, deliver.');
D.process.forEach((p, i) => {
  const x = M + i * 3.07, w = 2.8;
  pic(s, p.image, x, 2.0, w, 2.15, 'cover', 'Step ' + p.title);
  txt(s, String(i + 1).padStart(2, '0'), { x, y: 4.4, w: 1.2, h: 0.6, fontFace: THEME.headFontFace, fontSize: 36, color: STEEL });
  txt(s, p.title, { x, y: 5.05, w, h: 0.4, fontFace: THEME.headFontFace, fontSize: 20, bold: true });
  txt(s, p.text, { x, y: 5.5, w, h: 0.8, fontSize: 13, color: FG2 });
});

// ================================================================ 5–11 · Service detail
D.services.forEach((v, i) => {
  s = slide(SERVICE, 'Services', `( 02.${i + 1} ) — Services`, v.name, v.intro);
  pic(s, v.image, M, 0.6, 5.3, 6.15, 'cover', v.name);
  tag(s, `Service ${String(i + 1).padStart(2, '0')} / ${String(D.services.length).padStart(2, '0')}`, M + 0.18, 6.3);
  const x = 6.35, w = 6.3;
  txt(s, v.tagline, { x, y: 1.6, w, h: 0.55, fontFace: THEME.headFontFace, fontSize: 14, color: BRAND });
  txt(s, v.intro, { x, y: 2.25, w, h: 1.1, fontSize: 12, color: FG2, lineSpacingMultiple: 1.1 });
  v.points.forEach(([a, b], k) => {
    const px = x + (k % 2) * 3.2, py = 3.45 + Math.floor(k / 2) * 0.93;
    txt(s, a, { x: px, y: py, w: 3.05, h: 0.28, fontFace: THEME.headFontFace, fontSize: 12.5, bold: true });
    txt(s, b, { x: px, y: py + 0.3, w: 3.05, h: 0.6, fontSize: 10.5, color: MUTED });
  });
  mono(s, 'Deliverables', { x, y: 5.35, w: 3, h: 0.2, fontSize: 9 });
  let y = chips(s, v.deliverables, x, 5.6, w);
  mono(s, 'Industries', { x, y: y + 0.12, w: 3, h: 0.2, fontSize: 9 });
  chips(s, v.industries, x, y + 0.37, w, { outline: true });
});

// ================================================================ 12 · Portfolio — scan to CAD
pres.addSection({ title: 'Portfolio' });
s = slide(CONTENT, 'Portfolio', '( 04 ) — Portfolio', two('Scan in. ', 'CAD out.'),
  'Real parts VShark has captured and rebuilt as editable, manufacturable CAD.');
lead(s, 'Real parts we have captured and rebuilt as editable, manufacturable CAD.');
D.pairs.forEach((p, i) => {
  const x = M + (i % 2) * 6.1, y = 1.95 + Math.floor(i / 2) * 2.45, iw = 2.9, ih = 1.85;
  pic(s, p.scan, x, y, iw, ih, 'cover', p.title + ' scan');
  pic(s, p.cad, x + iw + 0.1, y, iw, ih, 'cover', p.title + ' CAD');
  tag(s, 'Scan', x + 0.1, y + 0.1); tag(s, 'CAD', x + iw + 0.2, y + 0.1, BRAND);
  txt(s, [{ text: p.title + '  ', options: { bold: true, color: FG, fontFace: THEME.headFontFace } }, { text: p.summary, options: { color: MUTED } }],
    { x, y: y + ih + 0.08, w: 2 * iw + 0.1, h: 0.4, fontSize: 11 });
});

// ================================================================ 13 · Portfolio — visualisation
s = slide(CONTENT, 'Portfolio', '( 04 ) — Portfolio', two('Design & ', 'visualisation'),
  'Surfacing, sculpting and photoreal rendering — visuals that sell a product before it is made.');
lead(s, 'Surfacing, sculpting and photoreal rendering — visuals that sell a product before it is made.');
D.visuals.forEach((v, i) => {
  const big = i === 0;
  const x = big ? M : M + 6.1 + ((i - 1) % 2) * 3.0, y = big ? 1.95 : 1.95 + Math.floor((i - 1) / 2) * 2.4;
  const w = big ? 5.95 : 2.9, h = big ? 4.75 : 2.35;
  pic(s, v.image, x, y, w, h, 'cover', v.caption);
  s.addShape(pres.shapes.RECTANGLE, { x, y: y + h - 0.75, w, h: 0.75, fill: { color: INK, transparency: 20 }, line: { type: 'none' } });
  txt(s, v.caption, { x: x + 0.15, y: y + h - 0.68, w: w - 0.3, h: 0.25, fontFace: THEME.headFontFace, fontSize: 12, bold: true, color: WHITE });
  txt(s, v.summary, { x: x + 0.15, y: y + h - 0.42, w: w - 0.3, h: 0.36, fontSize: 9.5, color: C.accent5 });
});

// ================================================================ 14 · Industries
pres.addSection({ title: 'Industries & products' });
s = slide(CONTENT, 'Industries & products', '( 05 ) — Industries', two('Industries ', 'we serve'),
  'Six sectors, one standard of precision.');
lead(s, 'Six sectors, one standard of precision.', { y: 1.3, h: 0.3, align: 'right' });
const iw6 = (CW - 5 * 0.15) / 6;
D.industries.forEach((d, i) => {
  const x = M + i * (iw6 + 0.15), y = 1.95, h = 4.75;
  pic(s, d.image, x, y, iw6, h, 'cover', d.name);
  s.addShape(pres.shapes.RECTANGLE, { x, y: y + h - 1.75, w: iw6, h: 1.75, fill: { color: INK, transparency: 12 }, line: { type: 'none' } });
  mono(s, String(i + 1).padStart(2, '0'), { x: x + 0.15, y: y + h - 1.62, w: 1, h: 0.2, fontSize: 9, color: BRAND_LT });
  txt(s, d.name, { x: x + 0.15, y: y + h - 1.4, w: iw6 - 0.3, h: 0.3, fontFace: THEME.headFontFace, fontSize: 14, bold: true, color: WHITE });
  txt(s, d.line, { x: x + 0.15, y: y + h - 1.05, w: iw6 - 0.3, h: 0.95, fontSize: 10.5, color: C.accent5 });
});

// ================================================================ 15 · Products
s = slide(CONTENT, 'Industries & products', '( 06 ) — Products', two('Professional ', '3D scanners'),
  'Vertex blue-laser and optical-tracking scanners, now available from VShark with set-up and support. Full spec sheet in the scanners brochure.');
lead(s, 'Vertex blue-laser and optical-tracking scanners — sold, set up and supported by VShark.');
D.products.forEach((p, i) => {
  const x = M + i * 4.07, y = 1.95, w = 3.87;
  box(s, x, y, w, 1.55, { objectName: 'Product ' + p.name });
  pic(s, p.image, x + 0.15, y + 0.12, 1.3, 1.3, 'contain', p.name);
  txt(s, p.name, { x: x + 1.6, y: y + 0.2, w: 2.15, h: 0.3, fontFace: THEME.headFontFace, fontSize: 15, bold: true });
  txt(s, p.type, { x: x + 1.6, y: y + 0.52, w: 2.15, h: 0.4, fontSize: 10, color: MUTED });
  txt(s, [{ text: p.figure, options: {} }, { text: ' ' + p.unit, options: { fontSize: 10, color: MUTED, fontFace: THEME.bodyFontFace } }],
    { x: x + 1.6, y: y + 0.95, w: 2.15, h: 0.4, fontFace: THEME.headFontFace, fontSize: 20 });
});
{
  const hdr = o => Object.assign({ fontFace: MONO, fontSize: 9, color: MUTED }, o);
  const rows = [[{ text: 'SPECIFICATION', options: hdr() }, ...D.products.map(p => ({ text: p.name.toUpperCase(), options: hdr() }))],
    ...D.specs.map(r => [{ text: r[0], options: { bold: true, color: FG } }, ...r.slice(1).map(c => ({ text: c, options: { color: FG2 } }))])];
  s.addTable(rows, { x: M, y: 3.7, w: CW, colW: [3.0, 3.0, 3.0, 3.0], fontSize: 10.5, fontFace: THEME.bodyFontFace, rowH: 0.3, valign: 'middle',
    border: { type: 'solid', pt: 0.5, color: LINE_HEX }, margin: [0, 0.08, 0, 0.08], objectName: 'Specifications' });
  txt(s, [{ text: 'RECOMMENDED PC   ', options: { fontFace: MONO, fontSize: 9, color: BRAND } }, { text: D.pc, options: {} }],
    { x: M, y: 6.25, w: CW, h: 0.4, fontSize: 10, color: MUTED });
}

// ================================================================ 16 · Testimonials
pres.addSection({ title: 'Clients & contact' });
s = slide(CONTENT, 'Clients & contact', '( 07 ) — What clients say', two('Trusted ', 'worldwide'),
  'Clients in ' + D.countries + '.');
mono(s, D.countries, { x: 6.9, y: 1.3, w: 5.77, h: 0.3, fontSize: 11, align: 'right' });
D.quotes.forEach((q, i) => {
  const x = M + (i % 3) * 4.07, y = 1.95 + Math.floor(i / 3) * 2.45, w = 3.87, h = 2.3;
  box(s, x, y, w, h, { objectName: 'Quote ' + q.name });
  txt(s, '“', { x: x + 0.22, y: y + 0.12, w: 0.5, h: 0.45, fontFace: THEME.headFontFace, fontSize: 36, color: BRAND });
  txt(s, q.text, { x: x + 0.22, y: y + 0.5, w: w - 0.44, h: 1.2, fontSize: 11.5, color: FG2 });
  txt(s, q.name, { x: x + 0.22, y: y + 1.75, w: w - 0.44, h: 0.25, fontFace: THEME.headFontFace, fontSize: 12, bold: true });
  mono(s, q.place, { x: x + 0.22, y: y + 2.0, w: w - 0.44, h: 0.2, fontSize: 9 });
});

// ================================================================ 17 · Contact
s = slide(DARK, 'Clients & contact', '( 08 ) — Get in touch',
  [{ text: 'Let’s start', options: { breakLine: true } }, { text: 'your project.', options: { color: BRAND_LT } }],
  'Close: ask for a photo, drawing or the part itself, and offer to come back with approach, timeline and quote.');
txt(s, 'Send us a photo, drawing or the part itself — we’ll come back with the right approach, timeline and quote.',
  { x: M, y: 3.95, w: 6.0, h: 0.8, fontSize: 14, color: STEEL });
const wa = D.contact.whatsapp;
const rows = [['Email', D.contact.email, 'mailto:' + D.contact.email],
  ...D.contact.phones.map(p => [p.label, p.display, 'tel:' + p.tel]),
  ['WhatsApp', `+${wa.slice(0, 2)} ${wa.slice(2, 7)} ${wa.slice(7)}`, 'https://wa.me/' + wa],
  ['Web', D.site, 'https://' + D.site]];
rows.forEach(([l, v, href], i) => {
  const y = 2.0 + i * 0.68;
  s.addShape(pres.shapes.LINE, { x: 7.33, y, w: 5.33, h: 0, line: { color: C.accent6, width: 0.75 } });
  mono(s, l, { x: 7.33, y: y + 0.24, w: 1.4, h: 0.22, fontSize: 9, color: STEEL });
  txt(s, [{ text: v, options: { hyperlink: { url: href }, color: WHITE } }], { x: 8.73, y: y + 0.17, w: 3.9, h: 0.35, fontSize: 17 });
});
s.addShape(pres.shapes.LINE, { x: 7.33, y: 2.0 + rows.length * 0.68, w: 5.33, h: 0, line: { color: C.accent6, width: 0.75 } });

// ---------------------------------------------------------------- write, then put the brand colours into the theme
(async () => {
  await pres.writeFile({ fileName: OUT });
  const JSZip = require(require.resolve('jszip', { paths: [require.resolve('pptxgenjs')] }));
  const zip = await JSZip.loadAsync(fs.readFileSync(OUT));
  const tp = 'ppt/theme/theme1.xml';
  let xml = await zip.file(tp).async('string');
  const slot = k => `<a:${k}><a:srgbClr val="${THEME.colors[k]}"/></a:${k}>`;
  const scheme = `<a:clrScheme name="${THEME.name}">` +
    ['dk1', 'lt1', 'dk2', 'lt2', 'accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6', 'hlink', 'folHlink'].map(slot).join('') + '</a:clrScheme>';
  xml = xml.replace(/<a:clrScheme [^>]*>[\s\S]*?<\/a:clrScheme>/, scheme).replace(/(<a:theme [^>]*name=")[^"]*"/, `$1${THEME.name}"`);
  zip.file(tp, xml);
  for (const f of Object.keys(zip.files).filter(f => /^ppt\/(slides|slideLayouts|slideMasters)\/[^/]+\.xml$/.test(f))) {
    const bad = (await zip.file(f).async('string')).match(/srgbClr val="(?![0-9A-Fa-f]{6}")[^"]*"/);
    if (bad) throw new Error(`${f}: scheme colour in a hex-only option (${bad[0]})`);
  }
  fs.writeFileSync(OUT, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
})().catch(e => { console.error(e.stack || e); process.exit(1); });
