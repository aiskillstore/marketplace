// Grammar rules — UE-GR001..UE-GR004, a deliberately high-precision subset.
//
// Subject-verb agreement, verb forms and tense are out of scope: choosing
// between them needs judgement a deterministic matcher cannot make without
// false positives. What is left is mechanical and provable: a doubled word,
// a space between a word and its punctuation, a full stop running straight
// into the next sentence, and (under a configuration gate) a run of doubled
// spaces between words.
//
// Two boundaries keep every finding honest:
//   * rules match `unit.text` — the extracted copy span, with URLs, quotes,
//     code, comments and markup already absent, never the raw source;
//   * `verbatim()` then re-checks each match against the unit's own source
//     slice at the mapped offset, so a space produced only by masking or by
//     joining hard-wrapped lines can never become a finding or a fix. When
//     that check cannot run (no offset map), nothing is reported — a rule
//     that cannot prove the defect stays silent.

import { emit, matchCase } from './rules.mjs';

/**
 * True when `matched` sits verbatim in the unit's source slice at the offset
 * the unit's map points to. Masked regions (URLs, quotations, code) and the
 * spaces that join hard-wrapped lines all collapse to a single space in the
 * cleaned text; without this check they would look exactly like a doubled
 * word or a "word ," defect. A rejected match is never reported, so every
 * reported replacement applies byte for byte — which is also why the guard
 * requires `index` to be an index into `unit.text` (the string `locate()`
 * and the fixer map through).
 */
function verbatim(unit, index, matched) {
  if (!unit.map || !unit.raw || !matched) return false;
  if (index < 0 || index >= unit.map.length) return false;
  const at = unit.map[index] - unit.offset;
  return at >= 0 && at + matched.length <= unit.raw.length
    && unit.raw.startsWith(matched, at);
}

/**
 * The exact source substring a collapsed match came from, when the copy span
 * normalised interior whitespace. `unit.text` collapses a run of spaces to
 * one, so "The  the" reaches a rule as "The the" — a doubled word the plain
 * verbatim proof rejects. When the matched characters can be recovered from
 * the unit's own source slice through the offset map, and the recovered span
 * is the matched copy with only the interior spacing widened, the span is
 * returned so the finding and the fixer can act on the real bytes.
 *
 * Only spaces bridge the span. A newline inside it is a hard-wrapped line
 * join, and a tab is indentation — layout, not stray spaces — so either
 * returns null: a rule that cannot prove the defect stays silent.
 */
function rawSpan(unit, index, matched) {
  if (!unit.map || !unit.raw || !matched) return null;
  if (index < 0 || index + matched.length > unit.map.length) return null;
  const start = unit.map[index] - unit.offset;
  const end = unit.map[index + matched.length - 1] - unit.offset + 1;
  if (start < 0 || end > unit.raw.length || start >= end) return null;
  const raw = unit.raw.slice(start, end);
  if (raw.replace(/ +/g, ' ') !== matched) return null;
  return raw;
}

// --- UE-GR001: unintentionally doubled word ---------------------------------

// The legitimate English doubles. Comparison is case-insensitive, so
// "Had had" is exempt exactly like "had had". Every entry is proved by the
// negative fixture tests/fixtures/negative/gr-doubles-ok.txt; repetition
// outside this list is still reported (see the guard notes).
const ALLOWED_DOUBLES = new Set(['had had', 'that that', 'very very']);

const DOUBLED_WORD_RE = /([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ0-9'’]*) ([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ0-9'’]*)/g;

function ruleGR001(state, unit) {
  const text = unit.text;
  DOUBLED_WORD_RE.lastIndex = 0;
  let m;
  while ((m = DOUBLED_WORD_RE.exec(text))) {
    const first = m[1];
    // Advance past the first word only: in "x x x" the second pair must
    // still be reachable from the position after the first word.
    DOUBLED_WORD_RE.lastIndex = m.index + first.length;
    if (first.toLowerCase() !== m[2].toLowerCase()) continue;
    if (ALLOWED_DOUBLES.has(`${first} ${m[2]}`.toLowerCase())) continue;
    const matched = m[0];
    // A single space between the words is proved in place. A padded pair
    // ("the  the") reaches the rule through the collapsed copy span, and its
    // real source span is recovered through the offset map instead; without
    // either proof the finding stays silent.
    let rawMatched = null;
    if (!verbatim(unit, m.index, matched)) {
      rawMatched = rawSpan(unit, m.index, matched);
      if (!rawMatched) continue;
    }
    const replacement = matchCase(matched, first);
    emit(state, unit, 'UE-GR001', matched, m.index,
      `The word "${first}" appears twice in a row in "${matched}".`,
      `Delete one copy: write "${replacement}".`,
      { replacement, proposed: replacement, rawMatched });
  }
}

// --- UE-GR002: space between a word and following punctuation ---------------
//
// Covered set: exactly , . ; : ? ! with exactly one space before it. The
// space is the defect; the presence of the mark is never reported here —
// an exclamation mark on its own is UE-RE005's territory.

const SPACE_BEFORE_PUNCT_RE = /([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ0-9'’&.-]*) ([,.;:?!])/g;

function ruleGR002(state, unit) {
  const text = unit.text;
  SPACE_BEFORE_PUNCT_RE.lastIndex = 0;
  let m;
  while ((m = SPACE_BEFORE_PUNCT_RE.exec(text))) {
    // A space before an ellipsis ("word ...") is a style choice, not the
    // stray-space defect: leave it to the ue:ignore escape hatch.
    if (m[2] === '.' && text[m.index + m[0].length] === '.') continue;
    const matched = m[0];
    if (!verbatim(unit, m.index, matched)) continue;
    const replacement = m[1] + m[2];
    emit(state, unit, 'UE-GR002', matched, m.index,
      `A space sits between "${m[1]}" and "${m[2]}".`,
      `Pull the punctuation onto the word: write "${replacement}".`,
      { replacement, proposed: replacement });
  }
}

// --- UE-GR003: missing space between sentences ------------------------------
//
// The period must run straight into a capital — "final.Next" — with no space
// at all. Everything in here exists to keep dotted conventions out:
//
//   * preceded by "." or "…"  → ellipsis ("...Next", "…Next");
//   * preceded by a digit     → decimals, version numbers, outline items;
//   * a standalone letter before the period → initials and dotted chains
//     ("U.S.A.", "J.P.", "e.g.", "i.e.");
//   * text ending in a listed abbreviation (word-boundary guarded, so
//     "the best.Next" is still reported while "St.Louis" is not).
//
// A period followed by a lowercase letter — index.js, v1.2's second dot,
// www.example.test — never enters the pattern at all.

const ABBREVIATIONS_END_RE =
  /(?:^|[^A-Za-z])(?:U\.S\.|U\.K\.|U\.N\.|e\.g\.|i\.e\.|etc\.|Dr\.|Mr\.|Mrs\.|Prof\.|vs\.|a\.m\.|p\.m\.|St\.)$/i;
const SENTENCE_JOIN_RE = /\.(?=[A-Z])/g;

function ruleGR003(state, unit) {
  const text = unit.text;
  SENTENCE_JOIN_RE.lastIndex = 0;
  let m;
  while ((m = SENTENCE_JOIN_RE.exec(text))) {
    const at = m.index; // position of the period
    const prev = at > 0 ? text[at - 1] : '';
    if (!prev) continue;                       // period opens the copy span
    if (prev === '.' || prev === '…') continue; // ellipsis
    if (prev >= '0' && prev <= '9') continue;   // decimal, version, numbering
    if (/[A-Za-z]/.test(prev)) {
      const before = at >= 2 ? text[at - 2] : '';
      // A standalone letter before the period is an initial or an initial
      // chain; those take no space after the period by convention.
      if (at < 2 || !/[A-Za-z0-9]/.test(before)) continue;
      if (ABBREVIATIONS_END_RE.test(text.slice(0, at + 1))) continue;
    }
    const word = text.slice(at + 1).match(/^[A-Za-z][A-Za-z0-9'’-]*/);
    if (!word) continue;
    const matched = `.${word[0]}`;
    if (!verbatim(unit, at, matched)) continue;
    const replacement = `. ${word[0]}`;
    emit(state, unit, 'UE-GR003', matched, at,
      `The full stop in "${matched}" runs straight into the next word.`,
      `Insert a space after the full stop: write "${replacement}".`,
      { replacement, proposed: replacement });
  }
}

// --- UE-GR004: a run of doubled spaces --------------------------------------
//
// Two or more literal spaces between words inside authored prose. The copy
// span collapses whitespace runs to one space (lib/units.mjs), so the defect
// is invisible in `unit.text`; the rule reads the unit's own source slice
// through the offset map instead. Three boundaries keep it honest:
//
//   * a run whose first character is a newline or a tab never matches — a
//     hard-wrapped line join and indentation are layout, not stray spaces;
//   * a run that a line break closes is a Markdown hard-line-break marker
//     (two trailing spaces) and never matches;
//   * only authored copy is judged: navigation, compact table units and
//     every other context are out of scope, because deliberately aligned
//     plain-text columns are a formatting choice the rule must not call a
//     defect.
//
// The review is configuration-gated (config.spacingReview) for exactly that
// last reason: an aligned .txt annex is legitimate, so the rule stays silent
// until a project asks for it. When it runs, the replacement is a single
// space and the finding is fixable.

function ruleGR004(state, unit) {
  if (!state.cfg.spacingReview) return;
  if (unit.context !== 'authored' || unit.compact) return;
  if (!unit.map || !unit.raw) return;
  const raw = unit.raw;
  const base = unit.offset;
  for (let i = 1; i < unit.text.length - 1; i++) {
    if (unit.text[i] !== ' ') continue;
    // A collapsed run appears exactly once in the text: the neighbours are
    // never spaces, so every interior text space is a candidate.
    if (unit.text[i - 1] === ' ' || unit.text[i + 1] === ' ') continue;
    const at = unit.map[i] - base;
    if (at < 1 || raw[at] !== ' ' || raw[at + 1] !== ' ') continue;
    let end = at + 2;
    while (raw[end] === ' ') end += 1;
    // A run the line break closes is a Markdown hard line break, not a defect.
    if (raw[end] === '\n') continue;
    const matched = ' '.repeat(end - at);
    emit(state, unit, 'UE-GR004', matched, i,
      'A run of two or more spaces sits between words.',
      'Collapse the run to a single space.',
      { replacement: ' ', rawMatched: matched });
  }
}

export const GRAMMAR_RULES = {
  'UE-GR001': ruleGR001,
  'UE-GR002': ruleGR002,
  'UE-GR003': ruleGR003,
  'UE-GR004': ruleGR004,
};

export const GRAMMAR_META = {
  'UE-GR001': { category: 'grammar', confidence: 'deterministic', severity: 'warning' },
  'UE-GR002': { category: 'grammar', confidence: 'deterministic', severity: 'warning' },
  'UE-GR003': { category: 'grammar', confidence: 'deterministic', severity: 'warning' },
  'UE-GR004': { category: 'grammar', confidence: 'deterministic', severity: 'warning' },
};
