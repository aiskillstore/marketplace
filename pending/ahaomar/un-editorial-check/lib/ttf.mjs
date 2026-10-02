// --- TrueType reading and subsetting ----------------------------------------
//
// A zero-dependency reader for the two font files this package ships. It does
// three jobs and nothing else:
//
//   * `fontDescriptor` reads the fields a `/FontDescriptor` has to carry,
//   * `winAnsiWidths` reads the advance for every byte the report can emit,
//   * `subset` writes a smaller font holding only those bytes' glyphs.
//
// The third job is what keeps an embedded report near its old size: the
// sources are 112 KB apiece, and a report that embeds both whole weighs three
// times what it did before embedding. Keeping `.notdef`, the glyphs the 218
// WinAnsi bytes name directly, and their composite components leaves 227 of
// 1031 glyphs, and dropping the four shaping tables takes the rest — a
// `WinAnsiEncoding` PDF never reads them, because nothing in this pipeline runs
// a shaper. See `.feedbacks/PHASE-10-PLAN.md` §6.
//
// The reader refuses anything it cannot read. Every offset is checked against
// the buffer before it is used, because `Buffer.copy` clamps a short source
// silently and leaves the destination's tail zeroed: a font claiming to run
// past the end of the file would otherwise yield glyphs that parse and draw
// nothing, while the checksums — computed over those same zeros — still say
// the file is well formed. That is the one failure a report cannot afford to
// discover from a reader.
//
// Every step is deterministic. There is no clock, no random subset tag and no
// environment read anywhere below, so the same source bytes always yield the
// same subset bytes — a requirement, because identical input must produce a
// byte-identical report.

import { Buffer } from 'node:buffer';

import { winAnsiToUnicode } from './winansi.mjs';

// OpenType layout tables. They exist to position and substitute glyphs for a
// shaper, and a PDF showing single-byte WinAnsi text is not one.
const SHAPING_TABLES = new Set(['GPOS', 'GSUB', 'GDEF', 'STAT']);

const SFNT_TRUETYPE = 0x00010000;

/**
 * The table directory, keyed by tag. Every entry is checked against the buffer
 * before it is returned, so no consumer can read past the end of a file that
 * describes itself as larger than it is.
 *
 * @param {Buffer} buf
 * @returns {Map<string, {checksum:number, offset:number, length:number}>}
 */
export function parseTables(buf) {
  if (buf.length < 12) {
    throw new Error(`sfnt: ${buf.length} bytes is shorter than a table directory`);
  }
  const version = buf.readUInt32BE(0);
  if (version !== SFNT_TRUETYPE) {
    throw new Error(`sfnt: version 0x${version.toString(16).padStart(8, '0')}, `
      + 'expected 0x00010000 (TrueType outlines)');
  }
  const numTables = buf.readUInt16BE(4);
  if (12 + numTables * 16 > buf.length) {
    throw new Error(`sfnt: ${numTables} tables need a ${12 + numTables * 16}-byte directory, `
      + `file is ${buf.length} bytes`);
  }
  const tables = new Map();
  for (let i = 0; i < numTables; i++) {
    const o = 12 + i * 16;
    const tag = buf.toString('latin1', o, o + 4);
    const checksum = buf.readUInt32BE(o + 4);
    const offset = buf.readUInt32BE(o + 8);
    const length = buf.readUInt32BE(o + 12);
    // `offset === buf.length` is the sharp edge: copy would return 0 and leave
    // every byte of the destination as the zero it was allocated with, without
    // raising. A table claiming to run past the file is not a short file, it is
    // a wrong one.
    if (offset > buf.length || offset + length > buf.length) {
      throw new Error(`sfnt: table '${tag}' spans bytes ${offset}..${offset + length}, `
        + `past the end of a ${buf.length}-byte file`);
    }
    tables.set(tag, { checksum, offset, length });
  }
  return tables;
}

/**
 * A table this reader cannot work without. Missing `head`, `maxp` or `hmtx`
 * would otherwise surface as `Cannot read properties of undefined`, which names
 * neither the font nor the table.
 */
function must(tables, tag) {
  const table = tables.get(tag);
  if (!table) throw new Error(`font: required table '${tag}' is missing`);
  return table;
}

/**
 * The largest power of two not greater than `n`, and its exponent. Integer
 * arithmetic throughout: these two values become bytes in the sfnt directory
 * and in the format 4 header, and floating-point rounding has no business in a
 * binary layout.
 */
function bitFloor(n) {
  let value = 1;
  let exponent = 0;
  while (value * 2 <= n) {
    value *= 2;
    exponent += 1;
  }
  return { value, exponent };
}

// --- cmap ---------------------------------------------------------------------

/**
 * The best Unicode subtable: Windows BMP (3,1) first, then any Unicode
 * platform, then the Windows symbol charset. A font may expose several; only
 * one is consulted, so a preference order has to be stated rather than
 * assumed.
 *
 * The record walk is bounded by the table's own directory entry — a corrupt
 * `numTables` would otherwise read the next table's bytes as encoding records.
 */
function cmapSubtable(buf, tables) {
  const cmap = must(tables, 'cmap');
  const base = cmap.offset;
  const end = base + cmap.length;
  if (base + 4 > end) throw new Error('cmap: table too short to hold a header');
  const count = buf.readUInt16BE(base + 2);
  if (base + 4 + count * 8 > end) {
    throw new Error(`cmap: ${count} encoding records overrun the ${cmap.length}-byte table`);
  }
  let found = 0;
  let score = -1;
  for (let i = 0; i < count; i++) {
    const o = base + 4 + i * 8;
    const platformId = buf.readUInt16BE(o);
    const encodingId = buf.readUInt16BE(o + 2);
    let candidate = -1;
    if (platformId === 3 && encodingId === 1) candidate = 3;
    else if (platformId === 0) candidate = 2;
    else if (platformId === 3 && encodingId === 0) candidate = 1;
    if (candidate > score) {
      score = candidate;
      found = base + buf.readUInt32BE(o + 4);
    }
  }
  if (score === -1) throw new Error('cmap: no Unicode subtable — this reader needs one');
  if (found + 2 > end) {
    throw new Error(`cmap: subtable at ${found} lies outside the table ending at ${end}`);
  }
  return found;
}

/**
 * A code point to glyph id lookup over a format 4 subtable.
 *
 * This throws rather than degrading. A font without a readable format 4
 * subtable cannot be subset and cannot be measured; returning `() => 0` would
 * produce a font of nothing but `.notdef` — every character a hollow box — and
 * a report that says nothing went wrong. The `0` a caller can get back is for
 * a code point the face does not cover, which is a real thing a font may
 * legitimately lack.
 *
 * @param {Buffer} buf
 * @param {Map<string, {offset:number, length:number}>} tables
 * @returns {(codePoint:number) => number}
 */
function cmapLookup(buf, tables) {
  const cmap = must(tables, 'cmap');
  const sub = cmapSubtable(buf, tables);
  const format = buf.readUInt16BE(sub);
  if (format !== 4) {
    throw new Error(`cmap: subtable is format ${format}, this reader handles format 4`);
  }
  // `length` is the subtable's own claim, and it must not reach past the table
  // that contains it: a glyphIdArray index past the subtable reads the next
  // table as glyph ids and yields a silently wrong glyph rather than an error.
  const subEnd = sub + buf.readUInt16BE(sub + 2);
  const tableEnd = cmap.offset + cmap.length;
  if (subEnd > tableEnd || subEnd > buf.length) {
    throw new Error(`cmap: format 4 subtable claims ${subEnd - sub} bytes, table ends at ${tableEnd}`);
  }
  const segCountX2 = buf.readUInt16BE(sub + 6);
  if (segCountX2 < 2 || segCountX2 % 2 !== 0) {
    throw new Error(`cmap: segCountX2 is ${segCountX2}, which cannot describe whole segments`);
  }
  const segCount = segCountX2 / 2;
  const endCode = sub + 14;
  const startCode = endCode + 2 * segCount + 2;
  const idDelta = startCode + 2 * segCount;
  const idRangeOffset = idDelta + 2 * segCount;
  if (idRangeOffset + 2 * segCount > subEnd) {
    throw new Error(`cmap: ${segCount} segments need ${idRangeOffset + 2 * segCount - sub} bytes, subtable has ${subEnd - sub}`);
  }
  return (codePoint) => {
    if (codePoint < 0 || codePoint > 0xFFFF) return 0;
    for (let i = 0; i < segCount; i++) {
      if (codePoint > buf.readUInt16BE(endCode + i * 2)) continue;
      const start = buf.readUInt16BE(startCode + i * 2);
      // Segments are non-overlapping and ascending, so a code point below this
      // segment's start lies in a gap rather than in an earlier segment.
      if (codePoint < start) return 0;
      const delta = buf.readInt16BE(idDelta + i * 2);
      const range = buf.readUInt16BE(idRangeOffset + i * 2);
      if (range === 0) return (codePoint + delta) & 0xFFFF;
      const at = idRangeOffset + i * 2 + range + (codePoint - start) * 2;
      if (at + 2 > subEnd) return 0;
      const gid = buf.readUInt16BE(at);
      return gid === 0 ? 0 : (gid + delta) & 0xFFFF;
    }
    return 0;
  };
}

/**
 * Advances and left side bearings, one entry per glyph.
 *
 * `numberOfHMetrics` may be less than `numGlyphs`, in which case every glyph
 * past the last full entry shares that entry's advance and carries its own
 * side bearing in the compact run that follows. Neither shipped face does this
 * and the subset forces equality, so the branch is exercised by a synthetic
 * header in `tests/ttf.mjs` rather than by the real fonts.
 *
 * Exported for that test — the layout it checks is the part of `hmtx` no
 * in-repo input can reach.
 *
 * @param {Buffer} buf
 * @param {{hhea:{offset:number}, hmtx:{offset:number}}} tables
 * @param {number} numGlyphs
 * @returns {{advances:Uint16Array, sideBearings:Int16Array}}
 */
export function metricsOf(buf, tables, numGlyphs) {
  const hhea = must(tables, 'hhea');
  const hmtx = must(tables, 'hmtx');
  const count = buf.readUInt16BE(hhea.offset + 34);
  if (count < 1) throw new Error('hmtx: numberOfHMetrics is 0; the first advance is undefined');
  if (count > numGlyphs) {
    throw new Error(`hmtx: numberOfHMetrics ${count} exceeds the ${numGlyphs} glyphs in maxp`);
  }
  const advances = new Uint16Array(numGlyphs);
  const sideBearings = new Int16Array(numGlyphs);
  for (let gid = 0; gid < numGlyphs; gid++) {
    advances[gid] = buf.readUInt16BE(hmtx.offset + Math.min(gid, count - 1) * 4);
    sideBearings[gid] = gid < count
      ? buf.readInt16BE(hmtx.offset + gid * 4 + 2)
      : buf.readInt16BE(hmtx.offset + count * 4 + (gid - count) * 2);
  }
  return { advances, sideBearings };
}

/** Byte range occupied by one glyph in `glyf`, from `loca`. */
function glyphRange(buf, tables, gid) {
  const longForm = buf.readInt16BE(must(tables, 'head').offset + 50) !== 0;
  const loca = must(tables, 'loca').offset;
  return longForm
    ? [buf.readUInt32BE(loca + gid * 4), buf.readUInt32BE(loca + gid * 4 + 4)]
    : [buf.readUInt16BE(loca + gid * 2) * 2, buf.readUInt16BE(loca + gid * 2 + 2) * 2];
}

/**
 * The glyphs a composite glyph references. Accented Latin-1 characters are
 * built this way — `é` is `e` plus `acute` — so a subset that keeps the
 * composite without its components draws a blank box.
 */
function compositeRefs(buf, tables, gid) {
  const refs = [];
  const [lo, hi] = glyphRange(buf, tables, gid);
  if (hi - lo < 10) return refs;
  const at = must(tables, 'glyf').offset + lo;
  if (buf.readInt16BE(at) >= 0) return refs; // simple glyph
  let p = at + 10;
  const end = at + (hi - lo);
  while (p + 4 <= end) {
    const flags = buf.readUInt16BE(p);
    refs.push(buf.readUInt16BE(p + 2));
    p += 4 + (flags & 0x0001 ? 4 : 2);           // ARG_1_AND_2_ARE_WORDS
    if (flags & 0x0008) p += 2;                   // WE_HAVE_A_SCALE
    else if (flags & 0x0040) p += 4;              // WE_HAVE_AN_X_AND_Y_SCALE
    else if (flags & 0x0080) p += 8;              // WE_HAVE_A_TWO_BY_TWO
    if (!(flags & 0x0020)) break;                 // MORE_COMPONENTS
  }
  return refs;
}

// --- public readers -----------------------------------------------------------

/**
 * The face's true outline metrics, normalised for a PDF `/FontDescriptor`.
 * Everything here is read from the file; the one derived value is `stemV`,
 * which no TrueType table states and which the descriptor wants anyway.
 *
 * @param {Buffer} buf
 * @returns {{unitsPerEm:number, ascent:number, descent:number, capHeight:number,
 *   xMin:number, yMin:number, xMax:number, yMax:number, italicAngle:number,
 *   stemV:number, numGlyphs:number, weightClass:number}}
 */
export function fontDescriptor(buf) {
  const tables = parseTables(buf);
  const head = must(tables, 'head').offset;
  const hhea = must(tables, 'hhea').offset;
  const unitsPerEm = buf.readUInt16BE(head + 18);
  const os2 = must(tables, 'OS/2');
  const post = must(tables, 'post');
  const ascent = buf.readInt16BE(hhea + 4);
  const descent = buf.readInt16BE(hhea + 6);
  // OS/2 version 2 onward carries a real cap height; older files do not, and
  // the typographic ascender is the closest thing they have.
  const capHeight = os2.length >= 90
    ? buf.readInt16BE(os2.offset + 88)
    : ascent;
  const weightClass = buf.readUInt16BE(os2.offset + 4);
  return {
    unitsPerEm,
    ascent,
    descent,
    capHeight,
    xMin: buf.readInt16BE(head + 36),
    yMin: buf.readInt16BE(head + 38),
    xMax: buf.readInt16BE(head + 40),
    yMax: buf.readInt16BE(head + 42),
    italicAngle: buf.readInt32BE(post.offset + 4) / 65536,
    // No table states a vertical stem width. The weight class is the only
    // measure the file gives of how heavy the face is, and a descriptor value
    // derived from it is both stable across runs and honest about its origin:
    // 400 -> 80, 700 -> 140, the range the base-14 faces sit in.
    stemV: Math.round(weightClass * 0.2),
    numGlyphs: buf.readUInt16BE(must(tables, 'maxp').offset + 4),
    weightClass,
  };
}

/**
 * The glyph a code point maps to, or 0 when the face does not cover it. A font
 * with no readable `cmap` throws — that is a broken face, not a missing
 * character.
 *
 * @param {Buffer} buf
 * @param {number} codePoint
 * @returns {number}
 */
export function glyphFor(buf, codePoint) {
  return cmapLookup(buf, parseTables(buf))(codePoint);
}

/**
 * Advance width for every byte from 0 to 255, in units of 1000 em — the unit
 * `/Widths` is written in. Indexed by the byte a viewer reads, not by the
 * code point, because that is how `measure()` walks a folded string.
 *
 * @param {Buffer} buf
 * @returns {Int32Array} length 256
 */
export function winAnsiWidths(buf) {
  const tables = parseTables(buf);
  const head = must(tables, 'head').offset;
  const unitsPerEm = buf.readUInt16BE(head + 18);
  const numGlyphs = buf.readUInt16BE(must(tables, 'maxp').offset + 4);
  const lookup = cmapLookup(buf, tables);
  const { advances } = metricsOf(buf, tables, numGlyphs);
  const widths = new Int32Array(256);
  for (let byte = 0; byte < 256; byte++) {
    const codePoint = winAnsiToUnicode(byte);
    if (codePoint === null) continue; // undefined position: unreachable, width 0
    // `advances` is indexed by glyph id: an id past `numGlyphs` reads past the
    // typed array, yields undefined, rounds to NaN and stores 0 — a character
    // that measures as nothing and reflows the line it sits on.
    const gid = lookup(codePoint);
    if (gid >= numGlyphs) {
      throw new Error(`cmap: U+${codePoint.toString(16).toUpperCase()} maps to glyph ${gid}, `
        + `but maxp says there are ${numGlyphs}`);
    }
    widths[byte] = Math.round((advances[gid] * 1000) / unitsPerEm);
  }
  return widths;
}

// --- subset -------------------------------------------------------------------

/** Sum of a byte range read as big-endian uint32s, zero-padded to 4 bytes. */
function checksum(data) {
  const padded = Buffer.alloc(Math.ceil(data.length / 4) * 4);
  data.copy(padded);
  let sum = 0;
  for (let p = 0; p < padded.length; p += 4) sum = (sum + padded.readUInt32BE(p)) >>> 0;
  return sum >>> 0;
}

/**
 * The format 4 subtable covering `entries`, a `[codePoint, glyphId]` list
 * sorted by code point. Segments run to the next code point wherever the
 * mapping stays contiguous in both, and each segment otherwise carries its own
 * glyph ids in `glyphIdArray`, so any mapping — contiguous or not — is
 * expressible.
 */
function buildCmap(entries) {
  const segments = [];
  for (const [codePoint, gid] of entries) {
    const last = segments[segments.length - 1];
    // Code points may run together even when the glyph ids do not: the ids
    // travel in `glyphIdArray`, so nothing about a segment requires them to be
    // consecutive. Merging on code points alone keeps the segment count, and
    // with it the table, as small as the mapping allows.
    if (last && codePoint === last.end + 1) {
      last.end = codePoint;
      last.gids.push(gid);
    } else {
      segments.push({ start: codePoint, end: codePoint, gids: [gid] });
    }
  }
  // Format 4 must close on 0xFFFF. idDelta 1 sends it to glyph 0, `.notdef`,
  // which is what a lookup outside the kept range should land on.
  segments.push({ start: 0xFFFF, end: 0xFFFF, gids: null });

  const segCount = segments.length;
  const glyphCount = segments.reduce((n, s) => n + (s.gids ? s.gids.length : 0), 0);
  // 14 header + 2*segCount endCode + 2 pad + 3 blocks of 2*segCount, then the ids.
  const length = 16 + 8 * segCount + glyphCount * 2;
  const out = Buffer.alloc(length);
  out.writeUInt16BE(4, 0);                       // format
  out.writeUInt16BE(length, 2);
  out.writeUInt16BE(0, 4);                       // language
  out.writeUInt16BE(segCount * 2, 6);
  // searchRange/entrySelector/rangeShift are a binary-search hint: the byte
  // length of the largest block of `segCount` that is a power of two, its log,
  // and what is left over. The spec allows a reader to ignore them, but a
  // validator checks them, and they cost nothing to get right.
  const { value: block, exponent } = bitFloor(segCount);
  const searchRange = 2 * block;
  out.writeUInt16BE(searchRange, 8);
  out.writeUInt16BE(exponent, 10);
  out.writeUInt16BE(segCount * 2 - searchRange, 12);

  const endCode = 14;
  const reserved = endCode + segCount * 2;
  const startCode = reserved + 2;
  const idDelta = startCode + segCount * 2;
  const idRangeOffset = idDelta + segCount * 2;
  const glyphIdArray = idRangeOffset + segCount * 2;

  let glyphCursor = 0;
  segments.forEach((segment, i) => {
    out.writeUInt16BE(segment.end, endCode + i * 2);
    out.writeUInt16BE(segment.start, startCode + i * 2);
    if (segment.gids === null) {
      out.writeUInt16BE(1, idDelta + i * 2);
      out.writeUInt16BE(0, idRangeOffset + i * 2);
      return;
    }
    // idRangeOffset is relative to its own position: pointing at the shared
    // array that follows the whole block means the offset grows with how much
    // of the block still lies ahead, and shrinks as the segment index rises.
    out.writeUInt16BE(0, idDelta + i * 2);
    out.writeUInt16BE(2 * segCount - 2 * i + 2 * glyphCursor, idRangeOffset + i * 2);
    for (const gid of segment.gids) {
      out.writeUInt16BE(gid, glyphIdArray + glyphCursor * 2);
      glyphCursor += 1;
    }
  });
  out.writeUInt16BE(0, reserved);
  return out;
}

/**
 * The whole `cmap` table: a directory entry, then one subtable. Only the
 * Windows BMP encoding (3,1) is declared, because that is what `cmapLookup`
 * prefers and declaring a second record pointing at the same bytes would buy
 * nothing.
 */
function buildCmapTable(entries) {
  const subtable = buildCmap(entries);
  const table = Buffer.alloc(12 + subtable.length);
  table.writeUInt16BE(0, 0);      // version
  table.writeUInt16BE(1, 2);      // numTables
  table.writeUInt16BE(3, 4);      // platform: Windows
  table.writeUInt16BE(1, 6);      // encoding: BMP, Unicode
  table.writeUInt32BE(12, 8);     // subtable offset, from the start of cmap
  subtable.copy(table, 12);
  return table;
}

/**
 * A copy of `buf` holding `.notdef` plus every glyph reachable from the bytes
 * a report can emit, with the shaping tables removed.
 *
 * @param {Buffer} buf the source face
 * @returns {Buffer} the subset
 */
export function subset(buf) {
  const tables = parseTables(buf);
  const numGlyphs = buf.readUInt16BE(must(tables, 'maxp').offset + 4);
  const lookup = cmapLookup(buf, tables);

  // Every byte a folded string can carry names one code point; those are the
  // glyphs worth keeping, plus `.notdef` for a lookup that resolves to none.
  // An id past `numGlyphs` is checked here rather than left to fail later in
  // `hmtx`: it would surface as a typed-array type error naming a number and
  // nothing else, after the cmap, the glyf and the loca had all been built.
  const claim = (gid, source) => {
    if (gid >= numGlyphs) {
      throw new Error(`${source} names glyph ${gid}, but maxp says there are ${numGlyphs}`);
    }
  };
  const keep = new Set([0]);
  const entries = [];
  for (let byte = 0x20; byte <= 0xFF; byte++) {
    const codePoint = winAnsiToUnicode(byte);
    if (codePoint === null) continue;
    const gid = lookup(codePoint);
    if (gid) {
      claim(gid, `cmap U+${codePoint.toString(16).toUpperCase()}`);
      keep.add(gid);
      entries.push([codePoint, gid]);
    }
  }
  // Composites pull in their components, which may themselves be composites —
  // a worklist rather than a single pass, because accented characters are
  // nested on top of accented characters in some faces.
  const queue = [...keep];
  while (queue.length) {
    for (const ref of compositeRefs(buf, tables, queue.shift())) {
      claim(ref, 'composite glyph record');
      if (!keep.has(ref)) {
        keep.add(ref);
        queue.push(ref);
      }
    }
  }

  const ordered = [...keep].sort((a, b) => a - b);
  const remap = new Map(ordered.map((gid, index) => [gid, index]));

  // --- glyf + loca ---
  const glyfSource = must(tables, 'glyf').offset;
  const glyphBlobs = [];
  for (const gid of ordered) {
    const [lo, hi] = glyphRange(buf, tables, gid);
    // Even-length, zero-padded — a convention this writer always applies. The
    // subset always writes long-form loca (forced above), so nothing depends on
    // it for its own correctness; it keeps every glyph on a word boundary, as
    // the spec's own examples do.
    const blob = Buffer.alloc(((hi - lo + 1) & ~1) || 0);
    buf.copy(blob, 0, glyfSource + lo, glyfSource + hi);
    if (hi - lo >= 10 && blob.readInt16BE(0) < 0) {
      let p = 10;
      while (p + 4 <= blob.length) {
        const flags = blob.readUInt16BE(p);
        const target = remap.get(blob.readUInt16BE(p + 2));
        if (target === undefined) {
          throw new Error(`composite glyph ${gid} references glyph ${blob.readUInt16BE(p + 2)} outside the kept set`);
        }
        blob.writeUInt16BE(target, p + 2);
        p += 4 + (flags & 0x0001 ? 4 : 2);
        if (flags & 0x0008) p += 2;
        else if (flags & 0x0040) p += 4;
        else if (flags & 0x0080) p += 8;
        if (!(flags & 0x0020)) break;
      }
    }
    glyphBlobs.push(blob);
  }
  const glyf = Buffer.concat(glyphBlobs);
  const loca = Buffer.alloc((ordered.length + 1) * 4);
  let cursor = 0;
  glyphBlobs.forEach((blob, i) => {
    loca.writeUInt32BE(cursor, i * 4);
    cursor += blob.length;
  });
  loca.writeUInt32BE(cursor, ordered.length * 4);

  // --- hmtx ---
  const { advances, sideBearings } = metricsOf(buf, tables, numGlyphs);
  const hmtx = Buffer.alloc(ordered.length * 4);
  ordered.forEach((gid, i) => {
    hmtx.writeUInt16BE(advances[gid], i * 4);
    hmtx.writeInt16BE(sideBearings[gid], i * 4 + 2);
  });

  // --- head: long-form loca from here on, and the checksum adjustment reset ---
  const headTable = must(tables, 'head');
  const head = Buffer.alloc(headTable.length);
  buf.copy(head, 0, headTable.offset, headTable.offset + head.length);
  head.writeInt16BE(1, 50);
  head.writeUInt32BE(0, 8);

  // --- hhea ---
  // Only `numberOfHMetrics` is rewritten. The four derived fields alongside it
  // — `advanceWidthMax`, `minLeftSideBearing`, `minRightSideBearing`,
  // `xMaxExtent` — still describe the 1031-glyph source. They are informational
  // for a shaper, which a PDF never runs, and nothing in this package reads
  // them back; recomputing them would mean reading a bounding box for every
  // kept glyph to produce values no consumer consults.
  const hheaTable = must(tables, 'hhea');
  const hhea = Buffer.alloc(hheaTable.length);
  buf.copy(hhea, 0, hheaTable.offset, hheaTable.offset + hhea.length);
  hhea.writeUInt16BE(ordered.length, 34);

  // --- maxp ---
  const maxpTable = must(tables, 'maxp');
  const maxp = Buffer.alloc(maxpTable.length);
  buf.copy(maxp, 0, maxpTable.offset, maxpTable.offset + maxp.length);
  maxp.writeUInt16BE(ordered.length, 4);

  const rebuilt = new Map([
    // The cmap holds ids in the subset's own numbering, not the source's:
    // `entries` was collected before the renumbering happened.
    ['cmap', buildCmapTable(entries
      .map(([codePoint, gid]) => [codePoint, remap.get(gid)])
      .sort((a, b) => a[0] - b[0]))],
    ['glyf', glyf],
    ['head', head],
    ['hhea', hhea],
    ['hmtx', hmtx],
    ['loca', loca],
    ['maxp', maxp],
  ]);

  // Everything else rides through untouched, minus the shaping tables. `name`,
  // `OS/2` and `post` all stay: `fontDescriptor` reads two of them, and the
  // subset keeps the source's name records — which still describe the family
  // the face was cut from rather than the subset, as any hand-made subset does.
  const output = new Map();
  for (const [tag, table] of tables) {
    if (SHAPING_TABLES.has(tag)) continue;
    if (rebuilt.has(tag)) {
      output.set(tag, rebuilt.get(tag));
      continue;
    }
    const blob = Buffer.alloc(table.length);
    buf.copy(blob, 0, table.offset, table.offset + table.length);
    output.set(tag, blob);
  }
  for (const [tag, blob] of rebuilt) if (!output.has(tag)) output.set(tag, blob);

  // --- directory ---
  const tags = [...output.keys()].sort(); // ascending by tag, as a reader binary-searches
  const directory = Buffer.alloc(12 + tags.length * 16);
  directory.writeUInt32BE(SFNT_TRUETYPE, 0);
  directory.writeUInt16BE(tags.length, 4);
  const { value: block, exponent: maxPower } = bitFloor(tags.length);
  directory.writeUInt16BE(16 * block, 6);
  directory.writeUInt16BE(maxPower, 8);
  directory.writeUInt16BE(tags.length * 16 - 16 * block, 10);

  const offsets = new Map();
  let place = directory.length;
  for (const tag of tags) {
    offsets.set(tag, place);
    place += (output.get(tag).length + 3) & ~3;
  }
  const out = Buffer.alloc(place);
  directory.copy(out);
  tags.forEach((tag, i) => {
    const blob = output.get(tag);
    const record = 12 + i * 16;
    out.write(tag, record, 4, 'latin1');
    out.writeUInt32BE(checksum(blob), record + 4);
    out.writeUInt32BE(offsets.get(tag), record + 8);
    out.writeUInt32BE(blob.length, record + 12);
    blob.copy(out, offsets.get(tag));
  });

  // The spec's own sequence: with the adjustment still zero, sum the whole
  // file, then store 0xB1B0AFBA minus that sum into `head`. The directory
  // entry for `head` was written from the zeroed buffer and is deliberately
  // not recomputed afterwards — recomputing it would change the file sum the
  // stored value was derived from. This is the same order the shipped sources
  // were built in, which is what makes the invariant testable: the whole-file
  // sum of the result comes to 0xB1B0AFBA.
  const adjustment = (0xB1B0AFBA - checksum(out)) >>> 0;
  out.writeUInt32BE(adjustment, offsets.get('head') + 8);
  return out;
}
