// Editorial rules. Every rule here runs on TextUnit objects — already
// extracted, already classified user-visible prose — never on raw source
// lines. That boundary is what keeps CSS property names, comments, identifiers,
// modulo operators and version strings out of editorial findings.
//
// Two things are enforced for every finding:
//   * a precise position (located inside the unit's original source slice),
//   * an honest confidence label — deterministic rules prove the defect,
//     heuristic rules ask for human or agent judgement and never claim proof.

import { locate, matchExcerpt } from './position.mjs';
import { HS_RULES, HS_META } from './rules-hs.mjs';
import { TONE_RULES, TONE_META, CAPS_EXEMPT } from './rules-tone.mjs';
import { GRAMMAR_RULES, GRAMMAR_META } from './rules-grammar.mjs';

/** Rule metadata for the editorial set. Catalogue fields are asserted equal by tests. */
export const EDITORIAL_RULES = {
  'UE-SP001': { category: 'spelling', confidence: 'deterministic', severity: 'error' },
  'UE-SP002': { category: 'spelling', confidence: 'heuristic', severity: 'warning' },
  'UE-SP003': { category: 'spelling', confidence: 'heuristic', severity: 'info' },
  'UE-TE001': { category: 'terminology', confidence: 'deterministic', severity: 'error' },
  'UE-TE002': { category: 'terminology', confidence: 'deterministic', severity: 'error' },
  'UE-TE003': { category: 'terminology', confidence: 'deterministic', severity: 'error' },
  'UE-TE004': { category: 'terminology', confidence: 'deterministic', severity: 'error' },
  'UE-TE005': { category: 'terminology', confidence: 'deterministic', severity: 'error' },
  'UE-NU001': { category: 'numerals', confidence: 'deterministic', severity: 'warning' },
  'UE-NU002': { category: 'numerals', confidence: 'deterministic', severity: 'warning' },
  'UE-RE001': { category: 'register', confidence: 'heuristic', severity: 'warning' },
  'UE-RE002': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-RE003': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-RE004': { category: 'register', confidence: 'heuristic', severity: 'warning' },
  'UE-RE005': { category: 'register', confidence: 'deterministic', severity: 'error' },
  'UE-DI001': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-CL001': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-CL002': { category: 'agent-review', confidence: 'deterministic', severity: 'warning' },
  'UE-CL003': { category: 'agent-review', confidence: 'deterministic', severity: 'warning' },
  'UE-DP001': { category: 'diplomacy', confidence: 'deterministic', severity: 'error' },
  'UE-HR001': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-HR002': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-HR003': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-HR004': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-HR005': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-HR006': { category: 'agent-review', confidence: 'heuristic', severity: 'warning' },
  'UE-HR007': { category: 'agent-review', confidence: 'heuristic', severity: 'info' },
  'UE-HR008': { category: 'agent-review', confidence: 'deterministic', severity: 'info' },
  'UE-HR009': { category: 'agent-review', confidence: 'deterministic', severity: 'info' },
  'UE-GL001': { category: 'terminology', confidence: 'deterministic', severity: 'warning' },
  'UE-GL002': { category: 'terminology', confidence: 'deterministic', severity: 'warning' },
  ...HS_META,
  ...TONE_META,
  ...GRAMMAR_META,
};

export const EDITORIAL_RULE_IDS = Object.keys(EDITORIAL_RULES);

const SCOPE = 'user-visible-copy';

export const escapeRe = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

export function matchCase(sample, replacement) {
  if (sample === sample.toUpperCase()) return replacement.toUpperCase();
  if (sample[0] === sample[0].toUpperCase()) return replacement[0].toUpperCase() + replacement.slice(1);
  return replacement;
}

export function wordRe(phrase, flags = 'g') {
  return new RegExp(`\\b${escapeRe(phrase)}\\b`, flags);
}

/** `ue:ignore UE-SP001,UE-TE003` / `<!-- ue:ignore all -->` inside a copy span. */
function suppression(unit) {
  const raw = [unit.raw, unit.suppress].filter(Boolean).join(' ');
  if (!/ue:ignore/.test(raw)) return null;
  const match = raw.match(/ue:ignore\s+([A-Za-z0-9*,\s-]+)/);
  if (!match) return { all: true, ids: new Set(), prefixes: [] };
  const specs = match[1].trim().split(/[,\s]+/).filter(Boolean);
  if (specs.some(s => s === 'all' || s === '*')) return { all: true, ids: new Set(), prefixes: [] };
  return {
    all: false,
    ids: new Set(specs),
    prefixes: specs.filter(s => s.endsWith('*')).map(s => s.slice(0, -1)),
  };
}

function isSuppressed(unit, ruleId) {
  const state = suppression(unit);
  if (!state) return false;
  if (state.all) return true;
  return state.ids.has(ruleId) || state.prefixes.some(prefix => ruleId.startsWith(prefix));
}

export function emit(ctx, unit, ruleId, matched, index, message, suggestion, override = {}) {
  if (isSuppressed(unit, ruleId)) return;
  const meta = ctx.meta[ruleId] || EDITORIAL_RULES[ruleId] || {};
  const severity = override.severity || ctx.cfg.severities[ruleId] || meta.severity || 'warning';
  const { line, column, offset } = locate(unit, matched, index);
  ctx.findings.push({
    file: unit.file,
    line,
    column,
    ruleId,
    category: override.category || meta.category || 'editorial',
    severity,
    confidence: override.confidence || meta.confidence || 'heuristic',
    scope: SCOPE,
    // Extraction context of the copy this finding came from — authored,
    // quoted, cited, code, nav or metadata (undefined on units built by
    // callers outside the extractors). The review lanes use it to report
    // quoted material separately; publicFinding copies it into JSON.
    context: unit.context,
    message,
    suggestion: suggestion || null,
    // What is currently written and what should replace it: the two halves of
    // the current-to-should-be report. `proposed` is guidance, not a fix —
    // only findings that also carry a `_replacement` are --fix-able.
    current: matched || null,
    proposed: override.proposed ?? override.replacement ?? null,
    // The line of copy this finding sits on, with the match marked — the
    // occurrence table's Content column. Built here, while the unit is in
    // hand, so the report never re-reads a file that may have changed since
    // the scan. Internal: publicFinding strips it, so JSON and SARIF stay
    // byte-identical to the shape they had before it existed.
    excerpt: matchExcerpt(unit, matched, index),
    _unit: unit,
    _index: index,
    _matched: matched,
    // The exact source substring a match collapsed out of (a doubled word
    // padded with extra spaces): present only when the rule proved the wider
    // span through the unit's offset map, and honoured by the fixer in place
    // of `matched`. Absent on every ordinary finding, so the fixer's behaviour
    // is unchanged.
    _rawMatched: override.rawMatched ?? null,
    // The provenance override for a rule the catalogue does not carry (an
    // organisation's custom rule): the annotate step prefers it to the
    // per-category defaults.
    _sourceOverride: override.source ?? null,
    _offset: offset,
    _replacement: override.replacement ?? null,
  });
}

export function enabled(ctx, ruleId) {
  const setting = ctx.cfg.rules[ruleId];
  if (setting && setting.enabled === false) return false;
  return true;
}

// --- spelling ---------------------------------------------------------------

const WORD_TAIL = /[A-Za-zÀ-ÖØ-öø-ÿ][\w'’&.-]*/;
const SMALL_WORDS = new Set(['of', 'the', 'and', 'for', 'in', 'on', 'at', 'to', 'a', 'an', 'de', 'la', 'du', 'des', 'del', 'and/or']);

function isCapitalised(word) {
  return Boolean(word) && word[0] !== word[0].toLowerCase() && word[0] === word[0].toUpperCase();
}

/**
 * True when a capitalised match sits inside a multi-word proper name:
 * "World Health Organization", "Organization of African Unity". Official
 * names keep their published spelling, so they are never rewritten — the
 * organisation's own name is exactly the case a UN editor must not touch.
 */
function inProperName(text, index, length) {
  const matched = text.slice(index, index + length);
  if (!isCapitalised(matched)) return false;
  const prev = text.slice(0, index).match(new RegExp(`(${WORD_TAIL.source})\\s*$`));
  if (prev && isCapitalised(prev[1])) return true;
  const after = text.slice(index + length);
  const words = after.match(new RegExp(`^\\s*(${WORD_TAIL.source})(?:\\s+(${WORD_TAIL.source}))?`));
  if (!words) return false;
  const first = words[1];
  if (isCapitalised(first)) return true;
  if (SMALL_WORDS.has(first.toLowerCase()) && words[2] && isCapitalised(words[2])) return true;
  return false;
}

// UE-SP001 has three stances, decided by the profile choice rather than by
// nationality:
//
//   conflict key, no profile chosen  → warning that names the choice; no
//                                      suggestion, never --fix-able
//   conflict key, profile accepts it → silent (the profile's spellingConflicts
//                                      list is the accepted set)
//   conflict key, profile enforces   → error with the "-ise" reference and a
//                                      fixable replacement
//   any other key                    → unchanged: the American-spelling error
//
// The conflict family (`vocab.conflictFamily`) is the static list derived
// from the baseline; `vocab.spellingConflicts` is the selected profile's
// stance over that same family.
function ruleSP001(ctx, unit) {
  const allow = new Set(ctx.cfg.allowlist.spellings || []);
  const family = ctx.vocab.conflictFamily || new Set();
  const accepted = ctx.vocab.spellingConflicts || new Set();
  for (const [american, british] of ctx.vocab.spellings) {
    if (allow.has(american) || allow.has(british)) continue;
    const conflict = family.has(american);
    if (conflict && ctx.profileSelected && accepted.has(american)) continue;
    const re = wordRe(american, 'gi');
    let m;
    while ((m = re.exec(unit.text))) {
      if (inProperName(unit.text, m.index, m[0].length)) continue;
      // The noun "programme" is the United Nations form in every sense except
      // computing, where "program" is the established term: a preceding
      // computer, software, pilot or flagship context is exempt, exactly as
      // the US rule exempts currency and the superlative rule its one fixed
      // economic collocation.
      if (PROGRAM_NOUN_EXEMPT.has(american) && PROGRAM_CONTEXT_RE.test(unit.text.slice(Math.max(0, m.index - 32), m.index))) continue;
      const replacement = matchCase(m[0], british);
      if (conflict && !ctx.profileSelected) {
        emit(ctx, unit, 'UE-SP001', m[0], m.index,
          `"${m[0]}" is an "-ize" family spelling; whether it stands is a profile choice. `
          + 'Run with --profile un-secretariat-document to accept it or '
          + '--profile generic-british-english to enforce "-ise".',
          null,
          { severity: 'warning' });
        continue;
      }
      if (conflict) {
        emit(ctx, unit, 'UE-SP001', m[0], m.index,
          `The ${ctx.profileName} profile prefers the "-ise" spelling; "${m[0]}" is an "-ize" form.`,
          `Use "${replacement}".`,
          { replacement });
        continue;
      }
      emit(ctx, unit, 'UE-SP001', m[0], m.index,
        `American spelling "${m[0]}" in prose.`,
        `Use "${replacement}".`,
        { replacement });
    }
  }
}

// The spelling keys that carry a computing-context exemption: the British
// form governs everywhere except a "computer program", "software program",
// "pilot program" or "flagship program", where the American word is the term
// of art. The exemption lives in code + tests/run.mjs; if it is ever written
// into a guard note, rules/spelling.md and rules/catalogue.json are where it
// belongs.
const PROGRAM_NOUN_EXEMPT = new Set(['program', 'programs']);
const PROGRAM_CONTEXT_RE = /\b(?:computer|software|pilot|flagship)\s+$/i;

function ruleSP002(ctx, unit) {
  const allow = new Set(ctx.cfg.allowlist.spellings || []);
  for (const [american, british] of ctx.vocab.spellings) {
    if (allow.has(american) || allow.has(british)) continue;
    const us = wordRe(american, 'gi').exec(unit.text);
    if (!us) continue;
    if (inProperName(unit.text, us.index, us[0].length)) continue;
    const gb = wordRe(british, 'gi').exec(unit.text);
    if (!gb) continue;
    emit(ctx, unit, 'UE-SP002', us[0], us.index,
      `British "${gb[0]}" and American "${us[0]}" variants appear in the same passage.`,
      'Choose one register and use it consistently.');
  }
}

// -ise candidates only: size, prize and their forms end in -ize but are not
// spelling variants, so they are skipped. The review is case-insensitive so a
// sentence-initial "Organize" is reviewed like any other occurrence. Words the
// baseline spelling map already owns are UE-SP001's, never this rule's — one
// word, one finding.
const IZE_RE = /\b(?!(?:size|sizes|sized|sizing|prize|prizes|prized)\b)[a-z]+(?:ize|izes|izing|ized)\b|\b(?:defense|offense|license|licenses|licensed)\b/gi;
function ruleSP003(ctx, unit) {
  if (!ctx.cfg.spellingReview) return;
  let m;
  while ((m = IZE_RE.exec(unit.text))) {
    if (ctx.vocab.spellingKeys.has(m[0].toLowerCase())) continue;
    emit(ctx, unit, 'UE-SP003', m[0], m.index,
      `"${m[0]}" may prefer an "-ise" form; some "-ize" spellings are standard (Oxford).`,
      'Confirm against the dictionary named in the organisation profile.');
  }
}

// --- terminology ------------------------------------------------------------

const DEFINING_RE = /\b(?:ratio|per\s*100,?000|is\s+defined\s+as|defined\s+as|defined\s+here\s+as|means|refers\s+to|namely)\b/i;

// UE-TE001's one context-gated term. "Maternal mortality rate" is a distinct
// technical measure — deaths per person-year lived by women of reproductive
// age, not per 100 000 live births (rules/sources.json,
// un-sdg-metadata-maternal-mortality) — and official UN and WHO prose itself
// uses the phrase (who-maternal-mortality-fact-sheet). It is therefore never
// an error, never --fix-rewritable, and is reported for review only where the
// copy prints a statistic the review can be about.
//
// Three offline states over a fixed window (120 characters before, 200 after):
//   1. a per 100 000 live-births figure is printed  -> review, message states
//      the figure it found;
//   2. another statistic is printed, no such figure -> review, message says
//      the denominator could not be determined offline and claims no defect;
//   3. no statistic printed at all                   -> no finding.
// The window is the whole of the detection: nothing outside it is inferred.
const GATED_TE001 = new Set(['maternal mortality rate']);

const PER_100_000_LIVE_BIRTHS_RE =
  /(?:\bper\b)?[\s ]*\b100[\s ,.]*000[\s -]*live[\s -]*births\b/i;

// A printed statistic is a number that is not a year: "550" and "25.4" count,
// "2020" does not.
function hasPrintedFigure(text) {
  for (const m of text.matchAll(/\d+(?:[.,]\d+)?/g)) {
    if (/^(?:18|19|20|21)\d{2}$/.test(m[0])) continue;
    return true;
  }
  return false;
}

function emitGatedTE001(ctx, unit, entry, m, index) {
  const before = unit.text.slice(Math.max(0, index - 120), index);
  const after = unit.text.slice(index, index + 200);
  const window = `${before} ${m[0]} ${after}`;
  const suggestion = `Confirm the measure; use "${entry.to}" if the ratio is meant.`;
  if (PER_100_000_LIVE_BIRTHS_RE.test(window)) {
    emit(ctx, unit, 'UE-TE001', m[0], index,
      `"${m[0]}" sits beside a printed per 100 000 live-births figure, so the statistic described is the ratio; the rate has a person-years denominator. Review the term — this is a review flag, not an error.`,
      suggestion,
      { severity: 'warning', confidence: 'heuristic', proposed: entry.to });
    return;
  }
  // No per 100 000 live-births figure in the window. Report only when there is
  // a printed statistic to review, and say plainly that the offline check
  // could not establish the denominator.
  if (!hasPrintedFigure(window)) return;
  emit(ctx, unit, 'UE-TE001', m[0], index,
    `"${m[0]}": a statistic is printed nearby but its denominator could not be determined offline — no per 100 000 live-births figure sits in the review window, so no defect is claimed. Review whether the ratio is meant.`,
    suggestion,
    { severity: 'warning', confidence: 'heuristic', proposed: entry.to });
}

function ruleTerminology(ctx, unit) {
  const allow = new Set(ctx.cfg.allowlist.terminology || []);
  for (const entry of ctx.vocab.terminology) {
    if (allow.has(entry.from)) continue;
    const ruleId = entry.rule;
    if (!enabled(ctx, ruleId)) continue;
    // UE-TE005 has its own matcher: country names are matched
    // case-sensitively, because a lowercase "turkey" is the bird.
    if (ruleId === 'UE-TE005') continue;
    const re = wordRe(entry.from, 'gi');
    let m;
    while ((m = re.exec(unit.text))) {
      if (ruleId === 'UE-TE001' && GATED_TE001.has(entry.from.toLowerCase())) {
        emitGatedTE001(ctx, unit, entry, m, m.index);
        continue;
      }
      const before = unit.text.slice(Math.max(0, m.index - 80), m.index);
      const after = unit.text.slice(m.index, m.index + 120);
      const defining = DEFINING_RE.test(before) || DEFINING_RE.test(after);
      if (ruleId === 'UE-TE001' && defining) {
        emit(ctx, unit, ruleId, m[0], m.index,
          `"${m[0]}" appears in a definition context.`,
          `State the indicator explicitly: "${entry.to}".`,
          { severity: 'warning', confidence: 'heuristic', proposed: entry.to });
        continue;
      }
      emit(ctx, unit, ruleId, m[0], m.index,
        `Unapproved terminology "${m[0]}".`,
        `Use "${entry.to}".`,
        { proposed: entry.to });
    }
  }
}

// UE-TE003 is deliberately silent: the live UN Numbers section permits both the
// percentage sign and "per cent" in running text, so ordinary prose is not
// flagged at all (rules/sources.json, un-editorial-manual-numbers). The one
// context the manual still bars — resolutions — has no deterministic offline
// detector in this tool, and a heuristic guess would claim certainty the code
// does not have. That is a documented limitation, recorded in
// rules/terminology.md and locked by tests/audit-terminology.mjs; the rule
// keeps its id, catalogue entry and suppressions so a future detector can be
// switched on without a format change. The word "percent" is UE-SP001's on
// spelling-list authority (rules/spelling.md), not this rule's.
function ruleTE003() {
  return;
}

function ruleTE004(ctx, unit) {
  // The guard notes promise exactly three exemptions and the regex honours
  // them: currency amounts (US dollars, US cents), the US$ figure, and the
  // U.S.A. acronym — which is not the bare "US" this rule targets. A full
  // stop is NOT an exemption: sentence-final bare US ("… in the US.") is
  // reported like any other occurrence (rules/terminology.md and the lock in
  // tests/run.mjs carry the same claim).
  //
  // Terminology is never auto-changed: this rule reports and proposes, and
  // passes no `replacement`, so --fix cannot reach it (README "The safe
  // --fix boundary"; locked by tests/audit-terminology.mjs).
  const re = /(?:\bUS\b(?!\$)(?!\s+(?:dollars?|cents?)\b)|U\.S\.(?![A-Za-z]))/g;
  let m;
  while ((m = re.exec(unit.text))) {
    const before = unit.text.slice(Math.max(0, m.index - 4), m.index);
    const suggestion = /\bthe\s+$/i.test(before) ? 'United States' : 'the United States';
    emit(ctx, unit, 'UE-TE004', m[0], m.index,
      `Bare "${m[0]}" in prose.`,
      `Write "${suggestion}".`,
      { proposed: suggestion });
  }
}

// --- numerals --------------------------------------------------------------

function ruleNU001(ctx, unit) {
  // Both components may be 1-31 so that day/m/y and m/d/y shapes are caught
  // (12/31/2026 is a US m/d/y date that the day-first-only form missed even
  // though the rules document promises both). URLs and code are masked before
  // rules run, so a slash pair plus a four-digit year is unambiguous here.
  const re = /\b(?:0?[1-9]|[12]\d|3[01])\s*\/\s*(?:0?[1-9]|[12]\d|3[01])\s*\/\s*\d{4}\b/g;
  let m;
  while ((m = re.exec(unit.text))) {
    emit(ctx, unit, 'UE-NU001', m[0], m.index,
      `Numeric date "${m[0]}" does not use the UN day-month-year form.`,
      'Write the date as day month year with the month spelled out, for example 9 November 2026.');
  }
  // The written month-first form — "March 5, 2026" — is the same defect in
  // prose words. Full month names only: an abbreviated month ("Mar. 5, 2026")
  // and a month-year reference ("March 2026") are out of scope, and the
  // correct day-month-year order never matches. Dates are never rewritten by
  // --fix, so this carries proposed wording, not a replacement.
  const written = /\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s*(\d{4})\b/gi;
  while ((m = written.exec(unit.text))) {
    const proposed = `${Number(m[2])} ${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[3]}`;
    emit(ctx, unit, 'UE-NU001', m[0], m.index,
      `Written date "${m[0]}" puts the month first.`,
      `Write the date in day-month-year order, for example "${proposed}".`,
      { proposed });
  }
}

function ruleNU002(ctx, unit) {
  if (unit.compact) return;
  const re = /(?<![\d-])\b\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\b(?![\d-])/g;
  let m;
  while ((m = re.exec(unit.text))) {
    const replacement = m[0].replace(/\s*-\s*/, '–');
    emit(ctx, unit, 'UE-NU002', m[0], m.index,
      `Numeric range "${m[0]}" uses a hyphen.`,
      `Use an en dash: "${replacement}".`,
      { replacement });
  }
}

// --- register and tone -----------------------------------------------------

function ruleRE001(ctx, unit) {
  const allow = new Set([
    ...(ctx.cfg.allowlist.register || []),
    ...(ctx.vocab.registerExempt || []),
  ]);
  for (const phrase of ctx.vocab.register) {
    if (allow.has(phrase)) continue;
    const re = wordRe(phrase, 'gi');
    const m = re.exec(unit.text);
    if (!m) continue;
    emit(ctx, unit, 'UE-RE001', m[0], m.index,
      `Register term "${m[0]}" is promotional rather than neutral.`,
      'Replace with neutral, literal wording.');
  }
}

// "leading indicator(s)" is a fixed economic term (a time series that
// precedes the cycle it signals), not a ranking claim, so the lookahead drops
// that collocation only — "the leading candidate" and every other superlative
// still fire. This exception lives in code + tests/audit-detection.mjs;
// if it is ever written into a guard note, rules/register.md (UE-RE002 bullet)
// and rules/catalogue.json (UE-RE002 guardNotes) are where it belongs.
const SUPERLATIVE_RE = /\b(best|worst|largest|smallest|highest|lowest|greatest|leading(?!\s+indicators?\b)|fastest|slowest|unrivalled|unmatched|unprecedented|record[- ]breaking|number one|#1|most (?:successful|powerful|important))\b/gi;

function ruleRE002(ctx, unit) {
  let m;
  while ((m = SUPERLATIVE_RE.exec(unit.text))) {
    emit(ctx, unit, 'UE-RE002', m[0], m.index,
      `Superlative or ranking claim "${m[0]}" — the CLI cannot prove it is derived from the data shown.`,
      'Confirm the claim against the presented data or add a source, or use neutral wording.');
  }
}

const FIGURE_RE = /\b\d[\d,]*(?:\.\d+)?\s*(?:per cent|million|billion|trillion|thousand)\b|\b\d[\d,]*(?:\.\d+)?\s*%(?!\w)|\b\d{1,3}(?:,\d{3})+\b/g;
const HEDGE_RE = /\b(?:approximately|about|at least|an estimated|a reported|according to|estimated|reported|as of|based on|figures from|data from|source:|sources:)\b/i;
// The unit that makes a number a prose figure. `%` cannot be wrapped in \b:
// a word boundary never follows a percent sign, so "8%" used to match nothing
// and the rule silently skipped the commonest UN figure of all.
const FIGURE_WORD_RE = /\b(?:per cent|million|billion|trillion|thousand)\b|%/;

function ruleRE003(ctx, unit) {
  if (unit.compact) return;
  const clauses = unit.text.split(/(?<=[.!?;])\s+/);
  let cursor = 0;
  for (const clause of clauses) {
    const at = unit.text.indexOf(clause, cursor);
    cursor = at < 0 ? cursor : at + clause.length;
    if (HEDGE_RE.test(clause)) continue;
    FIGURE_RE.lastIndex = 0;
    const figure = FIGURE_RE.exec(clause);
    if (!figure) continue;
    // A bare thousands separator without a unit word is not a prose figure.
    if (!FIGURE_WORD_RE.test(figure[0])) continue;
    const index = (at < 0 ? 0 : at) + figure.index;
    emit(ctx, unit, 'UE-RE003', figure[0], index,
      `Figure "${figure[0]}" appears without a hedge or a source in the same sentence.`,
      'Add a hedge such as "approximately" and identify the source and reference date.');
  }
}

const QUESTION_START_RE = /^\s*(?:why|how|what|when|where|who|which|isn'?t|aren'?t|don'?t|doesn'?t|didn'?t|can'?t|won'?t|shouldn'?t|is|are|was|were|do|does|did|can|could|will|would|shall|should|may|might|have|has|had|ready|looking|wondering|imagine|did you|have you|do you|could you|would you|will you|can you)\b/i;

function ruleRE004(ctx, unit) {
  const sentences = unit.text.split(/(?<=[.!?])\s+/);
  let cursor = 0;
  for (const sentence of sentences) {
    const at = unit.text.indexOf(sentence, cursor);
    cursor = at < 0 ? cursor : at + sentence.length;
    if (!/\?\s*$/.test(sentence)) continue;
    if (!QUESTION_START_RE.test(sentence)) continue;
    const index = (at < 0 ? 0 : at) + sentence.search(/\S/);
    // `current` carries the whole question — up to its terminating . ! ? or
    // the end of the line/paragraph — capped at 300 characters with "..."
    // beyond, so the report shows what was actually written instead of a
    // 40-character prefix. Message, suggestion and severity are unchanged,
    // and no replacement is passed: the rule stays report-only, never
    // fixable (locked by tests/audit-detection.mjs).
    const full = sentence.trim();
    const current = full.length > 300 ? `${full.slice(0, 300)}...` : full;
    emit(ctx, unit, 'UE-RE004', current, index,
      'Question phrased for effect — UN copy states findings directly.',
      'Rewrite as a declarative statement unless the question is genuinely soliciting information.');
  }
}

function ruleRE005(ctx, unit) {
  const re = /(?<![=!<>])!+(?=\s|$|[.,;:?])/g;
  let m;
  while ((m = re.exec(unit.text))) {
    emit(ctx, unit, 'UE-RE005', m[0], m.index,
      'Exclamation mark in formal copy.',
      'Remove the exclamation mark and state the point in a measured tone.');
  }
}

// The counted-noun list is bounded and covers the nouns humanitarian and
// programme copy actually counts: populations, facilities and outcomes. A
// count of a noun outside the list is not reported — the rule asks a reviewer
// to look at recognised count phrases, it does not claim to see every one.
const COUNT_RE = /\b\d[\d,]*(?:\.\d+)?\s+(?:countries|states|members|reports|projects|offices|centres|centers|people|users|datasets|publications|indicators|sites|locations|refugees|children|women|men|cases|deaths|households|families|students|patients|personnel|staff|schools|hospitals|clinics|migrants|returnees|infections|volunteers|workers)\b/g;
const QUALIFIER_RE = /\b(?:member|reporting|with a value|drawable|on the map|at the time of writing|covered|as of|in total|total|estimated|around|about|more than|at least|up to|over|nearly|approximately|roughly)\b/i;

function ruleDI001(ctx, unit) {
  // The qualifier must sit in the count's own sentence: a hedge in the next
  // sentence must not cover an unqualified figure. Sentence bounds are found
  // once, then each count is tested against the sentence containing it.
  const sentences = [];
  let start = 0;
  const ends = /[.!?]+(?=\s|$)/g;
  let bound;
  while ((bound = ends.exec(unit.text))) {
    sentences.push([start, bound.index + bound[0].length]);
    start = bound.index + bound[0].length;
  }
  sentences.push([start, unit.text.length]);
  let m;
  while ((m = COUNT_RE.exec(unit.text))) {
    const sentence = sentences.find(([from, to]) => m.index >= from && m.index < to);
    if (!sentence || QUALIFIER_RE.test(unit.text.slice(sentence[0], sentence[1]))) continue;
    emit(ctx, unit, 'UE-DI001', m[0], m.index,
      `Count "${m[0]}" does not state what was counted or whether it is reported, estimated or total.`,
      'Label the figure, for example "reported" or "estimated", and say what was counted.');
  }
}

const YEAR_RE = /\b(?:19|20)\d{2}\b/g;
const COMPARISON_RE = /\b(?:compared to|compared with|versus|vs\.?|relative to|up from|down from|higher than|lower than|greater than|less than|more than|fewer than|increase(?:d)? from|decrease(?:d)? from|rose from|fell from|grew from|dropped from|exceeded|exceeds|outpaced|outpaces|outstripped|ahead of|year[- ]on[- ]year)\b/i;

function ruleCL001(ctx, unit) {
  const years = new Set(unit.text.match(YEAR_RE) || []);
  if (years.size < 2) return;
  const m = COMPARISON_RE.exec(unit.text);
  if (!m) return;
  emit(ctx, unit, 'UE-CL001', m[0], m.index,
    `Comparison references ${years.size} different years (${[...years].sort().join(', ')}).`,
    'Confirm the periods being compared are aligned and state them explicitly.');
}

// --- country names (UE-TE005) -------------------------------------------------

// Superseded country designations, matched case-sensitively against the
// profile's UE-TE005 terminology pairs. Case sensitivity is the guard: the
// lowercase "turkey" is the bird and must never fire, so only the exact
// written form and the all-caps heading form are the country name. The
// proper-name exemption is deliberately narrower than the spelling rule's: a
// match preceded by a capitalised word is a name-internal position ("North
// Macedonia", "North Holland", "Wild Turkey") and never fires, but the
// lookahead stops there — "Burma and Turkey" is a list of countries, not one
// long proper name, and the guard must not silence it.
function ruleTE005(ctx, unit) {
  const allow = new Set(ctx.cfg.allowlist.terminology || []);
  if (!enabled(ctx, 'UE-TE005')) return;
  for (const entry of ctx.vocab.terminology) {
    if (entry.rule !== 'UE-TE005') continue;
    if (allow.has(entry.from)) continue;
    const re = new RegExp(`\\b${escapeRe(entry.from)}\\b|\\b${escapeRe(entry.from.toUpperCase())}\\b`, 'g');
    let m;
    while ((m = re.exec(unit.text))) {
      const prev = unit.text.slice(0, m.index).match(/([A-Za-zÀ-ÖØ-öø-ÿ][\w'’.-]*)\s*$/);
      if (prev && isCapitalised(prev[1])) continue;
      emit(ctx, unit, 'UE-TE005', m[0], m.index,
        `The country name "${m[0]}" is superseded; the current United Nations form is "${entry.to}".`,
        `Write "${entry.to}".`,
        { proposed: entry.to });
    }
  }
}

// --- contested claims ---------------------------------------------------------

/**
 * Attribution turns a bare assertion into a report of a party's position:
 * "Pakistan claims that Kashmir is part of Pakistan" names who advances the
 * claim, which is exactly what the rule asks copy to do. The window is the
 * current sentence — text after the last [.!?;] before the match — because a
 * reporting verb several sentences earlier attributes nothing here. The guard
 * runs before any emission: for an error rule, a suppressed false positive is
 * preferable to a false claim of defect, so joined trailing attribution
 * ("…, the minister said") is recognised as well as leading attribution.
 *
 * The verb list covers full stem families — every inflection of a reporting
 * verb exempts (`states/stated/stating`, `confirms/confirmed/confirming`,
 * `observes/observed/observing`, `tells/told/telling`, `underlines/…`,
 * `highlights/…`, `comments/…`, `warns/warned/warning`, `remarks/…`,
 * `explains/…`, `clarifies/…`) — so exempting one inflection never leaves a
 * sibling form reporting a false defect. Trailing attribution takes the
 * first six words of the tail after the claim, with the joining comma (or
 * dash, or quote) optional: a verb further away describes something else,
 * not who advances the claim. The guard-note pages (rules/diplomacy.md,
 * rules/hate-speech.md) give examples rather than a verb inventory; this
 * comment is the canonical enumeration.
 */
const ATTRIBUTION_RE = /\b(?:says?|said|states?|stating|stated|claims?|claimed|claiming|maintains?|maintained|argues?|argued|contends?|contended|alleges?|alleged|asserts?|asserted|insists?|insisted|noted|confirms?|confirmed|confirming|observes?|observed|observing|tells?|told|telling|underlines?|underlined|underlining|highlights?|highlighted|highlighting|comments?|commented|commenting|warns?|warned|warning|remarks?|remarked|remarking|explains?|explained|explaining|clarifies?|clarified|clarifying|according\s+to|denies|denied|rejects?|rejected|wrote|written|writes|reiterates?|reiterated|emphasizes?|emphasises?|stresses|stressed)\b/i;

export function attributedClaim(text, index, length) {
  const before = text.slice(0, index);
  const sentenceStart = Math.max(
    before.lastIndexOf('.'), before.lastIndexOf('!'),
    before.lastIndexOf('?'), before.lastIndexOf(';'));
  if (ATTRIBUTION_RE.test(before.slice(sentenceStart + 1))) return true;
  const after = text.slice(index + length);
  const end = after.search(/[.!?]/);
  const tail = end < 0 ? after : after.slice(0, end);
  // Trailing attribution: the joining punctuation is optional, and the verb
  // must sit within the first six words after the claim.
  const window = tail.replace(/^[\s"'“”‘’),;:–—-]+/, '').split(/\s+/).slice(0, 6).join(' ');
  return ATTRIBUTION_RE.test(window);
}

function ruleDP001(ctx, unit) {
  for (const claim of ctx.vocab.claims) {
    for (const re of claim.patterns) {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(unit.text))) {
        if (attributedClaim(unit.text, m.index, m[0].length)) continue;
        emit(ctx, unit, 'UE-DP001', m[0], m.index,
          `Contested status claim "${m[0]}" about ${claim.topic} stated as fact.`,
          `Attribute the claim to the party advancing it or use neutral wording: "${claim.neutral}" `
          + `(UN terminology: "${claim.unTerminology}"; source: ${claim.source}).`,
          { proposed: claim.neutral });
      }
    }
  }
}

// --- review heuristics (UE-HR001..HR005) -------------------------------------
//
// Five review-only heuristics: deterministic pattern checks whose verdicts
// are opinions about prose, not grammar facts, so every one is registered at
// warning severity and emits no `replacement` — none of them can ever join
// the --fix allow-list (tests/audit-fix-set.mjs probes fail-closed over
// every catalogue rule, future ones included). The gates below are
// deliberately narrow: each trades misses for fewer false positives, and
// the full limitation text lives in the catalogue guardNotes beside the
// rule it constrains. All five read authored (or, for headings, authored or
// navigation) copy only — code, metadata and quoted contexts are the
// extraction layer's, not the heuristics'.

// Auxiliaries and modals: their presence proves the sentence has a verb.
const HR_AUX = new Set([
  'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
  'has', 'have', 'had', 'do', 'does', 'did',
  'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
  'ought', 'cannot',
]);

// Curated base and irregular verbs. The list is generous on purpose — every
// added word can only silence a firing, never create one — because the
// suffix test below misses base forms ("Restart the service.") and irregular
// pasts that end in neither -ed nor -t-shaped endings ("The vote rose.").
// Ambiguous words that are nouns at least as often as verbs — report, note,
// state, plan, brief, review — stay OFF the list so noun-phrase fragments
// such as "The annual report on the situation." keep firing. This comment
// is the canonical enumeration; the guardNote points here.
const HR_BASE_VERBS = new Set([
  'run', 'read', 'install', 'use', 'see', 'check', 'try', 'add', 'remove', 'set', 'get',
  'make', 'take', 'give', 'write', 'open', 'close', 'start', 'stop', 'help', 'ensure',
  'require', 'provide', 'include', 'support', 'enable', 'disable', 'allow', 'apply', 'build',
  'change', 'create', 'delete', 'download', 'update', 'upload', 'test', 'deploy', 'copy', 'paste',
  'edit', 'save', 'exit', 'return', 'print', 'list', 'show', 'hide', 'select', 'click',
  'type', 'enter', 'submit', 'confirm', 'cancel', 'accept', 'reject', 'approve', 'point', 'said',
  'met', 'went', 'say', 'goes', 'go', 'come', 'came', 'rose', 'restart', 'rerun',
  'clean', 'held', 'fell', 'ran', 'grew', 'began', 'brought', 'thought', 'caught', 'led',
  'built', 'sent', 'left', 'kept', 'lost', 'felt', 'put', 'cut', 'won', 'began',
]);

/**
 * True when a sentence looks like a phrase standing where a sentence should
 * be: it ends in a full stop, is five to eight words long, and carries no
 * verb signal of any kind. Each gate suppresses a known false-positive
 * shape — commas and parentheses mean hidden structure, an abbreviation
 * tail means the sentence splitter cut a dotted form ("... via St."), a
 * repeated content word of five letters or more marks deliberate parallel
 * phrasing such as term demonstrations, and word counts outside the window
 * are simply not judgeable either way. The gates are per sentence; a
 * verbless sentence whose verb the list misses is the residual false
 * positive, and the curated list is the knob that trades against it.
 */
function hrFragmentSuspect(sentence) {
  if (!sentence.endsWith('.') || sentence.endsWith('...')) return false;
  // Tail of a dotted abbreviation split off by the sentence boundary:
  // "St.", "e.g.", "U.S.A." — letters only, four or fewer, with a period.
  const tail = (sentence.match(/[A-Za-z.]+$/) || [''])[0];
  if (tail.includes('.') && tail.replace(/\./g, '').length <= 4) return false;
  if (sentence.includes('(') || sentence.includes(')')) return false;
  const words = sentence.match(/[\w'-]+/g) || [];
  if (words.length < 5 || words.length > 8) return false;
  if (sentence.includes(',')) return false;
  const tally = new Map();
  for (const word of words) {
    const lower = word.toLowerCase();
    if (HR_AUX.has(lower)) return false;
    if (/(?:s|ed|ing)$/.test(lower)) return false;
    if (HR_BASE_VERBS.has(lower)) return false;
    if (lower.length >= 5) tally.set(lower, (tally.get(lower) || 0) + 1);
  }
  for (const count of tally.values()) if (count >= 2) return false;
  return true;
}

function ruleHR001(ctx, unit) {
  if (unit.context !== 'authored' || unit.heading || unit.listItem || unit.compact) return;
  const sentences = unit.text.split(/(?<=[.!?])\s+/);
  let cursor = 0;
  for (const sentence of sentences) {
    const at = unit.text.indexOf(sentence, cursor);
    cursor = at < 0 ? cursor : at + sentence.length;
    if (!hrFragmentSuspect(sentence)) continue;
    emit(ctx, unit, 'UE-HR001', sentence, at,
      `Sentence-like fragment "${sentence}" reads as a phrase without a finite verb (heuristic).`,
      'Add a finite verb, or merge the fragment into the surrounding sentence.');
    return; // one finding per unit: the first offending sentence only
  }
}

// The three tight collocations. The lookahead keeps the idiomatic
// "would of course" out; everything else after a modal "of" is malformed.
const HR002_RES = [
  /\b(?:could|would|should|must|might|shall)\s+of\b(?!\s+course\b)/gi,
  /\b(?:had|have|has|did)\s+went\b/gi,
  /\b(?:more|less)\s+(?:better|worse)\b/gi,
];

function hr002Suggestion(matched) {
  if (/\b(?:could|would|should|must|might|shall)\s+of\b/.test(matched)) {
    return `Write "${matched.replace(/\s+of\b/, ' have')}" — the verb is "have".`;
  }
  if (/\bwent\b/.test(matched)) {
    return `Use a standard past form, for example "had gone" instead of "${matched}".`;
  }
  return `Use "${matched.split(/\s+/)[1]}" on its own, or "more ..." with a noun.`;
}

function ruleHR002(ctx, unit) {
  if (unit.context !== 'authored') return;
  for (const re of HR002_RES) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(unit.text))) {
      emit(ctx, unit, 'UE-HR002', m[0], m.index,
        `Malformed wording "${m[0]}" — non-standard English form.`,
        hr002Suggestion(m[0]));
      // Guidance only: no `replacement` override, so the rule is never fixable.
    }
  }
}

// The second form of UE-HR003: a whole authored block repeated verbatim later
// in the same file.
//
// A *block* here is the visual paragraph, not the extracted unit. An inline
// element splits a paragraph's text into several units — `<strong>` or `<a>`
// breaks the text node — so comparing units alone let markup hide an exact
// repeat: the two copies were the same copy, but no single unit reached the
// word floor, so the duplication went unreported. The block is therefore
// reassembled and compared whole, with the floor unchanged.
//
// Built once per run and keyed by file, because a unit's rule call has no view
// of its siblings; the WeakMap hangs off the run's own context object, so a
// second scan in the same process starts empty and gives the same answer as the
// first. `pending` is the block being assembled — units arrive one at a time, so
// a split paragraph is only comparable once its last piece has arrived — and
// `seen` maps each block already met in the file to the line it was first seen
// at.
const REPEATED_BLOCKS = new WeakMap();

function repeatedBlocks(state) {
  let store = REPEATED_BLOCKS.get(state);
  if (!store) {
    store = { pending: null, seen: new Map() };
    REPEATED_BLOCKS.set(state, store);
  }
  return store;
}

// Add one unit to the block being assembled, and compare each block as it
// completes.
//
// The extractors supply the two fields this reads: `block` is the block a unit
// came from, and `blockLast` marks that block's final unit. A unit with neither
// comes from an extractor that reports no block structure, so it is its own
// block — the unit-at-a-time comparison, unchanged.
function collectBlock(state, unit) {
  const store = repeatedBlocks(state);
  // Keyed by file as well as block. A block id is a source offset, and offsets
  // restart at zero in every file, so a key of the offset alone would let the
  // second file of a scan continue the first file's open paragraph — and a
  // genuine repeat would then be reported or missed depending on which other
  // files happened to be in the run.
  const key = `${unit.file} ${unit.block === undefined ? unit.offset : unit.block}`;

  if (store.pending && store.pending.key !== key) {
    compareBlock(state, store.pending);
    store.pending = null;
  }

  if (!store.pending) {
    store.pending = { key, file: unit.file, units: [] };
  }
  store.pending.units.push(unit);
  if (unit.block === undefined || unit.blockLast) {
    compareBlock(state, store.pending);
    store.pending = null;
  }
}

function compareBlock(state, pending) {
  const { units } = pending;
  // Judged only when every part of it is eligible copy. A heading, a quoted or
  // navigation run, or a compact table unit inside the block disqualifies the
  // block whole, exactly as it disqualifies the unit alone: a long string
  // repeated in those surfaces is legitimate, and reporting it would put a
  // finding on correct copy. Copy from an attribute value is the exception: an
  // image inside a paragraph does not make the paragraph two paragraphs, so that
  // copy is carried by the block and left out of its running text.
  for (const unit of units) {
    if (unit.attribute) continue;
    if (unit.heading || unit.compact || unit.context !== 'authored') return;
  }
  // The pieces joined on what a reader sees between them, which the extractor
  // measured: nothing where an inline element broke a word, a space where one
  // sat between two whole words. A fixed space would turn `humanit<mark>arian`
  // into two words and miss the plain copy of the paragraph.
  const parts = units.filter((unit) => !unit.attribute);
  let text = '';
  for (const unit of parts) {
    if (text) text += unit.joiner === undefined ? ' ' : unit.joiner;
    text += unit.text;
  }
  const block = normaliseForRepetition(text);
  const words = block.split(' ');
  if (words.length < REPEATED_BLOCK_MIN_WORDS) return;

  const key = `${pending.file} ${block}`;
  const first = repeatedBlocks(state).seen.get(key);
  if (first !== undefined) {
    // Reported against the block's last unit, so the finding lands on the copy
    // on the page rather than in the middle of a split one.
    emit(state, units[units.length - 1], 'UE-HR003', text.slice(0, 300), 0,
      `A block of ${words.length} words is repeated verbatim in this file (first seen at line ${first}).`,
      'Remove the repeated block, or replace the repetition with a cross-reference.');
    return;
  }
  repeatedBlocks(state).seen.set(key, units[0].line);
}

// Twenty words. The boundary is the length at which an exact textual match
// stops being a coincidence and starts being a copy-paste, and it is set above
// the cross-referencing range rather than tuned to a corpus: below it, two
// paragraphs sharing a sentence ("see the paragraph above", a repeated
// recommendation) are ordinary editorial practice, and reporting them would put
// a finding on correct copy. Measured over this repository and both corpora —
// 479 candidate blocks in 168 files — twenty words yielded exactly one
// duplicate, the inserted paragraph in .feedbacks/v8/web/01.
const REPEATED_BLOCK_MIN_WORDS = 20;

function normaliseForRepetition(text) {
  return text.toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
}

function ruleHR003(ctx, unit) {
  // Every unit takes part in the block bookkeeping, including the ones this rule
  // would otherwise ignore, because a block is closed by its last unit whatever
  // that unit's context is. A paragraph ending in an image whose `title` is
  // navigation copy is closed by that title unit; skip ineligible units here and
  // the block stays open, and the next file's copy is appended to it. The
  // eligibility test itself is in `compareBlock`, which rejects a block that any
  // part of it disqualifies — so an ineligible unit still closes its block, it
  // just never contributes a finding.
  collectBlock(ctx, unit);
  // Tables are compact units: identical advice in two rows is legitimate.
  if (unit.context !== 'authored' || unit.compact) return;
  const seen = new Set();
  let cursor = 0;
  for (const sentence of unit.text.split(/(?<=[.!?])\s+/)) {
    const at = unit.text.indexOf(sentence, cursor);
    cursor = at < 0 ? cursor : at + sentence.length;
    const normalised = normaliseForRepetition(sentence);
    if (!normalised) continue;
    if (normalised.split(' ').length < 4) continue; // too short to judge
    if (seen.has(normalised)) {
      emit(ctx, unit, 'UE-HR003', sentence, at < 0 ? 0 : at,
        `Sentence repeated in the same block: "${sentence.slice(0, 120)}"`,
        'Remove the repetition or vary the second occurrence.');
      return; // one finding per block keeps the report readable
    }
    seen.add(normalised);
  }
}

function ruleHR004(ctx, unit) {
  if (!unit.heading) return;
  if (unit.context !== 'authored' && unit.context !== 'nav') return;
  const m = /[.;]\s*$/.exec(unit.text);
  if (!m) return;
  emit(ctx, unit, 'UE-HR004', unit.text, 0,
    `Heading ends in "${m[0].trim()}" — headings read as labels, not sentences.`,
    'Drop the final full stop or semicolon from the heading.');
}

const HR005_RE = /["“”‘]/g;

function ruleHR005(ctx, unit) {
  // Balanced pairs are already masked by the extractors, so anything left
  // here has no partner; apostrophes (’ and ') are never partners to find.
  if (unit.context === 'code' || unit.compact) return;
  let m;
  while ((m = HR005_RE.exec(unit.text))) {
    emit(ctx, unit, 'UE-HR005', m[0], m.index,
      `Unpaired quotation mark "${m[0]}" — no closing partner in the same unit.`,
      'Close the quotation with a matching mark, or remove the stray one.');
  }
}

// --- organisation custom rules ------------------------------------------------

// The profile's own pattern checks, run per unit like every other rule. Each
// match cap bounds a runaway pattern; suppression works unchanged because the
// emit path matches on the rule id, whatever namespace it comes from. Custom
// rules never carry a replacement, so --fix cannot reach them by construction.
const CUSTOM_MATCH_CAP = 100;

function ruleCustomRules(state, unit) {
  for (const rule of state.vocab.customRules || []) {
    rule.re.lastIndex = 0;
    let m;
    let matches = 0;
    while ((m = rule.re.exec(unit.text))) {
      if (m[0].length === 0) rule.re.lastIndex += 1; // zero-width guard
      if (matches >= CUSTOM_MATCH_CAP) break;
      matches += 1;
      emit(state, unit, rule.id, m[0], m.index,
        rule.message,
        rule.suggestion,
        {
          severity: rule.severity,
          confidence: 'deterministic',
          category: 'organisation',
          source: rule.source
            ? `${rule.source} (organisation profile rule ${rule.id})`
            : `organisation profile rule ${rule.id}`,
        });
    }
  }
}

// --- file-level review heuristics (UE-HR006, UE-HR007) ------------------------
//
// Two checks that can only judge a whole document: whether an acronym is ever
// expanded anywhere in it, and whether the copy is English at all. Both run
// after the per-unit loop, over the authored units of each file, and both are
// review findings — heuristic confidence, never fixable, never a verdict on
// the copy beyond the narrow claim the message states.

// Pure uppercase letter runs of three or more. Digits and hyphens are out:
// COVID-19, G7 and H1N1 are not the acronym shapes this rule judges, and a
// dotted form (U.S.A.) never matches \b[A-Z]{3,}\b in the first place.
const ACRONYM_TOKEN_RE = /\b[A-Z]{3,5}\b/g;

// A bare acronym is "expanded" when a word sequence whose initials spell the
// acronym sits within the window around one of its parenthetical uses. Small
// connective words inside an expansion (of, the, and) are NOT bridged — the
// initials must be contiguous — which is the conservative reading and a
// documented limitation: expansions like "United Nations High Commissioner
// for Refugees (UNHCR)" match, "Office for the Coordination of Humanitarian
// Affairs (OCHA)" does not, because its initials are interrupted.
const EXPANSION_WINDOW = 200;

function acronymExpansionWords(acronym) {
  return acronym.split('').map(letter => `[A-Z][a-z'’]*`).join('\\s+');
}

function acronymIsExpanded(text, acronym) {
  const wordSeq = acronymExpansionWords(acronym);
  const paren = new RegExp(`\\(${escapeRe(acronym)}\\)`, 'g');
  let m;
  while ((m = paren.exec(text))) {
    const before = text.slice(Math.max(0, m.index - EXPANSION_WINDOW), m.index);
    const after = text.slice(m.index + m[0].length, m.index + m[0].length + EXPANSION_WINDOW);
    if (new RegExp(`\\b${wordSeq}`).test(before)) return true;
    if (new RegExp(`\\b${wordSeq}`).test(after)) return true;
  }
  return false;
}

const LANGUAGE_STOPWORDS = new Set([
  'the', 'of', 'and', 'to', 'in', 'a', 'is', 'that', 'for', 'it', 'with', 'as',
  'was', 'on', 'are', 'by', 'an', 'be', 'or', 'from', 'this', 'which', 'at',
  'has', 'have', 'will', 'their', 'they', 'been', 'more', 'than', 'who', 'its',
  'can', 'may', 'other', 'new', 'some', 'would', 'these', 'also', 'not', 'but',
  'we', 'our', 'us', 'all', 'one', 'two', 'per', 'into', 'over', 'between',
  'during', 'under', 'after', 'before', 'where', 'when', 'while', 'both',
  'each', 'such', 'most', 'many',
]);

// Forty words and a six per cent stop-word rate, judged per paragraph: below
// the floor the passage is too short to judge, and under the rate no English
// paragraph of that length has yet been seen, while French, Spanish and German
// prose sits far below it.
const LANGUAGE_MIN_WORDS = 40;
const LANGUAGE_MIN_RATE = 0.06;

function runFileLevelReview(state) {
  const byFile = new Map();
  for (const unit of state.units) {
    if (unit.context !== 'authored' || unit.compact) continue;
    if (!byFile.has(unit.file)) byFile.set(unit.file, []);
    byFile.get(unit.file).push(unit);
  }

  for (const [file, units] of byFile) {
    // The consistency review is configuration-gated (consistencyReview): a
    // house style may deliberately mix conventions across files, and the
    // review exists to police one document's internal consistency.
    if (state.cfg.consistencyReview && enabled(state, 'UE-HR008')) {
      let straight = null;
      let curly = null;
      for (const unit of units) {
        if (!unit.raw) continue;
        // Balanced pairs reach raw untouched (masking happens downstream), so
        // a paired straight mark and a paired curly mark in one file are both
        // visible here. Unpaired marks belong to UE-HR005.
        straight = straight || /"[^"\n]+"/.exec(unit.raw);
        curly = curly || /\u201c[^\u201d\n]+\u201d/.exec(unit.raw);
      }
      if (straight && curly) {
        const at = units[0];
        emit(state, at, 'UE-HR008', 'straight and typographic quotation marks', 0,
          'Both straight ("...") and typographic ("...") quotation marks are used in this document.',
          'Choose one quotation style for the document and apply it consistently.',
          { proposed: null });
      }
    }

    if (state.cfg.consistencyReview && enabled(state, 'UE-HR009')) {
      let commaGrouped = null;
      let spaceGrouped = null;
      for (const unit of units) {
        commaGrouped = commaGrouped || /\b\d{1,3}(,\d{3})+\b/.exec(unit.text);
        spaceGrouped = spaceGrouped || /\b\d{1,3}( \d{3})+\b(?![-/.\d])/.exec(unit.text);
      }
      if (commaGrouped && spaceGrouped) {
        const at = units[0];
        emit(state, at, 'UE-HR009', 'mixed thousands separators', 0,
          `Both comma-grouped ("${commaGrouped[0]}") and space-grouped ("${spaceGrouped[0]}") numbers are used in this document.`,
          'Choose one grouping convention for the document and apply it consistently.',
          { proposed: null });
      }
    }

    if (enabled(state, 'UE-HR006')) {
      // Allowlisted acronyms are project decisions, exactly like spelling
      // allowlists: a name the house treats as a word is never reported.
      const allow = new Set(state.cfg.allowlist.acronyms || []);
      const seen = new Map(); // acronym -> { unit, index }
      const full = units.map(unit => unit.text).join(' \n ');
      for (const unit of units) {
        ACRONYM_TOKEN_RE.lastIndex = 0;
        let m;
        while ((m = ACRONYM_TOKEN_RE.exec(unit.text))) {
          if (seen.has(m[0]) || allow.has(m[0]) || CAPS_EXEMPT.has(m[0])) continue;
          // A token that names a file (CHANGELOG.md, README.html) is not an
          // acronym: the same extension guard the all-caps register rule uses.
          if (/^\.[a-z0-9]{1,4}\b/.test(unit.text.slice(m.index + m[0].length))) continue;
          // A token in a version or figure position ("PHP 8+", "ISO 9001") is
          // a technical designation, not prose to expand.
          if (/^ ?\d/.test(unit.text.slice(m.index + m[0].length))) continue;
          seen.set(m[0], { unit, index: m.index });
        }
      }
      for (const [acronym, at] of seen) {
        if (acronymIsExpanded(full, acronym)) continue;
        emit(state, at.unit, 'UE-HR006', acronym, at.index,
          `Acronym "${acronym}" is never expanded in this document.`,
          'Spell it out at first use, for example "United Nations Development Programme (UNDP)".',
          { proposed: null });
      }
    }

    if (enabled(state, 'UE-HR007')) {
      // Judged per paragraph, not per file: United Nations documents are
      // routinely bilingual in passing (a quoted title, a foreign-language
      // closing), so a whole-file ratio would stay silent exactly when one
      // long non-English passage needs the note — and would fire on a mixed
      // file whose English majority is fine.
      for (const unit of units) {
        const words = unit.text.match(/[A-Za-zÀ-ÿ]+/g) || [];
        if (words.length < LANGUAGE_MIN_WORDS) continue;
        const hits = words.filter(word => LANGUAGE_STOPWORDS.has(word.toLowerCase())).length;
        if (hits / words.length < LANGUAGE_MIN_RATE) {
          emit(state, unit, 'UE-HR007', unit.text.slice(0, 80), 0,
            `This paragraph does not appear to be English (${hits} common English words in ${words.length}); the rules are written for English copy and the results here may be unreliable.`,
            'Check the paragraph in its own language tooling, or run the check on an English version.',
            { proposed: null });
        }
      }
    }
  }
}

const RULE_BY_ID = {
  'UE-SP001': ruleSP001,
  'UE-SP002': ruleSP002,
  'UE-SP003': ruleSP003,
  'UE-TE003': ruleTE003,
  'UE-TE004': ruleTE004,
  'UE-TE005': ruleTE005,
  'UE-NU001': ruleNU001,
  'UE-NU002': ruleNU002,
  'UE-RE001': ruleRE001,
  'UE-RE002': ruleRE002,
  'UE-RE003': ruleRE003,
  'UE-RE004': ruleRE004,
  'UE-RE005': ruleRE005,
  'UE-DI001': ruleDI001,
  'UE-CL001': ruleCL001,
  'UE-DP001': ruleDP001,
  'UE-HR001': ruleHR001,
  'UE-HR002': ruleHR002,
  'UE-HR003': ruleHR003,
  'UE-HR004': ruleHR004,
  'UE-HR005': ruleHR005,
  ...HS_RULES,
  ...TONE_RULES,
  ...GRAMMAR_RULES,
};

/**
 * @param {Array} units  extracted copy spans (any file)
 * @param {object} ctx   { meta, cfg, vocab } — see lib/config.mjs
 * @param {object} extraRules  test-only rule registry merged over RULE_BY_ID
 *                             (used by lib/testkit.mjs during rule development;
 *                             production callers pass nothing).
 */
export function runEditorialRules(units, ctx, extraRules = {}) {
  // The per-run state the rules see. `profileSelected`/`profileName` carry the
  // profile choice down to UE-SP001, whose stance depends on it.
  const state = {
    findings: [], meta: ctx.meta, cfg: ctx.cfg, vocab: ctx.vocab,
    profileSelected: ctx.profileSelected, profileName: ctx.profileName,
    units: [],
  };
  const registry = { ...RULE_BY_ID, ...extraRules };
  const extraIds = Object.keys(extraRules).filter((id) => !EDITORIAL_RULES[id]);
  const ruleIds = extraIds.length ? [...EDITORIAL_RULE_IDS, ...extraIds] : EDITORIAL_RULE_IDS;

  for (const unit of units) {
    state.units.push(unit);
    const unitSuppression = suppression(unit);
    if (unitSuppression && unitSuppression.all) continue;
    for (const ruleId of ruleIds) {
      if (!enabled(state, ruleId)) continue;
      if (ruleId === 'UE-TE001' || ruleId === 'UE-TE002') continue; // handled together below
      const run = registry[ruleId];
      if (run) run(state, unit);
    }
    if (enabled(state, 'UE-TE001') || enabled(state, 'UE-TE002')) ruleTerminology(state, unit);
    if (state.vocab.customRules.length) ruleCustomRules(state, unit);
  }

  // Whole-document review heuristics: acronym expansion and language.
  runFileLevelReview(state);

  const seen = new Set();
  const findings = [];
  for (const finding of state.findings) {
    const key = `${finding.file}:${finding.line}:${finding.column}:${finding.ruleId}`;
    if (seen.has(key)) continue;
    seen.add(key);
    findings.push(finding);
  }
  findings.sort((a, b) =>
    a.file.localeCompare(b.file) || a.line - b.line || a.column - b.column ||
    a.ruleId.localeCompare(b.ruleId));
  return findings;
}
