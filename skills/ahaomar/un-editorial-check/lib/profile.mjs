// Organisation profiles and audit profiles.
//
// Two different file schemas share the --profile flag and are discriminated by
// their version field, never by filename:
//
//   profileVersion: 1  organisation profile — spelling, terminology, register,
//                      severities, rule switches. Merged over the bundled
//                      United Nations baseline (config/profiles/un-v1.json).
//   auditVersion: 1    audit profile — names the non-editorial checks that run
//                      only when explicitly requested (--profile security).
//
// Validation is strict and fail-closed: a malformed file aborts with exit code
// 2 instead of silently checking with a reduced rule set. Nothing here mutates
// module state; every applyProfile call returns a new object.

export class ProfileError extends Error {}

const SEVERITIES = new Set(['error', 'warning', 'info']);
const PROFILE_FIELDS = new Set([
  'profileVersion', 'name', 'source', 'description', 'spelling', 'terminology',
  'register', 'severities', 'rules', 'pageUrl', 'diplomacy', 'spellingConflicts',
  'customRules',
]);
const CUSTOM_RULE_FIELDS = new Set(['id', 'pattern', 'message', 'severity', 'suggestion', 'source']);
const AUDIT_FIELDS = new Set(['auditVersion', 'name', 'category', 'description', 'rules']);
const REGISTER_FIELDS = new Set(['forbidden', 'approved']);
const KNOWN_AUDITS = new Set(['publishing', 'accessibility', 'security']);
const DIPLOMACY_FIELDS = new Set(['claims']);
const CLAIM_FIELDS = new Set([
  'id', 'topic', 'subjects', 'claimants', 'patterns', 'neutral', 'unTerminology', 'source',
]);
const CLAIM_PLACEHOLDERS = new Set(['subject', 'claimant']);
const PLACEHOLDER_RE = /\{([a-zA-Z][a-zA-Z0-9_]*)\}/g;

// Duplicate keys never survive JSON.parse: the parser silently keeps only the
// last value, so a scan of the parsed tree can never see one. The check reads
// the raw text instead — a duplicate key is a classic config bypass (set a
// restriction twice, the reader honours only the second), and it must fail
// closed. The text is walked with a minimal scanner: JSON.parse has already
// proved the structure is valid, so every string followed by ":" is an object
// key and no value string can be mistaken for one.
function findDuplicateKeys(text) {
  const duplicates = new Set();
  const stack = []; // per depth: the keys seen so far, or null inside an array
  let i = 0;
  while (i < text.length) {
    const ch = text[i];
    if (ch === '{') { stack.push(new Set()); i += 1; continue; }
    if (ch === '[') { stack.push(null); i += 1; continue; }
    if (ch === '}' || ch === ']') { stack.pop(); i += 1; continue; }
    if (ch !== '"') { i += 1; continue; }
    const start = i;
    i += 1;
    while (i < text.length && text[i] !== '"') {
      if (text[i] === '\\') i += 1; // skip the escaped character
      i += 1;
    }
    i += 1; // past the closing quote, which JSON.parse has already proved exists
    let colon = i;
    while (colon < text.length && /\s/.test(text[colon])) colon += 1;
    const keys = stack[stack.length - 1];
    if (keys && text[colon] === ':') {
      let key;
      try { key = JSON.parse(text.slice(start, i)); } catch { key = text.slice(start, i); }
      if (keys.has(key)) duplicates.add(key);
      keys.add(key);
    }
  }
  return [...duplicates];
}

/** JSON.parse that rejects duplicate object keys (a classic config bypass). */
export function parseJsonStrict(text, label) {
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (err) {
    throw new ProfileError(`${label} is not valid JSON: ${err.message}`);
  }
  const duplicates = findDuplicateKeys(text);
  if (duplicates.length) {
    throw new ProfileError(`${label} contains duplicate keys: ${duplicates.join(', ')}`);
  }
  return parsed;
}

const isPlainObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);
const nonEmpty = (value) => typeof value === 'string' && value.trim().length > 0;

function checkKnownFields(obj, allowed, label, extras = []) {
  const unknown = Object.keys(obj).filter(key => !allowed.has(key) && !extras.includes(key));
  if (unknown.length) {
    throw new ProfileError(`${label} contains unknown fields: ${unknown.join(', ')}`);
  }
}

function validateSeverities(severities, knownIds, label) {
  if (!isPlainObject(severities)) throw new ProfileError(`${label} severities must be an object`);
  for (const [id, severity] of Object.entries(severities)) {
    if (!knownIds.includes(id)) throw new ProfileError(`${label} severities contains unknown rule "${id}"`);
    if (!SEVERITIES.has(severity)) throw new ProfileError(`${label} severity for ${id} must be error, warning or info`);
  }
}

function validateRuleSettings(rules, knownIds, label) {
  if (!isPlainObject(rules)) throw new ProfileError(`${label} rules must be an object`);
  for (const [id, setting] of Object.entries(rules)) {
    if (!knownIds.includes(id)) throw new ProfileError(`${label} rules contains unknown rule "${id}"`);
    if (!isPlainObject(setting)) throw new ProfileError(`${label} rules.${id} must be an object`);
    const keys = Object.keys(setting);
    if (!keys.length) throw new ProfileError(`${label} rules.${id} must set enabled or severity`);
    for (const key of keys) {
      if (key !== 'enabled' && key !== 'severity') {
        throw new ProfileError(`${label} rules.${id} contains unknown field "${key}"`);
      }
    }
    if ('enabled' in setting && typeof setting.enabled !== 'boolean') {
      throw new ProfileError(`${label} rules.${id}.enabled must be a boolean`);
    }
    if ('severity' in setting && !SEVERITIES.has(setting.severity)) {
      throw new ProfileError(`${label} rules.${id}.severity must be error, warning or info`);
    }
  }
}

export function normaliseTerminologyEntry(entry) {
  if (Array.isArray(entry)) {
    if (entry.length !== 2) throw new ProfileError('a terminology pair must contain exactly [from, to]');
    const [from, to] = entry;
    if (!nonEmpty(from) || !nonEmpty(to)) throw new ProfileError('terminology pairs must be non-empty strings');
    if (from === to) throw new ProfileError(`terminology pair "${from}" cannot map a term to itself`);
    return { rule: 'UE-TE001', from, to };
  }
  if (isPlainObject(entry)) {
    const unknown = Object.keys(entry).filter(key => !['rule', 'from', 'to'].includes(key));
    if (unknown.length) throw new ProfileError(`terminology entry contains unknown fields: ${unknown.join(', ')}`);
    if (entry.rule !== 'UE-TE001' && entry.rule !== 'UE-TE002' && entry.rule !== 'UE-TE005') {
      throw new ProfileError('terminology entry rule must be UE-TE001, UE-TE002 or UE-TE005');
    }
    if (!nonEmpty(entry.from) || !nonEmpty(entry.to)) throw new ProfileError('terminology entries must be non-empty strings');
    if (entry.from === entry.to) throw new ProfileError(`terminology pair "${entry.from}" cannot map a term to itself`);
    return { rule: entry.rule, from: entry.from, to: entry.to };
  }
  throw new ProfileError('terminology entries must be [from, to] arrays or {rule, from, to} objects');
}

function validateStringList(list, label) {
  if (!Array.isArray(list)) throw new ProfileError(`${label} must be an array`);
  const seen = new Set();
  for (const item of list) {
    if (!nonEmpty(item)) throw new ProfileError(`${label} must contain only non-empty strings`);
    if (seen.has(item)) throw new ProfileError(`${label} contains a duplicate entry "${item}"`);
    seen.add(item);
  }
}

/**
 * Validate one contested-claim knowledge-base entry. Every field is required:
 * a citation (`source`) is what makes a claim entry reviewable, and both the
 * neutral phrasing and the UN designation are what the report offers in place
 * of the matched claim. Patterns are literal templates that may only use the
 * {subject} and {claimant} placeholders, must always scope themselves with
 * {subject}, and must carry literal claim wording of their own — a template of
 * placeholders alone would match the bare region name, not a claim.
 */
function validateClaim(claim, label) {
  if (!isPlainObject(claim)) throw new ProfileError(`${label} must be an object`);
  checkKnownFields(claim, CLAIM_FIELDS, label);
  for (const field of ['id', 'topic', 'neutral', 'unTerminology', 'source']) {
    if (!nonEmpty(claim[field])) throw new ProfileError(`${label} ${field} must be a non-empty string`);
  }
  if (!Array.isArray(claim.subjects) || !claim.subjects.length) {
    throw new ProfileError(`${label} subjects must be a non-empty array`);
  }
  validateStringList(claim.subjects, `${label} subjects`);
  if (!Array.isArray(claim.claimants)) throw new ProfileError(`${label} claimants must be an array`);
  validateStringList(claim.claimants, `${label} claimants`);
  if (!Array.isArray(claim.patterns) || !claim.patterns.length) {
    throw new ProfileError(`${label} patterns must be a non-empty array`);
  }
  for (const pattern of claim.patterns) {
    if (!nonEmpty(pattern)) throw new ProfileError(`${label} patterns must contain only non-empty strings`);
    if (pattern !== pattern.trim()) {
      throw new ProfileError(`${label} pattern "${pattern}" must not start or end with whitespace`);
    }
    for (const [, name] of pattern.matchAll(PLACEHOLDER_RE)) {
      if (!CLAIM_PLACEHOLDERS.has(name)) {
        throw new ProfileError(`${label} pattern "${pattern}" contains unknown placeholder {${name}}`);
      }
    }
    const literal = pattern.replace(/\{(?:subject|claimant)\}/g, '');
    if (/[{}]/.test(literal)) {
      throw new ProfileError(`${label} pattern "${pattern}" contains a malformed placeholder`);
    }
    if (!literal.trim()) {
      throw new ProfileError(`${label} pattern "${pattern}" must contain literal claim wording`);
    }
    if (!pattern.includes('{subject}')) {
      throw new ProfileError(`${label} pattern "${pattern}" must include {subject}`);
    }
    if (pattern.includes('{claimant}') && !claim.claimants.length) {
      throw new ProfileError(`${label} pattern "${pattern}" uses {claimant} but claimants is empty`);
    }
  }
}

/**
 * Validate an organisation profile.
 * @param {object} profile   already parsed
 * @param {object} options
 * @param {object|null} options.baseline  baseline profile; when present, spelling
 *   keys must already exist in it so that a typo cannot silently disable a rule
 * @param {string[]} options.knownIds     catalogue rule ids
 */
export function validateProfile(profile, { baseline = null, knownIds = [], label = 'profile' } = {}) {
  if (!isPlainObject(profile)) throw new ProfileError(`${label} must be an object`);
  checkKnownFields(profile, PROFILE_FIELDS, label);

  if (profile.profileVersion !== 1) throw new ProfileError(`${label} profileVersion must be 1`);
  if (!nonEmpty(profile.name)) throw new ProfileError(`${label} name must be a non-empty string`);
  if (!nonEmpty(profile.source)) throw new ProfileError(`${label} source must be a non-empty string`);
  if ('description' in profile && !nonEmpty(profile.description)) throw new ProfileError(`${label} description must be a non-empty string`);

  if ('pageUrl' in profile) {
    let url;
    try { url = new URL(profile.pageUrl); } catch { throw new ProfileError(`${label} pageUrl must be an absolute URL`); }
    if (url.protocol !== 'https:' && url.protocol !== 'http:') throw new ProfileError(`${label} pageUrl must be an absolute http(s) URL`);
  }

  const baselineKeys = baseline && isPlainObject(baseline.spelling) ? new Set(Object.keys(baseline.spelling)) : null;

  if ('spelling' in profile) {
    if (!isPlainObject(profile.spelling)) throw new ProfileError(`${label} spelling must be an object`);
    for (const [from, to] of Object.entries(profile.spelling)) {
      if (!/^[a-z][a-z-]*$/.test(from)) throw new ProfileError(`${label} spelling key "${from}" must be a lowercase word`);
      if (!nonEmpty(to)) throw new ProfileError(`${label} spelling.${from} must be a non-empty string`);
      if (from === to) throw new ProfileError(`${label} spelling.${from} maps a word to itself`);
      if (baselineKeys && !baselineKeys.has(from)) {
        throw new ProfileError(`${label} spelling key "${from}" is not in the baseline vocabulary`);
      }
    }
  }

  // `spellingConflicts` is the -ize/-ise conflict family the profile accepts
  // (secretariat) or empties to enforce (british). Every entry must be a word
  // the vocabulary actually owns, otherwise a typo would silently widen the
  // conflict stance past anything the rules can enforce — fail closed.
  if ('spellingConflicts' in profile) {
    if (!Array.isArray(profile.spellingConflicts)) {
      throw new ProfileError(`${label} spellingConflicts must be an array`);
    }
    const conflictKeys = baselineKeys
      ?? (isPlainObject(profile.spelling) ? new Set(Object.keys(profile.spelling)) : null);
    const seenConflicts = new Set();
    for (const entry of profile.spellingConflicts) {
      if (!nonEmpty(entry)) throw new ProfileError(`${label} spellingConflicts must contain only non-empty strings`);
      if (seenConflicts.has(entry)) throw new ProfileError(`${label} spellingConflicts contains a duplicate entry "${entry}"`);
      seenConflicts.add(entry);
      if (conflictKeys && !conflictKeys.has(entry)) {
        throw new ProfileError(`${label} spellingConflicts entry "${entry}" is not in the baseline vocabulary`);
      }
    }
  }

  if ('terminology' in profile) {
    const terminology = profile.terminology;
    if (!isPlainObject(terminology)) throw new ProfileError(`${label} terminology must be an object`);
    checkKnownFields(terminology, new Set(['forbidden']), `${label} terminology`);
    if ('forbidden' in terminology) {
      if (!Array.isArray(terminology.forbidden)) throw new ProfileError(`${label} terminology.forbidden must be an array`);
      const seen = new Set();
      const normalised = [];
      for (const entry of terminology.forbidden) {
        const item = normaliseTerminologyEntry(entry);
        if (seen.has(item.from)) throw new ProfileError(`${label} terminology contains duplicate term "${item.from}"`);
        seen.add(item.from);
        normalised.push(item);
      }
      terminology.forbidden = normalised;
    }
  }

  if ('register' in profile) {
    const register = profile.register;
    if (!isPlainObject(register)) throw new ProfileError(`${label} register must be an object`);
    checkKnownFields(register, REGISTER_FIELDS, `${label} register`);
    const forbidden = register.forbidden || [];
    const approved = register.approved || [];
    if ('forbidden' in register) validateStringList(forbidden, `${label} register.forbidden`);
    if ('approved' in register) validateStringList(approved, `${label} register.approved`);
    const overlap = forbidden.filter(item => approved.includes(item));
    if (overlap.length) throw new ProfileError(`${label} register lists ${overlap[0]} as both forbidden and approved`);
  }

  if ('diplomacy' in profile) {
    const diplomacy = profile.diplomacy;
    if (!isPlainObject(diplomacy)) throw new ProfileError(`${label} diplomacy must be an object`);
    checkKnownFields(diplomacy, DIPLOMACY_FIELDS, `${label} diplomacy`);
    if ('claims' in diplomacy) {
      if (!Array.isArray(diplomacy.claims)) throw new ProfileError(`${label} diplomacy.claims must be an array`);
      const seen = new Set();
      diplomacy.claims.forEach((claim, index) => {
        validateClaim(claim, `${label} diplomacy.claims[${index}]`);
        if (seen.has(claim.id)) {
          throw new ProfileError(`${label} diplomacy.claims contains duplicate id "${claim.id}"`);
        }
        seen.add(claim.id);
      });
    }
  }

  // Custom rules: the organisation's own bounded pattern checks. Data only —
  // a regex and wording, never code — and fail-closed on every field, so a
  // typo cannot half-define a rule. The UE- prefix stays reserved for the
  // catalogue, and a custom id that collides with a shipped rule is refused.
  if ('customRules' in profile) {
    if (!Array.isArray(profile.customRules)) {
      throw new ProfileError(`${label} customRules must be an array`);
    }
    const seenCustom = new Set();
    for (const [index, rule] of profile.customRules.entries()) {
      const ruleLabel = `${label} customRules[${index}]`;
      if (!isPlainObject(rule)) throw new ProfileError(`${ruleLabel} must be an object`);
      checkKnownFields(rule, CUSTOM_RULE_FIELDS, ruleLabel);
      if (!nonEmpty(rule.id)) throw new ProfileError(`${ruleLabel} id must be a non-empty string`);
      if (rule.id.startsWith('UE-')) {
        throw new ProfileError(`${ruleLabel} id "${rule.id}" uses the reserved UE- prefix`);
      }
      if (!/^[A-Z][A-Z0-9]{0,11}-[A-Z0-9]{3,6}$/.test(rule.id)) {
        throw new ProfileError(`${ruleLabel} id "${rule.id}" must be ORG-001 style: uppercase prefix, dash, three to six characters`);
      }
      if (seenCustom.has(rule.id)) {
        throw new ProfileError(`${label} customRules contains duplicate id "${rule.id}"`);
      }
      seenCustom.add(rule.id);
      if (knownIds.includes(rule.id)) {
        throw new ProfileError(`${ruleLabel} id "${rule.id}" collides with a catalogue rule`);
      }
      if (!nonEmpty(rule.pattern)) throw new ProfileError(`${ruleLabel} pattern must be a non-empty string`);
      if (rule.pattern.length > 500) {
        throw new ProfileError(`${ruleLabel} pattern must be at most 500 characters`);
      }
      try {
        // One compile now: a pattern the engine cannot run must refuse the
        // profile instead of failing mid-scan.
        new RegExp(rule.pattern, 'gu');
      } catch (err) {
        throw new ProfileError(`${ruleLabel} pattern does not compile: ${err.message}`);
      }
      if (!nonEmpty(rule.message)) throw new ProfileError(`${ruleLabel} message must be a non-empty string`);
      if (rule.message.length > 300) {
        throw new ProfileError(`${ruleLabel} message must be at most 300 characters`);
      }
      if ('severity' in rule && !SEVERITIES.has(rule.severity)) {
        throw new ProfileError(`${ruleLabel} severity must be error, warning or info`);
      }
      if ('suggestion' in rule) {
        if (!nonEmpty(rule.suggestion)) throw new ProfileError(`${ruleLabel} suggestion must be a non-empty string`);
        if (rule.suggestion.length > 300) {
          throw new ProfileError(`${ruleLabel} suggestion must be at most 300 characters`);
        }
      }
      if ('source' in rule) {
        if (!nonEmpty(rule.source)) throw new ProfileError(`${ruleLabel} source must be a non-empty string`);
        if (rule.source.length > 200) {
          throw new ProfileError(`${ruleLabel} source must be at most 200 characters`);
        }
      }
    }
  }

  if ('severities' in profile) validateSeverities(profile.severities, knownIds, label);
  if ('rules' in profile) validateRuleSettings(profile.rules, knownIds, label);

  return profile;
}

/** Validate a named audit profile (publishing | accessibility | security). */
export function validateAuditProfile(value, { expectedName = null, meta = {}, label = 'audit profile' } = {}) {
  if (!isPlainObject(value)) throw new ProfileError(`${label} must be an object`);
  checkKnownFields(value, AUDIT_FIELDS, label);
  if (value.auditVersion !== 1) throw new ProfileError(`${label} auditVersion must be 1`);
  if (!KNOWN_AUDITS.has(value.name)) throw new ProfileError(`${label} name must be publishing, accessibility or security`);
  if (expectedName && value.name !== expectedName) throw new ProfileError(`${label} name "${value.name}" does not match "${expectedName}"`);
  if (!KNOWN_AUDITS.has(value.category)) throw new ProfileError(`${label} category must match a supported audit name`);
  if (value.category !== value.name) throw new ProfileError(`${label} category must equal name`);
  if (!nonEmpty(value.description)) throw new ProfileError(`${label} description must be a non-empty string`);
  if (!Array.isArray(value.rules) || !value.rules.length) throw new ProfileError(`${label} rules must be a non-empty array`);
  for (const id of value.rules) {
    if (!Object.hasOwn(meta, id)) throw new ProfileError(`${label} references unknown rule "${id}"`);
    if (meta[id].profile !== value.name) {
      throw new ProfileError(`${label} references rule "${id}", which belongs to the ${meta[id].profile || 'editorial'} set`);
    }
  }
  if (new Set(value.rules).size !== value.rules.length) throw new ProfileError(`${label} lists a rule twice`);
  return value;
}

/**
 * Merge an organisation profile over a base profile. Pure: returns a new
 * object, never mutates either input (so a bad profile cannot poison a later
 * run in the same process).
 */
export function applyProfile(base, profile) {
  const merged = {
    profileVersion: 1,
    name: profile.name ?? base.name,
    source: profile.source ?? base.source,
    description: profile.description ?? base.description,
    spelling: { ...base.spelling, ...(profile.spelling || {}) },
    // Replace, never extend: a profile that states the field decides the
    // conflict family wholesale (`[]` enforces, the six keys accept); one
    // that omits it inherits the baseline family unchanged.
    spellingConflicts: 'spellingConflicts' in profile
      ? [...profile.spellingConflicts]
      : [...(base.spellingConflicts || [])],
    terminology: { forbidden: [...(base.terminology?.forbidden || [])] },
    register: {
      forbidden: [...(base.register?.forbidden || [])],
      approved: [...(base.register?.approved || [])],
    },
    customRules: [...(base.customRules || [])],
    severities: { ...base.severities, ...(profile.severities || {}) },
    rules: { ...base.rules, ...(profile.rules || {}) },
    pageUrl: profile.pageUrl ?? base.pageUrl ?? null,
    diplomacy: { claims: [...(base.diplomacy?.claims || [])] },
  };

  // Claim entries merge by id: an organisation claim with a baseline id
  // replaces that entry wholesale (the sanctioned way to neutralise or reword
  // a default pattern); a new id is appended alongside the baseline set.
  for (const claim of profile.diplomacy?.claims || []) {
    const existing = merged.diplomacy.claims.findIndex(entry => entry.id === claim.id);
    if (existing >= 0) merged.diplomacy.claims[existing] = claim;
    else merged.diplomacy.claims.push(claim);
  }

  for (const entry of profile.terminology?.forbidden || []) {
    const normalised = normaliseTerminologyEntry(entry);
    const existing = merged.terminology.forbidden.findIndex(item =>
      (typeof item === 'string' ? item : item.from) === normalised.from);
    if (existing >= 0) merged.terminology.forbidden[existing] = normalised;
    else merged.terminology.forbidden.push(normalised);
  }

  for (const rule of profile.customRules || []) {
    const existing = merged.customRules.findIndex(entry => entry.id === rule.id);
    if (existing >= 0) merged.customRules[existing] = rule;
    else merged.customRules.push(rule);
  }

  for (const item of profile.register?.forbidden || []) {
    if (!merged.register.forbidden.includes(item)) merged.register.forbidden.push(item);
  }
  for (const item of profile.register?.approved || []) {
    if (!merged.register.approved.includes(item)) merged.register.approved.push(item);
  }

  return merged;
}

/**
 * Compile one knowledge-base claim into runnable pattern units. Each pattern
 * template is split on its placeholders; literal segments are regex-escaped
 * with whitespace loosened to \s+, and each placeholder becomes a
 * longest-first alternation of its phrases wrapped in word boundaries, so the
 * compiled pattern matches both claimants symmetrically and only whole words.
 * Flags are `gi`: detection is case-insensitive and every consumer resets
 * lastIndex before its exec loop.
 */
function compileClaim(claim) {
  const subjects = alternation(claim.subjects);
  const claimants = alternation(claim.claimants);
  const patterns = claim.patterns.map(pattern => {
    const parts = pattern.split(/(\{subject\}|\{claimant\})/g);
    let source = '';
    for (const part of parts) {
      if (part === '{subject}') source += `\\b(?:${subjects})\\b`;
      else if (part === '{claimant}') source += `\\b(?:${claimants})\\b`;
      else source += escapeReClaim(part).replace(/ /g, '\\s+');
    }
    return new RegExp(source, 'gi');
  });
  return {
    id: claim.id,
    topic: claim.topic,
    neutral: claim.neutral,
    unTerminology: claim.unTerminology,
    source: claim.source,
    patterns,
  };
}

const escapeReClaim = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function alternation(phrases) {
  const escaped = [...phrases].sort((a, b) => b.length - a.length).map(escapeReClaim);
  return escaped.join('|');
}

/** Turn a validated profile into the vocabulary the rules consume. */
export function buildVocabulary(profile, { registerAllow = [], claimsAllow = [] } = {}) {
  const spellings = Object.entries(profile.spelling || {});
  const terminology = (profile.terminology?.forbidden || []).map(normaliseTerminologyEntry);
  const forbidden = [...(profile.register?.forbidden || [])];
  const approved = [...(profile.register?.approved || [])];
  const registerExempt = new Set([...approved, ...registerAllow]);
  const claimAllow = new Set(claimsAllow);
  const claims = (profile.diplomacy?.claims || [])
    .filter(claim => !claimAllow.has(claim.id))
    .map(compileClaim);
  // One compiled regex per custom rule, consumed fresh (lastIndex reset) by
  // the rule runner; a match cap at run time bounds a runaway pattern.
  const customRules = (profile.customRules || []).map(rule => ({
    id: rule.id,
    re: new RegExp(rule.pattern, 'gu'),
    message: rule.message,
    suggestion: rule.suggestion ?? null,
    severity: rule.severity ?? 'warning',
    source: rule.source ?? null,
  }));
  return {
    spellings,
    // Set of every spelling key the merged vocabulary owns: UE-SP003 must not
    // double-report a word UE-SP001 already settles.
    spellingKeys: new Set(spellings.map(([from]) => from)),
    // The -ize/-ise conflict family the selected profile stance applies to.
    spellingConflicts: new Set(profile.spellingConflicts || []),
    terminology,
    register: forbidden,
    registerExempt,
    claims,
    customRules,
  };
}
