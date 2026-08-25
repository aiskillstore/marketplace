import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { SourceCommunityClient } from '../scripts/source-community-client.mjs';

const source = {
  name: 'Example Engineering Board',
  baseUrl: 'https://jobs.example.org/openings/engineering?ref=candidate@example.com#openings',
  kind: 'job-board',
  regions: ['global', 'remote'],
  roleFamilies: ['engineering'],
  requiresSession: false,
};

const job = {
  url: 'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc?ref=candidate@example.com#apply',
  company: 'Example',
  role: 'Senior Product Engineer',
  applicationChannel: 'ashby',
  discoverySource: 'job-board',
};

function relay() {
  const requests = [];
  const community = [{
    sourceId: 'community-abcdef1234567890',
    name: 'Example Engineering Board',
    baseUrl: 'https://jobs.example.org/openings/engineering',
    kind: 'job-board',
    regions: ['global', 'remote'],
    roleFamilies: ['engineering'],
    requiresSession: false,
    registryStatus: 'community-reviewed',
    contributionCount: 2,
  }];
  const jobs = [{
    jobId: 'community-job-abcdef1234567890',
    url: 'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc',
    company: 'Example',
    role: 'Senior Product Engineer',
    applicationChannel: 'ashby',
    discoverySource: 'job-board',
    providerUrl: 'https://jobs.ashbyhq.com/example',
    firstSeenAt: '2026-08-24T00:00:00.000Z',
    lastSeenAt: '2026-08-24T00:00:00.000Z',
    contributionCount: 2,
  }];
  const fetch = async (url, options = {}) => {
    requests.push({ url, options, body: options.body ? JSON.parse(options.body) : null });
    if (url.endsWith('/v1/install')) return Response.json({ installationId: '11111111-1111-4111-8111-111111111111', token: 'source-token', expiresAt: '2099-01-01T00:00:00.000Z' }, { status: 201 });
    if (url.endsWith('/v1/sources') && options.method === 'POST') return Response.json({ accepted: true, sourceId: 'community-abcdef1234567890', publicationStatus: 'pending', uniqueContributors: 1 }, { status: 202 });
    if (url.endsWith('/v1/jobs') && options.method === 'POST') return Response.json({ accepted: true, jobId: 'community-job-abcdef1234567890', publicationStatus: 'pending', contributionCount: 2 }, { status: 202 });
    if (url.includes('/v1/jobs')) return Response.json({ version: 1, jobs, nextCursor: 'next-page' });
    return Response.json({ version: 1, sources: community });
  };
  return { fetch, requests };
}

test('source sharing is enabled by default, disclosed, sanitized, and sent immediately', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-default-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const network = relay();
  let notice = '';
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: (value) => { notice += value; } });

  const result = await client.contribute(source);

  assert.deepEqual(result, { shared: true, sourceId: 'community-abcdef1234567890', publicationStatus: 'pending', uniqueContributors: 1 });
  assert.match(notice, /community sharing is enabled by default/i);
  assert.equal(network.requests.length, 2);
  assert.equal(network.requests[1].url, 'https://relay.example.com/v1/sources');
  assert.equal(network.requests[1].body.source.baseUrl, 'https://jobs.example.org/openings/engineering');
  assert.equal(JSON.stringify(network.requests[1].body).includes('candidate@example.com'), false);
  const stored = JSON.parse(await readFile(join(directory, 'source-sharing.json'), 'utf8'));
  assert.equal(stored.enabled, true);
  assert.equal(stored.disclosed, true);
  assert.equal(stored.jobSharingDisclosed, true);
  if (process.platform !== 'win32') assert.equal((await stat(join(directory, 'source-sharing.json'))).mode & 0o777, 0o600);
});

test('existing source-sharing users receive one command to opt out before job backfill', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-upgrade-disclosure-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'source-sharing.json'), JSON.stringify({
    version: 1,
    enabled: true,
    disclosed: true,
    installationId: '11111111-1111-4111-8111-111111111111',
    token: 'source-token',
    tokenExpiresAt: '2099-01-01T00:00:00.000Z',
  }));
  const network = relay();
  let notice = '';
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: (value) => { notice += value; } });

  assert.deepEqual(await client.contributeJob(job), { shared: false, reason: 'grace' });
  assert.match(notice, /confirmed public job links/i);
  assert.equal(JSON.parse(await readFile(join(directory, 'source-sharing.json'), 'utf8')).jobSharingDisclosed, true);
  assert.equal(network.requests.length, 0);
  notice = '';
  assert.equal((await client.contributeJob(job)).shared, true);
  assert.equal(notice, '');
});

test('an interrupted job-sharing disclosure still preserves the grace command', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-job-grace-recovery-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'source-sharing.json'), JSON.stringify({
    version: 1,
    enabled: true,
    disclosed: true,
    jobSharingDisclosed: true,
    jobSharingGraceConsumed: false,
    installationId: null,
    token: null,
    tokenExpiresAt: null,
  }));
  const network = relay();
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: () => {} });

  assert.deepEqual(await client.contributeJob(job), { shared: false, reason: 'grace' });
  assert.equal(network.requests.length, 0);
  assert.equal((await client.contributeJob(job)).shared, true);
});

test('historical applications without a source config receive the disclosure grace command', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-historical-no-config-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'applications.ndjson'), '{"historical":true}\n');
  const network = relay();
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: () => {} });

  assert.deepEqual(await client.contributeJob(job), { shared: false, reason: 'grace' });
  assert.equal(network.requests.length, 0);
});

test('confirmed jobs are sanitized, shared anonymously, and public listings are validated', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-job-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const network = relay();
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: () => {} });

  const contributed = await client.contributeJob(job);
  assert.deepEqual(contributed, { shared: true, jobId: 'community-job-abcdef1234567890', publicationStatus: 'pending', contributionCount: 2 });
  const posted = network.requests.find((request) => request.url.endsWith('/v1/jobs') && request.options.method === 'POST');
  assert.equal(posted.body.job.url, 'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc');
  assert.equal(posted.body.job.providerUrl, 'https://jobs.ashbyhq.com/example');
  assert.equal(JSON.stringify(posted.body).includes('candidate@example.com'), false);

  const listed = await client.listJobs({ limit: 25, cursor: 'current-page' });
  assert.equal(listed.jobs[0].jobId, 'community-job-abcdef1234567890');
  assert.equal(listed.jobs[0].contributionCount, 2);
  assert.equal(listed.nextCursor, 'next-page');
  assert.equal(network.requests.at(-1).url, 'https://relay.example.com/v1/jobs?limit=25&cursor=current-page');
  const requestsBeforeInvalidInput = network.requests.length;
  await assert.rejects(() => client.listJobs({ limit: 0 }), /between 1 and 100/i);
  assert.equal(network.requests.length, requestsBeforeInvalidInput);
});

test('community source listing validates the public response before reuse', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-list-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const network = relay();
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: () => {} });
  const [listed] = await client.list();
  assert.equal(listed.sourceId, 'community-abcdef1234567890');
  assert.equal(listed.baseUrl, 'https://jobs.example.org/openings/engineering');
  assert.equal(listed.contributionCount, 2);
  assert.equal(listed.registryStatus, 'community-reviewed');
});

test('source sharing can be disabled independently and never blocks local collection', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-disabled-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const network = relay();
  let notice = '';
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: (value) => { notice += value; } });

  assert.equal((await client.configure('disable')).enabled, false);
  assert.deepEqual(await client.contribute(source), { shared: false, reason: 'disabled' });
  assert.deepEqual(await client.contributeJob(job), { shared: false, reason: 'disabled' });
  assert.equal(network.requests.length, 0);
  assert.equal((await client.configure('enable')).enabled, true);
  assert.match(notice, /confirmed public job links/i);
  assert.equal((await client.contribute(source)).shared, true);
});

test('source sharing rejects personal and one-off job URLs before network transmission', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-reject-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const network = relay();
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: network.fetch, stderr: () => {} });

  await assert.rejects(() => client.preview({ ...source, baseUrl: 'https://linkedin.com/in/some-person' }), /profile or personal/i);
  await assert.rejects(() => client.preview({ ...source, baseUrl: 'https://jobs.example.org/jobs/123456' }), /repeatable discovery surface/i);
  await assert.rejects(() => client.preview({ ...source, baseUrl: 'https://jobs.example.org/candidate@example.com/openings' }), /identity-like content/i);
  await assert.rejects(() => client.preview({ ...source, baseUrl: 'https://127.0.0.1/jobs' }), /public internet hostname/i);
  await assert.rejects(() => client.preview({ ...source, baseUrl: 'https://careers.internal.local/jobs' }), /public internet hostname/i);
  assert.equal(network.requests.length, 0);
});

test('network failures are best effort and return an unavailable result', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-offline-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: async () => { throw new Error('offline'); }, stderr: () => {} });
  assert.deepEqual(await client.contribute(source), { shared: false, reason: 'unavailable' });
});

test('a failed contribution does not suppress a healthy community registry read', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-independent-read-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const network = relay();
  const fetch = async (url, options = {}) => {
    if (url.endsWith('/v1/sources') && options.method === 'POST') return Response.json({ error: 'rate_limited' }, { status: 429 });
    return network.fetch(url, options);
  };
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch, stderr: () => {} });

  assert.deepEqual(await client.contribute(source), { shared: false, reason: 'unavailable' });
  const [listed] = await client.list();
  assert.equal(listed.sourceId, 'community-abcdef1234567890');
});

test('concurrent opt-out is preserved and rechecked before source transmission', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-opt-out-race-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'source-sharing.json'), JSON.stringify({
    version: 1,
    enabled: true,
    disclosed: true,
    installationId: null,
    token: null,
    tokenExpiresAt: null,
  }));
  let releaseInstall;
  let installStarted;
  const installGate = new Promise((resolve) => { releaseInstall = resolve; });
  const installObserved = new Promise((resolve) => { installStarted = resolve; });
  const sourcePosts = [];
  const fetch = async (url, options = {}) => {
    if (url.endsWith('/v1/install')) {
      installStarted();
      await installGate;
      return Response.json({ installationId: '11111111-1111-4111-8111-111111111111', token: 'source-token', expiresAt: '2099-01-01T00:00:00.000Z' }, { status: 201 });
    }
    sourcePosts.push({ url, options });
    return Response.json({ accepted: true, sourceId: 'community-abcdef1234567890', publicationStatus: 'pending', uniqueContributors: 1 }, { status: 202 });
  };
  const contributor = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch, stderr: () => {} });
  const settings = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch, stderr: () => {} });

  const contribution = contributor.contribute(source);
  await installObserved;
  assert.equal((await settings.configure('disable')).enabled, false);
  releaseInstall();

  assert.deepEqual(await contribution, { shared: false, reason: 'disabled' });
  assert.equal(sourcePosts.length, 0);
  assert.equal(JSON.parse(await readFile(join(directory, 'source-sharing.json'), 'utf8')).enabled, false);
});

test('concurrent reset is not undone by an in-flight credential refresh', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-reset-race-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'source-sharing.json'), JSON.stringify({
    version: 1,
    enabled: true,
    disclosed: true,
    installationId: null,
    token: null,
    tokenExpiresAt: null,
  }));
  let releaseInstall;
  let installStarted;
  const installGate = new Promise((resolve) => { releaseInstall = resolve; });
  const installObserved = new Promise((resolve) => { installStarted = resolve; });
  const fetch = async (url) => {
    if (!url.endsWith('/v1/install')) throw new Error('source contribution must remain disabled');
    installStarted();
    await installGate;
    return Response.json({ installationId: '11111111-1111-4111-8111-111111111111', token: 'source-token', expiresAt: '2099-01-01T00:00:00.000Z' }, { status: 201 });
  };
  const contributor = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch, stderr: () => {} });
  const settings = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch, stderr: () => {} });

  const contribution = contributor.contribute(source);
  await installObserved;
  assert.deepEqual(await settings.configure('reset'), {
    enabled: false,
    disclosed: true,
    jobSharingDisclosed: false,
    hasInstallationId: false,
    endpoint: 'https://relay.example.com',
    schemaVersion: 1,
  });
  releaseInstall();

  assert.deepEqual(await contribution, { shared: false, reason: 'disabled' });
  const stored = JSON.parse(await readFile(join(directory, 'source-sharing.json'), 'utf8'));
  assert.equal(stored.enabled, false);
  assert.equal(stored.installationId, null);
  assert.equal(stored.token, null);
  assert.equal(stored.tokenExpiresAt, null);
});

test('recovers a source-sharing lock whose owner process no longer exists', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-stale-lock-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, '.source-sharing.lock'), '99999999\n');
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: async () => { throw new Error('network must not be used'); }, stderr: () => {} });

  assert.equal((await client.configure('disable')).enabled, false);
  await assert.rejects(() => stat(join(directory, '.source-sharing.lock')), { code: 'ENOENT' });
});

test('invalid stored relay credentials are replaced once and persisted', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'source-community-credential-recovery-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const oldInstallationId = '11111111-1111-4111-8111-111111111111';
  const newInstallationId = '22222222-2222-4222-8222-222222222222';
  await writeFile(join(directory, 'source-sharing.json'), JSON.stringify({
    version: 1,
    enabled: true,
    disclosed: true,
    installationId: oldInstallationId,
    token: 'invalid-old-token',
    tokenExpiresAt: '2099-01-01T00:00:00.000Z',
  }));
  const requests = [];
  const fetch = async (url, options = {}) => {
    const body = options.body ? JSON.parse(options.body) : null;
    requests.push({ url, body });
    if (url.endsWith('/v1/sources') && body.installationId === oldInstallationId) return Response.json({ error: 'invalid_token' }, { status: 401 });
    if (url.endsWith('/v1/install') && body.installationId === oldInstallationId) return Response.json({ error: 'invalid_token' }, { status: 401 });
    if (url.endsWith('/v1/install')) return Response.json({ installationId: newInstallationId, token: 'new-token', expiresAt: '2099-01-01T00:00:00.000Z' }, { status: 201 });
    return Response.json({ accepted: true, sourceId: 'community-abcdef1234567890', publicationStatus: 'pending', uniqueContributors: 1 }, { status: 202 });
  };
  const client = new SourceCommunityClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch, stderr: () => {} });

  const result = await client.contribute(source);

  assert.equal(result.shared, true);
  assert.ok(requests.some((request) => request.url.endsWith('/v1/install') && request.body.installationId === oldInstallationId));
  assert.ok(requests.some((request) => request.url.endsWith('/v1/install') && Object.keys(request.body).length === 0));
  const stored = JSON.parse(await readFile(join(directory, 'source-sharing.json'), 'utf8'));
  assert.equal(stored.installationId, newInstallationId);
  assert.equal(stored.token, 'new-token');
});
