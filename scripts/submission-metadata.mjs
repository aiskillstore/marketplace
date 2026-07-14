#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';

const UUID_PATTERN = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}';
const SOURCE_SHA_PATTERN = '[0-9a-fA-F]{40}';
const UUID_RE = new RegExp('^' + UUID_PATTERN + '$');
const SUBMISSION_LINE_RE = new RegExp('^\\*\\*Submission ID\\*\\*: `(' + UUID_PATTERN + ')`\\r?$', 'gm');
const SOURCE_PR_LINE_RE = /^\*\*Source PR\*\*: #(\d+)\r?$/gm;
const SOURCE_SHA_LINE_RE = new RegExp('^\\*\\*Source PR Head SHA\\*\\*: `(' + SOURCE_SHA_PATTERN + ')`\\r?$', 'gm');
const LEASE_REF_LINE_RE = new RegExp('^\\*\\*Authorization Lease Ref\\*\\*: `(refs/tags/autofix-approval-leases/(' + UUID_PATTERN + '))`\\r?$', 'gm');

function uniqueMatch(body, regex, name) {
  if (typeof body !== 'string') throw new Error(`${name} body must be a string`);
  const matches = [...body.matchAll(regex)];
  if (matches.length !== 1) {
    throw new Error(`Expected exactly one anchored ${name}; found ${matches.length}`);
  }
  return matches[0];
}

export function parseCanonicalSubmissionId(body) {
  return uniqueMatch(body, SUBMISSION_LINE_RE, 'Submission ID')[1].toLowerCase();
}

export function authorizationLeaseRef(submissionId) {
  const canonical = typeof submissionId === 'string' ? submissionId.toLowerCase() : '';
  if (!UUID_RE.test(canonical)) throw new Error('Authorization lease submission ID must be a UUID');
  return `refs/tags/autofix-approval-leases/${canonical}`;
}

export function canonicalizeSubmissionBody(body) {
  const match = uniqueMatch(body, SUBMISSION_LINE_RE, 'Submission ID');
  const submissionId = match[1].toLowerCase();
  return {
    submissionId,
    body: `${body.slice(0, match.index)}**Submission ID**: \`${submissionId}\`${body.slice(match.index + match[0].length)}`,
  };
}

export function parseReplacementSource(body) {
  const sourcePrMatch = uniqueMatch(body, SOURCE_PR_LINE_RE, 'Source PR');
  const sourceShaMatch = uniqueMatch(body, SOURCE_SHA_LINE_RE, 'Source PR Head SHA');
  const sourcePrNumber = Number(sourcePrMatch[1]);
  if (!Number.isSafeInteger(sourcePrNumber) || sourcePrNumber <= 0) {
    throw new Error('Source PR must be a positive integer');
  }
  return {
    sourcePrNumber,
    sourceHeadSha: sourceShaMatch[1].toLowerCase(),
  };
}

export function parseReplacementAuthorization(body) {
  const submissionId = parseCanonicalSubmissionId(body);
  const source = parseReplacementSource(body);
  const leaseMatch = uniqueMatch(body, LEASE_REF_LINE_RE, 'Authorization Lease Ref');
  const leaseRef = leaseMatch[1];
  const leaseSubmissionId = leaseMatch[2].toLowerCase();
  if (leaseSubmissionId !== submissionId || leaseRef !== authorizationLeaseRef(submissionId)) {
    throw new Error('Authorization Lease Ref does not match the canonical Submission ID');
  }
  return { submissionId, ...source, leaseRef };
}

async function main() {
  const { values } = parseArgs({
    options: {
      'event-path': { type: 'string' },
    },
    strict: true,
  });
  if (!values['event-path']) throw new Error('Missing required --event-path');

  const event = JSON.parse(await readFile(values['event-path'], 'utf8'));
  const body = event?.pull_request?.body;
  const submissionId = parseCanonicalSubmissionId(body);
  process.stdout.write(`${JSON.stringify({ submissionId })}\n`);
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : '';
if (invokedPath === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
