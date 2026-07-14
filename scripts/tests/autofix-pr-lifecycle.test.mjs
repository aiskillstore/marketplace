import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildSupersessionPlan,
  preflightReplacement,
  supersedeReplacement,
} from '../autofix-pr-lifecycle.mjs';

const submissionId = 'e950f6aa-4390-426c-b23e-17b2bc4c3670';
const sourceHeadSha = 'a'.repeat(40);
const replacementHeadSha = 'b'.repeat(40);
const sourceBody = `**Submission ID**: \`${submissionId}\``;
const replacementBody = `${sourceBody}\n\n**Source PR**: #2443\n**Source PR Head SHA**: \`${sourceHeadSha}\``;

function pull({ number, state = 'open', body, labels = [], headSha, headRef, mergedAt = null }) {
  return {
    number,
    state,
    body,
    labels: labels.map((name) => ({ name })),
    head: { sha: headSha, ref: headRef },
    merged_at: mergedAt,
    html_url: `https://github.com/aiskillstore/marketplace/pull/${number}`,
  };
}

function event() {
  return {
    pull_request: pull({
      number: 2443,
      body: sourceBody,
      labels: ['pending-review'],
      headSha: sourceHeadSha,
      headRef: 'submission/source',
    }),
  };
}

function source(overrides = {}) {
  return pull({
    number: 2443,
    body: sourceBody,
    labels: ['pending-review'],
    headSha: sourceHeadSha,
    headRef: 'submission/source',
    ...overrides,
  });
}

function replacement(overrides = {}) {
  return pull({
    number: 2468,
    body: replacementBody,
    labels: [],
    headSha: replacementHeadSha,
    headRef: `fix/skill-md-validation-pr-2443-${sourceHeadSha.slice(0, 12)}`,
    ...overrides,
  });
}

test('preflight rejects stale source head, body, or label before replacement creation', () => {
  const replacements = [];

  assert.throws(
    () => preflightReplacement({ event: event(), liveSource: source({ headSha: 'c'.repeat(40) }), replacements }),
    /source PR head changed/i,
  );
  assert.throws(
    () => preflightReplacement({ event: event(), liveSource: source({ body: `${sourceBody}\nchanged` }), replacements }),
    /source PR body changed/i,
  );
  assert.throws(
    () => preflightReplacement({ event: event(), liveSource: source({ labels: [] }), replacements }),
    /no longer has pending-review/i,
  );
});

test('preflight deduplicates one exact source PR and head SHA replacement', () => {
  const result = preflightReplacement({
    event: event(),
    liveSource: source(),
    replacements: [replacement()],
  });

  assert.equal(result.source.number, 2443);
  assert.equal(result.source.headSha, sourceHeadSha);
  assert.equal(result.existingReplacement.number, 2468);
  assert.equal(result.branchName, `fix/skill-md-validation-pr-2443-${sourceHeadSha.slice(0, 12)}`);

  assert.throws(
    () => preflightReplacement({
      event: event(),
      liveSource: source(),
      replacements: [replacement(), replacement({ number: 2469 })],
    }),
    /multiple replacement PRs/i,
  );
});

test('supersession plan revokes source approval before closing and labels replacement last', () => {
  const sourcePr = source();
  const replacementPr = replacement();

  assert.deepEqual(
    buildSupersessionPlan({
      source: sourcePr,
      replacement: replacementPr,
      openPulls: [sourcePr, replacementPr],
      submissionId,
    }),
    [
      { action: 'remove-label', number: 2443 },
      { action: 'close', number: 2443 },
      { action: 'add-label', number: 2468 },
    ],
  );
});

test('supersession plan is reentrant and repairs a previous dual-active state fail closed', () => {
  const sourcePr = source();
  const replacementPr = replacement({ labels: ['pending-review'] });

  assert.deepEqual(
    buildSupersessionPlan({
      source: sourcePr,
      replacement: replacementPr,
      openPulls: [sourcePr, replacementPr],
      submissionId,
    }),
    [
      { action: 'remove-label', number: 2468 },
      { action: 'remove-label', number: 2443 },
      { action: 'close', number: 2443 },
      { action: 'add-label', number: 2468 },
    ],
  );

  const closedSource = source({ state: 'closed', labels: [] });
  assert.deepEqual(
    buildSupersessionPlan({
      source: closedSource,
      replacement: replacementPr,
      openPulls: [replacementPr],
      submissionId,
    }),
    [],
  );
});

test('supersession rejects a competing OPEN pending-review PR for the same submission', () => {
  const sourcePr = source({ state: 'closed', labels: [] });
  const replacementPr = replacement();
  const competitor = pull({
    number: 2500,
    body: sourceBody,
    labels: ['pending-review'],
    headSha: 'd'.repeat(40),
    headRef: 'other-replacement',
  });

  assert.throws(
    () => buildSupersessionPlan({
      source: sourcePr,
      replacement: replacementPr,
      openPulls: [replacementPr, competitor],
      submissionId,
    }),
    /competing OPEN pending-review/i,
  );
});

class FakeClient {
  constructor(sourcePr, replacementPr) {
    this.pulls = new Map([[sourcePr.number, structuredClone(sourcePr)], [replacementPr.number, structuredClone(replacementPr)]]);
    this.operations = [];
  }

  async getPull(number) {
    return structuredClone(this.pulls.get(number));
  }

  async listPulls(state) {
    return [...this.pulls.values()]
      .filter((pr) => state === 'all' || pr.state === state)
      .map((pr) => structuredClone(pr));
  }

  async removeLabel(number) {
    this.operations.push(`remove:${number}`);
    const pr = this.pulls.get(number);
    pr.labels = pr.labels.filter((label) => label.name !== 'pending-review');
  }

  async closePull(number) {
    this.operations.push(`close:${number}`);
    this.pulls.get(number).state = 'closed';
  }

  async addLabel(number) {
    this.operations.push(`add:${number}`);
    const pr = this.pulls.get(number);
    if (!pr.labels.some((label) => label.name === 'pending-review')) pr.labels.push({ name: 'pending-review' });
  }
}

test('supersedeReplacement executes the fail-closed order and converges to exactly one active approval', async () => {
  const client = new FakeClient(source(), replacement());

  await supersedeReplacement({
    client,
    event: event(),
    replacementNumber: 2468,
    replacementHeadSha,
  });

  assert.deepEqual(client.operations, ['remove:2443', 'close:2443', 'add:2468']);
  assert.equal((await client.getPull(2443)).state, 'closed');
  assert.deepEqual((await client.getPull(2443)).labels, []);
  assert.deepEqual((await client.getPull(2468)).labels, [{ name: 'pending-review' }]);
});

test('stale source metadata revokes an already-labeled replacement before failing', async () => {
  const client = new FakeClient(
    source({ body: `${sourceBody}\nchanged` }),
    replacement({ labels: ['pending-review'] }),
  );

  await assert.rejects(
    supersedeReplacement({
      client,
      event: event(),
      replacementNumber: 2468,
      replacementHeadSha,
    }),
    /source PR body changed/i,
  );

  assert.deepEqual(client.operations, ['remove:2468']);
  assert.deepEqual((await client.getPull(2468)).labels, []);
});

test('a competing approval revokes the replacement before failing', async () => {
  const client = new FakeClient(
    source({ state: 'closed', labels: [] }),
    replacement({ labels: ['pending-review'] }),
  );
  const competitor = pull({
    number: 2500,
    body: sourceBody,
    labels: ['pending-review'],
    headSha: 'd'.repeat(40),
    headRef: 'other-replacement',
  });
  client.pulls.set(competitor.number, competitor);

  await assert.rejects(
    supersedeReplacement({
      client,
      event: event(),
      replacementNumber: 2468,
      replacementHeadSha,
    }),
    /competing OPEN pending-review/i,
  );

  assert.deepEqual(client.operations, ['remove:2468']);
  assert.deepEqual((await client.getPull(2468)).labels, []);
});
