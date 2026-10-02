// Offset -> line/column mapping for extracted copy spans.
//
// Every unit carries the exact source slice it was built from (`raw`) and the
// offset where that slice starts. Findings are positioned by locating the
// matched token inside `raw`, so a finding on the fortieth word of a paragraph
// points at that word, not at column 1 of the paragraph.

export function lineStarts(source) {
  const starts = [0];
  for (let i = 0; i < source.length; i++) if (source.charCodeAt(i) === 10) starts.push(i + 1);
  return starts;
}

export function posAt(starts, offset) {
  let low = 0;
  let high = starts.length - 1;
  while (low < high) {
    const mid = (low + high + 1) >> 1;
    if (starts[mid] <= offset) low = mid;
    else high = mid - 1;
  }
  return { line: low + 1, column: offset - starts[low] + 1 };
}

function tokenAt(raw, matched) {
  const direct = raw.indexOf(matched);
  if (direct >= 0) return direct;
  // The matched phrase may span a newline or an entity that normalisation
  // rewrote; fall back to its leading word, then its trailing word.
  const words = matched.split(/\s+/).filter(Boolean);
  for (const word of [words[0], words[words.length - 1]]) {
    if (!word) continue;
    const at = raw.indexOf(word);
    if (at >= 0) return at;
  }
  return -1;
}

/**
 * Position of `matched` (found at `index` in the cleaned unit text) inside the
 * original source. Falls back to the start of the copy span.
 */
export function locate(unit, matched, index) {
  const needle = matched || '';
  const map = unit.map;

  // Preferred: the unit's offset map points at the exact source character each
  // piece of copy came from, so the position cannot land on a masked region.
  if (map && typeof index === 'number' && index >= 0 && index < map.length && needle) {
    const offset = map[index];
    return { offset, ...posAt(unit.starts, offset) };
  }

  const raw = unit.raw || '';
  let at = -1;
  if (needle && typeof index === 'number' && index >= 0 && raw.startsWith(needle, index)) {
    at = index;
  } else if (needle) {
    at = tokenAt(raw, needle);
  }
  const offset = unit.offset + (at >= 0 ? at : 0);
  return { offset, ...posAt(unit.starts, offset) };
}

// --- the occurrence excerpt -------------------------------------------------
//
// The Content column of the occurrence table: the line of copy the match sits
// on, with the match marked.

// The mark around the match. Guillemets rather than brackets because brackets
// occur in the copy itself and a mark that can appear in the copy is not a
// mark; they sit at 0xAB and 0xBB in WinAnsi, so the PDF draws them without
// falling back to '?'; and they are characters rather than colours, so the mark
// survives greyscale and reaches a screen reader.
const MARK_OPEN = '»';
const MARK_CLOSE = '«';

/**
 * Longest excerpt, in characters. A line is used rather than a paragraph so a
 * table row stays one row, and this cap is what keeps a very long source line
 * from wrapping into a cell taller than the table expects.
 */
export const EXCERPT_MAX = 100;

/**
 * The line of copy carrying `matched`, with the match marked.
 *
 * Built while the unit is in hand, at scan time. The report never re-reads the
 * file: quoting text from a file that changed after the scan would put words in
 * an authoritative document that the scan never saw.
 *
 * Returns `null` when the unit carries no copy, so a caller falls back to the
 * matched token rather than showing an empty cell.
 *
 * @param {object} unit     the unit the match was found in
 * @param {string} matched  the matched token
 * @param {number} index    the token's index in `unit.raw`
 * @param {number} [max]    longest excerpt to return
 * @returns {string|null}
 */
export function matchExcerpt(unit, matched, index, max = EXCERPT_MAX) {
  const raw = unit && typeof unit.raw === 'string' ? unit.raw : '';
  const needle = matched || '';
  if (!raw || !needle) return null;

  // The offset map is the strongest proof of position: when the matched text
  // sits verbatim at the mapped source character, that character is where the
  // mark goes. Text indexes diverge from source offsets whenever masking or
  // whitespace collapsing shortened the copy span, so the index alone proves
  // nothing; a mapped position that does not hold the needle verbatim is
  // discarded rather than trusted.
  let at = -1;
  if (unit.map && Number.isInteger(index) && index >= 0 && index < unit.map.length
    && Number.isInteger(unit.offset)) {
    const mapped = unit.map[index] - unit.offset;
    if (mapped >= 0 && raw.startsWith(needle, mapped)) at = mapped;
  }
  if (at < 0) {
    at = (typeof index === 'number' && index >= 0 && raw.startsWith(needle, index))
      ? index
      : tokenAt(raw, needle);
  }
  // The match cannot be located in this unit's copy at all — the unit was
  // masked or normalised away from it. Marking anything else would name text
  // the finding never matched, so return nothing and let the caller fall back
  // to the matched token it already holds.
  if (at < 0) return null;

  // The line the match sits on, not the paragraph: a unit may span several
  // lines — a Markdown paragraph, an HTML span, a PDF's visual line — and the
  // table shows the one line the finding is on.
  const lineStart = raw.lastIndexOf('\n', at - 1) + 1;
  const nextBreak = raw.indexOf('\n', at + needle.length);
  const lineEnd = nextBreak < 0 ? raw.length : nextBreak;
  const line = raw.slice(lineStart, lineEnd);
  if (!line.trim()) return null;

  // A match may cross the line's end; mark only the part of it on this line,
  // because a mark that runs past the line would read as a second match.
  const rel = Math.min(Math.max(at - lineStart, 0), line.length);
  const markLen = Math.min(needle.length, line.length - rel);
  const marked = line.slice(0, rel) + MARK_OPEN
    + line.slice(rel, rel + markLen) + MARK_CLOSE
    + line.slice(rel + markLen);
  if (marked.length <= max) return marked;

  // Six characters of slack: both ends may be cut, and each cut is marked.
  const window = max - 6;
  const markAt = rel;
  const markEnd = rel + markLen + 2;
  if (markLen + 2 > window) {
    // The match alone will not fit. Show it alone, cut to the budget, and say
    // nothing about the rest of the line rather than implying a context that
    // is not there.
    return MARK_OPEN + line.slice(rel, rel + Math.max(1, max - 2)) + MARK_CLOSE;
  }

  let start = Math.max(0, markAt - Math.floor((window - (markLen + 2)) / 2));
  let end = Math.min(marked.length, start + window);
  if (end > marked.length) { end = marked.length; start = Math.max(0, end - window); }
  if (markEnd > end) { end = Math.min(marked.length, markEnd); start = Math.max(0, end - window); }
  if (markAt < start) { start = markAt; end = Math.min(marked.length, start + window); }
  let out = marked.slice(start, end);
  if (start > 0) out = `...${out}`;
  if (end < marked.length) out = `${out}...`;
  return out;
}
