// PDF fixture generator for tests/audit-pdf-extraction.mjs.
//
// A generator, not a corpus of committed binaries. A `.pdf` in git is an
// opaque blob: a reviewer cannot see what makes it different from its
// neighbours, and a fixture that silently stops exercising the property it
// claims will still be green forever. Everything here is written byte by byte
// so the case that breaks the engine is visible in the case that builds it,
// and every case carries the precondition that proves it really does what its
// name says.
//
// The generator is the inverse of the engine. Where lib/pdf-parse.mjs reads a
// document, this file writes one: cross-reference tables, cross-reference
// streams, object streams, Flate and LZW compression, the standard encodings
// with a /Differences override, ToUnicode CMaps, Identity-H CID fonts with
// two-byte codes, real RC4 encryption through the standard security handler,
// and the four refusal shapes (encrypted, scanned, truncated, not a PDF).
//
// Zero npm dependencies, and the same rule the product itself runs under:
// node:zlib and node:fs are the only modules that do work, node:path and
// node:url are used for locating the repository. MD5 and RC4 are implemented
// here rather than imported, because the encrypted fixture has to be a real
// encrypted document and a hand-rolled implementation is the only way to keep
// the import list at zero — both are locked against published test vectors in
// the suite, so neither can be quietly wrong.
//
// Nothing is ever written inside the repository. writeCorpus() refuses a
// destination under the package root outright.

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

// --- page geometry ------------------------------------------------------------
//
// A4 portrait, in points, as the report writer uses. Coordinates are chosen so
// a fixture can place a run at an exact horizontal offset and a test can
// compare the reconstructed columns against it.

export const PAGE_W = 595.28;
export const PAGE_H = 841.89;
export const MARGIN = 54;
export const COLUMN_GAP = 36;
export const LEADING = 16;

// --- string encoding ----------------------------------------------------------

// WinAnsi (PDF Annex D) is code page 1252: ASCII, the C1 range with its
// typographic specials, and Latin-1. Anything outside it is an error rather
// than a "?" fold, because a fixture that silently drops a character produces
// a document that is not the document the case claims to be.
const WINANSI = new Map([
  [0x20AC, 0x80], [0x201A, 0x82], [0x0192, 0x83], [0x201E, 0x84],
  [0x2026, 0x85], [0x2020, 0x86], [0x2021, 0x87], [0x02C6, 0x88],
  [0x2030, 0x89], [0x0160, 0x8A], [0x2039, 0x8B], [0x0152, 0x8C],
  [0x017D, 0x8E], [0x2018, 0x91], [0x2019, 0x92], [0x201C, 0x93],
  [0x201D, 0x94], [0x2022, 0x95], [0x2013, 0x96], [0x2014, 0x97],
  [0x02DC, 0x98], [0x2122, 0x99], [0x0161, 0x9A], [0x203A, 0x9B],
  [0x0153, 0x9C], [0x017E, 0x9E], [0x0178, 0x9F],
]);

/** Latin-1 (so one code unit becomes one byte) for a WinAnsi-encoded literal. */
export function winAnsi(value) {
  const out = [];
  for (const ch of value) {
    const cp = ch.codePointAt(0);
    if (cp >= 0x20 && cp <= 0x7E) out.push(cp);
    else if (cp >= 0xA0 && cp <= 0xFF) out.push(cp);
    else if (WINANSI.has(cp)) out.push(WINANSI.get(cp));
    else throw new Error(`make-pdf: U+${cp.toString(16).toUpperCase()} has no WinAnsi code`);
  }
  return Buffer.from(out);
}

/** Escape bytes into a PDF literal string operand. */
export function pdfString(bytes) {
  let out = '(';
  for (const byte of bytes) {
    if (byte === 0x28 || byte === 0x29 || byte === 0x5C) out += '\\' + String.fromCharCode(byte);
    else if (byte === 0x0A) out += '\\n';
    else if (byte === 0x0D) out += '\\r';
    else if (byte === 0x09) out += '\\t';
    else if (byte < 32 || byte > 126) out += '\\' + byte.toString(8).padStart(3, '0');
    else out += String.fromCharCode(byte);
  }
  return out + ')';
}

// --- stream filters -----------------------------------------------------------
//
// The generator encodes every filter the engine is required to read, so a
// filter with no encoder in the corpus has no proof that it works.

export const flate = (data) => zlib.deflateSync(data);

export function asciiHex(data) {
  return Buffer.from(data.toString('hex').toUpperCase() + '>', 'latin1');
}

export function ascii85(data) {
  let out = '';
  for (let i = 0; i < data.length; i += 4) {
    const n = Math.min(4, data.length - i);
    let v = 0;
    for (let k = 0; k < 4; k++) v = v * 256 + (data[i + k] ?? 0);
    if (n === 4 && v === 0) { out += 'z'; continue; }
    let chunk = '';
    for (let k = 0; k < 5; k++) {
      chunk = String.fromCharCode(33 + (v % 85)) + chunk;
      v = Math.floor(v / 85);
    }
    out += chunk.slice(0, n + 1);
  }
  return Buffer.from(out + '~>', 'latin1');
}

export function runLength(data) {
  const out = [];
  let i = 0;
  while (i < data.length) {
    let run = 1;
    while (run < 128 && i + run < data.length && data[i + run] === data[i]) run++;
    if (run >= 2) {
      out.push(257 - run, data[i]);
      i += run;
      continue;
    }
    let literal = 1;
    while (literal < 128 && i + literal < data.length) {
      if (i + literal + 1 < data.length && data[i + literal] === data[i + literal + 1]) break;
      literal++;
    }
    out.push(literal - 1);
    for (let k = 0; k < literal; k++) out.push(data[i + k]);
    i += literal;
  }
  out.push(128);
  return Buffer.from(out);
}

// LZW as PDF and TIFF define it: a 9-bit start, ClearCode 256, EOD 257, and a
// dictionary that grows from 258. The code width steps up when the next code to
// be assigned reaches 2^width (the early-change default widens one entry early,
// so both settings agree for any input that never crosses the boundary). Every
// fixture here is short enough to stay at 9 bits throughout, which lets the
// suite decode the stream as plain 9-bit codes and check the encoder against
// the specification rather than against itself.
export function lzw(data) {
  const bits = [];
  const push = (code, width) => {
    for (let i = width - 1; i >= 0; i--) bits.push((code >> i) & 1);
  };
  push(256, 9);
  const dict = new Map();
  let next = 258;
  let width = 9;
  let prefix = -1;
  for (const byte of data) {
    if (prefix < 0) { prefix = byte; continue; }
    const key = prefix * 256 + byte;
    const found = dict.get(key);
    if (found !== undefined) { prefix = found; continue; }
    push(prefix, width);
    dict.set(key, next);
    next++;
    if (next === (1 << width) - 1 || next === (1 << width)) width++;
    prefix = byte;
  }
  if (prefix >= 0) push(prefix, width);
  push(257, width);
  const out = Buffer.alloc(Math.ceil(bits.length / 8));
  bits.forEach((bit, i) => { out[i >> 3] |= bit << (7 - (i & 7)); });
  return out;
}

// --- MD5 and RC4, for the encrypted case --------------------------------------
//
// The encrypted fixture is a genuinely encrypted document, not a file with an
// /Encrypt dictionary bolted on: the content stream really is RC4 ciphertext
// under the standard security handler's key schedule, so an engine that ignored
// the dictionary and read the stream would get noise, and the suite can prove
// it by decrypting the bytes back to the content stream it started from.

const SHIFTS = [
  7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
  5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
];
// K[i] = floor(abs(sin(i + 1)) * 2^32) — computed rather than transcribed, so
// there is no chance of a typo in a 64-entry constant table.
const K = Array.from({ length: 64 }, (_, i) =>
  Math.floor(Math.abs(Math.sin(i + 1)) * 2 ** 32) >>> 0);

export function md5(input) {
  const msg = Buffer.isBuffer(input) ? input : Buffer.from(input, 'latin1');
  const total = (((msg.length + 8) >> 6) + 1) << 6;
  const padded = Buffer.alloc(total);
  msg.copy(padded);
  padded[msg.length] = 0x80;
  padded.writeUInt32LE((msg.length << 3) >>> 0, total - 8);
  padded.writeUInt32LE(Math.floor(msg.length / 536870912) >>> 0, total - 4);
  const M = new Uint32Array(16);
  let a0 = 0x67452301;
  let b0 = 0xefcdab89;
  let c0 = 0x98badcfe;
  let d0 = 0x10325476;
  for (let off = 0; off < total; off += 64) {
    for (let i = 0; i < 16; i++) M[i] = padded.readUInt32LE(off + i * 4);
    let A = a0;
    let B = b0;
    let C = c0;
    let D = d0;
    for (let i = 0; i < 64; i++) {
      let F;
      let g;
      if (i < 16) { F = (B & C) | (~B & D); g = i; }
      else if (i < 32) { F = (D & B) | (~D & C); g = (5 * i + 1) % 16; }
      else if (i < 48) { F = B ^ C ^ D; g = (3 * i + 5) % 16; }
      else { F = C ^ (B | ~D); g = (7 * i) % 16; }
      const sum = (F + A + K[i] + M[g]) >>> 0;
      A = D;
      D = C;
      C = B;
      B = (B + ((sum << SHIFTS[i]) | (sum >>> (32 - SHIFTS[i])))) >>> 0;
    }
    a0 = (a0 + A) >>> 0;
    b0 = (b0 + B) >>> 0;
    c0 = (c0 + C) >>> 0;
    d0 = (d0 + D) >>> 0;
  }
  const out = Buffer.alloc(16);
  out.writeUInt32LE(a0, 0);
  out.writeUInt32LE(b0, 4);
  out.writeUInt32LE(c0, 8);
  out.writeUInt32LE(d0, 12);
  return out;
}

export function rc4(key, data) {
  const s = new Uint8Array(256);
  for (let i = 0; i < 256; i++) s[i] = i;
  let j = 0;
  for (let i = 0; i < 256; i++) {
    j = (j + s[i] + key[i % key.length]) & 0xff;
    const swap = s[i];
    s[i] = s[j];
    s[j] = swap;
  }
  const out = Buffer.alloc(data.length);
  let i = 0;
  j = 0;
  for (let k = 0; k < data.length; k++) {
    i = (i + 1) & 0xff;
    j = (j + s[i]) & 0xff;
    const swap = s[i];
    s[i] = s[j];
    s[j] = swap;
    out[k] = data[k] ^ s[(s[i] + s[j]) & 0xff];
  }
  return out;
}

const PASSWORD_PAD = 0x28;
const padPassword = (pw) => {
  const bytes = Buffer.from(pw, 'latin1').subarray(0, 32);
  const out = Buffer.alloc(32, PASSWORD_PAD);
  bytes.copy(out);
  return out;
};

/** The V1/R2 standard-security key schedule, as PDF 1.7 §7.5.3 describes it. */
export function standardSecurity({ user, owner, permissions = -1, idFirst }) {
  const paddedUser = padPassword(user);
  const ownerKey = md5(padPassword(owner)).subarray(0, 5);
  const O = rc4(ownerKey, paddedUser);
  const perms = Buffer.alloc(4);
  perms.writeInt32LE(permissions, 0);
  const key = md5(Buffer.concat([paddedUser, O, perms, idFirst])).subarray(0, 5);
  const U = rc4(key, Buffer.alloc(32, PASSWORD_PAD));
  return { key, O, U, perms };
}

/** The per-object key for one stream or string (V1: key length + 5, capped 16). */
export function objectKey(key, num, gen = 0) {
  const suffix = Buffer.alloc(5);
  suffix.writeUIntLE(num, 0, 3);
  suffix.writeUIntLE(gen, 3, 2);
  return md5(Buffer.concat([key, suffix])).subarray(0, Math.min(key.length + 5, 16));
}

// --- ToUnicode CMaps ----------------------------------------------------------

const hex = (value, width) => value.toString(16).toUpperCase().padStart(width, '0');

/**
 * A ToUnicode CMap stream. `chars` is a list of `[code, unicodeString]` and
 * `ranges` a list of `[lo, hi, unicodeStart]`, so a fixture can be built with
 * only bfchar, only bfrange, or — as the contract requires — both.
 */
export function toUnicodeCMap({ chars = [], ranges = [], csLow = 0x0000, csHigh = 0xFFFF } = {}) {
  const lines = [
    '/CIDInit /ProcSet findresource begin',
    '12 dict begin',
    'begincmap',
    '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def',
    '/CMapName /Adobe-Identity-UCS def',
    '/CMapType 2 def',
    '1 begincodespacerange',
    `<${hex(csLow, 4)}> <${hex(csHigh, 4)}>`,
    'endcodespacerange',
  ];
  for (const [lo, hi] of chunks(chars.length || ranges.length, 100)) {
    const slice = chars.slice(lo, hi);
    if (slice.length) {
      lines.push(`${slice.length} beginbfchar`);
      for (const [code, value] of slice) {
        lines.push(`<${hex(code, 4)}> <${hex(value.codePointAt(0), 4)}>`);
      }
      lines.push('endbfchar');
    }
    const rslice = ranges.slice(lo, hi);
    if (rslice.length) {
      lines.push(`${rslice.length} beginbfrange`);
      for (const [first, last, start] of rslice) {
        lines.push(`<${hex(first, 4)}> <${hex(last, 4)}> <${hex(start, 4)}>`);
      }
      lines.push('endbfrange');
    }
  }
  lines.push('endcmap', 'CMapName currentdict /CMap defineresource pop', 'end', 'end');
  return Buffer.from(lines.join('\n') + '\n', 'latin1');
}

function* chunks(total, size) {
  for (let i = 0; i < Math.max(total, 1); i += size) yield [i, i + size];
}

// --- content streams ----------------------------------------------------------

const n = (value) => String(Math.round(value * 100) / 100);

/**
 * A content stream in which every visual line is one text object with an
 * explicit text matrix. Real documents do use Tm, and it makes each line's
 * position unambiguous, so a test can assert the reconstructed column against
 * the exact x the case placed the run at.
 */
export function textContent(lines, { font = 'F1', size = 12 } = {}) {
  const ops = [];
  for (const line of lines) {
    ops.push('BT');
    ops.push(`/${line.font || font} ${n(line.size || size)} Tf`);
    ops.push(`1 0 0 1 ${n(line.x ?? MARGIN)} ${n(line.y)} Tm`);
    ops.push(`${pdfString(line.bytes)} Tj`);
    ops.push('ET');
  }
  return Buffer.from(ops.join('\n') + '\n', 'latin1');
}

/** A content stream that draws an image and contains no text operator at all. */
export function imageContent(x = MARGIN, y = MARGIN) {
  return Buffer.from(
    `q\n${n(200)} 0 0 ${n(200)} ${n(x)} ${n(y)} cm\n/Im1 Do\nQ\n`, 'latin1');
}

// --- document assembly --------------------------------------------------------

/** A tiny 8x8 greyscale image, enough to be a real XObject. */
function imageObject(doc) {
  const num = doc.alloc();
  doc.set(num, '<< /Type /XObject /Subtype /Image /Width 8 /Height 8'
    + ' /ColorSpace /DeviceGray /BitsPerComponent 8 /Length 8',
  Buffer.from([0, 36, 72, 108, 144, 180, 216, 255]));
  return num;
}

function fontDescriptor(doc, name) {
  const num = doc.alloc();
  doc.set(num, '<< /Type /FontDescriptor /FontName /' + name
    + ' /Flags 4 /FontBBox [0 -200 1000 900] /ItalicAngle 0'
    + ' /Ascent 900 /Descent -200 /CapHeight 700 /StemV 80 >>');
  return num;
}

export const SIMPLE_FONT = (extra = '') =>
  '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding' + extra + ' >>';

export const DIFFERENCES_FONT = (differences) =>
  '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding'
  + ' << /Type /Encoding /BaseEncoding /WinAnsiEncoding'
  + ` /Differences [${differences}] >> >>`;

export const NO_ENCODING_FONT = (descriptor) =>
  '<< /Type /Font /Subtype /Type1 /BaseFont /QQQQQQ+SecretSubset'
  + ` /FirstChar 1 /LastChar 5 /Widths [500 500 500 500 500] /FontDescriptor ${descriptor} 0 R >>`;

export const TYPE0_FONT = (descendant, toUnicodeNum) =>
  '<< /Type /Font /Subtype /Type0 /BaseFont /TestIdentity /Encoding /Identity-H'
  + ` /DescendantFonts [${descendant}]`
  + (toUnicodeNum ? ` /ToUnicode ${toUnicodeNum} 0 R` : '')
  + ' >>';

export const CID_FONT = (descriptor) =>
  '<< /Type /Font /Subtype /CIDFontType2 /BaseFont /TestIdentity'
  + ' /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >>'
  + ` /FontDescriptor ${descriptor} 0 R >>`;

/** Collects numbered objects, then serialises them with a classic xref table. */
export class Doc {
  constructor({ version = '1.7' } = {}) {
    this.version = version;
    this.objects = new Map();
    this.next = 1;
  }

  alloc() { return this.next++; }

  set(num, body, stream) {
    this.objects.set(num, stream === undefined ? { body } : { body, stream });
  }

  add(body, stream) {
    const num = this.alloc();
    this.set(num, body, stream);
    return num;
  }
}

const latin1 = (text) => Buffer.from(text, 'latin1');

/**
 * Serialise a Doc.
 *
 * @param {Doc} doc
 * @param {object} options
 * @param {number} options.root          the /Root object number
 * @param {number} [options.encrypt]     the /Encrypt object number
 * @param {Buffer} [options.id]          16-byte file identifier
 * @param {number} [options.objStm]      object number to hold as the /ObjStm
 * @param {number[]} [options.inObjStm] object numbers to pack into it
 */
export function serialise(doc, {
  root, encrypt = null, id = null, objStm = null, inObjStm = null,
} = {}) {
  const packed = new Set(inObjStm || []);
  const numbers = [...doc.objects.keys()].sort((a, b) => a - b);
  const topLevel = numbers.filter((num) => !packed.has(num));
  const maxNum = Math.max(...numbers, objStm ?? 0);

  const chunks = [];
  let pos = 0;
  const offsets = new Map();
  const put = (buffer) => { chunks.push(buffer); pos += buffer.length; };

  put(latin1(`%PDF-${doc.version}\n`));
  // A binary comment marks the file as containing binary data, as every real
  // writer does; the high bytes are what distinguishes it.
  put(Buffer.from([0x25, 0xE2, 0xE3, 0xCF, 0xD3, 0x0A]));

  for (const num of topLevel) {
    const object = doc.objects.get(num);
    offsets.set(num, pos);
    if (object.stream === undefined) {
      put(latin1(`${num} 0 obj\n${object.body}\nendobj\n`));
    } else {
      // The dictionary body carries its own /Length, and it is checked against
      // the real byte count: a fixture whose declared length disagrees with its
      // stream is structurally broken, and a broken fixture is worse than none.
      const declared = Number(/\/Length (\d+)/.exec(object.body)?.[1]);
      if (declared !== object.stream.length) {
        throw new Error(
          `make-pdf: object ${num} declares /Length ${declared} but carries ${object.stream.length} bytes`);
      }
      put(latin1(`${num} 0 obj\n${object.body}\nstream\n`));
      put(object.stream);
      put(latin1('\nendstream\nendobj\n'));
    }
  }

  const xrefRows = new Map();
  for (const [num, offset] of offsets) xrefRows.set(num, { type: 1, second: offset, third: 0 });

  if (objStm !== null) {
    const members = [...packed].sort((a, b) => a - b);
    const bodies = members.map((num) => latin1(doc.objects.get(num).body));
    // Each pair is `<object number> <byte offset>`, and the offset is where
    // that object's bytes begin, counted from the first byte after `/First`.
    // It is not the object's index in the stream, which is what this used to
    // emit: a catalogue declared at offset 2 is read two bytes into its own
    // dictionary, so the file fails as malformed while looking well formed from
    // outside. `/First` below was already reasoned about correctly; this field
    // is its counterpart and had been missed.
    let relative = 0;
    const pairs = bodies.map((body, i) => {
      const pair = `${members[i]} ${relative}`;
      relative += body.length + 1; // the newline that separates two bodies
      return pair;
    });
    const head = pairs.join(' ');
    // /First is the offset of the first object body inside the decoded stream,
    // so it is the length of the pair list *including* the newline that ends it
    // — not the total size of the bodies, which is the other easy mistake.
    const first = Buffer.byteLength(head, 'latin1') + 1;
    const payload = Buffer.concat([
      latin1(head + '\n'),
      ...bodies.map((body) => Buffer.concat([body, latin1('\n')])),
    ]);
    offsets.set(objStm, pos);
    // The object stream is an object in the file like any other and needs its
    // own cross-reference row. `xrefRows` was last written above, before this
    // object existed, so without this row the stream is marked free: a reader
    // then cannot resolve it, and every object packed inside it — including the
    // catalogue — becomes unreachable while the cross-reference looks complete.
    xrefRows.set(objStm, { type: 1, second: pos, third: 0 });
    put(latin1(`${objStm} 0 obj\n<< /Type /ObjStm /N ${members.length}`
      + ` /First ${first} /Length ${payload.length} >>\nstream\n`));
    put(payload);
    put(latin1('\nendstream\nendobj\n'));
    members.forEach((num, index) => xrefRows.set(num, { type: 2, second: objStm, third: index }));
  }

  const xrefNum = maxNum + 1;
  let startxref;
  if (objStm !== null) {
    // A cross-reference stream: W = [1 4 1], one byte of type, four of offset
    // (or of object-stream number), one of generation (or of index).
    //
    // It also takes a row of its own, at the offset `startxref` names. `pos` is
    // that offset here: the rows are built below and the object is written
    // immediately after, with nothing in between.
    xrefRows.set(xrefNum, { type: 1, second: pos, third: 0 });
    const rows = [];
    for (let num = 0; num <= xrefNum; num++) {
      const row = xrefRows.get(num);
      if (!row) { rows.push([0, 0, 255]); continue; }
      rows.push([row.type, row.second, row.third]);
    }
    const table = Buffer.alloc(rows.length * 6);
    rows.forEach(([type, second, third], i) => {
      table[i * 6] = type;
      table.writeUInt32BE(second, i * 6 + 1);
      table[i * 6 + 5] = third;
    });
    startxref = pos;
    put(latin1(`${xrefNum} 0 obj\n<< /Type /XRef /Size ${xrefNum + 1} /W [1 4 1]`
      + ` /Root ${root} 0 R${trailerExtras(encrypt, id)}`
      + ` /Length ${table.length} >>\nstream\n`));
    put(table);
    put(latin1('\nendstream\nendobj\n'));
  } else {
    startxref = pos;
    put(latin1(`xref\n0 ${maxNum + 1}\n`));
    put(latin1('0000000000 65535 f \n'));
    for (let num = 1; num <= maxNum; num++) {
      const row = xrefRows.get(num);
      put(row
        ? latin1(`${String(row.second).padStart(10, '0')} ${String(row.third).padStart(5, '0')} n \n`)
        : latin1('0000000000 65535 f \n'));
    }
    put(latin1(`trailer\n<< /Size ${maxNum + 1} /Root ${root} 0 R${trailerExtras(encrypt, id)} >>\n`));
  }
  put(latin1(`startxref\n${startxref}\n%%EOF\n`));

  return Buffer.concat(chunks);
}

function trailerExtras(encrypt, id) {
  let out = '';
  if (encrypt !== null) out += ` /Encrypt ${encrypt} 0 R`;
  if (id) {
    const value = id.toString('hex').toUpperCase();
    out += ` /ID [<${value}> <${value}>]`;
  }
  return out;
}

// --- the corpus ---------------------------------------------------------------
//
// Fixture copy. Deliberate rule-violating text: the spelling rule, the doubled
// word, the ambiguous date and the shouted word are the four the integration
// test compares between a PDF and a .txt twin. Each line carries its own
// suppression so the repository's self-scan stays clean.

export const PROSE = {
  // ue:ignore all  (deliberate fixture copy — the rules must see this, the self-scan must not)
  clean: 'The delegation reviewed the draft of the resolution.',
  // ue:ignore all
  spelling: 'The organization published the report on schedule.',
  // ue:ignore all
  doubled: 'The delegation reviewed the the draft of the resolution.',
  // ue:ignore all
  date: 'The report was issued on 10/07/2026 and circulated widely.',
  // ue:ignore all
  shouted: 'The delegation arrived PRIOR to the opening of the session.',
  // All four defects on one visual line, so the PDF unit and the .txt unit are
  // the same string and the rule layer has no excuse to differ.
  // ue:ignore all
  combined: 'The organization reviewed the the report dated 10/07/2026 before PRIOR consultation.',
  // ue:ignore all
  quoted: 'The chair read: "The organization will publish the report."',
};

/** Page 1..n of the multi-page case: one distinguishable line each. */
export const PAGE_LINES = [
  // ue:ignore all  (deliberate fixture copy)
  'Page one carries the first sentence of the report.',
  // ue:ignore all
  'Page two carries the second sentence of the report.',
  // ue:ignore all
  'Page three carries the third sentence of the report.',
];

// The two-column page. Left column then right column, four lines each, with a
// gap in the middle of the page so the two columns cannot be confused.
export const COLUMN_LEFT = [
  // ue:ignore all  (deliberate fixture copy)
  'The first column opens here.',
  // ue:ignore all
  'The second column line follows.',
  // ue:ignore all
  'A third line closes the column.',
  // ue:ignore all
  'The fourth line ends the column.',
];
export const COLUMN_RIGHT = [
  // ue:ignore all  (deliberate fixture copy)
  'The right column starts here.',
  // ue:ignore all
  'Its second line is set beside the left.',
  // ue:ignore all
  'A third line completes the right column.',
  // ue:ignore all
  'The fourth line closes the right column.',
];

// `positions`: three lines with three different horizontal offsets, so the
// reconstructed columns are provable rather than assumed.
export const POSITION_LINES = [
  // ue:ignore all  (deliberate fixture copy, not a sentence the tool should read)
  { text: 'The first run starts at the left margin.', x: MARGIN },
  // ue:ignore all
  { text: 'The second run is indented by one gap.', x: MARGIN + COLUMN_GAP },
  // ue:ignore all
  { text: 'The third run is indented by two gaps.', x: MARGIN + 2 * COLUMN_GAP },
  // ue:ignore all
  { text: 'The fourth run returns to the margin.', x: MARGIN },
];

// `two-column`: the left column occupies the margin and the right column starts
// past the midpoint, so a reader of the bytes can tell the columns apart.
export const RIGHT_COLUMN_X = 320;

// ---------------------------------------------------------------------------
// The four fixtures that close out the decode register.
//
// `two-column-narrow` and `hanging-indent` are a PAIR, and neither means
// anything without the other. They are the boundary of
// `GUTTER_MIN_FRACTION` in lib/pdf-text.mjs, which is a fraction of the page
// width: one fixture sits just above the floor and must be split, the other
// sits just below it and must not be. Raising the floor breaks the first and
// lowering it breaks the second, so the number cannot drift in either
// direction without a test saying so. (The pair exists because the original
// threshold of 0.035 — 20.83pt on this page — left every real two-column
// layout with a gutter of 8 to 20pt unsplit, which is where the copy of a
// journal or a magazine is actually written.)
//
// Widths below are exact, not measured: lib/pdf-text.mjs gives a standard-14
// font with no /Widths array its per-font default, which is 556/1000 em for
// Helvetica, so a glyph at 10pt is 5.56pt wide whatever it is. Every length
// here is a character count times that.
// ---------------------------------------------------------------------------

export const NARROW_SIZE = 10;
export const NARROW_GLYPH_PT = 5.56;
// Four left-column lines, each exactly 29 characters, so the union of the
// left column ends at one known x rather than at whatever the ragged edge
// happens to reach.
export const NARROW_LEFT = [
  // ue:ignore all  (deliberate fixture copy)
  'The narrow column opens here.',
  // ue:ignore all
  'Its second line sets text.',
  // ue:ignore all
  'A third line runs down now.',
  // ue:ignore all
  'Fourth line of the left ends.',
];
export const NARROW_LEFT_CHARS = 29;
export const NARROW_LEFT_END_X = 215.24;  // 54 + 29 * 5.56
export const NARROW_GUTTER_PT = 12;       // 0.0202 of the page width
export const NARROW_RIGHT_X = 227.24;     // 12pt past the left column's edge
export const NARROW_RIGHT = [
  // ue:ignore all  (deliberate fixture copy)
  'The right column begins its own subject here.',
  // ue:ignore all
  'Its second line sits beside the left one.',
  // ue:ignore all
  'A third line completes the right hand part.',
  // ue:ignore all
  'The fourth line of the right column ends it.',
];

// `hanging-indent`: a numbered list, the number in the margin and the entry
// beside it. The numbers run "[1]" to "[16]", so the widest is four
// characters and the union of the left group stops at 76.24 — leaving a gap
// of 7.76pt, which is below the 8.93pt floor and above the 7.14pt one. This
// is a single column and must read as one line per row.
export const HANGING_SIZE = 10;
export const HANGING_ROWS = 16;
export const HANGING_TEXT_X = 84;
export const HANGING_NUM_END_X = 76.24;   // 54 + 4 * 5.56, from "[16]"
export const HANGING_GAP_PT = 7.76;
export const HANGING_ENTRIES = [
  // ue:ignore all  (deliberate fixture copy)
  'A reference entry of ordinary length for the list.',
  // ue:ignore all
  'A second entry that stands beside its own number.',
  // ue:ignore all
  'A third entry written to the same hanging indent.',
  // ue:ignore all
  'A fourth entry, and the rest repeat the pattern.',
  // ue:ignore all
  'A fifth entry carrying on with the same shape here.',
  // ue:ignore all
  'A sixth entry set at the same offset as the rest.',
  // ue:ignore all
  'A seventh entry with no unusual spacing at all.',
  // ue:ignore all
  'An eighth entry of the sort a bibliography holds.',
  // ue:ignore all
  'A ninth entry written to fill the sixteenth row.',
  // ue:ignore all
  'A tenth entry with the same indent as the others.',
  // ue:ignore all
  'An eleventh entry continuing the list of items.',
  // ue:ignore all
  'A twelfth entry of the same measured kind here.',
  // ue:ignore all
  'A thirteenth entry standing in for the rest.',
  // ue:ignore all
  'A fourteenth entry written in the same manner.',
  // ue:ignore all
  'A fifteenth entry near the end of this fixture.',
  // ue:ignore all
  'A sixteenth and last entry closing the list off.',
];

// `rotated-page`: `/Rotate 90` on the page, with the copy drawn turned in the
// content stream to compensate — which is how a landscape export actually
// reaches an extractor. On a page displayed a quarter turn clockwise, content
// +y runs right and content +x runs down, so the text advances along +y and
// each displayed line steps along +x.
export const ROTATE_DEGREES = 90;
export const ROTATED_LINES = [
  // ue:ignore all  (deliberate fixture copy)
  'First displayed line of the column.',
  // ue:ignore all
  'Second displayed line of the column.',
  // ue:ignore all
  'Third displayed line of the column.',
];

// `non-latin`: eighteen byte codes whose Unicode is only in the /ToUnicode
// CMap — nine Cyrillic, six Greek including a precomposed accent, two spaces
// and one accented Latin letter. A byte-wise reading would produce letters
// from WinAnsi instead, and the space would survive by luck while nothing
// else did.
export const NON_LATIN_TEXT = 'Делегация Ελλάδα é';
export const NON_LATIN_MAP = [
  [0x41, 'Д'], [0x42, 'е'], [0x43, 'л'], [0x44, 'е'], [0x45, 'г'],
  [0x46, 'а'], [0x47, 'ц'], [0x48, 'и'], [0x49, 'я'],
  [0x4A, ' '],
  [0x4B, 'Ε'], [0x4C, 'λ'], [0x4D, 'λ'], [0x4E, 'ά'], [0x4F, 'δ'], [0x50, 'α'],
  [0x51, ' '],
  [0x52, 'é'],
];
export const NON_LATIN_CODES = Buffer.from(NON_LATIN_MAP.map(([code]) => code));

// `vertical-gap`: two lines six leadings apart — 96pt, a whole paragraph's
// worth of whitespace — which must still come back as two units. This is the
// lock on the module header's account of itself in lib/pdf-text.mjs: the
// extractor never measures a vertical gap, so no size of gap may ever merge
// two lines, and a comment claiming otherwise would fail here.
export const VERTICAL_GAP_PT = 96;
export const VERTICAL_GAP_LINES = [
  // ue:ignore all  (deliberate fixture copy)
  'The first paragraph of this fixture stands alone.',
  // ue:ignore all
  'The second paragraph follows a very large gap.',
];

const SIMPLE_LINES = (texts, y = 700) => texts.map((text, i) => ({
  bytes: winAnsi(text), x: MARGIN, y: y - i * LEADING,
}));

// The control document's two lines, shared by plain-untagged and by all five
// filter cases. Declared before the builders that use it, and exported so the
// suite asserts against the same list rather than restating it.
export const FILTER_COPY = [PROSE.clean, PROSE.doubled];

/**
 * Build one case by name and return the bytes. Exported so a case can be
 * rebuilt in a scratch copy of the repository when a mutation has to be shown
 * to turn the suite red without touching the committed corpus.
 */
export function build(name) {
  switch (name) {
    case 'plain-untagged': return buildPlain();
    case 'flate': return buildFiltered('flate');
    case 'lzw': return buildFiltered('lzw');
    case 'ascii85': return buildFiltered('ascii85');
    case 'asciihex': return buildFiltered('asciihex');
    case 'runlength': return buildFiltered('runlength');
    case 'differences': return buildDifferences();
    case 'to-unicode': return buildToUnicode();
    case 'no-to-unicode': return buildNoToUnicode();
    case 'identity-h': return buildIdentityH();
    case 'object-streams': return buildObjectStreams();
    case 'multi-page': return buildMultiPage();
    case 'two-column': return buildTwoColumn();
    case 'two-column-narrow': return buildTwoColumnNarrow();
    case 'hanging-indent': return buildHangingIndent();
    case 'rotated-page': return buildRotatedPage();
    case 'non-latin': return buildNonLatin();
    case 'vertical-gap': return buildVerticalGap();
    case 'positions': return buildPositions();
    case 'quoted-paragraph': return buildQuotedParagraph();
    case 'rules-invisibility': return buildRulesInvisibility();
    case 'split-word': return buildSplitWord();
    case 'second-page-undecodable': return buildSecondPageUndecodable();
    case 'scanned': return buildScanned();
    case 'encrypted': return buildEncrypted();
    case 'truncated': return buildTruncated();
    case 'not-a-pdf': return buildNotAPdf();
    default: throw new Error(`make-pdf: unknown case ${name}`);
  }
}

const ID = Buffer.from('00112233445566778899aabbccddeeff', 'hex');

/**
 * A one-page document around a single content stream. The font resource is a
 * parameter so a case can swap in a /Differences encoding or a ToUnicode CMap
 * without a second document shape.
 */
/** The name each filter carries in a PDF dictionary. */
export const FILTER_NAMES = {
  flate: 'FlateDecode',
  lzw: 'LZWDecode',
  ascii85: 'ASCII85Decode',
  asciihex: 'ASCIIHexDecode',
  runlength: 'RunLengthDecode',
};

function simpleDocument(content, { filter = null, font = null, rotate = null } = {}) {
  const doc = new Doc();
  // `font` may be a dictionary body or a builder, so a case that needs a
  // sibling object (a ToUnicode CMap, say) can allocate one first and refer
  // to it by number.
  const fontBody = typeof font === 'function' ? font(doc) : font;
  const fontNum = fontBody ? doc.add(fontBody) : doc.add(SIMPLE_FONT());
  const data = filter ? filterStream(content, filter) : content;
  const filterEntry = filter ? ` /Filter /${FILTER_NAMES[filter]}` : '';
  const contentNum = doc.add(`<<${filterEntry} /Length ${data.length} >>`, data);
  const pagesNum = doc.alloc();
  const pageNum = doc.alloc();
  doc.set(pageNum, `<< /Type /Page /Parent ${pagesNum} 0 R`
    + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
    + (rotate === null ? '' : ` /Rotate ${rotate}`)
    + ` /Resources << /ProcSet [/PDF /Text] /Font << /F1 ${fontNum} 0 R >> >>`
    + ` /Contents ${contentNum} 0 R >>`);
  doc.set(pagesNum, `<< /Type /Pages /Kids [${pageNum} 0 R] /Count 1 >>`);
  const root = doc.add(`<< /Type /Catalog /Pages ${pagesNum} 0 R >>`); // ue:ignore UE-SP001  (a PDF object name, not prose)
  return { doc, root, pagesNum, pageNum, contentNum, fontNum };
}

function filterStream(content, filter) {
  switch (filter) {
    case 'flate': return flate(content);
    case 'lzw': return lzw(content);
    case 'ascii85': return ascii85(content);
    case 'asciihex': return asciiHex(content);
    case 'runlength': return runLength(content);
    default: throw new Error(`make-pdf: no encoder for ${filter}`);
  }
}

// --- the accepted cases -------------------------------------------------------

function buildPlain() {
  const content = textContent(SIMPLE_LINES(FILTER_COPY));
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

// The five filters carry exactly the control document's copy, so "the same
// text through five encodings" is a claim about the encoding and nothing else.
// The second line is the doubled word on purpose: it is a defect a .txt reader
// finds, so it is worth watching survive every filter.
function buildFiltered(filter) {
  const content = textContent(SIMPLE_LINES(FILTER_COPY));
  const { doc, root } = simpleDocument(content, { filter });
  return serialise(doc, { root, id: ID });
}

/**
 * A /Differences override. Codes 65 and 66 are "A" and "B" in WinAnsi; the
 * override maps them to /Aacute and /Ccedilla, so the text a reader sees is
 * "ÁÇ" and an extractor that falls back to the base encoding returns "AB".
 */
function buildDifferences() {
  const content = textContent([{ bytes: Buffer.from([65, 66]), x: MARGIN, y: 700 }]);
  const { doc, root } = simpleDocument(content, {
    font: DIFFERENCES_FONT('65 /Aacute 66 /Ccedilla'),
  });
  return serialise(doc, { root, id: ID });
}

/**
 * A ToUnicode CMap carrying both bfchar and bfrange. Codes 0x41 and 0x42 are
 * "A" and "B" in WinAnsi and map to "XY"; codes 0x50..0x52 are "PQR" and map
 * to "abc" through a bfrange. The CMap hangs off the page's own font resource,
 * so the document carries a real /ToUnicode entry rather than a stray
 * dictionary nothing points at.
 */
function buildToUnicode() {
  const cmap = toUnicodeCMap({
    chars: [[0x41, 'X'], [0x42, 'Y']],
    ranges: [[0x50, 0x52, 0x61]],
  });
  const content = textContent([{ bytes: Buffer.from([0x41, 0x42, 0x50, 0x51, 0x52]), x: MARGIN, y: 700 }]);
  const { doc, root } = simpleDocument(content, {
    font: (builder) => {
      const cmapNum = builder.add(
        `<< /Length ${cmap.length} >>`, cmap);
      return '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica'
        + ` /Encoding /WinAnsiEncoding /ToUnicode ${cmapNum} 0 R >>`;
    },
  });
  return serialise(doc, { root, id: ID });
}

/**
 * A subsetted font with no /Encoding and no /ToUnicode: nothing in the file
 * says what its byte codes mean, so the document must be refused rather than
 * guessed at. The content uses codes 0x01..0x05, which no standard encoding
 * defines, so a reader that assumed one would produce control characters
 * rather than copy.
 */
function buildNoToUnicode() {
  const content = textContent([{ bytes: Buffer.from([1, 2, 3, 4, 5]), x: MARGIN, y: 700 }]);
  const { doc, root } = simpleDocument(content, {
    font: (builder) => {
      const descriptor = fontDescriptor(builder, 'QQQQQQ+SecretSubset');
      return NO_ENCODING_FONT(descriptor);
    },
  });
  return serialise(doc, { root, id: ID });
}

/**
 * Identity-H: every character code is two bytes. The ToUnicode CMap maps CID
 * 0x03 to "G", CID 0x01A7 to "a" and CIDs 0x0030..0x0032 to "xyz" through a
 * bfrange — none of which is the code's own value, and the high bytes are NUL
 * for two of the four characters, so a byte-wise reading cannot work at all.
 */
function buildIdentityH() {
  const cmap = toUnicodeCMap({
    chars: [[0x0003, 'G'], [0x01A7, 'a']],
    ranges: [[0x0030, 0x0032, 0x78]],
  });
  const content = textContent([{
    bytes: Buffer.from([0x00, 0x03, 0x01, 0xA7, 0x00, 0x30, 0x00, 0x31, 0x00, 0x32]),
    x: MARGIN,
    y: 700,
  }]);
  const { doc, root } = simpleDocument(content, {
    font: (builder) => {
      const descriptor = fontDescriptor(builder, 'TestIdentity');
      const descendant = builder.add(CID_FONT(descriptor));
      const cmapNum = builder.add(`<< /Length ${cmap.length} >>`, cmap);
      return TYPE0_FONT(`${descendant} 0 R`, cmapNum);
    },
  });
  return serialise(doc, { root, id: ID });
}

/**
 * A document whose structure lives in a cross-reference stream and an object
 * stream: there is no `xref` table anywhere, the catalog and the page tree are
 * inside the /ObjStm payload, and the only way in is to read the stream.
 */
function buildObjectStreams() {
  const doc = new Doc();
  const font = doc.add(SIMPLE_FONT());
  const content = textContent(SIMPLE_LINES([PROSE.clean]));
  const contentNum = doc.add(`<< /Length ${content.length} >>`, content);
  const objStmNum = doc.alloc();
  const pagesNum = doc.alloc();
  const pageNum = doc.alloc();
  const root = doc.add(`<< /Type /Catalog /Pages ${pagesNum} 0 R >>`); // ue:ignore UE-SP001  (a PDF object name, not prose)
  doc.set(pageNum, `<< /Type /Page /Parent ${pagesNum} 0 R`
    + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
    + ` /Resources << /ProcSet [/PDF /Text] /Font << /F1 ${font} 0 R >> >>`
    + ` /Contents ${contentNum} 0 R >>`);
  doc.set(pagesNum, `<< /Type /Pages /Kids [${pageNum} 0 R] /Count 1 >>`);
  return serialise(doc, { root, id: ID, objStm: objStmNum, inObjStm: [root, pagesNum, pageNum] });
}

/** Three pages, one distinguishable line each, so page attribution is provable. */
function buildMultiPage() {
  const doc = new Doc();
  const font = doc.add(SIMPLE_FONT());
  const pagesNum = doc.alloc();
  const kids = [];
  for (let i = 0; i < PAGE_LINES.length; i++) {
    const content = textContent(SIMPLE_LINES([PAGE_LINES[i]]));
    const contentNum = doc.add(`<< /Length ${content.length} >>`, content);
    const pageNum = doc.alloc();
    doc.set(pageNum, `<< /Type /Page /Parent ${pagesNum} 0 R`
      + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
      + ` /Resources << /ProcSet [/PDF /Text] /Font << /F1 ${font} 0 R >> >>`
      + ` /Contents ${contentNum} 0 R >>`);
    kids.push(pageNum);
  }
  doc.set(pagesNum, `<< /Type /Pages /Kids [${kids.map((k) => `${k} 0 R`).join(' ')}]`
    + ` /Count ${kids.length} >>`);
  const root = doc.add(`<< /Type /Catalog /Pages ${pagesNum} 0 R >>`); // ue:ignore UE-SP001  (a PDF object name, not prose)
  return serialise(doc, { root, id: ID });
}

/** Two text columns per page, left column first in reading order. */
function buildTwoColumn() {
  const left = COLUMN_LEFT.map((text, i) => ({
    bytes: winAnsi(text), x: MARGIN, y: 700 - i * LEADING,
  }));
  const right = COLUMN_RIGHT.map((text, i) => ({
    bytes: winAnsi(text), x: RIGHT_COLUMN_X, y: 700 - i * LEADING,
  }));
  // Emitted in column order, not in y order: the right column's first line is
  // written to the stream after the left column's last line.
  const content = textContent([...left, ...right]);
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/** Four runs at four different x offsets, so the columns are provable. */
function buildPositions() {
  const content = textContent(POSITION_LINES.map((line, i) => ({
    bytes: winAnsi(line.text), x: line.x, y: 700 - i * LEADING,
  })));
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/**
 * A normal paragraph above a visually indented, quotation-marked paragraph. In
 * a .txt the second paragraph is quoted material and is never checked; in a PDF
 * it is indistinguishable, so it must come back as authored copy and be
 * checked. The suite asserts both halves.
 */
function buildQuotedParagraph() {
  const content = textContent([
    { bytes: winAnsi(PROSE.spelling), x: MARGIN, y: 700 },
    { bytes: winAnsi(PROSE.quoted), x: MARGIN + COLUMN_GAP, y: 700 - LEADING * 3 },
  ]);
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/** One visual line carrying all four rule defects, for the .txt twin comparison. */
function buildRulesInvisibility() {
  const content = textContent([{ bytes: winAnsi(PROSE.combined), x: MARGIN, y: 700 }]);
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/**
 * A doubled word that straddles a visual line break: "the" ends one line and
 * begins the next. No rule may report a position that is not in the document,
 * so the assertion on this case is about the position, not about whether the
 * rule fires — the contract does not say whether a word may span a line.
 */
function buildSplitWord() {
  const content = textContent([
    { bytes: winAnsi('The delegation reviewed the'), x: MARGIN, y: 700 },
    { bytes: winAnsi('the draft of the resolution.'), x: MARGIN, y: 700 - LEADING },
  ]);
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/**
 * The narrow-gutter half of the `GUTTER_MIN_FRACTION` boundary pair: twelve
 * points of gutter, which is 0.0202 of this page's width. It sits below the
 * 0.035 floor the constant used to carry and above the 0.015 floor it now
 * carries, so it reads column by column only while the number stays where the
 * measurement put it. The content stream is written column by column as an
 * engine would have to reconstruct it, so a page that comes back row by row
 * fails loudly rather than quietly.
 */
function buildTwoColumnNarrow() {
  const left = NARROW_LEFT.map((text, i) => ({
    bytes: winAnsi(text), x: MARGIN, y: 700 - i * LEADING, size: NARROW_SIZE,
  }));
  const right = NARROW_RIGHT.map((text, i) => ({
    bytes: winAnsi(text), x: NARROW_RIGHT_X, y: 700 - i * LEADING, size: NARROW_SIZE,
  }));
  const content = textContent([...left, ...right]);
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/**
 * The other half of that pair: a numbered list, one visual line per row, whose
 * widest uncovered band of x is 7.76pt — below the floor. Splitting this page
 * would break every row of the list in two and put a line number on half an
 * entry, so it is the fixture that stops the floor being lowered past the
 * point where an indent and a column stop being distinguishable.
 */
function buildHangingIndent() {
  const lines = [];
  for (let i = 0; i < HANGING_ROWS; i++) {
    lines.push({
      bytes: winAnsi(`[${i + 1}]`), x: MARGIN, y: 700 - i * LEADING, size: HANGING_SIZE,
    });
    lines.push({
      bytes: winAnsi(HANGING_ENTRIES[i]), x: HANGING_TEXT_X,
      y: 700 - i * LEADING, size: HANGING_SIZE,
    });
  }
  const { doc, root } = simpleDocument(textContent(lines));
  return serialise(doc, { root, id: ID });
}

/**
 * A page that says `/Rotate 90` and draws its copy turned to compensate, which
 * is how a landscape export reaches an extractor: the screen shows the columns
 * upright, the content stream has them running up the page.
 *
 * The copy and its order are what this case locks. The line structure is not:
 * in content space all three displayed lines share one baseline, so they come
 * back as a single reconstructed line. That is a real limitation, it is
 * asserted below rather than left to be discovered, and fixing it means
 * applying the page rotation to every run before lines are grouped.
 */
function buildRotatedPage() {
  const content = Buffer.from(ROTATED_LINES.map((text, i) => {
    const drawn = textContent([{ bytes: winAnsi(text), x: 0, y: 0, size: 10 }]);
    // content +y runs right on screen, content +x runs down it.
    return `q 0 1 -1 0 ${MARGIN + i * 14} 120 cm\n${drawn.toString('latin1')}Q\n`;
  }).join(''), 'latin1');
  const { doc, root } = simpleDocument(content, { rotate: ROTATE_DEGREES });
  return serialise(doc, { root, id: ID });
}

/**
 * Two lines with a very large vertical gap between them. The extractor never
 * measures a vertical gap, so both must survive as their own unit: a paragraph
 * break and an ordinary line break are the same thing here, by design rather
 * than by omission.
 */
function buildVerticalGap() {
  const content = textContent(VERTICAL_GAP_LINES.map((text, i) => ({
    bytes: winAnsi(text),
    x: MARGIN,
    y: i === 0 ? 700 : 700 - LEADING - VERTICAL_GAP_PT,
  })));
  const { doc, root } = simpleDocument(content);
  return serialise(doc, { root, id: ID });
}

/**
 * Cyrillic, Greek and an accented Latin letter, all of it carried only by the
 * /ToUnicode CMap. The byte codes are ordinary WinAnsi codes, so a reader that
 * ignored the CMap would confidently return Latin letters — the same failure
 * shape as a spelling mistake, in a document that had none.
 */
function buildNonLatin() {
  const cmap = toUnicodeCMap({ chars: NON_LATIN_MAP });
  const content = textContent([{ bytes: NON_LATIN_CODES, x: MARGIN, y: 700 }]);
  const { doc, root } = simpleDocument(content, {
    font: (builder) => {
      const cmapNum = builder.add(`<< /Length ${cmap.length} >>`, cmap);
      return '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica'
        + ` /Encoding /WinAnsiEncoding /ToUnicode ${cmapNum} 0 R >>`;
    },
  });
  return serialise(doc, { root, id: ID });
}

/**
 * Page 1 is perfectly readable and page 2 carries a font with no recoverable
 * encoding. The whole document must be refused: returning page 1 would report
 * findings at positions that silently omit half the file.
 */
function buildSecondPageUndecodable() {
  const doc = new Doc();
  const good = doc.add(SIMPLE_FONT());
  const descriptor = fontDescriptor(doc, 'QQQQQQ+SecretSubset');
  const bad = doc.add(NO_ENCODING_FONT(descriptor));
  const first = textContent(SIMPLE_LINES([PROSE.clean]));
  const second = textContent([{ bytes: Buffer.from([1, 2, 3, 4, 5]), x: MARGIN, y: 700 }]);
  const firstNum = doc.add(`<< /Length ${first.length} >>`, first);
  const secondNum = doc.add(`<< /Length ${second.length} >>`, second);
  const pagesNum = doc.alloc();
  const firstPage = doc.alloc();
  const secondPage = doc.alloc();
  doc.set(firstPage, `<< /Type /Page /Parent ${pagesNum} 0 R`
    + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
    + ` /Resources << /ProcSet [/PDF /Text] /Font << /F1 ${good} 0 R >> >>`
    + ` /Contents ${firstNum} 0 R >>`);
  doc.set(secondPage, `<< /Type /Page /Parent ${pagesNum} 0 R`
    + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
    + ` /Resources << /ProcSet [/PDF /Text] /Font << /F1 ${bad} 0 R >> >>`
    + ` /Contents ${secondNum} 0 R >>`);
  doc.set(pagesNum, `<< /Type /Pages /Kids [${firstPage} 0 R ${secondPage} 0 R] /Count 2 >>`);
  const root = doc.add(`<< /Type /Catalog /Pages ${pagesNum} 0 R >>`); // ue:ignore UE-SP001  (a PDF object name, not prose)
  return serialise(doc, { root, id: ID });
}

// --- the refusal cases --------------------------------------------------------

/** One page carrying an image and no text operator of any kind. */
function buildScanned() {
  const doc = new Doc();
  const image = imageObject(doc);
  const content = imageContent();
  const contentNum = doc.add(`<< /Length ${content.length} >>`, content);
  const pagesNum = doc.alloc();
  const pageNum = doc.alloc();
  doc.set(pageNum, `<< /Type /Page /Parent ${pagesNum} 0 R`
    + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
    + ' /Resources << /ProcSet [/PDF /Image] /XObject << /Im1 ' + image + ' 0 R >> >>'
    + ` /Contents ${contentNum} 0 R >>`);
  doc.set(pagesNum, `<< /Type /Pages /Kids [${pageNum} 0 R] /Count 1 >>`);
  const root = doc.add(`<< /Type /Catalog /Pages ${pagesNum} 0 R >>`); // ue:ignore UE-SP001  (a PDF object name, not prose)
  return serialise(doc, { root, id: ID });
}

/**
 * A genuinely encrypted document: RC4 under the V1/R2 standard security
 * handler, with the content stream really encrypted. A reader that ignored the
 * /Encrypt dictionary would read ciphertext.
 */
export const ENCRYPTED_PASSWORD = 'secret';

function buildEncrypted() {
  const doc = new Doc();
  const font = doc.add(SIMPLE_FONT());
  const content = textContent(SIMPLE_LINES([PROSE.clean]));
  const contentNum = doc.alloc();
  const { key, O, U, perms } = standardSecurity({
    user: ENCRYPTED_PASSWORD,
    owner: ENCRYPTED_PASSWORD,
    permissions: -3904,
    idFirst: ID,
  });
  const encrypted = rc4(objectKey(key, contentNum), content);
  doc.set(contentNum, `<< /Length ${encrypted.length} >>`, encrypted);
  const pagesNum = doc.alloc();
  const pageNum = doc.alloc();
  doc.set(pageNum, `<< /Type /Page /Parent ${pagesNum} 0 R`
    + ` /MediaBox [0 0 ${PAGE_W} ${PAGE_H}]`
    + ` /Resources << /ProcSet [/PDF /Text] /Font << /F1 ${font} 0 R >> >>`
    + ` /Contents ${contentNum} 0 R >>`);
  doc.set(pagesNum, `<< /Type /Pages /Kids [${pageNum} 0 R] /Count 1 >>`);
  const root = doc.add(`<< /Type /Catalog /Pages ${pagesNum} 0 R >>`); // ue:ignore UE-SP001  (a PDF object name, not prose)
  const encryptNum = doc.add('<< /Filter /Standard /V 1 /R 2 /O '
    + `<${O.toString('hex').toUpperCase()}> /U <${U.toString('hex').toUpperCase()}>`
    + ` /P ${perms.readInt32LE(0)} >>`);
  return serialise(doc, { root, encrypt: encryptNum, id: ID });
}

/**
 * The same document with its last content stream cut in half, so the file ends
 * inside an object: no endstream, no xref table, no trailer, no %%EOF.
 */
function buildTruncated() {
  const full = buildPlain();
  const text = full.toString('latin1');
  // The last stream keyword that is not the tail of an `endstream`.
  const opens = [...text.matchAll(/(?:^|\n)stream\n/g)];
  const cut = opens[opens.length - 1].index + '\nstream\n'.length + 12;
  assertCutLandsInside(text, cut);
  return full.subarray(0, cut);
}

function assertCutLandsInside(text, cut) {
  const head = text.slice(0, cut);
  if (head.includes('%%EOF')) throw new Error('make-pdf: the truncated case still has its end marker');
  if (head.includes('startxref')) throw new Error('make-pdf: the truncated case still has its xref pointer');
  const opens = (head.match(/stream\n/g) || []).length;
  const closes = (head.match(/\nendstream/g) || []).length;
  if (opens !== closes + 1) {
    throw new Error(`make-pdf: the cut does not leave a stream open (${opens} open, ${closes} closed)`);
  }
  const lastObject = head.lastIndexOf('\n', lastObjectStart(head, cut));
  const lastEnd = head.lastIndexOf('endobj\n');
  if (lastObject <= lastEnd) {
    throw new Error('make-pdf: the cut does not land inside an object');
  }
  if (!/^\d+ 0 obj\n/.test(head.slice(lastObject + 1))) {
    throw new Error(`make-pdf: the cut does not land inside an object: ${JSON.stringify(head.slice(lastObject + 1, lastObject + 20))}`);
  }
}

/** The offset of the `N 0 obj` that the head of the file ends inside. */
function lastObjectStart(head) {
  const matches = [...head.matchAll(/(?:^|\n)(\d+) 0 obj\n/g)];
  return matches[matches.length - 1].index;
}

/** A complete document whose header is not `%PDF-`. */
function buildNotAPdf() {
  const full = buildPlain();
  return Buffer.concat([Buffer.from('%PDX-1.7\n', 'latin1'), full.subarray(9)]);
}

// --- writing the corpus -------------------------------------------------------

/**
 * Every case, with what the contract requires of it. The suite reads this table
 * so a case cannot be added to the generator and quietly left untested: the
 * matrix is derived, not written out twice.
 */
export const CASES = [
  { name: 'plain-untagged', must: 'accept', note: 'WinAnsi text, no compression' },
  { name: 'flate', must: 'accept', note: 'FlateDecode content stream' },
  { name: 'lzw', must: 'accept', note: 'LZWDecode content stream' },
  { name: 'ascii85', must: 'accept', note: 'ASCII85Decode content stream' },
  { name: 'asciihex', must: 'accept', note: 'ASCIIHexDecode content stream' },
  { name: 'runlength', must: 'accept', note: 'RunLengthDecode content stream' },
  { name: 'differences', must: 'accept', note: '/Differences overrides the base encoding' },
  { name: 'to-unicode', must: 'accept', note: 'ToUnicode CMap with bfchar and bfrange' },
  { name: 'identity-h', must: 'accept', note: 'CID font, Identity-H, two-byte codes' },
  { name: 'object-streams', must: 'accept', note: 'cross-reference stream and /ObjStm' },
  { name: 'multi-page', must: 'accept', note: 'three pages, distinguishable text' },
  { name: 'two-column', must: 'accept', note: 'two text columns per page' },
  { name: 'two-column-narrow', must: 'accept', note: 'a 12pt gutter, below the old threshold' },
  { name: 'hanging-indent', must: 'accept', note: 'a numbered list with a 7.76pt indent gap' },
  { name: 'rotated-page', must: 'accept', note: '/Rotate 90 with the copy drawn turned' },
  { name: 'non-latin', must: 'accept', note: 'Cyrillic, Greek and accented Latin from ToUnicode' },
  { name: 'vertical-gap', must: 'accept', note: 'two lines 96pt apart that must not merge' },
  { name: 'positions', must: 'accept', note: 'varied x and y on every line' },
  { name: 'quoted-paragraph', must: 'accept', note: 'a visually indented quotation' },
  { name: 'rules-invisibility', must: 'accept', note: 'four rule defects on one line' },
  { name: 'split-word', must: 'accept', note: 'a doubled word across a line break' },
  { name: 'no-to-unicode', must: 'refuse', code: 'UNDECODABLE_FONT', note: 'no recoverable encoding' },
  { name: 'second-page-undecodable', must: 'refuse', code: 'UNDECODABLE_FONT', note: 'page 2 unreadable, no partial extraction' },
  { name: 'scanned', must: 'refuse', code: 'SCANNED', note: 'image only, no text operators' },
  { name: 'encrypted', must: 'refuse', code: 'ENCRYPTED', note: 'RC4 under the standard handler' },
  { name: 'truncated', must: 'refuse', code: 'MALFORMED', note: 'file cut inside an object' },
  { name: 'not-a-pdf', must: 'refuse', code: 'NOT_A_PDF', note: 'wrong magic bytes' },
];

export const CASE_NAMES = CASES.map((entry) => entry.name);

/**
 * Write every case into `dir` and return `{ name: filePath }`. Nothing is
 * written anywhere else, and a destination inside the package root is refused:
 * a committed PDF is unreviewable, and this rule is mechanical rather than a
 * note in a contributing guide.
 */
export function writeCorpus(dir) {
  const resolved = path.resolve(dir);
  if (resolved === ROOT || resolved.startsWith(ROOT + path.sep)) {
    throw new Error(`make-pdf: refusing to write PDF fixtures into the repository (${resolved})`);
  }
  fs.mkdirSync(resolved, { recursive: true });
  const written = {};
  for (const entry of CASES) {
    const file = path.join(resolved, `${entry.name}.pdf`);
    fs.writeFileSync(file, build(entry.name));
    written[entry.name] = file;
  }
  return written;
}

export { PROSE as FIXTURE_PROSE };
