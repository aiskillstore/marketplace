import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import { buildAutoFixPrMetadata } from '../build-autofix-pr-metadata.mjs';

const submissionId = 'e950f6aa-4390-426c-b23e-17b2bc4c3670';

function pullRequestEvent({ body, labels = [], number = 2443 } = {}) {
  return {
    pull_request: {
      number,
      body: body ?? '',
      labels: labels.map((name) => ({ name })),
    },
  };
}

test('pending-review auto-fix preserves submission metadata for its own merge event', () => {
  const sourceBody = `## Skill Submission\n\n**Submission ID**: \`${submissionId}\`\n**Source**: https://github.com/example/skills`;
  const result = buildAutoFixPrMetadata({
    eventName: 'pull_request',
    event: pullRequestEvent({ body: sourceBody, labels: ['pending-review'] }),
    modifiedCount: 1,
    deletedCount: 0,
  });

  assert.equal(result.inheritPendingReview, true);
  assert.equal(result.submissionId, submissionId);
  assert.ok(result.body.includes('**Submission ID**: `' + submissionId + '`'));
  assert.match(result.body, /\| Source PR \| #2443 \|/);
  assert.match(result.body, /Files Fixed \| 1/);
});

test('metadata inheritance does not depend on source commits surviving a squash merge', () => {
  const result = buildAutoFixPrMetadata({
    eventName: 'pull_request',
    event: pullRequestEvent({
      body: `**Submission ID**: \`${submissionId}\``,
      labels: ['pending-review'],
    }),
    modifiedCount: 2,
    deletedCount: 1,
  });

  assert.equal(result.inheritPendingReview, true);
  assert.equal(result.submissionId, submissionId);
  assert.equal(result.sourcePrNumber, 2443);
});

test('pending-review without a valid submission ID fails closed', () => {
  assert.throws(
    () => buildAutoFixPrMetadata({
      eventName: 'pull_request',
      event: pullRequestEvent({ body: 'missing metadata', labels: ['pending-review'] }),
      modifiedCount: 1,
      deletedCount: 0,
    }),
    /pending-review.*Submission ID/i,
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
  assert.match(result.body, /AI-powered auto-fix/);
  assert.doesNotMatch(result.body, /Submission ID/);
});

test('validate workflow uses event metadata and body-file instead of commit history', async () => {
  const workflow = await readFile(new URL('../../.github/workflows/validate-marketplace.yml', import.meta.url), 'utf8');
  const createStep = workflow.match(/- name: Create PR for SKILL\.md fixes[\s\S]*?(?=\n\s{6}- name:)/)?.[0] ?? '';

  assert.match(createStep, /build-autofix-pr-metadata\.mjs/);
  assert.match(createStep, /GITHUB_EVENT_PATH/);
  assert.match(createStep, /--body-file/);
  assert.match(createStep, /--label["']?\s+["']?pending-review/);
  assert.doesNotMatch(createStep, /git log|github\.event\.head_commit|git show/);
});
