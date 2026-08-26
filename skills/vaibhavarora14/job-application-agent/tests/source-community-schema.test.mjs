import assert from 'node:assert/strict';
import test from 'node:test';

import {
  communityJobId,
  communitySourceId,
  createCommunityJobContributionEnvelope,
  isRepeatableCommunitySourceRoute,
  normalizeCommunityJob,
  normalizeCommunitySource,
  validateCommunityJobContributionEnvelope,
  validateCommunityJobList,
} from '../scripts/source-community-schema.mjs';

const source = {
  name: 'Example Jobs',
  baseUrl: 'https://example.com/',
  kind: 'job-board',
  regions: ['global'],
  roleFamilies: ['engineering'],
  requiresSession: false,
};

const job = {
  url: 'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc?utm_source=private#apply',
  company: 'Example',
  role: 'Senior Product Engineer',
  applicationChannel: 'ashby',
  discoverySource: 'job-board',
};

test('normalizes an applied job and derives its reusable provider without referral data', () => {
  const normalized = normalizeCommunityJob(job);

  assert.deepEqual(normalized, {
    url: 'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc',
    company: 'Example',
    role: 'Senior Product Engineer',
    applicationChannel: 'ashby',
    discoverySource: 'job-board',
    providerUrl: 'https://jobs.ashbyhq.com/example',
  });
});

test('accepts public job detail identifiers but rejects private, personal, and credential-bearing routes', () => {
  const accepted = [
    'https://job-boards.greenhouse.io/example/jobs/1234567',
    'https://jobs.lever.co/example/12345678-1234-4123-8123-123456789abc',
    'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc',
    'https://company.example/careers/senior-product-engineer',
  ];
  for (const url of accepted) assert.equal(normalizeCommunityJob({ ...job, url }).url, url);

  const rejected = [
    'http://localhost/jobs/123',
    'https://jobs.example.com/123',
    'https://linkedin.com/in/some-person',
    'https://company.example/candidate/9876543210',
    'https://company.example/referral/12345678-1234-4123-8123-123456789abc',
    'https://candidate-14155550100.example.org/jobs/123',
    'https://company.example/jobs/+1-415-555-0100',
    'https://company.example/jobs/access-token=abcdefghijklmnop',
    'https://user:password@company.example/jobs/123',
  ];
  for (const url of rejected) assert.throws(() => normalizeCommunityJob({ ...job, url }), /public HTTPS|personal|credential|reserved example/i, url);
});

test('preserves only stable query job identifiers while removing referral data', async () => {
  const first = normalizeCommunityJob({
    ...job,
    url: 'https://company.example/viewjob?jobId=111&utm_source=private&ref=candidate@example.com',
  });
  const second = normalizeCommunityJob({
    ...job,
    url: 'https://company.example/viewjob?jobId=222&utm_source=private',
  });

  assert.equal(first.url, 'https://company.example/viewjob?jobid=111');
  assert.equal(second.url, 'https://company.example/viewjob?jobid=222');
  assert.notEqual(await communityJobId(first), await communityJobId(second));
  assert.equal(first.url.includes('candidate@example.com'), false);
  assert.equal(normalizeCommunityJob({ ...job, url: 'https://boards.example/jobs?gh_jid=7654321&utm_campaign=secret' }).url, 'https://boards.example/jobs?gh_jid=7654321');
});

test('community job IDs deduplicate tracking variants and contribution envelopes validate strictly', async () => {
  const first = await communityJobId(job);
  const second = await communityJobId({ ...job, url: `${job.url.split('?')[0]}?ref=another#details` });
  assert.equal(first, second);
  assert.match(first, /^community-job-[0-9a-f]{16}$/);

  const envelope = createCommunityJobContributionEnvelope({
    installationId: '12345678-1234-4123-8123-123456789abc',
    token: 'signed-token',
    job,
    skillVersion: '3.2.0',
  });
  assert.deepEqual(validateCommunityJobContributionEnvelope(envelope), envelope);
  assert.throws(() => validateCommunityJobContributionEnvelope({ ...envelope, answers: { private: true } }), /Unknown community job contribution property/i);
});

test('validates paginated public community job responses without accepting extra data', async () => {
  const jobId = await communityJobId(job);
  const response = {
    version: 1,
    jobs: [{
      jobId,
      ...normalizeCommunityJob(job),
      firstSeenAt: '2026-08-24T10:00:00.000Z',
      lastSeenAt: '2026-08-24T11:00:00.000Z',
      contributionCount: 2,
    }],
    nextCursor: 'opaque-cursor',
  };

  assert.deepEqual(validateCommunityJobList(response), response);
  assert.throws(() => validateCommunityJobList({ ...response, installationId: 'private' }), /Unknown community job list property/i);
  assert.throws(() => validateCommunityJobList({ ...response, jobs: [{ ...response.jobs[0], score: 90 }] }), /Unknown community job entry property/i);
});

test('rejects known ATS and network job-detail routes', () => {
  const detailUrls = [
    'https://example.wd5.myworkdayjobs.com/en-US/jobs/job/Bengaluru/Senior-Engineer_R-12345',
    'https://www.linkedin.com/jobs/view/1234567890',
    'https://job-boards.greenhouse.io/example/jobs/1234567',
    'https://jobs.lever.co/example/12345678-1234-4123-8123-123456789abc',
    'https://jobs.ashbyhq.com/example/12345678-1234-4123-8123-123456789abc',
    'https://apply.workable.com/example/j/ABC123DEF4/',
    'https://jobs.smartrecruiters.com/Example/123456789-senior-engineer',
  ];

  for (const baseUrl of detailUrls) {
    assert.equal(isRepeatableCommunitySourceRoute(new URL(baseUrl)), false, baseUrl);
    assert.throws(
      () => normalizeCommunitySource({ ...source, baseUrl }),
      /repeatable discovery surface|identity-like content/i,
      baseUrl,
    );
  }
});

test('accepts roots and recognizable collection, directory, feed, careers, openings, and job-index routes', () => {
  const collectionUrls = [
    'https://example.com/',
    'https://example.com/careers',
    'https://example.com/openings/engineering',
    'https://example.com/jobs/search',
    'https://example.com/job-index',
    'https://example.com/community/directory',
    'https://example.com/hiring/feed.xml',
    'https://example.wd5.myworkdayjobs.com/en-US/jobs',
    'https://www.linkedin.com/jobs/search',
    'https://job-boards.greenhouse.io/example',
    'https://jobs.lever.co/example',
    'https://jobs.ashbyhq.com/example',
    'https://apply.workable.com/example',
    'https://jobs.smartrecruiters.com/Example',
  ];

  for (const baseUrl of collectionUrls) {
    assert.equal(isRepeatableCommunitySourceRoute(new URL(baseUrl)), true, baseUrl);
    assert.equal(normalizeCommunitySource({ ...source, baseUrl }).baseUrl, baseUrl.replace(/\/$/, ''), baseUrl);
  }
});

test('fails closed for unknown non-collection paths and strips collection queries and fragments', () => {
  for (const baseUrl of ['https://example.com/software-engineer', 'https://example.com/jobs/senior-software-engineer']) {
    assert.equal(isRepeatableCommunitySourceRoute(new URL(baseUrl)), false, baseUrl);
    assert.throws(() => normalizeCommunitySource({ ...source, baseUrl }), /repeatable discovery surface/i);
  }

  const normalized = normalizeCommunitySource({
    ...source,
    baseUrl: 'https://example.com/openings/engineering?email=candidate@example.com&token=secret#jobs',
  });
  assert.equal(normalized.baseUrl, 'https://example.com/openings/engineering');
  assert.equal(JSON.stringify(normalized).includes('candidate@example.com'), false);
});

test('rejects identity-like path namespaces even when they contain a collection cue', () => {
  for (const baseUrl of ['https://example.com/users/jane/openings', 'https://example.com/profile/jane/careers', 'https://x.com/jane/jobs']) {
    assert.throws(() => normalizeCommunitySource({ ...source, baseUrl }), /profile or personal|identity-like/i, baseUrl);
  }
});

test('rejects repeatedly encoded identity paths and identity-bearing taxonomy fields', () => {
  assert.throws(
    () => normalizeCommunitySource({ ...source, baseUrl: 'https://example.com/candidate%2540example.com/openings' }),
    /identity-like/i,
  );
  assert.throws(() => normalizeCommunitySource({ ...source, regions: ['candidate@example.com'] }), /identity-like/i);
  assert.throws(() => normalizeCommunitySource({ ...source, roleFamilies: ['+1 415 555 0100'] }), /identity-like/i);
});

test('rejects Unicode and compatibility-form email identities before sharing', () => {
  const privateValues = [
    { name: 'Jobs curated by josé@example.com' },
    { regions: ['用户@example.com'] },
    { regions: ['उपयोगकर्ता@example.com'] },
    { roleFamilies: ['ｊｏｓｅ＠ｅｘａｍｐｌｅ．ｃｏｍ'] },
    { baseUrl: 'https://example.com/%E7%94%A8%E6%88%B7%40example.com/openings' },
  ];

  for (const override of privateValues) {
    assert.throws(() => normalizeCommunitySource({ ...source, ...override }), /identity-like/i);
  }
});

test('rejects credential-like opaque path segments before source sharing', () => {
  assert.throws(
    () => normalizeCommunitySource({ ...source, baseUrl: 'https://example.com/feed/AbCdEfGhIjKlMnOpQrStUvWxYz/jobs' }),
    /credential-like/i,
  );
});

test('rejects JWT, key-value, and prefixed credentials in source paths', () => {
  const credentialUrls = [
    'https://example.com/feed/eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c/jobs',
    'https://example.com/feed/token=AbCdEfGhIjKlMnOpQrStUvWxYz/jobs',
    'https://example.com/feed/api_key.AbCdEfGhIjKlMnOpQrStUvWxYz/jobs',
  ];

  for (const baseUrl of credentialUrls) {
    assert.throws(() => normalizeCommunitySource({ ...source, baseUrl }), /credential-like/i, baseUrl);
  }
});

test('rejects phone identities written with Unicode decimal digits', () => {
  const privateValues = [
    { name: 'Jobs curated by +٩١ ٩٨٧٦٥ ٤٣٢١٠' },
    { regions: ['+९१ ९८७६५ ४३२१०'] },
    { baseUrl: 'https://example.com/%2B%D9%A9%D9%A1%20%D9%A9%D9%A8%D9%A7%D9%A6%D9%A5%20%D9%A4%D9%A3%D9%A2%D9%A1%D9%A0/jobs' },
  ];

  for (const override of privateValues) {
    assert.throws(() => normalizeCommunitySource({ ...source, ...override }), /identity-like/i);
  }
});

test('normalizes compatibility characters before personal-path classification', () => {
  for (const baseUrl of ['https://example.com/ｐｒｏｆｉｌｅ/candidate/jobs', 'https://example.com/ｕｓｅｒ/candidate/jobs']) {
    assert.throws(() => normalizeCommunitySource({ ...source, baseUrl }), /identity-like/i, baseUrl);
  }
});

test('removes every trailing path separator when canonicalizing source URLs', async () => {
  const canonical = normalizeCommunitySource({ ...source, baseUrl: 'https://example.com/jobs' });
  const redundant = normalizeCommunitySource({ ...source, baseUrl: 'https://example.com/jobs///' });

  assert.equal(redundant.baseUrl, canonical.baseUrl);
  assert.equal(await communitySourceId(redundant), await communitySourceId(canonical));
});

test('normalizes trailing DNS root dots before rejecting private hosts', () => {
  for (const baseUrl of ['https://localhost./jobs', 'https://service.local./careers', 'https://service.internal./openings']) {
    assert.throws(() => normalizeCommunitySource({ ...source, baseUrl }), /public internet hostname/i, baseUrl);
  }
});

test('rejects identity-like public hostnames after normalizing a trailing DNS root dot', () => {
  for (const baseUrl of ['https://14155550100.example.org./jobs', 'https://candidate-14155550100.example.org/openings']) {
    assert.throws(() => normalizeCommunitySource({ ...source, baseUrl }), /identity-like/i, baseUrl);
  }
});

test('source IDs normalize scheme and hostname case while preserving path case', async () => {
  const upperHost = await communitySourceId({ ...source, baseUrl: 'HTTPS://EXAMPLE.COM/Jobs' });
  const lowerHost = await communitySourceId({ ...source, baseUrl: 'https://example.com/Jobs' });
  const lowerPath = await communitySourceId({ ...source, baseUrl: 'https://example.com/jobs' });
  assert.equal(upperHost, lowerHost);
  assert.notEqual(upperHost, lowerPath);
});
