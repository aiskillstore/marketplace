// un-editorial-check — source-registry contract tests.
//
// Standalone: `node tests/audit-registry.mjs`. Locks rules/sources.json as a
// verifiable registry rather than prose:
//
//   1. schema: the registry declares registryVersion, retrieved and a
//      non-empty sources list; every entry carries id, title, publisher, url,
//      retrieved, scope, appliesTo and evidence, plus a rationale recorded
//      under note;
//   2. identifiers: kebab-case shape and globally unique;
//   3. urls: parse as https URLs with a host;
//   4. dates: real calendar days in YYYY-MM-DD form, and no entry retrieved
//      after the registry itself;
//   5. appliesTo: a catalogue rule ID (UE-XX999 shape, present in
//      rules/catalogue.json) or profile:<name> resolved by name shape, never
//      by installation path;
//   6. catalogue `sources` references: any rule that lists registry IDs must
//      reference IDs that exist.
//
// Every check runs through one collect-first validator so the mutation
// self-checks below can prove the validator rejects bad data — not merely
// that today's registry happens to pass. Mutations happen on in-memory
// copies; no file is ever written.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const registry = JSON.parse(fs.readFileSync(path.join(root, 'rules', 'sources.json'), 'utf8'));
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'rules', 'catalogue.json'), 'utf8'));

const ENTRY_KEYS = ['id', 'title', 'publisher', 'url', 'retrieved', 'scope', 'appliesTo', 'evidence'];
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const RULE_ID = /^UE-[A-Z]{2}\d{3}$/;
const DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

const isRealDate = (value) => {
  const match = typeof value === 'string' && DATE.exec(value);
  if (!match) return false;
  const [, year, month, day] = match;
  const parsed = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
  return parsed.getUTCFullYear() === Number(year)
    && parsed.getUTCMonth() === Number(month) - 1
    && parsed.getUTCDate() === Number(day);
};

const nonEmptyString = (value) => typeof value === 'string' && value.trim().length > 0;

/** Collect every schema violation instead of stopping at the first. */
const validate = (reg, cat) => {
  const problems = [];
  const catalogueIds = new Set((cat.rules || []).map(entry => entry.id));
  const registryIds = new Set((reg.sources || []).map(entry => entry.id));

  if (!Number.isInteger(reg.registryVersion) || reg.registryVersion < 1) {
    problems.push('registryVersion must be a positive integer');
  }
  if (!isRealDate(reg.retrieved)) problems.push(`registry retrieved is not a real date: ${reg.retrieved}`);
  if (!Array.isArray(reg.sources) || !reg.sources.length) {
    problems.push('sources must be a non-empty array');
    return problems;
  }

  const seen = new Set();
  reg.sources.forEach((entry, index) => {
    const label = entry && entry.id ? entry.id : `sources[${index}]`;
    if (!entry || typeof entry !== 'object') {
      problems.push(`${label}: entry must be an object`);
      return;
    }
    for (const key of ENTRY_KEYS) {
      if (!(key in entry)) problems.push(`${label}: missing key ${key}`);
    }
    if (!('note' in entry) && !('rationale' in entry)) {
      problems.push(`${label}: a rationale is recorded under note or rationale`);
    }
    if (!nonEmptyString(entry.id)) problems.push(`${label}: id must be a non-empty string`);
    else if (!KEBAB.test(entry.id)) problems.push(`${label}: id must be kebab-case`);
    else if (seen.has(entry.id)) problems.push(`${label}: duplicate id`);
    else seen.add(entry.id);
    for (const key of ['title', 'publisher', 'scope']) {
      if (key in entry && !nonEmptyString(entry[key])) problems.push(`${label}: ${key} must be a non-empty string`);
    }
    // Evidence is a string on every entry. An empty one is allowed only for
    // an honest negative — the note must record that no evidence exists
    // (dead source, unretrievable document) rather than the entry silently
    // carrying nothing.
    if ('evidence' in entry) {
      if (typeof entry.evidence !== 'string') {
        problems.push(`${label}: evidence must be a string`);
      } else if (!entry.evidence.trim()) {
        const note = typeof entry.note === 'string' ? entry.note : '';
        if (!/^honest negative\b/i.test(note.trim())) {
          problems.push(`${label}: empty evidence must be recorded as an honest negative in the note`);
        }
      }
    }
    if ('url' in entry) {
      let url;
      try { url = new URL(entry.url); } catch { url = null; }
      if (!url) problems.push(`${label}: url does not parse: ${entry.url}`);
      else if (url.protocol !== 'https:') problems.push(`${label}: url must be https`);
      else if (!url.hostname) problems.push(`${label}: url has no host`);
    }
    if ('retrieved' in entry) {
      if (!isRealDate(entry.retrieved)) problems.push(`${label}: retrieved is not a real date: ${entry.retrieved}`);
      else if (isRealDate(reg.retrieved) && entry.retrieved > reg.retrieved) {
        problems.push(`${label}: retrieved ${entry.retrieved} is after the registry date ${reg.retrieved}`);
      }
    }
    if ('appliesTo' in entry) {
      if (!Array.isArray(entry.appliesTo) || !entry.appliesTo.length) {
        problems.push(`${label}: appliesTo must be a non-empty array`);
      } else {
        for (const target of entry.appliesTo) {
          if (typeof target !== 'string') { problems.push(`${label}: appliesTo entry must be a string`); continue; }
          if (target.startsWith('profile:')) {
            // Resolved by name shape, not by installation path (see
            // docs/CLAIM-EVIDENCE-AUDIT.md row 16): the alias must look like
            // a bundled profile name, without probing the filesystem.
            const name = target.slice('profile:'.length);
            if (!KEBAB.test(name)) problems.push(`${label}: profile target must be a kebab-case name: ${target}`);
          } else if (!RULE_ID.test(target)) {
            problems.push(`${label}: appliesTo target must be a catalogue rule ID or profile:<name>: ${target}`);
          } else if (!catalogueIds.has(target)) {
            problems.push(`${label}: appliesTo references an unknown rule: ${target}`);
          }
        }
      }
    }
  });

  // Conditional: catalogue rules may carry a `sources` key (the spelling
  // conflict work adds it). When present, every reference must exist here.
  for (const rule of cat.rules || []) {
    if (!Array.isArray(rule.sources)) continue;
    for (const reference of rule.sources) {
      if (!registryIds.has(reference)) problems.push(`${rule.id}: sources references an unknown registry id: ${reference}`);
    }
  }
  return problems;
};

// --- 1. the shipped registry validates clean --------------------------------

{
  const problems = validate(registry, catalogue);
  assert.deepEqual(problems, [], `rules/sources.json must validate:\n${problems.join('\n')}`);
  assert(registry.sources.length >= 20, `expected a populated registry, got ${registry.sources.length} entries`);
}

console.log('ok — registry schema: keys, kebab-unique ids, https urls, real dates, appliesTo targets');

// --- 2. mutation self-checks: the validator rejects bad data ----------------

{
  const clone = () => JSON.parse(JSON.stringify(registry));
  const expectProblem = (mutate, needle) => {
    const candidate = clone();
    mutate(candidate);
    const problems = validate(candidate, catalogue);
    assert(problems.some(problem => problem.includes(needle)),
      `mutation must be reported as: ${needle}\n got: ${problems.join(' | ') || 'no problems'}`);
  };

  // duplicate identifier
  expectProblem(candidate => { candidate.sources.push({ ...candidate.sources[0] }); }, 'duplicate id');
  // non-kebab identifier
  expectProblem(candidate => { candidate.sources[0].id = 'Not_Kebab'; }, 'kebab-case');
  // non-https url
  expectProblem(candidate => { candidate.sources[0].url = 'http://example.org/report'; }, 'must be https');
  // unparsable url
  expectProblem(candidate => { candidate.sources[0].url = 'not a url'; }, 'does not parse');
  // retrieval after the registry date
  expectProblem(candidate => { candidate.sources[0].retrieved = '2099-01-01'; }, 'after the registry date');
  // impossible calendar day
  expectProblem(candidate => { candidate.sources[0].retrieved = '2026-02-30'; }, 'not a real date');
  // unknown rule reference
  expectProblem(candidate => { candidate.sources[0].appliesTo = ['UE-ZZ999']; }, 'unknown rule');
  // malformed rule ID shape
  expectProblem(candidate => { candidate.sources[0].appliesTo = ['UE-SP1']; }, 'must be a catalogue rule ID');
  // profile target with a non-name shape
  expectProblem(candidate => { candidate.sources[0].appliesTo = ['profile:Un V1']; }, 'kebab-case name');
  // missing rationale
  expectProblem(candidate => { delete candidate.sources[0].note; }, 'rationale is recorded under note');
  // evidence emptied without recording a negative result
  expectProblem(candidate => { candidate.sources[0].evidence = '  '; }, 'honest negative in the note');

  // catalogue -> registry references, today and once rules gain `sources`
  {
    const withSource = JSON.parse(JSON.stringify(catalogue));
    const target = withSource.rules.find(rule => rule.id === 'UE-SP001');
    assert(target, 'UE-SP001 must exist for the sources self-check');
    assert.deepEqual(validate(registry, withSource), [], 'a valid sources reference must validate clean');
    target.sources = ['not-a-registry-id'];
    const problems = validate(registry, withSource);
    assert(problems.some(problem => problem.includes('unknown registry id')),
      `a bad catalogue sources reference must be reported:\n${problems.join('\n') || 'no problems'}`);
  }

  // an empty registry is not a registry
  {
    const problems = validate({ registryVersion: 1, retrieved: '2026-09-27', sources: [] }, catalogue);
    assert(problems.some(problem => problem.includes('non-empty array')),
      'an empty sources list must be reported');
  }
}

console.log('ok — registry mutations: each broken variant is rejected by the validator');
