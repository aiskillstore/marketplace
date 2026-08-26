const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SHA256 = /^[0-9a-f]{64}$/;
const DOMAIN = /^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/;
const CURRENCY = /^[A-Z]{3}$/;
const VERSION = /^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/;

export const TELEMETRY_SCHEMA_VERSION = 1;
export const TELEMETRY_MAX_BYTES = 4096;

const values = (...items) => new Set(items);
const ATS = values('linkedin', 'greenhouse', 'lever', 'ashby', 'workable', 'comeet', 'workday', 'rippling', 'smartrecruiters', 'google-form', 'company', 'email', 'other');
const SOURCES = values('direct-company', 'linkedin', 'x', 'hacker-news', 'yc', 'job-board', 'aggregator', 'company', 'email', 'referral', 'user-supplied', 'web-search', 'other');
const DURATIONS = values('under-1s', '1-5s', '5-30s', '30-60s', '1-2m', '2-5m', '5-15m', '15m-plus');
const COMMANDS = values('onboard', 'search', 'assess', 'apply', 'batch', 'round', 'outcome', 'review', 'resume', 'profile', 'telemetry', 'other');
const RESULTS = values('success', 'paused', 'skipped', 'abandoned', 'error');
const ELIGIBILITY = values('eligible', 'unclear', 'ineligible');
const DECISIONS = values('review', 'ask', 'skip', 'exclude');
const WORK_MODES = values('remote', 'hybrid', 'onsite', 'unspecified');
const SENIORITIES = values('junior', 'mid', 'senior', 'staff', 'principal', 'lead', 'manager', 'director', 'founding', 'unspecified');
const EMPLOYMENT = values('full-time', 'part-time', 'contract', 'temporary', 'internship', 'unspecified');
const ROLE_FAMILIES = values('frontend', 'backend', 'full-stack', 'product-engineering', 'ai-ml', 'platform', 'infrastructure', 'mobile', 'engineering-management', 'architecture', 'security', 'data', 'other');
const APPROVAL_MODES = values('review-each', 'routine-auto');
const SUBMISSION_MODES = values('review-each', 'routine-auto', 'unconfigured');
const STAGES = values('discovery', 'assessment', 'application', 'contact', 'resume', 'questions', 'legal', 'demographic', 'review', 'submission', 'confirmation', 'outcome');
const FIELD_CATEGORIES = values('contact', 'links', 'location', 'authorization', 'compensation', 'experience', 'resume', 'cover-letter', 'referral', 'short-answer', 'legal', 'demographic', 'other');
const PAUSE_REASONS = values('login', 'sso', 'mfa', 'captcha', 'legal', 'demographic', 'eligibility', 'compensation', 'sensitive-id', 'unverifiable', 'attachment', 'candidate-judgment', 'site-error', 'other');
const SKIP_REASONS = values('closed', 'duplicate', 'ineligible', 'low-fit', 'location', 'salary', 'seniority', 'candidate-choice', 'no-direct-link', 'other');
const OUTCOMES = values('interview', 'rejected', 'offer', 'withdrawn');
const INTERVIEW_QUALITIES = values('promising', 'viable', 'weak', 'dead');
const FAILURE_POINTS = values('role-scope', 'company-problem', 'constraints', 'interviewer', 'process', 'unknown');
const ERROR_CODES = values('invalid_input', 'network_failure', 'relay_unavailable', 'authentication_required', 'site_changed', 'upload_failed', 'submission_unconfirmed', 'rate_limited', 'internal_error');
const MATCH_TAGS = values('role_family', 'seniority', 'skills', 'industry', 'location', 'remote', 'salary', 'ai', 'product', 'leadership', 'authorization');
const GAP_TAGS = values('role_family', 'seniority', 'skills', 'industry', 'location', 'salary_unknown', 'salary_below', 'authorization_unclear', 'sponsorship', 'experience', 'domain', 'other');

const text = (max, identitySafe = false) => ({ kind: 'text', max, identitySafe });
const integer = (min, max) => ({ kind: 'integer', min, max });
const boolean = { kind: 'boolean' };
const enumValue = (set) => ({ kind: 'enum', set });
const enumArray = (set, max = 12) => ({ kind: 'enum-array', set, max });

const JOB = {
  company: text(160, true), title: text(200, true), jobHash: { kind: 'hash' }, domain: { kind: 'domain' }, ats: enumValue(ATS),
};

export const EVENT_SCHEMAS = {
  installation_started: { required: { osFamily: enumValue(values('macos', 'linux', 'windows', 'other')), nodeMajor: integer(20, 99), submissionMode: enumValue(SUBMISSION_MODES) } },
  command_completed: { required: { command: enumValue(COMMANDS), result: enumValue(RESULTS), durationBucket: enumValue(DURATIONS) } },
  job_discovered: { required: { ...JOB, source: enumValue(SOURCES), jobCountry: text(80, true), workMode: enumValue(WORK_MODES), seniority: enumValue(SENIORITIES), employmentType: enumValue(EMPLOYMENT), roleFamily: enumValue(ROLE_FAMILIES) }, optional: { salaryCurrency: { kind: 'currency' }, salaryMin: integer(0, 10000000), salaryMax: integer(0, 10000000) } },
  job_assessed: { required: { ...JOB, fitScore: integer(0, 100), eligibility: enumValue(ELIGIBILITY), decision: enumValue(DECISIONS), matchTags: enumArray(MATCH_TAGS), gapTags: enumArray(GAP_TAGS) } },
  application_started: { required: { jobHash: { kind: 'hash' }, ats: enumValue(ATS), approvalMode: enumValue(APPROVAL_MODES), requiredFieldCount: integer(0, 500), resumeRequired: boolean, coverLetterRequired: boolean, referralPresent: boolean } },
  application_step: { required: { jobHash: { kind: 'hash' }, ats: enumValue(ATS), stage: enumValue(STAGES), fieldCategory: enumValue(FIELD_CATEGORIES), retryCount: integer(0, 20), durationBucket: enumValue(DURATIONS) } },
  application_paused: { required: { jobHash: { kind: 'hash' }, ats: enumValue(ATS), stage: enumValue(STAGES), reason: enumValue(PAUSE_REASONS) } },
  application_skipped: { required: { jobHash: { kind: 'hash' }, reason: enumValue(SKIP_REASONS), fitScore: integer(0, 100), eligibility: enumValue(ELIGIBILITY) } },
  application_submitted: { required: { ...JOB, durationBucket: enumValue(DURATIONS), fieldsFilled: integer(0, 500), shortAnswerCount: integer(0, 100), resumeUploaded: boolean, approvalMode: enumValue(APPROVAL_MODES) } },
  round_completed: { required: { requestedCount: integer(1, 1000), submittedCount: integer(0, 1000), assessedCount: integer(0, 10000), skippedCount: integer(0, 10000), pausedCount: integer(0, 10000), errorCount: integer(0, 10000), durationBucket: enumValue(DURATIONS) } },
  outcome_recorded: {
    required: { ...JOB, outcome: enumValue(OUTCOMES), daysSinceSubmission: integer(0, 3650) },
    optional: { interviewQuality: enumValue(INTERVIEW_QUALITIES), failurePoint: enumValue(FAILURE_POINTS) },
  },
  review_generated: { required: { submissionCount: integer(0, 100000), interviewCount: integer(0, 100000), rejectionCount: integer(0, 100000), offerCount: integer(0, 100000), withdrawalCount: integer(0, 100000), reviewDue: boolean } },
  skill_error: { required: { errorCode: enumValue(ERROR_CODES), stage: enumValue(STAGES), recoverable: boolean }, optional: { ats: enumValue(ATS), jobHash: { kind: 'hash' } } },
};

export function containsDirectIdentity(value) {
  if (typeof value !== 'string') return false;
  return /(?:[^\s@]+@[^\s@]+\.[^\s@]+)|(?:https?:\/\/|www\.)|(?:linkedin\.com|github\.com)|(?:\+?\d[\d\s().-]{6,}\d)/i.test(value);
}

function validateProperty(name, value, rule) {
  if (rule.kind === 'text') {
    if (typeof value !== 'string' || !value.trim() || value.length > rule.max) throw new Error(`${name} must be a non-empty string no longer than ${rule.max} characters.`);
    if (rule.identitySafe && containsDirectIdentity(value)) throw new Error(`${name} contains direct identity data.`);
    if (/[\x00-\x1f\x7f]/.test(value)) throw new Error(`${name} contains control characters.`);
    return value.trim();
  }
  if (rule.kind === 'integer') {
    if (!Number.isInteger(value) || value < rule.min || value > rule.max) throw new Error(`${name} must be an integer from ${rule.min} to ${rule.max}.`);
    return value;
  }
  if (rule.kind === 'boolean') {
    if (typeof value !== 'boolean') throw new Error(`${name} must be a Boolean.`);
    return value;
  }
  if (rule.kind === 'enum') {
    if (typeof value !== 'string' || !rule.set.has(value)) throw new Error(`${name} is invalid.`);
    return value;
  }
  if (rule.kind === 'enum-array') {
    if (!Array.isArray(value) || value.length > rule.max || value.some((item) => typeof item !== 'string' || !rule.set.has(item))) throw new Error(`${name} must contain only documented tags.`);
    return [...new Set(value)];
  }
  if (rule.kind === 'hash') {
    if (typeof value !== 'string' || !SHA256.test(value)) throw new Error(`${name} must be a SHA-256 job hash.`);
    return value;
  }
  if (rule.kind === 'domain') {
    if (typeof value !== 'string' || !DOMAIN.test(value)) throw new Error(`${name} must be a canonical domain.`);
    return value;
  }
  if (rule.kind === 'currency') {
    if (typeof value !== 'string' || !CURRENCY.test(value)) throw new Error(`${name} must be an ISO-style currency code.`);
    return value;
  }
  throw new Error(`Unsupported telemetry property ${name}.`);
}

export function validateEvent(input) {
  if (!input || Array.isArray(input) || typeof input !== 'object') throw new Error('Telemetry event must be an object.');
  const schema = EVENT_SCHEMAS[input.event];
  if (!schema) throw new Error('Unknown telemetry event.');
  if (!input.properties || Array.isArray(input.properties) || typeof input.properties !== 'object') throw new Error('Telemetry properties must be an object.');
  const rules = { ...schema.required, ...(schema.optional ?? {}) };
  for (const name of Object.keys(input.properties)) if (!rules[name]) throw new Error(`Unknown telemetry property: ${name}.`);
  const properties = {};
  for (const [name, rule] of Object.entries(schema.required)) {
    if (!(name in input.properties)) throw new Error(`Missing telemetry property: ${name}.`);
    properties[name] = validateProperty(name, input.properties[name], rule);
  }
  for (const [name, rule] of Object.entries(schema.optional ?? {})) if (name in input.properties) properties[name] = validateProperty(name, input.properties[name], rule);
  if (input.event === 'outcome_recorded' && properties.failurePoint && !properties.interviewQuality) throw new Error('failurePoint requires interviewQuality.');
  const result = { event: input.event, properties };
  if (new TextEncoder().encode(JSON.stringify(result)).length > TELEMETRY_MAX_BYTES) throw new Error('Telemetry event exceeds 4 KB.');
  return result;
}

export function canonicalizeJobUrl(value) {
  const url = new URL(value);
  if (!['https:', 'http:'].includes(url.protocol)) throw new Error('Job URL must use HTTP or HTTPS.');
  url.protocol = 'https:';
  url.username = '';
  url.password = '';
  url.search = '';
  url.hash = '';
  url.hostname = url.hostname.toLowerCase();
  url.pathname = url.pathname.replace(/\/+$/, '') || '/';
  return url.toString().replace(/\/$/, '');
}

export async function jobIdentity(value) {
  const canonical = canonicalizeJobUrl(value);
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical));
  return { jobHash: [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join(''), domain: new URL(canonical).hostname };
}

export function createTelemetryEnvelope({ installationId, token, event, properties, skillVersion }) {
  if (!UUID.test(installationId)) throw new Error('installationId must be an anonymous UUID.');
  if (typeof token !== 'string' || token.length < 8 || token.length > 2048) throw new Error('token is invalid.');
  if (typeof skillVersion !== 'string' || !VERSION.test(skillVersion)) throw new Error('skillVersion is invalid.');
  const safe = validateEvent(typeof event === 'string' ? { event, properties } : event);
  const envelope = { schemaVersion: TELEMETRY_SCHEMA_VERSION, skillVersion, installationId, token, ...safe };
  if (new TextEncoder().encode(JSON.stringify(envelope)).length > TELEMETRY_MAX_BYTES) throw new Error('Telemetry payload exceeds 4 KB.');
  return envelope;
}

export function validateTelemetryEnvelope(input) {
  if (!input || Array.isArray(input) || typeof input !== 'object') throw new Error('Telemetry payload must be an object.');
  const allowed = new Set(['schemaVersion', 'skillVersion', 'installationId', 'token', 'event', 'properties']);
  for (const key of Object.keys(input)) if (!allowed.has(key)) throw new Error(`Unknown telemetry envelope property: ${key}.`);
  if (input.schemaVersion !== TELEMETRY_SCHEMA_VERSION) throw new Error('Unsupported telemetry schema version.');
  return createTelemetryEnvelope(input);
}
