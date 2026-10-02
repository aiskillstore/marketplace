// Markdown extraction. The whole fenced region — opening fence, body and
// closing fence — is one skipped span, which is exactly where the previous
// implementation broke (it skipped only the opening fence line and ran every
// body line through the prose checks).
//
// Blocks (paragraphs, headings, list items) become one unit each so that
// claim/sourcing checks see a whole paragraph: a figure and its source in the
// same paragraph must not be reported as an unsourced claim.
//
// Every transformation is equal-length: HTML comments and technical elements
// (including ones that span line breaks) are blanked first, then list markers,
// inline code, link targets, autolinks and stray tags are blanked in place. The
// rules therefore read a string from which code, link targets and quotations
// are absent — not merely skipped by a heuristic — and every surviving copy
// character carries an exact map back to its source offset.

import {
  makeUnit, mask, rewrite, maskUrls, maskQuotes, maskedToUnitText,
  createRegionMasker, COMMENT_SPEC, TECH_SPEC,
} from './units.mjs';

const FENCE_RE = /^\s*(`{3,}|~{3,})/;
const HR_RE = /^\s{0,3}([-*_])(?:\s*\1){2,}\s*$/;
const SETEXT_RE = /^\s{0,3}(=+|-+)\s*$/;
const HEADING_RE = /^\s{0,3}#{1,6}\s+(.*)$/;
const LIST_MASK_RE = /^\s*(?:[-*+]|\d+[.)])\s+/g;
// Non-global twin used with .test(): a /g regex keeps lastIndex between calls.
const LIST_LINE_RE = /^\s*(?:[-*+]|\d+[.)])\s+\S/;
const QUOTE_RE = /^\s{0,3}>+\s?/;
const TABLE_RE = /^\s*\|.*\|\s*$/;
const INDENT_RE = /^ {4,}\S/;

const INLINE_CODE_LINE_RE = /`[^`\n]*`/g;
const MD_LINK_RE = /!?\[([^\]]*)\]\([^)]*\)/g;
const MD_AUTOLINK_RE = /<https?:\/\/[^>]*>/g;
const TAG_LINE_RE = /<\/?[a-zA-Z][^>]*>/g;

/** Mask a single line and build its text with an exact offset map. */
function prepare(line, base) {
  let masked = mask(line, LIST_MASK_RE);        // "- item" -> "  item"
  masked = mask(masked, INLINE_CODE_LINE_RE);   // inline code is technical
  masked = rewrite(masked, MD_LINK_RE, m => m[1] ?? ''); // keep text, drop target
  masked = mask(masked, MD_AUTOLINK_RE);
  masked = mask(masked, TAG_LINE_RE);           // keep inner text
  masked = maskUrls(masked);
  masked = maskQuotes(masked);                  // published or reported speech
  return maskedToUnitText(masked, { base });
}

/**
 * @param {string} source
 * @param {string} filePath
 * @param {object} options
 * @param {number[]} options.starts
 */
export function extractMarkdown(source, filePath, { starts } = {}) {
  const units = [];
  const lines = source.split('\n');
  const offsets = [];
  let cursor = 0;
  for (const line of lines) { offsets.push(cursor); cursor += line.length + 1; }

  // Fences are never fed to the masker: a "<!--" inside a code block is code.
  const maskRegion = createRegionMasker([COMMENT_SPEC, TECH_SPEC]);

  let i = 0;
  // YAML front matter: only honoured when it actually closes.
  if (lines[0] === '---') {
    let j = 1;
    while (j < lines.length && lines[j] !== '---') j++;
    if (j < lines.length) i = j + 1;
  }

  let block = [];        // { text, map, joinAt } per line
  let blockStart = null; // source offset of the block's first line
  let blockEnd = null;   // source offset just past the block's last line
  let blockCompact = false;
  // Structural flags for the block: an ATX heading line makes its own block a
  // heading unit; a list marker anywhere in the block marks the whole block
  // (conservatively — a lazy continuation line inherits the flag).
  let blockHeading = false;
  let blockListItem = false;

  const flush = () => {
    if (block.length && blockStart !== null) {
      const raw = source.slice(blockStart, blockEnd);
      let text = '';
      const map = [];
      for (let k = 0; k < block.length; k++) {
        if (k) { text += ' '; map.push(block[k - 1].joinAt); }
        text += block[k].text;
        for (const at of block[k].map) map.push(at);
      }
      const unit = makeUnit({
        file: filePath,
        starts,
        offset: blockStart,
        raw,
        text,
        map,
        context: 'authored',
        compact: blockCompact,
      });
      if (unit) {
        if (blockHeading) unit.heading = true;
        if (blockListItem) unit.listItem = true;
        // No `block` id here, and none needed: an inline element in Markdown
        // (`**bold**`, `[text](url)`) stays inside the block's text rather than
        // splitting it, so a Markdown paragraph is already one unit and is its
        // own block. A unit with no block id is compared as its own block.
        units.push(unit);
      }
    }
    block = [];
    blockStart = null;
    blockEnd = null;
    blockCompact = false;
    blockHeading = false;
    blockListItem = false;
  };

  const addLine = (idx, prepared, compact) => {
    if (!prepared.text) {
      // A markup-only line still belongs to the block: extend the raw slice.
      if (blockStart !== null) blockEnd = offsets[idx] + lines[idx].length;
      return;
    }
    if (blockStart === null) blockStart = offsets[idx];
    block.push({ text: prepared.text, map: prepared.map, joinAt: offsets[idx] + lines[idx].length });
    blockEnd = offsets[idx] + lines[idx].length;
    if (compact) blockCompact = true;
  };

  let fence = null;
  let indentedCode = false;
  let prevBlank = true;

  for (; i < lines.length; i++) {
    const raw = lines[i];

    const fenceMatch = raw.match(FENCE_RE);
    if (fence) {
      if (fenceMatch && fenceMatch[1][0] === fence[0] && fenceMatch[1].length >= fence.length
        && raw.trim().slice(0, fenceMatch[1].length) === fenceMatch[1]
        && raw.trim() === fenceMatch[1]) {
        fence = null;
      }
      prevBlank = false;
      continue;
    }
    if (fenceMatch) { flush(); fence = fenceMatch[1]; prevBlank = false; continue; }

    // Comments and technical elements, including ones spanning line breaks.
    const line = maskRegion(raw);

    if (!raw.trim()) { flush(); indentedCode = false; prevBlank = true; continue; }
    if (!line.trim()) {
      if (blockStart !== null) blockEnd = offsets[i] + raw.length;
      prevBlank = false;
      continue;
    }

    if (INDENT_RE.test(line) && prevBlank) { indentedCode = true; }
    if (indentedCode) { prevBlank = false; continue; }

    if (HR_RE.test(line) || SETEXT_RE.test(line)) { flush(); prevBlank = false; continue; }

    // Block quotations are published or reported speech: never reported on,
    // never rewritten.
    if (QUOTE_RE.test(line)) { flush(); prevBlank = false; continue; }

    const heading = line.match(HEADING_RE);
    if (heading) {
      flush();
      const base = offsets[i] + (heading[0].length - heading[1].length);
      const prepared = prepare(heading[1], base);
      blockHeading = true;
      if (prepared.text) addLine(i, prepared, false);
      flush();
      prevBlank = false;
      continue;
    }

    const isTable = TABLE_RE.test(line);
    if (!isTable && blockCompact) flush();
    if (LIST_LINE_RE.test(line)) blockListItem = true;
    addLine(i, prepare(line, offsets[i]), isTable);
    prevBlank = false;
  }
  flush();
  return units;
}
