#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const SUBMISSION_ID_RE = /Submission ID[^\r\n]*`([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})`/i;

function normalizeCount(value, name) {
  const count = Number(value);
  if (!Number.isSafeInteger(count) || count < 0) {
    throw new Error(`${name} must be a non-negative integer`);
  }
  return count;
}

function hasLabel(pullRequest, expected) {
  return Array.isArray(pullRequest?.labels)
    && pullRequest.labels.some((label) => (typeof label === 'string' ? label : label?.name) === expected);
}

function genericBody({ eventName, modifiedCount, deletedCount }) {
  return `## Summary

AI-powered auto-fix for SKILL.md validation errors.

| Metric | Value |
|--------|-------|
| Files Fixed | ${modifiedCount} |
| Empty Skills Deleted | ${deletedCount} |
| Triggered By | ${eventName} |

### Fixes Applied
- Added missing YAML frontmatter
- Fixed \`name\` field format (lowercase alphanumeric with hyphens)
- Added missing \`description\` field
- Truncated overly long descriptions
- **Deleted empty skill directories** (unfixable)

### After Merge
The \`sync-to-supabase.yml\` workflow will automatically update the database.

---
*Automated fix by validate-marketplace.yml*
`;
}

export function buildAutoFixPrMetadata({
  eventName,
  event,
  modifiedCount: rawModifiedCount,
  deletedCount: rawDeletedCount,
}) {
  const modifiedCount = normalizeCount(rawModifiedCount, 'modifiedCount');
  const deletedCount = normalizeCount(rawDeletedCount, 'deletedCount');
  const pullRequest = eventName === 'pull_request' ? event?.pull_request : null;
  const sourceBody = typeof pullRequest?.body === 'string' ? pullRequest.body : '';
  const submissionId = sourceBody.match(SUBMISSION_ID_RE)?.[1]?.toLowerCase() ?? null;
  const pendingReview = hasLabel(pullRequest, 'pending-review');

  if (pullRequest && pendingReview !== Boolean(submissionId)) {
    throw new Error('Submission auto-fix metadata is incomplete: pending-review and a valid Submission ID must be present together');
  }

  if (!pullRequest || !pendingReview || !submissionId) {
    return {
      body: genericBody({ eventName, modifiedCount, deletedCount }),
      inheritPendingReview: false,
      submissionId: null,
      sourcePrNumber: null,
    };
  }

  const sourcePrNumber = Number(pullRequest.number);
  if (!Number.isSafeInteger(sourcePrNumber) || sourcePrNumber <= 0) {
    throw new Error('Submission auto-fix metadata is missing a valid source PR number');
  }

  const repairSummary = `## Automated SKILL.md Repair

This replacement PR preserves the source submission metadata so its own merge can run the normal approval workflow.

| Metric | Value |
|--------|-------|
| Source PR | #${sourcePrNumber} |
| Files Fixed | ${modifiedCount} |
| Empty Skills Deleted | ${deletedCount} |
| Triggered By | ${eventName} |

The \`pending-review\` label is inherited explicitly. Approval does not depend on source commits surviving a squash merge.

---
*Automated fix by validate-marketplace.yml*
`;

  return {
    body: `${sourceBody.trimEnd()}\n\n---\n\n${repairSummary}`,
    inheritPendingReview: true,
    submissionId,
    sourcePrNumber,
  };
}

async function main() {
  const { values } = parseArgs({
    options: {
      'event-path': { type: 'string' },
      'event-name': { type: 'string' },
      'body-file': { type: 'string' },
      'modified-count': { type: 'string' },
      'deleted-count': { type: 'string' },
    },
    strict: true,
  });

  for (const name of ['event-path', 'event-name', 'body-file', 'modified-count', 'deleted-count']) {
    if (values[name] === undefined) throw new Error(`Missing required --${name}`);
  }

  const event = JSON.parse(await readFile(values['event-path'], 'utf8'));
  const metadata = buildAutoFixPrMetadata({
    eventName: values['event-name'],
    event,
    modifiedCount: values['modified-count'],
    deletedCount: values['deleted-count'],
  });

  await writeFile(values['body-file'], metadata.body, 'utf8');
  process.stdout.write(`${JSON.stringify({
    inheritPendingReview: metadata.inheritPendingReview,
    submissionId: metadata.submissionId,
    sourcePrNumber: metadata.sourcePrNumber,
  })}\n`);
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : '';
if (invokedPath === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
