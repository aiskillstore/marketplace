import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const SCRIPT = join(ROOT, 'scripts/pack-opportunity-handoff.mjs');
const RUN_ID = '123456789';
const UUID = '11111111-1111-4111-8111-111111111111';
const ADMISSION_SHA = 'b'.repeat(40);
const SOURCE_CREATED_AT = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
const SKILLSTORE_GOLDEN = JSON.parse(readFileSync(join(ROOT, 'scripts/tests/fixtures/pack-production-evaluation-v4.golden.json'), 'utf8'));

function run(args) {
  const result = spawnSync('node', [SCRIPT, ...args], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
}

function brief() {
  const strict = {
    schemaVersion: 'skillstore.pack-opportunity-brief/v1',
    opportunityId: 'demand-workbook',
    evaluationTemplateId: 'runtime-ready-workbook',
    task: 'Create a real workbook.',
    name: 'Demand Workbook Pack',
    slug: 'demand-workbook-pack',
    keywords: ['workbook', 'spreadsheet'],
    capabilitySlots: [{
      id: 'workbook', name: 'Workbook', task: 'Create a workbook.',
      keywords: ['workbook'], required: true, artifactIds: ['workbook'],
    }],
    requiredArtifacts: [{
      id: 'workbook', description: 'A validated workbook.',
      extensions: ['.xlsx'], minimumCount: 1,
    }],
    candidateSkills: [
      {
        canonicalId: 'example-one', canonicalPath: 'skills/example/one',
        sourceCommit: 'a'.repeat(40), contentHash: 'c'.repeat(64), treeHash: 'e'.repeat(64),
        version: '1.0.0', slotIds: ['workbook'], safeToPublish: true, license: 'MIT',
      },
      {
        canonicalId: 'example-two', canonicalPath: 'skills/example/two',
        sourceCommit: 'a'.repeat(40), contentHash: 'd'.repeat(64), treeHash: 'f'.repeat(64),
        version: '2.0.0', slotIds: ['workbook'], safeToPublish: true, license: 'Apache-2.0',
      },
    ],
  };
  strict.briefDigest = createHash('sha256').update(canonical(strict)).digest('hex');
  return {
    ...strict,
    sourceEvidenceHash: 'f'.repeat(64),
    canonicalIntent: 'workbook automation',
    demandEvidence: {
      lookbackDays: 30,
      anonymousAggregateCount: 3,
      skillsSh: { view: 'trending', metric: 'installs24h', matchedEntries: [] },
    },
    candidateSkills: strict.candidateSkills.map((candidate) => ({
      ...candidate,
      repository: 'https://github.com/example/repo',
      qualityScore: 9,
    })),
    duplicate: { status: 'none', packSlugs: [] },
    gap: { status: 'open' },
    admittedForGeneration: true,
    score: 90,
    reasons: ['public demand'],
  };
}

function queue(opportunities = [brief()]) {
  return {
    data: {
      schemaVersion: 'skillstore.pack-opportunity-plan/v1',
      source: opportunities.length > 0 ? 'anonymous-aggregate' : 'no-op',
      generatedAt: '2026-07-22T00:00:00.000Z',
      lookbackDays: 30,
      limit: 3,
      opportunities,
      rejectionSummary: {
        considered: opportunities.length,
        admitted: opportunities.length,
        demandInsufficient: 0,
        duplicate: 0,
        cooldown: 0,
        supplyIncomplete: 0,
        templateIncompatible: 0,
        rankingOnlySkills: 0,
      },
    },
  };
}

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}

function rebindBriefDigest(value) {
  const strict = {
    schemaVersion: value.schemaVersion,
    opportunityId: value.opportunityId,
    briefDigest: value.briefDigest,
    evaluationTemplateId: value.evaluationTemplateId,
    task: value.task,
    name: value.name,
    slug: value.slug,
    keywords: value.keywords,
    capabilitySlots: value.capabilitySlots,
    requiredArtifacts: value.requiredArtifacts,
    candidateSkills: value.candidateSkills.map(({ canonicalId, contentHash, treeHash, version, sourceCommit, canonicalPath, slotIds, safeToPublish, license }) => ({ canonicalId, contentHash, treeHash, version, sourceCommit, canonicalPath, slotIds, safeToPublish, license })),
  };
  delete strict.briefDigest;
  value.briefDigest = createHash('sha256').update(canonical(strict)).digest('hex');
}

function briefFromSkillstoreGolden() {
  const value = brief();
  const { opportunityBinding, scenario } = SKILLSTORE_GOLDEN;
  Object.assign(value, {
    opportunityId: opportunityBinding.opportunityId,
    evaluationTemplateId: opportunityBinding.evaluationTemplateId,
    task: scenario.task,
    name: scenario.name,
    slug: scenario.slug,
    keywords: scenario.tags,
    capabilitySlots: scenario.requiredCapabilitySlots.map((id) => ({ id })),
    candidateSkills: opportunityBinding.candidateSkills.map((candidate) => ({
      ...candidate,
      repository: 'https://github.com/aiskillstore/marketplace',
      qualityScore: 9,
    })),
  });
  rebindBriefDigest(value);
  return value;
}

test('admission creates a stable digest-bound artifact and handoff binds its approved runtime fixture id', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const artifact = join(directory, 'opportunities.json');
    const plan = join(directory, 'plan.json');
    writeFileSync(input, JSON.stringify(queue()));
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    const first = readFileSync(artifact, 'utf8');
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    assert.equal(readFileSync(artifact, 'utf8'), first);
    const admitted = JSON.parse(first);
    assert.equal(admitted.admission.created_at, new Date(SOURCE_CREATED_AT).toISOString());
    assert.deepEqual(admitted.rejectionSummary, queue().data.rejectionSummary);
    run([
      'handoff', '--input', artifact, '--output', plan,
      '--opportunity-id', admitted.opportunities[0].opportunity_id,
      '--brief-digest', admitted.opportunities[0].brief_digest,
      '--source-run-id', RUN_ID, '--source-created-at', SOURCE_CREATED_AT, '--generation-id', UUID,
      '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--opportunity-output', join(directory, 'opportunity.json'),
      '--repository', 'aiskillstore/marketplace', '--workflow', 'Generate Pack',
      '--run-id', '987654321', '--run-attempt', '1', '--commit-sha', 'a'.repeat(40),
    ]);
    const bound = JSON.parse(readFileSync(plan, 'utf8'));
    assert.equal(bound.scenarios[0].id, 'demand-workbook');
    assert.equal(bound.scenarios[0].evaluationTemplateId, 'runtime-ready-workbook');
    assert.equal(bound.scenarios[0].generationId, UUID);
    assert.equal(bound.opportunityBinding.sourceCreatedAt, new Date(SOURCE_CREATED_AT).toISOString());
    const exact = JSON.parse(readFileSync(join(directory, 'opportunity.json'), 'utf8'));
    assert.deepEqual(bound.opportunityBinding.candidateSkills, exact.candidateSkills);
    const { planDigest, ...unsignedPlan } = bound;
    assert.equal(planDigest, createHash('sha256').update(canonical(unsignedPlan)).digest('hex'));
    unsignedPlan.opportunityBinding.sourceCreatedAt = new Date(Date.now()).toISOString();
    assert.notEqual(planDigest, createHash('sha256').update(canonical(unsignedPlan)).digest('hex'));
    assert.deepEqual(Object.keys(exact).sort(), [
      'briefDigest', 'candidateSkills', 'capabilitySlots', 'evaluationTemplateId',
      'keywords', 'name', 'opportunityId', 'requiredArtifacts', 'schemaVersion', 'slug', 'task',
    ].sort());
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('handoff preserves the Skillstore golden candidate binding and canonicalizes GitHub timestamps', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const artifact = join(directory, 'opportunities.json');
    const plan = join(directory, 'plan.json');
    const sourceCreatedAt = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
    const goldenBrief = briefFromSkillstoreGolden();
    writeFileSync(input, JSON.stringify(queue([goldenBrief])));
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', sourceCreatedAt, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    const admitted = JSON.parse(readFileSync(artifact, 'utf8')).opportunities[0];
    assert.equal(JSON.parse(readFileSync(artifact, 'utf8')).admission.created_at, new Date(sourceCreatedAt).toISOString());
    run(['handoff', '--input', artifact, '--output', plan, '--opportunity-output', join(directory, 'opportunity.json'),
      '--opportunity-id', admitted.opportunity_id, '--brief-digest', admitted.brief_digest,
      '--source-run-id', RUN_ID, '--source-created-at', sourceCreatedAt, '--generation-id', UUID,
      '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
      '--repository', 'aiskillstore/marketplace', '--workflow', 'Generate Pack', '--run-id', '987654321', '--run-attempt', '1', '--commit-sha', 'a'.repeat(40)]);
    const bound = JSON.parse(readFileSync(plan, 'utf8')).opportunityBinding;
    assert.deepEqual(bound.candidateSkills, SKILLSTORE_GOLDEN.opportunityBinding.candidateSkills);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('admission canonicalizes a GitHub RFC3339 seconds timestamp', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const output = join(directory, 'opportunities.json');
    writeFileSync(input, JSON.stringify(queue()));
    run(['admit', '--input', input, '--output', output, '--source-run-id', RUN_ID,
      '--source-created-at', '2026-07-23T12:34:56Z', '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    assert.equal(JSON.parse(readFileSync(output, 'utf8')).admission.created_at, '2026-07-23T12:34:56.000Z');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('plan claim validation accepts only the exact immutable admission binding', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const artifact = join(directory, 'opportunities.json');
    const plan = join(directory, 'plan.json');
    const claim = join(directory, 'claim.json');
    writeFileSync(input, JSON.stringify(queue()));
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    const admitted = JSON.parse(readFileSync(artifact, 'utf8')).opportunities[0];
    run(['handoff', '--input', artifact, '--output', plan, '--opportunity-output', join(directory, 'opportunity.json'),
      '--opportunity-id', admitted.opportunity_id, '--brief-digest', admitted.brief_digest,
      '--source-run-id', RUN_ID, '--source-created-at', SOURCE_CREATED_AT, '--generation-id', UUID,
      '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
      '--repository', 'aiskillstore/marketplace', '--workflow', 'Generate Pack', '--run-id', '987654321', '--run-attempt', '1', '--commit-sha', 'a'.repeat(40)]);
    run(['validate-plan-claim', '--input', plan, '--output', claim, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--opportunity-id', admitted.opportunity_id, '--brief-digest', admitted.brief_digest]);
    assert.equal(JSON.parse(readFileSync(claim, 'utf8')).generationId, UUID);
    const tampered = JSON.parse(readFileSync(plan, 'utf8'));
    tampered.opportunityBinding.sourceRunId = '987654321';
    writeFileSync(plan, JSON.stringify(tampered));
    const result = spawnSync('node', [SCRIPT, 'validate-plan-claim', '--input', plan, '--output', claim,
      '--source-run-id', RUN_ID, '--source-created-at', SOURCE_CREATED_AT,
      '--opportunity-id', admitted.opportunity_id, '--brief-digest', admitted.brief_digest], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /plan claim/);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('admission preserves only a strict bounded rejection summary', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const output = join(directory, 'opportunities.json');
    const valid = queue();
    valid.data.rejectionSummary = {
      considered: 7,
      admitted: 1,
      demandInsufficient: 5,
      duplicate: 2,
      cooldown: 1,
      supplyIncomplete: 4,
      templateIncompatible: 3,
      rankingOnlySkills: 100,
    };
    writeFileSync(input, JSON.stringify(valid));
    const args = ['admit', '--input', input, '--output', output, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA,
      '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
      '--skills-sh-snapshot-sha256', 'e'.repeat(64)];
    run(args);
    assert.deepEqual(JSON.parse(readFileSync(output, 'utf8')).rejectionSummary, valid.data.rejectionSummary);

    for (const invalidSummary of [
      { ...valid.data.rejectionSummary, extra: 0 },
      { ...valid.data.rejectionSummary, supplyIncomplete: undefined },
      { ...valid.data.rejectionSummary, templateIncompatible: undefined },
      { ...valid.data.rejectionSummary, rankingOnlySkills: undefined },
      { ...valid.data.rejectionSummary, considered: 1001 },
      { ...valid.data.rejectionSummary, cooldown: 8 },
      { ...valid.data.rejectionSummary, admitted: 0 },
      { ...valid.data.rejectionSummary, duplicate: 0.5 },
      { ...valid.data.rejectionSummary, supplyIncomplete: -1 },
      { ...valid.data.rejectionSummary, templateIncompatible: 8 },
      { ...valid.data.rejectionSummary, rankingOnlySkills: 1001 },
    ]) {
      valid.data.rejectionSummary = invalidSummary;
      writeFileSync(input, JSON.stringify(valid));
      const result = spawnSync('node', [SCRIPT, ...args], { encoding: 'utf8' });
      assert.notEqual(result.status, 0);
      assert.match(result.stderr, /rejectionSummary/);
    }
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('admission keeps duplicate and no-demand briefs inside Skillstore while exporting only admitted briefs', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const output = join(directory, 'opportunities.json');
    const rejected = brief();
    rejected.admittedForGeneration = false;
    rejected.reasons = ['existing Pack is a duplicate'];
    const value = queue([rejected]);
    value.data.source = 'no-op';
    value.data.rejectionSummary = {
      considered: 1, admitted: 0, demandInsufficient: 0, templateIncompatible: 0,
      duplicate: 1, cooldown: 0, supplyIncomplete: 0, rankingOnlySkills: 3,
    };
    writeFileSync(input, JSON.stringify(value));
    run(['admit', '--input', input, '--output', output, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA,
      '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
      '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    const artifact = JSON.parse(readFileSync(output, 'utf8'));
    assert.deepEqual(artifact.opportunities, []);
    assert.equal(artifact.rejectionSummary.duplicate, 1);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('handoff rejects a digest that does not cover the approved brief', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const artifact = join(directory, 'opportunities.json');
    writeFileSync(input, JSON.stringify(queue()));
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    const result = spawnSync('node', [SCRIPT, 'handoff', '--input', artifact, '--output', join(directory, 'plan.json'),
      '--opportunity-id', 'demand-workbook', '--brief-digest', '0'.repeat(64), '--source-run-id', RUN_ID, '--source-created-at', SOURCE_CREATED_AT,
      '--generation-id', UUID, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--opportunity-output', join(directory, 'opportunity.json'),
      '--repository', 'aiskillstore/marketplace', '--workflow', 'Generate Pack',
      '--run-id', '987654321', '--run-attempt', '1', '--commit-sha', 'a'.repeat(40)], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /digest/);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('admission rejects a brief without its approved runtime-ready fixture binding', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const incomplete = brief();
    delete incomplete.evaluationTemplateId;
    writeFileSync(input, JSON.stringify(queue([incomplete])));
    const result = spawnSync('node', [SCRIPT, 'admit', '--input', input,
      '--output', join(directory, 'opportunities.json'), '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml', '--skills-sh-snapshot-sha256', 'e'.repeat(64)], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /evaluationTemplateId/);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('select preserves planner ranking and admits only the first Opportunity Brief', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const artifact = join(directory, 'opportunities.json');
    const selected = join(directory, 'selected', 'multiple', 'selected.json');
    const first = brief();
    const second = brief();
    second.opportunityId = 'aaa-lexically-first-but-ranked-second';
    second.slug = 'ranked-second-pack';
    rebindBriefDigest(second);
    writeFileSync(input, JSON.stringify(queue([first, second])));
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA, '--admission-run-attempt', '2',
      '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
      '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    run(['select', '--input', artifact, '--output', selected]);
    const selection = JSON.parse(readFileSync(selected, 'utf8'));
    assert.equal(selection.opportunities[0].opportunity_id, 'demand-workbook');
    assert.deepEqual(selection.rejectionSummary, queue([first, second]).data.rejectionSummary);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('select creates nested outputs for zero, one, and multiple admissions', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const second = brief();
    second.opportunityId = 'second-opportunity';
    rebindBriefDigest(second);
    for (const [name, opportunities, expected] of [
      ['zero', [], 0],
      ['one', [brief()], 1],
      ['multiple', [brief(), second], 1],
    ]) {
      const input = join(directory, name, 'queue.json');
      const artifact = join(directory, name, 'admission', 'opportunities.json');
      const selected = join(directory, name, 'selected', 'nested', 'opportunities.json');
      mkdirSync(dirname(input), { recursive: true });
      writeFileSync(input, JSON.stringify(queue(opportunities)));
      run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
        '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA,
        '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
        '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
      run(['select', '--input', artifact, '--output', selected]);
      assert.equal(JSON.parse(readFileSync(selected, 'utf8')).opportunities.length, expected);
    }
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('handoff rejects stale, future, and mismatched source run creation timestamps', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-opportunity-handoff-'));
  try {
    const input = join(directory, 'queue.json');
    const artifact = join(directory, 'opportunities.json');
    writeFileSync(input, JSON.stringify(queue()));
    run(['admit', '--input', input, '--output', artifact, '--source-run-id', RUN_ID,
      '--source-created-at', SOURCE_CREATED_AT, '--admission-head-sha', ADMISSION_SHA,
      '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
      '--skills-sh-snapshot-sha256', 'e'.repeat(64)]);
    for (const sourceCreatedAt of [
      new Date(Date.now() - 24 * 60 * 60 * 1000 - 1).toISOString(),
      new Date(Date.now() + 5 * 60 * 1000 + 1).toISOString(),
      new Date(Date.now()).toISOString(),
    ]) {
      const result = spawnSync('node', [SCRIPT, 'handoff', '--input', artifact, '--output', join(directory, `${sourceCreatedAt}.json`),
        '--opportunity-id', 'demand-workbook', '--brief-digest', brief().briefDigest, '--source-run-id', RUN_ID,
        '--source-created-at', sourceCreatedAt, '--generation-id', UUID, '--admission-head-sha', ADMISSION_SHA,
        '--admission-run-attempt', '2', '--source-workflow-path', '.github/workflows/pack-opportunity-admission.yml',
        '--opportunity-output', join(directory, 'opportunity.json'), '--repository', 'aiskillstore/marketplace',
        '--workflow', 'Generate Pack', '--run-id', '987654321', '--run-attempt', '1', '--commit-sha', 'a'.repeat(40)], { encoding: 'utf8' });
      assert.notEqual(result.status, 0);
    }
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
