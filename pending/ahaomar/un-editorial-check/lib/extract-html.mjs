// HTML extraction: every text node, copy-bearing attribute, <title>, the meta
// description and the og/twitter social copy become units; markup, comments,
// <code>/<pre>/<template>, <style> internals and non-JavaScript <script>
// payloads never do.
//
// Each unit carries the context metadata of the surface it was copied from —
// authored, quoted (blockquotes and <q>), cited (<cite> titles), nav or
// metadata — so the review lanes can report quoted material separately, plus
// heading and list-item flags for the structure-sensitive heuristics.
//
// Parsing model (documented limitation, brief §6 "document and test"): this is
// a forward, single-pass tag scanner, not a standards-aware tree builder. It
// does not implement implied end tags, foster parenting or foreign-content
// rules; text nodes are attributed to the nearest open tag on the stack, and
// every malformed-HTML recovery case is pinned by tests/audit-depth.mjs.
//
// <script> JavaScript is delegated to extractJS with the script's own offset,
// so its string literals are classified by render evidence instead of by
// their position in a line.

import { extractJS } from './extract-js.mjs';
import { makeUnit, unitText, COMPACT_MARKER } from './units.mjs';
import { posAt } from './position.mjs';

// Technical surfaces (never copy): their contents never become checkable units.
const SKIP_CONTENT = new Set(['code', 'pre', 'template']);
// Quotation surfaces: scanned as visible copy, tagged for the review lanes.
const QUOTED_TAGS = new Set(['blockquote', 'q']);
// Page-furniture navigation: interface labels, not authored narrative copy.
const NAV_TAGS = new Set(['nav', 'menu', 'aside']);
const HEADING_TAGS = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']);
const LIST_TAGS = new Set(['li', 'dd', 'dt']);
// Social metadata carried in <meta content>.
const SOCIAL_META = new Set(['og:title', 'og:description', 'twitter:title', 'twitter:description']);
// Tabular and other space-constrained contexts: "%" and hyphens are legitimate.
const TABLE_CONTEXT = new Set(['table', 'thead', 'tbody', 'tr', 'td', 'th']);
// Block elements whose extent scopes a `ue:ignore` comment written anywhere
// inside (or next to) them: the suppression silences that block only.
const PARAGRAPH_TAGS = new Set([
  'p', 'li', 'dd', 'dt', 'td', 'th', 'figcaption', 'caption', 'legend',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
]);
// Buttons whose `value` attribute is published copy (a control label), as
// opposed to a text field's default value (user data, never scanned).
const BUTTON_INPUT_TYPES = new Set(['button', 'submit', 'reset']);
const VOID_TAGS = new Set([
  'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
  'param', 'source', 'track', 'wbr',
]);
// Copy-bearing attributes: the value of each is the context of the surface it
// describes. `alt` is authored description copy; interface labels belong to
// the navigation surface.
//
// The ARIA additions are the accessible-name and accessible-description
// properties a screen reader announces as text, which brief §6 requires to be
// scanned:
//   aria-label             — the accessible name of any element.
//   aria-description       — the accessible *description* (ARIA 1.3). A real
//     attribute, not an invention; sighted readers do not see it, which is why
//     it is navigation copy rather than authored narrative.
//   aria-roledescription   — a human-readable role name announced in place of
//     the role ("button", "link").
//   aria-valuetext         — the spoken form of a range value ("moderate"),
//     which is what a sighted user cannot read from the number itself.
//
// `aria-labelledby` takes a list of element IDs, not copy, so it is not here;
// the referenced element's own text is already extracted as a text node.
const COPY_ATTRS = new Map([
  ['alt', 'authored'],
  ['aria-label', 'nav'],
  ['aria-description', 'nav'],
  ['aria-roledescription', 'nav'],
  ['aria-valuetext', 'nav'],
  ['placeholder', 'nav'],
  ['title', 'nav'],
]);
const NON_JS_SCRIPT = /^(application\/(ld\+)?json|text\/template|text\/x-handlebars|text\/html)/i;

function findTagEnd(source, start) {
  let i = start + 1;
  let quote = null;
  while (i < source.length) {
    const c = source[i];
    if (quote) {
      if (c === quote) quote = null;
    } else if (c === '"' || c === "'") {
      quote = c;
    } else if (c === '>') {
      return i;
    }
    i++;
  }
  return source.length - 1;
}

// The HTML attribute grammar, in the order the spec lists it: a name, optional
// whitespace, `=`, optional whitespace, then a double-quoted, single-quoted or
// *unquoted* value. The unquoted form is legal HTML — `alt=The quick brown fox`
// is valid and is what a hand-edited or generated page looks like — and the
// previous pattern accepted only the two quoted forms, so every copy-bearing
// unquoted attribute was silently dropped.
//
// An unquoted value ends at whitespace or at `>`, which is why the lookahead
// excludes `>`, `"`, `'`, `=`, `<` and a backtick: those characters cannot
// appear in an unquoted value, so stopping at them never truncates a real one.
// The value is never empty (`*` after the first character), which keeps a
// valueless attribute out of the result.
const ATTR_RE = /([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;

function parseAttrs(tagText, tagStart) {
  const attrs = new Map();
  let m;
  while ((m = ATTR_RE.exec(tagText))) {
    const value = m[2] !== undefined ? m[2] : m[3] !== undefined ? m[3] : m[4];
    // Offset of the first character of the value, absolute in the file. For a
    // quoted value that is one past the opening quote; for an unquoted one it
    // is the offset of the first value character itself.
    const eq = m[0].indexOf('=');
    let valueAt = tagStart + m.index + m[0].length - value.length;
    if (m[2] !== undefined || m[3] !== undefined) {
      const quote = m[2] !== undefined ? '"' : "'";
      const quoteAt = eq >= 0 ? m[0].indexOf(quote, eq) : -1;
      valueAt = tagStart + m.index + (quoteAt >= 0 ? quoteAt + 1 : 0);
    }
    attrs.set(m[1].toLowerCase(), { value, offset: valueAt });
  }
  return attrs;
}

function isCompactElement(attrs) {
  for (const key of ['class', 'id', 'role', 'aria-label']) {
    const attr = attrs.get(key);
    if (attr && COMPACT_MARKER.test(attr.value)) return true;
  }
  return false;
}

/**
 * @param {string} source
 * @param {string} filePath
 * @param {object} options
 * @param {number[]} options.starts
 * @param {string[]} options.renderTargets
 */
export function extractHTML(source, filePath, { starts, renderTargets = [] } = {}) {
  const units = [];
  const stack = []; // { name, compact, start }
  const n = source.length;
  let i = 0;

  // `ue:ignore` comments, captured during the walk and applied afterwards so
  // a suppression can scope a whole paragraph regardless of where inside it
  // the comment sits. { start, end, inner }
  const suppressions = [];
  // Extents of block elements, for the same reason.
  const paragraphSpans = [];

  // The block a piece of copy sits in, as the offset of the nearest enclosing
  // block-level element's opening tag. Inline markup does not open a block, so
  // every text node of one <p> shares the id: an inline element splits a
  // paragraph into several units, and a rule that needs the paragraph whole
  // (UE-HR003) reassembles them. With no enclosing block the id is null and the
  // unit is its own block, which is the unit-at-a-time comparison those rules
  // have always done.
  const blockOf = () => {
    for (let k = stack.length - 1; k >= 0; k--) {
      if (PARAGRAPH_TAGS.has(stack[k].name)) return stack[k].start;
    }
    return null;
  };

  // Copy that came out of an attribute value rather than a text node. It sits
  // inside the block element around it and carries that block's id, so it does
  // not split the block, but it is not part of the block's running text either:
  // a paragraph with an image in it is one paragraph, and the image's alt text
  // is not a sentence of that paragraph.
  const pushAttribute = (unit) => {
    if (!unit) return;
    unit.attribute = true;
    const block = blockOf();
    if (block !== null) unit.block = block;
    units.push(unit);
  };
  const insideSkip = () => stack.some(e => SKIP_CONTENT.has(e.name));
  const insideCompact = () => stack.some(e => e.compact);
  const insideTag = (names) => stack.some(e => names.has(e.name));

  // The context of a text node: citation beats quotation, quotation beats
  // navigation, navigation beats authored copy. A <cite> anywhere around the
  // node marks it as a cited title wherever it sits.
  const htmlContext = () => {
    let context = 'authored';
    for (const entry of stack) {
      if (entry.name === 'cite') return 'cited';
      if (QUOTED_TAGS.has(entry.name)) context = 'quoted';
      else if (NAV_TAGS.has(entry.name) && context === 'authored') context = 'nav';
    }
    return context;
  };

  // A text node that is nothing but whitespace — a space between two inline
  // elements, or a `&nbsp;` that decodes to one — carries no copy, so it is not
  // a unit, but a reader sees the space. Remembered for the next unit, which
  // takes it as a space at its seam.
  let spaceBefore = false;

  const addText = (start, end) => {
    if (end <= start || insideSkip()) return;
    const raw = source.slice(start, end);
    const { text, map } = unitText(raw, { base: start, decode: true });
    const unit = makeUnit({
      file: filePath,
      starts,
      offset: start,
      raw,
      text,
      map,
      context: htmlContext(),
      compact: insideCompact(),
    });
    if (!unit) {
      // `text` is the decoded, collapsed text; the unit is dropped only when
      // there is nothing in it but whitespace.
      if (text && !text.trim()) spaceBefore = true;
      return;
    }
    if (insideTag(HEADING_TAGS)) unit.heading = true;
    if (insideTag(LIST_TAGS)) unit.listItem = true;
    const block = blockOf();
    if (block !== null) unit.block = block;
    if (spaceBefore) { unit.spaceBefore = true; spaceBefore = false; }
    units.push(unit);
  };

  const closeElement = (name, end) => {
    for (let k = stack.length - 1; k >= 0; k--) {
      if (stack[k].name === name) {
        const entry = stack[k];
        if (PARAGRAPH_TAGS.has(name)) {
          paragraphSpans.push({ start: entry.start, end: end === undefined ? n : end });
        }
        stack.splice(k, 1);
        return;
      }
    }
  };

  while (i < n) {
    const lt = source.indexOf('<', i);
    if (lt < 0) { addText(i, n); break; }
    addText(i, lt);

    // Comments, doctype and other declarations.
    if (source.startsWith('<!--', lt)) {
      const end = source.indexOf('-->', lt + 4);
      const stop = end < 0 ? n : end + 3;
      const inner = source.slice(lt + 4, end < 0 ? n : end);
      if (/ue:ignore/.test(inner)) suppressions.push({ start: lt, end: stop, inner });
      i = stop;
      continue;
    }
    if (source.startsWith('<!', lt) || source.startsWith('<?', lt)) {
      const end = source.indexOf('>', lt + 2);
      i = end < 0 ? n : end + 1;
      continue;
    }

    const closing = source.startsWith('</', lt);
    const tagEnd = findTagEnd(source, lt);
    const tagText = source.slice(lt, tagEnd + 1);
    const nameMatch = tagText.match(/^<\/?\s*([a-zA-Z][a-zA-Z0-9-]*)/);

    if (!nameMatch) { i = tagEnd + 1; continue; }
    const name = nameMatch[1].toLowerCase();

    if (closing) {
      closeElement(name, lt);
      i = tagEnd + 1;
      continue;
    }

    const attrs = parseAttrs(tagText, lt);
    const selfClosing = tagText.endsWith('/>') || VOID_TAGS.has(name);

    // Raw-text elements: their bodies are not walked by the tag scanner.
    if (name === 'script' || name === 'style') {
      const bodyStart = tagEnd + 1;
      const closeRe = new RegExp(`</${name}`, 'i');
      const rest = source.slice(bodyStart);
      const found = rest.search(closeRe);
      const bodyEnd = found < 0 ? n : bodyStart + found;
      if (name === 'script' && !NON_JS_SCRIPT.test(attrs.get('type')?.value || '')) {
        const body = source.slice(bodyStart, bodyEnd);
        if (body.trim()) {
          units.push(...extractJS(body, filePath, { starts, offsetBase: bodyStart, renderTargets }));
        }
      }
      i = found < 0 ? n : bodyStart + found;
      continue;
    }

    // Copy-bearing attributes.
    for (const [attr, kind] of COPY_ATTRS) {
      const attrValue = attrs.get(attr);
      if (!attrValue || !attrValue.value.trim()) continue;
      const { text, map } = unitText(attrValue.value, { base: attrValue.offset, decode: true });
      pushAttribute(makeUnit({
        file: filePath,
        starts,
        offset: attrValue.offset,
        raw: attrValue.value,
        text,
        map,
        context: kind,
        compact: kind === 'nav' || insideCompact(),
      }));
    }
    if (name === 'button'
      || (name === 'input' && BUTTON_INPUT_TYPES.has(
        (attrs.get('type')?.value || '').trim().toLowerCase()))) {
      const value = attrs.get('value');
      if (value && value.value.trim()) {
        const { text, map } = unitText(value.value, { base: value.offset, decode: true });
        pushAttribute(makeUnit({
          file: filePath,
          starts,
          offset: value.offset,
          raw: value.value,
          text,
          map,
          context: 'nav',
          compact: true,
        }));
      }
    }
    // The meta description and the og/twitter social copy are page metadata:
    // visible in result cards, never narrative copy.
    if (name === 'meta') {
      const key = ((attrs.get('name')?.value || attrs.get('property')?.value) || '').trim().toLowerCase();
      if (key === 'description' || SOCIAL_META.has(key)) {
        const content = attrs.get('content');
        if (content && content.value.trim()) {
          const { text, map } = unitText(content.value, { base: content.offset, decode: true });
          pushAttribute(makeUnit({
            file: filePath,
            starts,
            offset: content.offset,
            raw: content.value,
            text,
            map,
            context: 'metadata',
            compact: true,
          }));
        }
      }
    }

    if (!selfClosing) {
      stack.push({
        name,
        compact: insideCompact() || TABLE_CONTEXT.has(name) || isCompactElement(attrs),
        start: lt,
      });
    }
    i = tagEnd + 1;

    // <title> body is user-visible page copy but space-constrained.
    if (name === 'title' && !selfClosing) {
      const closeIdx = source.toLowerCase().indexOf('</title', i);
      const end = closeIdx < 0 ? n : closeIdx;
      const raw = source.slice(i, end);
      const { text, map } = unitText(raw, { base: i, decode: true });
      pushAttribute(makeUnit({
        file: filePath,
        starts,
        offset: i,
        raw,
        text,
        map,
        context: 'metadata',
        compact: true,
      }));
      closeElement('title', i);
      i = end;
    }
  }

  // Unclosed block elements still scope a suppression written inside them.
  for (const entry of stack) {
    if (PARAGRAPH_TAGS.has(entry.name)) {
      paragraphSpans.push({ start: entry.start, end: n });
    }
  }

  applySuppressions(source, starts, units, suppressions, paragraphSpans);
  markBlocks(source, units);

  return units;
}

/**
 * Mark the last unit of every block, and withdraw the block id from any block a
 * `ue:ignore` silenced in part.
 *
 * `blockLast` is how a rule knows a paragraph is complete: units arrive one at a
 * time, so a rule reassembling a paragraph needs to be told that the last piece
 * has arrived rather than guessing from the next unit.
 *
 * A partially suppressed block gives up its id, so its surviving units are
 * compared one by one as before. Reassembling around a suppression would join
 * copy the author asked not to be read together, and could report a repeat
 * against a paragraph that is only half present.
 */
function markBlocks(source, units) {
  const blocks = new Map();
  for (let k = 0; k < units.length; k++) {
    const unit = units[k];
    if (unit.block === undefined) continue;
    const entry = blocks.get(unit.block) || { last: -1, partial: false, before: null };
    entry.last = k;
    if (unit.suppress) entry.partial = true;
    // The joiner is measured here, while `entry.before` is still the unit
    // immediately preceding this one. An attribute unit carries the block id so
    // that it cannot end the block, but its value is not the paragraph's running
    // text, so it is neither a join point nor given a joiner of its own.
    if (!unit.attribute) {
      if (entry.before) {
        unit.joiner = unit.spaceBefore ? ' ' : joinerBetween(source, entry.before, unit);
      }
      entry.before = unit;
    }
    blocks.set(unit.block, entry);
  }
  for (let k = 0; k < units.length; k++) {
    const unit = units[k];
    if (unit.block === undefined) continue;
    const entry = blocks.get(unit.block);
    if (entry.partial) delete unit.block;
    else if (entry.last === k) unit.blockLast = true;
  }
}

// The text a reader sees between two pieces of one block: either nothing, or a
// space. Which of the two is decided by the source around the markup, not by a
// fixed guess.
//
// The markup between two text nodes of a paragraph sits either where a word was
// broken (`humanit<mark>arian</mark>`) or where a space already was
// (`...is <strong>badly</strong> underfunded`). Nothing is rendered at the first
// and a space at the second, so the two are one word and two words
// respectively. Reassembling on a fixed space would read the first as two words,
// and would then never match the plain copy of a paragraph whose word an inline
// element happened to break — which is the exact repeat this form exists to
// find. So: a space if the source carries whitespace at the seam, or if the
// markup between the two is something a reader sees as a space (a break, a
// rule, an image, a control); nothing if the markup renders nothing at all.
function joinerBetween(source, before, after) {
  if (/\s$/.test(before.raw) || /^\s/.test(after.raw)) return ' ';
  const gap = source.slice(before.offset + before.raw.length, after.offset);
  if (/\s/.test(gap)) return ' ';
  if (RENDERS_A_SPACE.test(gap)) return ' ';
  // Markup only, and none of it renders as anything: the word either side of it
  // is one word.
  return '';
}

// Tags a reader sees as a space whatever the source around them says, because
// each stands for something in the flow of the line rather than for styling.
const RENDERS_A_SPACE = /<\/?(?:br|hr|img|input|textarea|select|option|button|iframe|object|embed|video|audio|canvas|svg|picture|source|area|map|col|wbr)\b/i;

/**
 * Scope every `ue:ignore` comment to the copy it was written for.
 *
 * (a) inside a block element silences every unit of that block, however far
 *     from the comment;
 * (b) a standalone comment line silences the units on the next non-blank line
 *     (the "comment above the paragraph" pattern);
 * (c) otherwise it silences the units sharing its own lines that begin before
 *     it (a trailing comment after `</p>` on the same line).
 */
function applySuppressions(source, starts, units, suppressions, paragraphSpans) {
  if (!suppressions.length) return;

  const lineAt = (offset) => posAt(starts, offset).line;
  const lineText = (line) => {
    const from = starts[line - 1];
    const to = line < starts.length ? starts[line] - 1 : source.length;
    return source.slice(from, to);
  };
  const isStandalone = ({ start, end }) => {
    const before = source.slice(lineTextStart(start), start);
    const after = source.slice(end, lineTextEnd(end));
    return !before.trim() && !after.trim();
  };
  const lineTextStart = (offset) => starts[lineAt(offset) - 1];
  const lineTextEnd = (offset) => {
    const line = lineAt(offset);
    return line < starts.length ? starts[line] - 1 : source.length;
  };
  const firstNonBlankLineAfter = (endLine) => {
    for (let line = endLine + 1; line <= starts.length; line++) {
      if (lineText(line).trim()) return line;
    }
    return -1;
  };

  for (const sup of suppressions) {
    const spec = sup.inner.trim();
    if (!spec) continue;

    const containing = paragraphSpans
      .filter(p => p.start <= sup.start && sup.end <= p.end)
      .sort((a, b) => (a.end - a.start) - (b.end - b.start))[0];

    let targets;
    if (containing) {
      targets = units.filter(u => u.offset >= containing.start && u.offset < containing.end);
    } else if (isStandalone(sup)) {
      const line = firstNonBlankLineAfter(lineAt(sup.end));
      targets = line < 0 ? [] : units.filter(u => u.line === line);
    } else {
      const first = lineAt(sup.start);
      const last = lineAt(sup.end);
      targets = units.filter(u => u.line >= first && u.line <= last && u.offset < sup.start);
    }

    for (const unit of targets) {
      if (!unit.suppress) unit.suppress = spec;
    }
  }
}
