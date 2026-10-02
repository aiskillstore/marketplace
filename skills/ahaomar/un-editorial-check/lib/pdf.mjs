// Minimal, dependency-free PDF 1.4 writer for the report generator.
//
// renderPdf(elements, opts) lays the report model's element union out on A4
// portrait pages, stamps a footer on every page once layout has produced the
// page count (two passes), and returns the whole file as a Buffer. Content
// streams stay uncompressed so the structural test can read the text operands
// back with a regular expression; the embedded font streams are compressed,
// as the spec requires, and are told apart from page content by their filter.
// The module reads no clock and no environment: the two font files it embeds
// are addressed relative to this module, and every other input arrives as an
// argument, so the same input always yields the same bytes.
//
// Everything reader-visible goes through transliteration first: curly quotes
// and the ellipsis fold to ASCII, the soft hyphen is dropped, the WinAnsi
// specials — including the en dash (0x96) and the em dash (0x97) — keep their
// single-byte positions (a dash that folded to "-" made UE-NU002's Current and
// Should be print identically), and any remaining code point outside the
// encoding becomes "?".
//
// On that last fold, precisely, because it is a real limitation and the
// report must not hide it. WinAnsi is a single-byte encoding: a Cyrillic,
// Arabic or Han character has no code in it, and neither does the subset of
// the embedded faces the writer carries, which keeps only the glyphs those
// 218 reachable bytes name. A transliteration fold is not offered in its
// place because a wrong transliteration of an unfamiliar script is worse
// than an honest placeholder: the reader could not tell it from the real name.
// So the character is replaced by "?", and the loss is announced rather than
// silent: when any string in the report needed that fold, the report carries a
// closing note saying so, naming the encoding and stating that a character
// shown as "?" may be a character the font cannot draw and not a question mark
// in the copy. Two file names that differ only in a non-Latin character will
// therefore still print alike, and that is the documented cost — the JSON
// output, which the same run also produces, carries the exact path.
//
// The soft hyphen is the other dropped character, and unlike "?" it needs no
// note: it is an invisible line-breaking hint that carries no text of its own.
//
// Line breaking uses the advance widths of the two embedded faces themselves,
// read from `hmtx` and normalised to units per 1000 em. An unbroken run that
// is wider than the column is cut at the last character that fits, so no
// emitted line leaves the content box. The faces are Roboto Condensed Regular
// (`F1`) and Bold (`F2`), subset to the WinAnsi bytes and embedded as
// `/FontFile2` under a deterministic subset tag; there is no italic resource,
// because no code path ever draws one (R5).
//
// Since Phase 9 the writer also draws three surfaces shared with lib/html.mjs,
// in both `detail` modes: the thirteen-row category legend (lib/legend.mjs —
// marker code plus the category's own name, so colour and shape are never the
// only signal), and the UN-style document furniture (lib/furniture.mjs) whose
// header reads EDITORIAL REVIEW and never UNITED NATIONS — claim row 22
// promises the report never presents itself as United Nations endorsement.
// The `issue` element (grouped detail) renders as a structured block: banner,
// marker row (a count only when the group holds more than one occurrence),
// the finding's own fields, the six provenance rows, and an `Occurrences`
// list of File / Location / Content / Should be kv blocks that wraps within
// the measure. Summary counts are never derived from `issue.count`: they come
// from the summary paragraph the model computed from the findings.

import { Buffer } from 'node:buffer';
import { readFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';

import { legendRows } from './legend.mjs';
import { categoryIcon, pdfIcon, severityIcon } from './icons.mjs';
import { footerCells, headerRows } from './furniture.mjs';
import { capLines, sectionCount } from './report.mjs';
import { fontDescriptor, subset, winAnsiWidths } from './ttf.mjs';
import { toWinAnsi, winAnsiToUnicode } from './winansi.mjs';
import { PALETTE } from './palette.mjs';

// --- page geometry -----------------------------------------------------------

const PAGE_W = 595.28; // A4 portrait, points
const PAGE_H = 841.89;
const MARGIN = 54;
const CONTENT_W = PAGE_W - 2 * MARGIN;
const TOP = PAGE_H - MARGIN;
const BOTTOM = MARGIN;
const BODY = 10.5;
const BODY_LEAD = 14;
const LABEL_COL = 84;
const BULLET_INDENT = 14;
const FOOTER_SIZE = 7.5;
const FOOTER_Y = 30;
// R6: not `0 0 0`. A very dark navy-tinted near-black reads as black and sits
// in the same hue family as the chrome instead of fighting it — 17.20:1 on
// white, and it warms the page a little where pure black cools it.
const BLACK = PALETTE.body.pdf;
// The metadata beside a section title — its lane and its finding count — is
// set lighter than the title itself so a reader's eye takes the title first.
const META_GREY = PALETTE.meta.pdf;
const WHITE = PALETTE.onChip.pdf;
const FOOTER_GREY = PALETTE.footer.pdf;

// --- embedded faces -----------------------------------------------------------
//
// Both faces ship in `fonts/` and are read once, relative to this module, so
// the same package embeds the same bytes on every machine. Per face: subset to
// the WinAnsi glyphs, then take the descriptor, the width table and the program
// from the *subset*, so all three describe the same bytes — a `/Widths` read
// from the source and a `/FontFile2` holding the subset could disagree the day
// the subsetter changed, with nothing to notice it.
//
// The subset tag is six uppercase letters — three from the family, three from
// the style — derived from the face's own name, so `RobotoCondensed-Regular`
// always becomes `ROBREG+…` and two runs of the same report are byte-identical.
// A name that will not yield six letters throws rather than emitting a tag a
// later run might derive differently.

function subsetTag(baseName) {
  const match = /^([A-Za-z]+)-([A-Za-z]+)$/.exec(baseName);
  if (!match) {
    throw new Error(`pdf: face name "${baseName}" is not <Family>-<Style>; `
      + 'no subset tag can be derived from it');
  }
  const [, family, style] = match;
  if (family.length < 3 || style.length < 3) {
    throw new Error(`pdf: face name "${baseName}" has a part shorter than three letters; `
      + 'the subset tag would not be six letters wide');
  }
  return `${(family.slice(0, 3) + style.slice(0, 3)).toUpperCase()}+`;
}

const hexByte = (byte) => byte.toString(16).toUpperCase().padStart(2, '0');
const hexCodePoint = (cp) => cp.toString(16).toUpperCase().padStart(4, '0');

/**
 * The `/ToUnicode` CMap: one `bfchar` per WinAnsi byte that names a code
 * point, so copy-paste and text extraction return the characters the bytes
 * stand for rather than the bytes themselves. Adobe's five undefined C1
 * positions are skipped — no folded string can hold them — and the blocks are
 * cut at the spec's 100-entry limit.
 *
 * @returns {string}
 */
function toUnicodeCMap() {
  const pairs = [];
  for (let byte = 0x20; byte <= 0xFF; byte++) {
    const codePoint = winAnsiToUnicode(byte);
    if (codePoint === null) continue;
    pairs.push(`<${hexByte(byte)}> <${hexCodePoint(codePoint)}>`);
  }
  const lines = [
    '/CIDInit /ProcSet findresource begin',
    '12 dict begin',
    'begincmap',
    '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def',
    '/CMapName /Adobe-Identity-UCS def',
    '/CMapType 2 def',
    '1 begincodespacerange',
    '<00> <FF>',
    'endcodespacerange',
  ];
  for (let i = 0; i < pairs.length; i += 100) {
    const block = pairs.slice(i, i + 100);
    lines.push(`${block.length} beginbfchar`, ...block, 'endbfchar');
  }
  lines.push('endcmap', 'CMapName currentdict /CMap defineresource pop', 'end', 'end');
  return lines.join('\n');
}

/**
 * One face, ready to be written as four PDF objects: the subset program with
 * its Flate copy and its uncompressed length, the descriptor values scaled
 * from font units to units-per-1000, the byte-indexed width table, and the
 * compressed CMap.
 *
 * @param {string} baseName `<Family>-<Style>`, matching `fonts/<baseName>.ttf`
 * @returns {object}
 */
function loadFace(baseName) {
  const source = readFileSync(new URL(`../fonts/${baseName}.ttf`, import.meta.url));
  const program = subset(source);
  const from = fontDescriptor(program);
  // Glyph space to text space: PDF wants FontBBox, Ascent, Descent and
  // CapHeight per 1000 em, the face states them per 2048. `-0` would print as
  // a negative zero a reader can see, so it is normalised here, once.
  const scale = (value) => {
    const scaled = Math.round((value * 1000) / from.unitsPerEm);
    return Object.is(scaled, -0) ? 0 : scaled;
  };
  const cMap = Buffer.from(toUnicodeCMap(), 'latin1');
  return {
    baseFont: `${subsetTag(baseName)}${baseName}`,
    programLength: program.length,
    programDeflated: deflateSync(program),
    cMapLength: cMap.length,
    cMapDeflated: deflateSync(cMap),
    widths: winAnsiWidths(program),
    descriptor: {
      fontBBox: [scale(from.xMin), scale(from.yMin), scale(from.xMax), scale(from.yMax)],
      ascent: scale(from.ascent),
      descent: scale(from.descent),
      capHeight: scale(from.capHeight),
      italicAngle: from.italicAngle,
      stemV: from.stemV,
    },
  };
}

// F1 Regular, F2 Bold, in that order — every `font === 'F2'` downstream reads
// this array at the same index. There is no F3: no code path draws italic, and
// Roboto Condensed is upright by design.
const FACES = [loadFace('RobotoCondensed-Regular'), loadFace('RobotoCondensed-Bold')];

// --- transliteration ---------------------------------------------------------
// Moved whole to `lib/winansi.mjs`, because the font layer needs the byte-to-
// code-point direction of the same encoding and two copies of this table would
// drift apart with nothing to notice it. `toWinAnsi` is imported for the
// emitter and `winAnsiToUnicode` for the `/ToUnicode` CMap; their behaviour is
// unchanged.

/**
 * The width of `value` in points. The string is folded first — `wrap` passes
 * raw model text — so the index into the width table is always the byte a
 * viewer will read, which is exactly how `winAnsiWidths` is indexed.
 *
 * @param {string} value
 * @param {string} font resource name, `F1` or `F2`
 * @param {number} size
 * @returns {number}
 */
function measure(value, font, size) {
  const widths = (font === 'F2' ? FACES[1] : FACES[0]).widths;
  const folded = toWinAnsi(value);
  let width = 0;
  for (let i = 0; i < folded.length; i++) {
    const advance = widths[folded.charCodeAt(i)];
    // Every code unit of a folded string is a byte, so this cannot read past
    // the table; the guard exists so a future fold that let a wider character
    // through refuses instead of measuring as NaN and stacking every line it
    // touches onto one column edge.
    if (advance === undefined) {
      throw new Error(`pdf: character U+${folded.charCodeAt(i).toString(16).toUpperCase()} `
        + 'survived the WinAnsi fold with no byte to measure');
    }
    width += (advance * size) / 1000;
  }
  return width;
}

// Word wrap against the real advance widths. Whitespace collapses to single
// spaces; a word that cannot fit even alone is cut at the last character
// that fits, so no line leaves the column.

function wrap(value, font, size, maxWidth) {
  const normalized = toWinAnsi(value).replace(/\s+/g, ' ').trim();
  if (!normalized) return [];
  const fits = (piece) => measure(piece, font, size) <= maxWidth;
  const lines = [];
  let current = '';
  for (const word of normalized.split(' ')) {
    let rest = word;
    while (rest !== '' && !fits(rest)) {
      if (current !== '') {
        lines.push(current);
        current = '';
        continue;
      }
      let cut = 1;
      while (cut < rest.length && fits(rest.slice(0, cut + 1))) cut++;
      lines.push(rest.slice(0, cut));
      rest = rest.slice(cut);
    }
    const joined = current === '' ? rest : current + ' ' + rest;
    if (fits(joined)) current = joined;
    else {
      lines.push(current);
      current = rest;
    }
  }
  if (current !== '') lines.push(current);
  return lines;
}

function pdfLiteral(value) {
  const win = toWinAnsi(value);
  let out = '(';
  for (const ch of win) {
    if (ch === '(' || ch === ')' || ch === '\\') out += '\\';
    out += ch;
  }
  return out + ')';
}

function n(value) {
  const rounded = Math.round(value * 100) / 100;
  return String(Object.is(rounded, -0) ? 0 : rounded);
}

function bannerFill(kind) {
  if (kind === 'error') return PALETTE.severity.error.pdf;
  if (kind === 'warning') return PALETTE.severity.warning.pdf;
  // The cover title banner is the masthead colour: one navy, so the cover and
  // every running page head read as the same document.
  if (kind === 'title') return PALETTE.masthead.pdf;
  return PALETTE.severity.note.pdf;
}

/**
 * A legend marker's `#rrggbb` as a PDF fill colour, three decimal places per
 * channel (the precision `n()` would give, applied per channel rather than to
 * the whole triplet). Anything that is not a six-digit hex — an unknown
 * category carries `colour: ''` — falls back to the neutral marker grey, so a
 * missing colour still draws a swatch instead of corrupting the stream. The
 * value is never passed through `n()`: that rounds a single number, and
 * `0.4 0.4 0.4` must not become one number.
 */
function rgbFill(hex) {
  const match = /^#([0-9a-fA-F]{6})$/.exec(String(hex || ''));
  if (!match) return '0.45 0.45 0.45';
  const hex6 = match[1].toLowerCase();
  const channel = (start) =>
    String(Math.round(parseInt(hex6.slice(start, start + 2), 16) / 255 * 1000) / 1000);
  return `${channel(0)} ${channel(2)} ${channel(4)}`;
}

// --- serialization -----------------------------------------------------------

function serialize(pages) {
  const objects = new Map();
  const pageCount = pages.length;
  const kidRefs = [];
  for (let i = 0; i < pageCount; i++) kidRefs.push(`${11 + i * 2} 0 R`);

  objects.set(1, '<< /Type /Catalog /Pages 2 0 R >>');
  objects.set(2, `<< /Type /Pages /Kids [${kidRefs.join(' ')}] /Count ${pageCount} >>`);

  // Objects 3..10 hold the two faces: the font dictionary and its descriptor
  // first, then the two streams. The layout is fixed — 3/4 fonts, 5/6
  // descriptors, 7/8 programs, 9/10 CMaps — so page objects always start at
  // 11 however many pages follow. Every compressed stream carries `/Filter`,
  // which is how a reader tells the four font objects' binary from the page
  // content streams, which stay uncompressed for the structural test.
  FACES.forEach((face, i) => {
    const fontNum = 3 + i;
    const fdNum = 5 + i;
    const ffNum = 7 + i;
    const tuNum = 9 + i;
    // `/Widths` is indexed by the byte a viewer reads: one entry per code
    // from /FirstChar to /LastChar, so 224 entries for bytes 32..255. The
    // five undefined C1 positions and byte 127 measure 0, and no folded
    // string can hold them.
    const widths = [];
    for (let byte = 32; byte <= 255; byte++) widths.push(face.widths[byte]);
    objects.set(fontNum,
      `<< /Type /Font /Subtype /TrueType /BaseFont /${face.baseFont}`
      + ' /Encoding /WinAnsiEncoding /FirstChar 32 /LastChar 255'
      + ` /Widths [${widths.join(' ')}]`
      + ` /FontDescriptor ${fdNum} 0 R /ToUnicode ${tuNum} 0 R >>`);
    const d = face.descriptor;
    objects.set(fdNum,
      `<< /Type /FontDescriptor /FontName /${face.baseFont} /Flags 32`
      + ` /FontBBox [${d.fontBBox.join(' ')}] /ItalicAngle ${n(d.italicAngle)}`
      + ` /Ascent ${d.ascent} /Descent ${d.descent} /CapHeight ${d.capHeight}`
      + ` /StemV ${d.stemV} /FontFile2 ${ffNum} 0 R >>`);
    // `/Length1` is the *uncompressed* program length: it is what a viewer
    // checks the inflated font against, so the two lengths differ by design.
    objects.set(ffNum, Buffer.concat([
      Buffer.from(`<< /Length ${face.programDeflated.length} /Filter /FlateDecode`
        + ` /Length1 ${face.programLength} >>\nstream\n`, 'latin1'),
      face.programDeflated,
      Buffer.from('\nendstream', 'latin1'),
    ]));
    objects.set(tuNum, Buffer.concat([
      Buffer.from(`<< /Length ${face.cMapDeflated.length} /Filter /FlateDecode >>\nstream\n`, 'latin1'),
      face.cMapDeflated,
      Buffer.from('\nendstream', 'latin1'),
    ]));
  });

  for (let i = 0; i < pageCount; i++) {
    const pageNum = 11 + i * 2;
    const contentNum = 12 + i * 2;
    const data = pages[i].join('\n');
    objects.set(pageNum,
      `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89]`
      + ' /Resources << /ProcSet [/PDF /Text] /Font << /F1 3 0 R /F2 4 0 R >> >>'
      + ` /Contents ${contentNum} 0 R >>`);
    objects.set(contentNum,
      `<< /Length ${Buffer.byteLength(data, 'latin1')} >>\nstream\n${data}\nendstream`);
  }

  const maxObject = 10 + pageCount * 2;
  const offsets = [];
  const chunks = [];
  let cursor = 0;
  const put = (chunk) => {
    const buf = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk, 'latin1');
    chunks.push(buf);
    cursor += buf.length;
  };

  put('%PDF-1.4\n');
  for (let num = 1; num <= maxObject; num++) {
    offsets[num] = cursor;
    put(`${num} 0 obj\n`);
    put(objects.get(num));
    put('\nendobj\n');
  }
  const xrefStart = cursor;
  put(`xref\n0 ${maxObject + 1}\n`);
  put('0000000000 65535 f \n');
  for (let num = 1; num <= maxObject; num++) {
    put(`${String(offsets[num]).padStart(10, '0')} 00000 n \n`);
  }
  put(`trailer\n<< /Size ${maxObject + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF\n`);

  return Buffer.concat(chunks);
}

// --- layout ------------------------------------------------------------------

/** Every reader-visible string an element carries. */
function elementStrings(el) {
  if (!el || typeof el !== 'object') return [];
  const out = [];
  // Scalars: the original three plus an issue's own fields (the grouped
  // layout puts the copy and the explanation here instead of on kv and
  // paragraph elements, and the fold must find them or a grouped report
  // would lose its closing note), a legend row's text, and a cap block's
  // re-run command — which is the one string a reader copies out of the
  // report, so it must be warned about rather than silently folded.
  for (const key of ['text', 'label', 'value', 'current', 'should', 'message',
    'audit', 'category', 'intent', 'command']) {
    if (typeof el[key] === 'string') out.push(el[key]);
  }
  if (Array.isArray(el.items)) {
    for (const item of el.items) if (typeof item === 'string') out.push(item);
  }
  // An issue's provenance rows and its occurrence list carry paths and copy
  // the reader sees; a legend row carries the category name, its code and
  // what the category covers.
  if (Array.isArray(el.provenance)) {
    for (const row of el.provenance) {
      if (row && typeof row === 'object') {
        if (typeof row.label === 'string') out.push(row.label);
        if (typeof row.value === 'string') out.push(row.value);
      }
    }
  }
  if (Array.isArray(el.occurrences)) {
    for (const occurrence of el.occurrences) {
      if (occurrence && typeof occurrence === 'object') {
        for (const key of ['file', 'content', 'should']) {
          if (typeof occurrence[key] === 'string') out.push(occurrence[key]);
        }
      }
    }
  }
  if (Array.isArray(el.rows)) {
    for (const row of el.rows) {
      if (row && typeof row === 'object') {
        for (const key of ['category', 'code', 'intent']) {
          if (typeof row[key] === 'string') out.push(row[key]);
        }
      }
    }
  }
  return out;
}

// The "?" fold is never silent. When any string in the report needed it, the
// report says so in a closing note, because a "?" in a file name is otherwise
// indistinguishable from a "?" in the copy. The note is appended to the element
// list rather than drawn by the layout code, so it flows, wraps and paginates
// exactly like any other paragraph and costs no extra pass.
// Framing disclaimer, identical to FRAMING in lib/html.mjs and worded from
// row 22 of docs/CLAIM-EVIDENCE-AUDIT.md. Both report formats carry it, so a
// claim about "the report" stays true whichever format the reader opened.
const FRAMING = 'The report never presents itself as verification of facts, legal opinion or United Nations endorsement.';
const FOLD_NOTE = 'Note on characters: this report is set in Roboto Condensed, '
  + 'an embedded typeface covering the ASCII and Western European ranges of '
  + 'the WinAnsi encoding but not every script. A character with no code in '
  + 'that encoding is shown as a question mark, so a question mark in this '
  + 'report may be a character the font cannot draw rather than punctuation '
  + 'in the copy, and two names '
  + 'that differ only in such a character will look alike here. The source file '
  + 'is unchanged, and the JSON output from the same run carries the exact name.';

// A finding banner in `detail: 'full'`: "[ERROR] UE-GR001 · grammar ·
// deterministic · line 12:5". The capture is the category — the second field
// after the bracketed severity and the rule id. The cover banner ("Editorial
// Review Report") and a hand-built banner with no bracket ("error · line
// 12:5") do not match, so nothing outside the model's own finding banners can
// be counted as a finding.
const FINDING_BANNER = /^\[[^\]]+\]\s+\S+\s+·\s+([^\s·]+)/;

/**
 * The findings behind an element list, for `legendRows` — never a count read
 * off a rendered block. Grouping is presentation: in grouped detail each
 * `issue` stands for its occurrences, so every occurrence contributes one
 * finding with its category; in `full` detail there is one finding banner per
 * finding, and the category is parsed from the banner the model printed. The
 * result is exactly the list the findings themselves would make, so the
 * legend's counts equal the counts lib/html.mjs draws from the same scan —
 * and no severity summary anywhere is derived from `issue.count`.
 *
 * @param {object[]} elements  the report element union
 * @returns {object[]} `{ category }` per finding
 */
function legendFindings(elements) {
  const hasIssues = elements.some(el => el && el.type === 'issue');
  const findings = [];
  if (hasIssues) {
    for (const el of elements) {
      if (!el || el.type !== 'issue') continue;
      const occurrences = Array.isArray(el.occurrences) ? el.occurrences.length : 0;
      for (let i = 0; i < occurrences; i++) findings.push({ category: el.category });
    }
    return findings;
  }
  for (const el of elements) {
    if (!el || el.type !== 'banner') continue;
    const match = FINDING_BANNER.exec(String(el.text || ''));
    if (match) findings.push({ category: match[1] });
  }
  return findings;
}

/**
 * Splice the thirteen-row category legend in under the Categories heading the
 * model already pushed — the section D5 puts second, so the legend sits where
 * a reader meets the marker vocabulary and before any marker is used. Both
 * detail modes get it — a legend is how a reader decodes a marker, so an
 * absent legend on one mode is an absent vocabulary. The rows come from
 * lib/legend.mjs `legendRows`, so all thirteen categories are listed with their
 * counts (zero included) in catalogue order.
 *
 * The heading itself is the model's, not spliced here, so lib/html.mjs and
 * lib/pdf.mjs cannot name the section differently.
 *
 * @param {object[]} elements  the framed element list (framing disclaimer first)
 * @returns {object[]} a new list; the input is not mutated
 */
function insertLegend(elements) {
  const rows = legendRows(legendFindings(elements));
  const categories = elements.findIndex(el => el && el.type === 'heading' && el.text === 'Categories');
  if (categories >= 0) {
    // Directly under the model's own Categories heading: the heading stays the
    // model's, so both formats name the section from the same string.
    return [
      ...elements.slice(0, categories + 1),
      { type: 'legend', rows },
      { type: 'rule' },
      ...elements.slice(categories + 1),
    ];
  }
  // Only reachable if a caller hands over a list without the model's heading
  // (the renderer's own fixtures do exactly that). The legend is still given
  // the same section name, so a reader — and a test — meets one vocabulary.
  const at = elements.findIndex(el => el && el.type === 'heading');
  if (at < 0) {
    return [...elements, { type: 'rule' }, { type: 'legend', rows }];
  }
  return [
    ...elements.slice(0, at),
    { type: 'spacer' },
    {
      type: 'heading', level: 1, text: 'Categories',
      meta: 'thirteen checked categories',
      count: sectionCount(legendFindings(elements).length),
    },
    { type: 'legend', rows },
    { type: 'rule' },
    ...elements.slice(at),
  ];
}

/**
 * The input `headerRows` is drawn from. `lib/cli.mjs` renders the PDF with
 * `{ version }` only — the model it hands over carries the scan's date and
 * targets as the cover's own kv rows — so the header is derived from those
 * cover rows, first label found, exactly as the cover prints them. A caller
 * that holds the real report input (the tests) may pass `opts.input` and skip
 * the derivation; lib/html.mjs receives that same input, and both formats
 * therefore print the same document symbol.
 *
 * @param {object[]} elements  the report element union
 * @param {object} opts        `{ version, input? }`
 * @param {string} version     the version stamped into the footer
 * @returns {{date?: string, targets?: string[], version?: string}}
 */
function headerInputFor(elements, opts, version) {
  if (opts.input && typeof opts.input === 'object') return opts.input;
  const coverValue = (label) => {
    const row = elements.find(el => el && el.type === 'kv' && el.label === label);
    return row ? String(row.value) : '';
  };
  return {
    date: coverValue('Date'),
    // Round trip of the cover's own join: `Targets` prints as
    // `targets.join(' ')`, and splitting it back must not invent or drop a
    // target (an empty value yields [], keeping headerRows' fallback title).
    targets: coverValue('Targets').split(' ').filter(Boolean),
    version,
  };
}

/**
 * Render the report element union into a complete PDF file.
 *
 * @param {object[]} elements  banner | heading | paragraph | kv | bullets | spacer | rule | issue | legend
 * @param {object} [opts]      `{ version }` — stamped into the page footer;
 *                             `{ input }` — the report input headerRows is
 *                             drawn from, when the caller holds it (the
 *                             cover's kv rows are derived otherwise)
 * @returns {Buffer} the whole PDF, uncompressed streams, correct xref
 */
export function renderPdf(elements, opts = {}) {
  const version = typeof opts.version === 'string' ? opts.version : '';
  const pages = [];
  let ops = null;
  let y = 0;
  // The header block: two furniture rows of two cells, drawn at the top of
  // every page in `drawHeader` below. Derived once — it is the same document
  // on every page — and the input is kept because the footer's copyright year
  // is read from the same date.
  const furnitureInput = headerInputFor(elements, opts, version);
  const docHeader = headerRows(furnitureInput, version);
  // The note is about characters that became "?", and only those: a literal
  // "?" in the copy does not deserve one, and neither does the soft hyphen,
  // which is dropped rather than replaced. Checking the folded character
  // directly — rather than asking the encoding whether a code point has a
  // byte — is what keeps the en dash and the curly quotes, both folded to
  // something else entirely, from claiming a note they did not cost the
  // reader anything for.
  const becomesQuestionMark = (value) => [...value]
    .some(ch => ch !== '?' && toWinAnsi(ch) === '?');
  const folded = elements.some(el => elementStrings(el).some(becomesQuestionMark));
  // The framing disclaimer leads the document, directly after the summary
  // banner when there is one, so a reader meets the boundary of the report
  // before they meet any finding in it.
  const bannerLead = elements[0]?.type === 'banner' ? 1 : 0;
  const framed = [
    ...elements.slice(0, bannerLead),
    { type: 'paragraph', text: FRAMING },
    { type: 'spacer' },
    ...elements.slice(bannerLead),
  ];
  // The legend is spliced in before layout so it flows, wraps and paginates
  // like any other element, in both detail modes. The fold note stays last:
  // it closes the document.
  const withLegend = insertLegend(framed);
  const laidOut = folded
    ? [...withLegend, { type: 'spacer' }, { type: 'rule' },
      { type: 'paragraph', text: FOLD_NOTE }]
    : withLegend;

  // The document header (D2): two rows of two cells, at the top of every page —
  // cover and continuations alike. The left cell is set from the left margin
  // and the right cell ends flush with the right edge of the measure, so the
  // boundary word sits opposite the tool name whatever their lengths are; the
  // left cell wraps into the space the right one leaves instead of running
  // underneath it. A rule closes the block, and the body starts below it.
  const HEADER_GAP = 12;
  // How much white sits between the masthead band and the closing rule. Small
  // on purpose: enough to read as two elements, not so much that they look
  // unrelated.
  const BAND_GAP = 5;
  function drawHeader() {
    // The band has to be painted *before* the type it reverses out, but its
    // height is not known until the rows have been wrapped — a header row that
    // runs long pushes the rule down. So the rows go into a scratch stream
    // first, the band is drawn from the page top to just above the rule, and
    // only then is the type laid over it.
    const restore = ops;
    const textOps = [];
    ops = textOps;
    let cursor = TOP;
    for (let i = 0; i < docHeader.length; i++) {
      const row = docHeader[i];
      const font = i === 0 ? 'F2' : 'F1';
      const size = i === 0 ? 9 : 8.5;
      const right = String(row.right || '');
      const rightW = right ? measure(right, font, size) : 0;
      const avail = Math.max(24, CONTENT_W - (right ? rightW + HEADER_GAP : 0));
      const lines = wrap(String(row.left), font, size, avail);
      // The baseline is taken before the wrap is drawn, because the right cell
      // belongs to the row's *first* line: a left cell that wrapped to three
      // lines must not drag the boundary word down with it.
      const firstBaseline = cursor - size * 0.82;
      // An all-whitespace left cell wraps to nothing. The row still spends a
      // line of height so its right cell has a baseline to sit on and the two
      // header rows cannot collapse into one another.
      if (lines.length === 0) cursor -= size + 3;
      for (const line of lines) {
        // Reversed out of the masthead: white on `#24356B` is 11.69:1.
        place(line, font, size, MARGIN, cursor - size * 0.82, WHITE);
        cursor -= size + 3;
      }
      if (right) place(right, font, size, MARGIN + CONTENT_W - rightW, firstBaseline, WHITE);
    }
    cursor -= 2;
    const ruleY = cursor - 10;
    ops = restore;

    const bandBottom = ruleY + BAND_GAP;
    // Full bleed left to right — a masthead that stops at the margin reads as a
    // box, not as the top of the page.
    ops.push(`q ${PALETTE.masthead.pdf} rg 0 ${n(bandBottom)} ${n(PAGE_W)}`
      + ` ${n(PAGE_H - bandBottom)} re f Q`);
    ops.push(...textOps);

    // The `m` is not decoration: `l` appends to the *current* point, and with
    // no point established the operation is undefined. Acrobat rejects such a
    // page outright — "An error exists on this page" — while other viewers
    // silently guess, which is how a rule without a moveto shipped at all.
    ops.push(`q 0.5 w ${PALETTE.divider.pdf} RG ${n(MARGIN)} ${n(ruleY)} m`
      + ` ${n(MARGIN + CONTENT_W)} ${n(ruleY)} l S Q`);
    y = ruleY - 10;
  }

  function newPage() {
    ops = [];
    pages.push(ops);
    drawHeader();
  }

  function need(height) {
    if (y - height < BOTTOM) newPage();
  }

  function place(line, font, size, x, baseline, colour) {
    ops.push(`${colour} rg BT /${font} ${n(size)} Tf ${n(x)} ${n(baseline)}`
      + ` Td ${pdfLiteral(line)} Tj ET`);
  }

  function drawBanner(el) {
    const fontSize = 11;
    const lead = 15;
    const pad = 4;
    const lines = wrap(String(el.text), 'F2', fontSize, CONTENT_W - 12);
    if (lines.length === 0) return;
    const height = lines.length * lead + pad;
    need(height);
    const rectTop = y;
    ops.push(`q ${bannerFill(el.kind)} rg ${n(MARGIN)} ${n(rectTop - height)}`
      + ` ${n(CONTENT_W)} ${n(height)} re f Q`);
    const capHeight = fontSize * 0.717;
    for (let i = 0; i < lines.length; i++) {
      const lineTop = rectTop - pad / 2 - i * lead;
      place(lines[i], 'F2', fontSize, MARGIN + 6, lineTop - lead / 2 - capHeight / 2, WHITE);
    }
    y = rectTop - height - 4;
  }

  function drawHeading(el) {
    const second = Number(el.level) === 2;
    const size = second ? 13 : 16;
    const lead = second ? 17 : 20;
    const before = second ? 9 : 12;
    const after = second ? 4 : 6;
    const title = String(el.text);
    const meta = String(el.meta || '');
    const count = String(el.count || '');
    // D6: the title carries no number of its own. The section's finding count
    // is set at the right edge of the content column, level with the title, so
    // a reader meets how many findings a section claims at the same moment as
    // its name and cannot mistake a count for a section number. The lane
    // metadata follows the title in the lighter grey.
    const countW = count ? measure(count, 'F1', 9) : 0;
    const metaW = meta ? measure(` ${meta}`, 'F1', 9) : 0;
    const room = CONTENT_W - (countW ? countW + 10 : 0) - metaW;
    const lines = wrap(title, 'F2', size, room);
    if (lines.length === 0) return;
    // Keep the heading with the first body line where the page allows it.
    if (y - (before + lines.length * lead + BODY_LEAD) < BOTTOM) newPage();
    y -= y >= TOP ? 0 : before;
    const baseline = y - size * 0.82;
    for (const line of lines) {
      place(line, 'F2', size, MARGIN, y - size * 0.82, BLACK);
      y -= lead;
    }
    if (meta) place(meta, 'F1', 9, MARGIN + measure(lines[0], 'F2', size) + 6, baseline, META_GREY);
    if (count) place(count, 'F1', 9, MARGIN + CONTENT_W - countW, baseline, META_GREY);
    y -= after;
  }

  function drawParagraph(el) {
    for (const line of wrap(String(el.text), 'F1', BODY, CONTENT_W)) {
      need(BODY_LEAD);
      place(line, 'F1', BODY, MARGIN, y - BODY * 0.82, BLACK);
      y -= BODY_LEAD;
    }
    y -= 4;
  }

  function drawKv(el) {
    const labelLines = wrap(String(el.label), 'F2', BODY, LABEL_COL);
    const valueLines = wrap(String(el.value), 'F1', BODY, CONTENT_W - LABEL_COL);
    const rows = Math.max(labelLines.length, valueLines.length);
    for (let i = 0; i < rows; i++) {
      need(BODY_LEAD);
      if (labelLines[i]) place(labelLines[i], 'F2', BODY, MARGIN, y - BODY * 0.82, BLACK);
      if (valueLines[i]) {
        place(valueLines[i], 'F1', BODY, MARGIN + LABEL_COL, y - BODY * 0.82, BLACK);
      }
      y -= BODY_LEAD;
    }
    y -= 2;
  }

  function drawBullets(el) {
    const items = Array.isArray(el.items) ? el.items : [];
    for (const item of items) {
      const lines = wrap(String(item), 'F1', BODY, CONTENT_W - BULLET_INDENT);
      for (let i = 0; i < lines.length; i++) {
        need(BODY_LEAD);
        const x = i === 0 ? MARGIN : MARGIN + BULLET_INDENT;
        const shown = i === 0 ? '\u2022 ' + lines[i] : lines[i];
        place(shown, 'F1', BODY, x, y - BODY * 0.82, BLACK);
        y -= BODY_LEAD;
      }
    }
    y -= 3;
  }

  function drawSpacer() {
    y -= 6;
    if (y < BOTTOM) y = BOTTOM;
  }

  function drawRule() {
    need(8);
    const at = y - 4;
    ops.push(`q 0.5 w ${PALETTE.rule.pdf} RG ${n(MARGIN)} ${n(at)} m`
      + ` ${n(MARGIN + CONTENT_W)} ${n(at)} l S Q`);
    y -= 8;
  }

  // D13's cap block, in one bordered band so a capped section cannot be read
  // as a section that simply ended. The three lines are lib/report.mjs
  // `capLines`, printed verbatim: the count withheld, the promise that
  // nothing was discarded, and the exact command that lists the rest.
  function drawCap(el) {
    const [head, promise, command] = capLines({
      shown: Number(el.shown), total: Number(el.total), command: String(el.command),
    });
    const inner = CONTENT_W - 16;
    const bold = wrap(head, 'F2', BODY, inner);
    const prose = wrap(promise, 'F1', BODY, inner);
    const code = wrap(command, 'F2', BODY - 1, inner);
    const height = 10 + bold.length * BODY_LEAD + 5 + prose.length * BODY_LEAD
      + 5 + code.length * (BODY_LEAD - 1) + 12;
    // A band taller than a page could never be drawn whole; in that case the
    // page is turned instead of squeezing the box into the space that is left.
    if (height <= TOP - BOTTOM) need(height);
    else newPage();
    const top = y - 4;
    let cursor = top - 10;
    for (const line of bold) {
      place(line, 'F2', BODY, MARGIN + 8, cursor, BLACK);
      cursor -= BODY_LEAD;
    }
    cursor -= 5;
    for (const line of prose) {
      place(line, 'F1', BODY, MARGIN + 8, cursor, BLACK);
      cursor -= BODY_LEAD;
    }
    cursor -= 5;
    for (const line of code) {
      place(line, 'F2', BODY - 1, MARGIN + 8, cursor, BLACK);
      cursor -= BODY_LEAD - 1;
    }
    const bottom = cursor - 7;
    ops.push(`q 0.5 w ${PALETTE.rule.pdf} RG ${n(MARGIN)} ${n(bottom)} ${n(CONTENT_W)}`
      + ` ${n(top - bottom)} re S Q`);
    y = bottom - 8;
  }

  // One grouped issue: the severity banner, the marker row (shaded code
  // swatch, the category's own name as the text label, and the group's size
  // only when it is more than one occurrence), then exactly the block
  // pushFinding draws — Current, Should be, the explanation, the audit
  // marker, the heuristic note, the six provenance rows — and the structured
  // Occurrences list: one File / Location / Content / Should be block per
  // hit, separated by rules, every value wrapped within the measure. The
  // banner already carries ` · line L:C` when the group holds a single
  // occurrence, so no location is added here.
  function drawIssue(el) {
    drawBanner({ kind: el.kind, text: el.text });

    const count = Number(el.count);
    const showCount = count > 1;
    need(16);
    const rowTop = y;
    const baseline = rowTop - 10;
    // D11: the row's marks are drawn, not written. Severity artwork first,
    // then the category's own artwork, then the coloured swatch carrying the
    // category's short code — D12's order, and the reason colour is never the
    // only signal: two shapes and a code all say what the row is before a
    // word is read. The artwork is set in black on white here rather than
    // knocked out of the banner, because these marks knock their counters out
    // in white and would erase themselves on a dark field.
    const iconSize = 9;
    const iconY = rowTop - iconSize - 1;
    const sevShapes = severityIcon(el.kind);
    if (sevShapes) ops.push(pdfIcon(sevShapes, { x: MARGIN, y: iconY, size: iconSize }));
    const catShapes = el.category ? categoryIcon(el.category) : null;
    if (catShapes) ops.push(pdfIcon(catShapes, { x: MARGIN + 11, y: iconY, size: iconSize }));
    const swatchX = MARGIN + 22;
    const colour = typeof el.colour === 'string' && el.colour !== ''
      ? rgbFill(el.colour) : '';
    if (colour) {
      ops.push(`q ${colour} rg ${n(swatchX)} ${n(rowTop - 12.6)} 26 11 re f Q`);
    }
    const marker = String(el.marker || '');
    if (marker) {
      const codeWidth = measure(marker, 'F2', 8);
      place(marker, 'F2', 8, swatchX + (26 - codeWidth) / 2, baseline,
        colour ? WHITE : BLACK);
    }
    // A count is shown only when it is greater than one: a group of one is
    // not a summary, and "1 occurrence" beside a lone finding reads as though
    // something was counted that was not there.
    const countText = showCount ? `${count} occurrences` : '';
    const countWidth = countText ? measure(countText, 'F1', BODY) : 0;
    const nameX = MARGIN + 54;
    const nameWidth = MARGIN + CONTENT_W - countWidth - 8 - nameX;
    const name = wrap(String(el.category || ''), 'F2', BODY, Math.max(40, nameWidth))[0] || '';
    if (name) place(name, 'F2', BODY, nameX, baseline, BLACK);
    if (countText) {
      place(countText, 'F1', BODY, MARGIN + CONTENT_W - countWidth, baseline, BLACK);
    }
    y = rowTop - 16;

    drawKv({ type: 'kv', label: 'Current', value: el.current });
    drawKv({ type: 'kv', label: 'Should be', value: el.should });
    drawParagraph({ type: 'paragraph', text: el.message });
    if (el.audit) drawKv({ type: 'kv', label: 'Audit', value: el.audit });
    if (el.heuristic) {
      drawParagraph({ type: 'paragraph', text: 'Heuristic finding — routed to review.' });
    }
    if (Array.isArray(el.provenance)) {
      for (const row of el.provenance) {
        drawKv({ type: 'kv', label: row.label, value: row.value });
      }
    }
    const occurrences = Array.isArray(el.occurrences) ? el.occurrences : [];
    if (occurrences.length) {
      drawHeading({ type: 'heading', level: 2, text: 'Occurrences' });
      for (const occurrence of occurrences) {
        drawRule();
        // A PDF-derived finding carries the source page; a plain text finding
        // has no page and prints the position alone.
        const location = Number.isInteger(occurrence.pdfPage)
          ? `${occurrence.line}:${occurrence.column} · page ${occurrence.pdfPage}`
          : `${occurrence.line}:${occurrence.column}`;
        drawKv({ type: 'kv', label: 'File', value: occurrence.file });
        drawKv({ type: 'kv', label: 'Location', value: location });
        drawKv({ type: 'kv', label: 'Content', value: occurrence.content });
        drawKv({ type: 'kv', label: 'Should be', value: occurrence.should });
      }
    }
  }

  // The category legend: four column headers, then one row per category —
  // shaded code swatch, the category's own name (the text label, so colour
  // and shape are never the only signal), what the category covers, and how
  // many findings fired it (zero-count rows included: a legend that dropped
  // them would read as though those categories do not exist).
  function drawLegend(el) {
    const rows = Array.isArray(el.rows) ? el.rows : [];
    // D11: the row leads with the category's own artwork, then the coloured
    // swatch carrying its short code, then its name — the same order the
    // finding rows use, so the legend teaches a mark the report actually
    // draws rather than one it never prints.
    const ICON = 9;
    const SWATCH_X = MARGIN + ICON + 2;
    const NAME_X = MARGIN + 41;
    const INTENT_X = MARGIN + 146;
    const RIGHT = MARGIN + CONTENT_W;
    const NAME_W = INTENT_X - NAME_X - 8;
    const INTENT_W = RIGHT - INTENT_X - 46;
    const ROW_H = 14;
    need(ROW_H + 16);
    const headerBaseline = y - 9 * 0.82;
    place('Marker', 'F2', 9, MARGIN, headerBaseline, BLACK);
    place('Category', 'F2', 9, NAME_X, headerBaseline, BLACK);
    place('What it covers', 'F2', 9, INTENT_X, headerBaseline, BLACK);
    const findingsWidth = measure('Findings', 'F2', 9);
    place('Findings', 'F2', 9, RIGHT - findingsWidth, headerBaseline, BLACK);
    y -= 16;
    for (const row of rows) {
      need(ROW_H);
      const rowTop = y;
      const baseline = rowTop - 10;
      // The artwork is set in black on white: these marks knock their
      // counters out in white, so a coloured or reversed field would erase
      // them. An unknown category simply has no icon here — its code and its
      // name still say what it is, which is what keeps the row readable.
      const shapes = categoryIcon(row.category);
      if (shapes) {
        ops.push(pdfIcon(shapes, { x: MARGIN, y: rowTop - ICON - 1, size: ICON }));
      }
      ops.push(`q ${rgbFill(row.colour)} rg ${n(SWATCH_X)} ${n(rowTop - 12.6)}`
        + ` 26 11 re f Q`);
      const code = String(row.code || '');
      if (code) {
        const codeWidth = measure(code, 'F2', 8);
        place(code, 'F2', 8, SWATCH_X + (26 - codeWidth) / 2, baseline, WHITE);
      }
      const name = wrap(String(row.category || ''), 'F2', BODY, NAME_W)[0] || '';
      if (name) place(name, 'F2', BODY, NAME_X, baseline, BLACK);
      const intent = wrap(String(row.intent || ''), 'F1', 9, INTENT_W)[0] || '';
      if (intent) place(intent, 'F1', 9, INTENT_X, baseline, BLACK);
      const countText = String(row.count ?? 0);
      place(countText, 'F1', 9, RIGHT - measure(countText, 'F1', 9), baseline, BLACK);
      y = rowTop - ROW_H;
    }
  }

  newPage();
  for (const el of laidOut) {
    const kind = el && typeof el === 'object' ? el.type : undefined;
    switch (kind) {
      case 'banner': drawBanner(el); break;
      case 'heading': drawHeading(el); break;
      case 'paragraph': drawParagraph(el); break;
      case 'kv': drawKv(el); break;
      case 'bullets': drawBullets(el); break;
      case 'spacer': drawSpacer(); break;
      case 'rule': drawRule(); break;
      case 'issue': drawIssue(el); break;
      case 'cap': drawCap(el); break;
      case 'legend': drawLegend(el); break;
      default: throw new Error('unknown element type: ' + String(kind));
    }
  }

  // Second pass: the footer needs the final page count, so the three cells —
  // D3's page position (the renderer is the only place that knows how many
  // pages it drew), the copyright with its year read from the scan's date, and
  // the repository address — are stamped onto the finished pages before
  // serialization. Each cell is placed at its own edge of the measure: the
  // left cell from the left margin, the centre cell on the middle of it, the
  // right cell ending at the right margin. They read as three columns rather
  // than as one centred pile, which is what the plan's mockup draws and what
  // the footer cells are named for.
  const total = pages.length;
  const baseline = FOOTER_Y;
  // The band stops below the lowest line the body can draw (BOTTOM is MARGIN,
  // 54), so it is painted last without covering anything: nothing else on the
  // page reaches down this far.
  const FOOTER_BAND_TOP = 48;
  for (let i = 0; i < total; i++) {
    const cells = footerCells({ date: furnitureInput.date, page: i + 1, pages: total });
    // R8: the band first, so the three cells sit on it rather than under it.
    pages[i].push(`q ${PALETTE.footerBand.pdf} rg 0 0 ${n(PAGE_W)} ${n(FOOTER_BAND_TOP)} re f Q`);
    pages[i].push(`q 0.5 w ${PALETTE.divider.pdf} RG ${n(MARGIN)} ${n(FOOTER_BAND_TOP)} m`
      + ` ${n(MARGIN + CONTENT_W)} ${n(FOOTER_BAND_TOP)} l S Q`);
    const draws = [
      { text: cells.left, x: MARGIN },
      { text: cells.centre, x: MARGIN + (CONTENT_W - measure(cells.centre, 'F1', FOOTER_SIZE)) / 2 },
      { text: cells.right, x: MARGIN + CONTENT_W - measure(cells.right, 'F1', FOOTER_SIZE) },
    ];
    for (const d of draws) {
      pages[i].push(`${FOOTER_GREY} rg BT /F1 ${n(FOOTER_SIZE)} Tf ${n(d.x)} ${n(baseline)}`
        + ` Td ${pdfLiteral(d.text)} Tj ET`);
    }
  }

  return serialize(pages);
}
