#!/usr/bin/env node

import { createHash, randomUUID } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { appendFile, chmod, mkdir, open, readFile, rename, stat, unlink, writeFile } from 'node:fs/promises';
import { platform } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import { createSecretStore, migrateLegacyStateDir, resolveStateDir } from './secret-store.mjs';
import { SourceCommunityClient } from './source-community-client.mjs';
import { normalizeCommunityJob, normalizeCommunitySource } from './source-community-schema.mjs';
import { TelemetryClient } from './telemetry-client.mjs';
import { jobIdentity } from './telemetry-schema.mjs';

const SOURCES = new Set(['linkedin', 'greenhouse', 'lever', 'ashby', 'workable', 'comeet', 'workday', 'rippling', 'smartrecruiters', 'google-form', 'company', 'email', 'other']);
const DISCOVERY_SOURCES = new Set(['direct-company', 'linkedin', 'x', 'yc', 'hacker-news', 'job-board', 'email', 'user-supplied', 'web-search', 'other']);
const ELIGIBILITY = new Set(['eligible', 'unclear', 'ineligible']);
const POSTING_STATUS = new Set(['active', 'closed', 'unclear']);
const WORK_MODES = new Set(['remote', 'hybrid', 'onsite', 'unspecified']);
const JOB_SENIORITIES = new Set(['junior', 'mid', 'senior', 'staff', 'principal', 'lead', 'manager', 'director', 'founding', 'unspecified']);
const ROLE_FAMILIES = new Set(['frontend', 'backend', 'full-stack', 'product-engineering', 'ai-ml', 'platform', 'infrastructure', 'mobile', 'engineering-management', 'architecture', 'security', 'data', 'other']);
const MUST_HAVE_STATUS = new Set(['met', 'partial', 'missing', 'unclear']);
const INTERVIEW_QUALITIES = new Set(['promising', 'viable', 'weak', 'dead']);
const FAILURE_POINTS = new Set(['role-scope', 'company-problem', 'constraints', 'interviewer', 'process', 'unknown']);
const APPROVALS = new Set(['APPROVE SUBMIT', 'STANDING AUTHORIZATION']);
const MODES = new Set(['review-each', 'routine-auto']);
const TELEMETRY_DURATIONS = new Set(['under-1s', '1-5s', '5-30s', '30-60s', '1-2m', '2-5m', '5-15m', '15m-plus']);
const AUTONOMY_SCOPES = Object.freeze(['discover', 'assess', 'fill', 'upload-resume', 'submit', 'send-recruiting-email', 'record-ledger', 'record-outcomes', 'cleanup-tabs', 'open-improvement-pr']);
const AUTONOMY_HARD_STOPS = Object.freeze(['authentication', 'mfa', 'captcha', 'legal-attestation', 'demographic', 'government-id', 'unverifiable-claim', 'ambiguous-authorization', 'ambiguous-compensation']);
const ATTENTION_STAGES = new Set(['discovery', 'assessment', 'application', 'contact', 'resume', 'questions', 'legal', 'demographic', 'review', 'submission', 'confirmation', 'outcome', 'answers', 'upload']);
const ATTENTION_BLOCKERS = new Set(['authentication', 'mfa', 'captcha', 'legal-attestation', 'demographic', 'government-id', 'ambiguous-authorization', 'ambiguous-compensation', 'unverifiable-claim', 'judgment', 'video', 'upload', 'site-error', 'other']);
const REQUIRED_ACTIONS = new Set(['sign-in', 'complete-mfa', 'complete-captcha', 'review-legal', 'choose-demographic', 'provide-government-id', 'provide-authorization', 'provide-compensation', 'verify-claim', 'provide-judgment', 'record-video', 'enable-upload', 'retry-site']);
const COMPANY_REAPPLY_COOLDOWN_DAYS = 15;
const COMPANY_REAPPLY_OVERRIDE = 'CANDIDATE APPROVED EARLY REAPPLICATION';
const SOURCE_CATALOG_URL = new URL('../references/SOURCES.json', import.meta.url);
const SOURCE_CATALOG = JSON.parse(readFileSync(SOURCE_CATALOG_URL, 'utf8'));
if (!Array.isArray(SOURCE_CATALOG)) throw new Error('The packaged source catalog is invalid.');
const SOURCE_CATALOG_IDS = new Set(SOURCE_CATALOG.map((source) => sourceId(source.id, 'source catalog id')));
const COMMUNITY_SOURCE_ID = /^community-[0-9a-f]{16}$/;
const REQUIRED_PROFILE = ['name', 'email', 'phone', 'location', 'workAuthorization', 'roleFamilies', 'seniority', 'targetLocations', 'workModes', 'submissionMode', 'yearsExperience', 'autoSubmitMinScore', 'manualReviewMinScore', 'minMustHaveCoverage'];
const STRING_PROFILE_FIELDS = new Set(['name', 'email', 'phone', 'location', 'workAuthorization', 'linkedin', 'github', 'portfolio', 'availability', 'currentCompensation', 'targetCompensation', 'submissionMode']);
const ARRAY_PROFILE_FIELDS = new Set(['roleFamilies', 'seniority', 'skills', 'targetLocations', 'excludedLocations', 'workModes', 'industries', 'excludedCompanies']);
const NUMBER_PROFILE_FIELDS = new Set(['yearsExperience', 'autoSubmitMinScore', 'manualReviewMinScore', 'minMustHaveCoverage']);
const OBJECT_PROFILE_FIELDS = new Set(['compensationFloor']);
const LEGACY_PROFILE_FIELDS = new Set(['salaryPreference']);
const DEFAULT_TARGETING = {
  roleFamilies: ['product-engineering', 'full-stack', 'ai-ml'],
  seniority: ['senior', 'staff'],
  skills: ['TypeScript', 'Python', 'React', 'Node.js', 'PostgreSQL', 'MCP', 'AI agents'],
  targetLocations: ['India', 'Remote', 'Worldwide'],
  workModes: ['remote'],
  industries: ['AI', 'developer tools'],
  submissionMode: 'routine-auto',
  yearsExperience: 10,
  autoSubmitMinScore: 80,
  manualReviewMinScore: 70,
  minMustHaveCoverage: 70,
};

function stateDir() {
  return resolveStateDir();
}

const secretStore = createSecretStore({ stateDir });

export function durationBucket(milliseconds) {
  if (milliseconds < 1_000) return 'under-1s';
  if (milliseconds < 5_000) return '1-5s';
  if (milliseconds < 30_000) return '5-30s';
  if (milliseconds < 60_000) return '30-60s';
  if (milliseconds < 120_000) return '1-2m';
  if (milliseconds < 300_000) return '2-5m';
  if (milliseconds < 900_000) return '5-15m';
  return '15m-plus';
}

export function commandCategory([area, action]) {
  if (area === 'profile' && action === 'set') return 'onboard';
  if (area === 'profile' && action === 'migrate') return 'onboard';
  if (area === 'profile') return 'profile';
  if (area === 'resume') return 'resume';
  if (area === 'score') return 'assess';
  if (area === 'ledger' && action === 'add') return 'apply';
  if (area === 'ledger' && action === 'outcome') return 'outcome';
  if (area === 'ledger' && action === 'review') return 'review';
  if (area === 'ledger' && action === 'review-ack') return 'review';
  if (area === 'ledger') return 'apply';
  if (area === 'telemetry') return 'telemetry';
  if (area === 'autonomy') return 'profile';
  if (area === 'round') return 'round';
  if (area === 'sources') return 'search';
  if (area === 'attention' || area === 'friction') return 'batch';
  return 'other';
}

function telemetryStage(command) {
  return ({ search: 'discovery', assess: 'assessment', apply: 'submission', outcome: 'outcome', review: 'review', resume: 'resume', profile: 'contact', onboard: 'contact' })[command] ?? 'application';
}

function telemetryErrorCode(error) {
  const message = String(error?.message ?? '');
  if (/keychain|credential manager|dpapi|authentication|login/i.test(message)) return 'authentication_required';
  if (/network|fetch|http/i.test(message)) return 'network_failure';
  if (/invalid|must|required|expected|unsupported/i.test(message)) return 'invalid_input';
  return 'internal_error';
}

function sourceToAts(source) {
  return SOURCES.has(source) ? source : 'other';
}

function assessmentTags(result) {
  const matches = [];
  const gaps = [];
  for (const reason of result.reasons ?? []) {
    if (/^Role family:/i.test(reason)) matches.push('role_family');
    else if (/^Seniority:/i.test(reason)) matches.push('seniority');
    else if (/^Skills:/i.test(reason)) matches.push('skills');
    else if (/^Industry:/i.test(reason)) matches.push('industry');
    else if (/Remote-compatible/i.test(reason)) matches.push('remote');
    else if (/Target location:/i.test(reason)) matches.push('location');
  }
  for (const gap of result.gaps ?? []) {
    if (/role family/i.test(gap)) gaps.push('role_family');
    else if (/seniority/i.test(gap)) gaps.push('seniority');
    else if (/skill/i.test(gap)) gaps.push('skills');
    else if (/location|work mode/i.test(gap)) gaps.push('location');
    else if (/eligibility|authorization/i.test(gap)) gaps.push('authorization_unclear');
    else gaps.push('other');
  }
  return { matchTags: [...new Set(matches)], gapTags: [...new Set(gaps)] };
}

export async function telemetryJobAssessed(job, result) {
  if (!job.url) return null;
  const identity = await jobIdentity(job.url);
  return {
    event: 'job_assessed',
    properties: {
      ...identity,
      company: job.company,
      title: job.title,
      ats: sourceToAts(String(job.applicationChannel ?? job.source).toLowerCase()),
      fitScore: result.score,
      eligibility: String(job.eligibility).toLowerCase(),
      decision: result.decision,
      ...assessmentTags(result),
    },
  };
}

async function telemetryApplicationSubmitted(entry, details = {}) {
  const identity = await jobIdentity(entry.url);
  const answers = Object.keys(entry.answers ?? {});
  return {
    event: 'application_submitted',
    properties: {
      ...identity,
      company: entry.company,
      title: entry.role,
      ats: sourceToAts(entry.applicationChannel ?? entry.source),
      durationBucket: details.durationBucket ?? 'under-1s',
      fieldsFilled: details.fieldsFilled ?? answers.length,
      shortAnswerCount: details.shortAnswerCount ?? answers.filter((key) => !/resume|attachment/i.test(key)).length,
      resumeUploaded: details.resumeUploaded ?? answers.some((key) => /resume|attachment/i.test(key)),
      approvalMode: entry.approval === 'STANDING AUTHORIZATION' ? 'routine-auto' : 'review-each',
    },
  };
}

function object(value, label) {
  if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error(`${label} must be an object.`);
  return value;
}

function string(value, label, max = 5000) {
  if (typeof value !== 'string' || !value.trim() || value.length > max) throw new Error(`${label} must be a non-empty string no longer than ${max} characters.`);
  return value.trim();
}

function stringArray(value, label, required = false) {
  if (!Array.isArray(value) || (required && value.length === 0)) throw new Error(`${label} must be ${required ? 'a non-empty' : 'an'} array of strings.`);
  return value.map((item, index) => string(item, `${label}[${index}]`, 300));
}

function sourceId(value, label) {
  const id = string(value, label, 80).toLowerCase();
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id)) throw new Error(`${label} must be a kebab-case public source ID.`);
  return id;
}

function knownDiscoverySourceId(value, label) {
  const id = sourceId(value, label);
  if (!SOURCE_CATALOG_IDS.has(id) && !COMMUNITY_SOURCE_ID.test(id)) throw new Error(`${label} must match a packaged or community source ID.`);
  return id;
}

function integer(value, label, min, max) {
  if (!Number.isInteger(value) || value < min || value > max) throw new Error(`${label} must be an integer from ${min} to ${max}.`);
  return value;
}

function compensationFloor(value) {
  const input = object(value, 'profile.compensationFloor');
  const allowed = new Set(['amount', 'currency', 'period']);
  for (const key of Object.keys(input)) if (!allowed.has(key)) throw new Error(`Unknown profile.compensationFloor property: ${key}.`);
  const currency = string(input.currency, 'profile.compensationFloor.currency', 3).toUpperCase();
  if (!/^[A-Z]{3}$/.test(currency)) throw new Error('profile.compensationFloor.currency must be a three-letter currency code.');
  if (input.period !== 'year') throw new Error('profile.compensationFloor.period must be year.');
  return { amount: integer(input.amount, 'profile.compensationFloor.amount', 0, 100_000_000), currency, period: 'year' };
}

function normalizeUrl(value) {
  const url = new URL(string(value, 'url', 2048));
  url.hash = '';
  for (const key of [...url.searchParams.keys()]) {
    if (!/^(job|jobid|jid|gh_jid|requisition|requisitionid|reqid|posting|postingid|position|positionid|vacancy|vacancyid)$/i.test(key)) url.searchParams.delete(key);
  }
  return url.toString().replace(/\/$/, '').toLowerCase();
}

function terms(values) {
  return values.map((value) => value.toLowerCase().trim()).filter(Boolean);
}

function matchesAny(text, values) {
  return terms(values).filter((value) => text.includes(value));
}

export function validateProfile(input) {
  const profile = object(input, 'profile');
  for (const field of REQUIRED_PROFILE) {
    if (ARRAY_PROFILE_FIELDS.has(field)) stringArray(profile[field], `profile.${field}`, true);
    else if (NUMBER_PROFILE_FIELDS.has(field)) integer(profile[field], `profile.${field}`, field === 'yearsExperience' ? 0 : 0, field === 'yearsExperience' ? 80 : 100);
    else string(profile[field], `profile.${field}`, 1000);
  }
  if (!MODES.has(profile.submissionMode)) throw new Error('profile.submissionMode must be review-each or routine-auto.');
  if (profile.manualReviewMinScore > profile.autoSubmitMinScore) throw new Error('profile.manualReviewMinScore must not exceed profile.autoSubmitMinScore.');
  for (const field of STRING_PROFILE_FIELDS) if (profile[field] != null) string(profile[field], `profile.${field}`, 2000);
  for (const field of ARRAY_PROFILE_FIELDS) if (profile[field] != null) stringArray(profile[field], `profile.${field}`);
  for (const field of NUMBER_PROFILE_FIELDS) if (profile[field] != null) integer(profile[field], `profile.${field}`, 0, field === 'yearsExperience' ? 80 : 100);
  const normalized = Object.fromEntries(Object.entries(profile).filter(([key]) => STRING_PROFILE_FIELDS.has(key) || ARRAY_PROFILE_FIELDS.has(key) || NUMBER_PROFILE_FIELDS.has(key) || OBJECT_PROFILE_FIELDS.has(key)));
  if (profile.compensationFloor != null) normalized.compensationFloor = compensationFloor(profile.compensationFloor);
  return normalized;
}

export function profileStatus(input) {
  const profile = object(input, 'profile');
  const missing = REQUIRED_PROFILE.filter((field) => profile[field] == null || profile[field] === '' || (Array.isArray(profile[field]) && profile[field].length === 0));
  const legacyFields = Object.keys(profile).filter((field) => LEGACY_PROFILE_FIELDS.has(field));
  let valid = false;
  let validationError = null;
  if (missing.length === 0) {
    try { validateProfile(profile); valid = true; } catch (error) { validationError = error.message; }
  }
  return { configured: valid, missing, legacyFields, ...(validationError ? { validationError } : {}), fields: Object.keys(profile).sort() };
}

export function migrateProfile(existingInput, overridesInput = {}) {
  const existing = object(existingInput, 'existing profile');
  const overrides = object(overridesInput, 'profile migration');
  const migrated = { ...DEFAULT_TARGETING, ...existing, ...overrides };
  if (migrated.targetCompensation == null && existing.salaryPreference != null) migrated.targetCompensation = existing.salaryPreference;
  for (const field of LEGACY_PROFILE_FIELDS) delete migrated[field];
  return validateProfile(migrated);
}

export function scoreJob(input, target) {
  const job = object(input, 'job');
  const profile = validateProfile(target);
  const title = string(job.title, 'job.title', 300);
  const company = string(job.company, 'job.company', 300);
  const description = string(job.description, 'job.description', 40000);
  const source = string(job.source, 'job.source', 40).toLowerCase();
  const discoverySource = job.discoverySource == null ? null : string(job.discoverySource, 'job.discoverySource', 40).toLowerCase();
  if (job.discoverySourceId != null) knownDiscoverySourceId(job.discoverySourceId, 'job.discoverySourceId');
  const applicationChannel = job.applicationChannel == null ? null : string(job.applicationChannel, 'job.applicationChannel', 40).toLowerCase();
  const eligibility = string(job.eligibility, 'job.eligibility', 40).toLowerCase();
  const postingStatus = string(job.postingStatus ?? 'unclear', 'job.postingStatus', 40).toLowerCase();
  const seniority = string(job.seniority ?? 'unspecified', 'job.seniority', 40).toLowerCase();
  const roleFamily = string(job.roleFamily ?? 'other', 'job.roleFamily', 80).toLowerCase();
  const workMode = string(job.workMode ?? (job.remote === true ? 'remote' : 'unspecified'), 'job.workMode', 40).toLowerCase();
  if (!SOURCES.has(source)) throw new Error('job.source is invalid.');
  if (discoverySource != null && !DISCOVERY_SOURCES.has(discoverySource)) throw new Error('job.discoverySource is invalid.');
  if (applicationChannel != null && !SOURCES.has(applicationChannel)) throw new Error('job.applicationChannel is invalid.');
  if (!ELIGIBILITY.has(eligibility)) throw new Error('job.eligibility must be eligible, unclear, or ineligible.');
  if (!POSTING_STATUS.has(postingStatus)) throw new Error('job.postingStatus must be active, closed, or unclear.');
  if (!JOB_SENIORITIES.has(seniority)) throw new Error('job.seniority is invalid.');
  if (!ROLE_FAMILIES.has(roleFamily)) throw new Error('job.roleFamily is invalid.');
  if (!WORK_MODES.has(workMode)) throw new Error('job.workMode is invalid.');

  const gates = [];
  const result = (decision, score, reasons, gaps, mustHaveCoverage = null, autoEligible = false) => ({ score, decision, autoEligible, mustHaveCoverage, gates, reasons, gaps });
  const excludedCompany = terms(profile.excludedCompanies ?? []).some((name) => company.toLowerCase().includes(name));
  if (eligibility === 'ineligible' || excludedCompany) {
    const gap = excludedCompany ? 'Company is excluded by the candidate.' : 'Posting is explicitly ineligible.';
    gates.push({ name: excludedCompany ? 'company' : 'eligibility', status: 'fail', reason: gap });
    return result('exclude', 0, [], [gap]);
  }
  if (eligibility === 'unclear') {
    const gap = 'Work eligibility or authorization needs candidate confirmation.';
    gates.push({ name: 'eligibility', status: 'ask', reason: gap });
    return result('ask', 0, [], [gap]);
  }
  gates.push({ name: 'eligibility', status: 'pass', reason: 'Posting is explicitly eligible.' });

  if (postingStatus === 'closed') {
    const gap = 'Posting or application channel is closed or stale.';
    gates.push({ name: 'posting-status', status: 'fail', reason: gap });
    return result('exclude', 0, [], [gap]);
  }
  if (postingStatus === 'unclear') {
    const gap = 'Posting status or application channel needs verification.';
    gates.push({ name: 'posting-status', status: 'ask', reason: gap });
    return result('ask', 0, [], [gap]);
  }
  gates.push({ name: 'posting-status', status: 'pass', reason: 'Direct application channel is active.' });

  const text = `${title}\n${description}`.toLowerCase();
  const locations = Array.isArray(job.locations) ? job.locations.join(' ').toLowerCase() : '';
  const reasons = [];
  const gaps = [];

  const excludedLocation = terms(profile.excludedLocations ?? []).some((place) => locations.includes(place));
  if (excludedLocation) {
    const gap = 'Posting is in an excluded location.';
    gates.push({ name: 'location', status: 'fail', reason: gap });
    return result('exclude', 0, reasons, [...gaps, gap]);
  }
  if (!terms(profile.workModes).includes(workMode)) {
    if (workMode === 'unspecified') {
      const gap = 'Work mode or location needs verification.';
      gates.push({ name: 'work-mode', status: 'ask', reason: gap });
      return result('ask', 0, reasons, [...gaps, gap]);
    }
    const gap = 'Posting work mode is incompatible with the candidate target.';
    gates.push({ name: 'work-mode', status: 'fail', reason: gap });
    return result('exclude', 0, reasons, [...gaps, gap]);
  }
  gates.push({ name: 'work-mode', status: 'pass', reason: `Work mode matches: ${workMode}.` });

  if (!terms(profile.seniority).includes(seniority)) {
    const gap = `Seniority is outside the candidate target: ${seniority}.`;
    gates.push({ name: 'seniority', status: 'fail', reason: gap });
    return result(seniority === 'unspecified' ? 'ask' : 'skip', 0, reasons, [...gaps, gap]);
  }
  gates.push({ name: 'seniority', status: 'pass', reason: `Seniority matches: ${seniority}.` });

  if (!Array.isArray(job.mustHaves) || job.mustHaves.length === 0) {
    const gap = 'Structured must-have evidence is missing.';
    gates.push({ name: 'must-have-evidence', status: 'ask', reason: gap });
    return result('ask', 0, reasons, [...gaps, gap]);
  }
  const mustHaves = job.mustHaves.map((item, index) => {
    const requirement = string(object(item, `job.mustHaves[${index}]`).requirement, `job.mustHaves[${index}].requirement`, 500);
    const status = string(item.status, `job.mustHaves[${index}].status`, 40).toLowerCase();
    if (!MUST_HAVE_STATUS.has(status)) throw new Error(`job.mustHaves[${index}].status is invalid.`);
    if (item.evidence != null) string(item.evidence, `job.mustHaves[${index}].evidence`, 2000);
    return { requirement, status };
  });
  if (mustHaves.some((item) => item.status === 'unclear')) {
    const gap = 'One or more must-have requirements need evidence verification.';
    gates.push({ name: 'must-have-evidence', status: 'ask', reason: gap });
    return result('ask', 0, reasons, [...gaps, gap]);
  }
  const mustHaveCoverage = Math.round(100 * mustHaves.reduce((sum, item) => sum + (item.status === 'met' ? 1 : item.status === 'partial' ? 0.5 : 0), 0) / mustHaves.length);
  if (mustHaveCoverage < profile.minMustHaveCoverage) {
    const gap = `Must-have evidence coverage is ${mustHaveCoverage}%, below ${profile.minMustHaveCoverage}%.`;
    gates.push({ name: 'must-have-evidence', status: 'fail', reason: gap });
    return result('skip', 0, reasons, [...gaps, gap], mustHaveCoverage);
  }
  gates.push({ name: 'must-have-evidence', status: 'pass', reason: `Must-have evidence coverage is ${mustHaveCoverage}%.` });

  if (profile.compensationFloor && job.salaryMaximum != null && String(job.salaryCurrency ?? '').toUpperCase() === profile.compensationFloor.currency) {
    integer(job.salaryMaximum, 'job.salaryMaximum', 0, 100_000_000);
    if (job.salaryMaximum < profile.compensationFloor.amount) {
      const gap = 'Published compensation maximum is below the configured floor.';
      gates.push({ name: 'compensation', status: 'fail', reason: gap });
      return result('skip', 0, reasons, [...gaps, gap], mustHaveCoverage);
    }
  }

  let score = 0;
  if (terms(profile.roleFamilies).includes(roleFamily)) { score += 25; reasons.push(`Role family: ${roleFamily}.`); }
  else gaps.push('Role family does not directly match the target.');
  score += 15;
  reasons.push(`Seniority: ${seniority}.`);
  score += Math.round(mustHaveCoverage * 0.4);
  reasons.push(`Skills evidence: ${mustHaveCoverage}% of must-haves.`);
  const locationMatches = matchesAny(locations, profile.targetLocations);
  if (locationMatches.length || workMode === 'remote') {
    score += 10;
    reasons.push(job.remote === true ? 'Remote-compatible.' : `Target location: ${locationMatches.join(', ')}.`);
  } else gaps.push('Location or work mode is not an explicit match.');
  const industryMatches = matchesAny(text, profile.industries ?? []);
  if (industryMatches.length) { score += 5; reasons.push(`Industry: ${industryMatches[0]}.`); }
  if (profile.compensationFloor && job.salaryMaximum != null && String(job.salaryCurrency ?? '').toUpperCase() === profile.compensationFloor.currency) {
    score += 5;
    reasons.push('Published compensation meets the configured floor.');
  } else gaps.push('Published compensation is unavailable or not directly comparable.');

  let experienceMismatch = false;
  if (job.experienceMin != null) integer(job.experienceMin, 'job.experienceMin', 0, 80);
  if (job.experienceMax != null) integer(job.experienceMax, 'job.experienceMax', 0, 80);
  if ((job.experienceMax != null && profile.yearsExperience > job.experienceMax + 2) || (job.experienceMin != null && profile.yearsExperience + 2 < job.experienceMin)) {
    experienceMismatch = true;
    score = Math.min(score, profile.autoSubmitMinScore - 1);
    gaps.push('Explicit experience range is materially misaligned.');
    gates.push({ name: 'experience', status: 'warn', reason: 'Experience mismatch requires manual review.' });
  }
  const finalScore = Math.min(score, 100);
  const decision = finalScore >= profile.manualReviewMinScore ? 'review' : 'skip';
  const autoEligible = decision === 'review' && ['senior', 'staff'].includes(seniority) && !experienceMismatch
    && finalScore >= profile.autoSubmitMinScore && mustHaveCoverage >= profile.minMustHaveCoverage;
  return result(decision, finalScore, reasons, gaps, mustHaveCoverage, autoEligible);
}

export function validateLedgerEntry(input) {
  const entry = object(input, 'entry');
  const normalized = {
    id: string(entry.id, 'entry.id', 180),
    company: string(entry.company, 'entry.company', 300),
    role: string(entry.role, 'entry.role', 300),
    url: string(entry.url, 'entry.url', 2048),
    source: string(entry.source, 'entry.source', 40).toLowerCase(),
    score: entry.score,
    status: string(entry.status, 'entry.status', 40).toLowerCase(),
    submittedAt: string(entry.submittedAt, 'entry.submittedAt', 80),
    approval: string(entry.approval, 'entry.approval', 80),
    answers: entry.answers ?? {},
  };
  if (entry.employerJobId != null) normalized.employerJobId = string(entry.employerJobId, 'entry.employerJobId', 300);
  if (entry.discoverySource != null) normalized.discoverySource = string(entry.discoverySource, 'entry.discoverySource', 40).toLowerCase();
  if (entry.discoverySourceId != null) {
    normalized.discoverySourceId = knownDiscoverySourceId(entry.discoverySourceId, 'entry.discoverySourceId');
  }
  if (entry.applicationChannel != null) normalized.applicationChannel = string(entry.applicationChannel, 'entry.applicationChannel', 40).toLowerCase();
  if (entry.roundId != null) normalized.roundId = string(entry.roundId, 'entry.roundId', 180);
  if (!SOURCES.has(normalized.source)) throw new Error('entry.source is invalid.');
  if (normalized.discoverySource != null && !DISCOVERY_SOURCES.has(normalized.discoverySource)) throw new Error('entry.discoverySource is invalid.');
  if (normalized.applicationChannel != null && !SOURCES.has(normalized.applicationChannel)) throw new Error('entry.applicationChannel is invalid.');
  if (!Number.isInteger(normalized.score) || normalized.score < 0 || normalized.score > 100) throw new Error('entry.score must be an integer from 0 to 100.');
  if (normalized.status !== 'submitted') throw new Error('New ledger entries must have status submitted.');
  if (!APPROVALS.has(normalized.approval)) throw new Error('entry.approval is invalid.');
  if (Number.isNaN(Date.parse(normalized.submittedAt))) throw new Error('entry.submittedAt must be an ISO date.');
  object(normalized.answers, 'entry.answers');
  for (const [key, value] of Object.entries(normalized.answers)) {
    string(key, 'answer key', 200);
    string(value, `answer ${key}`, 5000);
  }
  return normalized;
}

export function validateSubmissionTelemetry(input) {
  if (input == null) return {};
  const value = object(input, 'entry.telemetry');
  const allowed = new Set(['durationBucket', 'fieldsFilled', 'shortAnswerCount', 'resumeUploaded']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown entry.telemetry property: ${key}.`);
  if (value.durationBucket != null && !TELEMETRY_DURATIONS.has(value.durationBucket)) throw new Error('entry.telemetry.durationBucket is invalid.');
  for (const [key, max] of [['fieldsFilled', 500], ['shortAnswerCount', 100]]) {
    if (value[key] != null && (!Number.isInteger(value[key]) || value[key] < 0 || value[key] > max)) throw new Error(`entry.telemetry.${key} must be an integer from 0 to ${max}.`);
  }
  if (value.resumeUploaded != null && typeof value.resumeUploaded !== 'boolean') throw new Error('entry.telemetry.resumeUploaded must be a Boolean.');
  return Object.fromEntries(Object.entries(value).filter(([, item]) => item != null));
}

function normalizedText(value) {
  return String(value ?? '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function comparableRoleTokens(value) {
  const normalized = normalizedText(value)
    .replace(/\bsr\b/g, 'senior')
    .replace(/\bjr\b/g, 'junior')
    .replace(/\bfull stack\b/g, 'fullstack')
    .replace(/\bfront end\b/g, 'frontend')
    .replace(/\bback end\b/g, 'backend');
  const ignored = new Set(['software', 'junior', 'mid', 'senior', 'staff', 'principal', 'lead', 'manager', 'director', 'founding']);
  return new Set(normalized.split(' ')
    .map((token) => token === 'developer' ? 'engineer' : token)
    .filter((token) => token && !ignored.has(token)));
}

function rolesLikelySame(left, right) {
  const leftTokens = comparableRoleTokens(left);
  const rightTokens = comparableRoleTokens(right);
  if (leftTokens.size === 0 || rightTokens.size === 0) return normalizedText(left) === normalizedText(right);
  const shared = [...leftTokens].filter((token) => rightTokens.has(token)).length;
  return shared / Math.min(leftTokens.size, rightTokens.size) >= 0.75;
}

function canonicalApplicationKey(entry, fallback = '') {
  if (entry.employerJobId) return `job:${normalizedText(entry.company)}:${String(entry.employerJobId).toLowerCase()}`;
  if (entry.company && entry.role) return `legacy-role:${normalizedText(entry.company)}:${normalizedText(entry.role)}`;
  if (entry.url) return `url:${normalizeUrl(entry.url)}`;
  return `id:${entry.id ?? fallback}`;
}

function businessDaysBetween(startValue, endValue) {
  const start = new Date(startValue);
  const end = new Date(endValue);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end <= start) return 0;
  let days = 0;
  for (const date = new Date(start); date < end; date.setUTCDate(date.getUTCDate() + 1)) {
    const weekday = date.getUTCDay();
    if (weekday !== 0 && weekday !== 6) days += 1;
  }
  return days;
}

export function buildReview(entries, outcomeEntries = [], acknowledgements = [], now = new Date()) {
  const submissions = entries.filter((entry) => !Number.isNaN(Date.parse(entry.submittedAt)));
  const explicitOutcomes = outcomeEntries.length > 0;
  const outcomes = explicitOutcomes ? outcomeEntries : entries.filter((entry) => ['interview', 'rejected', 'offer', 'withdrawn'].includes(entry.status));
  const groups = new Map();
  submissions.forEach((entry, index) => {
    const key = canonicalApplicationKey(entry, String(index));
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(entry);
  });
  const canonical = [...groups.values()].map((group) => [...group].sort((a, b) => Date.parse(a.submittedAt) - Date.parse(b.submittedAt))[0]);
  const outcomesById = new Map();
  for (const outcome of outcomes) {
    if (!outcomesById.has(outcome.id)) outcomesById.set(outcome.id, []);
    outcomesById.get(outcome.id).push(outcome);
  }
  const canonicalOutcomes = [];
  const matureCanonicalOutcomes = [];
  const canonicalInterviewDetails = [];
  for (const group of groups.values()) {
    const candidates = explicitOutcomes
      ? group.flatMap((entry) => outcomesById.get(entry.id) ?? [])
      : group.filter((entry) => ['interview', 'rejected', 'offer', 'withdrawn'].includes(entry.status));
    if (candidates.length) {
      const ordered = [...candidates].sort((a, b) => (Date.parse(b.occurredAt ?? 0) || 0) - (Date.parse(a.occurredAt ?? 0) || 0));
      const latest = ordered[0];
      const canonicalApplication = [...group].sort((a, b) => Date.parse(a.submittedAt) - Date.parse(b.submittedAt))[0];
      canonicalOutcomes.push(latest);
      const latestInterviewDetail = ordered.find((entry) => entry.interviewQuality);
      if (latestInterviewDetail) canonicalInterviewDetails.push({
        ...latestInterviewDetail,
        source: canonicalApplication.source,
        score: canonicalApplication.score,
      });
      if (businessDaysBetween(canonicalApplication.submittedAt, now) >= 10) matureCanonicalOutcomes.push(latest);
    }
  }
  const maturedApplications = canonical.filter((entry) => businessDaysBetween(entry.submittedAt, now) >= 10).length;
  const lastAck = acknowledgements.length ? acknowledgements[acknowledgements.length - 1] : {};
  const submittedSinceLastReview = Math.max(0, canonical.length - (lastAck.uniqueSubmissionCount ?? 0));
  const hygieneDue = submittedSinceLastReview >= 10;
  const outcomeDue = maturedApplications - (lastAck.maturedApplicationCount ?? 0) >= 20;
  const reviewReasons = [...(hygieneDue ? ['submission-hygiene'] : []), ...(outcomeDue ? ['outcome-effectiveness'] : [])];
  const outcomeCounts = Object.fromEntries(['interview', 'rejected', 'offer', 'withdrawn'].map((status) => [status, canonicalOutcomes.filter((entry) => entry.status === status).length]));
  const matureOutcomeCounts = Object.fromEntries(['interview', 'rejected', 'offer', 'withdrawn'].map((status) => [status, matureCanonicalOutcomes.filter((entry) => entry.status === status).length]));
  const reasonCounts = {};
  for (const outcome of canonicalOutcomes) for (const reason of outcome.reasons ?? []) reasonCounts[reason.category] = (reasonCounts[reason.category] ?? 0) + 1;
  const interviewQualityCounts = Object.fromEntries([...INTERVIEW_QUALITIES].map((quality) => [quality, canonicalInterviewDetails.filter((entry) => entry.interviewQuality === quality).length]));
  const failurePointCounts = Object.fromEntries([...FAILURE_POINTS].map((point) => [point, canonicalInterviewDetails.filter((entry) => entry.failurePoint === point).length]));
  const interviewLearningSegmentCounts = new Map();
  for (const detail of canonicalInterviewDetails) {
    const score = Number(detail.score);
    const lower = Number.isFinite(score) ? Math.floor(Math.max(0, Math.min(100, score)) / 10) * 10 : null;
    const fitScoreBand = lower == null ? 'unknown' : `${lower}-${Math.min(100, lower + 9)}`;
    const segment = {
      source: detail.source ?? 'other',
      fitScoreBand,
      interviewQuality: detail.interviewQuality,
      failurePoint: detail.failurePoint ?? 'unknown',
    };
    const key = JSON.stringify(segment);
    interviewLearningSegmentCounts.set(key, (interviewLearningSegmentCounts.get(key) ?? 0) + 1);
  }
  const interviewLearningSegments = [...interviewLearningSegmentCounts.entries()]
    .map(([key, count]) => ({ ...JSON.parse(key), count }))
    .sort((a, b) => a.source.localeCompare(b.source) || a.fitScoreBand.localeCompare(b.fitScoreBand) || a.interviewQuality.localeCompare(b.interviewQuality) || a.failurePoint.localeCompare(b.failurePoint));
  const rate = (count) => maturedApplications ? Math.round((1000 * count) / maturedApplications) / 10 : 0;
  return {
    reviewDue: reviewReasons.length > 0,
    reviewReasons,
    submittedTotal: canonical.length,
    uniqueSubmittedTotal: canonical.length,
    rawSubmissionRows: submissions.length,
    duplicateSubmissionRows: submissions.length - canonical.length,
    submittedSinceLastReview,
    maturedApplications,
    outcomeCounts,
    matureOutcomeCounts,
    reasonCounts,
    interviewQualityCounts,
    failurePointCounts,
    interviewLearningSegments,
    conversionRates: Object.fromEntries(Object.entries(matureOutcomeCounts).map(([status, count]) => [status, rate(count)])),
    autoAppliedChanges: false,
    nextStep: reviewReasons.length
      ? 'Propose evidence-based targeting and answer-guidance changes for candidate approval.'
      : 'Continue recording confirmed submissions and outcomes.',
  };
}

function storedProfileRaw() {
  try { return object(JSON.parse(secretStore.readProfile()), 'profile'); } catch (error) {
    if (/missing or unreadable|requires macOS or Windows|could not store|Windows profile storage/i.test(error.message)) throw error;
    throw new Error('The stored profile is missing or unreadable. Run profile set again.');
  }
}

function storedProfile() {
  try { return validateProfile(storedProfileRaw()); } catch (error) {
    if (/requires macOS or Windows/i.test(error.message)) throw error;
    throw new Error('The stored profile needs migration. Run profile check, then profile migrate --stdin.');
  }
}

async function ensureStateDir() {
  const dir = stateDir();
  await migrateLegacyStateDir(dir);
  await mkdir(dir, { recursive: true, mode: 0o700 });
  await chmod(dir, 0o700);
  return dir;
}

async function stdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString('utf8');
}

async function jsonStdin() {
  try { return JSON.parse(await stdin()); } catch { throw new Error('Expected one JSON object on standard input.'); }
}

async function jsonLines(file) {
  try {
    return (await readFile(file, 'utf8')).split('\n').filter(Boolean).map((line, index) => {
      try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON on line ${index + 1} of ${basename(file)}.`); }
    });
  } catch (error) {
    if (error.code === 'ENOENT') return [];
    throw error;
  }
}

async function sourceCatalog() {
  return SOURCE_CATALOG;
}

export async function sourcesList(filtersInput = {}, communitySources = []) {
  const filters = object(filtersInput, 'source filters');
  const allowed = new Set(['regions', 'roleFamilies', 'kinds', 'requiresSession']);
  for (const key of Object.keys(filters)) if (!allowed.has(key)) throw new Error(`Unknown source filter: ${key}.`);
  const regions = filters.regions == null ? [] : terms(stringArray(filters.regions, 'source filters.regions'));
  const roleFamilies = filters.roleFamilies == null ? [] : terms(stringArray(filters.roleFamilies, 'source filters.roleFamilies'));
  const kinds = filters.kinds == null ? [] : terms(stringArray(filters.kinds, 'source filters.kinds'));
  if (filters.requiresSession != null && typeof filters.requiresSession !== 'boolean') throw new Error('source filters.requiresSession must be a Boolean.');
  const community = communitySources.map((source) => ({
    id: source.sourceId,
    communitySourceId: source.sourceId,
    name: source.name,
    kind: source.kind,
    jobsUrl: source.baseUrl,
    regions: source.regions,
    roleFamilies: source.roleFamilies,
    requiresSession: source.requiresSession,
    access: 'community',
    verification: 'direct-employer-or-ats',
    registryStatus: source.registryStatus,
    contributionCount: source.contributionCount,
  }));
  const sources = [...await sourceCatalog(), ...community].filter((source) => {
    if (regions.length && !source.regions.some((value) => regions.includes(value))) return false;
    if (roleFamilies.length && !source.roleFamilies.some((value) => roleFamilies.includes(value))) return false;
    if (kinds.length && !kinds.includes(source.kind)) return false;
    if (filters.requiresSession != null && source.requiresSession !== filters.requiresSession) return false;
    return true;
  });
  return { version: 1, count: sources.length, sources };
}

function sourceSuggestion(input) {
  const value = normalizeCommunitySource(input);
  return {
    type: 'suggested',
    id: `source-suggestion-${randomUUID()}`,
    ...value,
    createdAt: new Date().toISOString(),
  };
}

function shareableSuggestion(suggestion) {
  return Object.fromEntries(['name', 'baseUrl', 'kind', 'regions', 'roleFamilies', 'requiresSession'].map((key) => [key, suggestion[key]]));
}

async function markSourceShared(suggestionId, contribution) {
  if (!contribution.shared) return;
  await appendPrivateEvent('source-contribution-receipts', { suggestionId, sourceId: contribution.sourceId, sharedAt: new Date().toISOString() });
}

async function sourcesSuggest(input, community) {
  const suggestion = sourceSuggestion(input);
  await appendPrivateEvent('source-suggestions', suggestion);
  const contribution = await community.contribute(shareableSuggestion(suggestion));
  await markSourceShared(suggestion.id, contribution);
  return { queued: true, community: contribution, suggestion };
}

async function sourcesPending() {
  const suggestions = await jsonLines(join(await ensureStateDir(), 'source-suggestions.ndjson'));
  const receipts = await jsonLines(join(await ensureStateDir(), 'source-contribution-receipts.ndjson'));
  const shared = new Set(receipts.map((receipt) => receipt.suggestionId));
  const pending = suggestions.filter((suggestion) => !shared.has(suggestion.id));
  return { scope: 'local-unsent', count: pending.length, suggestions: pending };
}

async function communityPendingStatus() {
  return { ...await sourcesPending(), communityJobs: await communityJobsPending() };
}

export async function sourcesSync(community, limit = 10) {
  const pending = (await sourcesPending()).suggestions.slice(0, limit);
  let shared = 0;
  let attempted = 0;
  for (const suggestion of pending) {
    attempted += 1;
    const contribution = await community.contribute(shareableSuggestion(suggestion));
    await markSourceShared(suggestion.id, contribution);
    if (contribution.shared) shared += 1;
    else if (contribution.reason === 'disabled' || contribution.reason === 'unavailable') break;
  }
  return { attempted, shared, remaining: (await sourcesPending()).count };
}

function shareableLedgerJob(entry) {
  return normalizeCommunityJob({
    url: entry.url,
    company: entry.company,
    role: entry.role,
    applicationChannel: entry.applicationChannel ?? entry.source,
    ...(entry.discoverySource == null ? {} : { discoverySource: entry.discoverySource }),
  });
}

async function markCommunityJobShared(applicationId, contribution) {
  if (!contribution.shared) return;
  await appendPrivateEvent('community-job-contribution-receipts', {
    applicationId,
    jobId: contribution.jobId,
    sharedAt: new Date().toISOString(),
  });
}

export async function communityJobsPending() {
  const directory = await ensureStateDir();
  const applications = await jsonLines(join(directory, 'applications.ndjson'));
  const receipts = await jsonLines(join(directory, 'community-job-contribution-receipts.ndjson'));
  const shared = new Set(receipts.map((receipt) => receipt.applicationId));
  const pending = [];
  let unshareable = 0;
  for (const entry of applications) {
    if (shared.has(entry.id)) continue;
    try {
      pending.push({ applicationId: entry.id, job: shareableLedgerJob(entry) });
    } catch {
      unshareable += 1;
    }
  }
  return { count: pending.length, unshareable, applications: pending };
}

export async function communityJobsSync(community, { limit = 10, applicationIds = null } = {}) {
  if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('Community job sync limit must be between 1 and 100.');
  const selected = applicationIds == null ? null : new Set(applicationIds);
  const state = await communityJobsPending();
  const pending = state.applications.filter((entry) => selected == null || selected.has(entry.applicationId)).slice(0, limit);
  let attempted = 0;
  let shared = 0;
  for (const entry of pending) {
    attempted += 1;
    const contribution = await community.contributeJob(entry.job);
    await markCommunityJobShared(entry.applicationId, contribution);
    if (contribution.shared) shared += 1;
    else if (contribution.reason === 'disabled' || contribution.reason === 'unavailable' || contribution.reason === 'grace') break;
  }
  const remaining = await communityJobsPending();
  return { attempted, shared, remaining: remaining.count, unshareable: remaining.unshareable };
}

async function syncAllCommunityData(community) {
  const sources = await sourcesSync(community);
  return {
    ...sources,
    communityJobs: await communityJobsSync(community),
  };
}

async function withStateLock(name, action) {
  const dir = await ensureStateDir();
  const lockPath = join(dir, `.${name}.lock`);
  let handle;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      handle = await open(lockPath, 'wx', 0o600);
      break;
    } catch (error) {
      if (error.code !== 'EEXIST') throw error;
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 10));
    }
  }
  if (!handle) throw new Error(`Could not acquire ${name} ledger lock.`);
  try { return await action(dir); }
  finally {
    await handle.close();
    await unlink(lockPath).catch((error) => { if (error.code !== 'ENOENT') throw error; });
  }
}

async function writePrivateJson(file, value) {
  const temporary = `${file}.${process.pid}.${randomUUID()}.tmp`;
  await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  await rename(temporary, file);
  await chmod(file, 0o600);
}

async function readPrivateJson(file, fallback) {
  try { return JSON.parse(await readFile(file, 'utf8')); }
  catch (error) {
    if (error.code === 'ENOENT') return fallback;
    throw new Error(`${basename(file)} is missing or unreadable.`);
  }
}

function autonomyView(value) {
  const enabled = value?.enabled === true && value?.mode === 'routine-auto';
  return {
    version: 1,
    enabled,
    mode: enabled ? 'routine-auto' : null,
    scopes: enabled ? [...AUTONOMY_SCOPES] : [],
    hardStops: [...AUTONOMY_HARD_STOPS],
    maySubmitRoutineApplications: enabled,
    maySendVerifiedRecruitingEmail: enabled,
    mayCreateImprovementPr: enabled,
    mayMergeReleaseOrPublish: false,
    mayBypassHostPermissionPrompts: false,
    ...(value?.grantedAt ? { grantedAt: value.grantedAt } : {}),
    ...(value?.revokedAt ? { revokedAt: value.revokedAt } : {}),
  };
}

async function autonomyStatus() {
  const file = join(await ensureStateDir(), 'autonomy.json');
  return autonomyView(await readPrivateJson(file, { version: 1, enabled: false }));
}

async function autonomyGrant(input) {
  const value = object(input, 'autonomy grant');
  const allowed = new Set(['mode']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown autonomy grant property: ${key}.`);
  if (value.mode !== 'routine-auto') throw new Error('autonomy grant mode must be routine-auto.');
  const grant = { version: 1, enabled: true, mode: 'routine-auto', scopes: [...AUTONOMY_SCOPES], grantedAt: new Date().toISOString() };
  const file = join(await ensureStateDir(), 'autonomy.json');
  await writePrivateJson(file, grant);
  return autonomyView(grant);
}

async function autonomyRevoke() {
  const file = join(await ensureStateDir(), 'autonomy.json');
  const current = await readPrivateJson(file, { version: 1, enabled: false });
  const revoked = { version: 1, enabled: false, revokedAt: new Date().toISOString(), ...(current.grantedAt ? { grantedAt: current.grantedAt } : {}) };
  await writePrivateJson(file, revoked);
  return autonomyView(revoked);
}

async function storeProfile(profileInput) {
  const profile = validateProfile(profileInput);
  if (process.platform === 'win32') await ensureStateDir();
  secretStore.writeProfile(JSON.stringify(profile));
  return profile;
}

async function profileSet(profileInput) {
  const profile = await storeProfile(profileInput);
  return { stored: true, fields: Object.keys(profile).sort() };
}

async function profileMigrate(overrides) {
  const before = storedProfileRaw();
  const profile = migrateProfile(before, overrides);
  await storeProfile(profile);
  return {
    migrated: true,
    fields: Object.keys(profile).sort(),
    addedFields: Object.keys(profile).filter((field) => !(field in before)).sort(),
    mappedLegacyFields: before.salaryPreference != null && profile.targetCompensation != null ? ['salaryPreference'] : [],
  };
}

async function importResume(source) {
  let bytes;
  let sourceLabel;
  if (/^https:\/\/docs\.google\.com\/document\/d\//i.test(source)) {
    const match = new URL(source).pathname.match(/^\/document\/d\/([A-Za-z0-9_-]+)/);
    if (!match) throw new Error('Invalid Google Docs resume URL.');
    const exportUrl = `https://docs.google.com/document/d/${match[1]}/export?format=pdf`;
    const response = await fetch(exportUrl, { redirect: 'follow' });
    if (!response.ok) throw new Error(`Resume export failed with HTTP ${response.status}.`);
    bytes = Buffer.from(await response.arrayBuffer());
    sourceLabel = source;
  } else {
    const local = resolve(source);
    if (!local.toLowerCase().endsWith('.pdf')) throw new Error('Local resume must be a PDF.');
    bytes = await readFile(local);
    sourceLabel = local;
  }
  if (bytes.length < 1000 || !bytes.subarray(0, 4).equals(Buffer.from('%PDF'))) throw new Error('Resume source did not contain a valid PDF.');
  const dir = await ensureStateDir();
  const temporary = join(dir, `resume-${process.pid}.pdf`);
  const target = join(dir, 'resume.pdf');
  await writeFile(temporary, bytes, { mode: 0o600 });
  await rename(temporary, target);
  await chmod(target, 0o600);
  const metadata = { source: sourceLabel, importedAt: new Date().toISOString(), sha256: createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length };
  await writeFile(join(dir, 'resume.json'), `${JSON.stringify(metadata, null, 2)}\n`, { mode: 0o600 });
  return { path: target, sha256: metadata.sha256, bytes: metadata.bytes };
}

async function canonicalResumePath() {
  const target = join(await ensureStateDir(), 'resume.pdf');
  try {
    const details = await stat(target);
    if (!details.isFile()) throw new Error('Canonical resume path is not a file. Import the resume again.');
  } catch (error) {
    if (error.code === 'ENOENT') throw new Error('Canonical resume is not imported. Run resume import first.');
    throw error;
  }
  return { path: target };
}

function duplicateResult(entries, candidate, outcomes = [], now = new Date()) {
  const candidateCompany = normalizedText(candidate.company);
  const candidateRole = normalizedText(candidate.role);
  const candidateUrl = normalizeUrl(candidate.url);
  const sameCompanyRole = (entry) => candidateCompany && candidateRole
    && normalizedText(entry.company) === candidateCompany
    && rolesLikelySame(entry.role, candidate.role);
  const hardId = entries.find((entry) => entry.id === candidate.id);
  const hardEmployerJobId = entries.find((entry) => candidate.employerJobId && entry.employerJobId
    && normalizedText(entry.company) === candidateCompany
    && entry.employerJobId.toLowerCase() === String(candidate.employerJobId).toLowerCase());
  const hardUrl = entries.find((entry) => normalizeUrl(entry.url) === candidateUrl);
  const hard = hardId ?? hardEmployerJobId ?? hardUrl;
  const hardReason = hardId ? 'id' : hardEmployerJobId ? 'employer-job-id' : hardUrl ? 'url' : null;
  const possible = hard ? null : entries.find(sameCompanyRole);
  const match = hard ?? possible;
  const sameCompanyEntries = candidateCompany
    ? entries.filter((entry) => normalizedText(entry.company) === candidateCompany)
    : [];
  const companyApplications = sameCompanyEntries.slice(-20).map((entry) => ({
      id: entry.id,
      company: entry.company,
      role: entry.role,
      submittedAt: entry.submittedAt,
      ...(entry.employerJobId ? { employerJobId: entry.employerJobId } : {}),
    }));
  const latestCompanyApplication = [...sameCompanyEntries]
    .filter((entry) => !Number.isNaN(Date.parse(entry.submittedAt)))
    .sort((left, right) => Date.parse(right.submittedAt) - Date.parse(left.submittedAt))[0] ?? null;
  const daysSinceLatest = latestCompanyApplication
    ? Math.max(0, Math.floor((now.getTime() - Date.parse(latestCompanyApplication.submittedAt)) / 86_400_000))
    : null;
  const hasFollowUp = latestCompanyApplication
    ? outcomes.some((outcome) => outcome.id === latestCompanyApplication.id)
    : false;
  let companyReapplyDecision = 'fresh-company';
  if (hard) companyReapplyDecision = 'hard-duplicate';
  else if (possible) companyReapplyDecision = 'same-role-review';
  else if (latestCompanyApplication && hasFollowUp) companyReapplyDecision = 'follow-up-present';
  else if (latestCompanyApplication && daysSinceLatest < COMPANY_REAPPLY_COOLDOWN_DAYS) companyReapplyDecision = 'cooldown-active';
  else if (latestCompanyApplication) companyReapplyDecision = 'eligible-after-cooldown';
  return {
    duplicate: Boolean(hard),
    possibleDuplicate: Boolean(possible),
    reason: hardReason ?? (possible ? 'company-role' : null),
    match: match ? { id: match.id, company: match.company, role: match.role, submittedAt: match.submittedAt } : null,
    sameCompany: companyApplications.length > 0,
    companyApplications,
    companyReapply: {
      eligible: companyReapplyDecision === 'eligible-after-cooldown',
      decision: companyReapplyDecision,
      cooldownDays: COMPANY_REAPPLY_COOLDOWN_DAYS,
      latestSubmittedAt: latestCompanyApplication?.submittedAt ?? null,
      daysSinceLatest,
      hasFollowUp,
    },
  };
}

async function ledgerCheck(candidate) {
  object(candidate, 'candidate');
  const dir = await ensureStateDir();
  const entries = await jsonLines(join(dir, 'applications.ndjson'));
  const outcomes = await jsonLines(join(dir, 'outcomes.ndjson'));
  string(candidate.url, 'candidate.url', 2048);
  return duplicateResult(entries, candidate, outcomes);
}

async function ledgerAdd(entryInput, duplicateOverride, companyReapplyOverride) {
  const entry = validateLedgerEntry(entryInput);
  return withStateLock('applications', async (dir) => {
    const file = join(dir, 'applications.ndjson');
    const entries = await jsonLines(file);
    const outcomes = await jsonLines(join(dir, 'outcomes.ndjson'));
    if (entry.roundId) {
      const roundEvents = await jsonLines(join(dir, 'rounds.ndjson'));
      if (!roundEvents.some((event) => event.type === 'started' && event.roundId === entry.roundId)) throw new Error('entry.roundId does not identify a started round.');
      if (roundEvents.some((event) => event.type === 'completed' && event.roundId === entry.roundId)) throw new Error('entry.roundId identifies a completed round.');
    }
    const duplicate = duplicateResult(entries, entry, outcomes);
    if (duplicate.duplicate) throw new Error(`Hard duplicate blocked: matching ${duplicate.reason === 'employer-job-id' ? 'employer job ID or requisition' : duplicate.reason === 'url' ? 'canonical URL' : 'ledger ID'}.`);
    if (duplicate.possibleDuplicate && duplicateOverride !== 'NEW REQUISITION CONFIRMED') throw new Error('A possible same-company role duplicate requires NEW REQUISITION CONFIRMED.');
    if (!duplicate.possibleDuplicate && duplicate.companyReapply.decision === 'cooldown-active' && companyReapplyOverride !== COMPANY_REAPPLY_OVERRIDE) {
      throw new Error(`Company reapplication cooldown is active for ${COMPANY_REAPPLY_COOLDOWN_DAYS} full days; use ${COMPANY_REAPPLY_OVERRIDE} only with explicit candidate approval.`);
    }
    if (!duplicate.possibleDuplicate && duplicate.companyReapply.decision === 'follow-up-present' && companyReapplyOverride !== COMPANY_REAPPLY_OVERRIDE) {
      throw new Error(`Company reapplication blocked because the latest application has a recorded follow-up; use ${COMPANY_REAPPLY_OVERRIDE} only with explicit candidate approval.`);
    }
    const storedEntry = ['cooldown-active', 'follow-up-present'].includes(duplicate.companyReapply.decision)
      ? { ...entry, reapplicationApproval: 'candidate-explicit' }
      : entry;
    await appendFile(file, `${JSON.stringify(storedEntry)}\n`, { mode: 0o600 });
    await chmod(file, 0o600);
    if (entry.roundId) {
      const roundsFile = join(dir, 'rounds.ndjson');
      await appendFile(roundsFile, `${JSON.stringify({ type: 'submission-confirmed', roundId: entry.roundId, applicationId: entry.id, occurredAt: entry.submittedAt })}\n`, { mode: 0o600 });
      await chmod(roundsFile, 0o600);
    }
    return { recorded: storedEntry.id, review: buildReview([...entries, storedEntry]) };
  });
}

async function appendPrivateEvent(name, event) {
  return withStateLock(name, async (dir) => {
    const file = join(dir, `${name}.ndjson`);
    await appendFile(file, `${JSON.stringify(event)}\n`, { mode: 0o600 });
    await chmod(file, 0o600);
    return event;
  });
}

function isoDate(value, label) {
  const result = string(value ?? new Date().toISOString(), label, 80);
  if (Number.isNaN(Date.parse(result))) throw new Error(`${label} must be an ISO date.`);
  return result;
}

async function roundStart(input) {
  const value = object(input, 'round');
  const allowed = new Set(['requestedCount', 'startedAt']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown round property: ${key}.`);
  const event = {
    type: 'started',
    roundId: `round-${new Date().toISOString().slice(0, 10)}-${randomUUID()}`,
    requestedCount: integer(value.requestedCount, 'round.requestedCount', 1, 1000),
    occurredAt: isoDate(value.startedAt, 'round.startedAt'),
  };
  await appendPrivateEvent('rounds', event);
  return { roundId: event.roundId, requestedCount: event.requestedCount, startedAt: event.occurredAt, completed: false };
}

function replayAttention(events, roundId = null) {
  const active = new Map();
  for (const event of events) {
    if (event.type === 'opened') active.set(event.id, event);
    else if (event.type === 'resolved') active.delete(event.id);
  }
  const priority = (blocker) => {
    if (['authentication', 'mfa', 'captcha'].includes(blocker)) return 0;
    if (['legal-attestation', 'ambiguous-authorization', 'ambiguous-compensation'].includes(blocker)) return 1;
    return 2;
  };
  return [...active.values()]
    .filter((item) => roundId == null || item.roundId === roundId)
    .sort((a, b) => priority(a.blocker) - priority(b.blocker) || Date.parse(a.createdAt) - Date.parse(b.createdAt));
}

async function attentionList(roundId = null) {
  const events = await jsonLines(join(await ensureStateDir(), 'attention.ndjson'));
  const items = replayAttention(events, roundId);
  return { count: items.length, items };
}

async function attentionAdd(input) {
  const value = object(input, 'attention item');
  const allowed = new Set(['roundId', 'applicationId', 'url', 'stage', 'blocker', 'requiredActions', 'createdAt']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown attention property: ${key}.`);
  const stage = string(value.stage, 'attention.stage', 40).toLowerCase();
  const blocker = string(value.blocker, 'attention.blocker', 60).toLowerCase();
  if (!ATTENTION_STAGES.has(stage)) throw new Error('attention.stage is invalid.');
  if (!ATTENTION_BLOCKERS.has(blocker)) throw new Error('attention.blocker is invalid.');
  const requiredActions = stringArray(value.requiredActions, 'attention.requiredActions', true).map((item) => item.toLowerCase());
  if (requiredActions.length > 8 || requiredActions.some((item) => !REQUIRED_ACTIONS.has(item))) throw new Error('attention.requiredActions must contain only documented actions.');
  const event = {
    type: 'opened',
    id: `attention-${randomUUID()}`,
    roundId: string(value.roundId, 'attention.roundId', 180),
    applicationId: string(value.applicationId, 'attention.applicationId', 180),
    url: string(value.url, 'attention.url', 2048),
    stage,
    blocker,
    requiredActions: [...new Set(requiredActions)],
    createdAt: isoDate(value.createdAt, 'attention.createdAt'),
  };
  await appendPrivateEvent('attention', event);
  return event;
}

async function attentionResolve(input) {
  const value = object(input, 'attention resolution');
  const allowed = new Set(['id', 'resolvedAt']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown attention resolution property: ${key}.`);
  const id = string(value.id, 'attention.id', 180);
  const current = await attentionList();
  if (!current.items.some((item) => item.id === id)) throw new Error('Attention item is not active.');
  const event = { type: 'resolved', id, resolvedAt: isoDate(value.resolvedAt, 'attention.resolvedAt') };
  await appendPrivateEvent('attention', event);
  return { resolved: id };
}

async function roundStatus(roundId = null) {
  const dir = await ensureStateDir();
  const events = await jsonLines(join(dir, 'rounds.ndjson'));
  const starts = events.filter((event) => event.type === 'started');
  const id = roundId ?? starts.at(-1)?.roundId;
  if (!id) throw new Error('No application round has been started.');
  const started = starts.find((event) => event.roundId === id);
  if (!started) throw new Error('Application round was not found.');
  const applications = (await jsonLines(join(dir, 'applications.ndjson'))).filter((entry) => entry.roundId === id && entry.status === 'submitted');
  const confirmedCount = new Set(applications.map((entry, index) => canonicalApplicationKey(entry, String(index)))).size;
  const attention = await attentionList(id);
  const completion = events.find((event) => event.type === 'completed' && event.roundId === id);
  return {
    roundId: id,
    requestedCount: started.requestedCount,
    confirmedCount,
    remainingCount: Math.max(0, started.requestedCount - confirmedCount),
    blockedCount: attention.count,
    completed: Boolean(completion),
    startedAt: started.occurredAt,
    ...(completion ? { completedAt: completion.occurredAt } : {}),
  };
}

async function roundComplete(input) {
  const value = object(input, 'round completion');
  const allowed = new Set(['roundId', 'completedAt']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown round completion property: ${key}.`);
  const status = await roundStatus(string(value.roundId, 'round.roundId', 180));
  if (status.completed) return status;
  if (status.confirmedCount < status.requestedCount) throw new Error(`Round requires ${status.requestedCount} confirmed submissions before completion.`);
  const event = { type: 'completed', roundId: status.roundId, occurredAt: isoDate(value.completedAt, 'round.completedAt') };
  await appendPrivateEvent('rounds', event);
  return { ...status, completed: true, completedAt: event.occurredAt };
}

async function frictionRecord(input) {
  const value = object(input, 'friction event');
  const allowed = new Set(['stage', 'ats', 'errorCode', 'reproducible', 'general', 'observedAt']);
  for (const key of Object.keys(value)) if (!allowed.has(key)) throw new Error(`Unknown friction property: ${key}.`);
  const stage = string(value.stage, 'friction.stage', 40).toLowerCase();
  const ats = string(value.ats, 'friction.ats', 40).toLowerCase();
  const errorCode = string(value.errorCode, 'friction.errorCode', 100).toLowerCase();
  if (!ATTENTION_STAGES.has(stage)) throw new Error('friction.stage is invalid.');
  if (!SOURCES.has(ats)) throw new Error('friction.ats is invalid.');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(errorCode)) throw new Error('friction.errorCode must be a stable kebab-case code.');
  if (typeof value.reproducible !== 'boolean' || typeof value.general !== 'boolean') throw new Error('friction.reproducible and friction.general must be Booleans.');
  const event = {
    id: `friction-${randomUUID()}`,
    type: 'observed',
    stage,
    ats,
    errorCode,
    reproducible: value.reproducible,
    general: value.general,
    qualifiesForPr: value.reproducible && value.general,
    observedAt: isoDate(value.observedAt, 'friction.observedAt'),
  };
  await appendPrivateEvent('friction', event);
  return event;
}

async function frictionList() {
  const items = (await jsonLines(join(await ensureStateDir(), 'friction.ndjson'))).filter((event) => event.type === 'observed');
  return { count: items.length, items, prCandidates: items.filter((item) => item.qualifiesForPr) };
}

async function ledgerOutcome(outcomeInput) {
  const input = object(outcomeInput, 'outcome');
  const allowed = new Set(['id', 'status', 'occurredAt', 'note', 'reasons', 'interviewQuality', 'failurePoint']);
  for (const key of Object.keys(input)) if (!allowed.has(key)) throw new Error(`Unknown outcome property: ${key}.`);
  const status = string(input.status, 'outcome.status', 40).toLowerCase();
  if (!['interview', 'rejected', 'offer', 'withdrawn'].includes(status)) throw new Error('Invalid outcome status.');
  const occurredAt = string(input.occurredAt ?? new Date().toISOString(), 'outcome.occurredAt', 80);
  if (Number.isNaN(Date.parse(occurredAt))) throw new Error('outcome.occurredAt must be an ISO date.');
  const reasonCategories = new Set(['eligibility', 'closed-stale', 'level-compensation', 'must-have-gap', 'generic-resume-screen', 'interview-stage', 'unknown']);
  const evidenceLevels = new Set(['explicit', 'inferred']);
  const reasons = input.reasons == null ? [] : input.reasons.map((item, index) => {
    const reason = object(item, `outcome.reasons[${index}]`);
    const category = string(reason.category, `outcome.reasons[${index}].category`, 80);
    const evidence = string(reason.evidence, `outcome.reasons[${index}].evidence`, 40);
    if (!reasonCategories.has(category)) throw new Error(`outcome.reasons[${index}].category is invalid.`);
    if (!evidenceLevels.has(evidence)) throw new Error(`outcome.reasons[${index}].evidence is invalid.`);
    return { category, evidence };
  });
  const interviewQuality = input.interviewQuality == null ? null : string(input.interviewQuality, 'outcome.interviewQuality', 40).toLowerCase();
  if (interviewQuality != null && !INTERVIEW_QUALITIES.has(interviewQuality)) throw new Error('outcome.interviewQuality is invalid.');
  const failurePoint = input.failurePoint == null ? null : string(input.failurePoint, 'outcome.failurePoint', 40).toLowerCase();
  if (failurePoint != null && !FAILURE_POINTS.has(failurePoint)) throw new Error('outcome.failurePoint is invalid.');
  if (failurePoint != null && interviewQuality == null) throw new Error('outcome.failurePoint requires outcome.interviewQuality.');
  const event = {
    id: string(input.id, 'outcome.id', 180), status, occurredAt,
    ...(typeof input.note === 'string' ? { note: input.note.slice(0, 2000) } : {}),
    ...(reasons.length ? { reasons } : {}),
    ...(interviewQuality ? { interviewQuality } : {}),
    ...(failurePoint ? { failurePoint } : {}),
  };
  const storage = await withStateLock('outcomes', async (dir) => {
    const file = join(dir, 'outcomes.ndjson');
    const existing = await jsonLines(file);
    const sameOccurrence = existing.filter((item) => item.id === event.id && item.status === event.status && item.occurredAt === event.occurredAt);
    const detailKey = (item) => JSON.stringify({ reasons: item.reasons ?? [], interviewQuality: item.interviewQuality ?? null, failurePoint: item.failurePoint ?? null });
    const duplicate = sameOccurrence.some((item) => detailKey(item) === detailKey(event));
    if (duplicate) return { stored: false, enriched: false };
    const enriched = sameOccurrence.length > 0;
    await appendFile(file, `${JSON.stringify(event)}\n`, { mode: 0o600 });
    await chmod(file, 0o600);
    return { stored: true, enriched };
  });
  const applications = await jsonLines(join(await ensureStateDir(), 'applications.ndjson'));
  return { result: { recorded: storage.stored, duplicate: !storage.stored, enriched: storage.enriched, recordedOutcome: event.id, status }, application: applications.find((entry) => entry.id === event.id) ?? null, event };
}

async function ledgerReview() {
  const dir = await ensureStateDir();
  const applications = await jsonLines(join(dir, 'applications.ndjson'));
  const outcomes = await jsonLines(join(dir, 'outcomes.ndjson'));
  const acknowledgements = await jsonLines(join(dir, 'reviews.ndjson'));
  return buildReview(applications, outcomes, acknowledgements);
}

async function ledgerReviewAcknowledge(input) {
  const value = object(input, 'review acknowledgement');
  const reviewedAt = string(value.reviewedAt ?? new Date().toISOString(), 'reviewedAt', 80);
  if (Number.isNaN(Date.parse(reviewedAt))) throw new Error('reviewedAt must be an ISO date.');
  const review = await ledgerReview();
  const event = { reviewedAt, uniqueSubmissionCount: review.uniqueSubmittedTotal, maturedApplicationCount: review.maturedApplications };
  await withStateLock('reviews', async (dir) => {
    const file = join(dir, 'reviews.ndjson');
    await appendFile(file, `${JSON.stringify(event)}\n`, { mode: 0o600 });
    await chmod(file, 0o600);
  });
  return { acknowledged: true, ...event };
}

function print(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

async function outcomeTelemetry(application, outcome) {
  if (!application) return null;
  const identity = await jobIdentity(application.url);
  return {
    event: 'outcome_recorded',
    properties: {
      ...identity,
      company: application.company,
      title: application.role,
      ats: sourceToAts(application.applicationChannel ?? application.source),
      outcome: outcome.status,
      daysSinceSubmission: Math.max(0, Math.min(3650, Math.floor((Date.parse(outcome.occurredAt) - Date.parse(application.submittedAt)) / 86_400_000))),
      ...(outcome.interviewQuality ? { interviewQuality: outcome.interviewQuality } : {}),
      ...(outcome.failurePoint ? { failurePoint: outcome.failurePoint } : {}),
    },
  };
}

function reviewTelemetry(review) {
  return {
    event: 'review_generated',
    properties: {
      submissionCount: review.submittedTotal,
      interviewCount: review.outcomeCounts.interview,
      rejectionCount: review.outcomeCounts.rejected,
      offerCount: review.outcomeCounts.offer,
      withdrawalCount: review.outcomeCounts.withdrawn,
      reviewDue: review.reviewDue,
    },
  };
}

function roundCompletedTelemetry(round) {
  return {
    event: 'round_completed',
    properties: {
      requestedCount: round.requestedCount,
      submittedCount: round.confirmedCount,
      assessedCount: round.confirmedCount,
      skippedCount: 0,
      pausedCount: round.blockedCount,
      errorCount: 0,
      durationBucket: durationBucket(Math.max(0, Date.parse(round.completedAt) - Date.parse(round.startedAt))),
    },
  };
}

async function executeCommand([area, action, value], telemetry, session, community) {
  const domainEvents = [];
  let result;
  if (area === 'profile' && action === 'set' && value === '--stdin') {
    const profile = await jsonStdin();
    result = await profileSet(profile);
  } else if (area === 'profile' && action === 'migrate' && value === '--stdin') {
    result = await profileMigrate(await jsonStdin());
  } else if (area === 'profile' && action === 'check') {
    result = { ...profileStatus(storedProfileRaw()), required: REQUIRED_PROFILE };
  } else if (area === 'profile' && action === 'field' && value) {
    if (![...STRING_PROFILE_FIELDS, ...ARRAY_PROFILE_FIELDS, ...NUMBER_PROFILE_FIELDS, ...OBJECT_PROFILE_FIELDS].includes(value)) throw new Error('Profile field is not allowed.');
    result = { [value]: storedProfile()[value] ?? null };
  } else if (area === 'resume' && action === 'import' && value) result = await importResume(value);
  else if (area === 'resume' && action === 'path' && value == null) result = await canonicalResumePath();
  else if (area === 'score' && action === '--stdin') {
    const job = await jsonStdin();
    result = scoreJob(job, job.target ?? storedProfile());
    const event = await telemetryJobAssessed(job, result);
    if (event) domainEvents.push(event);
  } else if (area === 'ledger' && action === 'check' && value === '--stdin') result = await ledgerCheck(await jsonStdin());
  else if (area === 'ledger' && action === 'add' && value === '--stdin') {
    const input = await jsonStdin();
    const telemetryDetails = validateSubmissionTelemetry(input.telemetry);
    const entry = validateLedgerEntry(input);
    result = await ledgerAdd(entry, input.duplicateOverride, input.companyReapplyOverride);
    result.communityJob = await communityJobsSync(community, { limit: 1, applicationIds: [entry.id] });
    domainEvents.push(await telemetryApplicationSubmitted(entry, telemetryDetails));
  } else if (area === 'ledger' && action === 'outcome' && value === '--stdin') {
    const outcome = await ledgerOutcome(await jsonStdin());
    result = outcome.result;
    const event = outcome.result.recorded && !outcome.result.enriched ? await outcomeTelemetry(outcome.application, outcome.event) : null;
    if (event) domainEvents.push(event);
  } else if (area === 'ledger' && action === 'review') {
    result = await ledgerReview();
    domainEvents.push(reviewTelemetry(result));
  } else if (area === 'ledger' && action === 'review-ack' && value === '--stdin') {
    result = await ledgerReviewAcknowledge(await jsonStdin());
  } else if (area === 'autonomy' && action === 'grant' && value === '--stdin') result = await autonomyGrant(await jsonStdin());
  else if (area === 'autonomy' && action === 'status' && value == null) result = await autonomyStatus();
  else if (area === 'autonomy' && action === 'preview' && value == null) result = await autonomyStatus();
  else if (area === 'autonomy' && action === 'revoke' && value == null) result = await autonomyRevoke();
  else if (area === 'round' && action === 'start' && value === '--stdin') result = await roundStart(await jsonStdin());
  else if (area === 'round' && action === 'status') result = await roundStatus(value ?? null);
  else if (area === 'round' && action === 'complete' && value === '--stdin') {
    result = await roundComplete(await jsonStdin());
    domainEvents.push(roundCompletedTelemetry(result));
  } else if (area === 'sources' && action === 'list' && value == null) {
    await syncAllCommunityData(community);
    result = await sourcesList({}, await community.list());
  } else if (area === 'sources' && action === 'list' && value === '--stdin') {
    const filters = await jsonStdin();
    await syncAllCommunityData(community);
    result = await sourcesList(filters, await community.list());
  }
  else if (area === 'sources' && action === 'suggest' && value === '--stdin') result = await sourcesSuggest(await jsonStdin(), community);
  else if (area === 'sources' && action === 'pending' && value == null) result = await communityPendingStatus();
  else if (area === 'sources' && action === 'sync' && value == null) result = await syncAllCommunityData(community);
  else if (area === 'sources' && action === 'jobs' && value == null) result = await community.listJobs();
  else if (area === 'sources' && action === 'jobs' && value === '--stdin') result = await community.listJobs(await jsonStdin());
  else if (area === 'sources' && action === 'sharing' && ['status', 'enable', 'disable', 'reset'].includes(value)) {
    result = await community.configure(value);
    if (value === 'enable') result.communityJobs = await communityJobsSync(community);
  }
  else if (area === 'attention' && action === 'add' && value === '--stdin') result = await attentionAdd(await jsonStdin());
  else if (area === 'attention' && action === 'list' && value == null) result = await attentionList();
  else if (area === 'attention' && action === 'resolve' && value === '--stdin') result = await attentionResolve(await jsonStdin());
  else if (area === 'friction' && action === 'record' && value === '--stdin') result = await frictionRecord(await jsonStdin());
  else if (area === 'friction' && action === 'list' && value == null) result = await frictionList();
  else throw new Error('Usage: profile set|migrate --stdin; profile check|field <name>; resume import <url-or-pdf>|path; score --stdin; ledger check|add|outcome|review-ack --stdin; ledger review; autonomy grant --stdin|status|preview|revoke; round start|complete --stdin|status [round-id]; sources list [--stdin]|jobs [--stdin]|suggest --stdin|pending|sync|sharing status|enable|disable|reset; attention add|resolve --stdin|list; friction record --stdin|list; telemetry status|enable|disable|reset|preview --stdin|record --stdin');
  for (const event of domainEvents) await telemetry.record(event, session);
  return result;
}

async function recordInstallationStart(telemetry, session) {
  if (!session.installationEventPending) return;
  let submissionMode = 'unconfigured';
  try { submissionMode = storedProfile().submissionMode; } catch {}
  await telemetry.record({
    event: 'installation_started',
    properties: {
      osFamily: ({ darwin: 'macos', linux: 'linux', win32: 'windows' })[platform()] ?? 'other',
      nodeMajor: Number(process.versions.node.split('.')[0]),
      submissionMode,
    },
  }, session);
}

async function main(args) {
  const [area, action, value] = args;
  const telemetry = new TelemetryClient({ stateDir: stateDir() });
  const community = new SourceCommunityClient({ stateDir: stateDir() });
  if (area === 'telemetry') {
    if (['status', 'enable', 'disable', 'reset'].includes(action) && value == null) return print(await telemetry.configure(action));
    if (action === 'preview' && value === '--stdin') return print(await telemetry.preview(await jsonStdin()));
    if (action === 'record' && value === '--stdin') {
      const session = await telemetry.beginCommand('telemetry');
      await recordInstallationStart(telemetry, session);
      return print(await telemetry.record(await jsonStdin(), session, { strict: true }));
    }
    throw new Error('Usage: telemetry status|enable|disable|reset|preview --stdin|record --stdin');
  }

  const command = commandCategory(args);
  const session = await telemetry.beginCommand(command);
  await recordInstallationStart(telemetry, session);
  const started = Date.now();
  try {
    const result = await executeCommand(args, telemetry, session, community);
    if (!(area === 'sources' || (area === 'ledger' && action === 'add'))) await communityJobsSync(community).catch(() => null);
    await telemetry.record({ event: 'command_completed', properties: { command, result: 'success', durationBucket: durationBucket(Date.now() - started) } }, session);
    return print(result);
  } catch (error) {
    await telemetry.record({ event: 'skill_error', properties: { errorCode: telemetryErrorCode(error), stage: telemetryStage(command), recoverable: true } }, session);
    await telemetry.record({ event: 'command_completed', properties: { command, result: 'error', durationBucket: durationBucket(Date.now() - started) } }, session);
    throw error;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv.slice(2)).catch((error) => {
    process.stderr.write(`Error: ${error.message}\n`);
    process.exitCode = 1;
  });
}
