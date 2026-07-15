#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { parseArgs } from 'node:util';

function fail(message) {
  throw new Error(message);
}

function asUniqueMap(rows, label) {
  if (!Array.isArray(rows)) fail(`${label} must be an array`);
  const result = new Map();
  for (const row of rows) {
    if (!row || typeof row.slug !== 'string' || !row.slug || result.has(row.slug)) {
      fail(`${label} must contain unique non-empty slugs`);
    }
    result.set(row.slug, row);
  }
  return result;
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) =>
      `${JSON.stringify(key)}:${canonicalJson(value[key])}`
    ).join(',')}}`;
  }
  return JSON.stringify(value);
}

export function planLegacyAuditBindingCohorts({
  classification,
  bindingEvidence,
  expectedTargetedCount,
  expectedDriftCount,
}) {
  if (classification?.schemaVersion !== 1 || classification?.status !== 'classified') {
    fail('hash classification is not frozen');
  }
  if (bindingEvidence?.schemaVersion !== 1 || bindingEvidence?.status !== 'verified') {
    fail('legacy audit binding evidence is not frozen');
  }
  const hashEquivalent = asUniqueMap(
    classification?.cohorts?.legacy_algorithm_equivalent,
    'hash-equivalent cohort'
  );
  const drift = asUniqueMap(
    classification?.cohorts?.actual_or_unproven_drift,
    'drift cohort'
  );
  for (const slug of hashEquivalent.keys()) {
    if (drift.has(slug)) fail(`classification cohorts overlap for ${slug}`);
  }

  const evidence = asUniqueMap(bindingEvidence.entries, 'binding evidence');
  const bindingScope = new Set([...hashEquivalent.keys(), ...drift.keys()]);
  if (evidence.size !== bindingScope.size) {
    fail('binding evidence does not cover the hash-equivalent and drift cohorts exactly once');
  }
  for (const slug of evidence.keys()) {
    if (!bindingScope.has(slug)) fail(`binding evidence contains an out-of-scope slug: ${slug}`);
  }

  const targeted = [];
  const unprovenHashEquivalent = [];
  for (const [slug, row] of hashEquivalent) {
    const proof = evidence.get(slug);
    if (
      proof.skillId !== row.id
      || proof.sourceAuditId !== row.publicEligibilityAuditId
    ) fail(`frozen binding identity mismatch for ${slug}`);
    const decision = {
      slug,
      skillId: row.id,
      sourceAuditId: row.publicEligibilityAuditId,
      bindingVerified: proof.decision === 'verified',
      artifactGovernanceAllowed: proof.decision === 'verified',
      reason: proof.reason,
      planEntry: proof.planEntry,
    };
    (decision.bindingVerified ? targeted : unprovenHashEquivalent).push(decision);
  }

  const driftQuarantine = [];
  for (const [slug, row] of drift) {
    const proof = evidence.get(slug);
    if (
      proof.skillId !== row.id
      || proof.sourceAuditId !== row.publicEligibilityAuditId
    ) fail(`frozen drift binding identity mismatch for ${slug}`);
    driftQuarantine.push({
      slug,
      skillId: row.id,
      sourceAuditId: row.publicEligibilityAuditId,
      bindingVerified: proof.decision === 'verified',
      artifactGovernanceAllowed: false,
      reason: 'artifact_hash_drift_quarantined',
    });
  }
  targeted.sort((a, b) => a.slug.localeCompare(b.slug));
  unprovenHashEquivalent.sort((a, b) => a.slug.localeCompare(b.slug));
  driftQuarantine.sort((a, b) => a.slug.localeCompare(b.slug));

  if (
    expectedTargetedCount !== undefined
    && targeted.length !== expectedTargetedCount
  ) fail(`targeted binding count mismatch: expected ${expectedTargetedCount}, got ${targeted.length}`);
  if (
    expectedDriftCount !== undefined
    && driftQuarantine.length !== expectedDriftCount
  ) fail(`drift quarantine count mismatch: expected ${expectedDriftCount}, got ${driftQuarantine.length}`);

  const plan = {
    schemaVersion: 1,
    status: 'legacy_audit_binding_cohorts_planned',
    counts: {
      hashEquivalent: hashEquivalent.size,
      targeted: targeted.length,
      unprovenHashEquivalent: unprovenHashEquivalent.length,
      driftQuarantined: driftQuarantine.length,
    },
    targeted,
    unprovenHashEquivalent,
    driftQuarantine,
  };
  const bindingPlanIdentity = {
    schemaVersion: 1,
    entries: targeted.map((row) => {
      if (!row.planEntry || row.planEntry.slug !== row.slug) {
        fail(`verified binding evidence lacks an exact plan entry for ${row.slug}`);
      }
      return row.planEntry;
    }),
  };
  const bindingPlan = {
    ...bindingPlanIdentity,
    planSha256: createHash('sha256').update(canonicalJson(bindingPlanIdentity)).digest('hex'),
  };
  return {
    planSha256: createHash('sha256').update(canonicalJson(plan)).digest('hex'),
    plan,
    bindingPlan,
  };
}

function parseCount(value, name) {
  if (value === undefined) return undefined;
  if (!/^(0|[1-9][0-9]*)$/.test(value)) fail(`${name} must be a non-negative integer`);
  return Number(value);
}

export function main(argv = process.argv.slice(2)) {
  const { values } = parseArgs({
    args: argv,
    options: {
      classification: { type: 'string' },
      evidence: { type: 'string' },
      output: { type: 'string' },
      'expected-targeted': { type: 'string' },
      'expected-drift': { type: 'string' },
    },
    strict: true,
  });
  if (!values.classification || !values.evidence || !values.output) {
    fail('--classification, --evidence, and --output are required');
  }
  const result = planLegacyAuditBindingCohorts({
    classification: JSON.parse(readFileSync(values.classification, 'utf8')),
    bindingEvidence: JSON.parse(readFileSync(values.evidence, 'utf8')),
    expectedTargetedCount: parseCount(values['expected-targeted'], '--expected-targeted'),
    expectedDriftCount: parseCount(values['expected-drift'], '--expected-drift'),
  });
  writeFileSync(values.output, `${JSON.stringify(result, null, 2)}\n`, { flag: 'wx' });
  process.stdout.write(`${JSON.stringify(result.plan.counts)}\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
