#!/usr/bin/env node

import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const PROVIDER_STEP = 'Sync skills to Supabase';

export function evaluateProviderRerun({ currentAttempt, previousAttempts }) {
  if (!Number.isSafeInteger(currentAttempt) || currentAttempt < 1) {
    return { allowed: false, reason: 'invalid-current-attempt' };
  }
  if (currentAttempt === 1) {
    return { allowed: true, reason: 'first-attempt' };
  }
  if (!Array.isArray(previousAttempts) || previousAttempts.length !== currentAttempt - 1) {
    return { allowed: false, reason: 'incomplete-prior-attempt-evidence' };
  }

  const byAttempt = new Map();
  for (const record of previousAttempts) {
    if (!record || !Number.isSafeInteger(record.attempt) || byAttempt.has(record.attempt)) {
      return { allowed: false, reason: 'malformed-prior-attempt-evidence' };
    }
    byAttempt.set(record.attempt, record);
  }

  for (let attempt = 1; attempt < currentAttempt; attempt += 1) {
    const record = byAttempt.get(attempt);
    if (!record || !Array.isArray(record.jobs)) {
      return { allowed: false, reason: `attempt-${attempt}-missing-jobs` };
    }
    const providerSteps = record.jobs.flatMap((job) =>
      Array.isArray(job?.steps) ? job.steps.filter((step) => step?.name === PROVIDER_STEP) : []);
    if (providerSteps.length !== 1) {
      return { allowed: false, reason: `attempt-${attempt}-provider-evidence-count-${providerSteps.length}` };
    }
    const conclusion = providerSteps[0].conclusion;
    if (conclusion !== 'skipped') {
      const normalized = typeof conclusion === 'string' && conclusion !== '' ? conclusion : 'unknown';
      return { allowed: false, reason: `attempt-${attempt}-provider-${normalized}` };
    }
  }

  return { allowed: true, reason: 'all-prior-provider-steps-skipped' };
}

function parseArgs(argv) {
  const inputIndex = argv.indexOf('--input');
  if (inputIndex === -1 || !argv[inputIndex + 1] || argv.length !== 2) {
    throw new Error('Usage: guard-provider-rerun.mjs --input <prior-attempts.json>');
  }
  return argv[inputIndex + 1];
}

function main() {
  const inputPath = parseArgs(process.argv.slice(2));
  const payload = JSON.parse(readFileSync(inputPath, 'utf8'));
  const decision = evaluateProviderRerun(payload);
  console.log(JSON.stringify(decision));
  if (!decision.allowed) {
    console.error(`Provider replay blocked: ${decision.reason}`);
    process.exitCode = 1;
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
