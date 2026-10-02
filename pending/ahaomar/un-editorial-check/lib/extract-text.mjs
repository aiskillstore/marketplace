// Plain-text extraction: paragraphs are units.
//
// A .txt file is assumed to be prose, but agents do drop HTML fragments into
// them, so comments, technical spans (<script>, <code>, <cite>, …), fenced
// blocks, URLs, quoted material and quote-prefixed lines are masked —
// equal-length, so every surviving character keeps its exact source offset and
// `--fix` can never land inside a quotation, a comment or a link target.

import {
  makeUnit, mask, maskUrls, maskQuotes, maskedToUnitText,
  maskRegions, COMMENT_SPEC, TECH_SPEC, FENCE_SPEC,
} from './units.mjs';

const HR_RE = /^\s*([-*_])(?:\s*\1){2,}\s*$/;
const QUOTE_LINE_RE = /^\s*>/;
const INLINE_CODE_RE = /`[^`\n]*`/g;

/** Mask a single line and build its text with an exact offset map. */
function prepare(line, base) {
  let masked = mask(line, INLINE_CODE_RE);
  masked = maskUrls(masked);
  masked = maskQuotes(masked);
  return maskedToUnitText(masked, { base });
}

export function extractText(source, filePath, { starts } = {}) {
  const units = [];
  const maskedSource = maskRegions(source, [COMMENT_SPEC, TECH_SPEC, FENCE_SPEC]);
  const lines = source.split('\n');
  const maskedLines = maskedSource.split('\n');
  const offsets = [];
  let cursor = 0;
  for (const line of lines) { offsets.push(cursor); cursor += line.length + 1; }

  let block = [];
  let blockStart = null;
  let blockEnd = null;

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
      });
      if (unit) units.push(unit);
    }
    block = [];
    blockStart = null;
    blockEnd = null;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const masked = maskedLines[i];
    if (!line.trim()) { flush(); continue; }
    if (!masked.trim()) {
      // Fully masked away (comment, technical span or fence): it belongs to
      // the paragraph it sits in, but contributes no copy.
      if (blockStart !== null) blockEnd = offsets[i] + line.length;
      continue;
    }
    if (HR_RE.test(masked)) { flush(); continue; }
    // Quote-prefixed lines are quotations: reported speech, left alone.
    if (QUOTE_LINE_RE.test(masked)) { flush(); continue; }
    const prepared = prepare(masked, offsets[i]);
    if (!prepared.text) {
      if (blockStart !== null) blockEnd = offsets[i] + line.length;
      continue;
    }
    if (blockStart === null) blockStart = offsets[i];
    block.push({ text: prepared.text, map: prepared.map, joinAt: offsets[i] + line.length });
    blockEnd = offsets[i] + line.length;
  }
  flush();
  return units;
}
