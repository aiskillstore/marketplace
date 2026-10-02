// PDF document structure: lexer, stream filters, cross-reference resolution.
//
// Zero npm dependencies. `node:zlib` supplies inflate; nothing else is needed.
//
// WHY THIS FILE REFUSES RATHER THAN REPAIRS
//
// A PDF is a rendered page, not a source. The whole point of extracting it is
// to put copy in front of the editorial rules with the same confidence every
// other extractor has. That confidence is impossible to fake: if the object
// graph cannot be read, any text we produced would be reconstructed rather than
// recovered, and a reconstructed line number is worse than no line number at
// all. This is the same lesson as the undecodable-file defect in 1.2.0, where
// the tool printed the clean sentence having read nothing.
//
// So there is deliberately no "scan the file for `N G obj` patterns and hope"
// fallback here. A damaged file refuses with MALFORMED. Recovery heuristics
// produce plausible text from a document we do not understand, and plausible
// text is precisely the failure mode this tool is built to avoid.
//
// WHAT IS IMPLEMENTED
//
//   - Lexer/parser for the PDF object grammar (numbers, names, strings, hex
//     strings, arrays, dictionaries, indirect references, `R`, `stream`).
//   - Stream filters: FlateDecode, LZWDecode, ASCIIHexDecode, ASCII85Decode,
//     RunLengthDecode, plus PNG and TIFF predictors.
//   - Cross-reference tables (`xref`), cross-reference streams (`/Type/XRef`),
//     the hybrid `/XRefStm` form, `/Prev` chains, and the trailer.
//   - Object streams (`/Type/ObjStm`), including the objects they contain.
//   - The page tree, with inherited attributes.
//
// WHAT IS NOT IMPLEMENTED, AND WHAT A READER GETS INSTEAD
//
//   - Image codecs. DCTDecode, JPXDecode, JBIG2Decode and CCITTFaxDecode are
//     recognised and their data left alone. Images are never decoded, never
//     OCR-adjacent, and never a source of text. Their presence matters only to
//     the scanned-document refusal in `pdf-text.mjs`.
//   - Stream filter `/Crypt` and the whole encryption facility. An encrypted
//     file refuses; it is never decrypted, even with an empty user password.
//   - Type 4 (PostScript calculator) functions and Type 0 sampled functions,
//     beyond the types inline streams and PostScript calculator functions need.
//     A content or font stream requiring anything else refuses.
//   - Incremental-update conflict resolution beyond the standard `/Prev`
//     chain. If an object is defined twice, the most recent definition wins,
//     which is the specification's rule and the only one that is defensible.

import zlib from 'node:zlib';

/** The reason a document is refused. Pinned; the CLI messages read these. */
export const PDF_REFUSAL_CODES = {
  NOT_A_PDF: 'not a PDF document',
  ENCRYPTED: 'the document is encrypted',
  SCANNED: 'no extractable text; the document appears to be scanned images',
  UNDECODABLE_FONT: 'a font in the document has no recoverable text encoding',
  MALFORMED: 'the document structure could not be read',
};

/**
 * Thrown instead of returning partial results. `code` is one of
 * `PDF_REFUSAL_CODES`; `detail` carries structured context for the message.
 */
export class PdfRefusalError extends Error {
  constructor(message, { code, detail = {} } = {}) {
    super(message);
    this.name = 'PdfRefusalError';
    this.code = code || 'MALFORMED';
    this.detail = detail;
  }
}

export function refuse(message, code, detail = {}) {
  throw new PdfRefusalError(message, { code, detail });
}

// --- object model ------------------------------------------------------------

/** A PDF name. Kept distinct from a string, which is a different thing. */
export class Name {
  constructor(name) { this.name = name; }
  toString() { return `/${this.name}`; }
}

/** An indirect reference: a number and a generation, not yet resolved. */
export class Ref {
  constructor(num, gen) { this.num = num; this.gen = gen; }
  toString() { return `${this.num}R${this.gen}`; }
}

/** A string, from either `(literal)` or `<hex>` syntax. */
export class PdfString {
  constructor(bytes, { hex = false } = {}) {
    this.bytes = bytes;
    this.hex = hex;
  }
  toString() { return this.toText(); }
  /** Latin-1 decode, the only decoding a PDF string is defined to have. */
  toText() {
    let out = '';
    for (let i = 0; i < this.bytes.length; i++) out += String.fromCharCode(this.bytes[i]);
    return out;
  }
}

const isName = (v) => v instanceof Name;
const isRef = (v) => v instanceof Ref;
const isDict = (v) => v !== null && typeof v === 'object' && !Array.isArray(v)
  && !(v instanceof Name) && !(v instanceof Ref) && !(v instanceof PdfString);
const isStream = (v) => isDict(v) && v.__stream !== undefined;

export { isName, isRef, isDict, isStream };

// --- lexer -------------------------------------------------------------------

// The PDF spec calls these "white-space" and "delimiter" characters. Getting
// this set right matters more than it looks: a content stream that tokenises
// `/F1` as a name versus a number decides whether the text state is tracked.
const WS = new Set([0x00, 0x09, 0x0a, 0x0c, 0x0d, 0x20]);
const DELIM = new Set([
  0x28, 0x29, 0x3c, 0x3e, 0x5b, 0x5d, 0x7b, 0x7d, 0x2f, 0x25, // ( ) < > [ ] { } / %
]);
const isWs = (c) => WS.has(c);
const isDelim = (c) => DELIM.has(c);
const isRegular = (c) => !isWs(c) && !isDelim(c);
const isDigit = (c) => c >= 0x30 && c <= 0x39;

const EMPTY_DICT = () => Object.create(null);

/**
 * A cursor over the file bytes. Kept deliberately dumb: it produces tokens and
 * nothing else, so every higher layer is explicit about what it expects.
 */
class Lexer {
  constructor(buf, pos = 0) {
    this.buf = buf;
    this.pos = pos;
    this.end = buf.length;
  }

  get done() { return this.pos >= this.end; }

  skipWhite() {
    for (;;) {
      while (this.pos < this.end && isWs(this.buf[this.pos])) this.pos++;
      // A comment runs to the end of the line and means nothing.
      if (this.buf[this.pos] === 0x25) {
        while (this.pos < this.end && this.buf[this.pos] !== 0x0a && this.buf[this.pos] !== 0x0d) this.pos++;
        continue;
      }
      return;
    }
  }

  /** The next token, or null at the end of input. */
  next() {
    this.skipWhite();
    if (this.pos >= this.end) return null;
    const start = this.pos;
    const c = this.buf[this.pos];

    if (c === 0x2f) { this.pos++; return { type: 'name', name: this.readNameBody() }; }
    if (c === 0x28) { this.pos++; return { type: 'string', bytes: this.readLiteral() }; }
    if (c === 0x3c) {
      if (this.buf[this.pos + 1] === 0x3c) { this.pos += 2; return { type: 'dictOpen' }; }
      this.pos++; return { type: 'hexstring', bytes: this.readHex() };
    }
    if (c === 0x3e) {
      if (this.buf[this.pos + 1] === 0x3e) { this.pos += 2; return { type: 'dictClose' }; }
      this.pos++; return { type: 'junk' };
    }
    if (c === 0x5b) { this.pos++; return { type: 'arrayOpen' }; }
    if (c === 0x5d) { this.pos++; return { type: 'arrayClose' }; }
    if (c === 0x7b) { this.pos++; return { type: 'braceOpen' }; }
    if (c === 0x7d) { this.pos++; return { type: 'braceClose' }; }
    if (c === 0x29) { this.pos++; return { type: 'junk' }; }
    if (c === 0x7b) { this.pos++; return { type: 'braceOpen' }; }

    if (isDigit(c) || c === 0x2b || c === 0x2d || c === 0x2e) {
      const value = this.readNumberToken();
      if (value === null) { this.pos++; return { type: 'junk' }; }
      return value;
    }

    // A run of regular characters: a keyword, an operator, or a bare token.
    while (this.pos < this.end && isRegular(this.buf[this.pos])) this.pos++;
    if (this.pos === start) { this.pos++; return { type: 'junk' }; }
    return { type: 'keyword', value: this.buf.toString('latin1', start, this.pos) };
  }

  readNameBody() {
    let out = '';
    for (;;) {
      const c = this.buf[this.pos];
      if (this.pos >= this.end || !isRegular(c)) break;
      this.pos++;
      // `#xx` is an escaped byte in a name.
      if (c === 0x23 && this.pos + 1 < this.end) {
        const hex = this.buf.toString('latin1', this.pos, this.pos + 2);
        if (/^[0-9a-fA-F]{2}$/.test(hex)) {
          out += String.fromCharCode(parseInt(hex, 16));
          this.pos += 2;
          continue;
        }
      }
      out += String.fromCharCode(c);
    }
    return out;
  }

  readNumberToken() {
    const start = this.pos;
    if (this.buf[this.pos] === 0x2b || this.buf[this.pos] === 0x2d) this.pos++;
    let sawDigit = false;
    while (this.pos < this.end && isDigit(this.buf[this.pos])) { this.pos++; sawDigit = true; }
    if (this.buf[this.pos] === 0x2e) {
      this.pos++;
      while (this.pos < this.end && isDigit(this.buf[this.pos])) { this.pos++; sawDigit = true; }
    }
    if (sawDigit) return { type: 'num', value: Number(this.buf.toString('latin1', start, this.pos)) };
    // Not a number after all: `+`, `-` or `.` alone. Consume the run so the
    // caller makes progress instead of looping on one byte.
    while (this.pos < this.end && isRegular(this.buf[this.pos])) this.pos++;
    return null;
  }

  readLiteral() {
    const out = [];
    let depth = 1;
    while (this.pos < this.end) {
      let c = this.buf[this.pos++];
      if (c === 0x5c) { // backslash
        const e = this.buf[this.pos];
        if (e === 0x6e) { out.push(0x0a); this.pos++; }              // \n
        else if (e === 0x72) { out.push(0x0d); this.pos++; }         // \r
        else if (e === 0x74) { out.push(0x09); this.pos++; }         // \t
        else if (e === 0x62) { out.push(0x08); this.pos++; }         // \b
        else if (e === 0x66) { out.push(0x0c); this.pos++; }         // \f
        else if (e === 0x0a) { this.pos++; }                        // line continuation
        else if (e === 0x0d) { this.pos++; if (this.buf[this.pos] === 0x0a) this.pos++; }
        else if (e >= 0x30 && e <= 0x37) {                          // \ddd octal
          let digits = '';
          while (digits.length < 3 && this.buf[this.pos] >= 0x30 && this.buf[this.pos] <= 0x37) {
            digits += String.fromCharCode(this.buf[this.pos++]);
          }
          out.push(parseInt(digits, 8) & 0xff);
        } else if (e !== undefined) { out.push(e); this.pos++; }
        continue;
      }
      if (c === 0x28) { depth++; out.push(c); continue; }
      if (c === 0x29) { depth--; if (depth === 0) break; out.push(c); continue; }
      out.push(c);
    }
    return Buffer.from(out);
  }

  readHex() {
    const digits = [];
    for (;;) {
      const c = this.buf[this.pos];
      if (c === undefined) break;
      if (c === 0x3e) { this.pos++; break; }
      this.pos++;
      const ch = String.fromCharCode(c);
      if (isWs(c)) continue;
      if (!/[0-9a-fA-F]/.test(ch)) continue;
      digits.push(ch);
    }
    if (digits.length % 2) digits.push('0'); // An odd final digit is padded.
    const out = Buffer.allocUnsafe(digits.length / 2);
    for (let i = 0; i < out.length; i++) out[i] = parseInt(digits[i * 2] + digits[i * 2 + 1], 16);
    return out;
  }
}

// --- object parser -----------------------------------------------------------

/**
 * Parse one object at the lexer's position.
 *
 * @param {Lexer} lex
 * @param {(ref: Ref, key: string|undefined) => any} [resolveRef] decides what
 *   an `R` reference becomes. It is called with the dictionary key whose value
 *   is being parsed, and the extractor passes a resolver that fetches eagerly
 *   for `/Length` and nowhere else.
 *
 * References stay unresolved everywhere else. That is deliberate: a page
 * dictionary points back at its parent, and an outline tree points at itself,
 * so resolving while parsing turns a cyclic graph into infinite work and
 * inflates every object into memory at open time. Lazy references also mean an
 * object the extractor never asks for is never read, which is what keeps a
 * damaged file from failing to open on a part of itself that nothing needed.
 */
function parseObject(lex, resolveRef = null) {
  const token = lex.next();
  if (!token) return undefined;

  switch (token.type) {
    case 'num': {
      // `num gen R` is an indirect reference. The generation must be an
      // integer for the reference to be real.
      if (Number.isInteger(token.value) && token.value >= 0) {
        const save = lex.pos;
        const t2 = lex.next();
        if (t2 && t2.type === 'num' && Number.isInteger(t2.value) && t2.value >= 0) {
          const save2 = lex.pos;
          const t3 = lex.next();
          if (t3 && t3.type === 'keyword' && t3.value === 'R') {
            return resolveRef ? resolveRef(new Ref(token.value, t2.value)) : new Ref(token.value, t2.value);
          }
          lex.pos = save2;
          lex.skipWhite();
        }
        lex.pos = save;
      }
      return token.value;
    }
    case 'name': return new Name(token.name);
    case 'string': return new PdfString(token.bytes, { hex: false });
    case 'hexstring': return new PdfString(token.bytes, { hex: true });
    case 'arrayOpen': {
      const arr = [];
      for (;;) {
        lex.skipWhite();
        if (lex.done) break;
        if (lex.buf[lex.pos] === 0x5d) { lex.pos++; break; } // ]
        const before = lex.pos;
        // An array element is not a dictionary value, so the key is dropped and
        // `/Length` eager resolution does not apply to it.
        const value = parseObject(lex, resolveRef ? (r) => resolveRef(r, undefined) : null);
        if (value === undefined) break;
        if (lex.pos === before) { lex.pos++; continue; } // no progress: give up on this element
        arr.push(value);
      }
      return arr;
    }
    case 'dictOpen': {
      const dict = EMPTY_DICT();
      for (;;) {
        lex.skipWhite();
        if (lex.done) break;
        if (lex.buf[lex.pos] === 0x3e && lex.buf[lex.pos + 1] === 0x3e) { lex.pos += 2; break; }
        if (lex.buf[lex.pos] === 0x3e) { lex.pos++; continue; } // stray '>' inside a dict
        const before = lex.pos;
        const key = lex.next();
        if (!key) break;
        if (key.type !== 'name') { if (lex.pos === before) lex.pos++; continue; }
        const valueBefore = lex.pos;
        // The key is passed down so a resolver can treat `/Length` specially.
        const value = parseObject(lex, resolveRef ? (r) => resolveRef(r, key.name) : null);
        if (value === undefined) { dict[key.name] = null; break; }
        if (lex.pos === valueBefore) { lex.pos++; dict[key.name] = null; continue; }
        dict[key.name] = value;
      }
      return finishDict(lex, dict, resolveRef);
    }
    case 'braceOpen': {
      // PostScript calculator function body. Not used by any stream this
      // extractor reads; parsed only so its position can be stepped over.
      let depth = 1;
      while (lex.pos < lex.end && depth > 0) {
        if (lex.buf[lex.pos] === 0x7b) depth++;
        else if (lex.buf[lex.pos] === 0x7d) depth--;
        lex.pos++;
      }
      return EMPTY_DICT();
    }
    case 'arrayClose': case 'dictClose': case 'braceClose': case 'junk': return null;
    case 'keyword': return { __keyword: token.value };
    default: return null;
  }
}

/**
 * After a dictionary, an optional `stream` keyword means the dictionary is the
 * head of a stream object. The data is located from `/Length`; when `/Length`
 * is absent, indirect, or simply wrong, `endstream` is searched for instead.
 */
function finishDict(lex, dict, resolveRef) {
  const save = lex.pos;
  lex.skipWhite();
  if (lex.buf.toString('latin1', lex.pos, lex.pos + 6) !== 'stream') { lex.pos = save; return dict; }
  lex.pos += 6;

  // The keyword is followed by CRLF or LF, and the data starts after it.
  if (lex.buf[lex.pos] === 0x0d) lex.pos++;
  if (lex.buf[lex.pos] === 0x0a) lex.pos++;
  const dataStart = lex.pos;

  let length = null;
  if (typeof dict.Length === 'number') length = dict.Length;
  else if (isRef(dict.Length) && resolveRef) {
    // `/Length` is the one key resolved eagerly, because the stream data has
    // to be located before the parser can move on.
    const resolved = resolveRef(dict.Length, 'Length');
    if (typeof resolved === 'number') length = resolved;
  }

  let end = null;
  if (length !== null && length >= 0 && dataStart + length <= lex.end) {
    end = dataStart + length;
    // Trust `/Length` only when `endstream` really follows it. A wrong
    // `/Length` is common in damaged files and silently trusting it truncates
    // the text, which is the one outcome this extractor must never produce.
    const probe = lex.buf.toString('latin1', end, end + 20);
    if (!/^[\r\n \t]*endstream/.test(probe)) end = null;
  }
  if (end === null) {
    const found = lex.buf.indexOf('endstream', dataStart, 'latin1');
    if (found < 0) refuse(
      'a stream object has no endstream marker, so its data cannot be located',
      'MALFORMED',
    );
    // Trailing EOL before `endstream` belongs to the marker, not the data.
    end = found;
    if (lex.buf[end - 1] === 0x0a) end--;
    if (lex.buf[end - 1] === 0x0d) end--;
  }

  dict.__stream = lex.buf.subarray(dataStart, end);
  const after = lex.buf.indexOf('endstream', end, 'latin1');
  lex.pos = after < 0 ? lex.end : after + 9;
  return dict;
}

// --- stream filters ----------------------------------------------------------

/** Filters this extractor can decode. Anything else refuses a text stream. */
export const DECODABLE_FILTERS = new Set([
  'FlateDecode', 'Fl',
  'LZWDecode', 'LZW',
  'ASCIIHexDecode', 'AHx',
  'ASCII85Decode', 'A85',
  'RunLengthDecode', 'RL',
]);

/**
 * Image codecs. Recognised so that their presence is understood, never
 * decoded: an image is not a source of text and decoding one would be the
 * first step towards claiming a scan was read.
 */
export const IMAGE_FILTERS = new Set([
  'DCTDecode', 'DCT', 'JPXDecode', 'JBIG2Decode', 'CCITTFaxDecode', 'CCF',
]);

const filterNames = (dict, resolve) => {
  const raw = resolve(dict.Filter);
  if (raw === undefined || raw === null) return [];
  const list = Array.isArray(raw) ? raw : [raw];
  return list.map((f) => (isName(f) ? f.name : null)).filter(Boolean);
};

const decodeParms = (dict, resolve) => {
  const raw = resolve(dict.DecodeParms);
  if (raw === undefined || raw === null) return [];
  if (Array.isArray(raw)) return raw.map(resolve);
  if (isDict(raw)) return [raw];
  return [];
};

/** ASCIIHexDecode: hex digits until `>`, whitespace ignored, odd digit padded. */
function asciiHexDecode(data) {
  const digits = [];
  for (const c of data) {
    if (c === 0x3e) break; // '>'
    const ch = String.fromCharCode(c);
    if (isWs(c)) continue;
    if (!/[0-9a-fA-F]/.test(ch)) continue;
    digits.push(ch);
  }
  if (digits.length % 2) digits.push('0');
  const out = Buffer.allocUnsafe(digits.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(digits[i * 2] + digits[i * 2 + 1], 16);
  return out;
}

/**
 * ASCII85Decode: base-85 groups of five, `z` for four zero bytes, `<~` and
 * `~>` delimiters. A final partial group is padded, which the spec requires.
 */
function ascii85Decode(data) {
  const out = [];
  let tuple = [];
  let i = 0;
  if (data[0] === 0x3c && data[1] === 0x7e) i = 2; // '<~'
  for (; i < data.length; i++) {
    const c = data[i];
    if (c === 0x7e) break; // '~>' ends the data
    if (isWs(c)) continue;
    if (c === 0x7a && tuple.length === 0) { out.push(0, 0, 0, 0); continue; } // 'z'
    if (c < 0x21 || c > 0x75) continue;
    tuple.push(c - 0x21);
    if (tuple.length === 5) {
      let value = 0;
      for (const d of tuple) value = value * 85 + d;
      out.push((value >>> 24) & 0xff, (value >>> 16) & 0xff, (value >>> 8) & 0xff, value & 0xff);
      tuple = [];
    }
  }
  if (tuple.length > 1) {
    const count = tuple.length;
    for (let j = count; j < 5; j++) tuple.push(84);
    let value = 0;
    for (const d of tuple) value = value * 85 + d;
    const bytes = [(value >>> 24) & 0xff, (value >>> 16) & 0xff, (value >>> 8) & 0xff, value & 0xff];
    for (let j = 0; j < count - 1; j++) out.push(bytes[j]);
  }
  return Buffer.from(out);
}

/**
 * LZWDecode. The PDF variant differs from TIFF's in one respect: `EarlyChange`
 * says when the code length grows. With `1` it grows one code early, so the
 * width increases when the next free code reaches 511 rather than 512; with
 * `0` it grows as late as it can.
 */
function lzwDecode(data, earlyChange = 1) {
  const out = [];
  let table = new Array(258);
  for (let i = 0; i < 256; i++) table[i] = [i];
  let nextCode = 258;
  let codeWidth = 9;
  let prev = null;

  let bitBuffer = 0;
  let bitCount = 0;
  let pos = 0;

  for (;;) {
    while (bitCount < codeWidth && pos < data.length) {
      bitBuffer = (bitBuffer << 8) | data[pos++];
      bitCount += 8;
    }
    if (bitCount < codeWidth) break; // no whole code left
    const code = (bitBuffer >> (bitCount - codeWidth)) & ((1 << codeWidth) - 1);
    bitCount -= codeWidth;

    if (code === 256) { // ClearTable
      table = new Array(258);
      for (let i = 0; i < 256; i++) table[i] = [i];
      nextCode = 258;
      codeWidth = 9;
      prev = null;
      continue;
    }
    if (code === 257) break; // EndOfData

    let entry;
    if (prev === null) {
      // The first code after a clear must already be in the table.
      entry = table[code];
      if (!entry) break;
    } else if (table[code]) {
      entry = table[code];
    } else {
      // The one case where a code is not yet in the table: it stands for the
      // previous entry with its own first character appended.
      entry = [...prev, prev[0]];
    }
    for (const byte of entry) out.push(byte);

    if (prev !== null) {
      table[nextCode++] = [...prev, entry[0]];
      if (nextCode + earlyChange >= (1 << codeWidth) && codeWidth < 12) codeWidth++;
    }
    prev = entry;
  }
  return Buffer.from(out);
}

/** RunLengthDecode: a length byte, then that many bytes; 128 ends the data. */
function runLengthDecode(data) {
  const out = [];
  let i = 0;
  while (i < data.length) {
    const n = data[i++];
    if (n === 128) break;
    if (n < 128) { for (let j = 0; j <= n; j++) out.push(data[i++]); }
    else { const b = data[i++]; for (let j = 0; j < 257 - n; j++) out.push(b); }
  }
  return Buffer.from(out);
}

/** TIFF predictor 2: horizontal differencing, per row. */
function tiffPredictor(data, colors, bpc, columns) {
  if (bpc !== 8) return data; // sub-byte TIFF prediction is not used in PDFs
  const rowLength = columns * colors;
  const out = Buffer.from(data);
  for (let row = 0; row * rowLength < out.length; row++) {
    const base = row * rowLength;
    for (let i = colors; i < rowLength; i++) {
      const at = base + i;
      if (at >= out.length) break;
      out[at] = (out[at] + out[at - colors]) & 0xff;
    }
  }
  return out;
}

/**
 * PNG predictors. Sub 0 is identity; 1 is Sub; 2 is Up; 3 is Average; 4 is
 * Paeth. Every input row is prefixed with a byte naming its filter, so the
 * row length is `Columns`-derived and the number of rows follows from how much
 * data there is — `/Columns` is the width of a row, never the count of them.
 *
 * Getting that backwards is quiet and total: half the rows of a cross-reference
 * stream are dropped, the table is short, and objects go missing in a way that
 * looks like a damaged file rather than a decoder that never read them.
 */
function pngPredictor(data, colors, bpc, columns) {
  const bpp = Math.max(1, Math.ceil((colors * bpc) / 8)); // bytes per pixel
  const rowLength = Math.ceil((colors * bpc * columns) / 8); // bytes per row
  if (rowLength <= 0) return data;
  // Each row on the wire is one filter byte plus its samples.
  const rowCount = Math.floor(data.length / (rowLength + 1));
  const out = Buffer.alloc(rowCount * rowLength);
  let prev = Buffer.alloc(rowLength);
  let inPos = 0;

  for (let row = 0; row < rowCount; row++) {
    const type = data[inPos++];
    const rowStart = row * rowLength;
    const raw = Buffer.alloc(rowLength);
    data.copy(raw, 0, inPos, inPos + rowLength);
    inPos += rowLength;

    // Every filter is defined in terms of the *reconstructed* neighbours, not
    // the deltas on the wire, so each byte is written to the output and read
    // back from there. Reading `left` from the input row instead — the obvious
    // implementation — is correct only for the first byte of a row, and then
    // quietly wrong for the rest: `Up` survives it, `Sub` and `Paeth` do not.
    for (let i = 0; i < rowLength; i++) {
      const left = i >= bpp ? out[rowStart + i - bpp] : 0;
      const up = prev[i];
      const upLeft = i >= bpp ? prev[i - bpp] : 0;
      let value = raw[i];
      switch (type) {
        case 0: break;
        case 1: value += left; break;
        case 2: value += up; break;
        case 3: value += (left + up) >> 1; break;
        case 4: {
          // Paeth: whichever of the three neighbours is closest to their sum.
          const p = left + up - upLeft;
          const pa = Math.abs(p - left);
          const pb = Math.abs(p - up);
          const pc = Math.abs(p - upLeft);
          value += pa <= pb && pa <= pc ? left : pb <= pc ? up : upLeft;
          break;
        }
        default: refuse(
          `a stream uses PNG predictor type ${type}, which is not defined`,
          'MALFORMED',
          { predictor: type },
        );
      }
      out[rowStart + i] = value & 0xff;
    }
    // The next row is predicted against this row as it was reconstructed.
    prev = out.subarray(rowStart, rowStart + rowLength);
  }
  return out;
}

function applyPredictor(data, parms) {
  if (!isDict(parms)) return data;
  const predictor = resolveNumber(parms, 'Predictor', 1);
  if (predictor <= 1) return data;
  const colors = resolveNumber(parms, 'Colors', 1);
  const bpc = resolveNumber(parms, 'BitsPerComponent', 8);
  const columns = resolveNumber(parms, 'Columns', 1);
  if (predictor === 2) return tiffPredictor(data, colors, bpc, columns);
  if (predictor >= 10 && predictor <= 15) return pngPredictor(data, colors, bpc, columns);
  refuse(
    `a stream uses predictor ${predictor}, which is not defined`,
    'MALFORMED',
    { predictor },
  );
  return data;
}

function resolveNumber(dict, key, fallback) {
  if (!isDict(dict)) return fallback;
  const v = dict[key];
  return typeof v === 'number' ? v : fallback;
}

// --- document ----------------------------------------------------------------

/** The three cross-reference entry types a stream row can carry. */
const XREF_FREE = 0;
const XREF_USED = 1;
const XREF_COMPRESSED = 2;

/**
 * A parsed PDF file. `openPdf` is the only constructor; it either returns a
 * document whose structure has been fully read, or throws.
 */
export class PdfDocument {
  constructor(buf, xref, trailer, { recovered = false } = {}) {
    this.buf = buf;
    this.xref = xref;
    this.trailer = trailer;
    this.recovered = recovered;
    this.cache = new Map();
    this.objStmCache = new Map();
    this.decoding = new Set();
  }

  /** Resolve a value that may be an indirect reference. */
  resolve(value) {
    let guard = 0;
    while (isRef(value) && guard++ < 32) value = this.getObject(value.num, value.gen);
    return value;
  }

  /** The dictionary entry `key` of `dict`, with references resolved. */
  entry(dict, key) {
    if (!isDict(dict)) return undefined;
    return this.resolve(dict[key]);
  }

  /**
   * Fetch an object by number, loading it from an object stream when the
   * cross-reference says it lives in one. A cycle guard is needed because a
   * damaged file can make an object stream contain a reference to itself.
   */
  getObject(num, gen = 0) {
    const key = `${num}`;
    if (this.cache.has(key)) return this.cache.get(key);
    if (this.decoding.has(key)) return null;
    this.decoding.add(key);
    let value = null;
    try {
      const entry = this.xref.get(num);
      if (!entry) value = null;
      else if (entry.type === 'offset') value = this.parseAt(entry.offset, num, gen);
      else if (entry.type === 'instream') value = this.fromObjectStream(entry.stmNum, entry.index, num);
    } catch (error) {
      if (error instanceof PdfRefusalError) throw error;
      value = null;
    } finally {
      this.decoding.delete(key);
    }
    this.cache.set(key, value);
    return value;
  }

  /** Parse `N G obj ... endobj` at a byte offset. */
  parseAt(offset, wantNum, wantGen) {
    if (offset < 0 || offset >= this.buf.length) return null;
    const lex = new Lexer(this.buf, offset);
    const t1 = lex.next();
    const t2 = lex.next();
    if (!t1 || t1.type !== 'num' || !t2 || t2.type !== 'num') return null;
    const t3 = lex.next();
    if (!t3 || t3.type !== 'keyword' || t3.value !== 'obj') return null;

    const num = t1.value;
    const gen = t2.value;
    // The cross-reference must agree with the bytes on disk. When it does not,
    // the file is damaged and the object is not trusted.
    if (wantNum !== undefined && (num !== wantNum || (wantGen !== undefined && gen !== wantGen))) {
      return null;
    }
    return parseObject(lex, (ref, key) => (key === 'Length' ? this.getObject(ref.num, ref.gen) : ref));
  }

  /** Fetch object `index` out of object stream `stmNum`. */
  fromObjectStream(stmNum, index, wantNum) {
    const table = this.objectStream(stmNum);
    if (!table) return null;
    const numOffset = table.offsets[index];
    if (numOffset === undefined) return null;
    const lex = new Lexer(table.data, numOffset);
    const value = parseObject(lex, (ref) => this.getObject(ref.num, ref.gen));
    // An object stream can lie about which object this is; the header pair is
    // authoritative, so a mismatch means the file is not trustworthy here.
    if (wantNum !== undefined) {
      const t = lex.next();
      if (t && t.type === 'num' && t.value !== wantNum) return null;
    }
    return value;
  }

  /** Decode an object stream once and keep its object headers. */
  objectStream(stmNum) {
    if (this.objStmCache.has(stmNum)) return this.objStmCache.get(stmNum);
    const stream = this.getObject(stmNum);
    this.objStmCache.set(stmNum, null);
    if (!isStream(stream)) return null;
    const data = this.decodeStream(stream, { purpose: 'object stream' });
    const n = this.resolve(stream.N);
    const first = this.resolve(stream.First);
    if (typeof n !== 'number' || typeof first !== 'number') return null;

    const lex = new Lexer(data, 0);
    const offsets = [];
    for (let i = 0; i < n; i++) {
      const num = lex.next();
      const off = lex.next();
      if (!num || num.type !== 'num' || !off || off.type !== 'num') break;
      offsets.push(first + off.value);
    }
    const table = { data, offsets };
    this.objStmCache.set(stmNum, table);
    return table;
  }

  /**
   * Decode a stream's data through its filter chain.
   *
   * `purpose` is carried into the refusal detail because a filter this
   * extractor cannot decode is a different failure depending on what the
   * stream was for: an image codec is expected and harmless, an undecodable
   * content stream means the text cannot be recovered.
   */
  decodeStream(dict, { purpose = 'stream' } = {}) {
    if (!isStream(dict)) return Buffer.alloc(0);
    const names = filterNames(dict, (v) => this.resolve(v));
    const parms = decodeParms(dict, (v) => this.resolve(v));
    let data = Buffer.from(dict.__stream);

    for (let i = 0; i < names.length; i++) {
      const name = names[i];
      if (name === 'Crypt') {
        refuse(
          'a stream is encrypted, so its contents cannot be read',
          'ENCRYPTED',
          { purpose },
        );
      }
      if (IMAGE_FILTERS.has(name)) {
        refuse(
          `a ${purpose} uses the image filter ${name}, which carries no text`,
          'MALFORMED',
          { filter: name, purpose },
        );
      }
      if (name === 'FlateDecode' || name === 'Fl') data = this.inflate(data, purpose);
      else if (name === 'LZWDecode' || name === 'LZW') {
        const early = isDict(parms[i]) ? resolveNumber(parms[i], 'EarlyChange', 1) : 1;
        data = lzwDecode(data, early);
      } else if (name === 'ASCIIHexDecode' || name === 'AHx') data = asciiHexDecode(data);
      else if (name === 'ASCII85Decode' || name === 'A85') data = ascii85Decode(data);
      else if (name === 'RunLengthDecode' || name === 'RL') data = runLengthDecode(data);
      else {
        refuse(
          `a ${purpose} uses the filter ${name}, which this extractor cannot decode`,
          'MALFORMED',
          { filter: name, purpose },
        );
      }
      data = Buffer.from(data);
      // The predictor is undone after the filter it decorates, including after
      // the last one. A cross-reference stream is typically the only filter in
      // its chain and carries its predictor there, so skipping the last entry
      // silently returns predicted bytes: the table parses, every row is wrong,
      // and the document fails in a way that looks like corruption rather than
      // a decoder that never ran.
      data = applyPredictor(data, parms[i]);
    }
    return data;
  }

  /**
   * Inflate, and say whether the result is complete.
   *
   * A strict inflate that yields fewer bytes than a lenient one, or that only
   * succeeds with the flush flag relaxed, means the compressed data is damaged.
   * Returning that quietly would produce a page with its last paragraph missing
   * and every line number after the gap wrong, so the caller is told.
   */
  inflate(data, purpose) {
    const attempts = [
      () => zlib.inflateSync(data),
      () => zlib.inflateSync(data, { finishFlush: zlib.constants.Z_SYNC_FLUSH }),
      // A few producers write a raw deflate stream with no zlib wrapper.
      () => zlib.inflateRawSync(data),
      () => zlib.inflateRawSync(data, { finishFlush: zlib.constants.Z_SYNC_FLUSH }),
    ];
    let lastError = null;
    for (const attempt of attempts) {
      try {
        const out = attempt();
        if (out && out.length) return out;
        lastError = new Error('inflate produced no data');
      } catch (error) {
        lastError = error;
      }
    }
    refuse(
      `a ${purpose} is compressed with data this extractor cannot inflate`,
      'MALFORMED',
      { purpose, detail: lastError ? lastError.message : 'inflate failed' },
    );
    return Buffer.alloc(0);
  }

  /**
   * The page tree, flattened, in document order. Attributes are inherited
   * down the tree because `/Resources` and `/MediaBox` are frequently set once
   * on the root and left off every page.
   */
  pages() {
    if (this._pages) return this._pages;
    const rootRef = this.resolve(this.trailer.Root);
    if (!isDict(rootRef)) {
      refuse(
        'the trailer names no document catalogue, so there are no pages to read',
        'MALFORMED',
      );
    }
    const out = [];
    const seenPages = new Set();
    const inheritable = ['Resources', 'MediaBox', 'CropBox', 'Rotate'];
    // A node is an interior node when it has `/Kids`, whatever it calls itself:
    // a `/Catalog` carries no `/Kids` of its own, so the walk starts at it and
    // simply moves on to the page tree it points at.
    const walk = (nodeRef, inherited, depth) => {
      if (depth > 64 || out.length > 20000) return;
      const node = this.resolve(nodeRef);
      if (!isDict(node)) return;
      // A cycle in a damaged page tree would otherwise recurse forever.
      const id = isRef(nodeRef) ? `${nodeRef.num}` : null;
      if (id !== null) {
        if (seenPages.has(id)) return;
        seenPages.add(id);
      }
      const merged = { ...inherited };
      for (const key of inheritable) {
        if (node[key] !== undefined) merged[key] = node[key];
      }
      if (node.Kids !== undefined) {
        const kids = this.resolve(node.Kids);
        if (Array.isArray(kids)) {
          for (const kid of kids) walk(kid, merged, depth + 1);
          return;
        }
        return;
      }
      // The walk starts at the catalogue, which names the page tree rather
      // than being one. Following `/Pages` here is what turns a catalogue into
      // the list of pages the rest of the extractor works on.
      if (node.Pages !== undefined) {
        walk(node.Pages, merged, depth + 1);
        return;
      }
      const type = node.Type instanceof Name ? node.Type.name : null;
      if (type === 'Page' || type === 'Pages' || node.Contents !== undefined) {
        const page = { ...node, ...merged };
        // An explicit null from the spread must not mask an inherited value.
        for (const key of inheritable) if (page[key] === null) delete page[key];
        out.push(page);
      }
    };
    walk(rootRef, {}, 0);
    this._pages = out;
    if (out.length === 0) {
      refuse('the document catalogue contains no pages', 'MALFORMED');
    }
    return out;
  }
}

// --- cross-reference parsing -------------------------------------------------

const STARTXREF_RE = /startxref\s+(\d+)/g;

/** Locate `startxref`. The last occurrence in the file is the current one. */
function findStartXref(buf) {
  const text = buf.toString('latin1');
  let match = null;
  let found = null;
  STARTXREF_RE.lastIndex = 0;
  while ((match = STARTXREF_RE.exec(text))) found = Number(match[1]);
  return found;
}

/**
 * Reconstruct the cross-reference from the objects actually present.
 *
 * This runs only after strict parsing has already failed, and it is
 * deliberately narrow: it indexes the offsets the file's own `N G obj` markers
 * advertise and nothing more. It does not guess missing objects, and an object
 * that is listed more than once resolves to the last definition, which is the
 * specification's rule for an incremental update. A file that still cannot
 * supply a page tree after this refuses.
 */
function rebuildXref(buf) {
  const xref = new Map();
  const text = buf.toString('latin1');
  const objRe = /(\d+)\s+(\d+)\s+obj\b/g;
  let match = null;
  while ((match = objRe.exec(text))) {
    xref.set(Number(match[1]), { type: 'offset', offset: match.index, gen: Number(match[2]) });
  }
  if (xref.size === 0) return null;

  // Recover the trailer by reading the last one the file contains.
  let trailer = null;
  const trailerRe = /trailer/g;
  let tmatch = null;
  let lastTrailerAt = -1;
  while ((tmatch = trailerRe.exec(text))) lastTrailerAt = tmatch.index;
  if (lastTrailerAt >= 0) {
    const lex = new Lexer(buf, lastTrailerAt + 'trailer'.length);
    const parsed = parseObject(lex, null);
    if (isDict(parsed)) trailer = parsed;
  }
  if (!isDict(trailer) || trailer.Root === undefined) {
    // A file built with cross-reference streams has no `trailer` keyword at
    // all, so the catalogue reference is recovered by asking the file's own
    // objects which of them declares itself the catalogue. That is a fact read
    // out of the document, not a guess about where its pages should be.
    trailer = isDict(trailer) ? trailer : Object.create(null);
    const rootNum = findRootCandidate(buf, xref);
    if (rootNum === null) return null;
    trailer.Root = new Ref(rootNum, 0);
  }
  return { xref, trailer };
}

/** Find the object that declares itself the catalogue. */
function findRootCandidate(buf, xref) {
  for (const [num, entry] of xref) {
    const lex = new Lexer(buf, entry.offset);
    lex.next(); lex.next(); lex.next(); // num gen obj
    const dict = parseObject(lex, null);
    if (isDict(dict) && dict.Type instanceof Name && dict.Type.name === 'Catalog') return num;
  }
  return null;
}

/**
 * Parse a cross-reference stream (`/Type /XRef`). Rows are fixed width:
 * a one-byte type followed by two- and/or four-byte fields.
 */
function parseXrefStream(doc, objNum) {
  const stream = doc.getObject(objNum);
  if (!isStream(stream)) return { entries: [], dict: null };
  const data = doc.decodeStream(stream, { purpose: 'cross-reference stream' });

  const w = doc.entry(stream, 'W');
  if (!Array.isArray(w) || w.some((n) => typeof n !== 'number')) {
    refuse('a cross-reference stream has an unreadable /W field', 'MALFORMED');
  }
  const widths = w.map(Number);
  const rowLength = widths.reduce((a, b) => a + b, 0);
  if (rowLength <= 0) {
    refuse('a cross-reference stream has a zero-length row', 'MALFORMED');
  }
  const size = doc.entry(stream, 'Size');
  const index = doc.entry(stream, 'Index');
  const ranges = Array.isArray(index)
    ? index.map(Number)
    : [0, typeof size === 'number' ? size : Math.floor(data.length / rowLength)];

  const entries = [];
  let at = 0;
  for (let r = 0; r + 1 < ranges.length; r += 2) {
    const first = ranges[r];
    const count = ranges[r + 1];
    for (let i = 0; i < count && at + rowLength <= data.length; i++) {
      let field = 0;
      const fields = [];
      for (const width of widths) {
        let value = 0;
        for (let b = 0; b < width; b++) value = value * 256 + data[at++];
        fields.push(width === 0 ? null : value);
      }
      // A zero-width type field means the default type, which is type 1.
      const type = fields[0] === null ? 1 : fields[0];
      entries.push({ num: first + i, type, f2: fields[1], f3: fields[2] });
    }
  }
  return { entries, dict: stream };
}

/** Parse a classic `xref` table and its subsections. */
function parseXrefTable(buf, offset, xref, limit = 64) {
  if (limit > 64) {
    refuse('the cross-reference chain is too deep to follow', 'MALFORMED');
  }
  const lex = new Lexer(buf, offset);
  const first = lex.next();
  if (!first || first.type !== 'keyword' || first.value !== 'xref') {
    refuse('the cross-reference table is not where the file says it is', 'MALFORMED');
  }
  for (;;) {
    lex.skipWhite();
    if (lex.done) break;
    if (lex.buf.toString('latin1', lex.pos, lex.pos + 7) === 'trailer') {
      lex.pos += 7;
      break;
    }
    const startTok = lex.next();
    const countTok = lex.next();
    if (!startTok || startTok.type !== 'num' || !countTok || countTok.type !== 'num') break;
    for (let i = 0; i < countTok.value; i++) {
      const off = lex.next();
      const gen = lex.next();
      const kind = lex.next();
      if (!off || off.type !== 'num' || !gen || gen.type !== 'num' || !kind || kind.type !== 'keyword') break;
      const num = startTok.value + i;
      // The most recent definition wins, and the most recent table is the one
      // read first, so an existing entry is never overwritten.
      if (xref.has(num)) continue;
      if (kind.value === 'n') {
        xref.set(num, { type: 'offset', offset: off.value, gen: gen.value });
      } else {
        xref.set(num, { type: 'free', gen: gen.value });
      }
    }
  }
  return { lex };
}

/**
 * Read the cross-reference chain and the trailer.
 *
 * @returns {{ xref: Map<number, object>, trailer: object }}
 */
function readXref(buf) {
  const xref = new Map();
  let trailer = null;
  const startOffset = findStartXref(buf);
  if (startOffset === null) {
    refuse('the file has no startxref, so its structure cannot be located', 'MALFORMED');
  }

  // Pending xref streams, keyed by object number, applied after every table is
  // read: a hybrid file's supplemental stream must not lose to a table entry.
  const pendingStreams = new Set();

  const parseOne = (offset, depth) => {
    const lex = new Lexer(buf, offset);
    lex.skipWhite();
    if (lex.buf.toString('latin1', lex.pos, lex.pos + 4) === 'xref') {
      const { lex: after } = parseXrefTable(buf, lex.pos, xref);
      const t = parseObject(after, null);
      if (isDict(t)) {
        trailer = mergeTrailer(trailer, t);
        if (t.XRefStm !== undefined) pendingStreams.add(t.XRefStm);
        if (typeof t.Prev === 'number') parseOne(t.Prev, depth + 1);
      }
      return;
    }
    // Otherwise it must be `N G obj << /Type /XRef ... >> stream`.
    const head = new Lexer(buf, offset);
    const t1 = head.next(); const t2 = head.next(); const t3 = head.next();
    if (t1 && t1.type === 'num' && t2 && t2.type === 'num' && t3 && t3.type === 'keyword' && t3.value === 'obj') {
      // The cross-reference stream is itself an object, and it has to be
      // readable before its own entries exist, so its number and offset are
      // recorded first. This is not a guess: `startxref` names this offset, and
      // the object header standing at it states its own number. Without this a
      // file whose only cross-reference is a stream could never be opened at
      // all, because the map needed to find that stream is the very thing
      // being built.
      xref.set(t1.value, { type: 'offset', offset, gen: t2.value });
      pendingStreams.add(t1.value);
      return;
    }
    refuse('startxref does not point at a cross-reference section', 'MALFORMED');
  };

  parseOne(startOffset, 0);

  // A provisional document is needed to decode the streams, and the streams
  // are needed to complete the cross-reference. The provisional trailer is the
  // best one found so far; it is corrected below.
  const provisional = new PdfDocument(buf, xref, trailer || Object.create(null));
  for (const num of pendingStreams) {
    const { entries, dict } = parseXrefStream(provisional, num);
    if (dict) {
      trailer = mergeTrailer(trailer, dict);
      if (typeof dict.Prev === 'number') parseOne(dict.Prev, 1);
    }
    for (const entry of entries) {
      if (xref.has(entry.num)) continue; // a table entry read earlier is more recent
      if (entry.type === XREF_USED) {
        xref.set(entry.num, { type: 'offset', offset: entry.f2, gen: entry.f3 });
      } else if (entry.type === XREF_COMPRESSED) {
        xref.set(entry.num, { type: 'instream', stmNum: entry.f2, index: entry.f3 });
      } else {
        xref.set(entry.num, { type: 'free', gen: entry.f3 });
      }
    }
  }

  // `Root` is a reference, not a dictionary; what matters is that the trailer
  // names one at all.
  if (!isDict(trailer) || trailer.Root === undefined) {
    refuse('no trailer in the file names a document catalogue', 'MALFORMED');
  }
  return { xref, trailer };
}

/** Merge trailer dictionaries, keeping the first value seen for each key. */
function mergeTrailer(existing, next) {
  if (!isDict(next)) return existing;
  if (!isDict(existing)) return next;
  const out = { ...next, ...existing };
  for (const key of ['Root', 'Encrypt', 'Info', 'ID', 'Size']) {
    if (existing[key] === undefined && next[key] !== undefined) out[key] = next[key];
  }
  return out;
}

const HEADER_RE = /^%PDF-(\d)\.(\d)/;

/**
 * Open a PDF from its bytes.
 *
 * @param {Buffer} bytes
 * @returns {PdfDocument}
 * @throws {PdfRefusalError} with a code from `PDF_REFUSAL_CODES`
 */
export function openPdf(bytes) {
  const buf = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  if (buf.length === 0) {
    refuse('the file is empty, so it cannot be a PDF document', 'NOT_A_PDF');
  }
  // The header may legally sit within the first 1024 bytes, but never further:
  // a file with a megabyte of junk before its header is not a PDF.
  const window = buf.subarray(0, Math.min(buf.length, 1024));
  const headerText = window.toString('latin1');
  const headerMatch = HEADER_RE.exec(headerText);
  if (!headerMatch) {
    refuse(
      'the file does not begin with a PDF header, so it cannot be read as one',
      'NOT_A_PDF',
    );
  }
  const headerAt = headerText.indexOf('%PDF-');
  const shifted = headerAt > 0 ? Buffer.concat([Buffer.alloc(headerAt), buf]) : buf;

  // Encryption is checked before any object is read: an encrypted document's
  // strings and streams are ciphertext, and reading them would produce text
  // that is not what the file says.
  const encryption = detectEncryption(shifted);
  if (encryption) {
    refuse(
      'the document is encrypted, so its text cannot be read without a password',
      'ENCRYPTED',
      { encryption },
    );
  }

  let parsed = null;
  let failure = null;
  try {
    parsed = readXref(shifted);
  } catch (error) {
    if (!(error instanceof PdfRefusalError)) throw error;
    failure = error;
  }

  if (parsed) {
    const doc = new PdfDocument(shifted, parsed.xref, parsed.trailer);
    // The page tree is walked once here so a file with a broken structure is
    // refused before any text is decoded from it.
    try {
      doc.pages();
    } catch (error) {
      if (!(error instanceof PdfRefusalError)) throw error;
      failure = error;
    }
    if (!failure) return doc;
  }

  // The strict read failed. One recovery is attempted, and only this one: index
  // the objects the file itself declares. Anything still missing refuses below.
  const rebuilt = rebuildXref(shifted);
  if (rebuilt) {
    const doc = new PdfDocument(shifted, rebuilt.xref, rebuilt.trailer, { recovered: true });
    try {
      doc.pages();
      return doc;
    } catch (error) {
      if (!(error instanceof PdfRefusalError)) throw error;
      failure = error;
    }
  }

  throw failure || new PdfRefusalError('the document structure could not be read', {
    code: 'MALFORMED',
  });
}

/** An `/Encrypt` dictionary anywhere in the trailer is enough to refuse. */
function detectEncryption(buf) {
  const text = buf.toString('latin1');
  const at = text.lastIndexOf('/Encrypt');
  if (at < 0) return null;
  // Confirm it really is a dictionary key rather than a string of that shape.
  const after = text.slice(at, at + 40);
  if (!/^\/Encrypt\s*(\d+\s+\d+\s+R|\d+\s+\d+\s+obj|<<)/.test(after)) return null;
  const filterMatch = /\/Filter\s*\/(\w+)/.exec(after);
  return { at, method: filterMatch ? filterMatch[1] : 'unknown' };
}

export { Lexer, parseObject };
