// Conservative --fix.
//
// Rules for auto-correction, all enforced here:
//   * prose files only (.md/.markdown/.txt) — HTML, JS and JSON are refused
//     with exit code 2, never rewritten;
//   * only findings for rules on the FIXABLE_RULE_IDS allow-list are applied
//     (British spelling, hyphen → en dash ranges, and the three clean-grammar
//     fixes); terminology, dates, claims, political wording, quotations,
//     harmful content and sourcing findings are reported and never rewritten
//     (remediation brief §8), and any rule not on the list is excluded
//     fail-closed until it is deliberately added;
//   * a finding that carries a replacement is not enough — both the rule id
//     and the deterministic, meaning-preserving replacement must be present,
//     and judgement calls such as register, sourcing and rhetorical questions
//     carry no replacement at all;
//   * edits are computed from extracted copy spans, so code, comments, URLs,
//     quoted titles and fenced blocks are structurally out of reach;
//   * the same span must appear literally in the source, otherwise the fix is
//     skipped rather than guessed;
//   * a lower-case replacement that lands at a sentence start (start of copy,
//     start of line, or after ". " "! " "? ") is capitalised — a sentence must
//     never start in lower case after a fix, and the re-scan has no rule that
//     could catch it later; mid-sentence replacements keep their case.
//   * writes refuse symlinks, non-regular files and hard-linked files, and
//     verify the file descriptor identity before truncating.

import fs from 'node:fs';
import path from 'node:path';
import { escapeControl } from './output.mjs';

export class FixError extends Error {}

const PROSE_EXTENSIONS = new Set(['.md', '.markdown', '.txt']);

/**
 * The fail-closed allow-list of rules `--fix` may rewrite (brief §8).
 *
 * Exactly the deterministic, meaning-preserving families: British spelling
 * (UE-SP001), hyphen → en dash numeric ranges (UE-NU002), the clean-grammar
 * corrections (UE-GR001..3) and the configuration-gated doubled-space
 * collapse (UE-GR004). Terminology, dates, claims, political wording,
 * quotations, harmful content and sourcing findings are reported, never
 * auto-changed — and any future rule is excluded by default: to become
 * fixable, a rule must be added here on purpose, with a test.
 */
export const FIXABLE_RULE_IDS = new Set([
  'UE-SP001',
  'UE-NU002',
  'UE-GR001',
  'UE-GR002',
  'UE-GR003',
  'UE-GR004',
]);

export function assertProseOnly(paths) {
  for (const file of paths) {
    const ext = path.extname(file).toLowerCase();
    if (!PROSE_EXTENSIONS.has(ext)) {
      throw new FixError(
        `refusing --fix on HTML, JavaScript, JSON or other non-prose file: ${file}`);
    }
  }
}

/**
 * Link and type guards for every file that is about to be rewritten: the file
 * must be the regular, unlinkable-looking object we think it is, with no hard
 * links, so a write here cannot reach another path through a second name.
 */
export function assertSafeToFix(paths) {
  for (const file of paths) {
    const stat = fs.lstatSync(file);
    if (stat.isSymbolicLink()) throw new FixError(`refusing symbolic link: ${file}`);
    if (!stat.isFile()) throw new FixError(`refusing non-regular file: ${file}`);
    if (stat.nlink > 1) throw new FixError(`refusing hard-linked file (${stat.nlink} links): ${file}`);
  }
}

function resolveSpan(source, finding) {
  // A finding whose match collapsed interior whitespace carries the exact
  // source substring the fix must cover (the padded doubled word, the space
  // run); every other finding is replaced over its matched text as before.
  const needle = finding._rawMatched || finding._matched;
  const replacement = finding._replacement;
  if (!needle || !replacement) return null;

  const offset = finding._offset;
  const unit = finding._unit;
  const anchored = Number.isInteger(offset) && source.startsWith(needle, offset);

  // A unit built from an offset map is exact: either the mapped position holds
  // the matched copy verbatim, or the match crossed masked whitespace / a
  // decoded entity. In the latter case the fix is skipped rather than guessed,
  // because guessing is how a fixer rewrites a URL, a quotation or a comment.
  if (unit && unit.map) return anchored ? { start: offset, end: offset + needle.length } : null;

  if (anchored) return { start: offset, end: offset + needle.length };

  const from = Number.isInteger(offset) ? Math.max(0, offset - 64) : 0;
  const at = source.indexOf(needle, from);
  if (at < 0) return null;
  if (unit && Number.isInteger(unit.offset)) {
    const limit = unit.offset + (unit.raw ? unit.raw.length : 0) + 64;
    if (at > limit) return null;
  }
  return { start: at, end: at + needle.length };
}

/**
 * True when an edit at `offset` starts a sentence: the start of the copy, the
 * start of a line, or a position right after `.` `!` `?` plus whitespace.
 * This is the one context where a lower-case replacement would corrupt the
 * sentence — and the re-scan has no "lower case after a full stop" rule, so
 * the corruption could never be caught again.
 */
function startsSentence(source, offset) {
  if (offset <= 0) return true;
  const before = source.slice(0, offset);
  if (before.endsWith('\n')) return true;
  return /[.!?]\s+$/.test(before);
}

/**
 * Capitalise a replacement that lands at a sentence start, and only then:
 * mid-sentence edits keep their lower case ("from the United States"), and a
 * replacement that does not open with a lower-case letter — digits, marks, or
 * a word case-preservation already capitalised (`ORGANISATION`, `Organisation`)
 * — passes through untouched.
 */
function capitaliseForSentence(source, offset, replacement) {
  if (typeof replacement !== 'string' || replacement.length === 0) return replacement;
  const first = replacement[0];
  const lowerCaseLetter = first === first.toLowerCase() && first !== first.toUpperCase();
  if (!lowerCaseLetter) return replacement;
  if (!startsSentence(source, offset)) return replacement;
  return first.toUpperCase() + replacement.slice(1);
}

/**
 * @param {Array} findings   editorial findings (with _unit/_matched/_replacement)
 * @param {Map<string,string>} sources  file path -> current contents
 * @returns {Array<{file, before, after, edits: Array}>} one entry per changed file
 */
export function planFixes(findings, sources) {
  const perFile = new Map();

  for (const finding of findings) {
    if (!finding._replacement || !finding._unit) continue;
    // Brief §8: the rule id itself is part of the contract. A deterministic
    // replacement on a rule that is not allow-listed (terminology, dates,
    // claims, political wording, quotations, harmful content, sourcing — or
    // any rule added later) never becomes an edit.
    if (!FIXABLE_RULE_IDS.has(finding.ruleId)) continue;
    const ext = path.extname(finding.file).toLowerCase();
    if (!PROSE_EXTENSIONS.has(ext)) continue;
    const source = sources.get(finding.file);
    if (source === undefined) continue;
    const span = resolveSpan(source, finding);
    if (!span) continue;
    if (!perFile.has(finding.file)) {
      perFile.set(finding.file, { file: finding.file, before: source, edits: [] });
    }
    perFile.get(finding.file).edits.push({
      ...span,
      ruleId: finding.ruleId,
      line: finding.line,
      column: finding.column,
      from: source.slice(span.start, span.end),
      to: capitaliseForSentence(source, span.start, finding._replacement),
      message: finding.message,
    });
  }

  const plans = [];
  for (const plan of perFile.values()) {
    plan.edits.sort((a, b) => a.start - b.start || a.end - b.end);
    const applied = [];
    let after = plan.before;
    // Apply from the end of the file backwards so earlier offsets stay valid.
    const ordered = [...plan.edits].sort((a, b) => b.start - a.start);
    let cursor = Infinity;
    for (const edit of ordered) {
      if (edit.end > cursor) continue; // overlaps an edit already applied
      after = after.slice(0, edit.start) + edit.to + after.slice(edit.end);
      cursor = edit.start;
      applied.push(edit);
    }
    if (after === plan.before) continue;
    plan.edits = applied.sort((a, b) => a.line - b.line || a.column - b.column);
    plan.after = after;
    plans.push(plan);
  }
  plans.sort((a, b) => a.file.localeCompare(b.file));
  return plans;
}

/** Line-accurate preview: replacements never introduce or remove newlines. */
export function renderPlan(plan, { applied = false } = {}) {
  const beforeLines = plan.before.split('\n');
  const afterLines = plan.after.split('\n');
  const out = [`--- ${escapeControl(plan.file)}`, `+++ ${escapeControl(plan.file)} (${applied ? 'applied' : 'proposed'})`];
  const count = Math.min(beforeLines.length, afterLines.length);
  for (let i = 0; i < count; i++) {
    if (beforeLines[i] === afterLines[i]) continue;
    out.push(`@@ ${i + 1} @@`);
    out.push(`-${escapeControl(beforeLines[i])}`);
    out.push(`+${escapeControl(afterLines[i])}`);
  }
  return out.join('\n');
}

/**
 * Write through a verified descriptor: refuse symlinks and hard links, confirm
 * the descriptor still points at the file we read, then truncate and write.
 */
export function writeSafely(file, expected, next) {
  const link = fs.lstatSync(file);
  if (link.isSymbolicLink()) throw new FixError(`${file} is a symbolic link; refusing to write`);
  if (!link.isFile()) throw new FixError(`${file} is not a regular file; refusing to write`);

  const fd = fs.openSync(file, 'r+');
  try {
    const stat = fs.fstatSync(fd);
    const regular = (stat.mode & 0o170000) === 0o100000;
    if (!regular) throw new FixError(`${file} is not a regular file; refusing to write`);
    if (stat.nlink > 1) throw new FixError(`${file} has hard links; refusing to write`);
    if (stat.dev !== link.dev || stat.ino !== link.ino) {
      throw new FixError(`${file} changed while it was being checked; refusing to write`);
    }
    const buffer = Buffer.alloc(stat.size);
    fs.readSync(fd, buffer, 0, stat.size, 0);
    const current = buffer.toString('utf8');
    if (current !== expected) {
      throw new FixError(`${file} was modified since it was read; refusing to overwrite`);
    }
    fs.ftruncateSync(fd, 0);
    fs.writeSync(fd, next, null, 'utf8');
    fs.fsyncSync(fd);
  } finally {
    fs.closeSync(fd);
  }
}
