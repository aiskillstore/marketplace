#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

const PLANNER_SCHEMA = 'skillstore.pack-opportunity-plan/v1';
const BRIEF_SCHEMA = 'skillstore.pack-opportunity-brief/v1';
const PLAN_SCHEMA = 'pack-production-queue/v1';
const ADMISSION_SCHEMA = 'marketplace.pack-opportunity-admission/v1';
const ID = /^[a-z0-9][a-z0-9-]{0,79}$/;
const SHA256 = /^[0-9a-f]{64}$/;
const RUN_ID = /^[1-9][0-9]*$/;
const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const RFC3339_UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;

function fail(message) {
  throw new Error(message);
}

function object(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`);
  return value;
}

function exactKeys(value, keys, label) {
  const actual = Object.keys(object(value, label)).sort();
  if (actual.length !== keys.length || actual.some((key, index) => key !== keys[index])) {
    const missing = keys.filter((key) => !actual.includes(key));
    const extra = actual.filter((key) => !keys.includes(key));
    fail(`${label} fields differ (missing: ${missing.join(',') || 'none'}; extra: ${extra.join(',') || 'none'})`);
  }
}

function rejectionSummary(value) {
  const summary = object(value, 'rejectionSummary');
  exactKeys(summary, [
    'admitted', 'considered', 'cooldown', 'demandInsufficient', 'duplicate', 'rankingOnlySkills', 'supplyIncomplete', 'templateIncompatible',
  ], 'rejectionSummary');
  if (Object.values(summary).some((count) => !Number.isSafeInteger(count) || count < 0 || count > 1000)
    || ['admitted', 'cooldown', 'demandInsufficient', 'duplicate', 'supplyIncomplete', 'templateIncompatible']
      .some((key) => summary[key] > summary.considered)) {
    fail('rejectionSummary counts must be safe integers from 0 to 1000 and no greater than considered');
  }
  return summary;
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function digest(value) {
  return createHash('sha256').update(canonicalJson(value)).digest('hex');
}

function required(args, name) {
  const value = args[name];
  if (typeof value !== 'string' || value.length === 0) fail(`--${name} is required`);
  return value;
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const args = {};
  for (let index = 0; index < rest.length; index += 2) {
    const flag = rest[index];
    const value = rest[index + 1];
    if (!flag?.startsWith('--') || value == null) fail('expected --name value arguments');
    const name = flag.slice(2);
    if (args[name] !== undefined) fail(`duplicate --${name}`);
    args[name] = value;
  }
  return { command, args };
}

function projectBrief(value, label) {
  const brief = object(value, label);
  exactKeys(brief, [
    'admittedForGeneration', 'briefDigest', 'candidateSkills', 'canonicalIntent',
    'capabilitySlots', 'demandEvidence', 'duplicate', 'evaluationTemplateId', 'gap',
    'keywords', 'name', 'opportunityId', 'reasons', 'requiredArtifacts',
    'schemaVersion', 'score', 'slug', 'sourceEvidenceHash', 'task',
  ], label);
  if (brief.schemaVersion !== BRIEF_SCHEMA || !ID.test(brief.opportunityId || '')
    || !ID.test(brief.evaluationTemplateId || '') || !ID.test(brief.slug || '')) {
    fail(`${label} requires safe generation identities`);
  }
  if (brief.admittedForGeneration !== true) fail(`${label} must be admittedForGeneration`);
  if (!SHA256.test(brief.briefDigest || '') || !SHA256.test(brief.sourceEvidenceHash || '')) {
    fail(`${label} requires exact brief and source-evidence digests`);
  }
  if (typeof brief.task !== 'string' || !brief.task.trim() || typeof brief.name !== 'string' || !brief.name.trim()
    || !Array.isArray(brief.keywords) || brief.keywords.length < 1 || brief.keywords.length > 32) {
    fail(`${label} requires a bounded task, name, and keywords`);
  }
  if (!Array.isArray(brief.capabilitySlots) || brief.capabilitySlots.length < 1 || brief.capabilitySlots.length > 4) {
    fail(`${label} requires one to four capabilitySlots`);
  }
  if (!Array.isArray(brief.requiredArtifacts) || brief.requiredArtifacts.length < 1 || brief.requiredArtifacts.length > 12) {
    fail(`${label} requires requiredArtifacts`);
  }
  if ('generationId' in brief || 'workflowBinding' in brief) fail(`${label} must not pre-bind generation state`);
  if (!Array.isArray(brief.candidateSkills) || brief.candidateSkills.length < 2 || brief.candidateSkills.length > 3) {
    fail(`${label} requires two to three candidateSkills`);
  }
  const candidateSkills = brief.candidateSkills.map((value, index) => {
    const candidate = object(value, `${label} candidateSkills[${index}]`);
    exactKeys(candidate, [
      'canonicalId', 'canonicalPath', 'contentHash', 'license', 'qualityScore',
      'repository', 'safeToPublish', 'slotIds', 'sourceCommit', 'treeHash', 'version',
    ], `${label} candidateSkills[${index}]`);
    if (!ID.test(candidate.canonicalId || '')
      || !/^skills\/[a-z0-9][a-z0-9_/-]*$/.test(candidate.canonicalPath || '')
      || !/^[0-9a-f]{40}$/.test(candidate.sourceCommit || '')
      || !SHA256.test(candidate.contentHash || '') || !SHA256.test(candidate.treeHash || '')
      || typeof candidate.version !== 'string' || !candidate.version
      || candidate.safeToPublish !== true || typeof candidate.license !== 'string' || !candidate.license
      || !Array.isArray(candidate.slotIds) || candidate.slotIds.length < 1) {
      fail(`${label} candidateSkills must contain exact canonical identities`);
    }
    return {
      canonicalId: candidate.canonicalId,
      contentHash: candidate.contentHash,
      treeHash: candidate.treeHash,
      version: candidate.version,
      sourceCommit: candidate.sourceCommit,
      canonicalPath: candidate.canonicalPath,
      slotIds: candidate.slotIds,
      safeToPublish: candidate.safeToPublish,
      license: candidate.license,
    };
  });
  const generationBrief = {
    schemaVersion: BRIEF_SCHEMA,
    opportunityId: brief.opportunityId,
    briefDigest: brief.briefDigest,
    evaluationTemplateId: brief.evaluationTemplateId,
    task: brief.task,
    name: brief.name,
    slug: brief.slug,
    keywords: brief.keywords,
    capabilitySlots: brief.capabilitySlots,
    requiredArtifacts: brief.requiredArtifacts,
    candidateSkills,
  };
  const { briefDigest, ...unsignedBrief } = generationBrief;
  if (digest(unsignedBrief) !== briefDigest) fail(`${label} briefDigest is invalid`);
  return { generationBrief, sourceEvidenceHash: brief.sourceEvidenceHash };
}

async function readJson(file) {
  try {
    return JSON.parse(await readFile(file, 'utf8'));
  } catch (error) {
    fail(`cannot read JSON ${file}: ${error.message}`);
  }
}

async function writeJson(file, value) {
  await mkdir(dirname(file), { recursive: true });
  await writeFile(file, `${canonicalJson(value)}\n`, { mode: 0o600 });
}

function sourceCreatedAt(value) {
  const parsed = Date.parse(value);
  if (!RFC3339_UTC.test(value || '') || !Number.isFinite(parsed)) {
    fail('--source-created-at must be a GitHub Actions created_at timestamp');
  }
  const canonical = new Date(parsed).toISOString();
  if (value !== canonical && value !== canonical.replace('.000Z', 'Z')) {
    fail('--source-created-at must be a GitHub Actions created_at timestamp');
  }
  return canonical;
}

function requireFreshSourceRun(value) {
  const createdAt = Date.parse(sourceCreatedAt(value));
  if (createdAt < Date.now() - 24 * 60 * 60 * 1000) fail('source run is older than 24 hours');
  if (createdAt > Date.now() + 5 * 60 * 1000) fail('source run is more than 5 minutes in the future');
}

async function admit(args) {
  const sourceRunId = required(args, 'source-run-id');
  const sourceCreated = sourceCreatedAt(required(args, 'source-created-at'));
  if (!RUN_ID.test(sourceRunId)) fail('--source-run-id must be a GitHub Actions run id');
  const admissionSha = required(args, 'admission-head-sha');
  const admissionRunAttempt = Number(required(args, 'admission-run-attempt'));
  const sourceWorkflowPath = required(args, 'source-workflow-path');
  const snapshotSha256 = required(args, 'skills-sh-snapshot-sha256');
  if (!/^[0-9a-f]{40}$/.test(admissionSha) || !SHA256.test(snapshotSha256) || !Number.isSafeInteger(admissionRunAttempt) || admissionRunAttempt < 1) {
    fail('admission identity is invalid');
  }
  const response = object(await readJson(required(args, 'input')), 'queue response');
  exactKeys(response, ['data'], 'queue response');
  const queue = object(response.data, 'queue data');
  exactKeys(queue, queue.noOpReason === undefined
    ? ['generatedAt', 'limit', 'lookbackDays', 'opportunities', 'rejectionSummary', 'schemaVersion', 'source']
    : ['generatedAt', 'limit', 'lookbackDays', 'noOpReason', 'opportunities', 'rejectionSummary', 'schemaVersion', 'source'], 'queue data');
  if (queue.schemaVersion !== PLANNER_SCHEMA || !Array.isArray(queue.opportunities) || queue.opportunities.length > 3) {
    fail('queue data must contain at most three Opportunity Briefs');
  }
  const summary = rejectionSummary(queue.rejectionSummary);
  const admittedBriefs = queue.opportunities.filter((brief) => brief?.admittedForGeneration === true);
  if (summary.admitted !== admittedBriefs.length) {
    fail('rejectionSummary admitted count must match admitted Opportunity Brief count');
  }
  if ((admittedBriefs.length === 0 && queue.source !== 'no-op')
    || (admittedBriefs.length > 0 && !['public-intent', 'anonymous-aggregate', 'mixed'].includes(queue.source))) {
    fail('queue source must agree with Opportunity Brief count');
  }
  const opportunities = admittedBriefs
    .map((brief, index) => {
    const { generationBrief, sourceEvidenceHash } = projectBrief(brief, `Opportunity Brief ${index + 1}`);
    return {
      opportunity_id: generationBrief.opportunityId,
      brief_digest: generationBrief.briefDigest,
      source_evidence_hash: sourceEvidenceHash,
      brief: generationBrief,
    };
  });
  if (new Set(opportunities.map(({ opportunity_id: id }) => id)).size !== opportunities.length) {
    fail('Opportunity Brief ids must be unique');
  }
  await writeJson(required(args, 'output'), {
    admission: {
      head_sha: admissionSha,
      created_at: sourceCreated,
      run_attempt: admissionRunAttempt,
      run_id: sourceRunId,
      workflow_path: sourceWorkflowPath,
    },
    schemaVersion: ADMISSION_SCHEMA,
    rejectionSummary: summary,
    skills_sh_snapshot_sha256: snapshotSha256,
    source_run_id: sourceRunId,
    opportunities,
  });
}

async function admissionArtifact(args, { requireFresh = false } = {}) {
  const sourceRunId = required(args, 'source-run-id');
  const sourceCreated = sourceCreatedAt(required(args, 'source-created-at'));
  if (requireFresh) requireFreshSourceRun(sourceCreated);
  const admissionSha = required(args, 'admission-head-sha');
  const admissionRunAttempt = Number(required(args, 'admission-run-attempt'));
  const sourceWorkflowPath = required(args, 'source-workflow-path');
  if (!RUN_ID.test(sourceRunId) || !/^[0-9a-f]{40}$/.test(admissionSha)
    || !Number.isSafeInteger(admissionRunAttempt) || admissionRunAttempt < 1) {
    fail('admission identity is invalid');
  }
  const artifact = object(await readJson(required(args, 'input')), 'admission artifact');
  exactKeys(artifact, ['admission', 'opportunities', 'rejectionSummary', 'schemaVersion', 'skills_sh_snapshot_sha256', 'source_run_id'], 'admission artifact');
  exactKeys(artifact.admission, ['created_at', 'head_sha', 'run_attempt', 'run_id', 'workflow_path'], 'admission identity');
  rejectionSummary(artifact.rejectionSummary);
  if (artifact.schemaVersion !== ADMISSION_SCHEMA || artifact.source_run_id !== sourceRunId
    || artifact.admission.run_id !== sourceRunId || artifact.admission.head_sha !== admissionSha
    || artifact.admission.created_at !== sourceCreated
    || artifact.admission.run_attempt !== admissionRunAttempt || artifact.admission.workflow_path !== sourceWorkflowPath
    || !Array.isArray(artifact.opportunities)) {
    fail('admission artifact does not match this source run');
  }
  return { artifact, sourceCreated, sourceRunId, admissionSha, admissionRunAttempt, sourceWorkflowPath };
}

async function handoff(args) {
  const {
    artifact, sourceCreated, sourceRunId, admissionSha, admissionRunAttempt, sourceWorkflowPath,
  } = await admissionArtifact(args, { requireFresh: true });
  const opportunityId = required(args, 'opportunity-id');
  const briefDigest = required(args, 'brief-digest');
  if (!RUN_ID.test(sourceRunId) || !ID.test(opportunityId) || !SHA256.test(briefDigest)) {
    fail('handoff inputs are invalid');
  }
  const matches = artifact.opportunities.filter((item) => item?.opportunity_id === opportunityId);
  if (matches.length !== 1) fail('admission artifact must contain exactly one requested Opportunity Brief');
  const entry = matches[0];
  exactKeys(entry, ['brief', 'brief_digest', 'opportunity_id', 'source_evidence_hash'], 'Opportunity Brief artifact entry');
  const strictBrief = object(entry.brief, 'Opportunity Brief');
  if (strictBrief.schemaVersion !== BRIEF_SCHEMA || strictBrief.opportunityId !== opportunityId
    || entry.brief_digest !== briefDigest || strictBrief.briefDigest !== briefDigest
    || !SHA256.test(entry.source_evidence_hash || '')) {
    fail('Opportunity Brief digest or admission state does not match');
  }
  const { briefDigest: _briefDigest, ...unsignedBrief } = strictBrief;
  if (digest(unsignedBrief) !== briefDigest) fail('Opportunity Brief digest or admission state does not match');
  const generationId = required(args, 'generation-id');
  const repository = required(args, 'repository');
  const workflow = required(args, 'workflow');
  const runId = required(args, 'run-id');
  const runAttempt = Number(required(args, 'run-attempt'));
  const commitSha = required(args, 'commit-sha');
  if (!UUID_V4.test(generationId) || !RUN_ID.test(runId) || !Number.isSafeInteger(runAttempt) || runAttempt < 1 || !/^[0-9a-f]{40}$/.test(commitSha)) {
    fail('workflow binding is invalid');
  }
  const scenario = {
    ...strictBrief,
    id: opportunityId,
    version: '1.0.0',
    tags: [...strictBrief.keywords],
    generationId,
  };
  const opportunityOutput = required(args, 'opportunity-output');
  await writeJson(opportunityOutput, strictBrief);
  const plan = {
    opportunityBinding: {
      briefDigest,
      candidateSkills: strictBrief.candidateSkills,
      evaluationTemplateId: strictBrief.evaluationTemplateId,
      opportunityId,
      sourceRunId,
      sourceRunAttempt: admissionRunAttempt,
      sourceCreatedAt: sourceCreated,
      sourceHeadSha: admissionSha,
      sourceWorkflowPath,
    },
    opportunityFile: 'opportunity.json',
    schemaVersion: PLAN_SCHEMA,
    source: 'signals',
    scenarios: [scenario],
    workflowBinding: { repository, workflow, runId, runAttempt, commitSha, scenarioId: scenario.id },
  };
  await writeJson(required(args, 'output'), { ...plan, planDigest: digest(plan) });
}

async function validatePlanClaim(args) {
  const sourceRunId = required(args, 'source-run-id');
  const sourceCreated = sourceCreatedAt(required(args, 'source-created-at'));
  requireFreshSourceRun(sourceCreated);
  const opportunityId = required(args, 'opportunity-id');
  const briefDigest = required(args, 'brief-digest');
  if (!RUN_ID.test(sourceRunId) || !ID.test(opportunityId) || !SHA256.test(briefDigest)) {
    fail('plan claim inputs are invalid');
  }
  const plan = object(await readJson(required(args, 'input')), 'plan claim');
  exactKeys(plan, ['opportunityBinding', 'opportunityFile', 'planDigest', 'scenarios', 'schemaVersion', 'source', 'workflowBinding'], 'plan claim');
  exactKeys(plan.opportunityBinding, [
    'briefDigest', 'candidateSkills', 'evaluationTemplateId', 'opportunityId', 'sourceCreatedAt', 'sourceHeadSha', 'sourceRunAttempt', 'sourceRunId', 'sourceWorkflowPath',
  ], 'plan claim binding');
  exactKeys(plan.workflowBinding, ['commitSha', 'repository', 'runAttempt', 'runId', 'scenarioId', 'workflow'], 'plan claim workflow binding');
  if (plan.schemaVersion !== PLAN_SCHEMA || plan.source !== 'signals' || plan.opportunityFile !== 'opportunity.json'
    || !SHA256.test(plan.planDigest || '') || !Array.isArray(plan.scenarios) || plan.scenarios.length !== 1
    || plan.opportunityBinding.sourceRunId !== sourceRunId || plan.opportunityBinding.sourceCreatedAt !== sourceCreated
    || plan.opportunityBinding.opportunityId !== opportunityId || plan.opportunityBinding.briefDigest !== briefDigest
    || plan.workflowBinding.scenarioId !== opportunityId || !UUID_V4.test(plan.scenarios[0]?.generationId || '')) {
    fail('plan claim does not match this admitted Opportunity Brief');
  }
  const { planDigest, ...unsignedPlan } = plan;
  if (digest(unsignedPlan) !== planDigest) fail('plan claim digest is invalid');
  await writeJson(required(args, 'output'), {
    generationId: plan.scenarios[0].generationId,
    opportunityId,
    sourceRunId,
  });
}

async function select(args) {
  const artifact = object(await readJson(required(args, 'input')), 'admission artifact');
  exactKeys(artifact, ['admission', 'opportunities', 'rejectionSummary', 'schemaVersion', 'skills_sh_snapshot_sha256', 'source_run_id'], 'admission artifact');
  rejectionSummary(artifact.rejectionSummary);
  if (artifact.schemaVersion !== ADMISSION_SCHEMA || !Array.isArray(artifact.opportunities)) fail('admission artifact is invalid');
  const opportunities = [...artifact.opportunities];
  if (opportunities.length !== 0 && opportunities.length !== 1) {
    await writeJson(required(args, 'output'), { ...artifact, opportunities: [opportunities[0]] });
    return;
  }
  await writeJson(required(args, 'output'), { ...artifact, opportunities });
}

try {
  const { command, args } = parseArgs(process.argv.slice(2));
  if (command === 'admit') await admit(args);
  else if (command === 'handoff') await handoff(args);
  else if (command === 'validate-admission') await admissionArtifact(args, { requireFresh: true });
  else if (command === 'validate-plan-claim') await validatePlanClaim(args);
  else if (command === 'select') await select(args);
  else fail('usage: pack-opportunity-handoff.mjs <admit|select|handoff|validate-admission|validate-plan-claim> --name value');
} catch (error) {
  process.stderr.write(`pack-opportunity-handoff: ${error.message}\n`);
  process.exitCode = 1;
}
