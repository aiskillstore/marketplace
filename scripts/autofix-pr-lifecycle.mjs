#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';

import {
  parseCanonicalSubmissionId,
  parseReplacementSource,
} from './submission-metadata.mjs';

const PENDING_REVIEW_LABEL = 'pending-review';
const SHA_RE = /^[0-9a-f]{40}$/;

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

function assertReplacementIdentity(source, replacement, expectedHeadSha = null) {
  if (stateOf(replacement) !== 'open') throw new Error(`Replacement PR #${replacement?.number} is not OPEN`);
  if (parseCanonicalSubmissionId(replacement?.body) !== source.submissionId) {
    throw new Error('Replacement PR Submission ID does not match the source event');
  }
  const replacementSource = parseReplacementSource(replacement.body);
  if (replacementSource.sourcePrNumber !== source.number || replacementSource.sourceHeadSha !== source.headSha) {
    throw new Error('Replacement PR metadata is not bound to the exact source PR and head SHA');
  }
  if (expectedHeadSha && canonicalSha(replacement?.head?.sha, 'Replacement PR head SHA') !== canonicalSha(expectedHeadSha, 'Expected replacement head SHA')) {
    throw new Error('Replacement PR head changed before approval transfer');
  }
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
        }
      : null,
  };
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
  if (stateOf(replacement) !== 'open') throw new Error(`Replacement PR #${replacement?.number} is not OPEN`);

  const allowedNumbers = new Set([Number(source.number), Number(replacement.number)]);
  const competitors = activeApprovals(openPulls)
    .filter((entry) => entry.submissionId === submissionId && !allowedNumbers.has(Number(entry.pull.number)));
  if (competitors.length > 0) {
    throw new Error(`Competing OPEN pending-review PR(s) exist for submission ${submissionId}: ${competitors.map((entry) => `#${entry.pull.number}`).join(', ')}`);
  }

  const plan = [];
  const replacementMustBeRevokedFirst = sourceState === 'open' && hasLabel(replacement);
  if (replacementMustBeRevokedFirst) {
    plan.push({ action: 'remove-label', number: positiveInteger(replacement.number, 'Replacement PR number') });
  }
  if (hasLabel(source)) {
    plan.push({ action: 'remove-label', number: positiveInteger(source.number, 'Source PR number') });
  }
  if (sourceState === 'open') {
    plan.push({ action: 'close', number: positiveInteger(source.number, 'Source PR number') });
  }
  if (!hasLabel(replacement) || replacementMustBeRevokedFirst) {
    plan.push({ action: 'add-label', number: positiveInteger(replacement.number, 'Replacement PR number') });
  }
  return plan;
}

export async function supersedeReplacement({ client, event, replacementNumber, replacementHeadSha }) {
  const source = sourceFromEvent(event);
  const replacementPrNumber = positiveInteger(replacementNumber, 'Replacement PR number');

  for (let iteration = 0; iteration < 10; iteration += 1) {
    const [liveSource, replacement, openPulls] = await Promise.all([
      client.getPull(source.number),
      client.getPull(replacementPrNumber),
      client.listPulls('open'),
    ]);
    try {
      assertLiveSource(source, liveSource);
      assertReplacementIdentity(source, replacement, replacementHeadSha);
    } catch (error) {
      // A stale event must never leave the replacement with approval capability.
      if (stateOf(replacement) === 'open' && hasLabel(replacement)) {
        await client.removeLabel(replacementPrNumber, PENDING_REVIEW_LABEL);
      }
      throw error;
    }

    let plan;
    try {
      plan = buildSupersessionPlan({
        source: liveSource,
        replacement,
        openPulls,
        submissionId: source.submissionId,
      });
    } catch (error) {
      if (stateOf(replacement) === 'open' && hasLabel(replacement)) {
        await client.removeLabel(replacementPrNumber, PENDING_REVIEW_LABEL);
      }
      throw error;
    }

    if (plan.length === 0) {
      if (stateOf(liveSource) !== 'closed' || hasLabel(liveSource) || stateOf(replacement) !== 'open' || !hasLabel(replacement)) {
        throw new Error('Supersession reached a non-canonical terminal state');
      }
      const approvals = activeApprovals(openPulls).filter((entry) => entry.submissionId === source.submissionId);
      if (approvals.length !== 1 || Number(approvals[0].pull.number) !== replacementPrNumber) {
        throw new Error('Supersession did not converge to exactly one OPEN pending-review replacement');
      }
      return {
        sourcePrNumber: source.number,
        sourceHeadSha: source.headSha,
        replacementPrNumber,
        submissionId: source.submissionId,
      };
    }

    const operation = plan[0];
    if (operation.action === 'remove-label') await client.removeLabel(operation.number, PENDING_REVIEW_LABEL);
    else if (operation.action === 'close') await client.closePull(operation.number);
    else if (operation.action === 'add-label') await client.addLabel(operation.number, PENDING_REVIEW_LABEL);
    else throw new Error(`Unsupported supersession operation: ${operation.action}`);
  }

  throw new Error('Supersession did not converge within the finite operation budget');
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

  return {
    getPull: (number) => request(`/pulls/${positiveInteger(number, 'PR number')}`),
    listPulls,
    removeLabel: (number, label) => request(`/issues/${positiveInteger(number, 'PR number')}/labels/${encodeURIComponent(label)}`, { method: 'DELETE', allowNotFound: true }),
    closePull: (number) => request(`/pulls/${positiveInteger(number, 'PR number')}`, { method: 'PATCH', body: { state: 'closed' } }),
    addLabel: (number, label) => request(`/issues/${positiveInteger(number, 'PR number')}/labels`, { method: 'POST', body: { labels: [label] } }),
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
