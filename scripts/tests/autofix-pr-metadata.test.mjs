import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import { buildAutoFixPrMetadata } from '../build-autofix-pr-metadata.mjs';
import { parseCanonicalSubmissionId } from '../submission-metadata.mjs';

const submissionId = 'e950f6aa-4390-426c-b23e-17b2bc4c3670';
const sourceHeadSha = 'a'.repeat(40);

function pullRequestEvent({ body, labels = [], number = 2443, headSha = sourceHeadSha } = {}) {
  return {
    pull_request: {
      number,
      body: body ?? '',
      labels: labels.map((name) => ({ name })),
      head: { sha: headSha },
    },
  };
}

test('pending-review auto-fix canonicalizes one anchored Submission ID for its own merge event', () => {
  const uppercaseId = submissionId.toUpperCase();
  const sourceBody = `## Skill Submission\n\n**Submission ID**: \`${uppercaseId}\`\n**Source**: https://github.com/example/skills`;
  const result = buildAutoFixPrMetadata({
    eventName: 'pull_request',
    event: pullRequestEvent({ body: sourceBody, labels: ['pending-review'] }),
    modifiedCount: 1,
    deletedCount: 0,
  });

  assert.equal(result.inheritPendingReview, true);
  assert.equal(result.submissionId, submissionId);
  assert.equal(result.sourceHeadSha, sourceHeadSha);
  assert.match(result.body, new RegExp('^\\*\\*Submission ID\\*\\*: `' + submissionId + '`$', 'm'));
  assert.doesNotMatch(result.body, new RegExp(uppercaseId));
  assert.equal(parseCanonicalSubmissionId(result.body), submissionId, 'on-pr-merge consumes the replacement body through the same canonical parser');
  assert.match(result.body, new RegExp('^\\*\\*Source PR Head SHA\\*\\*: `' + sourceHeadSha + '`$', 'm'));
  assert.match(
    result.body,
    new RegExp('^\\*\\*Authorization Lease Ref\\*\\*: `refs/tags/autofix-approval-leases/' + submissionId + '`$', 'm'),
  );
  assert.match(result.body, /Files Fixed \| 1/);
});

test('duplicate anchored Submission IDs fail closed instead of selecting one', () => {
  const sourceBody = `**Submission ID**: \`${submissionId}\`\n\n**Submission ID**: \`${submissionId}\``;

  assert.throws(
    () => buildAutoFixPrMetadata({
      eventName: 'pull_request',
      event: pullRequestEvent({ body: sourceBody, labels: ['pending-review'] }),
      modifiedCount: 1,
      deletedCount: 0,
    }),
    /exactly one anchored Submission ID/i,
  );
});

test('quoted Submission ID text fails closed instead of becoming approval metadata', () => {
  const sourceBody = `> **Submission ID**: \`${submissionId}\``;

  assert.throws(
    () => buildAutoFixPrMetadata({
      eventName: 'pull_request',
      event: pullRequestEvent({ body: sourceBody, labels: ['pending-review'] }),
      modifiedCount: 1,
      deletedCount: 0,
    }),
    /exactly one anchored Submission ID/i,
  );
});

test('pending-review without a unique canonical Submission ID fails closed', () => {
  assert.throws(
    () => buildAutoFixPrMetadata({
      eventName: 'pull_request',
      event: pullRequestEvent({ body: 'missing metadata', labels: ['pending-review'] }),
      modifiedCount: 1,
      deletedCount: 0,
    }),
    /exactly one anchored Submission ID/i,
  );
});

test('non-submission auto-fix remains unlabeled and uses the generic body', () => {
  const result = buildAutoFixPrMetadata({
    eventName: 'push',
    event: {},
    modifiedCount: 1,
    deletedCount: 0,
  });

  assert.equal(result.inheritPendingReview, false);
  assert.equal(result.submissionId, null);
  assert.equal(result.sourceHeadSha, null);
  assert.match(result.body, /AI-powered auto-fix/);
  assert.doesNotMatch(result.body, /Submission ID/);
});

test('workflows use the shared canonical parser and event-head lifecycle guard', async () => {
  const [validateWorkflow, mergeWorkflow, testWorkflow] = await Promise.all([
    readFile(new URL('../../.github/workflows/validate-marketplace.yml', import.meta.url), 'utf8'),
    readFile(new URL('../../.github/workflows/on-pr-merge.yml', import.meta.url), 'utf8'),
    readFile(new URL('../../.github/workflows/test-recalculate-scores.yml', import.meta.url), 'utf8'),
  ]);
  const createStep = validateWorkflow.match(/- name: Create PR for SKILL\.md fixes[\s\S]*?(?=\n\s{6}- name:)/)?.[0] ?? '';

  assert.match(validateWorkflow, /pull_request:\s*\n\s+types:\s*\[[^\]]*edited[^\]]*\]/);
  const concurrencyGroup = validateWorkflow.match(/concurrency:\s*\n\s+group:\s*([^\n]+)/)?.[1] ?? '';
  assert.match(concurrencyGroup, /pull_request\.number/);
  assert.doesNotMatch(concurrencyGroup, /head\.sha|github\.sha/);
  assert.match(validateWorkflow, /github\.event\.pull_request\.head\.sha/);
  assert.match(validateWorkflow, /git fetch --depth 1 origin "\$EVENT_HEAD_SHA"/);
  assert.match(validateWorkflow, /autofix-pr-lifecycle\.mjs[\s\S]*--mode preflight/);
  assert.match(createStep, /autofix-pr-lifecycle\.mjs[\s\S]*--mode ensure-replacement/);
  assert.match(createStep, /autofix-pr-lifecycle\.mjs[\s\S]*--mode supersede/);
  assert.match(createStep, /--body-file/);
  assert.doesNotMatch(createStep, /PR_ARGS\+=\(--label/);
  assert.match(mergeWorkflow, /actions\/checkout@v5/);
  assert.match(mergeWorkflow, /scripts\/submission-authorization\.mjs[\s\S]*--mode verify-merge/);
  assert.match(mergeWorkflow, /authorization[\s\S]*Find pending skills and commit to skills directory/i);
  assert.doesNotMatch(mergeWorkflow, /grep -oE 'Submission ID/);
  assert.match(testWorkflow, /scripts\/build-autofix-pr-metadata\.mjs/);
  assert.match(testWorkflow, /scripts\/submission-metadata\.mjs/);
  assert.match(testWorkflow, /scripts\/submission-authorization\.mjs/);
  assert.match(testWorkflow, /scripts\/autofix-pr-lifecycle\.mjs/);
  assert.match(testWorkflow, /\.github\/workflows\/validate-marketplace\.yml/);
  assert.match(testWorkflow, /\.github\/workflows\/on-pr-merge\.yml/);
  assert.match(testWorkflow, /node --test scripts\/tests\/autofix-pr-metadata\.test\.mjs/);
});
