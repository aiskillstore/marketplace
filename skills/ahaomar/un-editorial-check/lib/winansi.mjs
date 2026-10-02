// --- transliteration ---------------------------------------------------------
// The single-byte WinAnsi boundary, in one module because three things have to
// agree on it and agreement cannot be tested across a duplication:
//
//   * `toWinAnsi` writes it — it decides which byte leaves the PDF writer,
//   * `hasUnrepresentable` reports on it — it decides whether the report
//     appends the note telling the reader that a character was folded,
//   * the font layer reads it — `/Widths` is indexed by the byte, and the
//     embedded subset has to keep a glyph for every code point a byte can
//     name (`lib/ttf.mjs`).
//
// Keeping the first two in `lib/pdf.mjs` and the third in `lib/ttf.mjs` would
// mean two tables that drift apart silently: a new entry added to the emitter
// and not to the subsetter produces a report whose text measures correctly and
// then draws no glyph. There is no later stage at which that would be caught,
// so both read from here instead.
//
// The typographic folds are test-locked. The C1 table keeps the WinAnsi
// specials (bullets, the euro sign, fancy ligatures) at their encoded
// positions; every other code point outside the encoding — and every control
// character — is escaped as \uXXXX so that nothing is silently lost.

const WINANSI_EXTRAS = new Map([
  [0x20AC, 0x80], [0x201A, 0x82], [0x0192, 0x83], [0x201E, 0x84],
  [0x2020, 0x86], [0x2021, 0x87], [0x02C6, 0x88], [0x2030, 0x89],
  [0x0160, 0x8A], [0x2039, 0x8B], [0x0152, 0x8C], [0x017D, 0x8E],
  [0x2022, 0x95], [0x02DC, 0x98], [0x2122, 0x99], [0x0161, 0x9A],
  [0x203A, 0x9B], [0x0153, 0x9C], [0x017E, 0x9E], [0x0178, 0x9F],
]);

// The encoding read the other way round: every byte from 0x80 to 0x9F, which is
// the only part of WinAnsiEncoding that is not ASCII and Latin-1 standing on
// each other. `null` marks the five positions Adobe leaves undefined (0x81,
// 0x8D, 0x8F, 0x90, 0x9D); no string can reach them, because `toWinAnsi` folds
// an unmapped code point to "?" long before a byte exists.
//
// This table is deliberately *not* the inverse of `WINANSI_EXTRAS`. Of these 32
// positions, 5 Adobe leaves undefined, 7 the emitter handles by hand — the
// ellipsis at 0x85, the four smart quotes at 0x91-0x94 and the two dashes at
// 0x96-0x97 — and 20 come from the table proper: 5 + 7 + 20 = 32.
// `tests/ttf.mjs` asserts that the two agree wherever both are defined, which
// is the property that matters: an entry in the emitter must not disagree
// about the byte it names.
const WINANSI_C1 = new Map([
  [0x80, 0x20AC], [0x81, null], [0x82, 0x201A], [0x83, 0x0192],
  [0x84, 0x201E], [0x85, 0x2026], [0x86, 0x2020], [0x87, 0x2021],
  [0x88, 0x02C6], [0x89, 0x2030], [0x8A, 0x0160], [0x8B, 0x2039],
  [0x8C, 0x0152], [0x8D, null], [0x8E, 0x017D], [0x8F, null],
  [0x90, null], [0x91, 0x2018], [0x92, 0x2019], [0x93, 0x201C],
  [0x94, 0x201D], [0x95, 0x2022], [0x96, 0x2013], [0x97, 0x2014],
  [0x98, 0x02DC], [0x99, 0x2122], [0x9A, 0x0161], [0x9B, 0x203A],
  [0x9C, 0x0153], [0x9D, null], [0x9E, 0x017E], [0x9F, 0x0178],
]);

/**
 * The Unicode code point WinAnsiEncoding places at `byte`, or `null` when the
 * position is undefined. `/Widths` is indexed by the byte a viewer reads, so
 * this is the direction the font layer needs; `toWinAnsi` needs the other.
 *
 * @param {number} byte 0-255
 * @returns {number|null}
 */
export function winAnsiToUnicode(byte) {
  if (byte >= 0x20 && byte <= 0x7E) return byte;
  if (byte >= 0xA0 && byte <= 0xFF) return byte;
  if (WINANSI_C1.has(byte)) return WINANSI_C1.get(byte);
  return null;
}

/**
 * True when `codePoint` has no single-byte WinAnsi code, which is what the "?"
 * fold is for. The en dash and the em dash are deliberately absent: 0x96 and
 * 0x97 are the bytes WinAnsi puts them at, so they are representable.
 */
function unrepresentable(codePoint) {
  if (codePoint >= 0x20 && codePoint <= 0x7E) return false;
  if (codePoint >= 0xA0 && codePoint <= 0xFF) return false;
  if (codePoint === 0x96 || codePoint === 0x97) return false;
  if (WINANSI_EXTRAS.has(codePoint)) return false;
  return true;
}

/**
 * True when any code point in `value` will be replaced by "?". The soft hyphen
 * is excluded: it is dropped on purpose and needs no note.
 */
export function hasUnrepresentable(value) {
  for (const ch of value) {
    const cp = ch.codePointAt(0);
    if (cp === 0x00AD) continue;
    if (unrepresentable(cp)) return true;
  }
  return false;
}

/**
 * Fold a string into the bytes the report can show. Idempotent: the string
 * reaches this function twice (wrap measures, pdfLiteral emits) and folding an
 * already-folded string must not move it again.
 *
 * @param {string} value
 * @returns {string} one JS char per byte, its code being the byte value
 */
export function toWinAnsi(value) {
  let out = '';
  for (const ch of value) {
    const cp = ch.codePointAt(0);
    if (cp === 0x2018 || cp === 0x2019) out += "'";
    else if (cp === 0x201C || cp === 0x201D) out += '"';
    // WinAnsi encodes the en dash at 0x96 and the em dash at 0x97; folding
    // them to "-" hid UE-NU002's whole defect, where Current and Should be
    // differ only in the dash. The byte form passes through as well, because
    // every string reaches this function twice (wrap measures, pdfLiteral
    // emits) and the encoding must be idempotent.
    else if (cp === 0x2013 || cp === 0x96) out += '\u0096';
    else if (cp === 0x2014 || cp === 0x97) out += '\u0097';
    else if (cp === 0x2026) out += '...';
    else if (cp === 0x00AD) { /* soft hyphen: dropped, and announced nowhere */ }
    else if (unrepresentable(cp)) out += '?';
    else if (cp >= 0x20 && cp <= 0x7E) out += ch;
    else if (cp >= 0xA0 && cp <= 0xFF) out += ch;
    else {
      // Reaching here means `unrepresentable` called this representable, which
      // it only does for the table's own keys or the two byte-form dashes the
      // branches above already handled. If a future edit returns `false` for a
      // code point the table does not hold, `get` yields undefined and
      // `fromCharCode` yields a raw NUL — a byte no one chose, drawn as
      // nothing, in a content stream. Refuse instead.
      const byte = WINANSI_EXTRAS.get(cp);
      if (byte === undefined) {
        throw new Error(`winansi: U+${cp.toString(16).toUpperCase()} is treated as representable `
          + 'but has no byte in WINANSI_EXTRAS');
      }
      out += String.fromCharCode(byte);
    }
  }
  return out;
}
