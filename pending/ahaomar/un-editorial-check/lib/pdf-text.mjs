// PDF text extraction: fonts, encodings, content-stream text operators,
// reading order, and the contract's `Unit[]`.
//
// Zero npm dependencies. `node:fs` and `node:zlib` only.
//
// THE RULE THIS FILE EXISTS TO ENFORCE
//
// > If you cannot prove you recovered the text correctly, refuse.
//
// This is not a stylistic preference. In version 1.2.0 the tool printed its
// clean sentence after having read nothing at all, and the fix was to narrow
// what the tool claims rather than to argue about the wording. A PDF makes
// that failure mode easy to reach and hard to see, because a PDF is a rendered
// page: there is no source, no paragraph, no author. Every decision below is
// therefore made to protect one thing — the promise that a `file:line:col`
// in the output points at text a reader would agree is on that line.
//
// Three things make that promise, and each refuses rather than guesses:
//
//   1. A font whose encoding cannot be resolved refuses (UNDECODABLE_FONT).
//      There is no acceptable fallback: a `/Differences` array naming a glyph
//      this extractor has no Unicode for, or a CID font with no `/ToUnicode`,
//      would otherwise be decoded byte by byte into mojibake, and mojibake in
//      a copy checker reads as English and produces findings about words no
//      one wrote. Guessing there is indistinguishable from succeeding.
//   2. Text drawn with a vertical writing mode (`Identity-V`) refuses. The
//      characters are recoverable; the line they form is not a line, and
//      emitting one glyph per "line" would be a confidently wrong line number.
//   3. A page carrying images and no text at all refuses (SCANNED). Nothing
//      here reads an image and nothing claims to. A scan is not "read", it is
//      refused, and saying so is the whole point.
//
// A document that has been read, has images, and also has real text on other
// pages is NOT refused: its copy is recoverable and the images are decoration.
// A document read in full that genuinely contains no text returns no units,
// exactly as an empty `.txt` file does. The difference matters: "read nothing"
// and "read it, and it is empty" must not look the same, which is why the
// scanned case is decided by images rather than by an absence of words.
//
// A "line" IN THIS EXTRACTOR IS NOT A SOURCE LINE
//
// A PDF has no lines. What is reconstructed here is a *visual* line: text runs
// that share a baseline, ordered left to right. Two paragraphs of one article
// share the font, the measure and the rhythm, and the boundary between them is
// vertical whitespace — so where a paragraph ends is a matter of geometry, and
// never a fact about the author's intent.
//
// This module resolves that by declining to judge it. `unitsFromLines` gives
// every visual line its own unit and no vertical gap is ever measured, so two
// lines never merge however far apart they sit: a paragraph break comes out
// identical to an ordinary line break, and no paragraph structure is recovered
// at all. That is the one approximation in this module — a visual line standing
// in for whatever the author's line was — and it is the reason PDF units are
// reported with `context: 'authored'` always. It must never be described as a
// source line.

import { makeUnit } from './units.mjs';
import { lineStarts } from './position.mjs';
import {
  openPdf, PdfRefusalError, PDF_REFUSAL_CODES, refuse,
  isName, isDict, isStream, Lexer,
} from './pdf-parse.mjs';

// The refusal class and the code table are re-exported so that the adapter in
// `pdf-extract.mjs` can catch the *same* class this module throws. Declaring a
// second `PdfRefusalError` over there would make `instanceof` fail and turn
// every refusal into an unhandled error, so these are the canonical definitions
// and must be imported, not redefined.
export { PdfRefusalError, PDF_REFUSAL_CODES };

// --- glyph names to Unicode --------------------------------------------------
//
// The Adobe Glyph List, reduced to the names a PDF actually uses: the three
// predefined encodings below, the accented Latin repertoire, Greek, the
// typographic punctuation, and the ligatures. Completeness is not the point —
// an entry that is absent causes a refusal, and that is the intended
// behaviour. Inventing a Unicode value for an unknown name would produce
// exactly the mojibake this file is built to prevent.

const GLYPHS = {
  // Space and ASCII punctuation.
  space: ' ', exclam: '!', quotedbl: '"', numbersign: '#', dollar: '$', percent: '%',
  ampersand: '&', quotesingle: "'", quoteright: '’', quoteleft: '‘', parenleft: '(',
  parenright: ')', asterisk: '*', plus: '+', comma: ',', hyphen: '-', period: '.',
  slash: '/', colon: ':', semicolon: ';', less: '<', equal: '=', greater: '>',
  question: '?', at: '@', bracketleft: '[', backslash: '\\', bracketright: ']',
  asciicircum: '^', underscore: '_', grave: '`', braceleft: '{', bar: '|',
  braceright: '}', asciitilde: '~', sfthyphen: '‐', nbspace: ' ',
  // Digits and Latin letters.
  zero: '0', one: '1', two: '2', three: '3', four: '4', five: '5', six: '6',
  seven: '7', eight: '8', nine: '9',
  A: 'A', B: 'B', C: 'C', D: 'D', E: 'E', F: 'F', G: 'G', H: 'H', I: 'I', J: 'J',
  K: 'K', L: 'L', M: 'M', N: 'N', O: 'O', P: 'P', Q: 'Q', R: 'R', S: 'S', T: 'T',
  U: 'U', V: 'V', W: 'W', X: 'X', Y: 'Y', Z: 'Z',
  a: 'a', b: 'b', c: 'c', d: 'd', e: 'e', f: 'f', g: 'g', h: 'h', i: 'i', j: 'j',
  k: 'k', l: 'l', m: 'm', n: 'n', o: 'o', p: 'p', q: 'q', r: 'r', s: 's', t: 't',
  u: 'u', v: 'v', w: 'w', x: 'x', y: 'y', z: 'z',
  // Latin-1.
  exclamdown: '¡', cent: '¢', sterling: '£', currency: '¤', yen: '¥',
  brokenbar: '¦', section: '§', dieresis: '¨', copyright: '©',
  ordfeminine: 'ª', guillemotleft: '«', logicalnot: '¬', registered: '®',
  macron: '¯', degree: '°', plusminus: '±', acute: '´', mu: 'µ',
  paragraph: '¶', periodcentered: '·', cedilla: '¸', onesuperior: '¹',
  ordmasculine: 'º', guillemotright: '»', onequarter: '¼', onehalf: '½',
  threequarters: '¾', questiondown: '¿',
  Agrave: 'À', Aacute: 'Á', Acircumflex: 'Â', Atilde: 'Ã', Adieresis: 'Ä',
  Aring: 'Å', AE: 'Æ', Ccedilla: 'Ç', Egrave: 'È', Eacute: 'É',
  Ecircumflex: 'Ê', Edieresis: 'Ë', Igrave: 'Ì', Iacute: 'Í', Icircumflex: 'Î',
  Idieresis: 'Ï', Eth: 'Ð', Ntilde: 'Ñ', Ograve: 'Ò', Oacute: 'Ó',
  Ocircumflex: 'Ô', Otilde: 'Õ', Odieresis: 'Ö', multiply: '×', Oslash: 'Ø',
  Ugrave: 'Ù', Uacute: 'Ú', Ucircumflex: 'Û', Udieresis: 'Ü', Yacute: 'Ý',
  Thorn: 'Þ', germandbls: 'ß',
  agrave: 'à', aacute: 'á', acircumflex: 'â', atilde: 'ã', adieresis: 'ä',
  aring: 'å', ae: 'æ', ccedilla: 'ç', egrave: 'è', eacute: 'é',
  ecircumflex: 'ê', edieresis: 'ë', igrave: 'ì', iacute: 'í', icircumflex: 'î',
  idieresis: 'ï', eth: 'ð', ntilde: 'ñ', ograve: 'ò', oacute: 'ó',
  ocircumflex: 'ô', otilde: 'õ', odieresis: 'ö', divide: '÷', oslash: 'ø',
  ugrave: 'ù', uacute: 'ú', ucircumflex: 'û', udieresis: 'ü', yacute: 'ý',
  thorn: 'þ', ydieresis: 'ÿ',
  // Latin Extended-A, the range a European report actually reaches for.
  Amacron: 'Ā', amacron: 'ā', Abreve: 'Ă', abreve: 'ă', Aogonek: 'Ą',
  aogonek: 'ą', Cacute: 'Ć', cacute: 'ć', Ccaron: 'Č', ccaron: 'č',
  Dcaron: 'Ď', dcaron: 'ď', Dcroat: 'Đ', dcroat: 'đ', Emacron: 'Ē',
  emacron: 'ē', Ebreve: 'Ĕ', ebreve: 'ĕ', Eogonek: 'Ę', eogonek: 'ę',
  Ecaron: 'Ě', ecaron: 'ě', Gcircumflex: 'Ĝ', gcircumflex: 'ĝ', Gbreve: 'Ğ',
  gbreve: 'ğ', Idotaccent: 'İ', igrave: 'ì', Lacute: 'Ĺ', lacute: 'ĺ',
  Lcaron: 'Ľ', lcaron: 'ľ', Nacute: 'Ń', nacute: 'ń', Ncaron: 'Ň',
  ncaron: 'ň', Ntilde2: 'Ŋ', ntilde2: 'ŋ', Ohungarumlaut: 'Ő',
  ohungarumlaut: 'ő', OE: 'Œ', Racute: 'Ŕ', racute: 'ŕ', Rcaron: 'Ř',
  rcaron: 'ř', Sacute: 'Ś', sacute: 'ś', Scaron: 'Š', scaron: 'š',
  Tcommaaccent: 'Ţ', tcommaaccent: 'ŧ', Tcaron: 'Ť', tcaron: 'ť',
  Uring: 'Ů', uring: 'ů', Uhungarumlaut: 'Ű', uhungarumlaut: 'ű',
  Ucaron: 'Ů', Ydieresis2: 'Ÿ',
  // Typographic punctuation and marks.
  quotesinglbase: '‚', quotedblbase: '„', quotedblleft: '“',
  quotedblright: '”', guilsinglleft: '‹', guilsinglright: '›',
  endash: '–', emdash: '—', dagger: '†', daggerdbl: '‡', bullet: '•',
  ellipsis: '…', perthousand: '‰', fraction: '⁄', fi: 'ﬁ', fl: 'ﬂ',
  ff: 'ﬀ', ffi: 'ﬃ', ffl: 'ﬄ', dotlessi: 'ı', Lslash: 'Ł', lslash: 'ł',
  dotaccent: '˙', breve: '˘', ring: '˚', ogonek: 'ˉ', caron: 'ˇ',
  hungarumlaut: '˝', tilde: '˜', circumflex: 'ˆ',
  // Currency, symbols, arrows.
  Euro: '€', trademark: '™', minus: '−', infinity: '∞',
  arrowleft: '←', arrowup: '↑', arrowright: '→', arrowdown: '↓',
  arrowboth: '↔', arrowdblleft: '⇐', arrowdblright: '⇒',
  partialdiff: '∂', summation: '∑', product: '∏', integral: '∫',
  radical: '√', approxequal: '≈', notequal: '≠', lessthan: '<',
  greaterequal: '≥', element: '∈', universal: '∀', existential: '∃',
  angle: '∠', congruent: '≅', equivariance: '≃',
  therefore: '∴', florin: 'ƒ', currency2: '₡', logicalnot2: '¬',
  // Greek, lower then upper. Used by scientific and technical documents.
  alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ε', zeta: 'ζ',
  eta: 'η', theta: 'θ', iota: 'ι', kappa: 'κ', lambda: 'λ', nu: 'ν',
  xi: 'ξ', pi: 'π', rho: 'ρ', sigma: 'σ', tau: 'τ', upsilon: 'υ',
  phi: 'φ', chi: 'χ', psi: 'ψ', omega: 'ω', alpha1: 'α', beta1: 'β',
  theta1: 'ϑ', sigma1: 'ς', phi1: 'ϕ', omega1: 'ϖ',
  Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ', Xi: 'Ξ', Pi: 'Π',
  Sigma: 'Σ', Upsilon: 'Υ', Phi: 'Φ', Psi: 'Ψ', Omega: 'Ω',
  // Superscripts and ordinals.
  onesuperior2: '¹', twosuperior: '²', threesuperior: '³', oneeighth: '⅛',
  threeeighths: '⅜', fiveeighths: '⅝', seveneighths: '⅞',
  // A handful of names that are not really glyph names but appear as such.
  nbsp: ' ', space2: ' ', zero2: '0',
};

/**
 * Resolve a glyph name to Unicode.
 *
 * `/Differences` arrays may name a glyph that the AGL spells as a composition
 * (`a_acute` for `á`), so underscore forms are expanded once before giving up.
 */
function glyphToUnicode(name) {
  if (!name) return null;
  if (Object.hasOwn(GLYPHS, name)) return GLYPHS[name];
  if (name.length > 1 && name.includes('_')) {
    const [base, ...rest] = name.split('_');
    const combined = rest.map(cap).join('');
    const baseChar = GLYPHS[base];
    const mark = GLYPHS[combined];
    if (baseChar && mark) {
      // Decompose: the mark alone is a combining code point in the ranges
      // above, and a base plus combining mark composes to the right letter.
      const composed = String.fromCodePoint(baseChar.codePointAt(0))
        .normalize('NFC');
      const withMark = (composed + mark).normalize('NFC');
      if (withMark.length === 1) return withMark;
    }
  }
  // `uniXXXX` and `uXXXX` are the PDF spec's own escape hatches.
  const uni = /^uni([0-9a-fA-F]{4,6})$/.exec(name) || /^u([0-9a-fA-F]{4,6})$/.exec(name);
  if (uni) {
    const value = parseInt(uni[1], 16);
    if (value > 0 && value <= 0x10ffff) return String.fromCodePoint(value);
  }
  return null;
}

const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

// --- the three predefined encodings -----------------------------------------
//
// Codes 32 to 126 are shared by all three and differ only in the two quote
// characters, so one string covers the common range and the upper halves are
// spelled out. A code with no entry is genuinely unassigned in that encoding
// and resolves to no glyph, which is not an error until text actually uses it.

// Codes 32 to 126 in glyph NAMES, not in characters.
//
// This distinction is the whole ball game. An encoding maps a code to a glyph
// name, and the name is then looked up in the glyph list to get a character.
// A table written with the characters themselves would map code 45 to the
// two-character string "-", which is not a glyph name, resolves to nothing, and
// turns every hyphen in the document into a refusal.
const ASCII_GLYPH_NAMES = [
  'space', 'exclam', 'quotedbl', 'numbersign', 'dollar', 'percent',
  'ampersand', 'quotesingle', 'parenleft', 'parenright', 'asterisk', 'plus',
  'comma', 'hyphen', 'period', 'slash',
  'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
  'colon', 'semicolon', 'less', 'equal', 'greater', 'question', 'at',
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  'bracketleft', 'backslash', 'bracketright', 'asciicircum', 'underscore',
  'quoteleft',
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
  'braceleft', 'bar', 'braceright', 'asciitilde',
];

const ENCODING_TABLES = {
  StandardEncoding: {
    // Code 32 is a space in every one of these encodings. The typographic
    // quote is code 39 in StandardEncoding, not code 32.
    39: 'quoteright', 96: 'quoteleft',
    161: 'exclamdown', 162: 'cent', 163: 'sterling', 164: 'fraction', 165: 'yen',
    166: 'florin', 167: 'section', 168: 'currency', 169: 'quotesingle',
    170: 'quotedblleft', 171: 'guillemotleft', 172: 'guilsinglleft',
    173: 'guilsinglright', 174: 'fi', 175: 'fl', 177: 'endash', 178: 'dagger',
    179: 'daggerdbl', 180: 'periodcentered', 182: 'paragraph', 183: 'bullet',
    184: 'quotesinglbase', 185: 'quotedblbase', 186: 'quotedblright',
    187: 'guillemotright', 188: 'ellipsis', 189: 'perthousand', 191: 'questiondown',
    193: 'grave', 194: 'acute', 195: 'circumflex', 196: 'tilde', 197: 'macron',
    198: 'breve', 199: 'dotaccent', 200: 'dieresis', 202: 'ring', 203: 'cedilla',
    205: 'hungarumlaut', 206: 'ogonek', 207: 'caron', 208: 'emdash', 225: 'AE',
    227: 'ordfeminine', 232: 'Lslash', 233: 'Oslash', 234: 'OE',
    235: 'ordmasculine', 241: 'ae', 245: 'dotlessi', 248: 'lslash', 249: 'oslash',
    250: 'oe', 251: 'germandbls',
  },
  WinAnsiEncoding: {
    39: 'quotesingle', 96: 'grave',
    128: 'Euro', 130: 'quotesinglbase', 131: 'florin', 132: 'quotedblbase',
    133: 'ellipsis', 134: 'dagger', 135: 'daggerdbl', 136: 'circumflex',
    137: 'perthousand', 138: 'Scaron', 139: 'guilsinglleft', 140: 'OE',
    142: 'Zcaron', 145: 'quoteleft', 146: 'quoteright', 147: 'quotedblleft',
    148: 'quotedblright', 149: 'bullet', 150: 'endash', 151: 'emdash', 152: 'tilde',
    153: 'trademark', 154: 'scaron', 155: 'guilsinglright', 156: 'oe',
    158: 'zcaron', 159: 'Ydieresis',
    160: 'space', 161: 'exclamdown', 162: 'cent', 163: 'sterling', 164: 'currency',
    165: 'yen', 166: 'brokenbar', 167: 'section', 168: 'dieresis', 169: 'copyright',
    170: 'ordfeminine', 171: 'guillemotleft', 172: 'logicalnot', 173: 'hyphen',
    174: 'registered', 175: 'macron', 176: 'degree', 177: 'plusminus', 178: 'acute',
    179: 'mu', 180: 'paragraph', 181: 'periodcentered', 182: 'cedilla',
    183: 'onesuperior', 184: 'ordmasculine', 185: 'guillemotright', 186: 'onequarter',
    187: 'onehalf', 188: 'threequarters', 189: 'questiondown', 191: 'grave',
    192: 'acute', 193: 'circumflex', 194: 'tilde', 195: 'macron', 196: 'breve',
    197: 'dotaccent', 198: 'dieresis', 199: 'copyright', 200: 'Agrave', 201: 'Aacute',
    202: 'Acircumflex', 203: 'Atilde', 204: 'Adieresis', 205: 'Aring', 206: 'AE',
    207: 'Ccedilla', 208: 'Egrave', 209: 'Eacute', 210: 'Ecircumflex',
    211: 'Edieresis', 212: 'Igrave', 213: 'Iacute', 214: 'Icircumflex',
    215: 'Idieresis', 216: 'Eth', 217: 'Ntilde', 218: 'Ograve', 219: 'Oacute',
    220: 'Ocircumflex', 221: 'Otilde', 222: 'Odieresis', 223: 'multiply',
    224: 'Oslash', 225: 'Ugrave', 226: 'Uacute', 227: 'Ucircumflex',
    228: 'Udieresis', 229: 'Yacute', 230: 'Thorn', 231: 'germandbls', 232: 'agrave',
    233: 'aacute', 234: 'acircumflex', 235: 'atilde', 236: 'adieresis', 237: 'aring',
    238: 'ae', 239: 'ccedilla', 240: 'egrave', 241: 'eacute', 242: 'ecircumflex',
    243: 'edieresis', 244: 'igrave', 245: 'iacute', 246: 'icircumflex',
    247: 'idieresis', 248: 'eth', 249: 'ntilde', 250: 'ograve', 251: 'oacute',
    252: 'ocircumflex', 253: 'otilde', 254: 'odieresis', 255: 'divide',
  },
  MacRomanEncoding: {
    39: 'quotesingle', 96: 'grave',
    128: 'Adieresis', 129: 'Aring', 130: 'Ccedilla', 131: 'Eacute',
    132: 'Ntilde', 133: 'Odieresis', 134: 'Udieresis', 135: 'aacute', 136: 'agrave',
    137: 'acircumflex', 138: 'adieresis', 139: 'atilde', 140: 'aring', 141: 'ccedilla',
    142: 'eacute', 143: 'egrave', 144: 'ecircumflex', 145: 'edieresis', 146: 'iacute',
    147: 'igrave', 148: 'icircumflex', 149: 'idieresis', 150: 'ntilde', 151: 'oacute',
    152: 'ograve', 153: 'ocircumflex', 154: 'odieresis', 155: 'otilde', 156: 'uacute',
    157: 'ugrave', 158: 'ucircumflex', 159: 'udieresis', 160: 'dagger', 161: 'degree',
    162: 'cent', 163: 'sterling', 164: 'section', 165: 'bullet', 166: 'paragraph',
    167: 'germandbls', 168: 'registered', 169: 'copyright', 170: 'trademark',
    171: 'acute', 172: 'dieresis', 173: 'notequal', 174: 'AE', 175: 'Oslash',
    176: 'infinity', 177: 'plusminus', 178: 'less', 179: 'greater', 180: 'yen',
    181: 'mu', 182: 'partialdiff', 183: 'summation', 184: 'product', 185: 'pi',
    186: 'integral', 187: 'ordfeminine', 188: 'ordmasculine', 189: 'Omega', 190: 'ae',
    191: 'oslash', 192: 'questiondown', 193: 'exclamdown', 194: 'logicalnot',
    195: 'radical', 196: 'florin', 197: 'approxequal', 198: 'Delta', 199: 'guillemotleft',
    200: 'guillemotright', 201: 'ellipsis', 202: 'space', 203: 'Agrave',
    204: 'Atilde', 205: 'Otilde', 206: 'OE', 207: 'oe', 208: 'endash', 209: 'emdash',
    210: 'quotedblleft', 211: 'quotedblright', 212: 'quoteleft', 213: 'quoteright',
    214: 'divide', 215: 'lozenge', 216: 'ydieresis', 217: 'Ydieresis', 218: 'fraction',
    219: 'currency', 220: 'guilsinglleft', 221: 'guilsinglright', 222: 'fi', 223: 'fl',
    224: 'daggerdbl', 225: 'periodcentered', 226: 'quotesinglbase', 227: 'quotedblbase',
    228: 'perthousand', 229: 'Acircumflex', 230: 'Ecircumflex', 231: 'Aacute',
    232: 'Edieresis', 233: 'Egrave', 234: 'Iacute', 235: 'Icircumflex', 236: 'Idieresis',
    237: 'Igrave', 238: 'Oacute', 239: 'Ocircumflex', 240: 'apple', 241: 'Ograve',
    242: 'Uacute', 243: 'Ucircumflex', 244: 'Ugrave', 245: 'dotlessi', 246: 'circumflex',
    247: 'tilde', 248: 'macron', 249: 'breve', 250: 'dotaccent', 251: 'ring',
    252: 'cedilla', 253: 'hungarumlaut', 254: 'ogonek', 255: 'caron',
  },
};

/** Build a code -> glyph-name table for one predefined encoding. */
function encodingTable(name) {
  const special = ENCODING_TABLES[name] || {};
  const map = new Map();
  for (let code = 32; code <= 126; code++) {
    map.set(code, special[code] || ASCII_GLYPH_NAMES[code - 32]);
  }
  for (let code = 128; code <= 255; code++) {
    if (special[code]) map.set(code, special[code]);
  }
  return map;
}

const ENCODINGS = {
  StandardEncoding: encodingTable('StandardEncoding'),
  WinAnsiEncoding: encodingTable('WinAnsiEncoding'),
  MacRomanEncoding: encodingTable('MacRomanEncoding'),
};

// --- ToUnicode CMap ----------------------------------------------------------
//
// A CMap maps character codes to Unicode. Only the pieces that carry text are
// implemented: `begincodespacerange`, `beginbfchar`, `beginbfrange`, and the
// `end*` terminators. `begincidrange` and `begincidchar` are accepted and
// ignored, because they map to CIDs rather than to Unicode: a CMap relying on
// them simply has no Unicode to give, and saying nothing is the correct answer
// rather than a silent failure.
//
// An unrecognised operator inside a CMap refuses. Skipping it would leave a
// `bfchar` block unparsed and the mapping empty, which is precisely how
// mojibake gets in: the document would read as though it had no text there.

// The mapping blocks a CMap can contain, each with the terminator that ends it.
const CMAP_BLOCKS = new Map([
  ['begincodespacerange', 'endcodespacerange'],
  ['beginbfchar', 'endbfchar'],
  ['beginbfrange', 'endbfrange'],
  ['begincidrange', 'endcidrange'],
  ['begincidchar', 'endcidchar'],
]);

// A CMap is a PostScript program, so it is full of operators that define
// dictionaries and push them. None of these carries a character mapping, and
// all of them are stepped over.
const CMAP_IGNORED_OPERATORS = new Set([
  'begincmap', 'endcmap', 'usecmap', 'begin', 'end', 'def', 'defineresource',
  'findresource', 'currentdict', 'readonly', 'dict', 'dup', 'exch', 'pop',
  'index', 'copy', 'put', 'get', 'known', 'where', 'undef', 'load',
]);

/** Sentinel returned by `cmapOperand` for the `]` that ends an array. */
const CMAP_CLOSE = Symbol('cmapClose');

/**
 * Read one CMap operand. Unlike a content stream's, a CMap operand may be an
 * array — `bfrange` uses `[<src> <dst> ...]` destinations — so this reads
 * structure rather than a flat token list.
 */
function cmapOperand(lex) {
  const token = lex.next();
  if (!token) return null;
  if (token.type === 'arrayOpen') {
    const items = [];
    for (;;) {
      const item = cmapOperand(lex);
      if (item === null || item === CMAP_CLOSE) break;
      items.push(item);
    }
    return items;
  }
  if (token.type === 'arrayClose') return CMAP_CLOSE;
  return token;
}

/**
 * Decode a CMap destination into a JavaScript string.
 *
 * The hex digits are read from the *byte values*, never from a decoded string.
 * This is not a style choice: byte `0x44` is the letter `D`, so a `latin1`
 * string built from the bytes turns the destination `<0044>` into the text
 * `D`, and every later step then reads the wrong number of hex digits. Working
 * from the bytes is the only way `<0044>` can be seen as two digits, a leading
 * zero and a `4`.
 *
 * Destinations are UTF-16BE, so a code point above the basic plane arrives as
 * a surrogate pair and is read as a pair rather than as two characters.
 *
 * @returns {string|null} null when the bytes are not valid Unicode
 */
function hexToUnicode(bytes) {
  // Two things are deliberately not done here. The bytes are never decoded to a
  // string first: byte `0x41` is the character `D`, and a filter keeping the
  // characters matching `[0-9a-fA-F]` would keep that `D` and drop the leading
  // `0x00` of `<0041>`, turning every two-byte destination into a different
  // character. And no byte is treated as whitespace: the lexer has already
  // stripped whitespace while reading the hex, and byte `0x20` is not padding
  // here, it is the digit `2` — the first half of the destination `<2014>`,
  // an em dash.
  const digits = [];
  for (const byte of bytes) {
    digits.push(((byte >> 4) & 0x0f).toString(16));
    digits.push((byte & 0x0f).toString(16));
  }
  if (digits.length === 0) return '';
  if (digits.length % 2) digits.push('0'); // an odd final digit is padded
  const clean = digits.join('');

  let out = '';
  let i = 0;
  while (i < clean.length) {
    if (clean.length - i >= 8) {
      const high = parseInt(clean.slice(i, i + 4), 16);
      const low = parseInt(clean.slice(i + 4, i + 8), 16);
      if (high >= 0xd800 && high <= 0xdbff && low >= 0xdc00 && low <= 0xdfff) {
        out += String.fromCharCode(high, low);
        i += 8;
        continue;
      }
    }
    if (clean.length - i >= 4) {
      const value = parseInt(clean.slice(i, i + 4), 16);
      if (value > 0 && value <= 0x10ffff && !(value >= 0xd800 && value <= 0xdfff)) {
        out += String.fromCodePoint(value);
        i += 4;
        continue;
      }
      return null; // not a code point that can exist
    }
    const pair = clean.slice(i, i + 2);
    if (pair.length < 2) return null;
    const value = parseInt(pair, 16);
    if (value === 0) return null; // a NUL destination is not text
    if (value >= 0xd800 && value <= 0xdfff) return null; // a lone surrogate
    out += String.fromCharCode(value);
    i += 2;
  }
  return out;
}

/** Destination of a `bfchar`/`bfrange` entry, whether written `<hex>` or `( )`. */
function destinationToUnicode(operand) {
  if (!operand) return null;
  if (operand.type === 'hexstring' || operand.type === 'string') return hexToUnicode(operand.bytes);
  return null;
}

const keyOf = (bytes) => Buffer.from(bytes).toString('latin1');

/**
 * The keys a `code` may be stored under in a parsed ToUnicode CMap.
 *
 * A CMap declares its own codespace, and that codespace is not obliged to be as
 * wide as the codes the font actually uses. A producer emitting a CID-style
 * `<0000> <FFFF>` template onto a one-byte Type1 font stores every entry two
 * bytes wide while the content stream still supplies one, so forming the key
 * from the code alone misses — and the caller then reports a mapping that
 * exists as one that does not. That is the specific lie this tool refuses to
 * tell, so the declared codespace is used as the evidence it is.
 *
 * Only the declared widths and the plain single-byte form are tried, in that
 * order: a bounded lookup over stated evidence, not a search for anything that
 * happens to be in the map.
 */
function toUnicodeKeys(code, ranges) {
  const keys = [keyOf(Buffer.from([code & 0xff]))];
  for (const range of ranges) {
    const width = range?.length;
    if (!Number.isInteger(width) || width < 2 || width > 8) continue;
    const buf = Buffer.alloc(width);
    let value = code;
    for (let i = width - 1; i >= 0 && value > 0; i--) {
      buf[i] = value & 0xff;
      value = Math.floor(value / 256);
    }
    const key = keyOf(buf);
    if (!keys.includes(key)) keys.push(key);
  }
  return keys;
}

/** Add `offset` to a big-endian byte string. */
function addBytes(start, offset) {
  const out = Buffer.from(start);
  for (let i = out.length - 1; i >= 0; i--) {
    const sum = out[i] + (offset % 256);
    out[i] = sum & 0xff;
    offset = Math.floor(offset / 256);
    if (offset === 0) break;
  }
  return out;
}

const bytesToNumber = (bytes) => Number(BigInt('0x' + (Buffer.from(bytes).toString('hex') || '0')));

/**
 * Parse a CMap stream.
 *
 * @returns {{ map: Map<string,string>, ranges: Array<{lo:number,hi:number,length:number}> }}
 *   `map` is code bytes to Unicode; `ranges` is the codespace, which is what
 *   tells a caller how many bytes each character code occupies.
 */
export function parseCMap(bytes) {
  const map = new Map();
  const ranges = [];
  const lex = new Lexer(Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes));

  for (;;) {
    const token = lex.next();
    if (!token) break;
    if (token.type !== 'keyword') continue;
    const op = token.value;
    if (op === 'endcmap') break;

    const terminator = CMAP_BLOCKS.get(op);
    if (terminator === undefined) {
      if (CMAP_IGNORED_OPERATORS.has(op)) continue;
      // An unrecognised *mapping* block is different from an unrecognised
      // dictionary operator: its entries would be dropped, leaving codes that
      // look unassigned. That turns a real decode into a refusal at best, and
      // at worst into a partial one, so a `begin*` block this extractor does
      // not know refuses rather than being skipped. A bare `begin` is
      // PostScript, not a block.
      if (!op.startsWith('begin') || op === 'begin') continue;
      refuse(
        `a CMap uses the mapping block ${op}, which this extractor cannot interpret, so its text cannot be read`,
        'UNDECODABLE_FONT',
        { operator: op },
      );
    }

    // The count written after a `begin` keyword says how many items the block
    // holds; it is not a number of operands to read. Reading a fixed two, as an
    // operand count would suggest, throws away every mapping in a real font:
    // a CMap with a hundred `bfchar` entries would yield one. The block is
    // therefore read until its terminator, which is what the count is for.
    const operands = [];
    for (;;) {
      const item = cmapOperand(lex);
      if (item === null) break;
      if (item === CMAP_CLOSE) continue; // a stray bracket inside the block
      if (item.type === 'keyword') {
        if (item.value === terminator) break;
        // A nested block ends here: the outer one continues. A stray operator
        // is dropped, which for a dictionary operator is correct.
        if (CMAP_BLOCKS.has(item.value)) break;
        continue;
      }
      operands.push(item);
    }

    if (op === 'begincodespacerange') {
      for (let i = 0; i + 1 < operands.length; i += 2) {
        const lo = operands[i];
        const hi = operands[i + 1];
        if (lo?.type !== 'hexstring' || hi?.type !== 'hexstring') continue;
        if (lo.bytes.length !== hi.bytes.length || lo.bytes.length === 0) continue;
        ranges.push({
          lo: bytesToNumber(lo.bytes),
          hi: bytesToNumber(hi.bytes),
          length: lo.bytes.length,
        });
      }
    } else if (op === 'beginbfchar') {
      for (let i = 0; i + 1 < operands.length; i += 2) {
        const src = operands[i];
        if (src?.type !== 'hexstring') continue;
        const text = destinationToUnicode(operands[i + 1]);
        if (text === null) {
          refuse(
            'a CMap maps a character code to a value that is not valid Unicode',
            'UNDECODABLE_FONT',
          );
        }
        map.set(keyOf(src.bytes), text);
      }
    } else if (op === 'beginbfrange') {
      for (let i = 0; i + 2 < operands.length; i += 3) {
        const lo = operands[i];
        const hi = operands[i + 1];
        const dst = operands[i + 2];
        if (lo?.type !== 'hexstring' || hi?.type !== 'hexstring') continue;
        if (lo.bytes.length !== hi.bytes.length || lo.bytes.length === 0) continue;
        const start = bytesToNumber(lo.bytes);
        const end = bytesToNumber(hi.bytes);
        if (end < start) continue;
        // A machine-generated CJK table can be enormous. The limit is far
        // above any real mapping and stops a corrupt file allocating until it
        // dies; a range this large is refused rather than truncated.
        if (end - start > 65536) {
          refuse(
            'a CMap declares a character range too large to hold in memory',
            'UNDECODABLE_FONT',
          );
        }
        for (let offset = 0; start + offset <= end; offset++) {
          const codeBytes = addBytes(lo.bytes, offset);
          let text = null;
          if (Array.isArray(dst)) {
            // `[<d0> <d1> ...]` gives each code in the range its own value.
            const item = dst[offset];
            text = item ? destinationToUnicode(item) : null;
            if (text === null) continue; // no entry for this code: not mapped
          } else {
            // `<d0>` is a base value whose final byte is incremented.
            const base = Buffer.from(dst.type === 'hexstring' || dst.type === 'string' ? dst.bytes : []);
            if (base.length === 0) continue;
            const incremented = Buffer.from(base);
            incremented[incremented.length - 1] = (incremented[incremented.length - 1] + offset) & 0xff;
            text = hexToUnicode(incremented);
          }
          if (text === null) {
            refuse(
              'a CMap maps a character range to a value that is not valid Unicode',
              'UNDECODABLE_FONT',
            );
          }
          map.set(keyOf(codeBytes), text);
        }
      }
    }
    // `begincidrange` and `begincidchar` carry no Unicode, so there is nothing
    // to record. The block is consumed and the codes stay unmapped, which the
    // caller treats as unresolvable.
  }
  return { map, ranges };
}

// --- font resolution ---------------------------------------------------------

// A `/Widths` array is present on essentially every embedded font. The
// standard fourteen are the exception: they need metrics the file does not
// carry, and a coarse per-font default is used for those. This affects only
// horizontal spacing and the space-insertion threshold, never a character.
const DEFAULT_FONT_WIDTHS = {
  helvetica: 556, 'helvetica-bold': 556, 'helvetica-oblique': 556,
  'helvetica-boldoblique': 556, arial: 556, 'arial-bold': 556,
  'times-roman': 500, 'times-bold': 500, 'times-italic': 500,
  'times-bolditalic': 500, 'timesnewroman': 500, 'timesnewromanpsmt': 500,
  courier: 600, 'courier-bold': 600, 'courier-oblique': 600, 'courier-boldoblique': 600,
  symbol: 549, zapfdingbats: 760,
};

const subscriptOf = (name) => String(name || '').toLowerCase()
  .replace(/[^a-z0-9]/g, '');

function defaultWidthFor(baseFont) {
  const key = subscriptOf(baseFont);
  for (const [name, width] of Object.entries(DEFAULT_FONT_WIDTHS)) {
    if (key.includes(name)) return width;
  }
  return 500;
}

/**
 * Resolve a font dictionary into something a text-showing operator can use.
 *
 * Resolution happens when a font is first *used* to show text, not when it is
 * declared. A document that ships a font in its resources and never draws a
 * word with it has no encoding to resolve, and refusing on it would be a
 * refusal about something the reader never sees.
 *
 * @throws {PdfRefusalError} UNDECODABLE_FONT
 */
function resolveFont(doc, fontDict, { pageLabel }) {
  const subtype = doc.entry(fontDict, 'Subtype');
  const subtypeName = isName(subtype) ? subtype.name : null;
  const baseFont = doc.entry(fontDict, 'BaseFont');
  const baseName = isName(baseFont) ? baseFont.name : '';

  // A Type 3 font draws its glyphs as content streams, so there is no code to
  // Unicode mapping to look up. The characters are genuinely not recoverable
  // without interpreting the glyph procedures, which this extractor does not do.
  if (subtypeName === 'Type3') {
    refuse(
      `a Type 3 font (${baseName || 'unnamed'}) draws its letters as images of code, so its text cannot be read`,
      'UNDECODABLE_FONT',
      { font: baseName, subtype: 'Type3', page: pageLabel },
    );
  }

  // `/ToUnicode` is authoritative when present. It is what the producer of the
  // file itself used to say the codes mean.
  const toUnicodeRef = doc.entry(fontDict, 'ToUnicode');
  let toUnicode = null;
  let ranges = [];
  if (toUnicodeRef && isStream(toUnicodeRef)) {
    const parsed = parseCMap(doc.decodeStream(toUnicodeRef, { purpose: 'ToUnicode CMap' }));
    toUnicode = parsed.map;
    ranges = parsed.ranges;
  }

  if (subtypeName === 'Type0') {
    return resolveCompositeFont(doc, fontDict, { baseName, toUnicode, ranges, pageLabel });
  }
  return resolveSimpleFont(doc, fontDict, { baseName, toUnicode, ranges, pageLabel });
}

const isSymbolicFont = (flags) => flags !== null && (flags & 0x4) !== 0 && (flags & 0x20) === 0;

function descriptorFlags(doc, fontDict) {
  const descriptor = doc.entry(fontDict, 'FontDescriptor');
  const flags = descriptor ? doc.entry(descriptor, 'Flags') : undefined;
  return typeof flags === 'number' ? flags : null;
}

/** A one-byte-code font: an encoding table of glyph names, or a `/ToUnicode`. */
function resolveSimpleFont(doc, fontDict, { baseName, toUnicode, ranges = [], pageLabel }) {
  const first = doc.entry(fontDict, 'FirstChar');
  const widths = doc.entry(fontDict, 'Widths');
  const descriptor = doc.entry(fontDict, 'FontDescriptor');
  const missing = descriptor ? doc.entry(descriptor, 'MissingWidth') : undefined;
  const flags = descriptorFlags(doc, fontDict);
  const symbolic = isSymbolicFont(flags);

  const widthAt = (code) => {
    if (Array.isArray(widths) && typeof first === 'number') {
      const value = widths[code - first];
      if (typeof value === 'number') return value;
    }
    if (typeof missing === 'number') return missing;
    return defaultWidthFor(baseName);
  };

  // Build the code -> glyph name table: a base encoding, then `/Differences`.
  const encoding = doc.entry(fontDict, 'Encoding');
  let table;
  if (isName(encoding)) {
    table = new Map(ENCODINGS[encoding.name] || ENCODINGS.StandardEncoding);
  } else if (isDict(encoding)) {
    const base = doc.entry(encoding, 'BaseEncoding');
    table = new Map(ENCODINGS[isName(base) ? base.name : 'StandardEncoding'] || ENCODINGS.StandardEncoding);
    const differences = doc.entry(encoding, 'Differences');
    if (Array.isArray(differences)) {
      // The array is a run of names, with an integer restarting the run at a
      // new code. The counter advances only after a name is consumed: a number
      // *is* the code, so advancing past it would shift every following glyph
      // by one and turn correct text into garbage that still looks like text.
      let code = 0;
      for (const item of differences) {
        const value = doc.resolve(item);
        if (typeof value === 'number') { code = value; continue; }
        if (isName(value)) { table.set(code, value.name); code++; }
      }
    }
  } else {
    // No `/Encoding` at all. A descriptor that says the font is symbolic means
    // the codes are glyph indices with no meaning this extractor can recover;
    // a non-symbolic font falls back to StandardEncoding, which is what the
    // specification defines for that case.
    if (symbolic && !toUnicode) {
      refuse(
        `the font ${baseName || '(unnamed)'} is symbolic and carries no character mapping, so its text cannot be read`,
        'UNDECODABLE_FONT',
        { font: baseName, page: pageLabel, reason: 'symbolic without ToUnicode' },
      );
    }
    table = new Map(ENCODINGS.StandardEncoding);
  }

  // A symbolic font's `/Widths` is indexed by the font's own code space and is
  // frequently absent or meaningless, so the space width falls back to a
  // quarter em. This affects the space-insertion threshold, never a character.
  const spaceWidth = !symbolic && table.has(32) ? widthAt(32) : defaultWidthFor(baseName) * 0.25;

  return {
    kind: 'simple',
    baseName,
    page: pageLabel,
    table,
    toUnicode,
    widthAt,
    spaceWidth,
    /**
     * Resolve one byte to text, or null when it cannot be resolved.
     *
     * When a `/ToUnicode` is present it is used on its own. A code it omits
     * stays unresolvable rather than falling back to the encoding table: if the
     * producer wrote a mapping at all, that mapping is the authority, and
     * reading a different table for the codes it happens to skip is how a
     * partly-wrong decode comes to look wholly right. The key is formed against
     * the CMap's declared codespace for the same reason; see `toUnicodeKeys`.
     */
    decode(code) {
      if (toUnicode) {
        for (const key of toUnicodeKeys(code, ranges)) {
          const mapped = toUnicode.get(key);
          if (mapped !== undefined) return mapped;
        }
        return null;
      }
      const name = table.get(code);
      if (name === undefined) return null;
      return glyphToUnicode(name);
    },
  };
}

/** A composite font: an encoding CMap, a CID descendant, and glyph widths. */
function resolveCompositeFont(doc, fontDict, { baseName, toUnicode, ranges, pageLabel }) {
  const encoding = doc.entry(fontDict, 'Encoding');
  const encodingName = isName(encoding) ? encoding.name
    : isStream(encoding) && isName(doc.entry(encoding, 'CMapName')) ? doc.entry(encoding, 'CMapName').name
      : null;

  // Identity-H and Identity-V are predefined and name no mapping: the codes
  // are glyph indices, and only `/ToUnicode` can turn them into text.
  if (encodingName === 'Identity-V') {
    refuse(
      'the document sets text vertically, so its lines are not lines and cannot be numbered honestly',
      'MALFORMED',
      { writing: 'vertical', font: baseName, page: pageLabel },
    );
  }

  const descendants = doc.entry(fontDict, 'DescendantFonts');
  const descendant = Array.isArray(descendants) ? doc.resolve(descendants[0]) : undefined;
  if (!isDict(descendant)) {
    refuse(
      'a composite font has no readable descendant font, so its text cannot be read',
      'UNDECODABLE_FONT',
      { font: baseName, page: pageLabel },
    );
  }
  const defaultWidth = doc.entry(descendant, 'DW');
  const widthsRaw = doc.entry(descendant, 'W');

  // `/W` is a run-length table: `c [w...] cfirst clast w ...`.
  const widths = new Map();
  if (Array.isArray(widthsRaw)) {
    let i = 0;
    while (i < widthsRaw.length) {
      const first = doc.resolve(widthsRaw[i]);
      if (Array.isArray(first)) {
        const start = doc.resolve(widthsRaw[i - 1]);
        if (typeof start === 'number') {
          first.forEach((w, k) => {
            const value = doc.resolve(w);
            if (typeof value === 'number') widths.set(start + k, value);
          });
        }
        i += 1;
        continue;
      }
      const last = doc.resolve(widthsRaw[i + 1]);
      const value = doc.resolve(widthsRaw[i + 2]);
      if (typeof first === 'number' && typeof last === 'number' && typeof value === 'number') {
        for (let c = first; c <= last && c - first < 65536; c++) widths.set(c, value);
      }
      i += 3;
    }
  }

  const dw = typeof defaultWidth === 'number' ? defaultWidth : 1000;
  const spaceWidth = widths.get(32) ?? dw * 0.25;

  // An embedded encoding CMap supplies the codespace and may itself carry
  // Unicode mappings. It is read when present; the predefined CMaps are not.
  let effective = ranges;
  let embedded = null;
  if (isStream(encoding)) {
    const parsed = parseCMap(doc.decodeStream(encoding, { purpose: 'font encoding CMap' }));
    if (parsed.map.size) embedded = parsed.map;
    if (parsed.ranges.length && !effective.length) effective = parsed.ranges;
  }
  if (!toUnicode && !embedded) {
    // A CID font with no Unicode source at all: its codes are glyph indices
    // and nothing in the file says what they stand for.
    refuse(
      `the font ${baseName || '(unnamed)'} stores glyph indices with no character mapping, so its text cannot be read`,
      'UNDECODABLE_FONT',
      { font: baseName, page: pageLabel, reason: 'composite without ToUnicode' },
    );
  }
  // With no codespace of its own, the predefined two-byte form applies.
  if (!effective.length) effective = [{ lo: 0, hi: 0xffff, length: 2 }];
  const byLength = [...new Set(effective.map((r) => r.length))].sort((a, b) => a - b);
  const lookup = toUnicode || embedded;

  return {
    kind: 'composite',
    baseName,
    page: pageLabel,
    // A vertical composite font already refused above; this flag only tells
    // the text-showing path which path it is on.
    vertical: false,
    toUnicode: lookup,
    spaceWidth,
    codeLengths: byLength,
    widthAt: (code) => widths.get(code) ?? dw,

    /**
     * Split a string into character codes using the codespace ranges.
     *
     * The codespace bounds both the length and the value, so a stream may mix
     * one-byte and two-byte codes. A byte that starts no declared range is an
     * unresolvable sequence, and returns null so the caller refuses rather than
     * guessing a length and decoding nonsense.
     */
    split(bytes) {
      const out = [];
      let i = 0;
      while (i < bytes.length) {
        let chosen = null;
        for (const length of this.codeLengths) {
          if (i + length > bytes.length) continue;
          const slice = bytes.subarray(i, i + length);
          const value = bytesToNumber(slice);
          if (effective.some((r) => r.length === length && value >= r.lo && value <= r.hi)) {
            chosen = { slice, value };
            break;
          }
        }
        if (!chosen) return null;
        out.push({ code: chosen.slice.toString('latin1'), value: chosen.value });
        i += chosen.slice.length;
      }
      return out;
    },

    /**
     * Resolve one code to text, or null when it cannot be resolved.
     *
     * The code is the value the encoding is indexed by: a byte for a simple
     * font, and a byte string for a composite one, whose codes are longer than
     * a byte.
     */
    decode(code) {
      const mapped = this.toUnicode.get(keyOf(Buffer.from(code, 'latin1')));
      return mapped === undefined ? null : mapped;
    },
  };
}

// --- content stream interpretation -------------------------------------------

const mul = (m, n) => [
  m[0] * n[0] + m[1] * n[2], m[0] * n[1] + m[1] * n[3],
  m[2] * n[0] + m[3] * n[2], m[2] * n[1] + m[3] * n[3],
  m[4] * n[0] + m[5] * n[2] + n[4], m[4] * n[1] + m[5] * n[3] + n[5],
];

const IDENTITY = [1, 0, 0, 1, 0, 0];

/** The translation of a matrix: where the text origin lands on the page. */
const originOf = (m) => ({ x: m[4], y: m[5] });

/**
 * Walk one content stream, calling `onText` for every shown string and
 * `onImage` for every image drawn. Operators this extractor does not act on
 * are consumed and ignored, because a content stream legitimately contains
 * hundreds of them and refusing on `re` would refuse every real document.
 */
function runContentStream(doc, data, state, onText, onImage, { depth = 0 } = {}) {
  if (depth > 12) return; // a form that includes itself
  const lex = new Lexer(Buffer.isBuffer(data) ? data : Buffer.from(data));
  const stack = [];

  for (;;) {
    const token = lex.next();
    if (!token) break;
    if (token.type === 'arrayOpen') {
      // The array is read here, while the lexer is still on it. Reading it
      // after the closing operator is seen would take the tokens belonging to
      // the *next* operator, so every `TJ` would be given the wrong strings and
      // the document would decode to confident nonsense.
      stack.push({ type: 'array', items: readArrayItems(lex) });
      if (stack.length > 64) stack.splice(0, stack.length - 64);
      continue;
    }
    if (token.type !== 'keyword') {
      stack.push(token);
      if (stack.length > 64) stack.splice(0, stack.length - 64);
      continue;
    }
    const op = token.value;
    const operands = stack;
    const n = (i) => {
      const t = operands[operands.length + i];
      return t && t.type === 'num' ? t.value : 0;
    };
    const i = (k) => (operands[operands.length - k] || null);

    switch (op) {
      case 'q': state.gstack.push(state.snapshot()); break;
      case 'Q': {
        const saved = state.gstack.pop();
        if (saved) state.restore(saved);
        break;
      }
      case 'cm': {
        const m = [n(-6), n(-5), n(-4), n(-3), n(-2), n(-1)];
        state.ctm = mul(m, state.ctm);
        break;
      }
      case 'BT':
        state.tm = IDENTITY.slice();
        state.tlm = IDENTITY.slice();
        break;
      case 'ET': break;
      case 'Tf': {
        const fontToken = i(2);
        const sizeToken = i(1);
        state.fontSize = sizeToken && sizeToken.type === 'num' ? sizeToken.value : state.fontSize;
        if (fontToken && fontToken.type === 'name') {
          state.font = state.lookupFont(fontToken.name);
        }
        break;
      }
      case 'Td': {
        const line = [1, 0, 0, 1, n(-2), n(-1)];
        state.tlm = mul(line, state.tlm);
        state.tm = state.tlm.slice();
        break;
      }
      case 'TD': {
        state.leading = -n(-1);
        const line = [1, 0, 0, 1, n(-2), n(-1)];
        state.tlm = mul(line, state.tlm);
        state.tm = state.tlm.slice();
        break;
      }
      case 'Tm': {
        state.tlm = [n(-6), n(-5), n(-4), n(-3), n(-2), n(-1)];
        state.tm = state.tlm.slice();
        break;
      }
      case 'T*': {
        state.nextLine();
        break;
      }
      case 'TL': state.leading = n(-1); break;
      case 'Tc': state.charSpacing = n(-1); break;
      case 'Tw': state.wordSpacing = n(-1); break;
      case 'Tz': state.horizontalScale = n(-1) / 100; break;
      case 'Ts': state.rise = n(-1); break;
      case 'Tj': {
        const s = i(1);
        // Both string forms carry the same bytes. A hex string `<01020303>` is
        // not a lesser kind of string, and accepting only `(literal)` here
        // silently drops every word written in hex — which is a large share of
        // real content streams, and a document that then reads as empty.
        if (s && (s.type === 'string' || s.type === 'hexstring')) onText(s.bytes, []);
        break;
      }
      case "'": {
        state.nextLine();
        const s = i(1);
        if (s && (s.type === 'string' || s.type === 'hexstring')) onText(s.bytes, []);
        break;
      }
      case '"': {
        state.wordSpacing = n(-3);
        state.charSpacing = n(-2);
        state.nextLine();
        const s = i(1);
        if (s && (s.type === 'string' || s.type === 'hexstring')) onText(s.bytes, []);
        break;
      }
      case 'TJ': {
        const arr = i(1);
        if (!arr || arr.type !== 'array') break;
        onText(null, arr.items);
        break;
      }
      case 'Do': {
        const xobjName = i(1);
        if (xobjName && xobjName.type === 'name') onImage(xobjName.name);
        break;
      }
      case 'BI': skipInlineImage(lex); break;
      default: break;
    }
    stack.length = 0;
  }
}

/**
 * Read the elements of a `[ ... ]` array. Called with the lexer sitting just
 * after the opening bracket, so the array is read in place.
 */
function readArrayItems(lex) {
  const items = [];
  for (;;) {
    const token = lex.next();
    if (!token) break;
    if (token.type === 'arrayClose' || token.type === 'keyword') {
      // A keyword ends the array only if the array was already closed; a
      // malformed stream is stepped over rather than swallowing the operator
      // that follows it.
      if (token.type === 'arrayClose') break;
      break;
    }
    if (token.type === 'arrayOpen') {
      items.push({ type: 'array', items: readArrayItems(lex) });
      continue;
    }
    items.push(token);
  }
  return items;
}

/** An inline image runs to `EI`; its binary must not be tokenised as operators. */
function skipInlineImage(lex) {
  const marker = Buffer.from('EI', 'latin1');
  for (;;) {
    const at = lex.buf.indexOf(marker, lex.pos, 'latin1');
    if (at < 0) { lex.pos = lex.end; return; }
    // `EI` must be a token on its own, so the byte before it is whitespace and
    // the byte after is whitespace or the end of the stream.
    const before = lex.buf[at - 1];
    const after = lex.buf[at + 2];
    const clean = (before === undefined || before <= 0x20)
      && (after === undefined || after <= 0x20);
    if (clean) { lex.pos = at + 2; return; }
    lex.pos = at + 2;
  }
}

// --- reading order -----------------------------------------------------------

// Two columns is the only layout this extractor reconstructs deliberately, and
// the constants below are the whole of the heuristic. A page is treated as
// two-column when its text runs split into two groups on x with a gutter
// between them that neither group crosses, and each group is at least this
// fraction of the page's text. The thresholds are deliberately conservative:
// a wrong column split reorders every line in the document, so the evidence
// has to be clear before one is applied.
const GUTTER_MIN_FRACTION = 0.015;   // of page width
const COLUMN_MIN_FRACTION = 0.18;    // of runs, per side
const FULL_WIDTH_FRACTION = 0.68;    // of page width, for a spanning line
const MAX_INDENT_COLUMNS = 1000;     // bounds the reconstructed source

/**
 * Group runs into visual lines and order them.
 *
 * A line is the set of runs sharing a baseline: they are clustered on `y`
 * within a tolerance scaled to the type size, because a document with a
 * footnote marker or a superscript has baselines a fraction of a point apart
 * and a fixed tolerance would split one line in two. Within a line, runs are
 * ordered by `x`, which is what makes a two-column line read left to right.
 *
 * @returns {Array<{ y: number, x: number, runs: Array<object>, page: number }>}
 */
function groupIntoLines(runs) {
  if (!runs.length) return [];
  const sizes = runs.map((r) => Math.abs(r.fontSize) || 10).sort((a, b) => a - b);
  const median = sizes[Math.floor(sizes.length / 2)] || 10;
  const tolerance = Math.max(0.6, median * 0.28);

  const sorted = [...runs].sort((a, b) => (b.y - a.y) || (a.x - b.x));
  const lines = [];
  for (const run of sorted) {
    const last = lines[lines.length - 1];
    if (last && Math.abs(last.y - run.y) <= tolerance) {
      last.runs.push(run);
      // Keep the line's own baseline as the mean, so a line with a tall
      // capital and a low x-height still groups as one.
      last.y = last.runs.reduce((sum, r) => sum + r.y, 0) / last.runs.length;
      last.x = Math.min(last.x, run.x);
    } else {
      lines.push({ y: run.y, x: run.x, runs: [run], page: run.page });
    }
  }
  for (const line of lines) {
    line.runs.sort((a, b) => a.x - b.x);
    line.minX = Math.min(...line.runs.map((r) => r.x));
    line.maxX = Math.max(...line.runs.map((r) => r.endX));
  }
  return lines;
}

/**
 * Decide whether a page is two-column, and if so return the x that separates
 * the two. Only lines that do not already span the measure vote: a full-width
 * title says nothing about where the columns are, and letting it vote is how
 * a single-column page gets split down the middle.
 */
function detectColumnSplit(lines, pageWidth) {
  const spanning = pageWidth * FULL_WIDTH_FRACTION;

  // Take part only in runs that do not already cross the measure. A full-width
  // title is one run spanning the whole page: it covers the gutter and hides it,
  // and it says nothing about where the columns are, so letting it vote is how a
  // single-column page gets split down the middle.
  //
  // The test is per run, not per line, which is what the description above
  // already said — the two columns of a page share a baseline, so such a line
  // spans the measure while neither of its two runs does. Filtering on the line
  // excluded every line of a two-column page, so the gutter was never looked
  // for and no such page was ever split. The sample floor counts runs for the
  // same reason: `COLUMN_MIN_FRACTION` below counts runs, so one unit is used
  // throughout, and a page whose columns share baselines is not held to a floor
  // in lines that it meets only twice over.
  const runs = [];
  for (const line of lines) {
    for (const run of line.runs) {
      if (run.endX - run.x >= spanning) continue;
      runs.push(run);
    }
  }
  if (runs.length < 6) return null;

  // A gutter is a band of x that no run covers. Finding the widest such band
  // inside the page's text extent, and checking that runs sit on both sides of
  // it, is a statement about the geometry rather than about the text.
  const left = Math.min(...runs.map((run) => run.x));
  const right = Math.max(...runs.map((run) => run.endX));
  const width = right - left;
  if (width <= 0) return null;

  // Sample the covered x intervals and find the largest contiguous gap.
  const events = [];
  for (const run of runs) { events.push([run.x, 1], [run.endX, -1]); }
  events.sort((a, b) => a[0] - b[0]);
  let bestGap = 0;
  let bestAt = null;
  let cover = 0;
  let prev = null;
  for (const [x, delta] of events) {
    if (prev !== null && cover === 0 && x - prev > bestGap) { bestGap = x - prev; bestAt = (x + prev) / 2; }
    cover += delta;
    prev = x;
  }
  if (bestAt === null || bestGap < pageWidth * GUTTER_MIN_FRACTION) return null;

  const leftRuns = runs.filter((run) => run.endX <= bestAt).length;
  const rightRuns = runs.filter((run) => run.x >= bestAt).length;
  const total = leftRuns + rightRuns;
  if (!total) return null;
  if (leftRuns < total * COLUMN_MIN_FRACTION || rightRuns < total * COLUMN_MIN_FRACTION) return null;
  return bestAt;
}

/**
 * Order a page's lines for reading, and split the ones the gutter runs through.
 *
 * A line at one baseline in a two-column page is two lines. An index page draws
 * "2xx Successful Status Codes, 38" at the left margin and "Basic and Digest"
 * at the top of the right column on the *same* baseline, and joining them
 * produces one line reading "2xx Successful Status Codes, 38 Basic and
 * Digest" — a sentence that merges two unrelated entries and puts a false line
 * number on both. So when a gutter is found, any line that straddles it becomes
 * two lines, one per column, before anything is ordered.
 *
 * Single column: top to bottom, nothing else.
 *
 * Two columns: the page is read as a sequence of bands. A line spanning the
 * measure — a title, a full-width figure caption — is a boundary; the columns
 * of copy above or below it are read together, left column then right column,
 * and then the spanning line. That is the order a reader of a journal article
 * uses, and it is the only ordering that puts a page's sentences in the
 * sequence a person reads them in.
 */
function orderLines(lines, split) {
  if (split === null) return lines;

  // Split every line that runs through the gutter into a per-column pair. A
  // line entirely on one side is left alone.
  const prepared = [];
  for (const line of lines) {
    const straddles = line.runs.some((r) => r.x < split) && line.runs.some((r) => r.endX > split);
    if (!straddles || line.spansMeasure) { prepared.push({ line, spans: false }); continue; }
    const left = line.runs.filter((r) => r.x < split);
    const right = line.runs.filter((r) => r.endX > split);
    const side = (runs) => {
      const runs2 = [...runs].sort((a, b) => a.x - b.x);
      return {
        y: line.y,
        x: Math.min(...runs2.map((r) => r.x)),
        runs: runs2,
        page: line.page,
        minX: Math.min(...runs2.map((r) => r.x)),
        maxX: Math.max(...runs2.map((r) => r.endX)),
      };
    };
    if (left.length) prepared.push({ line: side(left), spans: false });
    if (right.length) prepared.push({ line: side(right), spans: false });
  }

  const out = [];
  let block = [];
  const flush = () => {
    if (!block.length) return;
    const left = block.filter((l) => l.minX < split).sort((a, b) => b.y - a.y);
    const right = block.filter((l) => l.minX >= split).sort((a, b) => b.y - a.y);
    out.push(...left, ...right);
    block = [];
  };
  for (const entry of prepared) {
    if (entry.line.spansMeasure) { flush(); out.push(entry.line); continue; }
    block.push(entry.line);
  }
  flush();
  return out;
}

// --- text reconstruction -----------------------------------------------------

/**
 * The device-space scale on the vertical axis, needed to turn the text rise
 * and a font size in text space into points on the page.
 */
const yScaleOf = (m) => Math.hypot(m[2], m[3]) || 1;

/**
 * Decide whether a horizontal gap between two text runs is a word space.
 *
 * This is the single heuristic in the reconstruction, and it is where a PDF
 * differs most from a text file. A producer either draws the space as a real
 * glyph — code 32, which needs no inference — or leaves a gap by moving the
 * text position, which does. The two cases are told apart by measuring the
 * document rather than by taste.
 *
 * Measured over RFC 2616, which is typeset with both literal space glyphs and
 * position gaps, the 3563 gaps between adjacent runs on a shared baseline fall
 * into three groups:
 *
 *   - 3011 at or below zero, where the runs touch or overlap. These are one
 *     phrase continuing — "The " before "TEXT", "An empty " before
 *     "abs_path" — and the space is already drawn in the text.
 *   - 450 at or above half a space width, where the runs are plainly separate
 *     items.
 *   - 102 in between, and these are the ones a naive half-space threshold
 *     throws away: a section number and its heading, "3.2.1" then "General
 *     Syntax", separated by 0.44 of a space. Dropping the space there yields
 *     "3.2.1General Syntax", which is not a heading any reader would recognise.
 *
 * So the threshold sits well below half a space, at 0.15, which clears every
 * separated-item case in the measurement while staying clear of the zero group
 * where runs merely abut. The 0.15 of a space also has a hard floor of 0.05
 * points so that floating-point noise between two runs that touch is not read
 * as a gap. Two further guards in `joinLineRuns` cover the common case: a run
 * that already ends in a space, or already begins with one, never gains
 * another.
 */
const WORD_GAP_FRACTION = 0.15;
const WORD_GAP_FLOOR_POINTS = 0.05;

function isWordGap(gap, spaceWidth) {
  if (!(spaceWidth > 0)) return gap > WORD_GAP_FLOOR_POINTS;
  return gap > Math.max(spaceWidth * WORD_GAP_FRACTION, WORD_GAP_FLOOR_POINTS);
}

// --- the extractor -----------------------------------------------------------

/**
 * Extract the text of a PDF as the contract's `Unit[]`.
 *
 * @param {Buffer} bytes raw file contents
 * @param {string} filePath
 * @param {object} [options] `{ starts }` accepted for signature parity; the
 *   reconstructed source is built here, so caller-supplied line starts do not
 *   apply to a PDF.
 * @returns {object[]} units
 * @throws {PdfRefusalError}
 */
export function extractPdfText(bytes, filePath, { starts = null } = {}) {
  void starts; // a PDF's lines are reconstructed, not read from the file bytes
  const doc = openPdf(bytes);
  const pages = doc.pages();
  const allLines = [];
  let sawImage = false;

  for (let pageIndex = 0; pageIndex < pages.length; pageIndex++) {
    const page = pages[pageIndex];
    const pageNumber = pageIndex + 1;
    const { width, height, rotation, originX, originY } = pageGeometry(doc, page);

    const { text: runs, images } = pageRuns(doc, page, {
      pageNumber, width, height, rotation, originX, originY,
    });
    if (images > 0) sawImage = true;
    if (!runs.length) continue;

    const lines = groupIntoLines(runs);
    const split = detectColumnSplit(lines, width);
    // A line carrying one run across the whole measure is a band boundary, not
    // a line to split: a title across a two-column page really is one line of
    // text. The test is per run, as in `detectColumnSplit`, because a line made
    // of two column runs also spans the measure while being exactly what must
    // be split — calling it a title left both columns joined on one line.
    const spanning = width > 0 ? width * FULL_WIDTH_FRACTION : Infinity;
    for (const line of lines) {
      const fullWidth = line.runs.some((run) => run.endX - run.x >= spanning);
      line.spansMeasure = split !== null && fullWidth;
    }
    const ordered = orderLines(lines, split);
    for (const line of ordered) allLines.push({ ...line, pageNumber });
  }

  if (!allLines.length) {
    // Nothing to read. An image-bearing page means the document is a scan and
    // the honest answer is a refusal; a document with neither text nor images
    // is the PDF equivalent of an empty text file, which the rest of the tool
    // already handles by producing no units.
    if (sawImage) {
      refuse(
        'no extractable text; the document appears to be scanned images',
        'SCANNED',
      );
    }
    return [];
  }

  return unitsFromLines(allLines, filePath);
}

/** The page box, rotation and user unit, normalised to a top-left origin. */
function pageGeometry(doc, page) {
  const box = doc.entry(page, 'MediaBox');
  let x0 = 0; let y0 = 0; let x1 = 612; let y1 = 792;
  if (Array.isArray(box) && box.length === 4) {
    const values = box.map((v) => doc.resolve(v)).map(Number);
    if (values.every((v) => Number.isFinite(v))) {
      x0 = Math.min(values[0], values[2]);
      y0 = Math.min(values[1], values[3]);
      x1 = Math.max(values[0], values[2]);
      y1 = Math.max(values[1], values[3]);
    }
  }
  const rotateRaw = doc.entry(page, 'Rotate');
  const rotation = ((typeof rotateRaw === 'number' ? Math.floor(rotateRaw / 90) * 90 : 0) % 360 + 360) % 360;
  const userUnitRaw = doc.entry(page, 'UserUnit');
  const userUnit = typeof userUnitRaw === 'number' && userUnitRaw > 0 ? userUnitRaw : 1;
  return {
    width: (x1 - x0) * userUnit,
    height: (y1 - y0) * userUnit,
    rotation,
    originX: x0 * userUnit,
    originY: y0 * userUnit,
  };
}

/**
 * Collect the text runs of one page, following form XObjects.
 *
 * A form XObject is a content stream of its own with its own resources and its
 * own matrix, and it may sit inside any operator's operand list. Text inside
 * one is real copy and is extracted with the matrix applied; an image XObject
 * is noted so a page made only of images can be recognised as a scan.
 */
function pageRuns(doc, page, geometry) {
  const runs = [];
  // Image markers are counted, never placed in the text-run list. They carry no
  // position, and a position-less entry in that list sorts to NaN and takes a
  // whole line of real text down with it.
  let imageCount = 0;
  const { pageNumber } = geometry;
  const pageResources = doc.entry(page, 'Resources');

  const makeState = (resources, ctm) => ({
    ctm: ctm || IDENTITY.slice(),
    tm: IDENTITY.slice(),
    tlm: IDENTITY.slice(),
    fontSize: 0,
    leading: 0,
    charSpacing: 0,
    wordSpacing: 0,
    horizontalScale: 1,
    rise: 0,
    font: null,
    resources,
    gstack: [],
    nextLine() {
      const shift = [1, 0, 0, 1, 0, -this.leading];
      this.tlm = mul(shift, this.tlm);
      this.tm = this.tlm.slice();
    },
    snapshot() {
      return {
        ctm: this.ctm.slice(), tm: this.tm.slice(), tlm: this.tlm.slice(),
        fontSize: this.fontSize, leading: this.leading, charSpacing: this.charSpacing,
        wordSpacing: this.wordSpacing, horizontalScale: this.horizontalScale,
        rise: this.rise, font: this.font, resources: this.resources,
      };
    },
    restore(saved) {
      this.ctm = saved.ctm.slice(); this.tm = saved.tm.slice(); this.tlm = saved.tlm.slice();
      this.fontSize = saved.fontSize; this.leading = saved.leading;
      this.charSpacing = saved.charSpacing; this.wordSpacing = saved.wordSpacing;
      this.horizontalScale = saved.horizontalScale; this.rise = saved.rise;
      this.font = saved.font; this.resources = saved.resources;
    },
    lookupFont(name) {
      const fonts = resources && doc.entry(resources, 'Font');
      const entry = fonts ? doc.entry(fonts, name) : undefined;
      if (!isDict(entry)) {
        // A text-showing operator with an unknown font is a document whose text
        // cannot be read. Refusing is the only safe answer: decoding with a
        // substitute would be inventing characters.
        refuse(
          `the page names a font (${name}) that is not in its resources, so its text cannot be read`,
          'UNDECODABLE_FONT',
          { font: name, page: pageNumber },
        );
      }
      return resolveFont(doc, entry, { pageLabel: pageNumber });
    },
  });

  const onText = (bytes, items, state) => {
    if (!state.font) return; // text with no font selected draws nothing readable
    const font = state.font;

    const size = Math.abs(state.fontSize) || 10;
    const th = state.horizontalScale;
    const device = mul(state.tm, state.ctm);
    const { x: startX, y: baseY } = originOf(device);
    const yScale = yScaleOf(state.ctm) * size;
    const y = baseY + state.rise * yScale;

    // The horizontal scale of the text matrix on the page. Text advances are
    // expressed in text-space units, so every threshold below is multiplied by
    // this to become a distance in points, which is what `x` is measured in.
    const advanceScale = (Math.hypot(state.tm[0], state.tm[1]) || 1)
      * (Math.hypot(state.ctm[0], state.ctm[1]) || 1);
    const spacePoints = (font.spaceWidth / 1000) * size * th * advanceScale;

    // `state.tm` is advanced by the text-showing operators, so the origin is
    // read before the string is shown and the scale is captured at the same
    // moment, while the matrix still describes this string's own placement.
    const emit = (rawBytes) => {
      const matrix = state.tm.slice();
      const origin = originOf(mul(matrix, state.ctm));
      const scale = Math.hypot(matrix[0], matrix[1]) || 1;
      const result = showString(font, rawBytes, state, size, th);
      state.tm = mul([1, 0, 0, 1, result.width, 0], state.tm);
      return { text: result.text, endX: origin.x + result.width * scale };
    };

    let text = '';
    if (bytes) {
      text = emit(bytes).text;
    } else {
      // A `TJ` array interleaves strings with displacement numbers. The numbers
      // are in thousandths of an em: a positive one moves right, and a wide
      // one is a space the producer chose to leave rather than to draw.
      for (const item of items) {
        if (item.type === 'string' || item.type === 'hexstring') {
          text += emit(item.bytes).text;
          continue;
        }
        if (item.type === 'num') {
          // The specification *subtracts* a `TJ` number from the horizontal
          // coordinate, so a negative number moves the text to the right and a
          // positive one to the left. That inversion is easy to get backwards,
          // and getting it backwards does not merely shift a run: every gap
          // where the producer left a word space reads as a leftward kern, so
          // no space is inserted and the words of a sentence run together.
          const shiftRight = (-item.value / 1000) * size * th * advanceScale;
          if (isWordGap(shiftRight, spacePoints) && !/\s$/.test(text)) text += ' ';
          // The displacement is applied whatever its size, because it is what
          // positions the next string on the line.
          state.tm = mul([1, 0, 0, 1, shiftRight / advanceScale, 0], state.tm);
        }
      }
    }

    if (!text.trim()) return;

    // A run is placed in reading coordinates rather than in page coordinates.
    //
    // Most text runs left to right and the coordinates need no help. Some is
    // rotated: the version stamp down the side of a preprint is drawn through
    // a form XObject with a quarter-turn matrix, so its glyphs advance upward
    // on the page while the reader reads it as a line across the top. Left in
    // page coordinates each glyph of such a line gets its own baseline, the
    // line is shredded, and the document reports one "line" per letter.
    //
    // The direction the text advances in is read from the text matrix, and a
    // run advancing vertically is turned a quarter turn so it advances to the
    // right. The turn is applied to the position as well, which is what keeps
    // the rotated block in the right place on the page instead of mirroring it
    // across the diagonal. Angles other than a right angle are not expected in
    // real documents and are left alone rather than guessed at.
    const dx = state.tm[0];
    const dy = state.tm[1];
    let px = startX;
    let py = y;
    let endPointX = originOf(mul(state.tm, state.ctm)).x;
    if (Math.abs(dy) > Math.abs(dx)) {
      if (dy > 0) {
        // Advancing upward: turn clockwise a quarter so it runs right.
        [px, py] = [y, -startX];
        endPointX = -endPointX;
      } else {
        // Advancing downward: turn the other way.
        [px, py] = [-y, startX];
        endPointX = -endPointX;
      }
    }
    const finalOrigin = originOf(mul(state.tm, state.ctm));
    let endX = endPointX;
    if (Math.abs(dy) > Math.abs(dx)) endX = (dy > 0 ? -finalOrigin.y : finalOrigin.y);

    runs.push({
      text, x: px, y: py, endX, fontSize: size, page: pageNumber,
      spaceWidth: spacePoints,
    });
  };

  const walk = (contentBytes, resources, ctm, depth) => {
    const state = makeState(resources, ctm);
    runContentStream(doc, contentBytes, state,
      (bytes, items) => onText(bytes, items, state),
      (name) => {
        const xobjects = resources ? doc.entry(resources, 'XObject') : undefined;
        const xobj = xobjects ? doc.entry(xobjects, name) : undefined;
        if (!isDict(xobj) || !isStream(xobj)) return;
        const subtype = doc.entry(xobj, 'Subtype');
        if (isName(subtype) && subtype.name === 'Form') {
          if (depth >= 6) return;
          const formResources = doc.entry(xobj, 'Resources') || resources;
          const matrix = doc.entry(xobj, 'Matrix');
          const m = Array.isArray(matrix) && matrix.length === 6
            ? matrix.map((v) => doc.resolve(v)).map(Number)
            : IDENTITY;
          let data;
          try {
            data = doc.decodeStream(xobj, { purpose: 'form XObject' });
          } catch (error) {
            if (error instanceof PdfRefusalError) throw error;
            return;
          }
          walk(data, formResources, mul(m, state.ctm), depth + 1);
          return;
        }
        imageCount++;
      },
      { depth });
  };

  const contents = doc.entry(page, 'Contents');
  const list = Array.isArray(contents) ? contents.map((c) => doc.resolve(c)) : [contents];
  const chunks = [];
  for (const item of list) {
    if (!isDict(item) || !isStream(item)) continue;
    chunks.push(doc.decodeStream(item, { purpose: 'content stream' }));
  }
  if (chunks.length) {
    // The parts of a content stream array are one stream: whitespace between
    // them keeps a token from one part from joining one in the next.
    walk(Buffer.concat(chunks), pageResources, IDENTITY.slice(), 0);
  }

  return { text: runs, images: imageCount };
}

/**
 * Turn a shown string into text plus the horizontal advance it causes.
 *
 * The advance matters as much as the text: it is what positions the next
 * string on the same line, so an error here silently moves every later run on
 * that line. The formula is the specification's,
 * `(w0/1000 * fontSize + charSpacing + wordSpacing) * horizontalScale` per
 * character, with `wordSpacing` applying only to a single-byte code 32.
 *
 * A code that cannot be resolved refuses the whole document. That is the one
 * place where a wrong answer cannot be argued away.
 */
function showString(font, bytes, state, size, th) {
  let text = '';
  let width = 0;
  const charSpacing = state.charSpacing;
  const wordSpacing = state.wordSpacing;

  const parts = font.kind === 'simple'
    ? [...bytes].map((b) => ({ code: b, space: b === 32 }))
    : font.split(bytes);
  if (parts === null) {
    refuse(
      'a string in the content stream does not match any character code the font defines',
      'UNDECODABLE_FONT',
      { font: font.baseName, page: font.page },
    );
  }

  for (const part of parts) {
    const decoded = font.decode(part.code);
    if (decoded === null) {
      // Three distinct faults, told apart because they are told apart to the
      // reader. Which one applies is the difference between a file that could
      // be fixed by re-encoding the font and a file that will never be readable.
      const named = font.kind === 'simple' ? font.table.get(part.code) : null;
      let why;
      if (font.toUnicode) {
        why = 'is not covered by the font\'s own character mapping, so what it stands for is not stated';
      } else if (named && !glyphToUnicode(named)) {
        why = `names the glyph "${named}", which has no character this extractor can read`;
      } else if (font.kind === 'composite') {
        why = 'is a glyph index the font provides no character for';
      } else {
        why = 'has no entry in the font encoding and the font provides no mapping';
      }
      refuse(
        `on page ${font.page}, the font ${font.baseName || '(unnamed)'} shows the character code `
        + `${escapeCode(part.code)}, which ${why}`,
        'UNDECODABLE_FONT',
        { font: font.baseName, page: font.page, code: escapeCode(part.code), glyphName: named ?? null },
      );
    }
    const w0 = font.widthAt(font.kind === 'simple' ? part.code : part.value);
    text += decoded;
    width += (w0 / 1000) * size + charSpacing + (part.space ? wordSpacing : 0);
  }
  return { text, width: width * th };
}

/** A code rendered for a refusal message, so a byte is never a control character. */
function escapeCode(code) {
  const bytes = typeof code === 'number'
    ? Buffer.from([code & 0xff])
    : Buffer.from(String(code), 'latin1');
  return `<${bytes.toString('hex').toUpperCase().match(/../g).join(' ')}>`;
}

// --- unit construction -------------------------------------------------------

/**
 * Build the contract's units from the ordered visual lines.
 *
 * The reconstructed source is a plain string with one reconstructed visual
 * line per row, and each row is *indented by the horizontal offset of its
 * first run from the page's own left edge*, in the font's own units treated as
 * columns. That indent is what makes `column` mean something: a finding's
 * column comes from `posAt(starts, offset)` over this string, so a line that
 * starts 306 points across a two-column page reports at column 307 without any
 * field being overridden after the fact, and a run sitting at the margin is
 * column 1 however wide the margin happens to be. `makeUnit` is used exactly as
 * every other extractor uses it.
 *
 * The left edge is measured per page, because pages need not share a margin,
 * and it is measured over the lines that carry text: a line with no text has no
 * position to speak of.
 *
 * The indent is a geometric offset rendered as whitespace. It is not a
 * measurement of characters on the page, because a page has none.
 */
function unitsFromLines(orderedLines, filePath) {
  const entries = [];
  for (const line of orderedLines) {
    const text = joinLineRuns(line);
    if (!text) continue;
    entries.push({ line, text });
  }
  if (!entries.length) return [];

  const leftEdge = new Map();
  for (const { line } of entries) {
    const seen = leftEdge.get(line.pageNumber);
    leftEdge.set(line.pageNumber, seen === undefined ? line.minX : Math.min(seen, line.minX));
  }

  const rows = [];
  const lineTexts = [];
  for (const { line, text } of entries) {
    const x = Math.round(line.minX - leftEdge.get(line.pageNumber));
    const indent = Math.min(MAX_INDENT_COLUMNS, Math.max(0, x));
    lineTexts.push(' '.repeat(indent) + text);
    rows.push({ text, indent, page: line.pageNumber });
  }

  const source = lineTexts.join('\n');
  const starts = lineStarts(source);

  const units = [];
  let cursor = 0;
  for (let i = 0; i < rows.length; i++) {
    const { text, indent, page } = rows[i];
    const offset = cursor + indent;
    // The map points each character of the text at its own offset in the
    // reconstructed source, which is the same discipline every other
    // extractor follows and the reason a finding lands on its word.
    const map = [];
    for (let k = 0; k < text.length; k++) map.push(offset + k);
    const unit = makeUnit({
      file: filePath,
      starts,
      offset,
      raw: text,
      text,
      map,
      context: 'authored',
    });
    if (!unit) { cursor += lineTexts[i].length + 1; continue; }
    unit.pdfPage = page;
    units.push(unit);
    cursor += lineTexts[i].length + 1;
  }
  return units;
}

/**
 * Join the runs of one visual line.
 *
 * Runs are already ordered by `x`. A space is inserted between two runs when
 * the horizontal gap between them is wider than half the font's space width —
 * a producer that draws two text-showing operators where a reader sees one
 * space has left exactly that gap, and the font's own space width is the only
 * measure that knows how wide a space should have been.
 */
function joinLineRuns(line) {
  let out = '';
  let previous = null;
  for (const run of line.runs) {
    if (previous) {
      const gap = run.x - previous.endX;
      if (isWordGap(gap, previous.spaceWidth) && !/\s$/.test(out) && !/^\s/.test(run.text)) {
        out += ' ';
      }
    }
    out += run.text;
    previous = run;
  }
  return out.replace(/\s+/g, ' ').trim();
}
