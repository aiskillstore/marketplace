#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';

import {
  authorizationLeaseRef,
  parseCanonicalSubmissionId,
  parseReplacementAuthorization,
} from './submission-metadata.mjs';

const SHA_RE = /^[0-9a-f]{40}$/;
const PENDING_REVIEW_LABEL = 'pending-review';

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

function stateOf(pull) {
  return typeof pull?.state === 'string' ? pull.state.toLowerCase() : '';
}

function hasLabel(pull, expected = PENDING_REVIEW_LABEL) {
  return Array.isArray(pull?.labels)
    && pull.labels.some((label) => (typeof label === 'string' ? label : label?.name) === expected);
}

function replacementMarkersPresent(body) {
  return ['**Source PR**:', '**Source PR Head SHA**:', '**Authorization Lease Ref**:']
    .some((marker) => typeof body === 'string' && body.includes(marker));
}

export function buildAuthorizationLease({
  version = 1,
  submissionId,
  sourcePrNumber,
  sourceHeadSha,
  holderPrNumber,
  holderHeadSha,
  holderKind,
}) {
  if (version !== 1) throw new Error('Unsupported authorization lease version');
  if (!['source', 'replacement'].includes(holderKind)) {
    throw new Error('Authorization lease holderKind must be source or replacement');
  }
  const canonicalSubmissionId = parseCanonicalSubmissionId(`**Submission ID**: \`${submissionId}\``);
  return {
    version: 1,
    submissionId: canonicalSubmissionId,
    sourcePrNumber: positiveInteger(sourcePrNumber, 'Authorization lease source PR number'),
    sourceHeadSha: canonicalSha(sourceHeadSha, 'Authorization lease source head SHA'),
    holderPrNumber: positiveInteger(holderPrNumber, 'Authorization lease holder PR number'),
    holderHeadSha: canonicalSha(holderHeadSha, 'Authorization lease holder head SHA'),
    holderKind,
    ref: authorizationLeaseRef(canonicalSubmissionId),
  };
}

export function parseAuthorizationLeaseTag(tagObject, expectedRef) {
  if (!tagObject || tagObject.object?.type !== 'commit') {
    throw new Error('Authorization lease tag must point to a commit');
  }
  let parsed;
  try {
    parsed = JSON.parse(tagObject.message);
  } catch {
    throw new Error('Authorization lease tag message must be canonical JSON');
  }
  const lease = buildAuthorizationLease(parsed);
  if (lease.ref !== expectedRef) throw new Error('Authorization lease ref does not match its submission');
  if (canonicalSha(tagObject.object.sha, 'Authorization lease tag target SHA') !== lease.holderHeadSha) {
    throw new Error('Authorization lease tag target does not match holder head SHA');
  }
  return lease;
}

export function authorizationLeaseTagMessage(lease) {
  const canonical = buildAuthorizationLease(lease);
  return JSON.stringify({
    version: canonical.version,
    submissionId: canonical.submissionId,
    sourcePrNumber: canonical.sourcePrNumber,
    sourceHeadSha: canonical.sourceHeadSha,
    holderPrNumber: canonical.holderPrNumber,
    holderHeadSha: canonical.holderHeadSha,
    holderKind: canonical.holderKind,
  });
}

export async function verifyMergeAuthorization({
  event,
  mergedPull,
  sourcePull = null,
  openPulls = [],
  lease = null,
}) {
  const eventPull = event?.pull_request;
  if (!eventPull || eventPull.merged !== true || !hasLabel(eventPull)) {
    throw new Error('Merged PR event is not pending-review authorized');
  }

  const mergedNumber = positiveInteger(mergedPull?.number, 'Merged PR number');
  if (mergedNumber !== positiveInteger(eventPull.number, 'Event PR number')) {
    throw new Error('Merged PR number does not match the event');
  }
  if (!mergedPull?.merged_at || stateOf(mergedPull) !== 'closed' || !hasLabel(mergedPull)) {
    throw new Error('Merged PR live state is not CLOSED + merged + pending-review');
  }
  if (mergedPull.body !== eventPull.body) throw new Error('Merged PR body changed after the merge event');
  const mergedHeadSha = canonicalSha(mergedPull?.head?.sha, 'Merged PR head SHA');
  if (mergedHeadSha !== canonicalSha(eventPull?.head?.sha, 'Event PR head SHA')) {
    throw new Error('Merged PR head SHA does not match the event');
  }

  const submissionId = parseCanonicalSubmissionId(mergedPull.body);
  const competitors = [];
  for (const candidate of Array.isArray(openPulls) ? openPulls : []) {
    if (stateOf(candidate) !== 'open' || !hasLabel(candidate)) continue;
    let candidateSubmissionId;
    try {
      candidateSubmissionId = parseCanonicalSubmissionId(candidate.body);
    } catch (error) {
      if (typeof candidate.body === 'string' && candidate.body.toLowerCase().includes(submissionId)) {
        throw new Error(`Malformed competing authorization metadata on PR #${candidate.number}`);
      }
      continue;
    }
    if (candidateSubmissionId === submissionId) competitors.push(candidate);
  }
  if (competitors.length > 0) {
    throw new Error(`Merged PR is not the unique authorization candidate; OPEN competitor(s): ${competitors.map((pull) => `#${pull.number}`).join(', ')}`);
  }

  let replacementAuthorization = null;
  if (replacementMarkersPresent(mergedPull.body)) {
    replacementAuthorization = parseReplacementAuthorization(mergedPull.body);
  }

  if (replacementAuthorization) {
    if (!lease) throw new Error('Replacement authorization lease is missing');
    const expectedLease = buildAuthorizationLease({
      submissionId,
      sourcePrNumber: replacementAuthorization.sourcePrNumber,
      sourceHeadSha: replacementAuthorization.sourceHeadSha,
      holderPrNumber: mergedNumber,
      holderHeadSha: mergedHeadSha,
      holderKind: 'replacement',
    });
    if (JSON.stringify(lease) !== JSON.stringify(expectedLease)) {
      throw new Error('Replacement authorization lease holder or metadata mismatch');
    }
    if (replacementAuthorization.leaseRef !== lease.ref) {
      throw new Error('Replacement Authorization Lease Ref mismatch');
    }
    if (!sourcePull || positiveInteger(sourcePull.number, 'Source PR number') !== replacementAuthorization.sourcePrNumber) {
      throw new Error('Replacement source PR metadata mismatch');
    }
    if (sourcePull.merged_at || stateOf(sourcePull) !== 'closed' || hasLabel(sourcePull)) {
      throw new Error('Replacement source PR must be CLOSED, unmerged, and deauthorized');
    }
    if (canonicalSha(sourcePull?.head?.sha, 'Live source PR head SHA') !== replacementAuthorization.sourceHeadSha) {
      throw new Error('Replacement source PR head SHA mismatch');
    }
    if (parseCanonicalSubmissionId(sourcePull.body) !== submissionId) {
      throw new Error('Replacement source PR Submission ID mismatch');
    }
  } else if (lease) {
    const expectedLease = buildAuthorizationLease({
      submissionId,
      sourcePrNumber: mergedNumber,
      sourceHeadSha: mergedHeadSha,
      holderPrNumber: mergedNumber,
      holderHeadSha: mergedHeadSha,
      holderKind: 'source',
    });
    if (JSON.stringify(lease) !== JSON.stringify(expectedLease)) {
      throw new Error('Source authorization lease holder mismatch');
    }
  }

  return {
    authorized: true,
    submissionId,
    mergedPrNumber: mergedNumber,
    mergedHeadSha,
    leaseRef: lease?.ref ?? null,
    authorizationKind: replacementAuthorization ? 'replacement' : 'source',
  };
}

function createGitHubReader({ repository, token, apiUrl = 'https://api.github.com', fetchImpl = globalThis.fetch }) {
  if (!/^[^/]+\/[^/]+$/.test(repository)) throw new Error('Repository must use owner/name format');
  if (!token) throw new Error('GH_TOKEN or GITHUB_TOKEN is required');

  async function request(path, { allowNotFound = false } = {}) {
    const response = await fetchImpl(`${apiUrl.replace(/\/$/, '')}/repos/${repository}${path}`, {
      headers: {
        Accept: 'application/vnd.github+json',
        Authorization: `Bearer ${token}`,
        'X-GitHub-Api-Version': '2022-11-28',
      },
    });
    if (allowNotFound && response.status === 404) return null;
    if (!response.ok) throw new Error(`GitHub API GET ${path} failed (${response.status}): ${(await response.text()).slice(0, 500)}`);
    return response.json();
  }

  async function listOpenPulls() {
    const pulls = [];
    for (let page = 1; page <= 100; page += 1) {
      const batch = await request(`/pulls?state=open&per_page=100&page=${page}`);
      pulls.push(...batch);
      if (batch.length < 100) return pulls;
    }
    throw new Error('GitHub PR pagination exceeded the finite 100-page budget');
  }

  async function getLease(ref) {
    const refPath = ref.replace(/^refs\//, '');
    const refObject = await request(`/git/ref/${refPath}`, { allowNotFound: true });
    if (!refObject) return null;
    const tagObject = await request(`/git/tags/${canonicalSha(refObject?.object?.sha, 'Authorization lease tag SHA')}`);
    return parseAuthorizationLeaseTag(tagObject, ref);
  }

  return {
    getPull: (number) => request(`/pulls/${positiveInteger(number, 'PR number')}`),
    listOpenPulls,
    getLease,
  };
}

async function main() {
  const { values } = parseArgs({
    options: {
      mode: { type: 'string' },
      'event-path': { type: 'string' },
      repository: { type: 'string' },
    },
    strict: true,
  });
  for (const name of ['mode', 'event-path', 'repository']) {
    if (!values[name]) throw new Error(`Missing required --${name}`);
  }
  if (values.mode !== 'verify-merge') throw new Error(`Unsupported --mode: ${values.mode}`);

  const event = JSON.parse(await readFile(values['event-path'], 'utf8'));
  const client = createGitHubReader({
    repository: values.repository,
    token: process.env.GH_TOKEN || process.env.GITHUB_TOKEN,
    apiUrl: process.env.GITHUB_API_URL || 'https://api.github.com',
  });
  const mergedNumber = positiveInteger(event?.pull_request?.number, 'Event PR number');
  const mergedPull = await client.getPull(mergedNumber);
  const submissionId = parseCanonicalSubmissionId(mergedPull.body);
  const ref = authorizationLeaseRef(submissionId);
  const [openPulls, lease] = await Promise.all([client.listOpenPulls(), client.getLease(ref)]);
  let sourcePull = null;
  if (replacementMarkersPresent(mergedPull.body)) {
    const replacement = parseReplacementAuthorization(mergedPull.body);
    sourcePull = await client.getPull(replacement.sourcePrNumber);
  }
  const result = await verifyMergeAuthorization({ event, mergedPull, sourcePull, openPulls, lease });
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : '';
if (invokedPath === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
