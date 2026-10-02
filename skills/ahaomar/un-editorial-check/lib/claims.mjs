// The claim-evidence register: a fill-in ledger of the figures, counts and
// comparisons the scan detects, which a later run verifies for completeness.
//
// The tool never judges whether a claim is true. What it can do is turn
// "review this figure" from a one-off prompt into a tracked checklist:
//
//   * `--claims-out <file>` writes every claim-shaped finding (UE-RE002,
//     UE-RE003, UE-DI001, UE-CL001) to a JSON register the author fills in —
//     each entry carrying its source and reference date fields, empty until
//     a human completes them. Writing the register is an extraction aid, not
//     a scan verdict: the run exits 0 whatever the copy looks like.
//   * `--claims <file>` verifies the committed register against a fresh scan:
//     an entry whose source or reference date is still empty is a finding
//     (UE-CL002), a detected claim that is not in the register is a finding
//     (UE-CL003), and an entry whose claim text no longer appears in the copy
//     is reported as stale without failing anything.
//
// The register is data, validated fail-closed like the glossary: a wrong
// version, an unknown field, a missing claim text or a bad shape refuses the
// run (exit 2) rather than half-checking.

import fs from 'node:fs';
import { parseJsonStrict } from './config.mjs';

export class ClaimsError extends Error {}

export const REGISTER_VERSION = 1;

// The rule ids whose findings are claim-shaped and therefore registerable.
export const CLAIM_RULE_IDS = ['UE-RE002', 'UE-RE003', 'UE-DI001', 'UE-CL001'];

export class RegisterRefusal extends ClaimsError {
  constructor(message) {
    super(message);
    this.name = 'RegisterRefusal';
  }
}

const isPlainObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);
const nonEmpty = (value) => typeof value === 'string' && value.trim().length > 0;

const ENTRY_FIELDS = new Set([
  'id', 'file', 'line', 'column', 'ruleId', 'claim', 'source', 'asOf', 'verified',
]);

/**
 * Validate a loaded register object. Returns it unchanged when valid.
 */
export function validateRegister(raw, label = 'claim register') {
  if (!isPlainObject(raw)) throw new RegisterRefusal(`${label} must be a JSON object`);
  if (raw.registerVersion !== REGISTER_VERSION) {
    throw new RegisterRefusal(`${label} registerVersion must be ${REGISTER_VERSION}`);
  }
  const unknown = Object.keys(raw).filter(key => key !== 'registerVersion' && key !== 'entries');
  if (unknown.length) {
    throw new RegisterRefusal(`${label} contains unknown fields: ${unknown.join(', ')}`);
  }
  if (!Array.isArray(raw.entries)) throw new RegisterRefusal(`${label} entries must be an array`);
  const seen = new Set();
  for (const [index, entry] of raw.entries.entries()) {
    const at = `${label} entries[${index}]`;
    if (!isPlainObject(entry)) throw new RegisterRefusal(`${at} must be an object`);
    const missing = ['id', 'file', 'line', 'column', 'ruleId', 'claim']
      .filter(field => entry[field] === undefined);
    if (missing.length) throw new RegisterRefusal(`${at} is missing: ${missing.join(', ')}`);
    const badField = Object.keys(entry).filter(key => !ENTRY_FIELDS.has(key));
    if (badField.length) {
      throw new RegisterRefusal(`${at} contains unknown fields: ${badField.join(', ')}`);
    }
    for (const field of ['id', 'file', 'ruleId', 'claim']) {
      if (!nonEmpty(String(entry[field]))) throw new RegisterRefusal(`${at} ${field} must be a non-empty string`);
    }
    if (!Number.isInteger(entry.line) || !Number.isInteger(entry.column)) {
      throw new RegisterRefusal(`${at} line and column must be integers`);
    }
    if ('source' in entry && entry.source !== null && typeof entry.source !== 'string') {
      throw new RegisterRefusal(`${at} source must be a string or null`);
    }
    if ('asOf' in entry && entry.asOf !== null && typeof entry.asOf !== 'string') {
      throw new RegisterRefusal(`${at} asOf must be a string or null`);
    }
    if ('verified' in entry && typeof entry.verified !== 'boolean') {
      throw new RegisterRefusal(`${at} verified must be a boolean`);
    }
    if (seen.has(entry.id)) throw new RegisterRefusal(`${label} contains duplicate id "${entry.id}"`);
    seen.add(entry.id);
  }
  return raw;
}

/** Load and validate a register from disk. */
export function loadRegister(file) {
  let raw;
  try {
    raw = parseJsonStrict(fs.readFileSync(file, 'utf8'), file);
  } catch (err) {
    if (err instanceof ClaimsError) throw err;
    if (err.code === 'ENOENT') throw new RegisterRefusal(`claim register not found: ${file}`);
    if (err instanceof Error && /JSON/.test(err.message)) {
      throw new RegisterRefusal(`${file} is not valid JSON: ${err.message}`);
    }
    throw err;
  }
  return validateRegister(raw, file);
}

/**
 * Build register entries from the scan's claim-shaped findings. The `claim`
 * text is what the finding matched (the figure, the comparison phrase, the
 * superlative) — the same text a later verify pass searches for, so an entry
 * whose claim no longer appears is recognisably stale.
 */
export function extractRegisterEntries(findings) {
  return findings
    .filter(finding => CLAIM_RULE_IDS.includes(finding.ruleId))
    .map((finding, index) => ({
      id: `C-${String(index + 1).padStart(3, '0')}`,
      file: finding.file,
      line: finding.line,
      column: finding.column,
      ruleId: finding.ruleId,
      claim: finding.current || '',
      source: null,
      asOf: null,
      verified: false,
    }));
}

/**
 * The text of one file's copy, assembled from its units, for claim lookup.
 * Units are joined with a single space — matching operates on normalised
 * runs of whitespace, so a claim split across inline elements is still found.
 */
function fileCopyText(units, file) {
  return (units || [])
    .filter(unit => unit.file === file)
    .map(unit => unit.text)
    .join(' ')
    .replace(/\s+/g, ' ');
}

function claimAppears(copyText, claim) {
  if (!claim) return false;
  const needle = claim.replace(/\s+/g, ' ').trim();
  if (!needle) return false;
  // Copy spans are joined with spaces, so the claim's own interior whitespace
  // is normalised the same way before the search.
  return copyText.includes(needle);
}

/**
 * Verify a register against a fresh scan.
 *
 * @param {Array} findings       the scan's annotated findings (annotated so
 *                               ruleId and position match the register's shape)
 * @param {object} register      a validated register
 * @param {Array} units          the scan's extracted copy units
 * @param {object} meta          catalogue metadata for the register rules
 * @returns {{findings: Array, stale: Array, status: string}}
 */
export function verifyRegister(findings, register, units, ctx) {
  const entries = register.entries || [];
  const byFile = new Map(entries.map(entry => [entry.file, entry]));
  const out = [];
  const stale = [];

  // 1. entries whose source or reference date is still empty.
  for (const entry of entries) {
    if (!entry.source) {
      out.push(makeFinding(ctx, 'UE-CL002', entry,
        `Claim register entry ${entry.id} has no source recorded for "${trimClaim(entry.claim)}".`,
        'Record the source the figure or ranking comes from, then mark the entry verified.'));
    } else if (!entry.asOf) {
      out.push(makeFinding(ctx, 'UE-CL002', entry,
        `Claim register entry ${entry.id} records a source but no reference date for "${trimClaim(entry.claim)}".`,
        'State the reference date the data was current at, then mark the entry verified.'));
    }
    // 2. entries whose claim no longer appears in the copy are stale.
    const copy = fileCopyText(units, entry.file);
    if (!copy || !claimAppears(copy, entry.claim)) {
      stale.push(entry.id);
    }
  }

  // 3. detected claims that are not in the register.
  const registered = new Set(entries.map(entry => `${entry.file}::${normaliseClaimKey(entry.claim)}`));
  for (const finding of findings) {
    if (!CLAIM_RULE_IDS.includes(finding.ruleId)) continue;
    const key = `${finding.file}::${normaliseClaimKey(finding.current || '')}`;
    if (registered.has(key)) continue;
    out.push(makeFinding(ctx, 'UE-CL003', {
      file: finding.file, line: finding.line, column: finding.column, id: null,
    },
    `A claim detected in the copy is not recorded in the claim register: "${trimClaim(finding.current)}".`,
    'Add the claim to the register with its source and reference date, or resolve the finding.'));
  }

  const incomplete = out.length;
  const status = `claim register: ${entries.length} entr${entries.length === 1 ? 'y' : 'ies'} checked, `
    + `${incomplete} incomplete or unregistered, ${stale.length} stale`;
  return { findings: out, stale, status };
}

const trimClaim = (claim) => {
  const text = String(claim || '');
  return text.length > 60 ? `${text.slice(0, 57)}...` : text;
};

function normaliseClaimKey(claim) {
  return String(claim || '').replace(/\s+/g, ' ').trim().toLowerCase();
}

/**
 * A register finding (UE-CL002, UE-CL003): agent-review lane, warning
 * severity, never fixable — the register is bookkeeping, and the check
 * verifies that bookkeeping happened, never that the claim is true.
 */
function makeFinding(ctx, ruleId, entry, message, suggestion) {
  return {
    file: entry.file,
    line: entry.line,
    column: entry.column,
    ruleId,
    category: (ctx.meta[ruleId] || {}).category || 'agent-review',
    severity: ctx.cfg.severities[ruleId] || (ctx.meta[ruleId] || {}).severity || 'warning',
    confidence: 'deterministic',
    scope: 'user-visible-copy',
    context: 'authored',
    message,
    suggestion: suggestion || null,
    current: null,
    proposed: null,
  };
}
