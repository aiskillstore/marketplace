#!/usr/bin/env node

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

function fail(message) {
  throw new Error(`Artifact governance campaign finalizer: ${message}`);
}

async function post({ endpoint, fetchImpl, secret, body }) {
  const response = await fetchImpl(endpoint, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${secret}`,
      'Content-Type': 'application/json',
      'User-Agent': 'skillstore-artifact-governance-finalizer',
    },
    body: JSON.stringify(body),
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) fail(`catalog epoch ${body.action} failed with HTTP ${response.status}`);
  return payload;
}

export async function activateCampaignCache({
  campaignProofSha256,
  endpoint = 'https://skillstore.io/api/cache/catalog-epoch',
  expectedEpoch,
  fetchImpl = fetch,
  readbackAttempts = 6,
  secret,
  sleepImpl = sleep,
}) {
  if (!secret || typeof expectedEpoch !== 'string' || expectedEpoch.length === 0
    || !/^[0-9a-f]{64}$/.test(campaignProofSha256 || '')
    || !Number.isSafeInteger(readbackAttempts) || readbackAttempts < 1) {
    fail('invalid activation inputs');
  }
  const nextEpoch = `g-${campaignProofSha256.slice(0, 32)}`;
  const before = await post({ endpoint, fetchImpl, secret, body: { action: 'read' } });
  const freshTransition = before?.epoch === expectedEpoch && before?.converged === true;
  const ambiguousCommittedTransition = before?.epoch === nextEpoch;
  if (before?.changed !== false || (!freshTransition && !ambiguousCommittedTransition)) {
    fail(`catalog epoch drifted before activation: expected ${expectedEpoch}, got ${before?.epoch}`);
  }
  const bump = await post({
    endpoint,
    fetchImpl,
    secret,
    body: { action: 'bump', expectedEpoch, nextEpoch },
  });
  if (bump?.changed !== true || bump?.previousEpoch !== expectedEpoch
    || bump?.epoch !== nextEpoch || bump?.converged !== true) {
    fail('catalog epoch bump returned an invalid transition');
  }

  let readback = null;
  for (let attempt = 1; attempt <= readbackAttempts; attempt += 1) {
    readback = await post({ endpoint, fetchImpl, secret, body: { action: 'read' } });
    if (readback?.epoch === bump.epoch && readback?.changed === false
      && readback?.converged === true) break;
    if (attempt < readbackAttempts) await sleepImpl(attempt * 1_000);
  }
  if (readback?.epoch !== bump.epoch || readback?.changed !== false
    || readback?.converged !== true) {
    fail(`catalog epoch ${bump.epoch} did not converge`);
  }
  return {
    schemaVersion: 1,
    status: 'artifact_governance_catalog_activated',
    campaignProofSha256,
    previousEpoch: expectedEpoch,
    epoch: bump.epoch,
    readbackVerified: true,
  };
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index < 0 || !args[index + 1] || args[index + 1].startsWith('--')) fail(`missing ${name}`);
  return args[index + 1];
}

export async function main(args = process.argv.slice(2)) {
  const siteUrl = option(args, '--site-url').replace(/\/$/, '');
  const output = resolve(option(args, '--output'));
  const result = await activateCampaignCache({
    campaignProofSha256: option(args, '--campaign-proof-sha256'),
    endpoint: `${siteUrl}/api/cache/catalog-epoch`,
    expectedEpoch: option(args, '--expected-epoch'),
    secret: process.env.CACHE_INVALIDATE_SECRET,
  });
  mkdirSync(dirname(output), { recursive: true });
  writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
}

if (import.meta.url === pathToFileURL(resolve(process.argv[1] || '')).href) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
