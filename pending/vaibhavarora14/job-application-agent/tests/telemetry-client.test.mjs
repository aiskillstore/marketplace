import assert from 'node:assert/strict';
import { mkdtemp, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { prepareTelemetryInput, TelemetryClient } from '../scripts/telemetry-client.mjs';

function fakeRelay() {
  const requests = [];
  const fetch = async (url, options = {}) => {
    requests.push({ url, options, body: options.body ? JSON.parse(options.body) : null });
    if (url.endsWith('/v1/install')) return Response.json({ installationId: '11111111-1111-4111-8111-111111111111', token: 'relay-token', expiresAt: '2099-01-01T00:00:00.000Z' });
    return Response.json({ accepted: true, eventId: '22222222-2222-4222-8222-222222222222' }, { status: 202 });
  };
  return { requests, fetch };
}

test('new installations disclose and send the first event immediately', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-new-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const relay = fakeRelay();
  let notice = '';
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: relay.fetch, stderr: (value) => { notice += value; } });
  const session = await client.beginCommand('search');
  assert.equal(session.installationEventPending, true);
  await client.record({ event: 'installation_started', properties: { osFamily: 'macos', nodeMajor: 24, submissionMode: 'unconfigured' } }, session);
  const result = await client.record({ event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: '1-5s' } }, session);
  assert.match(notice, /anonymous usage analytics/i);
  assert.equal(result.sent, true);
  assert.equal(relay.requests.length, 3);
  assert.equal((await client.beginCommand('search')).installationEventPending, false);
  if (process.platform !== 'win32') assert.equal((await stat(join(directory, 'telemetry.json'))).mode & 0o777, 0o600);
});

test('existing installations receive a one-command grace period without backfill', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-existing-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'applications.ndjson'), '{"private":"historical"}\n');
  const relay = fakeRelay();
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: relay.fetch, stderr: () => {} });
  const firstSession = await client.beginCommand('search');
  assert.equal(firstSession.installationEventPending, false);
  assert.equal((await client.record({ event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: 'under-1s' } }, firstSession)).sent, false);
  assert.equal(relay.requests.length, 0);
  const secondSession = await client.beginCommand('search');
  assert.equal((await client.record({ event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: 'under-1s' } }, secondSession)).sent, true);
  assert.equal(relay.requests.length, 2);
});

test('an interrupted existing-install disclosure still preserves the grace command', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-grace-recovery-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: true, disclosed: true, graceConsumed: false, installationEventPending: false }));
  const relay = fakeRelay();
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: relay.fetch, stderr: () => {} });
  const session = await client.beginCommand('search');
  assert.equal(session.allowSend, false);
  assert.equal((await client.record({ event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: 'under-1s' } }, session)).reason, 'grace');
  assert.equal(relay.requests.length, 0);
});

test('a pre-disclosure telemetry config cannot send on its disclosure command', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-undisclosed-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: true, disclosed: false, graceConsumed: false, installationEventPending: false }));
  const relay = fakeRelay();
  let notice = '';
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: relay.fetch, stderr: (value) => { notice += value; } });
  const session = await client.beginCommand('search');
  assert.match(notice, /anonymous usage analytics/i);
  assert.equal(session.allowSend, false);
  assert.equal(relay.requests.length, 0);
});

test('disable preserves identity while reset removes it and keeps telemetry disabled', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-controls-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const relay = fakeRelay();
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: relay.fetch, stderr: () => {} });
  const session = await client.beginCommand('search');
  await client.record({ event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: 'under-1s' } }, session);
  const disabled = await client.configure('disable');
  assert.equal(disabled.enabled, false);
  assert.equal(disabled.hasInstallationId, true);
  await client.configure('enable');
  const resumed = await client.beginCommand('search');
  await client.record({ event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: 'under-1s' } }, resumed);
  assert.equal(relay.requests.filter((request) => request.url.endsWith('/v1/install')).length, 1);
  const reset = await client.configure('reset');
  assert.equal(reset.enabled, false);
  assert.equal(reset.hasInstallationId, false);
  assert.equal((await client.status()).enabled, false);
});

test('preview validates but never transmits and network failures never escape', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-preview-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: async () => { throw new Error('offline'); }, stderr: () => {} });
  const event = { event: 'application_paused', properties: { jobHash: 'a'.repeat(64), ats: 'lever', stage: 'legal', reason: 'legal' } };
  assert.equal((await client.preview(event)).event, 'application_paused');
  const session = await client.beginCommand('apply');
  assert.deepEqual(await client.record(event, session), { sent: false, reason: 'unavailable' });
});

test('converts a transient job URL to a hash and domain before validation', async () => {
  const event = await prepareTelemetryInput({
    event: 'application_paused',
    properties: { jobUrl: 'https://jobs.example.com/role/123?email=candidate@example.com', ats: 'ashby', stage: 'legal', reason: 'legal' },
  });
  assert.equal(event.properties.domain, undefined);
  assert.equal(event.properties.jobHash.length, 64);
  assert.equal(JSON.stringify(event).includes('candidate@example.com'), false);
});

test('record input rejects undocumented top-level properties', async () => {
  await assert.rejects(() => prepareTelemetryInput({
    event: 'command_completed',
    properties: { command: 'search', result: 'success', durationBucket: 'under-1s' },
    prompt: 'private free-form content',
  }), /unknown/i);
});

test('strict record rejects invalid schema while automatic telemetry stays best effort', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'telemetry-strict-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const client = new TelemetryClient({ stateDir: directory, endpoint: 'https://relay.example.com', fetch: fakeRelay().fetch, stderr: () => {} });
  const session = await client.beginCommand('telemetry');
  const invalid = { event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: 'raw private value' } };
  await assert.rejects(() => client.record(invalid, session, { strict: true }), /durationBucket/i);
  assert.deepEqual(await client.record(invalid, session), { sent: false, reason: 'invalid' });
});
