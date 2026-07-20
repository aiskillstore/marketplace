#!/usr/bin/env node

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

export const INCIDENT = Object.freeze({
  dryRun: {
    id: 29743150038,
    sha: 'd75b0863d962bc58cf69d554f8fa6ea67a5c040a',
    artifactId: 8461534557,
    artifactDigest: 'sha256:627c18c8d1c127ed6fb4d5020043dae90f35643550b37e6b0150a76233dbfc4b',
  },
  failedRun: {
    id: 29744338076,
    sha: 'd75b0863d962bc58cf69d554f8fa6ea67a5c040a',
    artifactId: 8461872394,
    artifactDigest: 'sha256:e36360f2dd23fae710d9c6ea3a0f02e40b55b31fe18b57f354a62542b8560b50',
    jobId: 88358488559,
    runnerId: 174,
    runnerName: 'docker-runner-199-4-2',
  },
});

const STABLE_SKILL_FIELDS = [
  'id', 'slug', 'plugin_path', 'marketplace_commit_sha', 'content_hash', 'tree_hash',
  'artifact_revision', 'current_artifact_version_id', 'status', 'public_eligible',
  'public_eligibility_audit_id', 'published_at', 'updated_at', 'quality_score',
  'quality_tier', 'quality_score_calculated_at', 'current_quality_score_snapshot_id',
];

function exactRun(run, expected, conclusion) {
  assert.equal(run.id, expected.id);
  assert.equal(run.head_sha, expected.sha);
  assert.equal(run.name, 'Govern Fresh Canonical Audits');
  assert.equal(run.event, 'workflow_dispatch');
  assert.equal(run.head_branch, 'main');
  assert.equal(run.run_attempt, 1);
  assert.equal(run.actor?.login, 'mylukin');
  assert.equal(run.triggering_actor?.login, 'mylukin');
  assert.equal(run.conclusion, conclusion);
}

function exactArtifact(response, name, expected) {
  const matches = response.artifacts.filter((artifact) => artifact.id === expected.artifactId
    && artifact.name === name && artifact.expired === false
    && artifact.digest === expected.artifactDigest);
  assert.equal(matches.length, 1);
}

function rowMap(rows, ids) {
  return new Map(rows.filter((row) => ids.has(row.id)).map((row) => [row.id, row]));
}

function stableSkill(row) {
  return Object.fromEntries(STABLE_SKILL_FIELDS.map((field) => [field, row[field]]));
}

export function verifyZeroWriteRecovery(input) {
  const { boundary, originalInventory, currentInventory, dryRun, failedRun,
    dryArtifacts, failedArtifacts, failedJobs } = input;
  assert.equal(boundary.schemaVersion, 1);
  assert.equal(boundary.status, 'fresh_canonical_audit_frozen');
  assert.equal(boundary.candidates.length, 10);
  exactRun(dryRun, INCIDENT.dryRun, 'success');
  exactRun(failedRun, INCIDENT.failedRun, 'failure');
  exactArtifact(dryArtifacts, `fresh-canonical-audit-boundary-${INCIDENT.dryRun.id}`, INCIDENT.dryRun);
  exactArtifact(failedArtifacts, `fresh-canonical-audit-execution-${INCIDENT.failedRun.id}`, INCIDENT.failedRun);

  const job = failedJobs.jobs.find((candidate) => candidate.id === INCIDENT.failedRun.jobId);
  assert(job);
  assert.equal(job.name, 'execute-boundary');
  assert.equal(job.runner_id, INCIDENT.failedRun.runnerId);
  assert.equal(job.runner_name, INCIDENT.failedRun.runnerName);
  assert.equal(job.conclusion, 'failure');
  const steps = new Map(job.steps.map((step) => [step.name, step.conclusion]));
  for (const name of [
    'Checkout complete Marketplace history',
    'Normalize full checkout and verify governance runtime',
    'Validate execute inputs',
    'Download and authenticate the successful frozen boundary',
    'Generate GitHub App token',
    'Download exact audited CLI 2.15.5',
    'Verify frozen CLI identity',
    'Rematerialize exact source and overlay only frozen fresh reports',
  ]) assert.equal(steps.get(name), 'success');
  assert.equal(steps.get('Execute resumable compound governance, score, and cache closure'), 'failure');
  for (const name of [
    'Fetch exact post-execution artifact and Pack evidence',
    'Verify every P0/P1 download, install, NPX, Pack, and MCP channel',
    'Seal successful execute closure for the next cursor',
  ]) assert.equal(steps.get(name), 'skipped');

  const ids = new Set(boundary.candidates.map((candidate) => candidate.row.skillId));
  assert.equal(ids.size, 10);
  const original = rowMap(originalInventory.rows, ids);
  const current = rowMap(currentInventory.rows, ids);
  assert.equal(original.size, 10);
  assert.equal(current.size, 10);
  for (const candidate of boundary.candidates) {
    const before = original.get(candidate.row.skillId);
    const now = current.get(candidate.row.skillId);
    assert.deepEqual(stableSkill(now), stableSkill(before));
    assert.equal(now.artifact_revision, 0);
    assert.equal(now.current_artifact_version_id, null);
    assert.equal(now.content_hash, candidate.rpcPayload.p_expected_legacy_content_hash);
    assert.equal(now.tree_hash, candidate.rpcPayload.p_expected_legacy_tree_hash);
    assert.equal(now.public_eligibility_audit_id, candidate.rpcPayload.p_expected_latest_audit_id);
  }
  for (const inventory of [originalInventory, currentInventory]) {
    assert.equal(inventory.artifacts.filter((row) => ids.has(row.skill_id)).length, 0);
    assert.equal(inventory.observations.filter((row) => ids.has(row.skill_id)).length, 0);
  }
  return { count: ids.size };
}

function option(args, name) {
  const index = args.indexOf(name);
  assert(index >= 0 && args[index + 1], `missing ${name}`);
  return args[index + 1];
}

export function main(args = process.argv.slice(2)) {
  const read = (name) => JSON.parse(readFileSync(option(args, name), 'utf8'));
  const result = verifyZeroWriteRecovery({
    boundary: read('--boundary'),
    originalInventory: read('--original-inventory'),
    currentInventory: read('--current-inventory'),
    dryRun: read('--dry-run'),
    failedRun: read('--failed-run'),
    dryArtifacts: read('--dry-artifacts'),
    failedArtifacts: read('--failed-artifacts'),
    failedJobs: read('--failed-jobs'),
  });
  process.stdout.write(`${JSON.stringify({ status: 'zero_write_recovery_verified', ...result })}\n`);
}

if (import.meta.url === pathToFileURL(resolve(process.argv[1] || '')).href) {
  try { main(); } catch (error) {
    process.stderr.write(`zero-write recovery verification failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
