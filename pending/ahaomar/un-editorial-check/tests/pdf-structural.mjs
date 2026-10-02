// Structural verification for lib/pdf.mjs — written first, per the Phase 3
// contract, because xref correctness is the named risk of the hand-rolled
// writer.
//
// The suite builds synthetic element lists, renders them, then reads the
// bytes back: magic and end marker, xref offsets against `N 0 obj`, page and
// font objects, text extraction from the uncompressed `Tj` operands,
// transliteration, literal-string escaping, a footer on every page, an
// unbroken 600-character token, and byte-identical determinism. Line widths
// are re-measured against the embedded faces' own advances, pinned here, so
// the wrap logic cannot drift. Only node:assert and the module under test are
// used.

import assert from 'node:assert/strict';
import { inflateSync } from 'node:zlib';
import { renderPdf } from '../lib/pdf.mjs';
import { CATEGORY_LEGEND, legendRows } from '../lib/legend.mjs';
import { categoryIcon, pdfIcon, severityIcon } from '../lib/icons.mjs';
import { footerCells, headerRows } from '../lib/furniture.mjs';

// --- page geometry (mirrors the contract, restated independently) ----------

const PAGE_W = 595.28;
const PAGE_H = 841.89;
const MARGIN = 54;
const CONTENT_W = PAGE_W - 2 * MARGIN;
const LABEL_COL = 84;

// --- independent width tables (units per 1000 em) ---------------------------
// The advances of the two embedded faces, byte-indexed like `/Widths`: index 0
// is byte 0x20 (space) for ASCII, byte 0x80 for the upper half, and byte 127
// plus Adobe's five undefined C1 positions measure 0 because no folded string
// can hold them. These are pinned here rather than read through lib/ttf.mjs,
// so a drift in the font layer shows up as a line that no longer fits its
// column instead of as two copies of the same mistake agreeing.

const REG_ASCII = [
  229, 246, 320, 548, 494, 633, 544, 175, // 0x20..0x27 space ! " # $ % & '
  314, 319, 431, 497, 197, 248, 264, 371, // 0x28..0x2F ( ) * + , - . /
  494, 494, 494, 494, 494, 494, 494, 494, // 0x30..0x37 0 1 2 3 4 5 6 7
  494, 494, 233, 203, 446, 479, 460, 422, // 0x38..0x3F 8 9 : ; < = > ?
  769, 577, 546, 567, 571, 497, 481, 591, // 0x40..0x47 @ A B C D E F G
  620, 250, 483, 545, 476, 755, 620, 601, // 0x48..0x4F H I J K L M N O
  554, 601, 531, 519, 521, 562, 561, 762, // 0x50..0x57 P Q R S T U V W
  551, 525, 523, 250, 370, 250, 371, 405, // 0x58..0x5F X Y Z [ \ ] ^ _
  309, 479, 493, 462, 496, 469, 316, 493, // 0x60..0x67 ` a b c d e f g
  483, 229, 224, 451, 229, 753, 484, 502, // 0x68..0x6F h i j k l m n o
  493, 500, 305, 456, 296, 483, 428, 650, // 0x70..0x77 p q r s t u v w
  439, 417, 439, 307, 244, 307, 589, // 0x78..0x7E x y z { | } ~
];

const BOLD_ASCII = [
  230, 261, 321, 528, 505, 638, 579, 162, // 0x20..0x27
  323, 324, 454, 476, 245, 361, 291, 332, // 0x28..0x2F
  505, 505, 505, 505, 505, 505, 505, 505, // 0x30..0x37
  505, 505, 273, 253, 447, 503, 454, 447, // 0x38..0x3F
  766, 597, 561, 570, 565, 491, 476, 585, // 0x40..0x47
  614, 270, 490, 553, 479, 758, 612, 604, // 0x48..0x4F
  568, 604, 553, 540, 542, 571, 578, 750, // 0x50..0x57
  560, 542, 530, 264, 381, 264, 391, 400, // 0x58..0x5F
  331, 471, 495, 460, 496, 479, 328, 503, // 0x60..0x67
  492, 252, 245, 478, 252, 742, 492, 498, // 0x68..0x6F
  495, 497, 331, 454, 307, 492, 449, 633, // 0x70..0x77
  452, 445, 452, 298, 253, 298, 558, // 0x78..0x7E
];

const REG_UPPER = [
  494, 0, 195, 310, 327, 590, 483, 500, // 0x80..0x87 € ‚ ƒ „ … † ‡ ˆ
  428, 819, 519, 272, 827, 0, 523, 0, // 0x88..0x8F ‰ Š ‹ Œ Ž ˜ ­ ®¯ (0x8D and 0x8F undefined)
  0, 195, 195, 334, 337, 337, 572, 678, // 0x90..0x97 (0x90 undefined) ' ' " " • – —
  428, 548, 456, 272, 777, 0, 439, 525, // 0x98..0x9F ˜ ™ š › Œ ž Ÿ (0x9D undefined)
  229, 232, 480, 511, 713, 464, 240, 538, // 0xA0..0xA7
  418, 786, 396, 418, 487, 248, 786, 415, // 0xA8..0xAF
  374, 470, 330, 330, 313, 499, 435, 244, // 0xB0..0xB7
  229, 330, 403, 418, 638, 678, 673, 422, // 0xB8..0xBF
  577, 577, 577, 577, 577, 577, 813, 567, // 0xC0..0xC7
  497, 497, 497, 497, 250, 250, 250, 250, // 0xC8..0xCF
  585, 620, 601, 601, 601, 601, 601, 471, // 0xD0..0xD7
  601, 562, 562, 562, 562, 525, 515, 522, // 0xD8..0xDF
  479, 479, 479, 479, 479, 479, 729, 462, // 0xE0..0xE7
  469, 469, 469, 469, 235, 235, 235, 235, // 0xE8..0xEF
  514, 484, 502, 502, 502, 502, 502, 500, // 0xF0..0xF7
  499, 483, 483, 483, 483, 417, 508, 417, // 0xF8..0xFF
];

const BOLD_UPPER = [
  505, 0, 244, 330, 385, 661, 470, 509, // 0x80..0x87
  453, 821, 540, 284, 841, 0, 531, 0, // 0x88..0x8F
  0, 229, 225, 386, 389, 360, 548, 661, // 0x90..0x97
  437, 554, 454, 274, 771, 0, 452, 542, // 0x98..0x9F
  230, 271, 508, 524, 692, 475, 252, 552, // 0xA0..0xA7
  467, 785, 394, 449, 485, 361, 785, 457, // 0xA8..0xAF
  389, 472, 335, 335, 332, 548, 436, 284, // 0xB0..0xB7
  249, 335, 406, 449, 623, 663, 704, 446, // 0xB8..0xBF
  597, 597, 597, 597, 597, 597, 818, 570, // 0xC0..0xC7
  491, 491, 491, 491, 271, 271, 271, 271, // 0xC8..0xCF
  580, 612, 604, 604, 604, 604, 604, 469, // 0xD0..0xD7
  602, 571, 571, 571, 571, 542, 533, 558, // 0xD8..0xDF
  471, 471, 471, 471, 471, 471, 729, 459, // 0xE0..0xE7
  479, 479, 479, 479, 262, 262, 262, 262, // 0xE8..0xEF
  502, 493, 498, 498, 498, 498, 498, 500, // 0xF0..0xF7
  497, 492, 492, 492, 492, 445, 500, 445, // 0xF8..0xFF
];

/** The advance of one WinAnsi byte in the face `bold` selects. */
function byteWidth(byte, bold) {
  const table = bold
    ? (byte >= 0x80 ? BOLD_UPPER : BOLD_ASCII)
    : (byte >= 0x80 ? REG_UPPER : REG_ASCII);
  if (byte >= 0x20 && byte <= 0x7E) return table[byte - 0x20];
  if (byte >= 0x80 && byte <= 0xFF) return table[byte - 0x80];
  return 0; // byte 127 and the five undefined C1 positions
}

// Spot locks: the table must be the real advances, not a plausible guess.
// The seven pairs are the facts PHASE-10-PLAN pins for these faces and
// tests/ttf.mjs locks independently from the font files, so a table
// regenerated to agree with a broken font layer still fails here.
assert.equal(byteWidth(0x20, false), 229, 'space is 229 in Roboto Condensed');
assert.equal(byteWidth(0x41, false), 577, 'A is 577 in Roboto Condensed');
assert.equal(byteWidth(0x57, false), 762, 'W is 762 in Roboto Condensed');
assert.equal(byteWidth(0x69, false), 229, 'i is 229 in Roboto Condensed');
assert.equal(byteWidth(0x96, false), 572, 'the en dash keeps its WinAnsi byte and its width');
assert.equal(byteWidth(0x80, false), 494, 'the euro sign is 494 in Roboto Condensed');
assert.equal(byteWidth(0xE9, false), 469, 'e-acute is 469 in Roboto Condensed');
assert.equal(byteWidth(0x20, true), 230, 'space is 230 in Roboto Condensed Bold');
assert.equal(byteWidth(0x41, true), 597, 'A is 597 in Roboto Condensed Bold');
assert.equal(byteWidth(0x57, true), 750, 'W is 750 in Roboto Condensed Bold');
assert.equal(byteWidth(0x69, true), 252, 'i is 252 in Roboto Condensed Bold');
// The unreachable positions measure nothing, so no line break can be owed to a
// byte no string can carry.
for (const byte of [0x7F, 0x81, 0x8D, 0x8F, 0x90, 0x9D]) {
  assert.equal(byteWidth(byte, false), 0, `byte 0x${byte.toString(16)} has no advance`);
}

// Measured over the bytes the writer actually emits: an extracted line is one
// JS char per WinAnsi byte, so indexing by char code is indexing by byte.
function lineWidth(text, font, size) {
  const bold = font === 'F2';
  let width = 0;
  for (let i = 0; i < text.length; i++) {
    width += (byteWidth(text.charCodeAt(i), bold) * size) / 1000;
  }
  return width;
}

// --- extraction from the uncompressed content streams ------------------------

// Only F1 and F2 exist since Stage D dropped the italic resource: a resource
// name outside that pair is a renderer that started drawing something no code
// path asks for, so the extractor must not quietly read it.
const LINE_RE = /\/(F[12]) ([0-9.]+) Tf ([0-9.-]+) ([0-9.-]+) Td \(((?:\\[\s\S]|[^\\()])*)\) Tj/g;

function unpdf(operand) {
  return operand.replace(/\\([()\\])/g, '$1');
}

function extractLinesFrom(body) {
  const out = [];
  for (const m of body.matchAll(LINE_RE)) {
    out.push({
      font: m[1],
      size: Number(m[2]),
      x: Number(m[3]),
      y: Number(m[4]),
      text: unpdf(m[5]),
    });
  }
  return out;
}

/**
 * The page content streams, in file order. Each dictionary is read for its
 * `/Length` and the body taken at that exact byte count: since Stage D
 * embedded `/FontFile2` and `/ToUnicode` as compressed binary, a sweep that
 * regexed `stream…endstream` would hand font-program bytes to the extractor
 * as if they were drawn copy. A dictionary carrying `/Filter` is skipped —
 * no page content stream has one, and the binary behind it is not text.
 *
 * @param {Buffer} pdf
 * @returns {string[]} one entry per page content stream
 */
function streamBodies(pdf) {
  const text = pdf.toString('latin1');
  const out = [];
  for (const m of text.matchAll(/<<(.*?)>>\nstream\n/gs)) {
    // The match may open at a `<<` belonging to an earlier object and run on
    // to the `>>` that closes this stream's own dictionary (the page object
    // precedes its content object and neither is itself a stream). Only the
    // last dictionary in the span belongs to the stream, so only it is read —
    // otherwise an earlier object's numbers could be taken for this one's.
    const open = m[1].lastIndexOf('<<');
    const dict = open === -1 ? m[1] : m[1].slice(open + 2);
    if (dict.includes('/Filter')) continue;
    const length = /\/Length (\d+)/.exec(dict);
    assert(length, `a content stream without a /Length: ${JSON.stringify(dict.slice(0, 80))}`);
    out.push(text.slice(m.index + m[0].length, m.index + m[0].length + Number(length[1])));
  }
  return out;
}

/** Every drawn line of the whole document, in stream (page) order. */
function extractLines(pdf) {
  return streamBodies(pdf).flatMap(extractLinesFrom);
}

/** The drawn lines page by page: header first, footer last, on every page. */
function pageLines(pdf) {
  return streamBodies(pdf).map(extractLinesFrom);
}

// Word wrapping collapses runs of whitespace, so a drawn line and the string
// it was drawn from are compared with the runs collapsed on both sides.
const squash = (text) => text.replace(/\s+/g, ' ').trim();

/**
 * The value of one kv row, including every wrapped continuation line: the
 * label sits at x=54 (bold) and the value at x=54+84=138 (regular), and a
 * value wider than the value column continues at x=138 on the lines below.
 */
function kvValueAll(lines, label, from = 0) {
  const i = lines.findIndex((l, j) =>
    j >= from && l.text === label && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
  assert(i >= 0, `missing kv label: ${label}`);
  const parts = [];
  for (let j = i + 1; j < lines.length; j++) {
    const l = lines[j];
    if (l.x !== MARGIN + LABEL_COL || l.font !== 'F1' || l.size !== 10.5) break;
    parts.push(l.text);
  }
  assert(parts.length > 0, `missing kv value row after ${label}`);
  return squash(parts.join(' '));
}

// --- structural validation ---------------------------------------------------

/**
 * The two embedded faces, read back out of the bytes: the font dictionaries
 * and their descriptor values, the subset program behind each `/FontFile2`
 * inflated and checked against the `/Length1` it claims and the sfnt magic it
 * must start with, the `/Widths` row compared entry by entry against the
 * pinned table above, and the `/ToUnicode` CMap inflated and read for the
 * byte-to-character mapping copy-paste depends on. Stage D replaced three
 * base-14 Helvetica resources with these two, so every assertion that used to
 * name Helvetica now names the face that took its place, and the `/F3` lock
 * below is a *negative* one: nothing may re-add an italic resource no code
 * path draws.
 *
 * @param {string} s the whole file, latin1
 * @param {string} label the fixture name, for assertion messages
 */
function assertEmbeddedFaces(s, label) {
  // No base-14 face survives anywhere — including inside a stream.
  assert(!s.includes('Helvetica'), `${label}: no base-14 Helvetica reference remains`);

  const fonts = [...s.matchAll(/<< \/Type \/Font [^>]*\/BaseFont (\/[^ /]+)[^>]*>>/g)]
    .map(m => m[1]);
  assert.deepEqual(fonts, ['/ROBREG+RobotoCondensed-Regular', '/ROBBOL+RobotoCondensed-Bold'],
    `${label}: exactly two embedded faces, Regular as F1 and Bold as F2, each under a `
    + 'deterministic subset tag');

  assert.equal((s.match(/\/Subtype \/TrueType/g) || []).length, 2,
    `${label}: both fonts are simple TrueType, not a composite CID font`);
  assert.equal((s.match(/\/Encoding \/WinAnsiEncoding/g) || []).length, 2,
    `${label}: both embedded faces use WinAnsi encoding`);
  // The italic resource is gone (R5): it was never drawn by any code path.
  assert(!/\/F3\b/.test(s), `${label}: no /F3 resource, an italic nothing draws`);
  assert(s.includes('/F1 3 0 R') && s.includes('/F2 4 0 R'),
    `${label}: page resources reference the two embedded faces`);

  // --- /Widths, entry by entry -----------------------------------------------
  const widthRows = [...s.matchAll(/\/Widths \[([^\]]*)\]/g)].map(m =>
    m[1].trim().split(/\s+/).map(Number));
  assert.equal(widthRows.length, 2, `${label}: one /Widths row per face`);
  for (let f = 0; f < 2; f++) {
    const row = widthRows[f];
    // FirstChar 32, LastChar 255: 224 entries, indexed by the byte a viewer
    // reads — not 256, and not one entry per Unicode code point.
    assert.equal(row.length, 224, `${label}: /Widths for face ${f} has 224 entries (32..255)`);
    const bad = [];
    for (let i = 0; i < row.length; i++) {
      const expected = byteWidth(32 + i, f === 1);
      if (row[i] !== expected) bad.push(`0x${(32 + i).toString(16)}: ${row[i]} != ${expected}`);
    }
    assert.deepEqual(bad, [],
      `${label}: /Widths for face ${f} is the pinned advance of every byte `
      + `(${row.length - bad.length}/${row.length} match)`);
  }

  // --- the font descriptors ---------------------------------------------------
  const descriptors = [...s.matchAll(/<< \/Type \/FontDescriptor [^>]*>>/g)].map(m => m[0]);
  assert.equal(descriptors.length, 2, `${label}: one FontDescriptor per face`);
  // The outline metrics, scaled from the face's 2048-unit em to 1000: the
  // plan's own facts (ascent 1900, descent -500, cap height 1456, unitsPerEm
  // 2048), so a descriptor read from the wrong table fails here.
  const EXPECTED = [
    { box: '[-737 -271 998 1056]', ascent: 928, descent: -244, cap: 711, stem: 80 },
    { box: '[-727 -271 1040 1056]', ascent: 928, descent: -244, cap: 711, stem: 140 },
  ];
  descriptors.forEach((d, i) => {
    assert(d.includes('/Flags 32'), `${label}: descriptor ${i} declares symbolic-free flags 32`);
    assert(d.includes(`/FontBBox ${EXPECTED[i].box}`),
      `${label}: descriptor ${i} FontBBox is the face's own, scaled to 1000 em`);
    assert(d.includes('/ItalicAngle 0'), `${label}: descriptor ${i} is upright`);
    assert(d.includes(` /Ascent ${EXPECTED[i].ascent}`), `${label}: descriptor ${i} Ascent`);
    assert(d.includes(` /Descent ${EXPECTED[i].descent}`), `${label}: descriptor ${i} Descent`);
    assert(d.includes(` /CapHeight ${EXPECTED[i].cap}`), `${label}: descriptor ${i} CapHeight`);
    assert(d.includes(` /StemV ${EXPECTED[i].stem}`), `${label}: descriptor ${i} StemV`);
    assert(d.includes('/FontFile2 '), `${label}: descriptor ${i} points at its FontFile2`);
  });

  // --- the two compressed streams, inflated ----------------------------------
  const streams = [...s.matchAll(/<<(.*?)>>\nstream\n/gs)].map((m) => {
    const open = m[1].lastIndexOf('<<');
    const dict = open === -1 ? m[1] : m[1].slice(open + 2);
    const start = m.index + m[0].length;
    return { dict, body: s.slice(start, start + Number(/\/Length (\d+)/.exec(dict)[1])) };
  });
  const fontFiles = streams.filter(x => x.dict.includes('/Length1'));
  assert.equal(fontFiles.length, 2, `${label}: two FontFile2 streams`);
  for (const [i, { dict, body }] of fontFiles.entries()) {
    assert(dict.includes('/Filter /FlateDecode'), `${label}: FontFile2 ${i} is FlateDecode`);
    const raw = inflateSync(Buffer.from(body, 'latin1'));
    // /Length1 is the *uncompressed* length the viewer checks against.
    const length1 = Number(/\/Length1 (\d+)/.exec(dict)[1]);
    assert.equal(raw.length, length1,
      `${label}: FontFile2 ${i} inflates to the /Length1 it declares`);
    // A real sfnt program: version 1.0 as a uint32, not a stub.
    assert.equal(raw.readUInt32BE(0), 0x00010000,
      `${label}: FontFile2 ${i} is a TrueType sfnt (version 1.0)`);
    // The subset really is a subset: its table directory is checked out of the
    // inflated bytes themselves, not asserted to be merely "small enough". The
    // four shaping tables are dropped by the subsetter (nobody shapes a PDF's
    // single-byte runs) and the core layout tables must all survive, because
    // `/Widths` was measured from `hmtx` and the descriptor from head, hhea,
    // OS/2 and post — a subset that lost one of those would disagree with the
    // numbers already checked above.
    const tags = [];
    const numTables = raw.readUInt16BE(4);
    for (let t = 0; t < numTables; t++) tags.push(raw.toString('latin1', 12 + t * 16, 16 + t * 16));
    assert.equal(numTables, 14,
      `${label}: FontFile2 ${i} carries the 14 tables the subset keeps, found ${tags.join(' ')}`);
    for (const dropped of ['GPOS', 'GSUB', 'GDEF', 'STAT']) {
      assert(!tags.includes(dropped),
        `${label}: FontFile2 ${i} dropped the shaping table ${dropped}`);
    }
    for (const kept of ['cmap', 'glyf', 'head', 'hhea', 'hmtx', 'loca', 'maxp',
      'OS/2', 'post']) {
      assert(tags.includes(kept),
        `${label}: FontFile2 ${i} still carries ${kept}, which the metrics above were read from`);
    }
  }

  const cMaps = streams.filter(x => x.dict.includes('/Filter') && !x.dict.includes('/Length1'));
  assert.equal(cMaps.length, 2, `${label}: two ToUnicode streams`);
  for (const [i, { dict, body }] of cMaps.entries()) {
    assert(dict.includes('/Filter /FlateDecode'), `${label}: ToUnicode ${i} is FlateDecode`);
    const cmap = inflateSync(Buffer.from(body, 'latin1')).toString('latin1');
    assert(cmap.includes('begincmap'), `${label}: ToUnicode ${i} is a CMap`);
    assert(cmap.includes('beginbfchar'), `${label}: ToUnicode ${i} uses bfchar entries`);
    // The mapping copy-paste depends on: byte 0x96 is the en dash, and the
    // undefined positions Adobe leaves blank must not be invented as entries.
    assert(cmap.includes('<96> <2013>'),
      `${label}: ToUnicode ${i} maps byte 0x96 to U+2013, the en dash`);
    assert(!cmap.includes('<81>'), `${label}: ToUnicode ${i} leaves 0x81 undefined`);
    const entries = [...cmap.matchAll(/^<([0-9A-F]{2})> <([0-9A-F]{4})>$/gm)];
    assert.equal(entries.length, 218,
      `${label}: ToUnicode ${i} covers the 218 WinAnsi bytes, found ${entries.length}`);
  }

  // Exactly four compressed streams: two programs, two CMaps. Nothing else in
  // the file may hide behind a filter.
  assert.equal(streams.filter(x => x.dict.includes('/Filter')).length, 4,
    `${label}: four compressed streams, all of them font data`);
}

function validateStructure(pdf, label, minPages) {
  assert(Buffer.isBuffer(pdf), `${label}: renderPdf returns a Buffer`);
  const s = pdf.toString('latin1');

  assert(s.startsWith('%PDF-1.4\n'), `${label}: file starts with the PDF 1.4 magic`);
  assert(s.endsWith('%%EOF\n'), `${label}: file ends with the end-of-file marker line`);

  const startxref = s.match(/startxref\n(\d+)\n%%EOF\n$/);
  assert(startxref, `${label}: startxref present before EOF`);
  const xrefOffset = Number(startxref[1]);
  assert.equal(s.slice(xrefOffset, xrefOffset + 4), 'xref',
    `${label}: startxref offset points at the xref table`);

  const header = s.slice(xrefOffset).match(/^xref\n0 (\d+)\n/);
  assert(header, `${label}: xref subsection header present`);
  const slots = Number(header[1]);
  const entriesBase = xrefOffset + header[0].length;
  assert(s.startsWith('0000000000 65535 f \n', entriesBase),
    `${label}: free head entry occupies exactly 20 bytes`);

  for (let i = 1; i < slots; i++) {
    const entry = s.slice(entriesBase + i * 20, entriesBase + (i + 1) * 20);
    const m = entry.match(/^(\d{10}) (\d{5}) ([nf]) \n$/);
    assert(m, `${label}: xref entry ${i} is a 20-byte record: ${JSON.stringify(entry)}`);
    if (m[3] === 'n') {
      const offset = Number(m[1]);
      assert(s.startsWith(`${i} 0 obj\n`, offset),
        `${label}: xref entry ${i} offset ${offset} points at "${i} 0 obj"`);
    }
  }

  assert.equal((s.match(/^\d+ 0 obj\n/gm) || []).length, slots - 1,
    `${label}: exactly one object per xref slot`);
  assert(s.includes(`trailer\n<< /Size ${slots} /Root 1 0 R >>`),
    `${label}: trailer names size and root`);
  assert(s.includes('/MediaBox [0 0 595.28 841.89]'),
    `${label}: A4 portrait media box`);
  assert(s.includes('/Type /Catalog'), `${label}: document root object declared`);

  const pages = (s.match(/\/Type \/Page(?!s)/g) || []).length;
  assert(pages >= minPages, `${label}: at least ${minPages} page object(s), found ${pages}`);
  assert.equal(streamBodies(pdf).length, pages,
    `${label}: one uncompressed content stream per page`);

  assertEmbeddedFaces(s, label);

  for (const body of streamBodies(pdf)) {
    for (let i = 0; i < body.length; i++) {
      const code = body.charCodeAt(i);
      assert(code >= 32 || code === 10,
        `${label}: content streams carry no control bytes (found ${code})`);
    }
  }
  return s;
}

function assertLinesFit(pdf, label) {
  const lines = extractLines(pdf);
  assert(lines.length > 0, `${label}: extraction finds drawn lines`);
  for (const line of lines) {
    let box = CONTENT_W;
    if (line.x === MARGIN + LABEL_COL) box = CONTENT_W - LABEL_COL;
    else if (line.x === MARGIN && line.font === 'F2' && line.size === 10.5) box = LABEL_COL;
    const width = lineWidth(line.text, line.font, line.size);
    assert(width <= box + 0.01,
      `${label}: line fits its column (${width.toFixed(2)} > ${box}): ${line.text.slice(0, 48)}`);
  }
  return lines;
}

// --- fixture: enough element variety and length for >= 2 pages ---------------

const SENT_A = 'The committee reviewed the draft text clause by clause and noted each point for the record.';
const SENT_B = 'Delegates welcomed the clarification on procedure and asked the secretariat to circulate the revised version before the next meeting.';
const SENT_C = 'The secretariat will update the annex and circulate it to all participants once the corrections are approved.';
const SENT_D = 'Several delegations asked for a plain explanation of the timetable and for the supporting material in good time.';

const paragraphSeed = SENT_A + ' ' + SENT_B + ' ' + SENT_C + ' ' + SENT_D + ' ';
const longOne = paragraphSeed.repeat(8);
const longTwo = paragraphSeed.repeat(8);
const longThree = (SENT_B + ' ' + SENT_D + ' ' + SENT_A + ' ' + SENT_C + ' ').repeat(8);

const elements = [
  { type: 'banner', kind: 'title', text: 'Editorial Review Report' },
  { type: 'kv', label: 'Version', value: '9.9.9' },
  { type: 'kv', label: 'Date', value: '27 September 2026' },
  { type: 'spacer' },
  { type: 'paragraph', text: 'The phrase ‘smart’ – ok… appears in the draft.' },
  { type: 'paragraph', text: 'The quoted span a (b) c stays whole.' },
  { type: 'heading', level: 1, text: 'Findings by file' },
  { type: 'heading', level: 2, text: 'docs/draft-note.md' },
  { type: 'banner', kind: 'error', text: 'error · line 12:5' },
  { type: 'kv', label: 'Current', value: 'a (b) c' },
  { type: 'kv', label: 'Should be', value: 'a parenthetical in plain form' },
  { type: 'bullets', items: ['first bullet point', 'second bullet point'] },
  { type: 'rule' },
  { type: 'banner', kind: 'warning', text: 'warning · line 20:1' },
  { type: 'paragraph', text: longOne },
  { type: 'banner', kind: 'note', text: 'note · line 30:2' },
  { type: 'paragraph', text: longTwo },
  { type: 'heading', level: 1, text: 'Review queue' },
  { type: 'paragraph', text: longThree },
];

// --- 1-3: magic, xref, pages, fonts ------------------------------------------

const opts = { version: '9.9.9' };
const pdf = renderPdf(elements, opts);
const s = validateStructure(pdf, 'report', 2);

// Severity and banner colours exactly as the contract fixes them.
// Three of the six moved when the chrome went navy; each with its reason.
//   '0.216 0.278 0.31 rg' -> masthead: R7 makes the cover title banner the
//     same navy as every running page head, so the old slate is no longer
//     painted anywhere. The assertion that this exact slate appears was the
//     assertion that the old banner still existed.
//   '0.902 0.318 0 rg' -> R12 unified the warning hue with HTML's #e07b00;
//     the two renderers disagreed about the same severity mark, and severity
//     is a signal a reader has to recognise across formats.
//   '0 0 0 rg' -> R6 body text is #171b26, a very dark navy-tinted near-black
//     (17.20:1 on white) rather than pure black.
// Error, note and white are untouched and must still appear.
for (const colour of ['0.141 0.208 0.42 rg', '0.776 0.157 0.157 rg',
  '0.878 0.482 0 rg', '0.082 0.396 0.753 rg', '1 1 1 rg', '0.09 0.106 0.149 rg']) {
  assert(s.includes(colour), `fill colour "${colour}" appears in the streams`);
}
assert(s.includes('/F1 10.5 Tf'), 'body text renders at 10.5 pt');
assert(s.includes('/F2 16 Tf'), 'level 1 headings render at 16 pt bold');
assert(s.includes('/F2 13 Tf'), 'level 2 headings render at 13 pt bold');
assert(s.includes(' re f '), 'banners draw a filled rectangle');
assert(s.includes('0.5 w '), 'rules draw a half-point line');

// --- 4: extraction and transliteration ---------------------------------------

const lines = assertLinesFit(pdf, 'report');
const texts = lines.map((line) => line.text);
assert(texts.some((t) => t.includes('Editorial Review Report')),
  'title banner text round-trips through extraction');
assert(texts.some((t) => t.includes("'smart' \u0096 ok...")),
  'curly quotes and the ellipsis fold to ASCII; the en dash keeps WinAnsi byte 0x96');
assert(!texts.some((t) => t.includes("'smart' - ok...")),
  'the en dash must never fold to a plain hyphen (that hid UE-NU002\u2019s defect)');
assert(!pdf.includes(Buffer.from('‘', 'utf8')), 'no raw left quote bytes in the file');
assert(!texts.some((t) => /[‘’“”–—…]/.test(t)),
  'no typographic character survives in any extracted line');
assert(texts.some((t) => t.startsWith('• ') || t.startsWith('\u0095 ')),
  'bullet items render with the WinAnsi bullet glyph');
assert(lines.some((line) => line.x === MARGIN + LABEL_COL),
  'key-value values start in the 84 pt label column');

// --- 5: literal-string escaping round-trips ---------------------------------

assert(texts.some((t) => t.includes('a (b) c')),
  'a paragraph containing "a (b) c" extracts back unchanged');
assert(s.includes('a \\(b\\) c'), 'parentheses are escaped inside the raw literal');

// --- 6: header and footer on every page --------------------------------------
//
// Both are drawn from lib/furniture.mjs: the header block — two rows of two
// cells, the tool and its version against EDITORIAL REVIEW, then the document
// symbol and date against the distribution marking — at the top of every page,
// and the three footer cells — page position, copyright, repository address —
// at the bottom of every page (decisions D2 and D3). Each cell is its own
// drawn run in stream order, so the deepEqual below is the lock: remove any
// cell, or the furniture function behind it, and it fails.

// The header is derived from the cover's own kv rows when the caller holds no
// explicit `opts.input`: the date from the Date row, and the version from the
// renderer's own argument. Targets are cover material and no longer reach the
// repeating header at all.
const HEADER_INPUT = { date: '27 September 2026', targets: [], version: '9.9.9' };
/** A header row with whitespace collapsed, as the `{ left, right }` it is. */
const headerRowOf = (row) => ({ left: squash(row.left), right: squash(row.right) });
const expectedHeader = headerRows(HEADER_INPUT, '9.9.9').map(headerRowOf);
assert.equal(expectedHeader[0].right, 'EDITORIAL REVIEW',
  'the header reads EDITORIAL REVIEW — the endorsement boundary, restated here');
assert.equal(expectedHeader[0].left, 'un-editorial-check 9.9.9',
  'the header leads with the tool and its version (decision D2)');
assert.equal(expectedHeader[1].right, 'Distribution: General',
  'the distribution marking sits opposite the document symbol');

/** The four header runs a page opens with, in the order they are drawn. */
const EXPECTED_HEADER_CELLS = [
  expectedHeader[0].left, expectedHeader[0].right,
  expectedHeader[1].left, expectedHeader[1].right,
];

const pageArr = pageLines(pdf);
assert(pageArr.length >= 2, `fixture renders at least two pages, got ${pageArr.length}`);
pageArr.forEach((ls, i) => {
  // The footer is one row of three cells (decision D3), drawn last, in stream
  // order, all on the same baseline below the content box.
  const cells = footerCells({ date: HEADER_INPUT.date, page: i + 1, pages: pageArr.length });
  assert.deepEqual(ls.slice(-3).map((l) => l.text),
    [cells.left, cells.centre, cells.right],
    `page ${i + 1} carries its three footer cells verbatim`);
  // The literal n/m stamp, quoted rather than derived from footerCells: the
  // deepEqual above follows footerCells wherever it goes — this one does not,
  // so a footer that stamped a wrong total would fail here too.
  assert.equal(ls.slice(-3)[0].text, `Page ${i + 1} of ${pageArr.length}`,
    `page ${i + 1} footer stamps its own n/m page number`);
  for (const l of ls.slice(-3)) {
    assert.equal(l.font, 'F1', `footer cell is regular: ${l.text}`);
    assert.equal(l.size, 7.5, `footer cell is 7.5 pt: ${l.text}`);
    assert(l.y < MARGIN, `footer sits below the content box: ${l.text} at y=${l.y}`);
  }
  // The three cells must read as columns rather than as one centred pile: their
  // x positions strictly increase, so no cell can be drawn over the one before
  // it however long the copyright or the repository address becomes.
  const footerCellsDrawn = ls.slice(-3);
  assert(footerCellsDrawn[0].x < footerCellsDrawn[1].x
    && footerCellsDrawn[1].x < footerCellsDrawn[2].x,
    `page ${i + 1} footer cells are placed left, centre and right`);

  const head = ls.slice(0, 4);
  assert.deepEqual(head.map((l) => squash(l.text)), EXPECTED_HEADER_CELLS,
    `page ${i + 1} carries the two header rows, cell by cell`);
  head.forEach((l, j) => {
    const row = j < 2 ? 1 : 2;
    assert.equal(l.font, row === 1 ? 'F2' : 'F1', `header row ${row} font on page ${i + 1}`);
    assert.equal(l.size, row === 1 ? 9 : 8.5, `header row ${row} size on page ${i + 1}`);
    if (j % 2 === 0) {
      assert.equal(l.x, MARGIN, `header row ${row} left cell starts in the margin on page ${i + 1}`);
    } else {
      assert(l.x > MARGIN, `header row ${row} right cell is not sitting on the left margin on page ${i + 1}`);
    }
  });
  assert.equal(head[3].text, 'Distribution: General',
    'the header carries the distribution marking');
});
assert(s.includes('Page 1 of '), 'page 1 footer stamp present');
assert(s.includes('Page 2 of '), 'page 2 footer stamp present');
assert(s.includes('EDITORIAL REVIEW'), 'the header text is present in the file');
assert(!s.includes('UNITED NATIONS'),
  'the endorsement boundary: the report never prints UNITED NATIONS');
// The framing disclaimer leads the body, directly under the title banner,
// before any heading, kv row or finding.
assert(lines[5].text.startsWith('The report never presents itself as verification of facts'),
  'the framing disclaimer still leads the report body');

// --- 7: one unbroken 600-character token -------------------------------------

const stress = renderPdf([
  { type: 'paragraph', text: 'A long token follows: ' + 'x'.repeat(600) + ' end of line.' },
], opts);
validateStructure(stress, 'stress', 1);
const stressLines = assertLinesFit(stress, 'stress');
assert(stressLines.map((line) => line.text).join('').includes('x'.repeat(600)),
  'the long token survives extraction intact across the cut lines');

// --- 8: determinism ----------------------------------------------------------

assert.equal(Buffer.compare(renderPdf(elements, opts), pdf), 0,
  'the same input renders a byte-identical Buffer');

// --- extras: unknown types and the default version --------------------------

assert.throws(() => renderPdf([{ type: 'mystery' }]), /unknown element type/,
  'an unknown element type is rejected with the contract error');

const bare = renderPdf([{ type: 'paragraph', text: 'A short closing line.' }]);
validateStructure(bare, 'bare', 1);
{
  // An input with no date still produces a well-formed three-cell footer. The
  // year is dropped rather than guessed, so a report that cannot source a year
  // prints a copyright without one instead of reaching for the host clock.
  const bareCells = footerCells({ page: 1, pages: 1 });
  const bareLast = pageLines(bare)[0].slice(-3).map((l) => l.text);
  assert.deepEqual(bareLast, [bareCells.left, bareCells.centre, bareCells.right],
    'an input with no date still produces a well-formed footer');
  assert.equal(bareLast[1], '© un-editorial-check contributors',
    'a date with no four-digit year drops the year rather than inventing one');
}

// --- 9: characters WinAnsi cannot encode -------------------------------------
//
// WinAnsi is single-byte: a Cyrillic, Arabic or Han character has no code in
// it, and neither does the embedded subset — it keeps only the glyphs those
// 218 reachable bytes name. Those characters are therefore replaced by "?".
// That is a real, lossy fold, and these locks pin it exactly and make the loss
// visible rather than silent:
//
//   * the fold is per character, deterministic, and idempotent;
//   * Greek and Cyrillic, which WinAnsi *does* cover, are never folded — the
//     fold is about the encoding, not about "not English";
//   * a report that needed the fold says so in a closing note, and a report
//     that did not carries no note and not one extra byte;
//   * the documented cost is stated rather than hidden: two names differing
//     only in an unrepresentable character print alike.

{
  // The fold predicate is restated here rather than imported, so the test
  // cannot be satisfied by a change to the module under test: it asserts what
  // WinAnsi can and cannot encode, from the encoding, not from lib/pdf.mjs.
  // WinAnsi (PDF Annex D) is code page 1252: ASCII, the C1 range 0x80-0x9F
  // with its typographic specials, and Latin-1 0xA0-0xFF. Nothing else.
  const WINANSI_UNICODE = new Set([
    0x20AC, 0x201A, 0x0192, 0x201E, 0x2020, 0x2021, 0x02C6, 0x2030,
    0x0160, 0x2039, 0x0152, 0x017D, 0x2022, 0x02DC, 0x2122, 0x0161,
    0x203A, 0x0153, 0x017E, 0x0178, 0x2013, 0x2014,
  ]);
  const unrepresentable = (cp) => {
    if (cp >= 0x20 && cp <= 0x7E) return false;
    if (cp >= 0xA0 && cp <= 0xFF) return false;
    if (cp === 0x96 || cp === 0x97) return false; // the WinAnsi dashes
    if (WINANSI_UNICODE.has(cp)) return false;
    return true;
  };
  const folds = (value) => [...value].filter(ch => unrepresentable(ch.codePointAt(0))).length;
  const fold = (value) => '?'.repeat(folds(value));

  // The documented cost, stated rather than glossed: Turkish is a Latin script
  // in everyday UN use, and WinAnsi cannot spell it. The fold turns the dotted
  // and dotless i into "?", so a Turkish title loses two characters. This is
  // the case the closing note exists for, and it is asserted here so the
  // limitation is a measured one rather than an assumption.
  assert.equal(folds('Yıllık'), 2, 'Turkish dotless i is outside WinAnsi: two characters fold');
  assert.equal(folds('Yillik'), 0, 'its ASCII spelling is inside WinAnsi and survives');

  // Western European copy is inside the encoding and must survive untouched,
  // accented letters included. This is the case that must not regress: a fold
  // keyed on "not plain ASCII" would mangle every accented name in a report.
  for (const [name, value] of [
    ['French', 'Rapport sur la sécurité'],
    ['German', 'Jahresbericht für Europa'],
    ['Spanish', 'Informe sobre medidas'],
    ['Portuguese', 'Relatório anual'],
    ['Nordic', 'Årsrapport för säkerhet'],
    ['Polish', 'Raport roczny'],
    // Turkish dotted/dotless i is a genuine WinAnsi gap: U+0131 and U+0130
    // are in Latin-1, but U+0069/U+0067 do not spell Turkish, and the report
    // says so in the note rather than pretending the fold is rare.
    ['Romanian', 'Raport anual privind securitatea'],
  ]) {
    assert.equal(folds(value), 0, `${name} prose is inside WinAnsi and must not be folded`);
  }
  assert.equal(folds('€ · ƒ † ‰ ½ × ÿ'), 0,
    'the WinAnsi C1 specials are representable and must not be folded');

  // Every other script is outside it. The list is what the fold is *for*, and
  // it is why a non-Latin file name is a real case rather than a hypothetical.
  for (const [name, value] of [
    ['Greek', 'Έκθεση'],
    ['Cyrillic', 'документ'],
    ['Arabic', 'تقرير'],
    ['Hebrew', 'דוח'],
    ['Han', '报告'],
    ['Devanagari', 'रिपोर्ट'],
    ['Thai', 'รายงาน'],
    ['Armenian', 'հաշվետ'],
    ['Georgian', 'ანგარიში'],
    ['emoji', '\u{1f4c8}'],
  ]) {
    assert.equal(folds(value), [...value].length,
      `${name} is outside WinAnsi, so every character folds`);
  }

  // The en and em dash keep their bytes rather than folding, even though they
  // are outside ASCII: WinAnsi encodes them at 0x96 and 0x97.
  assert.equal(folds('–'), 0, 'the en dash keeps its WinAnsi byte');
  assert.equal(folds('—'), 0, 'the em dash keeps its WinAnsi byte');
  // The soft hyphen is dropped rather than folded, and is not a "?" either.
  assert.equal(folds('­'), 0, 'the soft hyphen is dropped, not folded');

  const rendered = renderPdf([
    { type: 'kv', label: 'Targets', value: '/tmp/report/تقرير.txt' },
    { type: 'kv', label: 'Accented', value: 'Rapport sur la sécurité' },
    { type: 'kv', label: 'Greek', value: 'Έκθεση στην Αθήνα' },
    { type: 'kv', label: 'Han', value: '报告草稿' },
    { type: 'kv', label: 'Emoji', value: '\u{1f4c8} report' },
  ], opts);
  validateStructure(rendered, 'folded', 1);
  const text = assertLinesFit(rendered, 'folded').map(line => line.text).join('\n');

  assert(text.includes(`/tmp/report/${fold('تقرير')}.txt`),
    'an unrepresentable file name folds to one question mark per character');
  assert(text.includes('Rapport sur la sécurité'),
    'accented Western European copy must survive the fold intact');
  // Word wrapping collapses whitespace, so a folded phrase is one question mark
  // per character with single spaces where the words were.
  const foldWords = (value) => value.split(/\s+/).map(fold).join(' ');
  assert(text.includes(foldWords('Έκθεση στην Αθήνα')),
    'Greek folds character by character');
  assert(text.includes(fold('报告草稿')), 'Han folds character by character');
  assert(text.includes(fold('\u{1f4c8}') + ' report'),
    'a code point beyond the basic plane folds once, not once per surrogate half');

  // The fold is announced, never silent: a "?" in a file name is otherwise
  // indistinguishable from a "?" in the copy.
  assert(text.includes('Note on characters:'),
    'a report that folded a character must say so');
  assert(text.includes('may be a character the font cannot draw'),
    'the note must state that a question mark may be a folded character');

  // A report that folded nothing carries no note and not one extra byte, so
  // the change is invisible to every document written in a covered script —
  // which is the overwhelming majority, including all Latin-script copy.
  const noFold = renderPdf([{ type: 'paragraph', text: 'A short closing line.' }]);
  assert(!assertLinesFit(noFold, 'nofold').map(l => l.text).join('\n')
    .includes('Note on characters'),
  'a report that folded nothing must not carry the note');
  assert.equal(Buffer.compare(noFold, bare), 0,
    'the fold note must not change one byte of a report that needed no fold');
  const accentedOnly = [{ type: 'paragraph', text: 'Rapport sur la sécurité, à Genève.' }];
  assert.equal(Buffer.compare(renderPdf(accentedOnly, opts), renderPdf(accentedOnly, opts)), 0,
    'an accented-only report needs no note and stays deterministic');
  assert(!assertLinesFit(renderPdf(accentedOnly, opts), 'accented').map(l => l.text)
    .join('\n').includes('Note on characters'),
  'accented Western European copy must not trigger the fold note');

  // Moved with Stage D's fold-gate change, and the reason it exists: the gate
  // no longer asks "does this string hold a character outside WinAnsi?" but
  // "does any character actually *become* '?' on the page?". The two disagree
  // exactly on the folds that go somewhere other than "?": the curly quotes
  // fold to their ASCII forms and the ellipsis to three periods, so under the
  // old predicate a report containing only them carried a note promising that
  // some characters had been lost — naming characters that were not. Nothing
  // here became "?", so nothing here is announced. The en and em dash are in
  // the same sentence because they keep their WinAnsi bytes and must not be
  // read as a loss either. All seven code points the gate must forgive —
  // ‘ ’ “ ” – — … — sit in this one sentence (the
  // single quotes added with F11, whose lock spec names them beside the
  // double ones), so a gate that asks the encoding instead of asking what
  // became of the character trips over every one of them:
  // lib/winansi.mjs's hasUnrepresentable answers "yes" for all seven while
  // toWinAnsi maps each to a plain byte.
  const foldFree = [{ type: 'paragraph', text: 'The range 1990–2025 — set and '
    + '“quoted”, with ‘single’ quotes — stands. Ellipsis … too.' }];
  assert(!assertLinesFit(renderPdf(foldFree, opts), 'foldfree').map(l => l.text)
    .join('\n').includes('Note on characters'),
  'smart quotes, the ellipsis and dashes fold without a note: none of them became "?"');

  // Determinism holds on the folded path too.
  const twice = [
    { type: 'kv', label: 'Targets', value: '/tmp/report/تقرير.txt' },
    { type: 'kv', label: 'Han', value: '报告草稿' },
  ];
  assert.equal(Buffer.compare(renderPdf(twice, opts), renderPdf(twice, opts)), 0,
    'the folded path is deterministic like every other');
}

// --- 10: Phase 9 — opts.input header, the issue block, the legend,
//           and the endorsement boundary --------------------------------------
//
// The guarantees this phase added, each asserted so it fails when removed:
// the header draws from furniture.mjs (opts.input verbatim), every issue
// carries all six provenance rows in order, a count is shown only above one,
// the structured Occurrences list wraps inside the value column, the legend
// lists exactly thirteen categories with the category name as the text label
// beside its marker, and the report never prints UNITED NATIONS.

// The legend's four columns, read positionally from the slice between the
// `Categories` heading and the next level-1 heading: the category name
// (the text label, so colour and shape are never the only signal), the short
// code inside its swatch, what the category covers, and the count cell.
function legendSlice(lines) {
  const start = lines.findIndex(l =>
    l.text === 'Categories' && l.font === 'F2' && l.size === 16 && l.x === MARGIN);
  assert(start >= 0, 'the category legend heading is present');
  const end = lines.findIndex((l, j) =>
    j > start && l.font === 'F2' && l.size === 16 && l.x === MARGIN);
  return lines.slice(start + 1, end === -1 ? lines.length : end);
}

function legendFields(lines) {
  const region = legendSlice(lines);
  return {
    // D11 moved both columns: the category's artwork now leads the row at the
    // content margin, so the swatch sits at 65 and the name at 95 — read
    // positionally, so an icon that pushed them back would fail here.
    names: region.filter(l => l.font === 'F2' && l.size === 10.5 && l.x === 95)
      .map(l => l.text),
    codes: region.filter(l => l.font === 'F2' && l.size === 8 && l.x > 65 && l.x < 91)
      .map(l => l.text),
    intents: region.filter(l => l.font === 'F1' && l.size === 9 && l.x === 200)
      .map(l => l.text),
    counts: region.filter(l => l.font === 'F1' && l.size === 9 && l.x > 400
      && /^\d+$/.test(l.text)).map(l => Number(l.text)),
  };
}

// A marker swatch in the content stream: `rgb rg 54 y 26 11 re f Q`. The
// expected colour is computed here from the hex with an independent
// expression (`byte * 1000 / 255`, rounded), so a change to lib/pdf.mjs's
// rgbFill cannot satisfy this test by construction.
function hexToRgb(hex) {
  const byte = (i) => parseInt(hex.slice(1 + i * 2, 3 + i * 2), 16);
  return [0, 1, 2].map(i => String(Math.round(byte(i) * 1000 / 255) / 1000)).join(' ');
}

// All six provenance rows on one issue, in contract order, bounded by the
// issue's own block (its banner to the next banner) so a row missing from
// this issue cannot be satisfied by the next issue's copy of it.
function assertProvenance(lines, bannerText, expected) {
  const start = lines.findIndex(l =>
    l.text === bannerText && l.font === 'F2' && l.size === 11);
  assert(start >= 0, `the issue banner is drawn: ${bannerText}`);
  const next = lines.findIndex((l, j) =>
    j > start && l.font === 'F2' && l.size === 11 && l.text.startsWith('['));
  const end = next === -1 ? lines.length : next;
  let cursor = start;
  for (const [label, value] of expected) {
    const idx = lines.findIndex((l, j) => j > cursor && j < end
      && l.text === label && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
    assert(idx > cursor && idx < end,
      `issue ${bannerText} carries the ${label} row, after the rows before it`);
    const parts = [];
    for (let k = idx + 1; k < lines.length
      && lines[k].x === MARGIN + LABEL_COL && lines[k].font === 'F1'
      && lines[k].size === 10.5; k++) {
      parts.push(lines[k].text);
    }
    assert.equal(squash(parts.join(' ')), squash(value),
      `${label} on ${bannerText} prints its value`);
    cursor = idx;
  }
}

// opts.input feeds the header and the footer verbatim: a caller that holds the
// real report input gets its date and document symbol in the header and its
// year in the footer's copyright, while the version in the header's first cell
// is still the renderer's own argument rather than the one the input carries.
{
  const overrideInput = { date: '2026-01-02', targets: ['/tmp/a.md', '/tmp/b.md'], version: '1.2.3' };
  const override = renderPdf([{ type: 'paragraph', text: 'Body.' }],
    { version: '9.9.9', input: overrideInput });
  validateStructure(override, 'override', 1);
  const overrideLines = assertLinesFit(override, 'override');
  const expectedOverride = headerRows(overrideInput, '9.9.9').map(headerRowOf);
  assert.deepEqual(overrideLines.slice(0, 4).map(l => squash(l.text)), [
    expectedOverride[0].left, expectedOverride[0].right,
    expectedOverride[1].left, expectedOverride[1].right,
  ], 'opts.input feeds headerRows exactly — symbol and date cell included');
  assert.equal(overrideLines[0].text, 'un-editorial-check 9.9.9',
    'the header leads with the renderer version, not the one opts.input carries');
  assert.match(overrideLines[2].text, /^Document symbol: UE\/2026\/\d{4} · 2 January 2026$/,
    'the header stamps the date opts.input carries');
  assert(overrideLines.slice(0, 4).every(l => !l.text.includes('/tmp/')),
    'targets are cover material and no longer repeat in the header');
  const overrideFooter = footerCells({ date: overrideInput.date, page: 1, pages: 1 });
  assert.deepEqual(pageLines(override)[0].slice(-3).map(l => l.text),
    [overrideFooter.left, overrideFooter.centre, overrideFooter.right],
    'the footer copyright reads its year from the opts.input date');
}

// A grouped-detail document: one issue of seven occurrences and one lone
// heuristic issue of a single occurrence — the two shapes the renderer must
// tell apart, with all six provenance rows on each. Every string is ASCII on
// purpose: this document must carry no fold note, and the Han-path document
// below is the one that must.
const issue7 = {
  type: 'issue', kind: 'warning',
  text: '[WARNING] UE-NU002 · numerals · deterministic',
  ruleId: 'UE-NU002', category: 'numerals', confidence: 'deterministic',
  severity: 'warning', lane: 'deterministic',
  marker: 'NU', colour: '#2e8b57', count: 7,
  current: '1990-2025', should: '1990-2025 - --fix-able',
  message: 'Numeric range "1990-2025" uses a hyphen.',
  audit: null, heuristic: false,
  provenance: [
    { label: 'Lane', value: 'deterministic' },
    { label: 'Source', value: 'rules/numerals.md' },
    { label: 'Profile', value: 'editorial baseline' },
    { label: 'Confidence', value: 'deterministic' },
    { label: 'Limitation', value: 'Deterministic match on extracted copy; quoted, cited and code spans are outside the scan.' },
    { label: 'Action', value: 'Editorial correction; verify in context before applying.' },
  ],
  occurrences: [
    { file: 'reports/sample.md', line: 1, column: 11, pdfPage: 3, content: 'The range 1990-2025 was set.', should: 'The range 1990-2025 was set.' },
    { file: 'reports/sample.md', line: 2, column: 11, content: 'The range 1990-2025 was noted.', should: 'The range 1990-2025 was noted.' },
    { file: 'reports/sample.md', line: 3, column: 11, content: 'The range 1990-2025 was recorded.', should: 'The range 1990-2025 was recorded.' },
    { file: 'reports/sample.md', line: 4, column: 11, content: 'The range 1990-2025 was confirmed.', should: 'The range 1990-2025 was confirmed.' },
    { file: 'reports/sample.md', line: 5, column: 11, content: 'The range 1990-2025 was extended.', should: 'The range 1990-2025 was extended.' },
    { file: 'reports/sample.md', line: 6, column: 11, content: 'The range 1990-2025 was shortened.', should: 'The range 1990-2025 was shortened.' },
    { file: 'reports/sample.md', line: 7, column: 11, content: 'The range 1990-2025 was repeated in a deliberately long excerpt line that runs past the value column so the renderer must wrap it inside the measure rather than overrunning the page edge.', should: 'The range 1990-2025 was repeated.' },
  ],
};
const issue1 = {
  type: 'issue', kind: 'note',
  text: '[NOTE] UE-AR001 · agent-review · audit · line 9:3',
  ruleId: 'UE-AR001', category: 'agent-review', confidence: 'heuristic',
  severity: 'info', lane: 'heuristic-review',
  marker: 'AR', colour: '#b8860b', count: 1,
  current: 'top-notch facilities', should: 'excellent facilities',
  message: 'Promotional tone.', audit: 'glossary', heuristic: true,
  provenance: [
    { label: 'Lane', value: 'heuristic-review' },
    { label: 'Source', value: 'config/profiles/glossary.json' },
    { label: 'Profile', value: 'glossary' },
    { label: 'Confidence', value: 'heuristic' },
    { label: 'Limitation', value: 'Routed to review; this report never asserts that a claim is true or false.' },
    { label: 'Action', value: 'Confirm with the author before applying.' },
  ],
  occurrences: [
    { file: 'reports/sample.md', line: 9, column: 3, content: 'top-notch facilities', should: 'excellent facilities' },
  ],
};
const issueElements = [
  { type: 'banner', kind: 'title', text: 'Editorial Review Report' },
  { type: 'kv', label: 'Version', value: '9.9.9' },
  { type: 'kv', label: 'Date', value: '2026-09-29' },
  { type: 'kv', label: 'Targets', value: 'reports/sample.md' },
  { type: 'heading', level: 1, text: 'Issues' },
  issue7,
  issue1,
];
const issuePdf = renderPdf(issueElements, opts);
const issueS = validateStructure(issuePdf, 'issue', 1);
const issueLines = assertLinesFit(issuePdf, 'issue');
const issueTexts = issueLines.map(l => l.text);

// The banner: a group of several carries the shared fields and no location
// (the model omits it when count > 1), a lone finding carries line:column.
assert(issueTexts.includes('[WARNING] UE-NU002 · numerals · deterministic'),
  'the multi-occurrence banner prints no location');
assert(!issueTexts.some(t => t.startsWith('[WARNING] UE-NU002') && t.includes(' · line ')),
  'a grouped banner never invents a location the model left out');
assert(issueTexts.includes('[NOTE] UE-AR001 · agent-review · audit · line 9:3'),
  'a lone finding carries its line and column on the banner');

// The marker row: the category name is the text label beside the code
// swatch — colour and shape are never the only signal. Since D11 the row
// leads with two drawn marks, so the swatch starts at 76 and the name at
// 108; both are read from the content stream, so an icon that displaced them
// or a name that vanished would fail here.
assert(issueLines.some(l => l.text === 'numerals' && l.font === 'F2'
  && l.size === 10.5 && l.x === 108),
  'the issue marker row prints the category name as its text label');
assert(issueLines.some(l => l.text === 'NU' && l.font === 'F2' && l.size === 8
  && l.x > 76 && l.x < 102),
  'the issue marker row prints the short code inside its swatch');
assert(issueLines.some(l => l.text === 'agent-review' && l.font === 'F2'
  && l.size === 10.5 && l.x === 108),
  'the lone issue prints its category name too');

// D11: the mark beside a row is *that row's* mark. The artwork is selected by
// severity and by category, so the only way this can go wrong is the renderer
// picking the wrong one — and that is invisible to every count in this file:
// a document where every row wore the spelling icon has exactly as many marks
// as one drawn correctly. The expected block is rebuilt here from the icon
// table at the placement the row gives it — the content margin for the
// severity mark, twelve points in for the category mark, nine points tall, on
// the row's own baseline, which is where `drawIssue` puts them — so a mark
// borrowed from another row, drawn for the wrong severity, or moved off the
// row fails outright.
const markAt = (shapes, x, y) => pdfIcon(shapes, { x, y, size: 9 });
const markerLine = (text) => {
  const line = issueLines.find((l) => l.text === text && l.x === 108);
  assert(line, `the issue row names its category: ${text}`);
  return line.y;
};
const issueMarks = [
  { category: 'numerals', severity: 'warning' },
  { category: 'agent-review', severity: 'note' },
];
for (const { category, severity } of issueMarks) {
  const y = markerLine(category);
  assert(issueS.includes(markAt(categoryIcon(category), 65, y)),
    `the ${category} issue wears the ${category} category mark, not a neighbour's`);
  assert(issueS.includes(markAt(severityIcon(severity), 54, y)),
    `the ${category} issue wears the ${severity} severity mark, not a neighbour's`);
}

// The same in the legend: each of the twelve rows teaches the mark the finding
// rows use, keyed by the category the row itself names. The name sits at the
// category column, and the mark leads it at the content margin.
for (const entry of CATEGORY_LEGEND) {
  const line = issueLines.find((l) => l.text === entry.category && l.x === 95);
  assert(line, `the legend names its category: ${entry.category}`);
  assert(issueS.includes(markAt(categoryIcon(entry.category), 54, line.y)),
    `legend row ${entry.code} wears the ${entry.category} mark it names`);
}

// A count is shown only when it is greater than one.
const countRow = issueLines.filter(l => /^\d+ occurrences$/.test(l.text));
assert.equal(countRow.length, 1, 'exactly one count marker in the document');
assert.equal(countRow[0].text, '7 occurrences', 'the count is the group size');
assert.equal(countRow[0].font, 'F1', 'the count sits in the regular weight');
assert.equal(countRow[0].size, 10.5, 'the count sits at body size');
assert(countRow[0].x > 400, 'the count is right-aligned in the marker row');
assert(!issueTexts.some(t => t === '1 occurrences' || t === '1 occurrence'),
  'a group of one shows no count at all');

// All six provenance rows, in contract order, on both issues.
const provenance7 = [
  ['Lane', 'deterministic'], ['Source', 'rules/numerals.md'],
  ['Profile', 'editorial baseline'], ['Confidence', 'deterministic'],
  ['Limitation', 'Deterministic match on extracted copy; quoted, cited and code spans are outside the scan.'],
  ['Action', 'Editorial correction; verify in context before applying.'],
];
const provenance1 = [
  ['Lane', 'heuristic-review'], ['Source', 'config/profiles/glossary.json'],
  ['Profile', 'glossary'], ['Confidence', 'heuristic'],
  ['Limitation', 'Routed to review; this report never asserts that a claim is true or false.'],
  ['Action', 'Confirm with the author before applying.'],
];
assertProvenance(issueLines, '[WARNING] UE-NU002 · numerals · deterministic', provenance7);
assertProvenance(issueLines, '[NOTE] UE-AR001 · agent-review · audit · line 9:3', provenance1);

// The Occurrences list is a structured list of rows, never a table: one
// heading per issue, one File row per occurrence, positions in order with
// the source page marked only where the finding came from a PDF.
const occHeadings = issueLines.filter(l => l.text === 'Occurrences'
  && l.font === 'F2' && l.size === 13 && l.x === MARGIN);
assert.equal(occHeadings.length, 2, 'each issue draws its own Occurrences heading');
const fileRows = issueLines.filter(l => l.text === 'File'
  && l.font === 'F2' && l.size === 10.5 && l.x === MARGIN);
assert.equal(fileRows.length, 8, 'one File row per occurrence: seven plus one');
const locationValues = [];
for (let i = 0; i < issueLines.length; i++) {
  const l = issueLines[i];
  if (l.text === 'Location' && l.font === 'F2' && l.size === 10.5 && l.x === MARGIN) {
    locationValues.push(kvValueAll(issueLines, 'Location', i));
  }
}
const expectedLocations = issue7.occurrences.map(o =>
  o.pdfPage != null ? `${o.line}:${o.column} · page ${o.pdfPage}` : `${o.line}:${o.column}`
).concat(issue1.occurrences.map(o => `${o.line}:${o.column}`));
assert.deepEqual(locationValues, expectedLocations,
  'every occurrence prints its position; only a PDF-derived one carries a page');
assert.equal(locationValues.filter(t => t.includes(' · page ')).length, 1,
  'exactly one occurrence carries its source page');
// The first occurrence block, in list order: File, Location, Content,
// Should be — the same four columns the HTML table draws.
let rowCursor = occHeadings.length
  ? issueLines.findIndex(l => l.text === 'Occurrences' && l.font === 'F2')
  : -1;
for (const label of ['File', 'Location', 'Content', 'Should be']) {
  const idx = issueLines.findIndex((l, j) => j > rowCursor
    && l.text === label && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
  assert(idx > rowCursor, `the occurrence block carries a ${label} row in order`);
  rowCursor = idx;
}
// The long excerpt wraps inside the value column and rejoins byte-identical:
// assertLinesFit already proved no line leaves the measure.
const contentLabels = [];
for (let i = 0; i < issueLines.length; i++) {
  const l = issueLines[i];
  if (l.text === 'Content' && l.font === 'F2' && l.size === 10.5 && l.x === MARGIN) {
    contentLabels.push(i);
  }
}
assert.equal(contentLabels.length, 8, 'one Content row per occurrence');
const longContentStart = contentLabels[6];
assert.equal(issueLines[longContentStart + 2].x, MARGIN + LABEL_COL,
  'the long excerpt wraps to a continuation line inside the value column');
assert.equal(kvValueAll(issueLines, 'Content', longContentStart),
  squash(issue7.occurrences[6].content),
  'the wrapped excerpt rejoins to exactly the copy it was drawn from');

// The legend: exactly thirteen categories, each with its name as the text
// label beside its marker, its code, its intent and its count.
const issueLegend = legendFields(issueLines);
assert.equal(issueTexts.filter(t => t === 'Categories').length, 1,
  'exactly one legend is drawn');
const issuesHeadingAt = issueLines.findIndex(l => l.text === 'Issues'
  && l.font === 'F2' && l.size === 16);
assert(issuesHeadingAt > issueLines.findIndex(l => l.text === 'Categories'
  && l.font === 'F2' && l.size === 16),
  'the legend is drawn before the findings section');
assert.deepEqual(issueLegend.names, CATEGORY_LEGEND.map(e => e.category),
  'the legend lists exactly the twelve categories by name, in catalogue order');
assert.equal(issueLegend.names.length, 13, 'thirteen category names (twelve catalogue categories plus organisation)');
assert.deepEqual(issueLegend.codes, CATEGORY_LEGEND.map(e => e.code),
  'each legend row prints its short code');
assert(issueLegend.codes.every(code => /^[A-Z]{2}$/.test(code)),
  'markers are two-letter text codes — no icon glyphs, no emoji');
assert.deepEqual(issueLegend.intents, CATEGORY_LEGEND.map(e => e.intent),
  'each legend row says what the category covers');
const expectedLegendCounts = legendRows(
  Array.from({ length: 7 }, () => ({ category: 'numerals' }))
    .concat({ category: 'agent-review' }),
).map(r => r.count);
assert.deepEqual(issueLegend.counts, expectedLegendCounts,
  'legend counts are the findings per category, zero rows included');
assert.equal(issueLegend.counts.length, 13, 'thirteen count cells');
assert.equal(issueLegend.counts.reduce((a, b) => a + b, 0),
  issue7.occurrences.length + issue1.occurrences.length,
  'the legend rows sum to the findings behind them — never to issue.count');

// The swatches: twelve legend colours in catalogue order, then one marker
// swatch per issue, each computed independently from the category hex. The
// x position is part of the lock since D11: both columns now lead with the
// category's artwork, so the legend's swatch sits at 54+9+2 and the issue
// row's at 54+9+11+2 — a swatch that crept back to the content margin would
// have to be drawn over the icon to get there.
const SWATCH_X = MARGIN;
const LEGEND_SWATCH_X = SWATCH_X + 9 + 2;
const ISSUE_SWATCH_X = SWATCH_X + 9 + 11 + 2;
const legendSwatches = [...issueS.matchAll(
  new RegExp(`q ([0-9.]+ [0-9.]+ [0-9.]+) rg ${LEGEND_SWATCH_X} [0-9.]+ 26 11 re f Q`, 'g'))]
  .map(m => m[1]);
const issueSwatches = [...issueS.matchAll(
  new RegExp(`q ([0-9.]+ [0-9.]+ [0-9.]+) rg ${ISSUE_SWATCH_X} [0-9.]+ 26 11 re f Q`, 'g'))]
  .map(m => m[1]);
assert.equal(legendSwatches.length, 13, 'thirteen legend swatches, each beside its icon');
assert.equal(issueSwatches.length, 2, 'one marker swatch per issue, each beside its icon');
assert.deepEqual(legendSwatches, CATEGORY_LEGEND.map(e => hexToRgb(e.colour)),
  'each legend swatch carries its category colour, computed independently');
assert.deepEqual(issueSwatches, [hexToRgb('#2e8b57'), hexToRgb('#b8860b')],
  'each issue marker swatch carries its category colour');

// The endorsement boundary on a findings-carrying report, and the guard note
// that must lead it.
assert(issueS.includes('EDITORIAL REVIEW'), 'the header text is present');
assert(!issueS.includes('UNITED NATIONS'),
  'the endorsement boundary: a report carrying findings never prints UNITED NATIONS');
assert(issueTexts[5].startsWith('The report never presents itself as verification of facts'),
  'the framing disclaimer still leads the issue report');

// The fold on the grouped path: an occurrence whose file name needs the fold
// announces it, and an all-ASCII issue report carries no note.
assert(!issueTexts.some(t => t.includes('Note on characters:')),
  'an all-ASCII issue report carries no fold note');
const hanPdf = renderPdf([
  { type: 'heading', level: 1, text: 'Issues' },
  {
    ...issue7, count: 1,
    occurrences: [{ file: '/tmp/报告.txt', line: 1, column: 1, content: '报告', should: '报告' }],
  },
], opts);
validateStructure(hanPdf, 'han', 1);
const hanTexts = assertLinesFit(hanPdf, 'han').map(l => l.text);
assert(hanTexts.some(t => t.includes('Note on characters:')),
  'a grouped report that folded a character says so in a closing note');
assert(hanTexts.some(t => t.includes(`/tmp/${'?'.repeat(2)}.txt`)),
  'the folded path shows one question mark per unrepresentable character');

// In `detail: 'full'` there is no issue element: the legend counts are parsed
// from the finding banners the model printed. One spelling and two numerals
// must tally to exactly those counts, and the legend is drawn there too.
const fullBanners = [
  '[ERROR] UE-SP001 · spelling · deterministic · line 3:4',
  '[WARNING] UE-NU002 · numerals · deterministic · line 1:11',
  '[WARNING] UE-NU002 · numerals · deterministic · line 2:11',
];
const fullPdf = renderPdf([
  { type: 'banner', kind: 'title', text: 'Editorial Review Report' },
  { type: 'banner', kind: 'error', text: fullBanners[0] },
  { type: 'banner', kind: 'warning', text: fullBanners[1] },
  { type: 'banner', kind: 'warning', text: fullBanners[2] },
  { type: 'heading', level: 1, text: 'Findings by file' },
  { type: 'paragraph', text: 'The draft text.' },
], opts);
const fullS = validateStructure(fullPdf, 'full', 1);
const fullLines = assertLinesFit(fullPdf, 'full');
const fullTexts = fullLines.map(l => l.text);
for (const banner of fullBanners) {
  assert(fullTexts.includes(banner), `the full-detail banner reaches the page: ${banner}`);
}
const fullLegend = legendFields(fullLines);
assert.deepEqual(fullLegend.counts, legendRows([
  { category: 'spelling' }, { category: 'numerals' }, { category: 'numerals' },
]).map(r => r.count),
'full-detail legend counts are parsed from the finding banners');
assert.deepEqual(fullLegend.names, CATEGORY_LEGEND.map(e => e.category),
  'full detail lists all twelve categories too');
assert(fullLines.findIndex(l => l.text === 'Findings by file' && l.font === 'F2')
  > fullLines.findIndex(l => l.text === 'Categories' && l.font === 'F2'),
  'the full-detail legend is drawn before the findings section');
const fullFooter = footerCells({ page: 1, pages: 1 });
assert(fullLines.slice(-3).map(l => l.text).join(' | ')
  === [fullFooter.left, fullFooter.centre, fullFooter.right].join(' | '),
  'the full-detail footer is the same three-cell furniture');
assert(!fullS.includes('UNITED NATIONS'),
  'the endorsement boundary holds in full detail as well');

// --- 11: the cap block is drawn, not merely claimed --------------------------
//
// D13 (REPORT-REDESIGN-PLAN §4): a capped section prints a record under it
// stating the count withheld and the exact re-run command, so a printed copy
// states what it is not showing. The wording is lib/report.mjs capLines; this
// suite builds its own cap element rather than importing one, so the check is
// on the renderer. A block that was dropped, or that drew its first line and
// stopped, fails here.

{
  const CAP_CMD = 'un-editorial-check docs --report-detail full --report docs.pdf';
  const capPdf = renderPdf([
    { type: 'banner', kind: 'title', text: 'Editorial Review Report' },
    { type: 'kv', label: 'Version', value: '9.9.9' },
    { type: 'spacer' },
    { type: 'heading', level: 1, text: 'Categories',
      meta: 'twelve checked categories', count: '41 findings' },
    { type: 'heading', level: 1, text: 'Editorial Warnings',
      meta: 'deterministic · warning only', count: '41 findings' },
    { type: 'cap', shown: 17, total: 41, command: CAP_CMD },
    { type: 'paragraph', text: 'Body text after the cap.' },
  ], { version: '9.9.9' });

  // Every line the renderer draws is checked against its column first, so the
  // cap's wrapped lines are proven to fit the measure and not to run into the
  // right margin.
  const capExtracted = assertLinesFit(capPdf, 'cap');
  const sequence = capExtracted.map(line => line.text).join('\n');
  const start = capExtracted.findIndex(line =>
    line.text === 'Showing 17 of 41 · 24 not listed above.');
  assert(start > 0, 'the cap line reaches the page verbatim');

  const body = capExtracted.findIndex(line => line.text === 'Body text after the cap.');
  assert(body > start, 'the block closes before the body resumes');
  const drawn = capExtracted.slice(start, body).map(line => line.text);
  assert.equal(drawn[0], 'Showing 17 of 41 · 24 not listed above.',
    'the count withheld leads the block');
  assert(drawn.some(t => t.includes('Nothing is discarded. All 41 are in this run')),
    'the promise that nothing was discarded follows it');
  assert(drawn.some(t => t === CAP_CMD),
    'the re-run command reaches the page whole, in the same monospace line');
  assert(drawn.length >= 3, 'all three lines are drawn, however the promise wraps');
  assert.equal(drawn[drawn.length - 1], CAP_CMD,
    'the command is the last line of the block, immediately before the body resumes');

  // The block is a bordered band, not three loose paragraphs: without the
  // border a reader could take the cap for the end of the section.
  assert(capPdf.toString('latin1').includes(' re S '),
    'the cap block draws its border');

  // The header beside it still claims the whole count, not the drawn part.
  const header = capExtracted.findIndex(line => line.text === 'Editorial Warnings');
  assert(header >= 0 && capExtracted[header + 1].text === 'deterministic · warning only',
    'the lane metadata is set beside the header');
  assert(capExtracted[header + 2].text === '41 findings'
    && capExtracted[header + 2].x > MARGIN,
    'the count sits at the right edge, level with the header it belongs to');

  // Nothing above leaked the endorsement boundary on the way through.
  assert(!sequence.includes('UNITED NATIONS'), 'the cap block never names the United Nations');
}

// --- 12: no path is extended before it is started ---------------------------
//
// `l` appends a line to the *current point*; with no point established the
// operation is undefined. Acrobat refuses such a page — "An error exists on
// this page. Acrobat may not display the page correctly." — while PDFKit,
// Quick Look and qpdf all guess a starting point and render happily. The
// header rule shipped exactly that defect as `54 752.39 541.28 752.39 l S`,
// four operands and no `m`, once per page, so every page of a generated report
// was rejected by the reader people actually use. A one-line patch test would
// have missed the class: what is asserted is the rule, that no path-extending
// operator may appear before `m` or `re` within the current subpath.

{
  const PATH_START = new Set(['m', 're']);
  const PATH_PAINT = new Set(['S', 's', 'f', 'F', 'f*', 'B', 'B*', 'b', 'b*', 'n']);
  const PATH_EXTEND = new Set(['l', 'c', 'v', 'y', 'h']);

  // Tokens with literal strings and comments removed. A drawn line of prose
  // contains the letter `l` and the digit `5`; reading string contents as
  // operators would make this check cry wolf on every page of text.
  function pathTokens(body) {
    const out = [];
    let i = 0;
    while (i < body.length) {
      const ch = body[i];
      if (ch === '%') { while (i < body.length && body[i] !== '\n') i++; continue; }
      if (/\s/.test(ch)) { i += 1; continue; }
      if (ch === '(') {
        let j = i + 1;
        let depth = 1;
        while (j < body.length && depth > 0) {
          if (body[j] === '\\') { j += 2; continue; }
          if (body[j] === '(') depth += 1;
          else if (body[j] === ')') depth -= 1;
          j += 1;
        }
        i = j; continue;
      }
      if (ch === '/') {
        let j = i + 1;
        while (j < body.length && !/[\s()<>\[\]{}/%]/.test(body[j])) j += 1;
        i = j; continue;
      }
      if (/[-+0-9.]/.test(ch)) {
        let j = i;
        while (j < body.length && /[-+0-9.eE]/.test(body[j])) j += 1;
        i = j; continue;
      }
      if ('[]<>{}'.includes(ch)) { i += 1; continue; }
      let j = i;
      while (j < body.length && !/[\s()<>\[\]{}/%]/.test(body[j])) j += 1;
      out.push(body.slice(i, j));
      i = j;
    }
    return out;
  }

  /** Path-extending operators applied with no current point, in order. */
  function orphanPathOps(body) {
    const bad = [];
    let current = false;
    for (const op of pathTokens(body)) {
      if (PATH_START.has(op)) { current = true; continue; }
      if (PATH_PAINT.has(op)) { current = false; continue; }
      if (PATH_EXTEND.has(op) && !current) bad.push(op);
    }
    return bad;
  }

  const targets = [
    ['report', pdf], ['stress', stress], ['bare', bare],
    ['issue', issuePdf], ['han', hanPdf], ['full', fullPdf],
  ];

  // Anti-vacuity: these fixtures all draw rules, so if the tokenizer silently
  // stopped finding operators the loop below would pass on nothing at all.
  const extenders = targets.flatMap(([, doc]) => streamBodies(doc)
    .flatMap((body) => pathTokens(body).filter((op) => PATH_EXTEND.has(op))));
  assert.ok(extenders.length > 10,
    `the path check has path operators to inspect (${extenders.length}), so it is `
    + 'not passing on an empty token stream');

  let inspected = 0;
  for (const [label, doc] of targets) {
    streamBodies(doc).forEach((body, index) => {
      inspected += 1;
      assert.deepEqual(orphanPathOps(body), [],
        `${label} page ${index + 1}: a path operator was applied with no current point. `
        + 'A rule must moveto before it lineto, or Acrobat rejects the whole page.');
    });
  }
  assert.ok(inspected >= 6, `every fixture page was inspected (${inspected})`);
}

// --- 13: the two full-bleed bands, pinned (E20) ------------------------------
//
// The masthead band and the footer band are the report's page chrome: the two
// fills that make every sheet read as one document. Nothing asserted either
// one until now, so both could move without a suite noticing — a masthead
// inset to the margin reads as a box rather than as the top of the page, a
// footer band of a different height leaves the three footer cells standing
// off the band they are stamped on. Four properties, each named for the
// failure it exists to catch:
//
//   (a) every page carries exactly one masthead fill at x = 0, width the
//       full 595.28, its top edge at the page top — genuinely full bleed on
//       all four sides, not a wide rectangle inset to the margin;
//   (b) every page carries exactly one footer band, `0 0 595.28 48 re f`;
//   (c) the divider rule sits at y = 48, the top edge of that band, so the
//       footer cells read as standing on the band rather than floating;
//   (d) the masthead's bottom edge sits above its own divider rule — the
//       band and the rule may never overlap or swap, or the fill covers the
//       rule that closes it.
//
// The fill regex pins x = 0 by matching the `0` that follows `rg` (the fill's
// first `re` operand) and then reads y, width and height off the operand, so
// a band that moved off the page edge stops matching entirely and fails the
// count instead of passing as "a band".

function assertBandGeometry(doc, label) {
  let inspected = 0;
  streamBodies(doc).forEach((body, index) => {
    inspected += 1;
    const page = `${label} page ${index + 1}`;
    const bands = [...body.matchAll(/rg 0 ([0-9.]+) ([0-9.]+) ([0-9.]+) re f/g)]
      .map(m => ({ y: Number(m[1]), w: Number(m[2]), h: Number(m[3]) }));

    // (a) The masthead is the only band above the page corner. `n()` rounds
    // each operand to two decimals on its own, so the top edge y + h is
    // compared against PAGE_H within a hundredth rather than for equality.
    const masthead = bands.filter(b => b.y > 0);
    assert.equal(masthead.length, 1,
      `${page}: exactly one masthead band rising from x=0, found ${masthead.length}`);
    assert.equal(masthead[0].w, PAGE_W,
      `${page}: the masthead spans the full page width (${masthead[0].w} of ${PAGE_W})`);
    assert(Math.abs(masthead[0].y + masthead[0].h - PAGE_H) < 0.011,
      `${page}: the masthead's top edge reaches the page top (`
      + `${(masthead[0].y + masthead[0].h).toFixed(2)} of ${PAGE_H})`);

    // (b) The footer band, pinned to the page corner at 48 pt high. Section 6
    // already proved the three cells sit below the content box; this pins
    // what they sit *on*.
    const footer = bands.filter(b => b.y === 0);
    assert.equal(footer.length, 1,
      `${page}: exactly one footer band at the page corner, found ${footer.length}`);
    assert.equal(footer[0].w, PAGE_W,
      `${page}: the footer band spans the full page width (${footer[0].w} of ${PAGE_W})`);
    assert.equal(footer[0].h, 48,
      `${page}: the footer band is the 48 pt band "0 0 595.28 48 re f"`);

    // Every horizontal rule the page draws, in stream order: the masthead's
    // own divider first (drawHeader pushes it before any body content), then
    // whatever rules the body adds, then the footer's. The right edge is
    // computed from the suite's own MARGIN and CONTENT_W, rounded as the
    // renderer rounds it, so a table drifted in either direction disagrees.
    const rightEdge = String(Math.round((MARGIN + CONTENT_W) * 100) / 100);
    const rules = [...body.matchAll(
      new RegExp(`RG ${MARGIN} ([0-9.]+) m ${rightEdge} ([0-9.]+) l S`, 'g'))]
      .map(m => ({ y1: Number(m[1]), y2: Number(m[2]) }));

    // (c) One divider, horizontal, at y = 48 — exactly the band's own top
    // edge pinned in (b). A rule anywhere else leaves the cells floating off
    // the band or drawing a second line across it.
    const footerRules = rules.filter(r => r.y1 === 48 && r.y2 === 48);
    assert.equal(footerRules.length, 1,
      `${page}: exactly one divider rule at y=48, found ${footerRules.length}`);

    // (d) The first rule on the page is the masthead's divider, and the band
    // painted above it must stop *above* that line: bandBottom is ruleY plus
    // a gap, so the two touch nothing and can neither overlap nor swap.
    const headRule = rules[0];
    assert(headRule, `${page}: the masthead's closing rule is drawn`);
    assert.equal(headRule.y1, headRule.y2,
      `${page}: the masthead's closing rule is horizontal`);
    assert(masthead[0].y > headRule.y1,
      `${page}: the masthead's bottom edge (${masthead[0].y}) sits above its `
      + `divider rule (${headRule.y1}) — band and rule never overlap or swap`);
  });
  return inspected;
}

// Every page of every fixture built above, cover and continuations alike.
const BAND_TARGETS = [['report', pdf], ['stress', stress], ['bare', bare],
  ['issue', issuePdf], ['han', hanPdf], ['full', fullPdf]];
const bandPages = BAND_TARGETS.reduce((total, [label, doc]) =>
  total + assertBandGeometry(doc, label), 0);
assert(bandPages >= 6,
  `band geometry inspected on at least six pages, found ${bandPages}`);

console.log('ok — pdf structure: magic, xref offsets, pages, fonts, extraction, '
  + 'transliteration, escaping, header and footer furniture on every page, '
  + 'stress token, determinism, documented and announced fold for characters '
  + 'WinAnsi cannot encode, issue block with six provenance rows and a count '
  + 'only above one, twelve-row legend with text labels and per-category '
  + 'counts, each row and legend row wearing the mark its own severity and '
  + 'category ask for, '
  + 'the capped section\'s three-line record with its re-run command, '
  + 'the endorsement boundary, '
  + 'the full-bleed masthead and footer bands with their divider rules on every page, '
  + 'and no path extended before it was started');
