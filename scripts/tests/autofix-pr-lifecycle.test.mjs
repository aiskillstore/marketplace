import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildSupersessionPlan,
  ensureReplacement,
  preflightReplacement,
  supersedeReplacement,
} from '../autofix-pr-lifecycle.mjs';

const submissionId = 'e950f6aa-4390-426c-b23e-17b2bc4c3670';
const sourceHeadSha = 'a'.repeat(40);
const nextSourceHeadSha = 'c'.repeat(40);
const replacementHeadSha = 'b'.repeat(40);
const nextReplacementHeadSha = 'e'.repeat(40);
const leaseRef = `refs/tags/autofix-approval-leases/${submissionId}`;
const sourceBody = `**Submission ID**: \`${submissionId}\``;

function replacementBodyFor(headSha = sourceHeadSha) {
  return `${sourceBody}\n\n**Source PR**: #2443\n**Source PR Head SHA**: \`${headSha}\`\n**Authorization Lease Ref**: \`${leaseRef}\``;
}

const replacementBody = replacementBodyFor();

function pull({ number, state = 'open', title = '', body, labels = [], headSha, headRef, mergedAt = null }) {
  return {
    number,
    state,
    title,
    body,
    labels: labels.map((name) => ({ name })),
    head: { sha: headSha, ref: headRef },
    merged_at: mergedAt,
    html_url: `https://github.com/aiskillstore/marketplace/pull/${number}`,
  };
}

function event({ headSha = sourceHeadSha, body = sourceBody } = {}) {
  return {
    pull_request: pull({
      number: 2443,
      body,
      labels: ['pending-review'],
      headSha,
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

function nextReplacement(overrides = {}) {
  return pull({
    number: 2469,
    body: replacementBodyFor(nextSourceHeadSha),
    labels: [],
    headSha: nextReplacementHeadSha,
    headRef: `fix/skill-md-validation-pr-2443-${nextSourceHeadSha.slice(0, 12)}`,
    ...overrides,
  });
}

function activePendingReview(pulls) {
  return [...pulls.values()].filter((pr) => pr.state === 'open' && pr.labels.some((label) => label.name === 'pending-review'));
}

test('create response loss is deduped to the one exact unlabeled replacement', async () => {
  const sourcePr = source();
  const created = replacement({ title: 'fix: replacement' });
  const pulls = new Map([[sourcePr.number, structuredClone(sourcePr)]]);
  let createAttempts = 0;
  const client = {
    getPull: async (number) => structuredClone(pulls.get(number)),
    listPulls: async (_state, headRef) => [...pulls.values()]
      .filter((candidate) => candidate.head.ref === headRef)
      .map((candidate) => structuredClone(candidate)),
    createPull: async () => {
      createAttempts += 1;
      pulls.set(created.number, structuredClone(created));
      throw new Error('injected create response loss after apply');
    },
  };

  const result = await ensureReplacement({
    client,
    event: event(),
    title: created.title,
    body: created.body,
    headRef: created.head.ref,
    headSha: replacementHeadSha,
  });

  assert.equal(createAttempts, 1);
  assert.equal(result.number, created.number);
  assert.equal(result.headSha, replacementHeadSha);
  assert.deepEqual(pulls.get(created.number).labels, []);
});

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

test('preflight resumes one exact CLOSED unmerged replacement after source deauthorization', () => {
  const result = preflightReplacement({
    event: event(),
    liveSource: source({ state: 'closed', labels: [] }),
    replacements: [replacement({ state: 'closed' })],
  });

  assert.equal(result.existingReplacement.number, 2468);
  assert.equal(result.existingReplacement.state, 'closed');
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
  constructor(sourcePr, replacementPr, { hooks = {}, failures = [] } = {}) {
    this.pulls = new Map([[sourcePr.number, structuredClone(sourcePr)], [replacementPr.number, structuredClone(replacementPr)]]);
    this.operations = [];
    this.hooks = hooks;
    this.failures = failures.map((failure) => ({ remaining: 1, timing: 'after', ...failure }));
    this.lease = null;
    this.consumerAcceptedDualAuthorization = false;
  }

  #recordAuthorizationWindow() {
    const candidates = activePendingReview(this.pulls);
    const authorized = this.lease
      ? candidates.filter((pr) => pr.number === this.lease.holderPrNumber && pr.head.sha === this.lease.holderHeadSha)
      : candidates;
    if (authorized.length > 1) this.consumerAcceptedDualAuthorization = true;
  }

  async #mutate(action, number, apply) {
    const key = `${action}:${number}`;
    await this.hooks[`before:${key}`]?.(this);
    const failure = this.failures.find((entry) => entry.remaining > 0 && entry.action === action && (entry.number === undefined || entry.number === number));
    if (failure?.timing === 'before') {
      failure.remaining -= 1;
      throw new Error(`injected ${key} failure before apply`);
    }
    this.operations.push(key);
    apply();
    await this.hooks[`after:${key}`]?.(this);
    this.#recordAuthorizationWindow();
    if (failure) {
      failure.remaining -= 1;
      throw new Error(`injected ${key} failure after apply`);
    }
  }

  async getPull(number) {
    await this.hooks[`before:get:${number}`]?.(this);
    const result = structuredClone(this.pulls.get(number));
    await this.hooks[`after:get:${number}`]?.(this);
    return result;
  }

  async listPulls(state) {
    await this.hooks[`before:list:${state}`]?.(this);
    const result = [...this.pulls.values()]
      .filter((pr) => state === 'all' || pr.state === state)
      .map((pr) => structuredClone(pr));
    await this.hooks[`after:list:${state}`]?.(this);
    return result;
  }

  async removeLabel(number) {
    return this.#mutate('remove', number, () => {
      const pr = this.pulls.get(number);
      pr.labels = pr.labels.filter((label) => label.name !== 'pending-review');
    });
  }

  async closePull(number) {
    return this.#mutate('close', number, () => {
      this.pulls.get(number).state = 'closed';
    });
  }

  async reopenPull(number) {
    return this.#mutate('reopen', number, () => {
      const pr = this.pulls.get(number);
      if (pr.merged_at) throw new Error(`cannot reopen merged PR #${number}`);
      pr.state = 'open';
    });
  }

  async addLabel(number) {
    return this.#mutate('add', number, () => {
      const pr = this.pulls.get(number);
      if (!pr.labels.some((label) => label.name === 'pending-review')) pr.labels.push({ name: 'pending-review' });
    });
  }

  async getAuthorizationLease() {
    return structuredClone(this.lease);
  }

  async createAuthorizationLease(manifest) {
    if (this.lease) throw new Error('authorization lease already exists');
    this.operations.push(`lease-create:${manifest.holderPrNumber}`);
    this.lease = structuredClone(manifest);
    this.#recordAuthorizationWindow();
    return structuredClone(this.lease);
  }

  async updateAuthorizationLease(manifest) {
    if (!this.lease) throw new Error('authorization lease is missing');
    if (this.lease.sourcePrNumber !== manifest.sourcePrNumber) throw new Error('authorization lease source owner mismatch');
    this.operations.push(`lease-update:${manifest.holderPrNumber}`);
    this.lease = structuredClone(manifest);
    this.#recordAuthorizationWindow();
    return structuredClone(this.lease);
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

  assert.deepEqual(client.operations, ['lease-create:2468', 'remove:2443', 'close:2443', 'add:2468']);
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

  assert.deepEqual(client.operations, ['lease-create:2443', 'remove:2468']);
  assert.deepEqual((await client.getPull(2468)).labels, []);
  assert.equal(client.lease?.holderPrNumber, 2443);
});

test('a competing approval is revoked while the leased replacement remains uniquely authorized', async () => {
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

  await supersedeReplacement({
    client,
    event: event(),
    replacementNumber: 2468,
    replacementHeadSha,
  });

  assert.deepEqual((await client.getPull(competitor.number)).labels, []);
  assert.deepEqual((await client.getPull(2468)).labels, [{ name: 'pending-review' }]);
  assert.equal(client.lease?.holderPrNumber, 2468);
  assert.equal(client.consumerAcceptedDualAuthorization, false);
});

test('cross-head stale run compensates to one authorized source and the serialized new head can continue', async () => {
  let drifted = false;
  const client = new FakeClient(source(), replacement(), {
    hooks: {
      'after:remove:2443': (fake) => {
        if (drifted) return;
        drifted = true;
        fake.pulls.get(2443).head.sha = nextSourceHeadSha;
      },
    },
  });

  await assert.rejects(
    supersedeReplacement({
      client,
      event: event(),
      replacementNumber: 2468,
      replacementHeadSha,
    }),
    /source PR head changed/i,
  );

  assert.equal((await client.getPull(2443)).state, 'open');
  assert.deepEqual((await client.getPull(2443)).labels, [{ name: 'pending-review' }]);
  assert.deepEqual((await client.getPull(2468)).labels, []);
  assert.equal(activePendingReview(client.pulls).length, 1);

  const next = nextReplacement();
  client.pulls.set(next.number, next);
  await supersedeReplacement({
    client,
    event: event({ headSha: nextSourceHeadSha }),
    replacementNumber: next.number,
    replacementHeadSha: nextReplacementHeadSha,
  });

  assert.equal(activePendingReview(client.pulls).length, 1);
  assert.deepEqual((await client.getPull(next.number)).labels, [{ name: 'pending-review' }]);
});

test('body drift after source close reopens and reauthorizes the source before aborting', async () => {
  let drifted = false;
  const client = new FakeClient(source(), replacement(), {
    hooks: {
      'after:close:2443': (fake) => {
        if (drifted) return;
        drifted = true;
        fake.pulls.get(2443).body = `${sourceBody}\n\nEdited description`;
      },
    },
  });

  await assert.rejects(
    supersedeReplacement({
      client,
      event: event(),
      replacementNumber: 2468,
      replacementHeadSha,
    }),
    /source PR body changed/i,
  );

  assert.equal((await client.getPull(2443)).state, 'open');
  assert.deepEqual((await client.getPull(2443)).labels, [{ name: 'pending-review' }]);
  assert.deepEqual((await client.getPull(2468)).labels, []);
  assert.equal(client.lease?.holderPrNumber, 2443);
});

test('drift immediately after the first terminal snapshot is caught by stable confirmation and compensated', async () => {
  let terminalReads = 0;
  let drifted = false;
  const client = new FakeClient(source(), replacement(), {
    hooks: {
      'after:get:2443': (fake) => {
        const sourcePr = fake.pulls.get(2443);
        const replacementPr = fake.pulls.get(2468);
        if (drifted || sourcePr.state !== 'closed' || !replacementPr.labels.some((label) => label.name === 'pending-review')) return;
        terminalReads += 1;
        if (terminalReads === 3) {
          drifted = true;
          sourcePr.head.sha = nextSourceHeadSha;
        }
      },
    },
  });

  await assert.rejects(
    supersedeReplacement({
      client,
      event: event(),
      replacementNumber: 2468,
      replacementHeadSha,
    }),
    /source PR head changed/i,
  );

  assert.equal((await client.getPull(2443)).state, 'open');
  assert.deepEqual((await client.getPull(2443)).labels, [{ name: 'pending-review' }]);
  assert.deepEqual((await client.getPull(2468)).labels, []);
  assert.equal(client.lease?.holderPrNumber, 2443);
});

test('competitor injected immediately before grant never becomes consumer-authorized and is revoked', async () => {
  const competitor = pull({
    number: 2500,
    body: sourceBody,
    labels: ['pending-review'],
    headSha: 'd'.repeat(40),
    headRef: 'competing-submission',
  });
  const client = new FakeClient(source(), replacement(), {
    hooks: {
      'before:add:2468': (fake) => fake.pulls.set(competitor.number, structuredClone(competitor)),
    },
  });

  await supersedeReplacement({
    client,
    event: event(),
    replacementNumber: 2468,
    replacementHeadSha,
  });

  assert.equal(client.consumerAcceptedDualAuthorization, false);
  assert.deepEqual((await client.getPull(2500)).labels, []);
  assert.deepEqual(activePendingReview(client.pulls).map((pr) => pr.number), [2468]);
  assert.equal(client.lease?.holderPrNumber, 2468);
  assert.equal(client.lease?.holderHeadSha, replacementHeadSha);
});

test('rerun reopens an exact unmerged replacement closed after source deauthorization', async () => {
  let closedReplacement = false;
  const client = new FakeClient(source(), replacement(), {
    hooks: {
      'after:close:2443': (fake) => {
        if (closedReplacement) return;
        closedReplacement = true;
        fake.pulls.get(2468).state = 'closed';
      },
    },
  });

  await supersedeReplacement({
    client,
    event: event(),
    replacementNumber: 2468,
    replacementHeadSha,
  });

  assert.equal((await client.getPull(2443)).state, 'closed');
  assert.deepEqual((await client.getPull(2443)).labels, []);
  assert.equal((await client.getPull(2468)).state, 'open');
  assert.deepEqual((await client.getPull(2468)).labels, [{ name: 'pending-review' }]);
  assert.equal(activePendingReview(client.pulls).length, 1);
  assert.ok(client.operations.includes('reopen:2468'));
});

for (const failure of [
  { action: 'remove', number: 2443 },
  { action: 'close', number: 2443 },
  { action: 'add', number: 2468 },
]) {
  test(`response loss after ${failure.action} is reconciled to exactly one authorized candidate`, async () => {
    const client = new FakeClient(source(), replacement(), { failures: [failure] });

    await supersedeReplacement({
      client,
      event: event(),
      replacementNumber: 2468,
      replacementHeadSha,
    });

    assert.deepEqual(activePendingReview(client.pulls).map((pr) => pr.number), [2468]);
    assert.equal(client.consumerAcceptedDualAuthorization, false);
    assert.equal(client.lease?.holderPrNumber, 2468);
  });
}

test('response loss after replacement reopen is reconciled and still grants only the replacement', async () => {
  const client = new FakeClient(
    source({ state: 'closed', labels: [] }),
    replacement({ state: 'closed' }),
    { failures: [{ action: 'reopen', number: 2468 }] },
  );

  await supersedeReplacement({
    client,
    event: event(),
    replacementNumber: 2468,
    replacementHeadSha,
  });

  assert.deepEqual(activePendingReview(client.pulls).map((pr) => pr.number), [2468]);
  assert.equal(client.lease?.holderPrNumber, 2468);
});
