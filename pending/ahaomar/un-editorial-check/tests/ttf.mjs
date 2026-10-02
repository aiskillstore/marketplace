// TrueType reading and subsetting — `lib/ttf.mjs`.
//
// The subsetter is the one piece of this redesign that can fail silently: a
// font that parses, compresses and embeds still produces a wrong report if it
// is missing a glyph or carries a width that disagrees with the source. Line
// breaking is computed from these numbers, so a width that drifts reflows text
// against a measure it no longer fits.
//
// Every assertion below is checked against both shipped faces, and the
// round-trip in particular re-reads the generated subset with the same reader
// and demands that all 218 reachable bytes still measure what they measured
// before subsetting. The source values are pinned because the fonts are
// vendored: they cannot change without this file changing first.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

import { fontDescriptor, glyphFor, metricsOf, parseTables, subset, winAnsiWidths } from '../lib/ttf.mjs';
import { toWinAnsi, winAnsiToUnicode } from '../lib/winansi.mjs';

const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const FACES = ['RobotoCondensed-Regular.ttf', 'RobotoCondensed-Bold.ttf'];
const SHAPING = ['GPOS', 'GSUB', 'GDEF', 'STAT'];
// 0xB1B0AFBA is the constant the OpenType checksum adjustment is derived from.
// A font built by the book sums to exactly that, which is why it works as a
// whole-file check rather than as a value to compare against anything.
const CHECKSUM_BIAS = 0xB1B0AFBA;

const sources = new Map(FACES.map(name => [name, fs.readFileSync(path.join(ROOT, 'fonts', name))]));

/** Big-endian uint32 sum over `data`, zero-padded to a 4-byte boundary. */
function checksum(data) {
  const padded = Buffer.alloc(Math.ceil(data.length / 4) * 4);
  data.copy(padded);
  let sum = 0;
  for (let p = 0; p < padded.length; p += 4) sum = (sum + padded.readUInt32BE(p)) >>> 0;
  return sum >>> 0;
}

/** Every byte whose WinAnsi position is defined — 218 of 256. */
function definedBytes() {
  const out = [];
  for (let byte = 0; byte < 256; byte++) if (winAnsiToUnicode(byte) !== null) out.push(byte);
  return out;
}

// --- the sources themselves ---------------------------------------------------

for (const [name, src] of sources) {
  const tables = parseTables(src);
  assert.equal(src.readUInt32BE(0), 0x00010000, `${name}: expected a TrueType sfnt header`);
  assert.equal(src.length, name.endsWith('Regular.ttf') ? 112600 : 113112, `${name}: source size changed`);
  for (const tag of SHAPING) assert.ok(tables.has(tag), `${name}: ${tag} should be present in the source`);
  for (const tag of ['glyf', 'loca', 'cmap', 'hmtx', 'head', 'hhea', 'maxp', 'OS/2', 'post', 'name']) {
    assert.ok(tables.has(tag), `${name}: missing ${tag}`);
  }

  // The convention the subsetter copies. Both shipped faces record `head`'s
  // directory checksum over the table with its adjustment zeroed, and their
  // whole-file sum comes to the bias exactly — the proof that the algorithm in
  // `subset` is the one these files were built with rather than a plausible
  // alternative.
  const head = tables.get('head');
  const zeroed = Buffer.from(src.subarray(head.offset, head.offset + head.length));
  zeroed.writeUInt32BE(0, 8);
  assert.equal(checksum(zeroed), head.checksum, `${name}: head directory checksum is not the zeroed one`);
  assert.equal(checksum(src), CHECKSUM_BIAS, `${name}: whole-file sum should be 0xB1B0AFBA`);
}
ok('sources: vendored faces intact, shaping tables present, checksum convention is the spec one');

// --- descriptor fields --------------------------------------------------------

for (const [name, src] of sources) {
  const d = fontDescriptor(src);
  const bold = name.includes('Bold');
  assert.equal(d.unitsPerEm, 2048, `${name}: unitsPerEm`);
  assert.equal(d.ascent, 1900, `${name}: ascent`);
  assert.equal(d.descent, -500, `${name}: descent`);
  assert.equal(d.capHeight, 1456, `${name}: capHeight`);
  assert.equal(d.italicAngle, 0, `${name}: italicAngle`);
  assert.equal(d.numGlyphs, 1031, `${name}: numGlyphs`);
  assert.equal(d.weightClass, bold ? 700 : 400, `${name}: weightClass`);
  // Derived, not read: see the comment where `stemV` is computed. Regular lands
  // on 80 and Bold on 140, the band the base-14 faces sit in.
  assert.equal(d.stemV, bold ? 140 : 80, `${name}: stemV should follow the weight class`);
  // Bold is wider: -1489/2130 against Regular's -1510/2044.
  assert.deepEqual(
    [d.xMin, d.yMin, d.xMax, d.yMax],
    bold ? [-1489, -555, 2130, 2163] : [-1510, -555, 2044, 2163],
    `${name}: fontBBox`,
  );
}
ok('descriptor: outline metrics read from head, hhea, OS/2 and post');

// --- widths -------------------------------------------------------------------

const expectedWidths = {
  // byte: [Regular, Bold] — in units of 1000 em, which is what /Widths carries.
  0x20: [229, 230],  // space
  0x41: [577, 597],  // A
  0x57: [762, 750],  // W — the letter that decides whether a line fits the measure
  0x69: [229, 252],  // i
  0x96: [572, 548],  // en dash, reached through the C1 table rather than Latin-1
  0x80: [494, 505],  // euro
  0xE9: [469, 479],  // e-acute, a composite glyph
};
for (const [name, src] of sources) {
  const widths = winAnsiWidths(src);
  const index = name.includes('Bold') ? 1 : 0;
  assert.equal(widths.length, 256, `${name}: /Widths must cover all 256 positions`);
  for (const [byte, expected] of Object.entries(expectedWidths)) {
    assert.equal(widths[byte], expected[index], `${name}: width of byte 0x${Number(byte).toString(16)}`);
  }
  // Adobe leaves five positions undefined. They are unreachable — `toWinAnsi`
  // folds an unmapped code point to "?" before a byte exists — so a width of 0
  // can never reach a line-break calculation.
  for (const byte of [0x81, 0x8D, 0x8F, 0x90, 0x9D]) {
    assert.equal(winAnsiToUnicode(byte), null, `${name}: byte 0x${byte.toString(16)} should be undefined`);
    assert.equal(widths[byte], 0, `${name}: undefined byte 0x${byte.toString(16)} must measure 0`);
  }
}
ok('widths: advance per WinAnsi byte in units of 1000, undefined positions left at 0');

// --- the byte table agrees with the emitter -----------------------------------

// The two maps are read in opposite directions and neither is the inverse of
// the other: the reader is keyed by byte and covers every defined position,
// while the emitter folds a handful of code points somewhere else entirely —
// the ellipsis becomes "...", the soft hyphen disappears, and the smart quotes
// land on plain ASCII instead of their C1 positions.
//
// So the property worth locking is one-directional, and it is the one that
// protects a report: whatever byte leaves the emitter, the reader must have a
// position for it. A byte neither can resolve would measure as zero width and
// draw no glyph — text that silently reflows instead of failing.
let definedPositions = 0;
for (let byte = 0; byte < 256; byte++) if (winAnsiToUnicode(byte) !== null) definedPositions += 1;
assert.equal(definedPositions, 218, 'Adobe leaves five positions undefined; the rest must be known');

for (let codePoint = 0; codePoint <= 0xFFFF; codePoint++) {
  const folded = toWinAnsi(String.fromCodePoint(codePoint));
  for (const char of folded) {
    const byte = char.charCodeAt(0);
    assert.notEqual(winAnsiToUnicode(byte), null,
      `U+${codePoint.toString(16)} folded to byte 0x${byte.toString(16)}, which the reader cannot resolve`);
  }
}
// There used to be an `assert.equal(scanned, 0x10000)` here, counting loop
// iterations against the loop's own bound — an assertion that can never fail
// and so asserts nothing. The per-code-point assertions inside the loop are
// the real test: they check every fold actually resolves.

// The case that matters most: the en dash must survive as byte 0x96, because
// folding it to "-" hides UE-NU002's whole defect.
assert.equal(toWinAnsi('–'), '\u0096', 'en dash must encode, not fold');
assert.equal(winAnsiToUnicode(0x96), 0x2013, 'byte 0x96 must name the en dash');

// Idempotence: a string reaches `toWinAnsi` twice, once to measure and once to
// emit, so folding an already-folded string must not move it again.
for (const sample of ['ASCII text', 'en–dash', 'em—dash', '“curly”', '…more', 'e-acute é', '(paren)', 'back\\slash']) {
  const once = toWinAnsi(sample);
  assert.equal(toWinAnsi(once), once, `toWinAnsi is not idempotent on ${sample}`);
}
ok('winansi: emitter output always resolvable, 218 defined positions, folding idempotent');

// --- the subset ---------------------------------------------------------------

const subsets = new Map();
for (const [name, src] of sources) {
  const built = subset(src);
  subsets.set(name, built);
  const tables = parseTables(built);

  assert.ok(built.length < src.length, `${name}: subset must be smaller than its source`);
  assert.equal(built.length, name.endsWith('Regular.ttf') ? 29348 : 29456, `${name}: subset size changed`);
  for (const tag of SHAPING) {
    assert.ok(!tables.has(tag), `${name}: ${tag} should have been dropped — nothing in a WinAnsi PDF reads it`);
  }

  const numGlyphs = built.readUInt16BE(tables.get('maxp').offset + 4);
  // .notdef plus every glyph reachable from the 218 bytes, components included.
  assert.equal(numGlyphs, 227, `${name}: kept glyph count`);
  assert.equal(built.readUInt16BE(tables.get('hhea').offset + 34), numGlyphs,
    `${name}: numberOfHMetrics must match numGlyphs so hmtx has no trailing run`);
  // Long-form loca, because the short form only holds if every glyph offset is
  // even and the rebuilt glyf is not padded for it.
  assert.equal(built.readInt16BE(tables.get('head').offset + 50), 1, `${name}: loca must be long form`);

  // Proof that the cmap was renumbered rather than copied: the source puts A
  // at 37, and a subset that wrote source ids straight through would leave it
  // there, past the end of a 227-glyph font.
  assert.notEqual(glyphFor(built, 0x41), glyphFor(src, 0x41),
    `${name}: A should have been renumbered`);
  assert.ok(glyphFor(built, 0x41) < numGlyphs, `${name}: A must land inside the kept set`);
  assert.equal(glyphFor(built, 0), 0, `${name}: glyph 0 must stay .notdef`);
  // é is a composite: without its components resolved it would draw blank.
  assert.notEqual(glyphFor(built, 0x00E9), 0, `${name}: e-acute must be present`);
  assert.notEqual(glyphFor(built, 0x2013), 0, `${name}: en dash must be present`);
  // Composite components: é is `e` plus an accent no WinAnsi byte names on its
  // own, so the kept set must be larger than the glyphs the bytes name
  // directly. Blanking every accented letter is what happens if this fails.
  const directlyNamed = new Set();
  for (const byte of definedBytes()) {
    const gid = glyphFor(src, winAnsiToUnicode(byte));
    if (gid !== 0) directlyNamed.add(gid);
  }
  // 227 kept against however many the bytes name directly: the difference is
  // the components, which no byte names on its own. Blanking every accented
  // letter is what happens if they are not pulled in.
  const components = numGlyphs - (directlyNamed.size + 1); // +1 for .notdef
  assert.ok(components > 0,
    `${name}: expected composite components beyond the ${directlyNamed.size} named glyphs, found none`);
  // Pinned, measured on both shipped faces: all 218 defined WinAnsi bytes name
  // distinct glyphs, and the composites pull in 8 more (1 + 218 + 8 = 227).
  // The former assertion here was `directlyNamed.size + 1 + components ===
  // numGlyphs` — algebraically always true, because `components` was defined
  // three lines above as exactly `numGlyphs - (directlyNamed.size + 1)`. It
  // could never fail and therefore asserted nothing; these numbers can.
  assert.equal(directlyNamed.size, 218, `${name}: WinAnsi bytes should name 218 distinct glyphs`);
  assert.equal(components, 8, `${name}: composites should pull in 8 components beyond the directly named`);

  // Structure: every directory checksum matches its bytes, with `head`'s
  // adjustment zeroed as the convention requires.
  for (const [tag, record] of tables) {
    let data = built.subarray(record.offset, record.offset + record.length);
    if (tag === 'head') {
      data = Buffer.from(data);
      data.writeUInt32BE(0, 8);
    }
    assert.equal(checksum(data), record.checksum, `${name}: directory checksum for ${tag}`);
  }
  // And the whole file sums to the bias, which is what makes the adjustment
  // correct rather than merely present.
  assert.equal(checksum(built), CHECKSUM_BIAS, `${name}: whole-file checksum sum`);

  // Determinism: no clock, no random tag, no environment read.
  assert.equal(Buffer.compare(built, subset(src)), 0, `${name}: subsetting must be byte-reproducible`);
}
ok('subset: shaping tables dropped, 227 of 1031 glyphs, checksums valid, byte-reproducible');

// --- format 4 header fields ----------------------------------------------------

// `cmapLookup` reads only format, segCountX2 and the segment arrays; nothing
// in this package ever reads `searchRange`, `entrySelector`, `rangeShift`, the
// subtable `length`, the `reservedPad` or the `0xFFFF` terminator back. A
// subset that mangled any of them would pass every other assertion in this
// file and be caught only by a third-party validator, so they are locked here.
for (const [name, built] of subsets) {
  const tables = parseTables(built);
  const cmap = tables.get('cmap');
  const sub = cmap.offset + 12; // the single encoding record's offset field says 12
  const tableEnd = cmap.offset + cmap.length;

  // The subtable's own length claim must end exactly at the end of the table
  // holding it: longer reaches past the cmap, shorter leaves bytes a reader
  // would silently skip.
  assert.equal(built.readUInt16BE(sub + 2), tableEnd - sub,
    `${name}: format 4 length should span exactly from the subtable to the end of cmap`);

  const segCountX2 = built.readUInt16BE(sub + 6);
  assert.ok(segCountX2 > 0 && segCountX2 % 2 === 0,
    `${name}: segCountX2 is ${segCountX2}, which must be even and non-zero`);
  const segCount = segCountX2 / 2;

  // The binary-search hints, computed from the parsed segCount rather than
  // pinned: the largest power of two not greater than segCount, its exponent,
  // and what the segments do not fit into it.
  let block = 1;
  while (block * 2 <= segCount) block *= 2;
  assert.equal(built.readUInt16BE(sub + 8), 2 * block, `${name}: searchRange should be 2 * ${block}`);
  assert.equal(built.readUInt16BE(sub + 10), Math.log2(block),
    `${name}: entrySelector should be log2(${block})`);
  assert.equal(built.readUInt16BE(sub + 12), segCountX2 - 2 * block,
    `${name}: rangeShift should be segCountX2 - searchRange`);

  const endCode = sub + 14;
  assert.equal(built.readUInt16BE(endCode + (segCount - 1) * 2), 0xFFFF,
    `${name}: the final endCode must be the 0xFFFF terminator`);
  assert.equal(built.readUInt16BE(endCode + segCount * 2), 0,
    `${name}: the reservedPad word after endCode must be 0`);
}
ok('cmap: format 4 header locked — length, search hints, reservedPad, 0xFFFF terminator');

// --- hmtx: the compact trailing run -------------------------------------------

// This branch is dead under every real input: both shipped faces record
// `numberOfHMetrics === numGlyphs === 1031`, and `subset()` forces equality in
// its own output, so `metricsOf`'s path where `gid >= count` reads the compact
// side-bearing run is unreachable from the fonts in this repo. A hand-built
// hhea+hmtx buffer is the only way to reach it — which is exactly why
// `metricsOf` is exported rather than left private.
const synthetic = Buffer.alloc(44);
const syntheticTables = new Map([
  ['hhea', { offset: 0 }],  // numberOfHMetrics lives at hhea + 34
  ['hmtx', { offset: 36 }], // 1 full metric (advance + bearing), then a 2-word run
]);
// numberOfHMetrics = 1, numGlyphs = 3: glyph 0 carries the only full metric,
// glyphs 1 and 2 get their bearings from the compact run that follows.
synthetic.writeUInt16BE(1, 34);
synthetic.writeUInt16BE(500, 36);  // glyph 0 advance
synthetic.writeInt16BE(10, 38);     // glyph 0 left side bearing
synthetic.writeInt16BE(-20, 40);    // glyph 1 bearing, no advance of its own
synthetic.writeInt16BE(30, 42);     // glyph 2 bearing, no advance of its own

{
  const { advances, sideBearings } = metricsOf(synthetic, syntheticTables, 3);
  // Glyph 0 takes its own advance; glyphs past the last full metric share it.
  assert.equal(advances[0], 500, 'synthetic: glyph 0 advance');
  assert.equal(advances[1], 500, 'synthetic: glyph 1 should share glyph 0 advance');
  assert.equal(advances[2], 500, 'synthetic: glyph 2 should share glyph 0 advance');
  // Each glyph still reads its own left side bearing from the compact run.
  assert.equal(sideBearings[0], 10, 'synthetic: glyph 0 side bearing');
  assert.equal(sideBearings[1], -20, 'synthetic: glyph 1 bearing should come from the run');
  assert.equal(sideBearings[2], 30, 'synthetic: glyph 2 bearing should come from the run');

  // There must be a first advance: without one, every glyph's advance is undefined.
  synthetic.writeUInt16BE(0, 34);
  assert.throws(() => metricsOf(synthetic, syntheticTables, 3), /numberOfHMetrics is 0/,
    'synthetic: count 0 must throw — the first advance is undefined');
  // More metrics than glyphs means hhea describes glyphs maxp denies exist.
  synthetic.writeUInt16BE(4, 34);
  assert.throws(() => metricsOf(synthetic, syntheticTables, 3), /exceeds the 3 glyphs/,
    'synthetic: count > numGlyphs must throw');
}
ok('hmtx: synthetic trailing run — shared advance, per-glyph bearings, count guards');

// --- composite renumbering -----------------------------------------------------

/**
 * A glyph's raw `glyf` record, from `loca`. Shared by the decoder below and
 * the outline comparison further down.
 */
function glyphRecord(buf, tables, gid) {
  const longForm = buf.readInt16BE(tables.get('head').offset + 50) !== 0;
  const loca = tables.get('loca').offset;
  const lo = longForm ? buf.readUInt32BE(loca + gid * 4) : buf.readUInt16BE(loca + gid * 2) * 2;
  const hi = longForm ? buf.readUInt32BE(loca + gid * 4 + 4) : buf.readUInt16BE(loca + gid * 2 + 2) * 2;
  return buf.subarray(tables.get('glyf').offset + lo, tables.get('glyf').offset + hi);
}

/**
 * The component glyph ids a composite names, decoded straight from `glyf`.
 * Simple glyphs have `numberOfContours >= 0` at int16 offset 0 and yield no
 * components; a composite has it `< 0`, with flags/component-id pairs from
 * byte 10. Deliberately independent of `lib/ttf.mjs`'s own walker: the test
 * must decode the outlines itself to check what the subsetter wrote into them.
 */
function compositeGlyphIds(buf, tables, gid) {
  const record = glyphRecord(buf, tables, gid);
  if (record.length < 10 || record.readInt16BE(0) >= 0) return []; // simple glyph
  const refs = [];
  let p = 10;
  while (p + 4 <= record.length) {
    const flags = record.readUInt16BE(p);
    refs.push(record.readUInt16BE(p + 2));
    p += 4 + (flags & 0x0001 ? 4 : 2);   // ARG_1_AND_2_ARE_WORDS
    if (flags & 0x0008) p += 2;           // WE_HAVE_A_SCALE
    else if (flags & 0x0040) p += 4;      // WE_HAVE_AN_X_AND_Y_SCALE
    else if (flags & 0x0080) p += 8;      // WE_HAVE_A_TWO_BY_TWO
    if (!(flags & 0x0020)) break;         // MORE_COMPONENTS
  }
  return refs;
}

// A composite's component ids are rewritten to the subset's numbering, and no
// width assertion can catch a mis-rewrite: widths come from `hmtx`, never from
// the outlines, so a component pointing at a coincidentally-kept wrong glyph
// would draw the wrong shape while every number in the round-trip stayed
// green. Decoding `é` in both faces checks two things of each component: its
// advance read through the subset's own `hmtx` matches the *source*
// component's advance, and — because the advance alone is not unique (measured
// on these faces: every e-variant, é/è/ê/ë, shares `e`'s advance, so a
// component mis-landed on a sibling would pass the advance check) — its
// outline is byte-identical to the source component's record.
for (const [name, src] of sources) {
  const built = subsets.get(name);
  const srcTables = parseTables(src);
  const builtTables = parseTables(built);
  const srcMetrics = metricsOf(src, srcTables, src.readUInt16BE(srcTables.get('maxp').offset + 4));
  const builtNumGlyphs = built.readUInt16BE(builtTables.get('maxp').offset + 4);
  const builtMetrics = metricsOf(built, builtTables, builtNumGlyphs);

  const srcParts = compositeGlyphIds(src, srcTables, glyphFor(src, 0x00E9));
  const builtParts = compositeGlyphIds(built, builtTables, glyphFor(built, 0x00E9));
  assert.ok(srcParts.length >= 2,
    `${name}: source e-acute should be a composite of at least two glyphs, found ${srcParts.length}`);
  assert.equal(builtParts.length, srcParts.length,
    `${name}: the subset e-acute should keep the source's component count`);
  for (let i = 0; i < srcParts.length; i++) {
    assert.ok(builtParts[i] < builtNumGlyphs,
      `${name}: e-acute component ${i} should land inside the ${builtNumGlyphs}-glyph subset`);
    assert.equal(builtMetrics.advances[builtParts[i]], srcMetrics.advances[srcParts[i]],
      `${name}: e-acute component ${i} should carry source component ${srcParts[i]}'s advance`);
    // Both components are simple in these faces (measured: one contour each),
    // so the subsetter copies their records verbatim, zero-padded to even
    // length — comparing over the source record's length is a full identity
    // check the advance alone cannot give.
    const srcRecord = glyphRecord(src, srcTables, srcParts[i]);
    const builtRecord = glyphRecord(built, builtTables, builtParts[i]);
    assert.ok(srcRecord.readInt16BE(0) >= 0,
      `${name}: source e-acute component ${i} should be a simple glyph, so outlines can be compared`);
    assert.ok(builtRecord.subarray(0, srcRecord.length).equals(srcRecord),
      `${name}: e-acute component ${i} should keep source component ${srcParts[i]}'s exact outline`);
  }
}
ok('composite: e-acute components renumbered onto the glyphs with their source advances');

// --- round trip ---------------------------------------------------------------

// The assertion this whole file exists for. Re-reading the generated subset
// with the same reader and demanding identical widths proves the remapping
// survived: a wrong glyph id or a stale width shows up here as a number that
// no longer matches, not as a crash.
for (const [name, src] of sources) {
  const before = winAnsiWidths(src);
  const after = winAnsiWidths(subsets.get(name));
  let checked = 0;
  for (const byte of definedBytes()) {
    assert.equal(after[byte], before[byte],
      `${name}: byte 0x${byte.toString(16)} moved from ${before[byte]} to ${after[byte]}`);
    checked += 1;
  }
  assert.equal(checked, 218, `${name}: every reachable byte should have been compared`);
}
ok('round-trip: all 218 bytes keep their advance after subsetting, in both faces');

// --- the size this was done for ------------------------------------------------

const embedded = FACES.reduce((total, name) => {
  const source = sources.get(name);
  return {
    raw: total.raw + source.length,
    flate: total.flate + zlib.deflateSync(subsets.get(name), { level: 9 }).length,
    before: total.before + zlib.deflateSync(source, { level: 9 }).length,
  };
}, { raw: 0, flate: 0, before: 0 });

// Embedding both faces whole would have added ~135 KB to a 68 KB report. The
// budget this phase agreed on is ~38 KB, so the check is against that figure
// rather than against a percentage that a font update could satisfy while
// quietly costing more.
assert.ok(embedded.flate <= 40000, `embedded cost is ${embedded.flate} bytes, over the 40 KB budget`);
assert.ok(embedded.flate < embedded.before / 3, 'subsetting should cut the embedded cost by two thirds');
ok(`size: embedded cost ${Math.round(embedded.flate / 1024)} KB against ${Math.round(embedded.before / 1024)} KB whole — ${Math.round((1 - embedded.flate / embedded.before) * 100)}% saved`);

/** Print one passing line, matching the rest of the suite's output. */
function ok(message) {
  console.log(`ok — ttf: ${message}`);
}
