// User-supplied glossary: the reader's own required and forbidden terminology.
//
// A glossary is not a United Nations rule. It is one organisation's house
// vocabulary, imported from a JSON file the reader wrote (`--glossary <path>`
// or the `glossary` key in `.un-editorial.json`), and everything downstream
// says so: the finding id is UE-GL001/UE-GL002, the lane is `audit`, the
// message names the file the term came from, and the catalogue entry labels
// the source as user-supplied.
//
// Three properties are deliberate and load-bearing:
//
//   * Fail closed. A missing file, a file that is not a regular file, invalid
//     JSON, a duplicate key, an unknown field, a wrong type, an empty term, a
//     term that can never match, or a replacement that names no forbidden term
//     is a refusal (exit code 2) with a message naming the problem — never a
//     silently reduced rule set.
//   * Never auto-rewritable. Terminology is NEVER_AUTO (remediation brief §8):
//     a glossary finding never passes a `_replacement`, so `--fix` cannot reach
//     it even by accident, and its rule ids are absent from the fixable
//     allow-list, so a future replacement on the finding would still not be
//     applied. The preferred wording in `replacements` is guidance printed in
//     the report, never an edit.
//   * Positions are the engine's. Findings are emitted through lib/rules.mjs's
//     `emit`, so a glossary match is located inside the extracted copy span,
//     honours `ue:ignore` suppression and `config.severities` / `config.rules`
//     exactly like every other rule.
//
// Matching is deliberately conservative: terms match case-insensitively on
// whole words, and only inside the copy spans the extractors produced, so
// quoted, cited, code, URL and comment regions are structurally out of reach
// (they are masked before any rule reads them).

import fs from 'node:fs';
import path from 'node:path';

import { ProfileError, parseJsonStrict } from './profile.mjs';
import { emit, enabled, escapeRe } from './rules.mjs';
import { lineStarts } from './position.mjs';

export class GlossaryError extends Error {}

export const GLOSSARY_FIELDS = new Set([
  'glossaryVersion', 'name', 'requiredTerms', 'forbiddenTerms', 'replacements',
]);

/** Catalogue rule ids, in catalogue order. Registered in rules/catalogue.json. */
export const GLOSSARY_RULE_IDS = ['UE-GL001', 'UE-GL002'];

/**
 * The audit lane is the name the finding carries, so the text report prints
 * `OPTIONAL AUDIT — glossary` and the PDF prints `Audit: glossary`. It is the
 * same shape the bundled audit profiles use, and it means what they mean: a
 * declared check that never decides the exit code.
 */
export const GLOSSARY_LANE_NAME = 'glossary';

const isPlainObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);
const nonEmpty = (value) => typeof value === 'string' && value.trim().length > 0;

// A term with no word character can never match a \b-delimited pattern, so it
// would be a silent no-op. Refusing it is the honest reading of "empty entry".
const MATCHABLE = /[\p{L}\p{N}_]/u;

function termList(value, label) {
  if (value === undefined) return [];
  if (!Array.isArray(value)) throw new GlossaryError(`${label} must be an array`);
  return value.map((term, index) => {
    if (!nonEmpty(term)) {
      throw new GlossaryError(`${label}[${index}] must be a non-empty string`);
    }
    if (!MATCHABLE.test(term)) {
      throw new GlossaryError(
        `${label}[${index}] ("${term}") contains no letter, digit or underscore, so it can never match`);
    }
    return term;
  });
}

/**
 * Whole-word, case-insensitive occurrence matcher, built the same way the
 * terminology rules build theirs (lib/rules.mjs `wordRe`) so a glossary entry
 * and a profile term behave identically. It is global, so it is only ever read
 * through `matchAll`, which clones before iterating.
 */
function wordMatcher(term) {
  return new RegExp(`\\b${escapeRe(term)}\\b`, 'gi');
}

/**
 * Presence matcher for required terms. Whitespace between the words of a
 * phrase is flexible, because a required phrase split by a line break or by a
 * masked span is still the phrase: this test only decides presence, never a
 * position, so the looser pattern cannot produce a mis-located finding. It can
 * only ever under-report an absence, which is the safe direction.
 */
function presenceMatcher(term) {
  return new RegExp(`\\b${term.trim().split(/\s+/).map(escapeRe).join('\\s+')}\\b`, 'i');
}

/**
 * Load, validate and compile a glossary file. Fail-closed throughout: every
 * problem is a GlossaryError, which the CLI turns into exit code 2.
 *
 * @param {string} file  path as given (used verbatim in every message, so the
 *                       report names the file the reader wrote)
 * @param {object} [options]
 * @param {string} [options.cwd]  base for a relative path, like every other path
 * @returns {object} frozen, compiled glossary
 */
export function loadGlossary(file, { cwd = process.cwd() } = {}) {
  if (!nonEmpty(file)) throw new GlossaryError('--glossary requires a value');
  const resolved = path.resolve(cwd, file);
  const label = `glossary ${file}`;

  let stat;
  try {
    stat = fs.statSync(resolved);
  } catch (err) {
    throw new GlossaryError(`${label} cannot be read: ${err.message}`);
  }
  if (!stat.isFile()) throw new GlossaryError(`${label} is not a regular file`);

  const raw = parseJsonStrict(fs.readFileSync(resolved, 'utf8'), label);

  if (!isPlainObject(raw)) throw new GlossaryError(`${label} must be a JSON object`);
  const unknown = Object.keys(raw).filter(key => !GLOSSARY_FIELDS.has(key));
  if (unknown.length) throw new GlossaryError(`${label} contains unknown fields: ${unknown.join(', ')}`);
  if (raw.glossaryVersion !== 1) {
    throw new GlossaryError(`${label} must declare glossaryVersion 1`);
  }
  if ('name' in raw && !nonEmpty(raw.name)) {
    throw new GlossaryError(`${label}.name must be a non-empty string`);
  }

  const required = termList(raw.requiredTerms, `${label}.requiredTerms`);
  const forbidden = termList(raw.forbiddenTerms, `${label}.forbiddenTerms`);
  if (!required.length && !forbidden.length) {
    throw new GlossaryError(
      `${label} declares no terms: requiredTerms and forbiddenTerms are both empty`);
  }

  // `replacements` is guidance, and guidance for a term that is not forbidden
  // is a mistake worth reporting: it would read as a preference with nothing
  // to attach to.
  let replacements = {};
  if (raw.replacements !== undefined) {
    if (!isPlainObject(raw.replacements)) {
      throw new GlossaryError(`${label}.replacements must be an object`);
    }
    const forbiddenSet = new Set(forbidden);
    for (const [term, preferred] of Object.entries(raw.replacements)) {
      if (!nonEmpty(term)) {
        throw new GlossaryError(`${label}.replacements has an empty term`);
      }
      if (!nonEmpty(preferred)) {
        throw new GlossaryError(`${label}.replacements["${term}"] must be a non-empty string`);
      }
      if (!forbiddenSet.has(term)) {
        throw new GlossaryError(
          `${label}.replacements has a key that is not a forbidden term: "${term}"`);
      }
      replacements[term] = preferred;
    }
  }

  const duplicate = (list) => {
    const seen = new Set();
    for (const term of list) {
      const key = term.toLowerCase();
      if (seen.has(key)) {
        throw new GlossaryError(`${label} lists "${term}" more than once`);
      }
      seen.add(key);
    }
  };
  duplicate(required);
  duplicate(forbidden);

  return Object.freeze({
    file,
    resolved,
    name: raw.name ?? null,
    label: raw.name ? `"${raw.name}"` : 'with no declared name',
    // `present` is the loose presence pattern for required terms and `re` the
    // global occurrence pattern for forbidden ones. Both are global but are
    // only ever read through String.prototype.matchAll, which clones the
    // pattern before iterating: a shared compiled glossary therefore carries
    // no scan state between units, files or runs.
    required: Object.freeze(required.map(term =>
      Object.freeze({ term, present: presenceMatcher(term) }))),
    forbidden: Object.freeze(forbidden.map(term =>
      Object.freeze({ term, re: wordMatcher(term, 'gi'), use: replacements[term] ?? null }))),
  });
}

/** A file-level anchor: line 1, column 1 of the named file. */
function fileAnchor(file) {
  return {
    file,
    text: '',
    raw: '',
    offset: 0,
    starts: lineStarts(''),
    context: 'authored',
  };
}

/**
 * Run the two glossary rules over the extracted copy of a scan.
 *
 * @param {Array} units    extracted copy spans (any file)
 * @param {object} glossary  compiled by loadGlossary
 * @param {object} ctx     the run context: { meta, cfg } (lib/config.mjs)
 * @returns {Array} findings, sorted by file, line, column and rule id
 */
export function runGlossaryRules(units, glossary, ctx) {
  const state = { findings: [], meta: ctx.meta, cfg: ctx.cfg };
  const where = `Glossary ${glossary.file}`;
  const notUN = 'this is the reader\'s house terminology, not a United Nations rule';

  // One place where a finding is created, so the audit-lane name and the
  // structured provenance beside the message can never drift from the text.
  // `emit` honours `ue:ignore` suppression and may therefore decline to push,
  // which is why the term travels in as an argument rather than being read
  // back off the finding afterwards.
  const fire = ({ unit, ruleId, matched, index, message, suggestion, term, use }) => {
    const before = state.findings.length;
    // `config.rules` may switch a glossary rule off, exactly as it switches
    // any other rule off. The switch is honoured here, outside emit(), so no
    // glossary code path can bypass it.
    if (enabled(state, ruleId)) {
      emit(state, unit, ruleId, matched, index, message, suggestion, { confidence: 'deterministic' });
    }
    if (state.findings.length === before) return;
    const finding = state.findings[state.findings.length - 1];
    finding.audit = GLOSSARY_LANE_NAME;
    finding.glossary = {
      file: glossary.file,
      name: glossary.name,
      kind: ruleId === 'UE-GL001' ? 'forbidden' : 'required',
      term,
      replacement: use ?? null,
    };
  };

  // UE-GL001 — a forbidden term appears in user-visible copy. Reported at
  // every occurrence, and never with a replacement: terminology is never
  // auto-rewritten, so --fix has nothing to apply even when the reader has
  // declared the preferred wording.
  for (const unit of units) {
    for (const entry of glossary.forbidden) {
      for (const m of unit.text.matchAll(entry.re)) {
        const preferred = entry.use
          ? `The glossary\'s preferred wording is "${entry.use}"`
          : 'The glossary names no replacement for it';
        fire({
          unit,
          ruleId: 'UE-GL001',
          matched: m[0],
          index: m.index,
          message: `${where} ${glossary.label} forbids the term "${m[0]}"; ${notUN}.`,
          suggestion: `${preferred}; write the house wording into the source by hand.`,
          term: entry.term,
          use: entry.use,
        });
      }
    }
  }

  // UE-GL002 — a required term never appears in a file. The unit of judgement
  // is the file, because the promise is "this document must call it X": a file
  // whose extracted copy never contains the term does not keep the promise.
  // A file that produced no copy spans at all is not judged, because nothing
  // was extracted to read.
  const byFile = new Map();
  for (const unit of units) {
    if (!byFile.has(unit.file)) byFile.set(unit.file, []);
    byFile.get(unit.file).push(unit);
  }
  for (const [file, fileUnits] of byFile) {
    // A `ue:ignore` comment is a per-unit suppression, and this finding is
    // about the whole file, so it is honoured only where the reader asked for
    // it file-wide: `ue:ignore all` (or `ue:ignore *`) on any unit of the
    // file. `suppress` is the comment text the extractor attached, kept
    // separate from `raw`; the anchor unit handed to emit() carries no copy, so
    // emit() cannot see the comment and the check is made here.
    const silenced = fileUnits.some(unit => {
      const spec = unit.suppress;
      if (typeof spec !== 'string') return false;
      const match = spec.match(/ue:ignore\s+([A-Za-z0-9*,\s-]+)/);
      if (!match) return true; // a bare `ue:ignore` suppresses everything
      return match[1].trim().split(/[,\s]+/).some(token => token === 'all' || token === '*');
    });
    if (silenced) continue;
    for (const entry of glossary.required) {
      if (fileUnits.some(unit => entry.present.test(unit.text))) continue;
      fire({
        unit: fileAnchor(file),
        ruleId: 'UE-GL002',
        matched: '',
        index: 0,
        message: `${where} ${glossary.label} requires the term "${entry.term}"; it does not appear in the extracted copy of this file; ${notUN}.`,
        suggestion: 'Write the required wording into the passage the concept belongs to; the checker does not decide which passage that is.',
        term: entry.term,
      });
    }
  }

  state.findings.sort((a, b) =>
    a.file.localeCompare(b.file) || a.line - b.line || a.column - b.column ||
    a.ruleId.localeCompare(b.ruleId));
  return state.findings;
}
