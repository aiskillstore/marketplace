// un-editorial-check — PDF extraction: fixtures proven, contract held.
//
// This suite is the reason the PDF feature can be trusted, and its job is
// inverted on purpose. It does not show that extraction works; it tries to
// catch the engine being wrong and to prove that every refusal happens. A
// confidently wrong line number is worse than a refusal, so a test that only
// checked "some text came out" would be worse than no test at all.
//
// The order of the two halves is the whole argument:
//
//   Part A  the generator's own tests. Every fixture is read back and shown to
//           really exhibit the property its name claims — /ToUnicode really
//           absent in the case that must refuse for want of it, the scanned
//           page really carrying no text operator, the LZW stream really
//           being 9-bit codes that decode to the exact content stream. This
//           half has no dependency on the engine and runs today.
//   Part B  the engine contract. Every refusal code, the exact reconstructed
//           line text, the page attribution, the context, the unit map, the
//           rule layer seeing a PDF unit as ordinary copy, determinism, and
//           the absence of a crash or a hang on every refusal path.
//
// The lesson this suite encodes is from the last phase, where a fixture that
// wrapped a whole word instead of splitting one let a real bug ship and the
// suite still passed: for every case, the precondition is asserted BEFORE the
// behaviour. A fixture that does not exercise what it claims is a green lie.
//
// Standalone: node tests/audit-pdf-extraction.mjs
//
// Part B needs lib/pdf-extract.mjs, and an absent engine fails this suite
// outright. Part A alone proves the fixtures and not the engine, and a run
// that prints half the suite as skipped reads like a pass on the way past.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

import { makeContext, loadBaselineProfile, loadCatalogue, validateConfig } from '../lib/config.mjs';
import { extractText } from '../lib/extract-text.mjs';
import { runEditorialRules } from '../lib/rules.mjs';
import { lineStarts, locate } from '../lib/position.mjs';
import {
  CASES, CASE_NAMES, COLUMN_LEFT, COLUMN_RIGHT, ENCRYPTED_PASSWORD, FILTER_COPY, MARGIN,
  PAGE_LINES, POSITION_LINES, PROSE, RIGHT_COLUMN_X, ascii85, asciiHex, build, lzw, md5,
  objectKey, rc4, runLength, standardSecurity, winAnsi, writeCorpus,
  HANGING_ENTRIES, HANGING_GAP_PT, HANGING_NUM_END_X, HANGING_ROWS, HANGING_SIZE,
  HANGING_TEXT_X, NON_LATIN_CODES, NON_LATIN_TEXT, NARROW_GLYPH_PT, NARROW_GUTTER_PT,
  NARROW_LEFT, NARROW_LEFT_CHARS, NARROW_LEFT_END_X, NARROW_RIGHT, NARROW_RIGHT_X,
  NARROW_SIZE, ROTATE_DEGREES, ROTATED_LINES, LEADING, VERTICAL_GAP_LINES, VERTICAL_GAP_PT,
} from './lib/make-pdf.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-pdf-'));
// The corpus is deterministic and rebuildable, so it is removed on every exit
// including a crash: a suite that leaves a directory behind on each red run
// fills the temporary directory with hundreds of orphaned fixtures, and the
// one run whose fixtures you want to look at is then the hardest to find.
process.on('exit', () => fs.rmSync(tmp, { recursive: true, force: true }));
const corpus = writeCorpus(path.join(tmp, 'corpus'));
const read = (name) => fs.readFileSync(corpus[name]);
const asText = (bytes) => bytes.toString('latin1');

const accepted = CASES.filter((entry) => entry.must === 'accept');
const refused = CASES.filter((entry) => entry.must === 'refuse');

// ===========================================================================
// Part 0 — a fixture reader, written independently of the engine.
//
// Everything in Part A is checked with this. It is a deliberately naive
// scanner: it finds objects by walking the bytes, not by consulting any
// cross-reference structure the engine would also consult. If it shared code
// with lib/pdf-parse.mjs, a bug in that code would make the fixture look
// correct while being wrong.
// ===========================================================================

/** Every `N 0 obj` in the file, in file order, with its dictionary and stream. */
function readObjects(bytes) {
  const text = asText(bytes);
  const objects = [];
  for (const match of text.matchAll(/(?:^|[\r\n])(\d+) 0 obj\n/g)) {
    const num = Number(match[1]);
    const start = match.index + match[0].length;
    const end = text.indexOf('\nendobj\n', start);
    const bodyEnd = end < 0 ? text.length : end;
    const raw = text.slice(start, bodyEnd);
    const streamAt = raw.indexOf('\nstream\n');
    if (streamAt >= 0) {
      const dict = raw.slice(0, streamAt);
      const dataStart = start + streamAt + '\nstream\n'.length;
      const length = Number(/\/Length (\d+)/.exec(dict)?.[1]);
      objects.push({
        num,
        dict,
        data: bytes.subarray(dataStart, dataStart + (Number.isFinite(length) ? length : 0)),
        at: match.index + (match[0].startsWith('\n') ? 1 : 0),
      });
    } else {
      objects.push({ num, dict: raw, data: null, at: match.index });
    }
  }
  return objects;
}

function ascii85Decode(data) {
  const text = asText(data).replace(/\s/g, '');
  assert.ok(text.endsWith('~>'), 'an ASCII85 stream must end with its terminator');
  const body = text.slice(0, -2);
  const out = [];
  let group = [];
  for (const ch of body) {
    if (ch === 'z') {
      assert.equal(group.length, 0, 'z may only appear at a group boundary');
      out.push(0, 0, 0, 0);
      continue;
    }
    group.push(ch.charCodeAt(0) - 33);
    if (group.length === 5) {
      let v = 0;
      for (const digit of group) v = v * 85 + digit;
      out.push((v >>> 24) & 0xff, (v >>> 16) & 0xff, (v >>> 8) & 0xff, v & 0xff);
      group = [];
    }
  }
  if (group.length) {
    const count = group.length - 1;
    while (group.length < 5) group.push(84);
    let v = 0;
    for (const digit of group) v = v * 85 + digit;
    const full = [(v >>> 24) & 0xff, (v >>> 16) & 0xff, (v >>> 8) & 0xff, v & 0xff];
    out.push(...full.slice(0, count));
  }
  return Buffer.from(out);
}

function asciiHexDecode(data) {
  const text = asText(data).replace(/\s/g, '');
  assert.ok(text.endsWith('>'), 'an ASCIIHex stream must end with its terminator');
  const body = text.slice(0, -1);
  const padded = body.length % 2 ? body + '0' : body;
  return Buffer.from(padded, 'hex');
}

function runLengthDecode(data) {
  const out = [];
  let i = 0;
  while (i < data.length) {
    const control = data[i++];
    if (control === 128) break;
    if (control < 128) {
      for (let k = 0; k <= control; k++) out.push(data[i++]);
    } else {
      // The specification: a control byte of 129 to 255 repeats the next byte
      // 257 - n times.
      const byte = data[i++];
      for (let k = 0; k < 257 - control; k++) out.push(byte);
    }
  }
  return Buffer.from(out);
}

/**
 * LZW as a flat sequence of 9-bit codes. Only valid when no code crossed 511,
 * which the caller asserts — the alternative would be to trust an encoder
 * against a decoder that shares its assumptions.
 */
function lzwDecode9(data) {
  const codes = [];
  for (let i = 0; i + 9 <= data.length * 8; i += 9) {
    let code = 0;
    for (let k = 0; k < 9; k++) {
      const bit = i + k;
      code = (code << 1) | ((data[bit >> 3] >> (7 - (bit & 7))) & 1);
    }
    codes.push(code);
  }
  // The dictionary holds byte strings indexed by code. The entry added after
  // reading a code is the *string* the previous code stands for plus the first
  // byte of the code just read, which is the only formulation that stays in
  // step with the encoder across a repeated run.
  let table = new Array(4096);
  const stands = (code) => (code < 256 ? [code] : table[code]);
  const out = [];
  let next = 258;
  let previous = null;
  let highest = 0;
  for (const code of codes) {
    if (code === 256) { table = new Array(4096); next = 258; previous = null; continue; }
    if (code === 257) break;
    highest = Math.max(highest, code);
    let entry;
    if (code < 256) entry = [code];
    else if (table[code]) entry = table[code];
    else {
      assert.equal(code, next,
        `LZW code ${code} is neither a dictionary entry nor the next code to be assigned`);
      entry = stands(previous).concat([stands(previous)[0]]);
    }
    for (const byte of entry) out.push(byte);
    if (previous !== null) table[next++] = stands(previous).concat([entry[0]]);
    previous = code;
  }
  return { bytes: Buffer.from(out), codes, highest };
}

const FILTERS = {
  FlateDecode: (data) => zlib.inflateSync(data),
  LZWDecode: (data) => lzwDecode9(data).bytes,
  ASCII85Decode: ascii85Decode,
  ASCIIHexDecode: asciiHexDecode,
  RunLengthDecode: runLengthDecode,
};

/** The decoded bytes of one stream object, with the filter actually applied. */
function decodedStream(object) {
  assert(object.data, `object ${object.num} is not a stream`);
  const name = /\/Filter\s*\/(\w+)/.exec(object.dict)?.[1];
  if (!name) return object.data;
  const decode = FILTERS[name];
  assert(decode, `this suite has no decoder for /${name}`);
  return decode(object.data);
}

/** The text runs a content stream draws, in stream order, with their positions. */
function contentRuns(stream) {
  const text = asText(stream);
  const runs = [];
  const pattern = /\/(\w+) ([\d.]+) Tf\n1 0 0 1 (-?[\d.]+) (-?[\d.]+) Tm\n\(([\s\S]*?)\) Tj\nET/g;
  for (const match of text.matchAll(pattern)) {
    const bytes = Buffer.from(match[5].replace(/\\(\d{3})/g, (_, oct) =>
      String.fromCharCode(parseInt(oct, 8))).replace(/\\([()\\])/g, '$1'), 'latin1');
    runs.push({ font: match[1], size: Number(match[2]), x: Number(match[3]), y: Number(match[4]), bytes });
  }
  return runs;
}

const winAnsiRead = (bytes) => bytes.toString('latin1');

/** The single content stream a one-stream fixture carries. */
function contentStream(name, filter = null) {
  const found = readObjects(read(name))
    .find((object) => object.data && (!filter || object.dict.includes(`/Filter /${filter}`)));
  assert(found, `the ${name} case must carry a content stream`);
  return found;
}

/** The stream that actually draws text, where a fixture carries a CMap too. */
function textStream(name) {
  const found = readObjects(read(name)).find((object) => {
    if (!object.data) return false;
    try { return contentRuns(decodedStream(object)).length > 0; }
    catch { return false; }
  });
  assert(found, `the ${name} case must carry a content stream that draws text`);
  return found;
}

/** The xref table's entries, checked against the bytes they point at. */
function readXrefTable(bytes) {
  const text = asText(bytes);
  const start = Number(/startxref\n(\d+)\n%%EOF\n$/.exec(text)?.[1]);
  assert(Number.isFinite(start), 'the document must end with a startxref pointer');
  const head = text.slice(start);
  assert(head.startsWith('xref\n'), `startxref must point at the xref table: ${JSON.stringify(head.slice(0, 8))}`);
  const size = Number(/^xref\n0 (\d+)\n/.exec(head)[1]);
  const entries = new Map();
  const base = start + /^xref\n0 \d+\n/.exec(head)[0].length;
  for (let i = 1; i < size; i++) {
    const record = text.slice(base + i * 20, base + (i + 1) * 20);
    const match = /^(\d{10}) (\d{5}) ([nf]) \n$/.exec(record);
    assert(match, `xref entry ${i} must be a 20-byte record: ${JSON.stringify(record)}`);
    if (match[3] === 'n') {
      const offset = Number(match[1]);
      assert(text.startsWith(`${i} 0 obj\n`, offset),
        `xref entry ${i} must point at "${i} 0 obj"`);
      entries.set(i, offset);
    }
  }
  return { start, size, entries };
}

/** The xref stream's rows, decoded from its own W and Index-free layout. */
function readXrefStream(bytes) {
  const objects = readObjects(bytes);
  const xref = objects.find((object) => object.dict.includes('/Type /XRef'));
  assert(xref, 'the document must carry a cross-reference stream');
  const table = xref.data;
  const widths = [/\/W \[(\d+ \d+ \d+)\]/.exec(xref.dict)[1]]
    .flatMap((line) => [...line.matchAll(/\d+/g)].map((m) => Number(m[0])));
  const width = widths.reduce((a, b) => a + b, 0);
  assert.equal(table.length % width, 0, 'the xref stream must be a whole number of rows');
  const rows = [];
  for (let i = 0; i + width <= table.length; i += width) {
    let value = 0;
    for (let k = 0; k < width; k++) value = value * 256 + (widths[k] ? table[i + k] : 0);
    rows.push(value);
  }
  return { object: xref, rows, widths, at: xref.at };
}

// ===========================================================================
// Part A — the generator's own tests.
//
// For every case, the precondition first. Nothing in this half depends on
// lib/pdf-extract.mjs, so it runs on its own.
// ===========================================================================

// --- A1. the encoders themselves, against the specification -----------------

// MD5 and RC4 are hand-written so the import list stays at zero, and the
// encrypted fixture is only honest if they are the real algorithms. RFC 1321
// test vectors first, then the classic RC4 vector.
{
  const vectors = [
    ['', 'd41d8cd98f00b204e9800998ecf8427e'],
    ['a', '0cc175b9c0f1b6a831c399e269772661'],
    ['abc', '900150983cd24fb0d6963f7d28e17f72'],
    ['message digest', 'f96b697d7cb7938d525a2f31aaf161d0'],
    ['abcdefghijklmnopqrstuvwxyz', 'c3fcd3d76192e4007dfb496cca67e13b'],
    ['ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
      'd174ab98d277d9f5a5611c2c9f419d9f'],
    ['12345678901234567890123456789012345678901234567890'
      + '123456789012345678901234567890', '57edf4a22be3c955ac49da2e2107b67a'],
  ];
  for (const [input, expected] of vectors) {
    assert.equal(md5(input).toString('hex'), expected, `MD5(${JSON.stringify(input)})`);
  }
  // Multi-block input, so the padding and length encoding are exercised.
  assert.equal(md5('x'.repeat(1000)).toString('hex'),
    md5(Buffer.from('x'.repeat(1000), 'latin1')).toString('hex'),
    'MD5 must take a string and a buffer alike');

  assert.equal(rc4(Buffer.from('Key'), Buffer.from('Plaintext')).toString('hex'),
    'bbf316e8d940af0ad3', 'the RC4 test vector from its specification');
  const once = rc4(Buffer.from('k'), Buffer.from('round trip me'));
  assert.equal(rc4(Buffer.from('k'), once).toString('latin1'), 'round trip me',
    'RC4 must be its own inverse');
}

// The filters are locked two ways: a round trip, and a check against the
// specification's own definition of the encoding — not against another
// function of mine that could be wrong in the same way.
{
  for (let length = 1; length <= 40; length++) {
    const data = Buffer.from(Array.from({ length }, (_, i) => (i * 37 + 11) & 0xff));
    assert.deepEqual(ascii85Decode(ascii85(data)), data, `ASCII85 round trip, ${length} bytes`);
    assert.deepEqual(asciiHexDecode(asciiHex(data)), data, `ASCIIHex round trip, ${length} bytes`);
    assert.deepEqual(runLengthDecode(runLength(data)), data, `RunLength round trip, ${length} bytes`);
  }
  // A round trip over bytes with no two alike never reaches the repeat branch,
  // so the control bytes above are only proven against literal runs. These
  // inputs have runs of two, of three and of a hundred.
  for (const [label, data] of [
    ['a pair', Buffer.from('aabb', 'latin1')],
    ['a triple', Buffer.from('xxxy', 'latin1')],
    ['a long run', Buffer.alloc(100, 0x5a)],
    ['runs and literals', Buffer.from('aa bbbb  ccccccc d', 'latin1')],
  ]) {
    assert.deepEqual(runLengthDecode(runLength(data)), data, `RunLength round trip, ${label}`);
  }
  assert.deepEqual([...runLength(Buffer.from('aabb', 'latin1'))], [255, 0x61, 255, 0x62, 128],
    'a pair must become one repeat code of 257 - 2');
  assert.deepEqual([...runLength(Buffer.alloc(100, 0x5a))], [157, 0x5a, 128],
    'a run of 100 must become one repeat code, split at the 128-byte limit');
  assert.deepEqual([...runLength(Buffer.alloc(200, 0x5a))], [129, 0x5a, 185, 0x5a, 128],
    'a run longer than 128 must be split into one repeat code of 128 and one of 72');

  // The spec's z shortcut, and the grouping rule: a full four-byte group is
  // five characters, a final partial group of n bytes is n + 1.
  assert.equal(ascii85(Buffer.from([0, 0, 0, 0])).toString('latin1'), 'z~>',
    'four zero bytes must use the z shortcut');
  // The worked example from Adobe's own documentation of the encoding.
  assert.equal(ascii85(Buffer.from('Man ', 'latin1')).toString('latin1'), '9jqo^~>',
    'the documented ASCII85 example must encode exactly as published');
  const sample = Buffer.from('un-editorial-check 1.2.1', 'latin1');
  const encoded = ascii85(sample).toString('latin1');
  const tail = sample.length % 4 === 0 ? 0 : (sample.length % 4) + 1;
  const expectedLength = Math.floor(sample.length / 4) * 5 + tail + 2;
  assert.equal(encoded.length, expectedLength,
    'each four-byte group must be five characters and the final group n + 1');
  assert.ok(/^[\x21-\x7e]+~>$/.test(encoded), 'ASCII85 output must be printable and terminated');
  assert.equal(encoded.indexOf('z'), -1,
    'this sample has no zero group, so no z may appear');

  // The spec's repeat code: 257 - n, followed by the byte, for a run of n.
  assert.deepEqual([...runLength(Buffer.alloc(5, 0x41))], [252, 0x41, 128],
    'a run of five must be one repeat code, not five literal bytes');
  assert.deepEqual([...runLength(Buffer.from('abcde'))], [4, 0x61, 0x62, 0x63, 0x64, 0x65, 128],
    'five distinct bytes must be a literal run');
  const rl = asciiHex(Buffer.from([0x00, 0xff, 0x10]));
  assert.equal(rl.toString('latin1'), '00FF10>', 'ASCIIHex must emit uppercase hex and its terminator');
  assert.equal(asciiHex(Buffer.from([0xab])).toString('latin1'), 'AB>',
    'an odd final digit is left unpaired: the specification says to assume a trailing zero');
  assert.deepEqual(asciiHexDecode(Buffer.from('AB>', 'latin1')), Buffer.from([0xab]),
    'a reader must complete an odd final digit with zero');
}

// LZW is locked by decoding the generated stream as flat 9-bit codes, which
// only works if the encoder really emitted 9-bit codes with the Clear and EOD
// markers where the specification puts them.
{
  const stream = contentStream('lzw', 'LZW');
  const runs = contentRuns(decodedStream(stream));
  assert.ok(runs.length > 0, 'the lzw fixture must draw text');

  const { codes, highest, bytes } = lzwDecode9(stream.data);
  assert.equal(codes[0], 256, 'an LZW stream must open with the Clear code');
  assert.equal(codes[codes.length - 1], 257, 'an LZW stream must close with the EOD code');
  assert.ok(highest < 511,
    `the fixture must stay inside 9-bit codes so the decode above is valid (highest ${highest})`);
  const expected = decodedStream(contentStream('flate'));
  assert.equal(asText(bytes), asText(expected),
    'the LZW stream must decode to the same bytes as the Flate case carries');
}

// --- A2. the corpus, case by case -------------------------------------------

// Every case builds, and builds the same way twice. A generator that drifted
// between runs would make a byte-level precondition meaningless.
{
  for (const entry of CASES) {
    const first = build(entry.name);
    const second = build(entry.name);
    assert(Buffer.isBuffer(first) && first.length > 0, `${entry.name} must produce bytes`);
    assert.equal(Buffer.compare(first, second), 0, `${entry.name} must be deterministic`);
  }
  const names = CASE_NAMES;
  assert.equal(new Set(names).size, names.length, 'case names must be unique');
  assert.deepEqual(Object.keys(corpus).sort(), [...names].sort(),
    'writeCorpus must write exactly the cases it declares');
  for (const name of names) {
    assert.equal(Buffer.compare(fs.readFileSync(corpus[name]), build(name)), 0,
      `${name} on disk must be exactly the case the generator builds`);
  }
  // Binaries never enter the repository: the destination is refused outright.
  assert.throws(() => writeCorpus(path.join(ROOT, 'tests', 'pdf-fixtures')),
    /refusing to write PDF fixtures into the repository/,
    'writing a PDF into the package must be impossible');
  assert.throws(() => writeCorpus(ROOT), /refusing to write PDF fixtures into the repository/);
}

// plain-untagged: the control. A classic xref table, uncompressed content, a
// WinAnsi font, and the copy visible in the bytes as plain text.
{
  const bytes = read('plain-untagged');
  const text = asText(bytes);
  assert.ok(text.startsWith('%PDF-'), 'the control case must carry the PDF magic');
  assert.ok(text.trimEnd().endsWith('%%EOF'), 'the control case must carry the end marker');
  const xref = readXrefTable(bytes);
  assert.equal(xref.entries.size, 5, 'every object must have an xref entry');
  assert.match(text, /\/Encoding \/WinAnsiEncoding/,
    'the control case must declare a font whose encoding can be resolved');
  const content = contentStream('plain-untagged');
  assert.ok(!/\/Filter/.test(content.dict), 'the control case must not be compressed');
  const runs = contentRuns(decodedStream(content));
  assert.deepEqual(runs.map((run) => winAnsiRead(run.bytes)), FILTER_COPY,
    'the control case must draw the two authored lines as literal text');
  assert.deepEqual(runs.map((run) => [run.x, run.y]), [[MARGIN, 700], [MARGIN, 684]],
    'the control case must place its lines at known coordinates');
}

// flate, lzw, ascii85, asciihex, runlength: the same document through five
// filters. Each must be really encoded — the copy must not be readable in the
// bytes — and each must decode to the exact same content stream.
{
  // The five filters are one document, so the Flate decode is the reference
  // the other four have to reproduce byte for byte.
  const expected = asText(decodedStream(contentStream('flate', 'FlateDecode')));
  assert.deepEqual(
    contentRuns(Buffer.from(expected, 'latin1')).map((run) => winAnsiRead(run.bytes)),
    FILTER_COPY,
    'the filter family must carry the two authored lines');
  for (const [name, filter] of [
    ['flate', 'FlateDecode'], ['lzw', 'LZWDecode'], ['ascii85', 'ASCII85Decode'],
    ['asciihex', 'ASCIIHexDecode'], ['runlength', 'RunLengthDecode'],
  ]) {
    const bytes = read(name);
    const text = asText(bytes);
    assert.ok(text.includes(`/Filter /${filter}`), `${name} must declare /${filter}`);
    const stream = contentStream(name, filter);
    assert.ok(stream, `${name} must carry one filtered stream`);
    const raw = stream.data;
    assert.notEqual(Buffer.compare(Buffer.from(expected, 'latin1'), raw), 0,
      `${name}: the stored bytes must not be the content stream itself — the filter must really run`);
    assert.equal(asText(decodedStream(stream)), expected,
      `${name} must decode to the same copy as the uncompressed case`);
    if (filter !== 'RunLengthDecode') {
      assert.ok(!text.includes('The delegation reviewed'),
        `${name} must really be encoded: the copy is readable in the bytes`);
    }
  }

  // RunLength is the honest exception: it only collapses runs of two or more
  // identical bytes, so prose survives almost intact. What makes the case real
  // is that both of its control codes are exercised — a literal run and a
  // repeat — and that the decode still reproduces the content exactly.
  {
    const stream = contentStream('runlength', 'RunLengthDecode');
    const controls = [...stream.data];
    assert.ok(controls.some((byte) => byte >= 129 && byte <= 255),
      'the RunLength stream must contain a repeat code');
    assert.ok(controls.some((byte) => byte >= 1 && byte <= 127),
      'the RunLength stream must contain a literal-run code');
    assert.equal(controls[controls.length - 1], 128,
      'the RunLength stream must end with the end-of-data code');
  }
}

// differences: a font whose /Differences overrides the base encoding. Codes 65
// and 66 are "A" and "B" in WinAnsi; the override makes them two accented
// letters, so a reader that ignores the array produces different copy from a
// reader that honours it. The fixture is only a real test if the two differ.
{
  const text = asText(read('differences'));
  assert.match(text, /\/Differences \[65 \/Aacute 66 \/Ccedilla\]/,
    'the differences case must carry the override it claims');
  assert.ok(!text.includes('/ToUnicode'),
    'the differences case must resolve its encoding without a CMap');
  const runs = contentRuns(decodedStream(contentStream('differences')));
  assert.deepEqual([...runs[0].bytes], [65, 66], 'the content must use the overridden codes');
  assert.equal(winAnsiRead(runs[0].bytes), 'AB',
    'a reader that ignored /Differences would produce this, not the intended text');
  assert.notEqual(winAnsiRead(runs[0].bytes), 'ÁÇ',
    'the intended text must differ from the base-encoding reading, or the case proves nothing');
}

// to-unicode: a CMap with both bfchar and bfrange, whose mappings all disagree
// with WinAnsi, so an extractor that falls back to the base encoding returns
// "ABPQR" where the document says "XYabc".
{
  const text = asText(read('to-unicode'));
  assert.match(text, /\/ToUnicode \d+ 0 R/, 'the to-unicode case must point a font at its CMap');
  const cmapObject = readObjects(read('to-unicode')).find((object) => object.dict.includes('/Length')
    && asText(object.data).includes('begincmap'));
  assert(cmapObject, 'the CMap must be a stream object in the file');
  const cmap = asText(decodedStream(cmapObject));
  assert.match(cmap, /begincodespacerange\n<0000> <FFFF>\nendcodespacerange/,
    'the CMap must declare a codespace range');
  assert.match(cmap, /beginbfchar/, 'the CMap must use bfchar');
  assert.match(cmap, /beginbfrange/, 'the CMap must use bfrange');
  assert.match(cmap, /<0041> <0058>/, 'bfchar must map 0x41 to X');
  assert.match(cmap, /<0042> <0059>/, 'bfchar must map 0x42 to Y');
  assert.match(cmap, /<0050> <0052> <0061>/, 'bfrange must map 0x50..0x52 to a, b, c');
  const runs = contentRuns(decodedStream(textStream('to-unicode')));
  assert.deepEqual([...runs[0].bytes], [0x41, 0x42, 0x50, 0x51, 0x52],
    'the content must use exactly the codes the CMap remaps');
  assert.equal(winAnsiRead(runs[0].bytes), 'ABPQR',
    'the base-encoding reading must differ from the CMap reading, or the case proves nothing');
}

// no-to-unicode: the font must have nothing at all to resolve its codes with.
// This is the assertion that makes the refusal provable rather than a guess.
{
  const bytes = read('no-to-unicode');
  const text = asText(bytes);
  assert.ok(!text.includes('/ToUnicode'),
    'the no-to-unicode case must contain no ToUnicode CMap anywhere in the file');
  const font = readObjects(bytes).find((object) => /\/Type \/Font \/Subtype/.test(object.dict));
  assert.ok(font, 'the case must declare a font');
  assert.ok(!/\/Encoding/.test(font.dict),
    'the font must declare no encoding, or the codes would be resolvable');
  assert.match(font.dict, /\/BaseFont \/\w{6}\+/,
    'the font must be a subset name, not one of the standard fourteen');
  for (const standard of ['/Helvetica', '/Times-Roman', '/Courier']) {
    assert.ok(!font.dict.includes(standard), `the font must not be ${standard}`);
  }
  const descriptor = readObjects(bytes).find((object) => /\/Type \/FontDescriptor/.test(object.dict));
  assert.ok(descriptor && descriptor.dict.includes('/QQQQQQ+SecretSubset'),
    'the font descriptor must name the same subset as the font');
  const runs = contentRuns(decodedStream(textStream('no-to-unicode')));
  assert.deepEqual([...runs[0].bytes], [1, 2, 3, 4, 5],
    'the content must use codes that no standard encoding defines');
}

// identity-h: every code is two bytes, and the CMap maps each CID to a
// character that is not its own value.
{
  const text = asText(read('identity-h'));
  assert.match(text, /\/Subtype \/Type0/, 'the font must be a composite Type0 font');
  assert.match(text, /\/Encoding \/Identity-H/, 'the composite font must be Identity-H');
  assert.match(text, /\/Subtype \/CIDFontType2/, 'the descendant must be a CID font');
  const cmapObject = readObjects(read('identity-h')).find((object) => object.data
    && asText(object.data).includes('begincmap'));
  const cmap = asText(decodedStream(cmapObject));
  assert.match(cmap, /<0000> <FFFF>/, 'the CMap must cover the two-byte code space');
  assert.match(cmap, /<0003> <0047>/, 'CID 0x03 must map to G');
  assert.match(cmap, /<01A7> <0061>/, 'CID 0x01A7 must map to a');
  assert.match(cmap, /<0030> <0032> <0078>/, 'CIDs 0x30..0x32 must map to x, y, z');
  const runs = contentRuns(decodedStream(textStream('identity-h')));
  assert.equal(runs[0].bytes.length % 2, 0, 'the codes must be two bytes each');
  assert.equal([...runs[0].bytes].filter((byte) => byte === 0).length, 4,
    'four of the five codes must have a NUL high byte, so no byte-wise reading can work');
  assert.deepEqual([...runs[0].bytes], [0x00, 0x03, 0x01, 0xA7, 0x00, 0x30, 0x00, 0x31, 0x00, 0x32]);
  assert.notEqual(winAnsiRead(runs[0].bytes).replace(/\0/g, ''), 'Gaxyz',
    'the byte reading must differ from the CMap reading, or the case proves nothing');
}

// object-streams: no xref table at all, the catalog and the page tree inside an
// object stream, and a cross-reference stream to find them.
{
  const bytes = read('object-streams');
  const text = asText(bytes);
  assert.ok(!/^xref$/m.test(text), 'the object-streams case must carry no xref table');
  assert.match(text, /\/Type \/XRef/, 'the document must carry a cross-reference stream');
  assert.match(text, /\/Type \/ObjStm/, 'the document must carry an object stream');
  const xref = readXrefStream(bytes);
  assert.deepEqual(xref.widths, [1, 4, 1], 'the xref stream must declare its field widths');
  const packed = readObjects(bytes).find((object) => object.dict.includes('/Type /ObjStm'));
  assert(packed, 'the object stream must be a stream object in the file');
  const payload = asText(packed.data);
  const declared = Number(/\/N (\d+)/.exec(packed.dict)[1]);
  const first = Number(/\/First (\d+)/.exec(packed.dict)[1]);
  assert.ok(first > 0 && first < packed.data.length,
    '/First must point inside the object stream payload, past the header');
  // The header is the pairs before /First, and the bodies are everything from
  // /First on. Reading the header from /First rather than by a pattern matters:
  // a greedy pattern runs into the first body and loses the member list.
  const header = payload.slice(0, first);
  const members = [...header.matchAll(/(\d+) (\d+)/g)].map((m) => Number(m[1]));
  const offsets = [...header.matchAll(/(\d+) (\d+)/g)].map((m) => Number(m[2]));
  const body = payload.slice(first);
  assert.equal(members.length, declared, '/N must match the number of pairs in the header');
  assert.ok(members.length >= 3, 'the catalog, the page tree and the page must all be packed');
  // The second field of each pair is the byte offset of that object's bytes,
  // counted from the start of the body. It is not the object's position in the
  // list, and this suite used to assert that it was — which pinned the
  // generator to emitting indices, left the fixture unreadable, and kept every
  // check here green the whole time. Each offset is now tested against where it
  // claims to point rather than against its position.
  assert.equal(offsets[0], 0, 'the first packed object must start at offset 0');
  for (let i = 1; i < offsets.length; i++) {
    assert.ok(offsets[i] > offsets[i - 1],
      `the offset for object ${members[i]} must come after that of object ${members[i - 1]}`);
  }
  members.forEach((num, i) => {
    const segment = body.slice(offsets[i], offsets[i + 1] ?? body.length).trimEnd();
    assert.ok(segment.startsWith('<<'),
      `object ${num} must begin at its declared offset ${offsets[i]}, `
      + `got ${JSON.stringify(segment.slice(0, 40))}`);
    assert.ok(segment.endsWith('>>'),
      `object ${num} must be complete at its declared offset, `
      + `got ${JSON.stringify(segment.slice(-40))}`);
  });
  for (const num of members) {
    assert.ok(!new RegExp(`(?:^|\\n)${num} 0 obj\\n`).test(text),
      `object ${num} must live inside the object stream, not at the top level`);
  }
  for (const kind of ['/Type /Catalog', '/Type /Pages', '/Type /Page ']) {
    assert.ok(body.includes(kind), `the packed objects must include ${kind}`);
  }
  // /First must land on the first body, not on the pair list and not past the
  // end: an engine that trusts a wrong /First reads garbage here.
  assert.ok(body.startsWith('<<'), '/First must point at the first object body');
  const run = contentRuns(decodedStream(textStream('object-streams')));
  assert.equal(run.length, 1, 'the content stream stays outside the object stream');
  // The xref stream is the only way in, so its rows must name the object
  // stream and each packed object's own index.
  const start = Number(asText(bytes).match(/startxref\n(\d+)\n%%EOF/)[1]);
  assert.equal(asText(bytes).slice(start, start + `${xref.object.num} 0 obj`.length),
    `${xref.object.num} 0 obj`,
  'startxref must point at the cross-reference stream object itself');
  const rowSize = xref.widths.reduce((a, b) => a + b, 0);
  const table = xref.object.data;
  assert.equal(xref.rows.length * rowSize, table.length,
    'the xref stream must be a whole number of fixed-width rows');
  assert.ok(xref.rows.length > Math.max(...members),
    'the xref stream must have a row for every object, packed ones included');
  for (const [position, num] of members.entries()) {
    const at = num * rowSize;
    assert.equal(table[at], 2, `the xref row for object ${num} must be a type-2 (packed) row`);
    const streamNumber = table.subarray(at + 1, at + 1 + xref.widths[1])
      .reduce((a, b) => a * 256 + b, 0);
    assert.equal(streamNumber, packed.num,
      `the xref row for object ${num} must name the object stream it lives in`);
    assert.equal(table[at + 1 + xref.widths[1]], position,
      `the xref row for object ${num} must name its index in the object stream`);
  }
}

// multi-page: three pages, each distinguishable, and the tree really ordered.
{
  const bytes = read('multi-page');
  const text = asText(bytes);
  const pages = readObjects(bytes).filter((object) => /\/Type \/Page(?!s)/.test(object.dict));
  assert.equal(pages.length, 3, 'the multi-page case must have three page objects');
  assert.match(text, /\/Type \/Pages \/Kids \[[^\]]*\] \/Count 3/,
    'the page tree must declare three children');
  const streams = readObjects(bytes).filter((object) => object.data
    && asText(object.data).includes('Tj'));
  const drawn = streams.map((stream) => contentRuns(decodedStream(stream))
    .map((run) => winAnsiRead(run.bytes)).join(''));
  assert.deepEqual(drawn, PAGE_LINES,
    'each page must carry its own distinguishable text');
  // Page 1 in the kids array must be the first page object in the file, or the
  // page numbers the suite asserts would be a matter of chance.
  const kids = [.../\/Kids \[([^\]]*)\]/.exec(text)[1].matchAll(/(\d+) 0 R/g)].map((m) => Number(m[1]));
  assert.equal(kids[0], pages[0].num, 'the first kid must be the first page object');
}

// two-column: two columns per page, written in column order rather than in
// descending y, so a reader that takes the stream's order for the reading
// order gets the page the wrong way round.
{
  const bytes = read('two-column');
  const runs = contentRuns(decodedStream(contentStream('two-column')));
  assert.equal(runs.length, 8, 'the two-column case must draw eight runs');
  assert.deepEqual(runs.slice(0, 4).map((run) => run.x), Array(4).fill(MARGIN),
    'the left column must sit at the margin');
  assert.deepEqual(runs.slice(4).map((run) => run.x), Array(4).fill(RIGHT_COLUMN_X),
    'the right column must sit past the midpoint');
  assert.ok(RIGHT_COLUMN_X > 595.28 / 2, 'the right column must be on the far side of the page');
  assert.deepEqual(runs.slice(0, 4).map((run) => run.bytes.toString('latin1')), COLUMN_LEFT);
  assert.deepEqual(runs.slice(4).map((run) => run.bytes.toString('latin1')), COLUMN_RIGHT);
  // In stream order the right column's first line follows the left column's
  // last, but in y order it is the highest line on the page. The two orders
  // disagree, which is the whole point of the case.
  assert.ok(runs[4].y > runs[3].y,
    'the two-column page must be ambiguous between stream order and y order');
  for (let i = 1; i < 4; i++) {
    assert.ok(runs[i].y < runs[i - 1].y, 'each column must descend');
  }
}

// positions: three horizontal offsets and a return to the margin, so the
// reconstructed column is a claim about numbers rather than a shape.
{
  const runs = contentRuns(decodedStream(contentStream('positions')));
  assert.deepEqual(runs.map((run) => run.x), POSITION_LINES.map((line) => line.x));
  assert.deepEqual(runs.map((run) => winAnsiRead(run.bytes)), POSITION_LINES.map((l) => l.text));
  assert.ok(new Set(runs.map((run) => run.x)).size >= 3,
    'the positions case must use at least three distinct offsets');
  for (let i = 1; i < runs.length; i++) {
    assert.ok(runs[i].y < runs[i - 1].y, 'the lines must descend down the page');
  }
}

// quoted-paragraph: an indented, quotation-marked line that a text extractor
// would classify as quoted material and skip.
{
  const runs = contentRuns(decodedStream(contentStream('quoted-paragraph')));
  assert.equal(runs.length, 2, 'the case must draw a paragraph and a quotation');
  assert.equal(runs[1].x, MARGIN + 36, 'the quotation must be indented');
  assert.ok(runs[1].bytes.toString('latin1').includes('"'),
    'the quotation must carry quotation marks, as a rendered quotation does');
  const twin = `${PROSE.quoted}\n`;
  const quotedContext = extractText(twin, 'twin.txt', { starts: lineStarts(twin) })[0].context;
  assert.equal(quotedContext, 'authored',
    'the control: as a plain .txt line this copy is authored too, so the comparison is about '
    + 'the quotation marks the .txt extractor masks, not about the context');
}

// rules-invisibility and split-word.
{
  const stream = readObjects(read('rules-invisibility')).find((object) => object.data);
  const runs = contentRuns(decodedStream(stream));
  assert.equal(runs.length, 1, 'the rules case must draw exactly one line');
  assert.equal(winAnsiRead(runs[0].bytes), PROSE.combined,
    'the rules case must draw exactly the string the .txt twin carries');

  const split = contentRuns(decodedStream(contentStream('split-word')));
  assert.equal(split.length, 2, 'the split case must draw two lines');
  assert.ok(winAnsiRead(split[0].bytes).endsWith('the'),
    'the first line must end with the first half of the doubled word');
  assert.ok(winAnsiRead(split[1].bytes).startsWith('the'),
    'the second line must start with the second half');
}

// second-page-undecodable: page 1 must be genuinely readable, or the case is
// not "no partial extraction" but "nothing to extract".
{
  const bytes = read('second-page-undecodable');
  const pages = readObjects(bytes).filter((object) => /\/Type \/Page(?!s)/.test(object.dict));
  assert.equal(pages.length, 2, 'the case must have two pages');
  const [first, second] = pages;
  assert.match(first.dict, /\/F1 \d+ 0 R/, 'page 1 must reference a font');
  assert.ok(!/\/Encoding/.test(second.dict), 'page 2 must not add an encoding');
  const fonts = readObjects(bytes).filter((object) => object.dict.includes('/Type /Font'));
  const good = fonts.find((font) => font.dict.includes('/WinAnsiEncoding'));
  const bad = fonts.find((font) => font.dict.includes('/QQQQQQ+'));
  assert(good && bad, 'the case must carry one readable font and one unreadable font');
  assert.ok(!bad.dict.includes('/ToUnicode'), 'the unreadable font must have no CMap');
  const firstRuns = contentRuns(decodedStream(textStream('second-page-undecodable')));
  assert.equal(winAnsiRead(firstRuns[0].bytes), PROSE.clean,
    'page 1 must be genuinely readable, with real copy on it');
}

// scanned: an image and no text operator of any kind.
{
  const bytes = read('scanned');
  const text = asText(bytes);
  // Two streams in this one: the image XObject's data and the page's content
  // stream. The content stream is the one the page's /Contents points at, so it
  // is selected by that reference rather than by being the first stream.
  const page = readObjects(bytes).find((object) => /\/Type \/Page(?!s)/.test(object.dict));
  const contentsNum = Number(/\/Contents (\d+) 0 R/.exec(page.dict)[1]);
  const body = asText(decodedStream(
    readObjects(bytes).find((object) => object.num === contentsNum)));
  assert.match(body, /\/Im1 Do/, 'the scanned case must draw its image');
  for (const operator of ['Tj', 'TJ', 'Tf', 'BT']) {
    assert.ok(!body.includes(operator),
      `the scanned case must contain no ${operator} operator`);
  }
  assert.ok(!/\)\s*Tj/.test(body), 'the scanned case must show no string operand');
  const image = readObjects(bytes).find((object) => object.dict.includes('/Subtype /Image'));
  assert(image, 'the scanned case must carry a real image XObject');
  assert.match(image.dict, /\/Width \d+ \/Height \d+/, 'the image must have real dimensions');
  assert.ok(!text.includes(PROSE.clean.slice(0, 12)),
    'the scanned case must contain no copy at all');
}

// encrypted: a real encrypted document, not a header bolted onto plaintext.
{
  const bytes = read('encrypted');
  const text = asText(bytes);
  assert.match(text, /trailer[\s\S]*\/Encrypt \d+ 0 R/, 'the trailer must name an /Encrypt dictionary');
  const encrypt = readObjects(bytes).find((object) => object.dict.includes('/Filter /Standard'));
  assert(encrypt, 'the /Encrypt dictionary must use the standard security handler');
  assert.match(encrypt.dict, /\/V 1 \/R 2/, 'the fixture uses the V1/R2 handler');
  assert.match(encrypt.dict, /\/O <[0-9A-F]+>/, 'the handler must carry an owner key');
  assert.match(encrypt.dict, /\/U <[0-9A-F]{64}>/, 'the handler must carry a user key');

  const id = /\/ID \[<([0-9A-F]+)>/.exec(text)[1];
  const { key, O, U } = standardSecurity({
    user: ENCRYPTED_PASSWORD,
    owner: ENCRYPTED_PASSWORD,
    permissions: -3904,
    idFirst: Buffer.from(id, 'hex'),
  });
  assert.equal(encrypt.dict.includes(O.toString('hex').toUpperCase()), true,
    'the /O value must be the one the key schedule derives');
  assert.equal(encrypt.dict.includes(U.toString('hex').toUpperCase()), true,
    'the /U value must be the one the key schedule derives');
  assert.equal(key.length, 5, 'the V1 key is five bytes');

  // The content stream is ciphertext. This is the load-bearing part of the
  // case: a file that merely declares an /Encrypt dictionary would let an
  // extractor read the plaintext straight through, and the refusal would then
  // be testing nothing. So the bytes are proved to be ciphertext by decrypting
  // them, with the key the schedule derives, back to the authored copy.
  const stream = contentStream('encrypted');
  const ciphertext = stream.data;
  assert.ok(!asText(ciphertext).includes('Tj'),
    'the encrypted content stream must be ciphertext, not readable operators');
  assert.ok(!asText(ciphertext).includes(' '),
    'the ciphertext must not contain readable spacing either');
  assert.ok(!asText(bytes).includes(PROSE.clean.slice(0, 12)),
    'the plaintext must not survive anywhere in the encrypted file');
  assert.ok(!asText(bytes).includes('Tj'),
    'no content stream in the encrypted file may be left in the clear');
  const decrypted = rc4(objectKey(key, stream.num), ciphertext);
  const runs = contentRuns(decrypted);
  assert.equal(runs.length, 1, 'the decrypted content stream must draw one run');
  assert.equal(winAnsiRead(runs[0].bytes), PROSE.clean,
    'the content stream must decrypt, with the derived key, to the authored copy');
  // A wrong key does not work, so the round trip above is not a coincidence.
  assert.notEqual(asText(rc4(objectKey(key, stream.num + 1), ciphertext)),
    asText(decrypted), 'the per-object key must depend on the object number');
}

// truncated: a strict prefix of a complete document, cut inside an object.
{
  const full = read('plain-untagged');
  const bytes = read('truncated');
  const text = asText(bytes);
  assert.ok(bytes.length < full.length, 'the truncated case must be shorter than the whole');
  assert.deepEqual(bytes, full.subarray(0, bytes.length),
    'the truncated case must be a strict prefix of a complete document');
  assert.ok(!text.includes('%%EOF'), 'the truncated case must have lost its end marker');
  assert.ok(!text.includes('startxref'), 'the truncated case must have lost its xref pointer');
  assert.ok(!text.includes('trailer'), 'the truncated case must have lost its trailer');
  const opens = (text.match(/(?:^|\n)stream\n/g) || []).length;
  const closes = (text.match(/\nendstream/g) || []).length;
  assert.equal(opens, closes + 1, 'the cut must leave exactly one stream open');
  assert.ok(text.startsWith('%PDF-'), 'the truncated case must still have valid magic bytes');
}

// not-a-pdf: right everything, wrong magic.
{
  const bytes = read('not-a-pdf');
  const text = asText(bytes);
  assert.ok(!text.startsWith('%PDF-'), 'the not-a-pdf case must not carry the PDF magic');
  assert.equal(text.slice(0, 9), '%PDX-1.7\n', 'the wrong magic must be exactly what it claims');
  assert.deepEqual(bytes.subarray(9), read('plain-untagged').subarray(9),
    'everything after the header must be a complete document, so only the magic is wrong');
  assert.ok(!text.includes('\x00'), 'the case must not be binary: it is a text file with a bad header');
}

// The decode register's four fixtures, each proved to exhibit the property it
// is named for before the engine is allowed near it. The first two are the
// two sides of one boundary and are worthless apart: `two-column-narrow` puts
// a 12pt gutter in front of the detector, `hanging-indent` puts a 7.76pt one
// in front of the same detector, and the constant that decides between them
// is only held by both assertions standing at once.
{
  // two-column-narrow: eight lines, drawn column by column, with a gutter of
  // exactly twelve points. The width of a glyph is arithmetic rather than a
  // measurement, because a standard-14 font with no /Widths array is given its
  // per-font default of 556/1000 em by the engine, which is 5.56pt at 10pt.
  const runs = contentRuns(decodedStream(contentStream('two-column-narrow')));
  assert.deepEqual(runs.map((run) => winAnsiRead(run.bytes)),
    [...NARROW_LEFT, ...NARROW_RIGHT],
    'the narrow case must draw its four left lines first, then its four right');
  const longest = Math.max(...NARROW_LEFT.map((text) => text.length));
  assert.equal(longest, NARROW_LEFT_CHARS,
    'every left-column line must be as long as the gutter arithmetic claims');
  const leftEnd = MARGIN + longest * NARROW_GLYPH_PT;
  assert.ok(Math.abs(leftEnd - NARROW_LEFT_END_X) < 1e-9,
    `the left column must end at ${NARROW_LEFT_END_X}, not ${leftEnd}`);
  const gutter = NARROW_RIGHT_X - leftEnd;
  assert.ok(Math.abs(gutter - NARROW_GUTTER_PT) < 1e-9,
    `the narrow gutter must be ${NARROW_GUTTER_PT}pt, not ${gutter}pt`);
  assert.ok(runs.every((run) => run.x === MARGIN || run.x === NARROW_RIGHT_X),
    'the narrow case must use exactly two column origins');
  // Where that sits: above the 8.93pt floor the constant now carries, and well
  // below the 20.83pt one it carried before this pair existed.
  assert.ok(gutter > 8.93 && gutter < 20.83,
    `the narrow gutter must sit between the two floors, got ${gutter}pt`);
  for (const run of runs) {
    const width = winAnsiRead(run.bytes).length * NARROW_GLYPH_PT;
    assert.ok(width < 0.68 * 595.28,
      'no line of the narrow case may span the measure, or it would not vote');
  }
}

// hanging-indent: sixteen rows, two runs each, where the widest run in the
// left group is "[16]" and the entries start at 84 — a gap of 7.76pt, which is
// below the 8.93pt floor and above the 7.14pt one. Lowering the constant past
// that band splits every row of this list in two.
{
  const runs = contentRuns(decodedStream(contentStream('hanging-indent')));
  assert.equal(runs.length, HANGING_ROWS * 2, 'each row must draw a number and an entry');
  const drawn = [];
  for (let row = 0; row < HANGING_ROWS; row++) drawn.push(`[${row + 1}]`, HANGING_ENTRIES[row]);
  assert.deepEqual(runs.map((run) => winAnsiRead(run.bytes)), drawn,
    'the rows must alternate number, entry, number, entry');
  const widest = Math.max(...Array.from({ length: HANGING_ROWS },
    (_, i) => `[${i + 1}]`.length));
  assert.equal(widest, 4, 'the widest number must be four characters, from "[16]"');
  const numEnd = MARGIN + widest * NARROW_GLYPH_PT;
  assert.ok(Math.abs(numEnd - HANGING_NUM_END_X) < 1e-9,
    `the numbers must end at ${HANGING_NUM_END_X}, not ${numEnd}`);
  const gap = HANGING_TEXT_X - numEnd;
  assert.ok(Math.abs(gap - HANGING_GAP_PT) < 1e-9,
    `the hanging gap must be ${HANGING_GAP_PT}pt, not ${gap}pt`);
  assert.ok(gap > 7.14 && gap < 8.93,
    `the hanging gap must sit between 7.14pt and 8.93pt, got ${gap}pt`);
  assert.ok(runs.every((run) => run.x === MARGIN || run.x === HANGING_TEXT_X),
    'the hanging case must use exactly two x origins, the margin and the indent');
}

// rotated-page: the page really does carry /Rotate, and the content stream
// really does draw the copy turned. A fixture that forgot either would still
// be a PDF and would still extract.
{
  const text = asText(read('rotated-page'));
  assert.ok(text.includes(`/Rotate ${ROTATE_DEGREES}`),
    'the rotated case must carry /Rotate on its page');
  const stream = asText(decodedStream(contentStream('rotated-page')));
  assert.ok(stream.includes('0 1 -1 0'),
    'the rotated case must draw its copy through a quarter-turn matrix');
  const shown = (stream.match(/ Tj/g) || []).length;
  assert.equal(shown, ROTATED_LINES.length,
    `the rotated case must show ${ROTATED_LINES.length} strings, got ${shown}`);
  const turns = (stream.match(/0 1 -1 0/g) || []).length;
  assert.equal(turns, ROTATED_LINES.length,
    `every drawn line must pass through the quarter-turn, got ${turns}`);
  assert.ok(stream.includes('1 0 0 1 0 0 Tm'),
    'each turned line must set its own text matrix at the origin');
}

// non-latin: every code is a plain single byte, and the copy it stands for is
// not expressible in those bytes. That gap is the whole fixture — a reader
// that ignored the /ToUnicode CMap would return ordinary Latin letters.
{
  const codes = [...NON_LATIN_CODES];
  assert.ok(codes.every((code) => code >= 0x21 && code <= 0x7E),
    'every code must be a printable single byte');
  assert.ok(new Set(codes).size === codes.length, 'each code must map to one character');
  const points = [...NON_LATIN_TEXT].map((ch) => ch.codePointAt(0));
  assert.ok(points.some((point) => point > 0xFF),
    'the expected copy must contain a character no single byte can stand for');
  assert.equal([...NON_LATIN_TEXT].filter((ch) => ch === ' ').length, 2,
    'the expected copy must contain the two spaces the codes map to');
}

// vertical-gap: the two lines really are drawn 96pt of whitespace apart, so
// the assertion below is about the extractor and not about a fixture that
// happened to place its lines close together.
{
  const runs = contentRuns(decodedStream(contentStream('vertical-gap')));
  assert.deepEqual(runs.map((run) => winAnsiRead(run.bytes)), VERTICAL_GAP_LINES,
    'the vertical-gap case must draw exactly its two lines');
  assert.deepEqual(runs.map((run) => run.y), [700, 700 - LEADING - VERTICAL_GAP_PT],
    'the vertical-gap case must place its lines at the baselines it claims');
  assert.equal(runs[0].y - runs[1].y - LEADING, VERTICAL_GAP_PT,
    `the two lines must be ${VERTICAL_GAP_PT}pt apart beyond one leading`);
  assert.ok(VERTICAL_GAP_PT > 4 * LEADING,
    'the gap must be far larger than any plausible paragraph threshold, or the '
    + 'case would prove nothing about it');
}

// --- A3. the copy itself, checked through the real rule layer ---------------
//
// The integration claim is that a PDF unit is ordinary copy. Its first half is
// checkable today, because the .txt side of the comparison needs no engine:
// the four defects in the fixture must be exactly the four the shipped rules
// report for the identical string in a plain file.
{
  const { meta, ids: catalogueIds } = loadCatalogue(ROOT);
  const cfg = validateConfig({}, { knownIds: catalogueIds });
  const baseline = loadBaselineProfile(ROOT, catalogueIds);
  globalThis.__ctx = makeContext({ cfg, baseline, meta });
}
const ctx = globalThis.__ctx;
delete globalThis.__ctx;

{
  const twin = `${PROSE.combined}\n`;
  const found = runEditorialRules(
    extractText(twin, 'twin.txt', { starts: lineStarts(twin) }), ctx);
  const byRule = new Map();
  for (const finding of found) byRule.set(finding.ruleId, (byRule.get(finding.ruleId) || 0) + 1);
  // UE-HR006 joins since the acronym rule landed: "PRIOR" is a five-letter
  // capitalised word inside the acronym window, the residual overlap with
  // shouted words the rule's guard notes document (the register rule reports
  // the shouting on the same token).
  assert.deepEqual([...byRule.keys()].sort(), ['UE-GR001', 'UE-HR006', 'UE-NU001', 'UE-RE008', 'UE-SP001'],
    'the twin copy must exercise the spelling, doubled-word, ambiguous-date, shouted-word and acronym rules');
  globalThis.__twinIds = [...byRule.keys()].sort();
  globalThis.__twinCounts = Object.fromEntries([...byRule.entries()].sort());
  globalThis.__twinFindings = found;
  for (const [rule, count] of byRule) {
    assert.equal(count, 1, `${rule} must fire exactly once on the twin copy`);
  }
}

console.log('ok — fixtures: encoders against their specifications, and every case shown to '
  + `exhibit the property it claims (${CASES.length} cases: ${accepted.length} accepted, `
  + `${refused.length} refused)`);

// ===========================================================================
// Part B — the engine contract.
//
// Everything below needs lib/pdf-extract.mjs. It is written against the Phase 8
// contract in .feedbacks/PHASE-8-PLAN.md §1, so it compiles and runs the moment
// the adapter lands.
// ===========================================================================

const ENGINE_PATH = '../lib/pdf-extract.mjs';
let engine = null;
let engineFailure = null;
try {
  engine = await import(ENGINE_PATH);
} catch (error) {
  engineFailure = error;
}

// An absent engine is unconditionally a failure. It was briefly escapable with
// UN_PDF_ENGINE_PENDING=1 while the adapter was still being written in another
// worktree; that window has closed, and a variable that turns missing coverage
// into a green run is exactly the quiet partial pass this suite exists to
// prevent. Part A passing on its own is not a pass.
if (!engine) {
  console.error(`FAIL — lib/pdf-extract.mjs is not in the tree, so the engine half of this `
    + `suite cannot run.\n${engineFailure && engineFailure.message}\n`
    + 'Part A ran and passed. That is not a pass on its own.');
  process.exit(1);
}

const { extractPdf, pdfRefusalMessage, PdfRefusalError, PDF_REFUSAL_CODES } = engine;

for (const code of ['NOT_A_PDF', 'ENCRYPTED', 'SCANNED', 'UNDECODABLE_FONT', 'MALFORMED']) {
  assert.equal(typeof PDF_REFUSAL_CODES[code], 'string',
    `the contract must publish a reason for ${code}`);
  assert.ok(PDF_REFUSAL_CODES[code].length > 10,
    `the reason for ${code} must name the reason, not the code`);
}
assert.equal(typeof extractPdf, 'function', 'the contract must publish extractPdf');
assert.equal(typeof PdfRefusalError, 'function', 'the contract must publish PdfRefusalError');

/** Extract a case, or record the refusal it produced. */
function attempt(name) {
  const file = corpus[name];
  const bytes = read(name);
  try {
    return { units: extractPdf(bytes, file) };
  } catch (error) {
    return { error };
  }
}

/** Read the two cases as a rule, and fail with a message that names the case. */
function expectRefusal(name, code) {
  const { error } = attempt(name);
  const label = `the ${name} case`;
  assert(error, `${label} must be refused, not extracted`);
  assert(error instanceof PdfRefusalError,
    `${label} must be refused with a PdfRefusalError, not a ${error.constructor.name}: ${error.message}`);
  assert.equal(error.code, code,
    `${label} must be refused with code ${code}, got ${error.code}: ${error.message}`);
  // The code must be a key the rest of the tool can look up. `isPdfRefusal`
  // and `asRefusal` both test `Object.hasOwn(PDF_REFUSAL_CODES, error.code)`,
  // so a code that is the description rather than the key does not raise an
  // error — it silently downgrades to MALFORMED and the reader is told the
  // document is corrupt when it is really only unreadable. Nothing else in
  // this function would catch that.
  assert.ok(Object.hasOwn(PDF_REFUSAL_CODES, error.code),
    `${label}: the code "${error.code}" must be a key of PDF_REFUSAL_CODES`);
  // The engine must explain itself. Its message carries the specific detail —
  // which font, which page — and §1 of the plan fixes the codes table rather
  // than the wording of every message, so the detail is expected to be its own
  // sentence here, not a copy of the canonical reason.
  assert.ok(typeof error.message === 'string' && error.message.trim().length > 0,
    `${label}: the refusal must explain itself, got ${JSON.stringify(error.message)}`);
  // What a reader is actually shown, which is not what the engine threw. The
  // canonical reason must reach the reader whatever the engine put in its
  // message, and it must be followed by a remedy: a refusal that names only a
  // dead end leaves the reader to work out the next step themselves. The reason
  // half was asserted against `error.message` before, which tested the engine's
  // internal wording instead of the surface users read and never checked the
  // remedy at all.
  const reason = PDF_REFUSAL_CODES[error.code];
  const shown = pdfRefusalMessage(error, label);
  assert.ok(shown.includes(reason),
    `${label}: the message a reader sees must state the reason ("${reason}"), `
    + `got "${shown}"`);
  const afterReason = shown.slice(shown.indexOf(reason) + reason.length);
  assert.ok(/\.\s+\S/.test(afterReason),
    `${label}: the message a reader sees must offer a remedy after the reason, `
    + `got "${shown}"`);
  assert.ok(!('units' in error), `${label}: a refusal must carry no units`);
  assert.ok(!('warnings' in error), `${label}: a refusal must carry no warnings`);
  return error;
}

// --- B1. every refusal, with its exact code and a named reason --------------

for (const entry of refused) {
  const started = Date.now();
  expectRefusal(entry.name, entry.code);
  const elapsed = Date.now() - started;
  assert.ok(elapsed < 5000, `the ${entry.name} case must refuse promptly, took ${elapsed}ms`);
}

// The refusal codes are a closed set: a document that is refused for a reason
// outside it would be a refusal the documentation cannot describe.
{
  const published = Object.keys(PDF_REFUSAL_CODES).sort();
  assert.deepEqual(published, ['ENCRYPTED', 'MALFORMED', 'NOT_A_PDF', 'SCANNED', 'UNDECODABLE_FONT'],
    'the published refusal codes are the five the contract fixes');
  for (const entry of refused) {
    assert.ok(published.includes(entry.code), `${entry.name} must use a published code`);
  }
}

// No partial extraction: page 1 is readable and page 2 is not, so returning
// page 1 would report findings at positions that silently omit half the file.
{
  const error = expectRefusal('second-page-undecodable', 'UNDECODABLE_FONT');
  assert.ok(!JSON.stringify(error.detail).includes(PROSE.clean),
    'a refusal must not hand back the copy it managed to read');
}

// --- B2. every accepted case extracts, and the reconstruction is provable ----

/** The units in reading order, as a plain list of strings. */
const linesOf = (units) => units.map((unit) => unit.text);

for (const entry of accepted) {
  const { units, error } = attempt(entry.name);
  assert(!error,
    `the ${entry.name} case must be extracted, got ${error && error.constructor.name}: `
    + `${error && error.message}`);
  assert.ok(Array.isArray(units), `the ${entry.name} case must return an array of units`);
  assert.ok(units.length > 0, `the ${entry.name} case must produce at least one unit`);
  for (const unit of units) {
    assert.equal(typeof unit.text, 'string');
    assert.ok(unit.text.trim().length > 0, 'a unit may not be blank');
    assert.equal(typeof unit.raw, 'string', 'every unit keeps the slice it was built from');
    assert.equal(unit.file, corpus[entry.name], 'every unit names the file it came from');
    assert.ok(Number.isInteger(unit.line) && unit.line >= 1,
      `${entry.name}: line must be a positive integer, got ${unit.line}`);
    assert.ok(Number.isInteger(unit.column) && unit.column >= 1,
      `${entry.name}: column must be a positive integer, got ${unit.column}`);
    // The map discipline: a map is either absent or exactly one source offset
    // per character of the text, in order, inside the unit's own slice. A map
    // that drifts is how a finding lands on the wrong character.
    if (unit.map !== null && unit.map !== undefined) {
      assert.equal(unit.map.length, unit.text.length,
        `${entry.name}: the offset map must have one entry per character of the text`);
      let previous = -1;
      for (const at of unit.map) {
        assert.ok(Number.isInteger(at), `${entry.name}: map entries must be integer offsets`);
        assert.ok(at >= unit.offset && at <= unit.offset + unit.raw.length,
          `${entry.name}: a mapped offset ${at} falls outside the unit's own slice`);
        assert.ok(at >= previous, `${entry.name}: map offsets must not go backwards`);
        previous = at;
      }
    }
  }
  // Line numbers run continuously from 1 in reading order.
  const numbers = units.map((unit) => unit.line);
  assert.deepEqual(numbers, [...numbers].sort((a, b) => a - b),
    `${entry.name}: units must come back in reading order`);
  assert.equal(numbers[0], 1, `${entry.name}: the first line of the document is line 1`);
  assert.equal(numbers[numbers.length - 1], units.length,
    `${entry.name}: one visual line is one line number, with no gaps`);
  // Columns on a single-run line are ordered by their horizontal offset.
  const columns = units.map((unit) => unit.column);
  assert.ok(columns.every((value) => value >= 1), `${entry.name}: every column must be positive`);
}

// The exact reconstructed copy for each case, against the text that was put in.
{
  const cases = [
    ['plain-untagged', FILTER_COPY],
    ['differences', ['ÁÇ']],
    ['to-unicode', ['XYabc']],
    ['identity-h', ['Gaxyz']],
    ['multi-page', PAGE_LINES],
    ['rules-invisibility', [PROSE.combined]],
    ['split-word', ['The delegation reviewed the', 'the draft of the resolution.']],
    ['non-latin', [NON_LATIN_TEXT]],
  ];
  for (const [name, expected] of cases) {
    const { units } = attempt(name);
    assert.deepEqual(linesOf(units), expected,
      `the ${name} case must reconstruct exactly the copy that was authored`);
  }

  // The filter cases all carry the same two lines as the uncompressed control.
  const plain = linesOf(attempt('plain-untagged').units);
  for (const name of ['flate', 'lzw', 'ascii85', 'asciihex', 'runlength',
    'differences']) {
    if (name === 'differences') continue;
    assert.deepEqual(linesOf(attempt(name).units), plain,
      `the ${name} case must reconstruct the same copy as the uncompressed control`);
  }

  // two-column: column-major reading order, left column then right column.
  {
    const { units } = attempt('two-column');
    assert.deepEqual(linesOf(units), [...COLUMN_LEFT, ...COLUMN_RIGHT],
      'the two-column page must be read column by column, not row by row');
    const left = units.slice(0, 4).map((unit) => unit.column);
    const right = units.slice(4).map((unit) => unit.column);
    assert.ok(Math.max(...left) < Math.min(...right),
      'the right column must start to the right of every line in the left column');
  }
}

// positions: the reconstructed column follows the horizontal offset of the run.
{
  const { units } = attempt('positions');
  assert.deepEqual(linesOf(units), POSITION_LINES.map((line) => line.text),
    'the positions case must reconstruct the copy it was given');
  const columns = units.map((unit) => unit.column);
  assert.equal(columns[0], 1, 'a run at the left margin must be column 1');
  assert.ok(columns[1] > columns[0],
    'an indented run must report a larger column than the margin run above it');
  assert.ok(columns[2] > columns[1],
    'a run indented further must report a larger column still');
  assert.equal(columns[3], columns[0],
    'a run back at the margin must report the margin column again');
}

// --- B2b. the two-column threshold, held from both sides --------------------
//
// One constant decides this, and it is a fraction of the page width. The pair
// below exists because a threshold with one fixture has one direction of
// drift: a case that must be split, and a case that must not be, are the only
// way to make raising it and lowering it both visible.
//
// Raising the floor above 12pt of this 595.28pt page stops the narrow case
// splitting, and its assertion fails on the column order. Lowering it below
// 7.76pt splits the hanging list, and its assertion fails on the row count.
{
  const { units } = attempt('two-column-narrow');
  assert.equal(units.length, NARROW_LEFT.length + NARROW_RIGHT.length,
    `a ${NARROW_GUTTER_PT}pt gutter must still produce one line per drawn line, `
    + `got ${units.length}`);
  assert.deepEqual(linesOf(units), [...NARROW_LEFT, ...NARROW_RIGHT],
    'a twelve-point gutter must be read column by column, not row by row');
  const left = units.slice(0, NARROW_LEFT.length).map((unit) => unit.column);
  const right = units.slice(NARROW_LEFT.length).map((unit) => unit.column);
  assert.ok(Math.max(...left) < Math.min(...right),
    'the narrow right column must still start to the right of every left line');

  const hanging = attempt('hanging-indent');
  assert(!hanging.error, `the hanging case must extract, got ${hanging.error && hanging.message}`);
  assert.equal(hanging.units.length, HANGING_ROWS,
    `a ${HANGING_GAP_PT}pt indent gap is not a column gutter: the list must come back as `
    + `${HANGING_ROWS} rows, not ${hanging.units.length} halves of rows`);
  hanging.units.forEach((unit, index) => {
    assert.ok(unit.text.startsWith(`[${index + 1}] `),
      `row ${index + 1} must keep its number and its entry on one line, got `
      + JSON.stringify(unit.text));
  });
}

// The rotated page. What must hold is the copy and its order, and both do:
// three displayed lines come back in the order they were drawn. What does not
// hold is the line structure — in content space the three share a baseline, so
// they arrive as one reconstructed line.
//
// The assertion below is a tripwire rather than an endorsement. It pins the
// limitation so that a change which applies /Rotate to run coordinates before
// lines are grouped fails here and forces this comment, and the limitation in
// the documentation, to be updated with it. A limitation nobody can prove has
// stopped being a limitation is how one survives a refactor unnoticed.
{
  const { units } = attempt('rotated-page');
  const copy = linesOf(units).join(' ');
  assert.equal(copy, ROTATED_LINES.join(' '),
    'the copy of a rotated page must survive whole and in drawing order, got ' + JSON.stringify(copy));
  assert.equal(units.length, 1,
    'KNOWN LIMITATION: the three displayed lines of a /Rotate page arrive as one '
    + `reconstructed line, and the fixture asserts that so it cannot pass unnoticed. `
    + `When the page rotation is applied to run coordinates before grouping, this `
    + `becomes ${ROTATED_LINES.length} and the comment above must change with it; got ${units.length}`);
}

// The vertical gap, which is the lock on how lib/pdf-text.mjs describes its
// own unit boundary. The extractor never measures a vertical gap, so no size
// of one may ever merge two lines — a paragraph break and an ordinary line
// break are deliberately the same thing here. A change that starts joining
// lines across whitespace fails this, and the module header would then have
// to describe the new behaviour rather than the old one.
{
  const { units } = attempt('vertical-gap');
  assert.equal(units.length, VERTICAL_GAP_LINES.length,
    `a ${VERTICAL_GAP_PT}pt vertical gap must leave ${VERTICAL_GAP_LINES.length} units, `
    + `got ${units.length} — no vertical gap may merge two visual lines`);
  assert.deepEqual(linesOf(units), VERTICAL_GAP_LINES,
    'both paragraphs must come back whole and in order');
}

// --- B3. the page number ----------------------------------------------------

{
  const { units } = attempt('multi-page');
  assert.equal(units.length, PAGE_LINES.length, 'one line per page, no line invented or lost');
  units.forEach((unit, index) => {
    assert.equal(unit.pdfPage, index + 1,
      `unit ${index} ("${unit.text}") must carry its own page number`);
  });
  assert.ok(units[0].text.startsWith('Page one'), 'page 1 must come first');
  assert.ok(units[1].text.startsWith('Page two'), 'page 2 must come second');
  assert.ok(units[2].text.startsWith('Page three'), 'page 3 must come third');
  // Lines are continuous across the document, not restarted per page.
  assert.deepEqual(units.map((unit) => unit.line), [1, 2, 3],
    'line numbers run continuously across pages');
}

// --- B4. the context is always authored -------------------------------------

{
  for (const entry of accepted) {
    const { units } = attempt(entry.name);
    for (const unit of units) {
      assert.equal(unit.context, 'authored',
        `the ${entry.name} case: context is always authored, got ${unit.context}`);
    }
  }
}

// The consequence of that, which is the part a reader has to be told about: a
// quotation rendered in a PDF is checked, where the identical copy in a .txt is
// quoted material and is never checked. Both halves are asserted, so the
// limitation cannot be quietly lost and the check cannot quietly stop working.
//
// Three controls, because "the PDF fires" is only interesting next to "the
// .txt does not" and "the .txt fires when the quotation marks come off".
{
  const { units } = attempt('quoted-paragraph');
  const quotation = units.find((unit) => unit.text.includes('The chair read'));
  assert(quotation, 'the quotation must come back as copy');
  assert.equal(quotation.context, 'authored',
    'a quotation in a PDF is indistinguishable from a paragraph and is reported as authored');

  const pdfFindings = runEditorialRules(units, ctx);
  const spelling = pdfFindings.filter((finding) => finding.ruleId === 'UE-SP001');
  assert.ok(spelling.length > 0,
    'the quotation in the PDF must be checked: the rules cannot tell it from authored copy');
  assert.ok(spelling.some((finding) => finding.current === 'organization'),
    `the defect inside the quotation is the one that must be reported: ${JSON.stringify(spelling)}`);

  const quotedTwin = `${PROSE.quoted}\n`;
  const quotedUnits = extractText(quotedTwin, 'twin.txt', { starts: lineStarts(quotedTwin) });
  const quotedFindings = runEditorialRules(quotedUnits, ctx);
  assert.ok(!quotedFindings.some((finding) => finding.ruleId === 'UE-SP001'),
    'the .txt twin of the same line masks its quoted material, so the rule stays silent — '
    + 'and that silence is exactly what a PDF cannot reproduce');

  // A quote-prefixed line is the other .txt form of quoted material: the whole
  // unit is dropped, not masked.
  const prefixed = `> ${PROSE.spelling}\n`;
  assert.ok(!runEditorialRules(extractText(prefixed, 'twin.txt',
    { starts: lineStarts(prefixed) }), ctx).some((f) => f.ruleId === 'UE-SP001'),
  'a quote-prefixed .txt line is quoted material and is never checked');

  // With the quotation marks removed the .txt does fire, which is what makes
  // the two silences above meaningful rather than the rule being broken.
  const bare = `${PROSE.spelling}\n`;
  assert.ok(runEditorialRules(extractText(bare, 'twin.txt', { starts: lineStarts(bare) }), ctx)
    .some((finding) => finding.ruleId === 'UE-SP001'),
  'the same defect as bare .txt prose must fire, so the two silences are about quoting');
}

// --- B5. the rules cannot tell a PDF unit from any other --------------------

{
  const { units } = attempt('rules-invisibility');
  const pdfFindings = runEditorialRules(units, ctx);
  const pdfByRule = new Map();
  for (const finding of pdfFindings) pdfByRule.set(finding.ruleId, (pdfByRule.get(finding.ruleId) || 0) + 1);
  const pdfIds = [...pdfByRule.keys()].sort();
  const twinIds = globalThis.__twinIds;

  // The message names which ids moved, not just that something did. The
  // likeliest single cause is a missing unit map: UE-GR001 is fixable, and
  // every fixable rule refuses to fire on a unit whose map it cannot trust, so
  // a PDF adapter that returned `map: null` would lose exactly the fixable
  // rules and keep the rest. That is the failure this message is written for.
  const missing = twinIds.filter((id) => !pdfIds.includes(id));
  const extra = pdfIds.filter((id) => !twinIds.includes(id));
  assert.deepEqual(missing, [],
    `the rules-invisibility case lost ${missing.join(', ')}. The txt twin fires `
    + `${twinIds.join(', ')}; the PDF fires only ${pdfIds.join(', ')} (a fixable rule needs a `
    + 'trustworthy unit map, so check that every PDF unit carries one). '
    + `Per rule on the txt side: ${JSON.stringify(globalThis.__twinCounts)}`);
  assert.deepEqual(extra, [],
    `the rules-invisibility case gained ${extra.join(', ')}: the PDF fires a rule `
    + 'the .txt twin does not');
  assert.deepEqual(Object.fromEntries([...pdfByRule.entries()].sort()), globalThis.__twinCounts,
    'a PDF must produce exactly as many findings per rule as the identical .txt copy');
  for (const finding of pdfFindings) {
    const twin = globalThis.__twinFindings.find((f) => f.ruleId === finding.ruleId);
    assert.equal(finding.severity, twin.severity,
      `${finding.ruleId} must carry the same severity from a PDF as from a txt file`);
    assert.equal(finding.current, twin.current,
      `${finding.ruleId} must quote the same copy from a PDF as from a txt file`);
    // `suggestion` is null for a rule whose suggestion comes from the
    // catalogue, so the comparison is between the two sides rather than
    // against a shape: whatever the .txt gives, the PDF must give the same.
    assert.equal(finding.suggestion, twin.suggestion,
      `${finding.ruleId} must give the same suggestion from a PDF as from a txt file`);
    // The position discipline: a finding on a PDF unit must point at a line
    // the document has, and at a column inside the unit it came from, which is
    // the only thing "column" can honestly mean without a source.
    const host = units.find((unit) => unit.text.includes(twin.current));
    assert(host, `${finding.ruleId} must name a unit the document really has`);
    const at = locate(host, finding.current, host.text.indexOf(finding.current));
    assert.ok(Number.isInteger(at.line) && at.line >= 1 && at.line <= units.length,
      `${finding.ruleId} reported line ${at.line}, outside the ${units.length} lines the document has`);
    assert.ok(at.column >= host.column,
      `${finding.ruleId} reported column ${at.column}, before its own unit starts at ${host.column}`);
  }
}

// split-word: a doubled word across a visual line break. The contract does not
// say whether a rule may span a line, so the assertion is only about honesty —
// every reported position must name a line that exists, and the copy a finding
// quotes must be copy the document really contains.
{
  const { units } = attempt('split-word');
  const whole = units.map((unit) => unit.text).join(' ');
  const findings = runEditorialRules(units, ctx);
  for (const finding of findings) {
    assert.ok(finding.line >= 1 && finding.line <= units.length,
      `the split-word case: ${finding.ruleId} reported line ${finding.line}, `
      + `outside the ${units.length} lines the document has`);
    const quoted = finding.matched ?? finding.current;
    assert.ok(whole.includes(quoted.replace(/\s+/g, ' ').trim()),
      `the split-word case: ${finding.ruleId} quoted "${quoted}", which is not in the document`);
  }
}

// --- B6. determinism --------------------------------------------------------

for (const entry of CASES) {
  const file = corpus[entry.name];
  const bytes = read(entry.name);
  const first = attempt(entry.name);
  const second = attempt(entry.name);
  if (entry.must === 'refuse') {
    assert(first.error && second.error,
      `the ${entry.name} case must refuse both times`);
    assert.equal(first.error.code, second.error.code,
      `the ${entry.name} case must refuse for the same reason both times`);
    assert.equal(first.error.message, second.error.message,
      `the ${entry.name} case must refuse with the same message both times`);
    continue;
  }
  assert.deepEqual(second.units, first.units,
    `the ${entry.name} case must extract identical units on a second run`);
  assert.equal(Buffer.compare(fs.readFileSync(file), bytes), 0,
    `the ${entry.name} case must not be written to by extraction`);
}

// --- B7. a refusal is a clean refusal, never a crash ------------------------

{
  for (const entry of refused) {
    const bytes = read(entry.name);
    let thrown = null;
    try {
      extractPdf(bytes, corpus[entry.name]);
    } catch (error) {
      thrown = error;
    }
    assert(thrown, `the ${entry.name} case must throw, not return`);
    assert.equal(thrown.constructor, PdfRefusalError,
      `the ${entry.name} case must throw exactly a PdfRefusalError, `
      + `not a ${thrown.constructor.name}: ${thrown.message}`);
    assert.equal(thrown.name, 'PdfRefusalError', 'the error must name itself');
    assert.ok(thrown instanceof Error, 'the refusal must be an Error');
    assert.ok(typeof thrown.message === 'string' && thrown.message.length > 0,
      'the refusal must say something');
    // A crash caught and relabelled is still a crash. Node's own TypeError
    // phrasings are the observable signature of one, so they are banned in a
    // refusal message: "cannot read properties of undefined" means the engine
    // walked off the end of a malformed document and dressed the fall.
    for (const crash of ['Cannot read propert', 'is not a function', 'of undefined',
      'of null', 'Assignment to constant', 'Maximum call stack']) {
      assert.ok(!thrown.message.includes(crash),
        `the ${entry.name} case refused with a crash message rather than a reason: `
        + `"${thrown.message}" contains "${crash}"`);
    }
    assert.ok(typeof thrown.stack === 'string' && thrown.stack.includes('extract'),
      `the ${entry.name} refusal must carry a stack from inside the extractor`);
  }
  // A refusal is also not a hang: a bounded number of milliseconds per case is
  // asserted above for every refusal, and these are the pathological shapes.
  for (const name of ['scanned', 'encrypted', 'truncated', 'not-a-pdf']) {
    const started = Date.now();
    attempt(name);
    assert.ok(Date.now() - started < 5000, `the ${name} case must not hang`);
  }
}

// --- B8. nothing about the extracted copy is invented -----------------------
//
// A decoding can go wrong in three directions: it can invent characters, drop
// them, or repeat them. The exact expected text is already asserted per case,
// so what is added here is a bound that holds for every case whatever the
// engine's decoding: no unit without a drawn run behind it, and no more
// characters out than the document put codes in.
//
// The count was originally an equality — one unit per drawn run — because
// every fixture then on the list drew exactly one run per visual line, so the
// two counts were the same number arrived at differently. Two cases added by
// the decode register draw several runs on one line on purpose: the hanging
// list draws a number and then its entry at a second x, and the rotated page
// draws one block per quarter turn. For those the equality would be wrong
// about the engine rather than strict with it — a line drawn in three pieces
// is one line — so they are bounded instead of equated, and the character
// bound below is asserted across the whole case rather than index by index,
// where a unit built from two runs could not be measured against one.
//
// The "no character the document never draws" bound is deliberately *not*
// asserted across every case. It is only sound where the font is a plain
// WinAnsi encoding, because a ToUnicode CMap legitimately turns a code that
// does not look like a letter into one — which is exactly what the
// to-unicode and identity-h cases are for. It is asserted for that family
// alone, below.

const WINANSI_FAMILY = ['plain-untagged', 'flate', 'lzw', 'ascii85', 'asciihex', 'runlength'];

// Cases whose fixture draws more than one run on a visual line. Each is named
// with the reason, so the list cannot quietly become a place where assertions
// go to be skipped.
const MULTI_RUN_PER_LINE = new Map([
  ['hanging-indent', 'a number in the margin and its entry at the indent'],
  ['rotated-page', 'one text block per quarter turn, all on one content baseline'],
]);

for (const entry of accepted) {
  const { units } = attempt(entry.name);
  const runs = readObjects(read(entry.name))
    .filter((object) => object.data && !/\/Subtype \/Image/.test(object.dict))
    .flatMap((object) => {
      try { return contentRuns(decodedStream(object)); } catch { return []; }
    });
  assert.ok(runs.length > 0, `the ${entry.name} case must draw at least one text run`);
  const marks = (text) => text.replace(/\s/g, '').length;

  if (MULTI_RUN_PER_LINE.has(entry.name)) {
    const codes = runs.reduce((total, run) => total + run.bytes.length, 0);
    const produced = units.reduce((total, unit) => total + marks(unit.text), 0);
    assert.ok(units.length <= runs.length,
      `the ${entry.name} case (${MULTI_RUN_PER_LINE.get(entry.name)}) must not return more `
      + `units than it drew runs: ${runs.length} drawn, ${units.length} returned`);
    assert.ok(produced <= codes,
      `the ${entry.name} case: decoding produced ${produced} characters from ${codes} codes `
      + '— nothing may be invented, so the total may only fall');
    continue;
  }

  assert.equal(units.length, runs.length,
    `the ${entry.name} case must return one unit per drawn run: ${runs.length} drawn, `
    + `${units.length} returned (${JSON.stringify(units.map((unit) => unit.text))})`);
  for (const [index, unit] of units.entries()) {
    assert.ok(marks(unit.text) <= runs[index].bytes.length,
      `the ${entry.name} case: unit ${index} returned ${marks(unit.text)} `
      + `characters from a run of ${runs[index].bytes.length} codes — `
      + 'decoding cannot produce more characters than it consumed codes');
  }
}

// The WinAnsi family, where one byte is one character: every character of the
// extracted copy has to be a byte the document really draws. This is the bound
// that catches a decoder reaching past the end of a string operand.
for (const name of WINANSI_FAMILY) {
  const { units } = attempt(name);
  const runs = contentRuns(decodedStream(contentStream(name, name === 'plain-untagged' ? null : filterOf(name))))
    .map((run) => run.bytes.toString('latin1'));
  for (const unit of units) {
    for (const ch of unit.text) {
      assert.ok(runs.some((run) => run.includes(ch)),
        `the ${name} case: "${unit.text}" carries a character the document never draws (${ch})`);
    }
  }
  assert.deepEqual(units.map((unit) => unit.text), FILTER_COPY,
    `the ${name} case is one byte per character and must come back exactly`);
}

function filterOf(name) {
  return {
    flate: 'FlateDecode', lzw: 'LZWDecode', ascii85: 'ASCII85Decode',
    asciihex: 'ASCIIHexDecode', runlength: 'RunLengthDecode',
  }[name];
}

// --- B9. the documentation may not claim more than the contract delivers ----

{
  const docs = ['README.md', 'USER-GUIDE.md', 'SECURITY.md', 'docs/MIGRATION.md',
    'docs/CLAIM-EVIDENCE-AUDIT.md'];
  // Claims the contract forbids. Kept as literal phrases so a failure names
  // the sentence rather than a number.
  const forbidden = [
    /recognis\w* (?:the )?quotation/i,
    /quotation context (?:is|remains) recoverable/i,
    /recognis\w* quoted material in a pdf/i,
    /pdfs? (?:are|is) (?:read|scanned) (?:by|with) ocr/i,
    /ocr(?: reads| is used| extracts) (?:the )?pdf/i,
    /extracts? (?:all|every) text/i,
    /context is detected in pdfs/i,
  ];
  let mentioned = 0;
  for (const name of docs) {
    const file = path.join(ROOT, name);
    if (!fs.existsSync(file)) continue;
    const text = fs.readFileSync(file, 'utf8');
    if (!/\bpdf\b/i.test(text)) continue;
    mentioned++;
    for (const pattern of forbidden) {
      assert.ok(!pattern.test(text),
        `${name} must not claim more than the contract delivers: ${pattern} matched\n`
        + `  ${text.split('\n').find((line) => pattern.test(line))}`);
    }
  }
  assert.ok(mentioned > 0, 'at least one document must mention PDF support');
  // And the context limitation must be stated, not left implied. The wording is
  // P3's; this only requires that a document which mentions PDF says so near
  // where it mentions PDF.
  const readers = docs
    .filter((name) => fs.existsSync(path.join(ROOT, name)))
    .map((name) => fs.readFileSync(path.join(ROOT, name), 'utf8'))
    .filter((text) => /\bpdf\b/i.test(text));
  assert.ok(readers.some((text) => /pdf[\s\S]{0,600}?context is always/i.test(text)
    || /context is always[\s\S]{0,600}?pdf/i.test(text)),
  'a document that mentions PDF must state that the context is always authored');
}

fs.rmSync(tmp, { recursive: true, force: true });
delete globalThis.__twinIds;
delete globalThis.__twinCounts;
delete globalThis.__twinFindings;

console.log('ok — PDF extraction: '
  + `${CASES.length} cases proven, ${refused.length} refusals held, `
  + 'line and column reconstruction exact, page attribution correct, context always authored, '
  + 'the rule layer unable to tell a PDF unit from any other, extraction deterministic');
