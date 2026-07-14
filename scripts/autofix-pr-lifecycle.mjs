#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';

import {
  authorizationLeaseTagMessage,
  buildAuthorizationLease,
  parseAuthorizationLeaseTag,
} from './submission-authorization.mjs';
import {
  authorizationLeaseRef,
  parseCanonicalSubmissionId,
  parseReplacementAuthorization,
} from './submission-metadata.mjs';

const PENDING_REVIEW_LABEL = 'pending-review';
const SHA_RE = /^[0-9a-f]{40}$/;
const MAX_RECONCILE_ITERATIONS = 30;

function stateOf(pull) {
  return typeof pull?.state === 'string' ? pull.state.toLowerCase() : '';
}

function hasLabel(pull, expected = PENDING_REVIEW_LABEL) {
  return Array.isArray(pull?.labels)
    && pull.labels.some((label) => (typeof label === 'string' ? label : label?.name) === expected);
}

function positiveInteger(value, name) {
  const number = Number(value);
  if (!Number.isSafeInteger(number) || number <= 0) throw new Error(`${name} must be a positive integer`);
  return number;
}

function canonicalSha(value, name) {
  const sha = typeof value === 'string' ? value.toLowerCase() : '';
  if (!SHA_RE.test(sha)) throw new Error(`${name} must be a 40-character Git SHA`);
  return sha;
}

function leasesEqual(left, right) {
  return left !== null && right !== null
    && left.version === right.version
    && left.submissionId === right.submissionId
    && left.sourcePrNumber === right.sourcePrNumber
    && left.sourceHeadSha === right.sourceHeadSha
    && left.holderPrNumber === right.holderPrNumber
    && left.holderHeadSha === right.holderHeadSha
    && left.holderKind === right.holderKind
    && left.ref === right.ref;
}

export function sourceFromEvent(event) {
  const pull = event?.pull_request;
  if (!pull) throw new Error('pull_request event metadata is required');
  const number = positiveInteger(pull.number, 'Source PR number');
  const body = typeof pull.body === 'string' ? pull.body : '';
  const submissionId = parseCanonicalSubmissionId(body);
  const headSha = canonicalSha(pull?.head?.sha, 'Source PR head SHA');
  if (!hasLabel(pull)) throw new Error('Source event does not have pending-review');
  return { number, body, submissionId, headSha };
}

export function replacementBranchName(source) {
  return `fix/skill-md-validation-pr-${source.number}-${source.headSha.slice(0, 12)}`;
}

function assertLiveSource(source, liveSource) {
  if (positiveInteger(liveSource?.number, 'Live source PR number') !== source.number) {
    throw new Error('Live source PR number does not match the event');
  }
  if (canonicalSha(liveSource?.head?.sha, 'Live source PR head SHA') !== source.headSha) {
    throw new Error('Source PR head changed after the workflow event');
  }
  if (liveSource?.body !== source.body) {
    throw new Error('Source PR body changed after the workflow event');
  }
  if (parseCanonicalSubmissionId(liveSource.body) !== source.submissionId) {
    throw new Error('Source PR Submission ID changed after the workflow event');
  }
  if (liveSource?.merged_at) throw new Error('Source PR was already merged; replacement approval is forbidden');
  if (!['open', 'closed'].includes(stateOf(liveSource))) throw new Error(`Unsupported source PR state: ${liveSource?.state}`);
}

function assertReplacementIdentity(source, replacement, expectedHeadSha = null, { allowClosed = true } = {}) {
  const replacementState = stateOf(replacement);
  if (!['open', ...(allowClosed ? ['closed'] : [])].includes(replacementState) || replacement?.merged_at) {
    throw new Error(`Replacement PR #${replacement?.number} is not an OPEN or recoverable CLOSED PR`);
  }
  const authorization = parseReplacementAuthorization(replacement?.body);
  if (authorization.submissionId !== source.submissionId) {
    throw new Error('Replacement PR Submission ID does not match the source event');
  }
  if (authorization.sourcePrNumber !== source.number || authorization.sourceHeadSha !== source.headSha) {
    throw new Error('Replacement PR metadata is not bound to the exact source PR and head SHA');
  }
  if (authorization.leaseRef !== authorizationLeaseRef(source.submissionId)) {
    throw new Error('Replacement PR Authorization Lease Ref is invalid');
  }
  if (expectedHeadSha && canonicalSha(replacement?.head?.sha, 'Replacement PR head SHA') !== canonicalSha(expectedHeadSha, 'Expected replacement head SHA')) {
    throw new Error('Replacement PR head changed before approval transfer');
  }
  return authorization;
}

export function preflightReplacement({ event, liveSource, replacements }) {
  const source = sourceFromEvent(event);
  assertLiveSource(source, liveSource);
  const branchName = replacementBranchName(source);
  const matchingReplacements = (Array.isArray(replacements) ? replacements : [])
    .filter((pull) => pull?.head?.ref === branchName);

  if (matchingReplacements.length > 1) {
    throw new Error(`Found multiple replacement PRs for source PR #${source.number} at ${source.headSha}`);
  }

  const existingReplacement = matchingReplacements[0] ?? null;
  if (existingReplacement) {
    assertReplacementIdentity(source, existingReplacement);
  } else if (stateOf(liveSource) !== 'open' || !hasLabel(liveSource)) {
    throw new Error('Source PR is not OPEN or no longer has pending-review before replacement creation');
  }

  return {
    source,
    branchName,
    existingReplacement: existingReplacement
      ? {
          number: positiveInteger(existingReplacement.number, 'Replacement PR number'),
          url: existingReplacement.html_url,
          headSha: canonicalSha(existingReplacement?.head?.sha, 'Replacement PR head SHA'),
          state: stateOf(existingReplacement),
        }
      : null,
  };
}

function matchingPendingApprovals(pulls, submissionId) {
  const matches = [];
  for (const pull of Array.isArray(pulls) ? pulls : []) {
    if (stateOf(pull) !== 'open' || !hasLabel(pull)) continue;
    let candidateSubmissionId;
    try {
      candidateSubmissionId = parseCanonicalSubmissionId(pull?.body);
    } catch (error) {
      if (typeof pull?.body === 'string' && pull.body.toLowerCase().includes(submissionId)) {
        throw new Error(`Malformed pending-review competitor metadata on PR #${pull.number}`);
      }
      continue;
    }
    if (candidateSubmissionId === submissionId) matches.push(pull);
  }
  return matches;
}

function activeApprovals(openPulls) {
  return (Array.isArray(openPulls) ? openPulls : [])
    .filter((pull) => stateOf(pull) === 'open' && hasLabel(pull))
    .map((pull) => ({ pull, submissionId: parseCanonicalSubmissionId(pull?.body) }));
}

export function buildSupersessionPlan({ source, replacement, openPulls, submissionId }) {
  const sourceState = stateOf(source);
  if (!['open', 'closed'].includes(sourceState) || source?.merged_at) {
    throw new Error(`Source PR #${source?.number} cannot be superseded from state ${source?.state}`);
  }
  if (!['open', 'closed'].includes(stateOf(replacement)) || replacement?.merged_at) {
    throw new Error(`Replacement PR #${replacement?.number} is not recoverable`);
  }

  const allowedNumbers = new Set([Number(source.number), Number(replacement.number)]);
  const competitors = activeApprovals(openPulls)
    .filter((entry) => entry.submissionId === submissionId && !allowedNumbers.has(Number(entry.pull.number)));
  if (competitors.length > 0) {
    throw new Error(`Competing OPEN pending-review PR(s) exist for submission ${submissionId}: ${competitors.map((entry) => `#${entry.pull.number}`).join(', ')}`);
  }

  const plan = [];
  if (stateOf(replacement) === 'closed') plan.push({ action: 'reopen', number: positiveInteger(replacement.number, 'Replacement PR number') });
  const replacementMustBeRevokedFirst = sourceState === 'open' && hasLabel(replacement);
  if (replacementMustBeRevokedFirst) {
    plan.push({ action: 'remove-label', number: positiveInteger(replacement.number, 'Replacement PR number') });
  }
  if (hasLabel(source)) plan.push({ action: 'remove-label', number: positiveInteger(source.number, 'Source PR number') });
  if (sourceState === 'open') plan.push({ action: 'close', number: positiveInteger(source.number, 'Source PR number') });
  if (!hasLabel(replacement) || replacementMustBeRevokedFirst) {
    plan.push({ action: 'add-label', number: positiveInteger(replacement.number, 'Replacement PR number') });
  }
  return plan;
}

function replacementLease(source, replacementNumber, replacementHeadSha) {
  return buildAuthorizationLease({
    submissionId: source.submissionId,
    sourcePrNumber: source.number,
    sourceHeadSha: source.headSha,
    holderPrNumber: replacementNumber,
    holderHeadSha: replacementHeadSha,
    holderKind: 'replacement',
  });
}

function sourceLease(sourcePull, submissionId) {
  const headSha = canonicalSha(sourcePull?.head?.sha, 'Compensation source PR head SHA');
  return buildAuthorizationLease({
    submissionId,
    sourcePrNumber: positiveInteger(sourcePull.number, 'Compensation source PR number'),
    sourceHeadSha: headSha,
    holderPrNumber: positiveInteger(sourcePull.number, 'Compensation source PR number'),
    holderHeadSha: headSha,
    holderKind: 'source',
  });
}

async function ensureLease(client, desired, sourcePrNumber) {
  let current = await client.getAuthorizationLease(desired.submissionId);
  if (leasesEqual(current, desired)) return current;
  if (current && current.sourcePrNumber !== sourcePrNumber) {
    throw new Error(`Authorization lease belongs to competing source PR #${current.sourcePrNumber}`);
  }

  try {
    if (current) await client.updateAuthorizationLease(desired);
    else await client.createAuthorizationLease(desired);
  } catch (error) {
    current = await client.getAuthorizationLease(desired.submissionId);
    if (!leasesEqual(current, desired)) throw error;
    return current;
  }

  current = await client.getAuthorizationLease(desired.submissionId);
  if (!leasesEqual(current, desired)) throw new Error('Authorization lease mutation did not converge to the expected holder');
  return current;
}

async function restoreSourceAuthorization({ client, source, replacementNumber }) {
  const liveSource = await client.getPull(source.number);
  if (liveSource?.merged_at) throw new Error('Cannot compensate a merged source PR');
  const liveSubmissionId = parseCanonicalSubmissionId(liveSource?.body);
  if (liveSubmissionId !== source.submissionId) throw new Error('Cannot compensate after source Submission ID changed');
  if (!['open', 'closed'].includes(stateOf(liveSource))) throw new Error('Cannot compensate unsupported source PR state');

  const desired = sourceLease(liveSource, source.submissionId);
  await ensureLease(client, desired, source.number);

  if (stateOf(liveSource) === 'closed') {
    try {
      await client.reopenPull(source.number);
    } catch (error) {
      const refreshed = await client.getPull(source.number);
      if (stateOf(refreshed) !== 'open') throw error;
    }
  }

  const openPulls = await client.listPulls('open');
  for (const candidate of matchingPendingApprovals(openPulls, source.submissionId)) {
    if (Number(candidate.number) === source.number) continue;
    try {
      await client.removeLabel(candidate.number, PENDING_REVIEW_LABEL);
    } catch (error) {
      const refreshed = await client.getPull(candidate.number);
      if (hasLabel(refreshed)) throw error;
    }
  }

  const refreshedSource = await client.getPull(source.number);
  if (!hasLabel(refreshedSource)) {
    try {
      await client.addLabel(source.number, PENDING_REVIEW_LABEL);
    } catch (error) {
      if (!hasLabel(await client.getPull(source.number))) throw error;
    }
  }

  if (replacementNumber) {
    const replacement = await client.getPull(replacementNumber);
    if (stateOf(replacement) === 'open' && hasLabel(replacement)) {
      await client.removeLabel(replacementNumber, PENDING_REVIEW_LABEL);
    }
  }

  const [terminalSource, terminalPulls, terminalLease] = await Promise.all([
    client.getPull(source.number),
    client.listPulls('open'),
    client.getAuthorizationLease(source.submissionId),
  ]);
  const approvals = matchingPendingApprovals(terminalPulls, source.submissionId);
  if (stateOf(terminalSource) !== 'open' || !hasLabel(terminalSource)
      || approvals.length !== 1 || Number(approvals[0].number) !== source.number
      || !leasesEqual(terminalLease, desired)) {
    throw new Error('Source approval compensation did not converge to exactly one authorized source');
  }
  return desired;
}

async function attemptMutation(operation) {
  try {
    await operation();
    return null;
  } catch (error) {
    return error;
  }
}

export async function supersedeReplacement({ client, event, replacementNumber, replacementHeadSha }) {
  const source = sourceFromEvent(event);
  const replacementPrNumber = positiveInteger(replacementNumber, 'Replacement PR number');
  const expectedReplacementHeadSha = canonicalSha(replacementHeadSha, 'Expected replacement head SHA');
  const desiredLease = replacementLease(source, replacementPrNumber, expectedReplacementHeadSha);
  let lastMutationError = null;
  let terminalConfirmations = 0;

  for (let iteration = 0; iteration < MAX_RECONCILE_ITERATIONS; iteration += 1) {
    const [liveSource, replacement] = await Promise.all([
      client.getPull(source.number),
      client.getPull(replacementPrNumber),
    ]);

    try {
      assertLiveSource(source, liveSource);
      assertReplacementIdentity(source, replacement, expectedReplacementHeadSha);
    } catch (error) {
      try {
        await restoreSourceAuthorization({ client, source, replacementNumber: replacementPrNumber });
      } catch (compensationError) {
        throw new AggregateError([error, compensationError], `Approval transfer failed and compensation failed: ${error.message}`);
      }
      throw error;
    }

    if (stateOf(replacement) === 'closed') {
      terminalConfirmations = 0;
      lastMutationError = await attemptMutation(() => client.reopenPull(replacementPrNumber));
      continue;
    }

    try {
      await ensureLease(client, desiredLease, source.number);
    } catch (error) {
      try {
        await restoreSourceAuthorization({ client, source, replacementNumber: replacementPrNumber });
      } catch (compensationError) {
        throw new AggregateError([error, compensationError], `Authorization lease failed and compensation failed: ${error.message}`);
      }
      throw error;
    }

    const [checkedSource, checkedReplacement, openPulls] = await Promise.all([
      client.getPull(source.number),
      client.getPull(replacementPrNumber),
      client.listPulls('open'),
    ]);
    try {
      assertLiveSource(source, checkedSource);
      assertReplacementIdentity(source, checkedReplacement, expectedReplacementHeadSha, { allowClosed: false });
    } catch (error) {
      try {
        await restoreSourceAuthorization({ client, source, replacementNumber: replacementPrNumber });
      } catch (compensationError) {
        throw new AggregateError([error, compensationError], `Approval transfer became stale and compensation failed: ${error.message}`);
      }
      throw error;
    }

    const approvals = matchingPendingApprovals(openPulls, source.submissionId);
    const unauthorized = approvals.filter((pull) => Number(pull.number) !== replacementPrNumber);
    if (unauthorized.length > 0) {
      terminalConfirmations = 0;
      lastMutationError = await attemptMutation(() => client.removeLabel(unauthorized[0].number, PENDING_REVIEW_LABEL));
      continue;
    }

    if (stateOf(checkedSource) === 'open') {
      terminalConfirmations = 0;
      lastMutationError = await attemptMutation(() => client.closePull(source.number));
      continue;
    }

    if (!hasLabel(checkedReplacement)) {
      const [grantSource, grantReplacement, grantPulls, grantLease] = await Promise.all([
        client.getPull(source.number),
        client.getPull(replacementPrNumber),
        client.listPulls('open'),
        client.getAuthorizationLease(source.submissionId),
      ]);
      try {
        assertLiveSource(source, grantSource);
        assertReplacementIdentity(source, grantReplacement, expectedReplacementHeadSha, { allowClosed: false });
      } catch (error) {
        try {
          await restoreSourceAuthorization({ client, source, replacementNumber: replacementPrNumber });
        } catch (compensationError) {
          throw new AggregateError([error, compensationError], `Final grant became stale and compensation failed: ${error.message}`);
        }
        throw error;
      }
      if (stateOf(grantSource) !== 'closed' || hasLabel(grantSource) || !leasesEqual(grantLease, desiredLease)) {
        continue;
      }
      const grantCompetitors = matchingPendingApprovals(grantPulls, source.submissionId)
        .filter((pull) => Number(pull.number) !== replacementPrNumber);
      if (grantCompetitors.length > 0) {
        terminalConfirmations = 0;
        lastMutationError = await attemptMutation(() => client.removeLabel(grantCompetitors[0].number, PENDING_REVIEW_LABEL));
        continue;
      }
      terminalConfirmations = 0;
      lastMutationError = await attemptMutation(() => client.addLabel(replacementPrNumber, PENDING_REVIEW_LABEL));
      continue;
    }

    const [terminalSource, terminalReplacement, terminalPulls, terminalLease] = await Promise.all([
      client.getPull(source.number),
      client.getPull(replacementPrNumber),
      client.listPulls('open'),
      client.getAuthorizationLease(source.submissionId),
    ]);
    let terminalApprovals;
    try {
      assertLiveSource(source, terminalSource);
      assertReplacementIdentity(source, terminalReplacement, expectedReplacementHeadSha, { allowClosed: false });
      terminalApprovals = matchingPendingApprovals(terminalPulls, source.submissionId);
    } catch (error) {
      try {
        await restoreSourceAuthorization({ client, source, replacementNumber: replacementPrNumber });
      } catch (compensationError) {
        throw new AggregateError([error, compensationError], `Terminal verification failed and compensation failed: ${error.message}`);
      }
      throw error;
    }
    if (stateOf(terminalSource) === 'closed' && !hasLabel(terminalSource)
        && terminalApprovals.length === 1
        && Number(terminalApprovals[0].number) === replacementPrNumber
        && leasesEqual(terminalLease, desiredLease)) {
      terminalConfirmations += 1;
      if (terminalConfirmations < 2) continue;
      return {
        sourcePrNumber: source.number,
        sourceHeadSha: source.headSha,
        replacementPrNumber,
        replacementHeadSha: expectedReplacementHeadSha,
        submissionId: source.submissionId,
        leaseRef: desiredLease.ref,
      };
    }
    terminalConfirmations = 0;
  }

  const convergenceError = new Error(`Supersession did not converge within the finite operation budget${lastMutationError ? `: ${lastMutationError.message}` : ''}`);
  try {
    await restoreSourceAuthorization({ client, source, replacementNumber: replacementPrNumber });
  } catch (compensationError) {
    throw new AggregateError([convergenceError, compensationError], 'Supersession exhausted retries and compensation failed');
  }
  throw convergenceError;
}

export async function ensureReplacement({
  client,
  event,
  title,
  body,
  headRef,
  headSha,
  baseRef = 'main',
}) {
  const source = sourceFromEvent(event);
  const expectedBranch = replacementBranchName(source);
  if (headRef !== expectedBranch) throw new Error('Replacement head ref does not match the source lifecycle');
  const expectedHeadSha = canonicalSha(headSha, 'Replacement head SHA');
  const liveSource = await client.getPull(source.number);
  assertLiveSource(source, liveSource);
  let replacements = await client.listPulls('all', headRef);
  if (replacements.length > 1) throw new Error('Multiple replacement PRs exist for one source lifecycle');
  let replacement = replacements[0] ?? null;

  if (!replacement) {
    if (stateOf(liveSource) !== 'open' || !hasLabel(liveSource)) {
      throw new Error('Source PR is not authorized before replacement creation');
    }
    try {
      replacement = await client.createPull({ title, body, head: headRef, base: baseRef });
    } catch (error) {
      replacements = await client.listPulls('all', headRef);
      if (replacements.length !== 1) throw error;
      replacement = replacements[0];
    }
  } else if (replacement.body !== body || replacement.title !== title) {
    try {
      replacement = await client.updatePull(replacement.number, { title, body });
    } catch (error) {
      replacement = await client.getPull(replacement.number);
      if (replacement.body !== body || replacement.title !== title) throw error;
    }
  }

  assertReplacementIdentity(source, replacement, expectedHeadSha);
  if (hasLabel(replacement)) throw new Error('Replacement creation must not grant pending-review');
  return {
    number: positiveInteger(replacement.number, 'Replacement PR number'),
    url: replacement.html_url,
    headSha: expectedHeadSha,
    state: stateOf(replacement),
  };
}

export function createGitHubClient({ repository, token, apiUrl = 'https://api.github.com', fetchImpl = globalThis.fetch }) {
  if (!/^[^/]+\/[^/]+$/.test(repository)) throw new Error('Repository must use owner/name format');
  if (!token) throw new Error('GH_TOKEN or GITHUB_TOKEN is required');
  if (typeof fetchImpl !== 'function') throw new Error('fetch is unavailable');
  const [owner] = repository.split('/');

  async function request(path, { method = 'GET', body = null, allowNotFound = false } = {}) {
    const response = await fetchImpl(`${apiUrl.replace(/\/$/, '')}/repos/${repository}${path}`, {
      method,
      headers: {
        Accept: 'application/vnd.github+json',
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
      body: body === null ? undefined : JSON.stringify(body),
    });
    if (allowNotFound && response.status === 404) return null;
    if (!response.ok) {
      const message = await response.text();
      throw new Error(`GitHub API ${method} ${path} failed (${response.status}): ${message.slice(0, 500)}`);
    }
    if (response.status === 204) return null;
    return response.json();
  }

  async function listPulls(state, headRef = null) {
    const pulls = [];
    for (let page = 1; ; page += 1) {
      const query = new URLSearchParams({ state, per_page: '100', page: String(page) });
      if (headRef) query.set('head', `${owner}:${headRef}`);
      const batch = await request(`/pulls?${query}`);
      pulls.push(...batch);
      if (batch.length < 100) return pulls;
      if (page >= 100) throw new Error('GitHub PR pagination exceeded the finite 100-page budget');
    }
  }

  async function getAuthorizationLease(submissionId) {
    const ref = authorizationLeaseRef(submissionId);
    const refPath = ref.replace(/^refs\//, '');
    const refObject = await request(`/git/ref/${refPath}`, { allowNotFound: true });
    if (!refObject) return null;
    const tagSha = canonicalSha(refObject?.object?.sha, 'Authorization lease tag SHA');
    const tag = await request(`/git/tags/${tagSha}`);
    return parseAuthorizationLeaseTag(tag, ref);
  }

  async function createLeaseTag(lease) {
    const tag = await request('/git/tags', {
      method: 'POST',
      body: {
        tag: `autofix-approval-lease-${lease.submissionId}`,
        message: authorizationLeaseTagMessage(lease),
        object: lease.holderHeadSha,
        type: 'commit',
        tagger: {
          name: 'ai-skill-store[bot]',
          email: '2628292+ai-skill-store[bot]@users.noreply.github.com',
          date: new Date().toISOString(),
        },
      },
    });
    return canonicalSha(tag?.sha, 'Created authorization lease tag SHA');
  }

  async function createAuthorizationLease(lease) {
    const tagSha = await createLeaseTag(lease);
    await request('/git/refs', { method: 'POST', body: { ref: lease.ref, sha: tagSha } });
    return getAuthorizationLease(lease.submissionId);
  }

  async function updateAuthorizationLease(lease) {
    const tagSha = await createLeaseTag(lease);
    const refPath = lease.ref.replace(/^refs\//, '');
    await request(`/git/refs/${refPath}`, { method: 'PATCH', body: { sha: tagSha, force: true } });
    return getAuthorizationLease(lease.submissionId);
  }

  return {
    getPull: (number) => request(`/pulls/${positiveInteger(number, 'PR number')}`),
    listPulls,
    removeLabel: (number, label) => request(`/issues/${positiveInteger(number, 'PR number')}/labels/${encodeURIComponent(label)}`, { method: 'DELETE', allowNotFound: true }),
    closePull: (number) => request(`/pulls/${positiveInteger(number, 'PR number')}`, { method: 'PATCH', body: { state: 'closed' } }),
    reopenPull: (number) => request(`/pulls/${positiveInteger(number, 'PR number')}`, { method: 'PATCH', body: { state: 'open' } }),
    addLabel: (number, label) => request(`/issues/${positiveInteger(number, 'PR number')}/labels`, { method: 'POST', body: { labels: [label] } }),
    createPull: ({ title, body, head, base }) => request('/pulls', { method: 'POST', body: { title, body, head, base } }),
    updatePull: (number, fields) => request(`/pulls/${positiveInteger(number, 'PR number')}`, { method: 'PATCH', body: fields }),
    getAuthorizationLease,
    createAuthorizationLease,
    updateAuthorizationLease,
  };
}

async function main() {
  const { values } = parseArgs({
    options: {
      mode: { type: 'string' },
      'event-path': { type: 'string' },
      repository: { type: 'string' },
      'replacement-pr': { type: 'string' },
      'replacement-head-sha': { type: 'string' },
      title: { type: 'string' },
      'body-file': { type: 'string' },
      'head-ref': { type: 'string' },
      'base-ref': { type: 'string' },
    },
    strict: true,
  });
  for (const name of ['mode', 'event-path', 'repository']) {
    if (!values[name]) throw new Error(`Missing required --${name}`);
  }

  const event = JSON.parse(await readFile(values['event-path'], 'utf8'));
  const client = createGitHubClient({
    repository: values.repository,
    token: process.env.GH_TOKEN || process.env.GITHUB_TOKEN,
    apiUrl: process.env.GITHUB_API_URL || 'https://api.github.com',
  });

  if (values.mode === 'preflight') {
    const source = sourceFromEvent(event);
    const branchName = replacementBranchName(source);
    const [liveSource, replacements] = await Promise.all([
      client.getPull(source.number),
      client.listPulls('all', branchName),
    ]);
    process.stdout.write(`${JSON.stringify(preflightReplacement({ event, liveSource, replacements }))}\n`);
    return;
  }

  if (values.mode === 'ensure-replacement') {
    for (const name of ['replacement-head-sha', 'title', 'body-file', 'head-ref']) {
      if (!values[name]) throw new Error(`ensure-replacement mode requires --${name}`);
    }
    const body = await readFile(values['body-file'], 'utf8');
    const result = await ensureReplacement({
      client,
      event,
      title: values.title,
      body,
      headRef: values['head-ref'],
      headSha: values['replacement-head-sha'],
      baseRef: values['base-ref'] || 'main',
    });
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return;
  }

  if (values.mode === 'supersede') {
    if (!values['replacement-pr'] || !values['replacement-head-sha']) {
      throw new Error('supersede mode requires --replacement-pr and --replacement-head-sha');
    }
    const result = await supersedeReplacement({
      client,
      event,
      replacementNumber: values['replacement-pr'],
      replacementHeadSha: values['replacement-head-sha'],
    });
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return;
  }

  throw new Error(`Unsupported --mode: ${values.mode}`);
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : '';
if (invokedPath === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
