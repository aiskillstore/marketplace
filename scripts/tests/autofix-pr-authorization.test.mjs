import assert from 'node:assert/strict';
import test from 'node:test';

const submissionId = 'e950f6aa-4390-426c-b23e-17b2bc4c3670';
const sourceHeadSha = 'a'.repeat(40);
const replacementHeadSha = 'b'.repeat(40);
const leaseRef = `refs/tags/autofix-approval-leases/${submissionId}`;
const sourceBody = `**Submission ID**: \`${submissionId}\``;
const replacementBody = `${sourceBody}\n\n**Source PR**: #2443\n**Source PR Head SHA**: \`${sourceHeadSha}\`\n**Authorization Lease Ref**: \`${leaseRef}\``;

function pull({
  number,
  state = 'open',
  body,
  labels = [],
  headSha,
  mergedAt = null,
} = {}) {
  return {
    number,
    state,
    body,
    labels: labels.map((name) => ({ name })),
    head: { sha: headSha },
    merged_at: mergedAt,
  };
}

function fixture(overrides = {}) {
  const mergedPull = pull({
    number: 2468,
    state: 'closed',
    body: replacementBody,
    labels: ['pending-review'],
    headSha: replacementHeadSha,
    mergedAt: '2026-07-14T12:00:00Z',
  });
  const sourcePull = pull({
    number: 2443,
    state: 'closed',
    body: sourceBody,
    labels: [],
    headSha: sourceHeadSha,
  });
  const event = {
    pull_request: structuredClone(mergedPull),
  };
  event.pull_request.merged = true;

  return {
    event,
    mergedPull,
    sourcePull,
    openPulls: [],
    lease: {
      version: 1,
      submissionId,
      sourcePrNumber: 2443,
      sourceHeadSha,
      holderPrNumber: 2468,
      holderHeadSha: replacementHeadSha,
      holderKind: 'replacement',
      ref: leaseRef,
    },
    ...overrides,
  };
}

async function loadVerifier() {
  try {
    const contract = await import('../submission-authorization.mjs');
    return contract.verifyMergeAuthorization;
  } catch (error) {
    if (error?.code !== 'ERR_MODULE_NOT_FOUND') throw error;
    // This mirrors the old workflow's label-only `if:` gate so each negative
    // fixture demonstrates the actual fail-open behavior on the old head.
    return async ({ event }) => {
      const pullRequest = event?.pull_request;
      const approved = pullRequest?.merged === true
        && pullRequest.labels?.some((label) => label.name === 'pending-review');
      if (!approved) throw new Error('merge is not label-authorized');
      return { authorized: true };
    };
  }
}

test('consumer accepts the exact unique replacement lease holder', async () => {
  const verifyMergeAuthorization = await loadVerifier();
  const result = await verifyMergeAuthorization(fixture());
  assert.equal(result.authorized, true);
});

test('consumer rejects another OPEN pending-review PR for the same submission', async () => {
  const verifyMergeAuthorization = await loadVerifier();
  const competitor = pull({
    number: 2500,
    body: sourceBody,
    labels: ['pending-review'],
    headSha: 'd'.repeat(40),
  });

  await assert.rejects(
    verifyMergeAuthorization(fixture({ openPulls: [competitor] })),
    /unique|compet|multiple|authorization/i,
  );
});

test('consumer rejects a replacement with a missing authorization lease', async () => {
  const verifyMergeAuthorization = await loadVerifier();
  await assert.rejects(
    verifyMergeAuthorization(fixture({ lease: null })),
    /lease/i,
  );
});

test('consumer rejects a lease held by another PR or head SHA', async () => {
  const verifyMergeAuthorization = await loadVerifier();
  await assert.rejects(
    verifyMergeAuthorization(fixture({
      lease: {
        ...fixture().lease,
        holderPrNumber: 2500,
        holderHeadSha: 'd'.repeat(40),
      },
    })),
    /lease|holder|authorization/i,
  );
});

test('consumer fails closed when transfer compensation failed after the source head drifted', async () => {
  const verifyMergeAuthorization = await loadVerifier();
  const uncompensatedSource = pull({
    number: 2443,
    state: 'open',
    body: sourceBody,
    labels: [],
    headSha: 'c'.repeat(40),
  });

  await assert.rejects(
    verifyMergeAuthorization(fixture({ sourcePull: uncompensatedSource })),
    /source|sha|deauthorized|metadata/i,
  );
});

test('consumer rejects source SHA and replacement metadata mismatch', async () => {
  const verifyMergeAuthorization = await loadVerifier();
  const mismatchedSource = pull({
    number: 2443,
    state: 'closed',
    body: sourceBody,
    labels: [],
    headSha: 'c'.repeat(40),
  });
  await assert.rejects(
    verifyMergeAuthorization(fixture({ sourcePull: mismatchedSource })),
    /source|sha|metadata/i,
  );

  const mismatchedBody = replacementBody.replace(sourceHeadSha, 'c'.repeat(40));
  const mismatchedMerged = pull({
    number: 2468,
    state: 'closed',
    body: mismatchedBody,
    labels: ['pending-review'],
    headSha: replacementHeadSha,
    mergedAt: '2026-07-14T12:00:00Z',
  });
  const mismatchedEvent = { pull_request: { ...structuredClone(mismatchedMerged), merged: true } };
  await assert.rejects(
    verifyMergeAuthorization(fixture({ event: mismatchedEvent, mergedPull: mismatchedMerged })),
    /source|sha|metadata/i,
  );
});
