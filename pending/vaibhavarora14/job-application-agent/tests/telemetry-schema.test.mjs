import assert from 'node:assert/strict';
import test from 'node:test';

import {
  canonicalizeJobUrl,
  createTelemetryEnvelope,
  jobIdentity,
  validateEvent,
} from '../scripts/telemetry-schema.mjs';

const baseJob = {
  company: 'Example AI',
  title: 'Staff Product Engineer',
  jobHash: 'a'.repeat(64),
  domain: 'jobs.example.com',
  ats: 'greenhouse',
};

test('canonicalizes job URLs and hashes the destination without query data', async () => {
  assert.equal(canonicalizeJobUrl('https://Jobs.Example.com/role/123/?utm_source=x#apply'), 'https://jobs.example.com/role/123');
  const first = await jobIdentity('https://jobs.example.com/role/123?ref=friend');
  const second = await jobIdentity('https://jobs.example.com/role/123?utm_source=x');
  assert.equal(first.jobHash, second.jobHash);
  assert.equal(first.domain, 'jobs.example.com');
  assert.equal(first.jobHash.length, 64);
});

test('accepts rich structured job and workflow events', () => {
  const event = validateEvent({
    event: 'job_assessed',
    properties: {
      ...baseJob,
      fitScore: 84,
      eligibility: 'eligible',
      decision: 'review',
      matchTags: ['role_family', 'skills', 'remote'],
      gapTags: ['salary_unknown'],
    },
  });
  assert.equal(event.properties.company, 'Example AI');
  assert.equal(event.properties.fitScore, 84);
});

test('accepts bounded discovery sources without exposing application URLs or attention details', () => {
  for (const source of ['direct-company', 'job-board', 'user-supplied', 'web-search']) {
    const event = validateEvent({
      event: 'job_discovered',
      properties: {
        ...baseJob,
        source,
        jobCountry: 'India',
        workMode: 'remote',
        seniority: 'staff',
        employmentType: 'full-time',
        roleFamily: 'product-engineering',
      },
    });
    assert.equal(event.properties.source, source);
    assert.equal('url' in event.properties, false);
  }
});

test('rejects direct identity, free-form content, unknown properties, and oversized payloads', () => {
  const valid = { event: 'job_assessed', properties: { ...baseJob, fitScore: 80, eligibility: 'eligible', decision: 'review', matchTags: [], gapTags: [] } };
  assert.throws(() => validateEvent({ ...valid, properties: { ...valid.properties, company: 'candidate@example.com' } }), /identity/i);
  assert.throws(() => validateEvent({ ...valid, properties: { ...valid.properties, title: 'Call +1 555 555 1212' } }), /identity/i);
  assert.throws(() => validateEvent({ ...valid, properties: { ...valid.properties, candidateLocation: 'Toronto' } }), /unknown/i);
  assert.throws(() => validateEvent({ event: 'skill_error', properties: { errorCode: 'network_failure', stage: 'submission', recoverable: true, rawError: 'private text' } }), /unknown/i);
  assert.throws(() => validateEvent({ ...valid, properties: { ...valid.properties, company: 'x'.repeat(5000) } }), /company/i);
});

test('creates a bounded relay envelope without client timestamps or direct identity', () => {
  const envelope = createTelemetryEnvelope({
    installationId: '11111111-1111-4111-8111-111111111111',
    token: 'signed-token',
    event: { event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: '1-5s' } },
    skillVersion: '1.1.0',
  });
  assert.deepEqual(Object.keys(envelope).sort(), ['event', 'installationId', 'properties', 'schemaVersion', 'skillVersion', 'token']);
  assert.ok(Buffer.byteLength(JSON.stringify(envelope)) < 4096);
});

test('validates a representative payload for every documented event', () => {
  const samples = [
    { event: 'installation_started', properties: { osFamily: 'macos', nodeMajor: 24, submissionMode: 'unconfigured' } },
    { event: 'command_completed', properties: { command: 'search', result: 'success', durationBucket: '1-5s' } },
    { event: 'job_discovered', properties: { ...baseJob, source: 'x', jobCountry: 'United States', workMode: 'remote', seniority: 'staff', employmentType: 'full-time', roleFamily: 'product-engineering', salaryCurrency: 'USD', salaryMin: 100000, salaryMax: 180000 } },
    { event: 'job_assessed', properties: { ...baseJob, fitScore: 75, eligibility: 'unclear', decision: 'ask', matchTags: ['skills'], gapTags: ['authorization_unclear'] } },
    { event: 'application_started', properties: { jobHash: baseJob.jobHash, ats: 'ashby', approvalMode: 'review-each', requiredFieldCount: 12, resumeRequired: true, coverLetterRequired: false, referralPresent: false } },
    { event: 'application_step', properties: { jobHash: baseJob.jobHash, ats: 'lever', stage: 'questions', fieldCategory: 'short-answer', retryCount: 1, durationBucket: '1-2m' } },
    { event: 'application_paused', properties: { jobHash: baseJob.jobHash, ats: 'workday', stage: 'legal', reason: 'legal' } },
    { event: 'application_skipped', properties: { jobHash: baseJob.jobHash, reason: 'closed', fitScore: 82, eligibility: 'eligible' } },
    { event: 'application_submitted', properties: { ...baseJob, durationBucket: '5-15m', fieldsFilled: 14, shortAnswerCount: 2, resumeUploaded: true, approvalMode: 'routine-auto' } },
    { event: 'round_completed', properties: { requestedCount: 10, submittedCount: 7, assessedCount: 15, skippedCount: 5, pausedCount: 2, errorCount: 1, durationBucket: '15m-plus' } },
    { event: 'outcome_recorded', properties: { ...baseJob, outcome: 'interview', daysSinceSubmission: 4, interviewQuality: 'promising', failurePoint: 'process' } },
    { event: 'review_generated', properties: { submissionCount: 10, interviewCount: 1, rejectionCount: 2, offerCount: 0, withdrawalCount: 0, reviewDue: true } },
    { event: 'skill_error', properties: { errorCode: 'site_changed', stage: 'application', ats: 'comeet', jobHash: baseJob.jobHash, recoverable: true } },
  ];
  for (const sample of samples) assert.equal(validateEvent(sample).event, sample.event);
});

test('keeps interview-learning telemetry bounded and rejects free-form notes', () => {
  const event = validateEvent({
    event: 'outcome_recorded',
    properties: { ...baseJob, outcome: 'rejected', daysSinceSubmission: 12, interviewQuality: 'weak', failurePoint: 'interviewer' },
  });
  assert.equal(event.properties.interviewQuality, 'weak');
  assert.equal(event.properties.failurePoint, 'interviewer');
  assert.throws(() => validateEvent({
    event: 'outcome_recorded',
    properties: { ...baseJob, outcome: 'rejected', daysSinceSubmission: 12, interviewQuality: 'weak', failurePoint: 'interviewer', note: 'private interview notes' },
  }), /unknown/i);
  assert.throws(() => validateEvent({
    event: 'outcome_recorded',
    properties: { ...baseJob, outcome: 'rejected', daysSinceSubmission: 12, failurePoint: 'interviewer' },
  }), /requires interviewQuality/i);
});
