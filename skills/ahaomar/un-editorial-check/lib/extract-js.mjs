// JavaScript / TypeScript extraction: only string literals that carry evidence
// of being user-visible copy become units.
//
// Evidence, in order of strength:
//   1. the literal is assigned to, or passed to, a render surface
//      (label, title, text, message, tooltip, caption, innerHTML, add(...)),
//   2. the literal is concatenated into a larger string (narrative assembly
//      such as `add("... " + value + "% ...")`),
//   3. an interpolated template literal that reads like a sentence.
//
// Everything else — property names, identifiers, selectors, URLs, version
// literals, single-quoted code strings — never becomes a unit, so no rule can
// report it. That boundary is what the line-regex implementation lacked.

import { tokenizeJS } from './tokenize.mjs';
import { makeUnit, stripTags, COMPACT_MARKER, unitText } from './units.mjs';

// Nothing here is a "render function name" gate: JSX copy is found by the shape
// of the markup, and literal copy by the three evidence rules below. A new
// render surface therefore needs no list entry.

const TARGET_KEYS = [
  'label', 'title', 'text', 'message', 'msg', 'tooltip', 'heading', 'caption',
  'placeholder', 'summary', 'description', 'narrative', 'takeaway', 'emptystate',
  'empty-state', 'button', 'header', 'subtitle', 'alt', 'content', 'innertext',
  'textcontent', 'innerhtml', 'copy', 'body', 'html', 'note', 'alert', 'banner',
  'kicker', 'lede', 'disclaimer', 'notice', 'hint', 'footnote', 'citation',
];

const TARGET_CALLS = [
  'add', 'append', 'write', 'render', 'show', 'display', 'alert', 'toast',
  'notify', 'announce', 'setlabel', 'settitle', 'settext', 'settooltip',
  'setmessage', 'setheading', 'setcaption', 'setsummary', 'setdescription',
  'setnarrative', 'createtextnode',
];

const COMPACT_RE = /legend|axis|tooltip|tile|stat|badge|pill|sparkline|gauge|knob/i;
const HTMLISH_RE = /<\/?[a-zA-Z][^>]*>/;

function compile(words) {
  return new RegExp(`^(?:${words.join('|')})$`, 'i');
}

function classify(tail) {
  let t = tail.replace(/\s+$/, '');
  // TypeScript annotation on a declaration: strip it so the *variable* name is
  // classified before `=`, not the type. `const msg: Record<string, string> = `
  // becomes `const msg = `. A type containing `=` or `;` is left alone (the
  // pattern cannot cross those characters), so `case foo: b =` tails stay put.
  t = t.replace(
    /\b(const|let|var)\s+([A-Za-z_$][\w$]*)\s*:\s*[^=;]*?(?=\s*=\s*$)/,
    '$1 $2',
  );
  let m;
  if ((m = t.match(/([A-Za-z_$][\w$]*)\s*:\s*$/))) return { kind: 'key', name: m[1] };
  if ((m = t.match(/([A-Za-z_$][\w$.]*)\s*\(\s*$/))) return { kind: 'call', name: m[1] };
  if ((m = t.match(/([A-Za-z_$][\w$.]*)\s*[+]?=\s*$/))) return { kind: 'assign', name: m[1] };
  if (/\+\s*$/.test(t)) return { kind: 'concat', name: null };
  if (/,\s*$/.test(t)) {
    const calls = [...t.slice(-200).matchAll(/([A-Za-z_$][\w$.]*)\(/g)];
    if (calls.length) return { kind: 'arg', name: calls[calls.length - 1][1] };
  }
  return { kind: 'unknown', name: null };
}

function passesShapeGate(value) {
  if (!value) return false;
  return /[A-Za-z]{2,}[^A-Za-z0-9]+[A-Za-z]{2,}/.test(value)
    || (value.length >= 20 && /[A-Za-z]/.test(value));
}

function unquote(token) {
  if (token.type === 'template') return token.text.replace(/^`/, '').replace(/`$/, '');
  return token.text.slice(1, -1);
}

// Sentence-like copy: at least four whitespace-separated words AND a sentence
// ending. Position-independent — prose written into any literal (a fallback
// message, an array element, a console argument) is copy, not a label.
//
// Shape (settled against the self-scan gate): the literal must be a
// double-quoted string or a template with no interpolation. A single-quoted
// literal in JavaScript is conventionally an identifier, a path or a label, and
// an interpolated template is a format string whose source text is not the
// string that ships — neither is the sentence as published. A bare double
// quoted or bare template literal *is* the sentence, wherever it sits.
function isSentenceLike(value) {
  const trimmed = value.trim();
  if (!/[.!?]$/.test(trimmed)) return false;
  return trimmed.split(/\s+/).length >= 4;
}

function isSentenceLiteral(token) {
  if (token.type === 'string-double') return true;
  return token.type === 'template' && !token.interp;
}

// --- JSX and TSX text children ------------------------------------------------
//
// A .jsx or .tsx file writes its copy in the markup, not in a literal:
// `<p>The organization reports.</p>` contains no quotes at all, so the
// tokenizer — which classifies only string and template tokens — produced
// nothing for the whole file. That is the largest extraction gap found in the
// audit: an entire supported format contributed zero copy, which brief §6
// names as "dynamically rendered copy".
//
// The gate is structural, not a file extension. A text run is copy only when it
// sits in an element's text position: directly after the `>` that closes an
// opening tag, and directly before the `<` that opens the next tag. That single
// shape is what separates rendered copy from the identifiers, keywords and
// operators that fill the rest of a .js or .ts file, so the scan stays narrow
// without needing to know the extension; a file with no element yields no JSX
// units at all.
//
// Three JSX-specific exclusions, each because the text is not what a reader
// sees: `{expression}` children are code (a literal inside braces is still
// reached by the string path above, as `{"The organization…"}`), `{/* … */}`
// comments are not copy, and a self-closing or void element has no text
// position at all.
//
// The run is decoded through unitText with quotes masked, exactly like a
// literal, so a quotation inside JSX copy is still reported as quoted material
// and a fix can never land inside it.

const JSX_OPEN_RE = /<([A-Za-z][-A-Za-z0-9_.]*)((?:[^<>"']|"[^"]*"|'[^']*')*)>/g;
const JSX_VOID_TAGS = new Set(['br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'area', 'col', 'wbr']);

/** The offset just past the `}` closing the `{` at `from`, or -1. */
function skipJSXHole(source, from) {
  let depth = 0;
  for (let i = from; i < source.length; i++) {
    const ch = source[i];
    if (ch === '{') depth++;
    else if (ch === '}') {
      depth--;
      if (depth === 0) return i + 1;
    } else if (ch === '"' || ch === "'" || ch === '`') {
      const close = source.indexOf(ch, i + 1);
      if (close < 0) return -1;
      i = close;
    }
  }
  return -1;
}

/** The offset just past the `>` closing the tag at `from`, or -1. */
function skipJSXTag(source, from) {
  let quote = null;
  for (let i = from; i < source.length; i++) {
    const ch = source[i];
    if (quote) {
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'") { quote = ch; continue; }
    if (ch === '>') return i + 1;
  }
  return -1;
}

/**
 * Collect the copy in `[from, to)`, which is one element's children. Three
 * things are stepped over rather than read: a tag (its attribute values are
 * literals the string path already reaches, and its text position is a
 * sibling's business), an expression hole, and a comment. Everything else is
 * text a reader sees.
 */
function collectJSXText(source, from, to, filePath, starts, offsetBase, units, suppressAt) {
  let i = from;
  while (i < to) {
    const ch = source[i];
    if (ch === '<') {
      const end = skipJSXTag(source, i);
      i = end < 0 || end > to ? to : end;
      continue;
    }
    if (ch === '{') {
      const end = skipJSXHole(source, i);
      i = end < 0 || end > to ? to : end;
      continue;
    }
    // A plain text run, up to the next tag, hole or end of children.
    let j = i;
    while (j < to && source[j] !== '<' && source[j] !== '{') j++;
    const raw = source.slice(i, j);
    const { text, map } = unitText(raw, { base: offsetBase + i, decode: true });
    const unit = makeUnit({
      file: filePath,
      starts,
      offset: offsetBase + i,
      raw,
      text,
      map,
      context: 'authored',
      // A ue:ignore on the line that carries the copy suppresses it, the
      // same contract the string/template path honours.
      suppress: suppressAt ? suppressAt(offsetBase + i) : null,
    });
    if (unit) units.push(unit);
    i = j;
  }
}

/**
 * The offset just past `</name>` at or after `from`, or -1 when the element is
 * never closed. Matches the *corresponding* close rather than the first one, so
 * a nested same-name element does not close the outer element early.
 */
function findJSXClose(source, from, name) {
  const close = new RegExp(`<(/?)${name}(?=[\\s/>])`, 'gi');
  close.lastIndex = from;
  let depth = 1;
  let m;
  while ((m = close.exec(source))) {
    if (m[1]) {
      depth--;
      if (depth === 0) {
        const gt = source.indexOf('>', m.index);
        return gt < 0 ? -1 : gt + 1;
      }
    } else {
      depth++;
    }
  }
  return -1;
}

function extractJSXChildren(source, filePath, { starts, offsetBase = 0, suppressAt = null } = {}) {
  const units = [];
  JSX_OPEN_RE.lastIndex = 0;
  let m;
  while ((m = JSX_OPEN_RE.exec(source))) {
    const tag = m[0];
    const tagEnd = m.index + tag.length;
    if (tag.startsWith('</')) continue;             // a close carries no text
    if (tag.endsWith('/>')) continue;               // self-closing: no children
    const name = m[1];
    if (JSX_VOID_TAGS.has(name.toLowerCase())) continue;

    const close = findJSXClose(source, tagEnd, name);
    if (close < 0) continue;   // unclosed element: documented, not a silent miss
    // The children run from the opening tag's `>` to the `<` that starts the
    // matching close, so the close tag itself is never read as copy.
    const childrenEnd = source.lastIndexOf('<', close - 1);
    collectJSXText(source, tagEnd, childrenEnd < tagEnd ? tagEnd : childrenEnd,
      filePath, starts, offsetBase, units, suppressAt);
    // Nested elements' own text is collected by their own entry in this walk, so
    // stepping past this close keeps every run to exactly one collection.
    JSX_OPEN_RE.lastIndex = close;
  }
  return units;
}

/**
 * @param {string} source   JavaScript source (may be a slice of a larger file)
 * @param {string} filePath
 * @param {object} options
 * @param {number[]} options.starts      line starts of the *containing* document
 * @param {number}   options.offsetBase  where `source` starts inside that document
 * @param {string[]} options.renderTargets  extra identifiers treated as render surfaces
 */
export function extractJS(source, filePath, { starts, offsetBase = 0, renderTargets = [] } = {}) {
  const tokens = tokenizeJS(source);
  const units = [];
  const sanitised = renderTargets.map(t => String(t).replace(/[^\w$-]/g, '')).filter(Boolean);
  const targetRe = compile([...TARGET_KEYS, ...sanitised]);
  const callRe = compile([...TARGET_CALLS, ...sanitised]);

  // JSX and TSX write their copy in the markup, not in a literal:
  // `<p>The organization reports.</p>` has no quotes anywhere, so the
  // tokenizer — which classifies only string and template tokens — returned
  // nothing for the whole file. A .jsx or .tsx file therefore contributed zero
  // copy, which brief §6 names as the gap ("dynamically rendered copy").
  //
  // JSX text is extracted only from real element text positions: the run
  // between a `>` that closes an opening tag and the `<` that opens the next
  // one, at the top level of a JSX expression. Every other kind of text in a
  // .js/.ts file is code, and the structural gate is what keeps this from
  // turning the whole file into copy: no element, no JSX units.
  // Line starts of this slice, used to honour a `ue:ignore` written in a
  // comment on the same line as the literal — including the JSX-shaped copy
  // below, whose units are built before the string/template loop.
  const lineStartsOfSource = [0];
  for (let i = 0; i < source.length; i++) {
    if (source[i] === '\n') lineStartsOfSource.push(i + 1);
  }
  const suppressionAt = (offset) => {
    let lo = 0;
    let hi = lineStartsOfSource.length - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (lineStartsOfSource[mid] <= offset) lo = mid;
      else hi = mid - 1;
    }
    const from = lineStartsOfSource[lo];
    const to = lo + 1 < lineStartsOfSource.length ? lineStartsOfSource[lo + 1] - 1 : source.length;
    const span = source.slice(from, to);
    return /ue:ignore/.test(span) ? span : null;
  };

  units.push(...extractJSXChildren(source, filePath, { starts, offsetBase, suppressAt: suppressionAt }));
  function lineIndexAt(offset) {
    let lo = 0;
    let hi = lineStartsOfSource.length - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (lineStartsOfSource[mid] <= offset) lo = mid;
      else hi = mid - 1;
    }
    return lo;
  }
  function suppressionFor(token) {
    const first = lineIndexAt(token.start);
    const last = lineIndexAt(token.end);
    const from = lineStartsOfSource[first];
    const to = last + 1 < lineStartsOfSource.length
      ? lineStartsOfSource[last + 1] - 1
      : source.length;
    const span = source.slice(from, to);
    return /ue:ignore/.test(span) ? span : null;
  }

  for (let index = 0; index < tokens.length; index++) {
    const token = tokens[index];
    if (token.type !== 'string-double' && token.type !== 'string-single' && token.type !== 'template') continue;

    const prev = index > 0 && tokens[index - 1].type === 'code' ? tokens[index - 1].text : '';
    const ctx = classify(prev.slice(-160));
    const shortName = ctx.name ? ctx.name.split('.').pop() : null;

    let include;
    if (ctx.kind === 'key' || ctx.kind === 'assign') {
      include = shortName !== null && targetRe.test(shortName);
    } else if (ctx.kind === 'call' || ctx.kind === 'arg') {
      include = shortName !== null && callRe.test(shortName);
    } else if (ctx.kind === 'concat') {
      include = token.type !== 'string-single';
    } else {
      include = token.type === 'template' && Boolean(token.interp) && passesShapeGate(unquote(token));
    }

    const value = unquote(token);
    if (!value.trim()) continue;
    // Sentence-like copy is copy wherever it sits — comments are already
    // excluded because they never reach the tokenizer as string tokens.
    if (!include && isSentenceLiteral(token) && isSentenceLike(value)) include = true;
    if (!include) continue;

    // The offset map is built from the literal's *contents*, so every copy
    // character points at its own source offset and the surrounding quotes can
    // never be touched by a fix.
    const opening = '`"\''.includes(token.text[0]) ? 1 : 0;
    const closing = token.text.length > 1 && '`"\''.includes(token.text[token.text.length - 1]) ? 1 : 0;
    const content = token.text.slice(opening, token.text.length - closing);
    const prepared = HTMLISH_RE.test(content) ? stripTags(content) : content;
    const { text, map } = unitText(prepared, { base: offsetBase + token.start + opening });

    const unit = makeUnit({
      file: filePath,
      starts,
      offset: offsetBase + token.start,
      raw: source.slice(token.start, token.end),
      suppress: suppressionFor(token),
      text,
      map,
      context: 'code',
      compact: COMPACT_RE.test(shortName || ''),
    });
    if (unit) units.push(unit);
  }
  return units;
}
