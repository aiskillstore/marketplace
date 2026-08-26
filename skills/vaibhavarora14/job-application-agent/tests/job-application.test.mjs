import assert from 'node:assert/strict';
import { execFileSync, spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { buildReview, commandCategory, durationBucket, migrateProfile, profileStatus, scoreJob, telemetryJobAssessed, validateLedgerEntry, validateProfile, validateSubmissionTelemetry } from '../scripts/job-application.mjs';

const target = {
  name: 'Test Candidate',
  email: 'candidate@example.com',
  phone: '+1 555 0100',
  location: 'Toronto, Canada',
  workAuthorization: 'Canada',
  roleFamilies: ['product-engineering', 'full-stack', 'ai-ml'],
  seniority: ['senior', 'staff'],
  skills: ['TypeScript', 'Python', 'React'],
  targetLocations: ['Canada', 'Remote'],
  excludedLocations: ['United States only'],
  workModes: ['remote'],
  industries: ['AI'],
  excludedCompanies: ['Blocked Corp'],
  submissionMode: 'review-each',
  yearsExperience: 10,
  autoSubmitMinScore: 80,
  manualReviewMinScore: 70,
  minMustHaveCoverage: 70,
};

const matchingJob = {
  title: 'Senior Product Engineer',
  company: 'Example AI',
  description: 'Build AI products with TypeScript, React and Python.',
  source: 'greenhouse',
  eligibility: 'eligible',
  postingStatus: 'active',
  roleFamily: 'product-engineering',
  seniority: 'senior',
  workMode: 'remote',
  remote: true,
  locations: ['Remote', 'Canada'],
  mustHaves: [
    { requirement: 'TypeScript', status: 'met', evidence: 'Resume skills and shipped products' },
    { requirement: 'React', status: 'met', evidence: 'Multiple production roles' },
    { requirement: 'Python', status: 'partial', evidence: 'Snorkel and Juvoxa' },
  ],
};

function isolatedCliEnv(directory) {
  return {
    ...process.env,
    JOB_APPLICATION_AGENT_STATE_DIR: directory,
    JOB_APPLICATION_AGENT_SOURCE_COMMUNITY_URL: 'http://127.0.0.1:9',
  };
}

function runCli(script, args, input, env) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [script, ...args], { env, stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
    child.stdin.end(JSON.stringify(input));
  });
}

test('validates a candidate-defined target profile', () => {
  assert.equal(validateProfile(target).name, 'Test Candidate');
  assert.throws(() => validateProfile({ ...target, roleFamilies: [] }), /non-empty/);
  assert.throws(() => validateProfile({ ...target, submissionMode: 'always' }), /review-each/);
});

test('returns the canonical resume path for direct browser uploads', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-resume-path-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  const resume = join(directory, 'resume.pdf');
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: false, disclosed: true, graceConsumed: true, installationEventPending: false }));
  await writeFile(resume, '%PDF-1.7\ncanonical resume fixture');
  const env = isolatedCliEnv(directory);

  const result = JSON.parse(execFileSync(process.execPath, [script, 'resume', 'path'], { env, encoding: 'utf8' }));

  assert.deepEqual(result, { path: resume });
});

test('migrates a legacy profile without discarding identity or salary preference', () => {
  const legacy = {
    name: 'Test Candidate', email: 'candidate@example.com', phone: '+1 555 0100',
    location: 'Bengaluru, India', workAuthorization: 'India', linkedin: 'https://linkedin.com/in/example',
    salaryPreference: 'INR 90 lakh annually',
  };
  const migrated = migrateProfile(legacy, {});
  assert.equal(migrated.name, legacy.name);
  assert.equal(migrated.targetCompensation, legacy.salaryPreference);
  assert.deepEqual(migrated.roleFamilies, ['product-engineering', 'full-stack', 'ai-ml']);
  assert.deepEqual(migrated.seniority, ['senior', 'staff']);
  assert.equal(migrated.submissionMode, 'routine-auto');
  assert.equal(migrated.autoSubmitMinScore, 80);
  assert.equal(migrated.manualReviewMinScore, 70);
  assert.equal(migrated.minMustHaveCoverage, 70);
  assert.equal(profileStatus(legacy).configured, false);
  assert.ok(profileStatus(legacy).legacyFields.includes('salaryPreference'));
  assert.equal(profileStatus(migrated).configured, true);
  const customized = migrateProfile({ ...migrated, autoSubmitMinScore: 85 }, {});
  assert.equal(customized.autoSubmitMinScore, 85);
});

test('scores a matching role from candidate preferences', () => {
  const result = scoreJob(matchingJob, target);
  assert.equal(result.decision, 'review');
  assert.equal(result.autoEligible, true);
  assert.equal(result.mustHaveCoverage, 83);
  assert.ok(result.score >= 80);
  assert.equal(scoreJob({ ...matchingJob, discoverySourceId: 'community-abcdef1234567890' }, target).decision, 'review');
});

test('applies posting, eligibility, work-mode, seniority and evidence gates before auto-submit', () => {
  assert.equal(scoreJob({ ...matchingJob, postingStatus: 'closed' }, target).decision, 'exclude');
  assert.equal(scoreJob({ ...matchingJob, postingStatus: 'unclear' }, target).decision, 'ask');
  assert.equal(scoreJob({ ...matchingJob, eligibility: 'ineligible' }, target).decision, 'exclude');
  assert.equal(scoreJob({ ...matchingJob, eligibility: 'unclear' }, target).decision, 'ask');
  assert.equal(scoreJob({ ...matchingJob, workMode: 'onsite' }, target).decision, 'exclude');
  assert.equal(scoreJob({ ...matchingJob, seniority: 'principal' }, target).decision, 'skip');
  assert.equal(scoreJob({ ...matchingJob, mustHaves: undefined }, target).decision, 'ask');
  assert.equal(scoreJob({ ...matchingJob, mustHaves: [{ requirement: 'Rust', status: 'unclear' }] }, target).decision, 'ask');
  assert.equal(scoreJob({ ...matchingJob, mustHaves: [{ requirement: 'Rust', status: 'missing' }] }, target).decision, 'skip');
});

test('keeps 70-79 scores manual and caps experience mismatches below auto-submit', () => {
  const manualRequirements = Array.from({ length: 10 }, (_, index) => ({ requirement: `Requirement ${index + 1}`, status: index < 7 ? 'met' : 'missing' }));
  const manual = scoreJob({ ...matchingJob, description: 'General software products', mustHaves: manualRequirements }, target);
  assert.equal(manual.decision, 'review');
  assert.equal(manual.autoEligible, false);
  assert.ok(manual.score >= 70 && manual.score < 80);

  const overlevel = scoreJob({ ...matchingJob, experienceMin: 2, experienceMax: 5 }, target);
  assert.equal(overlevel.decision, 'review');
  assert.equal(overlevel.autoEligible, false);
  assert.ok(overlevel.score <= 79);

  const customTarget = { ...target, seniority: [...target.seniority, 'lead'] };
  const lead = scoreJob({ ...matchingJob, seniority: 'lead' }, customTarget);
  assert.equal(lead.decision, 'review');
  assert.equal(lead.autoEligible, false);
});

test('skips published compensation below a comparable configured floor', () => {
  const compensatedTarget = { ...target, compensationFloor: { amount: 9000000, currency: 'INR', period: 'year' } };
  assert.equal(scoreJob({ ...matchingJob, salaryMaximum: 6000000, salaryCurrency: 'INR' }, compensatedTarget).decision, 'skip');
  const unknown = scoreJob({ ...matchingJob, salaryMaximum: undefined, salaryCurrency: undefined }, compensatedTarget);
  assert.equal(unknown.decision, 'review');
  assert.equal(unknown.autoEligible, true);
});

test('regresses the five confirmed rejection patterns', () => {
  const dave = scoreJob({ ...matchingJob, company: 'Dave Evans', title: 'Founding Engineer', postingStatus: 'closed', seniority: 'founding' }, target);
  assert.equal(dave.decision, 'exclude');

  const launchDarkly = scoreJob({ ...matchingJob, company: 'LaunchDarkly', eligibility: 'ineligible' }, target);
  assert.equal(launchDarkly.decision, 'exclude');

  const playPower = scoreJob({ ...matchingJob, company: 'PlayPower Labs', experienceMin: 2, experienceMax: 5 }, target);
  assert.equal(playPower.decision, 'review');
  assert.equal(playPower.autoEligible, false);
  assert.ok(playPower.score <= 79);

  const railway = scoreJob({
    ...matchingJob,
    company: 'Railway',
    mustHaves: [
      { requirement: 'TypeScript', status: 'met' },
      { requirement: 'React product architecture', status: 'met' },
      { requirement: 'Complex asynchronous deployment jobs', status: 'partial' },
      { requirement: 'GraphQL', status: 'missing' },
      { requirement: 'Temporal or Rust', status: 'missing' },
    ],
  }, target);
  assert.equal(railway.decision, 'skip');
  assert.equal(railway.autoEligible, false);

  const holepunch = scoreJob({
    ...matchingJob,
    company: 'Holepunch',
    title: 'Senior Node.js Software Engineer',
    postingStatus: 'closed',
    mustHaves: [{ requirement: 'P2P networking', status: 'missing' }],
  }, target);
  assert.equal(holepunch.decision, 'exclude');
});

test('excludes explicit ineligibility and candidate exclusions', () => {
  assert.equal(scoreJob({
    title: 'Staff Backend Engineer', company: 'Example', description: 'Python', source: 'lever', eligibility: 'ineligible', remote: true, locations: ['Canada'],
  }, target).decision, 'exclude');
  assert.equal(scoreJob({
    title: 'Staff Backend Engineer', company: 'Blocked Corp Ltd', description: 'Python', source: 'lever', eligibility: 'eligible', remote: true, locations: ['Canada'],
  }, target).decision, 'exclude');
});

test('pauses on unclear eligibility', () => {
  const result = scoreJob({
    title: 'Senior Backend Engineer', company: 'Example', description: 'Python', source: 'company', eligibility: 'unclear', remote: true, locations: ['Remote'],
  }, target);
  assert.equal(result.decision, 'ask');
});

test('accepts only confirmed submission ledger shapes', () => {
  const entry = {
    id: 'example-senior-product-engineer-2026-01-15',
    company: 'Example',
    role: 'Senior Product Engineer',
    url: 'https://jobs.example.com/123',
    source: 'company',
    score: 80,
    status: 'submitted',
    submittedAt: '2026-01-15T10:00:00.000Z',
    approval: 'APPROVE SUBMIT',
    answers: {},
  };
  assert.deepEqual(validateLedgerEntry(entry), entry);
  assert.equal(validateLedgerEntry({ ...entry, employerJobId: 'greenhouse:123' }).employerJobId, 'greenhouse:123');
  assert.equal(validateLedgerEntry({ ...entry, id: 'workday-role', source: 'workday' }).source, 'workday');
  assert.throws(() => validateLedgerEntry({ ...entry, status: 'draft' }), /submitted/);
});

test('validates structured submission metrics without adding them to the ledger shape', () => {
  const metrics = { durationBucket: '5-15m', fieldsFilled: 14, shortAnswerCount: 2, resumeUploaded: true };
  assert.deepEqual(validateSubmissionTelemetry(metrics), metrics);
  assert.throws(() => validateSubmissionTelemetry({ ...metrics, note: 'private text' }), /unknown/i);
  assert.throws(() => validateSubmissionTelemetry({ ...metrics, fieldsFilled: 1.5 }), /integer/i);
});

test('requires review at each ten confirmed submissions', () => {
  const entries = Array.from({ length: 10 }, (_, index) => ({ status: 'submitted', submittedAt: `2026-01-${String(index + 1).padStart(2, '0')}T10:00:00Z` }));
  assert.equal(buildReview(entries).reviewDue, true);
  assert.equal(buildReview(entries.slice(0, 9)).reviewDue, false);
  const withOutcome = entries.map((entry, index) => index === 0 ? { ...entry, status: 'interview' } : entry);
  assert.equal(buildReview(withOutcome).submittedTotal, 10);
  assert.equal(buildReview(withOutcome).outcomeCounts.interview, 1);
  assert.equal(buildReview(withOutcome).reviewDue, true);
});

test('deduplicates ledger entries by normalized URL', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  const entry = {
    id: 'example-role-1', company: 'Example', role: 'Senior Product Engineer', url: 'https://jobs.example.com/123?utm_source=x', source: 'company', score: 80, status: 'submitted', submittedAt: '2026-01-15T10:00:00Z', approval: 'STANDING AUTHORIZATION', answers: {},
    telemetry: { durationBucket: '5-15m', fieldsFilled: 14, shortAnswerCount: 2, resumeUploaded: true },
  };
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: false, disclosed: true, graceConsumed: true, installationEventPending: false }));
  const env = isolatedCliEnv(directory);
  execFileSync(process.execPath, [script, 'ledger', 'add', '--stdin'], { input: JSON.stringify(entry), env, encoding: 'utf8' });
  const duplicate = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'check', '--stdin'], { input: JSON.stringify({ id: 'different', url: 'https://jobs.example.com/123?ref=friend' }), env, encoding: 'utf8' }));
  assert.equal(duplicate.duplicate, true);
  const relabelled = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'check', '--stdin'], {
    input: JSON.stringify({ id: 'different-again', company: 'Example Holdings', role: 'Staff Engineer', url: 'https://jobs.example.com/123?candidateTracking=opaque-value' }), env, encoding: 'utf8',
  }));
  assert.equal(relabelled.duplicate, true);
  assert.equal((await readFile(join(directory, 'applications.ndjson'), 'utf8')).includes('telemetry'), false);
  if (process.platform !== 'win32') assert.equal((await stat(join(directory, 'applications.ndjson'))).mode & 0o777, 0o600);
});

test('warns on same-company role matches and serializes concurrent duplicate submissions', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-dedup-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: false, disclosed: true, graceConsumed: true, installationEventPending: false }));
  const env = isolatedCliEnv(directory);
  const base = {
    company: 'Example', role: 'Senior Product Engineer', url: 'https://jobs.example.com/123', source: 'company', score: 88,
    status: 'submitted', submittedAt: '2026-01-15T10:00:00Z', approval: 'STANDING AUTHORIZATION', answers: {}, employerJobId: 'example:123',
  };
  const [first, second] = await Promise.all([
    runCli(script, ['ledger', 'add', '--stdin'], { ...base, id: 'example-role-1' }, env),
    runCli(script, ['ledger', 'add', '--stdin'], { ...base, id: 'example-role-2', url: 'https://jobs.example.com/123?ref=other' }, env),
  ]);
  assert.deepEqual([first.code, second.code].sort(), [0, 1]);
  assert.equal((await readFile(join(directory, 'applications.ndjson'), 'utf8')).trim().split('\n').length, 1);

  const possible = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'check', '--stdin'], {
    input: JSON.stringify({ id: 'new-requisition', company: 'Example', role: 'Senior Product Engineer', url: 'https://jobs.example.com/456' }), env, encoding: 'utf8',
  }));
  assert.equal(possible.duplicate, false);
  assert.equal(possible.possibleDuplicate, true);
});

test('records structured outcomes idempotently without duplicate rows', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-outcomes-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: false, disclosed: true, graceConsumed: true, installationEventPending: false }));
  await writeFile(join(directory, 'applications.ndjson'), `${JSON.stringify({
    id: 'example-role-1', company: 'Example', role: 'Senior Product Engineer', url: 'https://jobs.example.com/123', source: 'company', score: 88,
    status: 'submitted', submittedAt: '2026-01-15T10:00:00Z', approval: 'STANDING AUTHORIZATION', answers: {},
  })}\n`);
  const env = isolatedCliEnv(directory);
  const outcome = { id: 'example-role-1', status: 'rejected', occurredAt: '2026-01-20T09:00:00Z', note: 'No sponsorship' };
  const enriched = { ...outcome, reasons: [{ category: 'eligibility', evidence: 'explicit' }] };
  const first = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'outcome', '--stdin'], { input: JSON.stringify(outcome), env, encoding: 'utf8' }));
  const second = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'outcome', '--stdin'], { input: JSON.stringify(enriched), env, encoding: 'utf8' }));
  const third = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'outcome', '--stdin'], { input: JSON.stringify(enriched), env, encoding: 'utf8' }));
  assert.equal(first.recorded, true);
  assert.equal(second.recorded, true);
  assert.equal(second.enriched, true);
  assert.equal(third.recorded, false);
  assert.equal(third.duplicate, true);
  assert.equal((await readFile(join(directory, 'outcomes.ndjson'), 'utf8')).trim().split('\n').length, 2);
});

test('records bounded interview quality and failure-point enrichment idempotently', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-interview-quality-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: false, disclosed: true, graceConsumed: true, installationEventPending: false }));
  await writeFile(join(directory, 'applications.ndjson'), `${JSON.stringify({
    id: 'example-role-1', company: 'Example', role: 'Staff Product Engineer', url: 'https://jobs.example.com/123', source: 'company', score: 91,
    status: 'submitted', submittedAt: '2026-01-15T10:00:00Z', approval: 'STANDING AUTHORIZATION', answers: {},
  })}\n`);
  const env = isolatedCliEnv(directory);
  const base = { id: 'example-role-1', status: 'interview', occurredAt: '2026-01-20T09:00:00Z' };
  const enriched = { ...base, interviewQuality: 'weak', failurePoint: 'role-scope' };
  const first = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'outcome', '--stdin'], { input: JSON.stringify(base), env, encoding: 'utf8' }));
  const second = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'outcome', '--stdin'], { input: JSON.stringify(enriched), env, encoding: 'utf8' }));
  const third = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'outcome', '--stdin'], { input: JSON.stringify(enriched), env, encoding: 'utf8' }));
  assert.equal(first.recorded, true);
  assert.equal(second.recorded, true);
  assert.equal(second.enriched, true);
  assert.equal(third.duplicate, true);
  const rows = (await readFile(join(directory, 'outcomes.ndjson'), 'utf8')).trim().split('\n').map(JSON.parse);
  assert.equal(rows.length, 2);
  assert.equal(rows[1].interviewQuality, 'weak');
  assert.equal(rows[1].failurePoint, 'role-scope');

  const invalid = await runCli(script, ['ledger', 'outcome', '--stdin'], { ...base, occurredAt: '2026-01-21T09:00:00Z', interviewQuality: 'excellent' }, env);
  assert.equal(invalid.code, 1);
  assert.match(invalid.stderr, /interviewQuality/i);
});

test('builds canonical mature-cohort reviews and honors explicit acknowledgement', () => {
  const old = Array.from({ length: 20 }, (_, index) => ({
    id: `old-${index}`, company: `Company ${index}`, role: 'Senior Engineer', url: `https://jobs.example.com/${index}`,
    status: 'submitted', submittedAt: '2025-12-01T10:00:00Z', source: 'company', score: 80, approval: 'STANDING AUTHORIZATION', answers: {},
  }));
  const recent = Array.from({ length: 2 }, (_, index) => ({
    id: `recent-${index}`, company: `Recent ${index}`, role: 'Staff Engineer', url: `https://jobs.example.com/recent-${index}`,
    status: 'submitted', submittedAt: '2026-01-19T10:00:00Z', source: 'company', score: 85, approval: 'STANDING AUTHORIZATION', answers: {},
  }));
  const duplicate = { ...old[0], id: 'old-0-duplicate', url: 'https://another-ats.example.com/requisition/old-0' };
  const outcomes = [
    { id: 'old-0', status: 'interview', occurredAt: '2025-12-10T10:00:00Z', interviewQuality: 'promising' },
    { id: 'old-1', status: 'rejected', occurredAt: '2025-12-11T10:00:00Z', interviewQuality: 'dead', failurePoint: 'constraints', reasons: [{ category: 'must-have-gap', evidence: 'inferred' }] },
  ];
  const now = new Date('2026-01-20T12:00:00Z');
  const review = buildReview([...old, ...recent, duplicate], outcomes, [], now);
  assert.equal(review.rawSubmissionRows, 23);
  assert.equal(review.uniqueSubmittedTotal, 22);
  assert.equal(review.duplicateSubmissionRows, 1);
  assert.equal(review.maturedApplications, 20);
  assert.equal(review.reviewDue, true);
  assert.deepEqual(review.reviewReasons.sort(), ['outcome-effectiveness', 'submission-hygiene']);
  assert.equal(review.reasonCounts['must-have-gap'], 1);
  assert.equal(review.interviewQualityCounts.promising, 1);
  assert.equal(review.interviewQualityCounts.dead, 1);
  assert.equal(review.failurePointCounts.constraints, 1);
  assert.deepEqual(review.interviewLearningSegments, [
    { source: 'company', fitScoreBand: '80-89', interviewQuality: 'dead', failurePoint: 'constraints', count: 1 },
    { source: 'company', fitScoreBand: '80-89', interviewQuality: 'promising', failurePoint: 'unknown', count: 1 },
  ]);
  assert.equal(review.matureOutcomeCounts.interview, 1);
  assert.equal(review.matureOutcomeCounts.rejected, 1);
  assert.equal(review.conversionRates.interview, 5);
  assert.equal(review.conversionRates.rejected, 5);

  const acknowledged = buildReview([...old, ...recent, duplicate], outcomes, [{
    reviewedAt: '2026-01-20T11:00:00Z', uniqueSubmissionCount: 22, maturedApplicationCount: 20,
  }], now);
  assert.equal(acknowledged.reviewDue, false);
});

test('preserves interview quality after a later final outcome', () => {
  const applications = [{
    id: 'role-1', company: 'Example', role: 'Staff Engineer', url: 'https://jobs.example.com/role-1',
    status: 'submitted', submittedAt: '2025-12-01T10:00:00Z', source: 'company', score: 90, approval: 'STANDING AUTHORIZATION', answers: {},
  }];
  const outcomes = [
    { id: 'role-1', status: 'interview', occurredAt: '2025-12-10T10:00:00Z', interviewQuality: 'promising' },
    { id: 'role-1', status: 'rejected', occurredAt: '2025-12-15T10:00:00Z' },
  ];
  const review = buildReview(applications, outcomes, [], new Date('2026-01-20T12:00:00Z'));
  assert.equal(review.outcomeCounts.rejected, 1);
  assert.equal(review.outcomeCounts.interview, 0);
  assert.equal(review.interviewQualityCounts.promising, 1);
});

test('acknowledges a generated review only through the explicit CLI command', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-review-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  await writeFile(join(directory, 'telemetry.json'), JSON.stringify({ version: 1, enabled: false, disclosed: true, graceConsumed: true, installationEventPending: false }));
  const entries = Array.from({ length: 10 }, (_, index) => ({
    id: `role-${index}`, company: `Company ${index}`, role: 'Senior Engineer', url: `https://jobs.example.com/${index}`,
    source: 'company', score: 80, status: 'submitted', submittedAt: '2026-01-01T10:00:00Z', approval: 'STANDING AUTHORIZATION', answers: {},
  }));
  await writeFile(join(directory, 'applications.ndjson'), `${entries.map(JSON.stringify).join('\n')}\n`);
  const env = isolatedCliEnv(directory);
  const before = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'review'], { env, encoding: 'utf8' }));
  assert.equal(before.reviewDue, true);
  assert.equal(await readFile(join(directory, 'reviews.ndjson'), 'utf8').catch(() => ''), '');
  const ack = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'review-ack', '--stdin'], {
    input: JSON.stringify({ reviewedAt: '2026-02-01T10:00:00Z' }), env, encoding: 'utf8',
  }));
  assert.equal(ack.acknowledged, true);
  const after = JSON.parse(execFileSync(process.execPath, [script, 'ledger', 'review'], { env, encoding: 'utf8' }));
  assert.equal(after.reviewDue, false);
});

test('maps commands and durations to bounded telemetry categories', () => {
  assert.equal(commandCategory(['ledger', 'add', '--stdin']), 'apply');
  assert.equal(commandCategory(['ledger', 'outcome', '--stdin']), 'outcome');
  assert.equal(commandCategory(['score', '--stdin']), 'assess');
  assert.equal(commandCategory(['sources', 'list']), 'search');
  assert.equal(durationBucket(700), 'under-1s');
  assert.equal(durationBucket(70_000), '1-2m');
  assert.equal(durationBucket(2_000_000), '15m-plus');
});

test('builds a structured assessment event without description or candidate profile data', async () => {
  const job = {
    title: 'Senior Product Engineer', company: 'Example AI', description: 'private long job description', source: 'greenhouse', eligibility: 'eligible',
    remote: true, locations: ['Remote'], url: 'https://jobs.example.com/123?candidate=secret',
  };
  const result = scoreJob(job, target);
  const event = await telemetryJobAssessed(job, result);
  assert.equal(event.event, 'job_assessed');
  assert.equal(event.properties.company, 'Example AI');
  assert.equal('description' in event.properties, false);
  assert.equal(JSON.stringify(event).includes('candidate=secret'), false);
  assert.equal(JSON.stringify(event).includes('Test Candidate'), false);
});

test('telemetry CLI controls are private and reset removes anonymous credentials', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'public-job-agent-telemetry-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const script = fileURLToPath(new URL('../scripts/job-application.mjs', import.meta.url));
  const env = { ...process.env, JOB_APPLICATION_AGENT_STATE_DIR: directory, JOB_APPLICATION_AGENT_TELEMETRY_URL: 'https://relay.invalid' };
  const disabled = JSON.parse(execFileSync(process.execPath, [script, 'telemetry', 'disable'], { env, encoding: 'utf8' }));
  assert.equal(disabled.enabled, false);
  const reset = JSON.parse(execFileSync(process.execPath, [script, 'telemetry', 'reset'], { env, encoding: 'utf8' }));
  assert.equal(reset.hasInstallationId, false);
  if (process.platform !== 'win32') assert.equal((await stat(join(directory, 'telemetry.json'))).mode & 0o777, 0o600);
});
