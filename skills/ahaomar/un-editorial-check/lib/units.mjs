// Shared copy-span (unit) construction.
//
// A unit is a piece of user-visible text that has already been separated from
// markup, comments, code and URLs. Editorial rules only ever see units, which
// is the boundary that keeps CSS property names, identifiers, modulo
// operators, comments and version strings out of editorial findings.
//
// Positional integrity: masking happens on equal-length input, so every
// character that survives into `unit.text` keeps an exact map back to its
// offset in the source file (`unit.map`). A rule can therefore only ever match
// text that really was copy — protected material is not merely "skipped by a
// heuristic", it is absent from the string the rules read, and the fixer can
// never land inside a URL, a quotation, a comment or code.

import { posAt } from './position.mjs';

const NAMED_ENTITIES = {
  amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ',
  rsquo: '’', lsquo: '‘', ldquo: '“', rdquo: '”',
  ndash: '–', mdash: '—', hellip: '…', middot: '·',
};

const WHITESPACE = /\s/;

/** Decode one entity starting at `i`, or null when it is not a known entity. */
export function decodeEntityAt(text, i) {
  if (text[i] !== '&') return null;
  const semi = text.indexOf(';', i + 1);
  if (semi < 0 || semi - i > 12) return null;
  const body = text.slice(i + 1, semi);
  let value;
  if (/^#x[0-9a-f]+$/i.test(body)) value = fromCodePoint(parseInt(body.slice(2), 16));
  else if (/^#\d+$/.test(body)) value = fromCodePoint(parseInt(body.slice(1), 10));
  else if (Object.hasOwn(NAMED_ENTITIES, body.toLowerCase())) value = NAMED_ENTITIES[body.toLowerCase()];
  else return null;
  if (value === null) return null;
  return { value, length: semi - i + 1 };
}

function fromCodePoint(code) {
  if (!Number.isSafeInteger(code) || code < 0 || code > 0x10ffff) return null;
  if (code >= 0xd800 && code <= 0xdfff) return null;
  return String.fromCodePoint(code);
}

export function decodeEntities(text) {
  let out = '';
  for (let i = 0; i < text.length; i++) {
    const entity = decodeEntityAt(text, i);
    if (entity) { out += entity.value; i += entity.length - 1; }
    else out += text[i];
  }
  return out;
}

// Absolute links, query strings, mailto targets — and bare relative paths such
// as `./overview`, which are file references in copy and must never be
// rewritten into a file name that does not exist.
const URL_RE = /(?:https?:\/\/|file:\/\/|mailto:|ftp:\/\/|www\.)[^\s<>"'`]+|(?:\.{1,2}\/|~\/)[\w./~@+-]+/g;
const DOUBLE_QUOTED_RE = /"(?:[^\n"\\]|\\.)*"|“[^”\n]*”|‘[^’\n]*’/g;
const HTML_COMMENT_RE = /<!--[\s\S]*?(?:-->|$)/g;
const FENCE_RE = /(`{3,}|~{3,})[\s\S]*?\1/g;
const INLINE_CODE_RE = /`[^`\n]*`/g;

/** Replace matches with equal-length spaces so the offset map stays aligned. */
export function mask(text, re) {
  re.lastIndex = 0;
  let out = '';
  let last = 0;
  for (const match of text.matchAll(re)) {
    out += text.slice(last, match.index) + ' '.repeat(match[0].length);
    last = match.index + match[0].length;
  }
  return out + text.slice(last);
}

/**
 * Rewrite matches with something no longer than the match — `pick(match)` may
 * keep part of it (link text is kept, the target is dropped) — padding to equal
 * length so offsets stay aligned.
 */
export function rewrite(text, re, pick) {
  re.lastIndex = 0;
  let out = '';
  let last = 0;
  for (const match of text.matchAll(re)) {
    const replacement = String(pick(match)).slice(0, match[0].length);
    out += text.slice(last, match.index) + replacement + ' '.repeat(match[0].length - replacement.length);
    last = match.index + match[0].length;
  }
  return out + text.slice(last);
}

/** URLs, query strings and `mailto:` targets are never editorial targets. */
export const maskUrls = (text) => mask(text, URL_RE);

/** Quoted material is treated as published/reported speech and left alone. */
export const maskQuotes = (text) => mask(text, DOUBLE_QUOTED_RE);

/** HTML comments are authoring notes, never copy — even inside prose files. */
export const maskHtmlComments = (text) => mask(text, HTML_COMMENT_RE);

/** Fenced and inline code are technical material. */
export const maskCode = (text) => mask(mask(text, FENCE_RE), INLINE_CODE_RE);

const TAG_RE = /<\/?[a-zA-Z][^>]*>/g;

/** Blank markup tags while keeping the text they wrap, at equal length. */
export const maskTags = (text) => mask(text, TAG_RE);

/**
 * Collapse a masked, equal-length string into unit text while recording, for
 * every character that survives, the absolute offset it came from.
 *
 * @param {string} masked  same length as the source slice it was made from
 * @param {object} options { base: absolute offset of masked[0], decode: bool }
 * @returns {{ text: string, map: number[] }} map[i] is the source offset of text[i]
 */
export function maskedToUnitText(masked, { base = 0, decode = false } = {}) {
  const chars = [];
  const map = [];
  let pendingSpace = -1;

  const flushSpace = () => {
    if (pendingSpace >= 0 && chars.length) { chars.push(' '); map.push(base + pendingSpace); }
    pendingSpace = -1;
  };

  for (let i = 0; i < masked.length; i++) {
    const ch = masked[i];
    if (WHITESPACE.test(ch)) { if (pendingSpace < 0) pendingSpace = i; continue; }
    if (decode && ch === '&') {
      const entity = decodeEntityAt(masked, i);
      if (entity) {
        flushSpace();
        for (const value of entity.value) { chars.push(value); map.push(base + i); }
        i += entity.length - 1;
        continue;
      }
    }
    flushSpace();
    chars.push(ch);
    map.push(base + i);
  }
  return { text: chars.join(''), map };
}

/** Mask standard copy hazards (URLs, optionally quotes) then build text+map. */
export function unitText(raw, { base = 0, decode = false, quotes = true, patterns = [] } = {}) {
  let masked = raw;
  for (const re of [URL_RE, ...(quotes ? [DOUBLE_QUOTED_RE] : []), ...patterns]) {
    masked = mask(masked, re);
  }
  return maskedToUnitText(masked, { base, decode });
}

/** Blank inline markup tags, keeping the text they wrap (equal length). */
export const stripTags = (text) => maskTags(text);

// --- regions that span line breaks ------------------------------------------
//
// HTML comments, technical elements and fenced blocks can open on one line and
// close on another. They are masked over the whole file before any line is
// parsed, so a comment that wraps three lines cannot leak copy — or a fix — on
// line two.

export const COMMENT_SPEC = { open: /<!--/g, close: /-->/g };
export const TECH_SPEC = {
  open: /<(?:script|style|code|pre|cite|kbd|samp|var|template)\b[^>]*>/gi,
  close: /<\/(?:script|style|code|pre|cite|kbd|samp|var|template)\s*>/gi,
};
export const FENCE_SPEC = {
  open: /^[ \t]*(`{3,}|~{3,})[^\n]*$/gm,
  close: /^[ \t]*(`{3,}|~{3,})[^\n]*$/gm,
};

const blankRange = (text, start, end) =>
  text.slice(0, start) + ' '.repeat(Math.max(0, end - start)) + text.slice(end);

/**
 * A stateful line masker for regions that can span line breaks. Feed it the
 * lines of a document in order; each call returns the line with every open
 * region blanked. A region left open at the end of a line stays open for the
 * next one (HTML comments behave exactly this way); an unclosed region runs to
 * the end of the document.
 *
 * @param {Array<{open: RegExp, close: RegExp}>} specs
 */
export function createRegionMasker(specs) {
  let open = null;
  return function maskLine(line) {
    let out = line;
    let pos = 0;
    for (;;) {
      if (open) {
        open.close.lastIndex = pos;
        const closing = open.close.exec(out);
        const end = closing ? closing.index + closing[0].length : out.length;
        out = blankRange(out, pos, end);
        pos = end;
        if (!closing) return out;
        open = null;
      }
      let best = null;
      for (const spec of specs) {
        spec.open.lastIndex = pos;
        const found = spec.open.exec(out);
        if (found && (best === null || found.index < best.m.index)) best = { spec, m: found };
      }
      if (!best) return out;
      // Blank the opening marker itself and start the region after it. When
      // the open and close patterns are the same (fenced blocks), searching
      // for the closer from the marker's own start let the marker close its
      // own region: the fence never opened, its body reached the rules — and
      // the fixer rewrote it.
      const markerEnd = best.m.index + best.m[0].length;
      out = blankRange(out, best.m.index, markerEnd);
      open = best.spec;
      pos = markerEnd;
    }
  };
}

/**
 * Blank every region opened by one of `specs` up to its closing marker (or the
 * end of the text), preserving the length of the text exactly.
 *
 * @param {string} text
 * @param {Array<{open: RegExp, close: RegExp}>} specs
 */
export function maskRegions(text, specs) {
  const maskLine = createRegionMasker(specs);
  return text.split('\n').map(maskLine).join('\n');
}

/** Compact, space-constrained surfaces where "%" and hyphens are legitimate. */
export function isCompact(text) {
  return /^\s*\d[\d\s.,%‰+–—/-]*$/.test(text) && /\d/.test(text);
}

export const COMPACT_MARKER = /stat|tile|axis|legend|tooltip|badge|pill|chip|sparkline|knob|gauge/i;

/**
 * @param {object} unit
 * @param {number[]} [unit.map] absolute source offset of each text character
 */
export function makeUnit({
  file, starts, offset, raw, text, map = null, context, compact = false, suppress = null,
}) {
  const clean = text.replace(/\s+/g, ' ').trim();
  if (!clean) return null;
  if (!map || map.length !== text.length || clean !== text) map = null;
  const pos = posAt(starts, offset);
  return {
    file,
    line: pos.line,
    column: pos.column,
    offset,
    raw,
    // Source outside the literal (a comment on the same line) that carries a
    // `ue:ignore` for this unit. Kept separate from `raw` so a suppression can
    // never be read out of the copy itself.
    suppress,
    text: clean,
    map,
    context,
    compact: compact || isCompact(clean),
    starts,
  };
}
