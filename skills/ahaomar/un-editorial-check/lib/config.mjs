// Config loading, catalogue loading and rule-context assembly.
//
// Everything is validated before use and the module keeps no mutable global
// state: two runs in the same process cannot contaminate each other, and a
// bad file always aborts (exit code 2) instead of silently checking with a
// reduced rule set.

import fs from 'node:fs';
import path from 'node:path';
import {
  ProfileError, parseJsonStrict, validateProfile, validateAuditProfile,
  applyProfile, buildVocabulary,
} from './profile.mjs';

export { ProfileError };

const SEVERITIES = new Set(['error', 'warning', 'info']);
const CONFIG_FIELDS = new Set([
  'ignoredPaths', 'allowlist', 'severities', 'rules', 'spellingReview',
  'spacingReview', 'consistencyReview', 'baseOrigin', 'renderTargets', 'glossary', 'extraExtensions',
]);
// Kinds a configured extra extension may be read as. JavaScript is
// deliberately absent: the render-evidence heuristic is tuned to JS/TS syntax,
// and a template language read as script would claim evidence it does not have.
const EXTRA_KINDS = new Set(['markdown', 'html', 'text']);
const ALLOWLIST_FIELDS = new Set(['spellings', 'terminology', 'register', 'claims', 'acronyms']);
const RULE_FIELDS = new Set(['enabled', 'severity']);

const isPlainObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);
const nonEmpty = (value) => typeof value === 'string' && value.trim().length > 0;

function validateStringList(list, label) {
  if (!Array.isArray(list)) throw new ProfileError(`${label} must be an array`);
  for (const item of list) {
    if (!nonEmpty(item)) throw new ProfileError(`${label} must contain only non-empty strings`);
  }
}

/**
 * Config `severities` is the flat `{ "UE-SP001": "warning" }` map documented
 * in the README and consumed as a plain value by the engine — the same shape
 * a profile uses. It shares no validator with `rules`, whose values are
 * `{ enabled, severity }` objects.
 */
function validateSeverities(severities, knownIds, label) {
  if (!isPlainObject(severities)) throw new ProfileError(`${label} must be an object`);
  for (const [id, severity] of Object.entries(severities)) {
    if (!knownIds.includes(id)) throw new ProfileError(`${label} contains unknown rule "${id}"`);
    if (!SEVERITIES.has(severity)) throw new ProfileError(`${label}.${id} must be error, warning or info`);
  }
}

function validateRuleSettings(rules, knownIds, label) {
  if (!isPlainObject(rules)) throw new ProfileError(`${label} must be an object`);
  for (const [id, setting] of Object.entries(rules)) {
    if (!knownIds.includes(id)) throw new ProfileError(`${label} contains unknown rule "${id}"`);
    if (!isPlainObject(setting)) throw new ProfileError(`${label}.${id} must be an object`);
    if (!Object.keys(setting).length) throw new ProfileError(`${label}.${id} must set enabled or severity`);
    for (const key of Object.keys(setting)) {
      if (!RULE_FIELDS.has(key)) throw new ProfileError(`${label}.${id} contains unknown field "${key}"`);
    }
    if ('enabled' in setting && typeof setting.enabled !== 'boolean') {
      throw new ProfileError(`${label}.${id}.enabled must be a boolean`);
    }
    if ('severity' in setting && !SEVERITIES.has(setting.severity)) {
      throw new ProfileError(`${label}.${id}.severity must be error, warning or info`);
    }
  }
}

/** Validate a raw config object. Returns a normalised, frozen config. */
export function validateConfig(raw, { knownIds = [] } = {}) {
  if (!isPlainObject(raw)) throw new ProfileError('config must be a JSON object');
  const unknown = Object.keys(raw).filter(key => !CONFIG_FIELDS.has(key));
  if (unknown.length) throw new ProfileError(`config contains unknown fields: ${unknown.join(', ')}`);

  const cfg = {
    ignoredPaths: raw.ignoredPaths ?? [],
    allowlist: raw.allowlist ?? {},
    severities: raw.severities ?? {},
    rules: raw.rules ?? {},
    spellingReview: raw.spellingReview ?? false,
    // Doubled-space review (UE-GR004): off by default, because deliberately
    // aligned plain-text columns are a formatting choice, not a defect.
    spacingReview: raw.spacingReview ?? false,
    // Mixed-quote and mixed-number-grouping review (UE-HR008, UE-HR009):
    // off by default, because a house style may deliberately mix conventions
    // across files and the review polices one document's internal consistency.
    consistencyReview: raw.consistencyReview ?? false,
    // Extensions this project wants scanned under an existing extractor
    // ({"\.mdx": "markdown"}): data-only, fail-closed on a bad key or kind.
    extraExtensions: raw.extraExtensions ?? {},
    baseOrigin: raw.baseOrigin ?? null,
    renderTargets: raw.renderTargets ?? [],
    // The reader's own glossary: a path, never the glossary itself. The file
    // is loaded and validated by lib/glossary.mjs after the config is read, so
    // a bad path refuses the run (exit 2) rather than scanning without it.
    glossary: raw.glossary ?? null,
  };

  validateStringList(cfg.ignoredPaths, 'config ignoredPaths');
  if (!isPlainObject(cfg.allowlist)) throw new ProfileError('config allowlist must be an object');
  const badAllow = Object.keys(cfg.allowlist).filter(key => !ALLOWLIST_FIELDS.has(key));
  if (badAllow.length) throw new ProfileError(`config allowlist contains unknown fields: ${badAllow.join(', ')}`);
  for (const key of ALLOWLIST_FIELDS) {
    if (key in cfg.allowlist) validateStringList(cfg.allowlist[key], `config allowlist.${key}`);
  }
  validateSeverities(cfg.severities, knownIds, 'config severities');
  validateRuleSettings(cfg.rules, knownIds, 'config rules');
  if (typeof cfg.spellingReview !== 'boolean') throw new ProfileError('config spellingReview must be a boolean');
  if (typeof cfg.spacingReview !== 'boolean') throw new ProfileError('config spacingReview must be a boolean');
  if (typeof cfg.consistencyReview !== 'boolean') throw new ProfileError('config consistencyReview must be a boolean');
  if (!isPlainObject(cfg.extraExtensions)) throw new ProfileError('config extraExtensions must be an object');
  for (const [ext, kind] of Object.entries(cfg.extraExtensions)) {
    if (!/^\.[a-z0-9]+(\.[a-z0-9]+)*$/i.test(ext)) {
      throw new ProfileError(`config extraExtensions key "${ext}" must be a dot-prefixed file extension`);
    }
    if (!EXTRA_KINDS.has(kind)) {
      throw new ProfileError(`config extraExtensions.${ext} must be markdown, html or text`);
    }
  }

  if (cfg.baseOrigin !== null) {
    if (!nonEmpty(cfg.baseOrigin)) throw new ProfileError('config baseOrigin must be a non-empty absolute URL');
    let url;
    try { url = new URL(cfg.baseOrigin); } catch { throw new ProfileError('config baseOrigin must be an absolute URL'); }
    if (url.protocol !== 'https:' && url.protocol !== 'http:') throw new ProfileError('config baseOrigin must be an absolute http(s) URL');
    cfg.baseOrigin = url.href;
  }

  validateStringList(cfg.renderTargets, 'config renderTargets');
  for (const target of cfg.renderTargets) {
    if (!/^[\w$-]+$/.test(target)) throw new ProfileError(`config renderTargets entry "${target}" must be an identifier`);
  }

  if (cfg.glossary !== null && !nonEmpty(cfg.glossary)) {
    throw new ProfileError('config glossary must be a non-empty path to a glossary file');
  }

  cfg.allowlist = {
    spellings: cfg.allowlist.spellings ?? [],
    terminology: cfg.allowlist.terminology ?? [],
    register: cfg.allowlist.register ?? [],
    claims: cfg.allowlist.claims ?? [],
    acronyms: cfg.allowlist.acronyms ?? [],
  };
  return Object.freeze(cfg);
}

/**
 * Load rules/sources.json and return the set of recorded source ids. Missing
 * or unparseable behind a cited id is a refusal, never a silent pass: a
 * citation nobody can resolve is worse than no citation at all.
 */
function loadSourceRegistryIds(root) {
  const file = path.join(root, 'rules', 'sources.json');
  let raw;
  try {
    raw = parseJsonStrict(fs.readFileSync(file, 'utf8'), 'rules/sources.json');
  } catch (err) {
    if (err instanceof ProfileError) throw err;
    throw new ProfileError(`rules/sources.json cannot be read behind a cited source id: ${err.message}`);
  }
  if (!isPlainObject(raw) || !Array.isArray(raw.sources)) {
    throw new ProfileError('rules/sources.json must declare a sources array');
  }
  const ids = new Set();
  for (const entry of raw.sources) {
    if (!isPlainObject(entry) || !nonEmpty(entry.id)) throw new ProfileError('rules/sources.json entries must be objects with an id');
    if (ids.has(entry.id)) throw new ProfileError(`rules/sources.json contains duplicate id "${entry.id}"`);
    ids.add(entry.id);
  }
  return ids;
}

/** Load and validate rules/catalogue.json — the single source of rule metadata. */
export function loadCatalogue(root) {
  const file = path.join(root, 'rules', 'catalogue.json');
  const raw = parseJsonStrict(fs.readFileSync(file, 'utf8'), 'rules/catalogue.json');
  if (!isPlainObject(raw) || raw.catalogueVersion !== 1 || !Array.isArray(raw.rules) || !raw.rules.length) {
    throw new ProfileError('rules/catalogue.json must declare catalogueVersion 1 and a non-empty rules array');
  }
  const meta = {};
  const ids = [];
  const citedSources = new Set();
  for (const entry of raw.rules) {
    if (!isPlainObject(entry) || !nonEmpty(entry.id)) throw new ProfileError('catalogue entries must be objects with an id');
    if (meta[entry.id]) throw new ProfileError(`catalogue contains duplicate rule "${entry.id}"`);
    if (!SEVERITIES.has(entry.severity)) throw new ProfileError(`catalogue ${entry.id} severity must be error, warning or info`);
    if (!nonEmpty(entry.category) || !nonEmpty(entry.confidence) || !nonEmpty(entry.scope) || !nonEmpty(entry.status)) {
      throw new ProfileError(`catalogue ${entry.id} must declare category, confidence, scope and status`);
    }
    if (entry.confidence !== 'deterministic' && entry.confidence !== 'heuristic') {
      throw new ProfileError(`catalogue ${entry.id} confidence must be deterministic or heuristic`);
    }
    if ('profile' in entry && entry.profile !== null
      && entry.profile !== 'publishing' && entry.profile !== 'accessibility' && entry.profile !== 'security') {
      throw new ProfileError(`catalogue ${entry.id} profile must be null, publishing, accessibility or security`);
    }
    // `sources` is optional but fail-closed when present: an array of
    // non-empty, duplicate-free ids, each cross-checked against the recorded
    // registry below so a typo can never cite a source that does not exist.
    if ('sources' in entry) {
      if (!Array.isArray(entry.sources)) throw new ProfileError(`catalogue ${entry.id} sources must be an array`);
      const seenSources = new Set();
      for (const source of entry.sources) {
        if (!nonEmpty(source)) throw new ProfileError(`catalogue ${entry.id} sources must contain only non-empty strings`);
        if (seenSources.has(source)) throw new ProfileError(`catalogue ${entry.id} sources contains duplicate id "${source}"`);
        seenSources.add(source);
        citedSources.add(source);
      }
    }
    meta[entry.id] = entry;
    ids.push(entry.id);
  }
  if (citedSources.size) {
    const registry = loadSourceRegistryIds(root);
    for (const source of citedSources) {
      if (!registry.has(source)) {
        throw new ProfileError(`rules/catalogue.json cites unknown source id "${source}" (not recorded in rules/sources.json)`);
      }
    }
  }
  return { meta, ids, catalogue: raw };
}

/** The bundled United Nations baseline organisation profile. */
export function loadBaselineProfile(root, knownIds) {
  const file = path.join(root, 'config', 'profiles', 'un-v1.json');
  const raw = parseJsonStrict(fs.readFileSync(file, 'utf8'), 'config/profiles/un-v1.json');
  return validateProfile(raw, { baseline: null, knownIds, label: 'config/profiles/un-v1.json' });
}

/** A bundled audit profile (publishing | accessibility | security). */
export function loadAuditProfile(root, name, meta) {
  const file = path.join(root, 'config', 'profiles', `${name}.json`);
  const raw = parseJsonStrict(fs.readFileSync(file, 'utf8'), `config/profiles/${name}.json`);
  return validateAuditProfile(raw, { expectedName: name, meta, label: `config/profiles/${name}.json` });
}

/**
 * Load an organisation profile from disk and merge it over the baseline.
 * Kept separate from audit loading so `--profile <file>` and
 * `--profile security` can never be confused: an existing path always wins.
 */
export function loadOrganisationProfile(root, file, baseline, knownIds, meta) {
  const resolved = path.resolve(file);
  if (!fs.existsSync(resolved)) throw new ProfileError(`profile not found: ${file}`);
  const stat = fs.statSync(resolved);
  if (!stat.isFile()) throw new ProfileError(`profile path is not a regular file: ${file}`);
  const raw = parseJsonStrict(fs.readFileSync(resolved, 'utf8'), file);
  if (isPlainObject(raw) && 'auditVersion' in raw) {
    return { kind: 'audit', value: validateAuditProfile(raw, { meta, label: file }) };
  }
  const profile = validateProfile(raw, { baseline, knownIds, label: file });
  return { kind: 'organisation', value: applyProfile(baseline, profile) };
}

/**
 * Assemble the rule context consumed by the editorial engine.
 *
 * `profileSelected` records whether an organisation profile was chosen: the
 * default (audit-only) stance reports the -ize/-ise conflict family as a
 * warning that names the choice, while a selected profile applies its own
 * `spellingConflicts` stance instead. `conflictFamily` is the static family
 * derived from the baseline (un-v1.json), passed separately from the merged
 * profile's list so an unselected run still knows which keys are contested.
 */
export function makeContext({ cfg, baseline, meta, profileSelected = false, conflictFamily = null }) {
  const vocab = buildVocabulary(baseline, {
    registerAllow: cfg.allowlist.register,
    claimsAllow: cfg.allowlist.claims,
  });
  vocab.conflictFamily = new Set(conflictFamily ?? vocab.spellingConflicts);
  // A profile may carry severities and rule states, but they were validated
  // and merged without ever reaching the engine — a documented feature that
  // silently did nothing. A configuration file is the more specific source,
  // so it wins on any key both set.
  const severities = { ...(baseline.severities || {}), ...cfg.severities };
  const rules = { ...(baseline.rules || {}), ...cfg.rules };
  return { cfg: Object.freeze({ ...cfg, severities, rules }), meta, vocab, profileSelected, profileName: baseline.name };
}

export { applyProfile, buildVocabulary, validateProfile, validateAuditProfile, parseJsonStrict };
