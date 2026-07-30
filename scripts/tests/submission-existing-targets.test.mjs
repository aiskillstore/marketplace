import assert from 'node:assert/strict';
import {
  mkdirSync,
  mkdtempSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { classifySubmissionTargets } from '../classify-submission-targets.mjs';

const SOURCE_COMMIT = '1'.repeat(40);

function withMarketplace(fn) {
  const root = mkdtempSync(join(tmpdir(), 'submission-targets-'));
  mkdirSync(join(root, 'skills'), { recursive: true });
  try {
    return fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function selectionPlan(
  skills = [
    { slug: 'alpha', path: 'skills/alpha' },
    { slug: 'beta', path: 'skills/beta' },
  ],
  repository = 'example/source',
) {
  return {
    schemaVersion: 1,
    repository,
    sourceCommit: SOURCE_COMMIT,
    scope: { reason: 'conventional_skills', path: 'skills' },
    skills,
  };
}

function writeTarget(root, slug, {
  layout = 'community',
  repository = 'example/source',
  sourceRef = 'main',
  skillPath = `skills/${slug}`,
  malformed = false,
  targetOwner = 'example',
  skillName = slug,
  sourceUrl = null,
  schemaValid = true,
} = {}) {
  const relative = layout === 'community' ? `skills/${targetOwner}/${slug}` : `skills/${slug}`;
  const directory = join(root, ...relative.split('/'));
  mkdirSync(directory, { recursive: true });
  writeFileSync(join(directory, 'SKILL.md'), `---\nname: ${skillName}\n---\n`);
  if (malformed) {
    writeFileSync(join(directory, 'skill-report.json'), '{not-json\n');
  } else {
    const [owner, repo] = repository.split('/');
    const report = {
      schema_version: '2.0',
      meta: {
        generated_at: '2026-07-19T00:00:00.000Z',
        slug: layout === 'community' ? `${targetOwner}-${slug}` : slug,
        source_url: sourceUrl ?? `https://github.com/${owner}/${repo}/tree/${sourceRef}/${skillPath}/`,
        source_ref: sourceRef,
        model: 'fixture',
        analysis_version: '3.0.0',
        source_type: layout === 'community' ? 'community' : 'official',
      },
      skill: {
        name: skillName,
        author: layout === 'community' ? targetOwner : owner,
        description: 'fixture',
        supported_tools: ['codex'],
      },
      security_audit: {
        risk_level: 'safe',
        is_blocked: false,
        safe_to_publish: true,
        summary: 'fixture',
        files_scanned: 1,
        total_lines: 1,
        audit_model: 'fixture',
        audited_at: '2026-07-19T00:00:00.000Z',
      },
      content: {
        user_title: 'Fixture',
        value_statement: 'Fixture',
        seo_keywords: [],
        actual_capabilities: [],
        limitations: [],
        use_cases: [],
        prompt_templates: [],
        output_examples: [],
        best_practices: [],
        anti_patterns: [],
        faq: [],
      },
    };
    if (!schemaValid) delete report.security_audit;
    writeFileSync(join(directory, 'skill-report.json'), `${JSON.stringify(report)}\n`);
  }
  return directory;
}

function classify(root, plan = selectionPlan(), sourceRef = 'main') {
  return classifySubmissionTargets({ marketplaceRoot: root, selectionPlan: plan, sourceRef });
}

test('zero existing targets preserves the complete processable selection', () => withMarketplace((root) => {
  assert.deepEqual(classify(root), {
    schemaVersion: 1,
    disposition: 'processable',
    reasonCode: 'no_selected_targets_already_published',
    selectedCount: 2,
    existingCount: 0,
    existingTargets: [],
  });
}));

test('all exact community targets become a handled rejection', () => withMarketplace((root) => {
  writeTarget(root, 'alpha');
  writeTarget(root, 'beta');
  assert.deepEqual(classify(root), {
    schemaVersion: 1,
    disposition: 'all_existing',
    reasonCode: 'all_selected_targets_already_published',
    selectedCount: 2,
    existingCount: 2,
    existingTargets: ['skills/example/alpha', 'skills/example/beta'],
  });
}));

test('an exact repository-bound alias validates the published display name', () => withMarketplace((root) => {
  const path = '装修水电避坑指南';
  const slug = 'zhuangxiu-shuidian-bikeng';
  const repository = 'zx029w/zhuangxiu-skills';
  writeTarget(root, slug, {
    repository,
    targetOwner: 'zx029w',
    skillPath: path,
    skillName: path,
  });
  const plan = selectionPlan([{ slug, path }], repository);
  plan.scope = { reason: 'repository_fallback', path: '.' };
  const result = classifySubmissionTargets({
    marketplaceRoot: root,
    selectionPlan: plan,
    sourceRef: 'main',
    slugAliasRegistry: {
      schemaVersion: 1,
      aliases: [{ repository, path, expectedName: path, baseSlug: slug }],
    },
  });
  assert.equal(result.disposition, 'all_existing');
}));

test('an exact official flat target is recognized without weakening community identity', () => withMarketplace((root) => {
  writeTarget(root, 'alpha', { layout: 'official', repository: 'anthropics/skills' });
  const result = classify(
    root,
    selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }], 'anthropics/skills'),
  );
  assert.equal(result.disposition, 'all_existing');
  assert.deepEqual(result.existingTargets, ['skills/alpha']);
}));

test('mixed existing and new targets fail closed instead of processing a subset', () => withMarketplace((root) => {
  writeTarget(root, 'alpha');
  assert.throws(() => classify(root), /partial published-target collision: 1 existing, 1 new/);
}));

for (const mismatch of [
  { name: 'repository', options: { repository: 'other/source' }, pattern: /source (?:repository mismatch|URL is not canonical)|source_url is not canonical/ },
  { name: 'ref', options: { sourceRef: 'release' }, pattern: /source ref mismatch/ },
  { name: 'path', options: { skillPath: 'skills/other' }, pattern: /source (?:path mismatch|URL is not canonical)|source_url is not canonical/ },
]) {
  test(`a published target with a ${mismatch.name} mismatch fails closed`, () => withMarketplace((root) => {
    writeTarget(root, 'alpha', mismatch.options);
    assert.throws(
      () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
      mismatch.pattern,
    );
  }));
}

test('malformed report and ambiguous exact identities fail closed', () => withMarketplace((root) => {
  writeTarget(root, 'alpha', { malformed: true });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /malformed JSON/,
  );

  rmSync(join(root, 'skills', 'example', 'alpha'), { recursive: true, force: true });
  writeTarget(root, 'alpha');
  writeTarget(root, 'alpha', { layout: 'official' });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /ambiguous published target identity/,
  );
}));

test('an identity-looking report that omits required schema fields fails closed', () => withMarketplace((root) => {
  writeTarget(root, 'alpha', { schemaValid: false });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /security_audit.*must be an object/,
  );
}));

test('malformed alternate target layouts fail closed instead of being ignored', () => withMarketplace((root) => {
  writeTarget(root, 'alpha', { layout: 'official', malformed: true });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /malformed JSON/,
  );

  rmSync(join(root, 'skills', 'alpha'), { recursive: true, force: true });
  writeTarget(root, 'alpha', { layout: 'community', targetOwner: 'anthropics', malformed: true });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }], 'anthropics/skills')),
    /malformed JSON/,
  );
}));

test('pending paths, including dangling symlinks, fail before target classification', () => withMarketplace((root) => {
  mkdirSync(join(root, 'pending', 'example'), { recursive: true });
  symlinkSync(join(root, 'missing'), join(root, 'pending', 'example', 'alpha'));
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /pending target (?:collision|contains a symlink)/,
  );
}));

test('official flat pending and source mismatches fail closed', () => withMarketplace((root) => {
  mkdirSync(join(root, 'pending', 'alpha'), { recursive: true });
  const officialPlan = selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }], 'anthropics/skills');
  assert.throws(() => classify(root, officialPlan), /pending target collision: pending\/alpha/);

  rmSync(join(root, 'pending'), { recursive: true, force: true });
  writeTarget(root, 'alpha', { layout: 'official', repository: 'other/source' });
  assert.throws(() => classify(root, officialPlan), /source (?:repository mismatch|URL is not canonical)|source_url is not canonical/);
}));

test('alternate pending layouts also fail closed for community and official sources', () => withMarketplace((root) => {
  mkdirSync(join(root, 'pending', 'alpha'), { recursive: true });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /pending target collision: pending\/alpha/,
  );

  rmSync(join(root, 'pending'), { recursive: true, force: true });
  mkdirSync(join(root, 'pending', 'anthropics', 'alpha'), { recursive: true });
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }], 'anthropics/skills')),
    /pending target collision: pending\/anthropics\/alpha/,
  );
}));

for (const sourceUrl of [
  'https://github.com:444/example/source/tree/main/skills/alpha/',
  'https://github.com/example/source/tree/main/skills%2Falpha',
  'https://github.com/example/source/tree/main/skills/%2e/alpha',
  'https://github.com/example/source/tree/main/skills/%0Aalpha',
  'https://github.com/Example/source/tree/main/skills/alpha/',
]) {
  test(`noncanonical published source URL fails closed: ${sourceUrl}`, () => withMarketplace((root) => {
    writeTarget(root, 'alpha', { sourceUrl });
    assert.throws(
      () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
      /source_(?:url|repository)|source (?:URL|repository)|source_url|no source ref/,
    );
  }));
}

test('a symlink anywhere inside an existing target fails closed', () => withMarketplace((root) => {
  const target = writeTarget(root, 'alpha');
  mkdirSync(join(target, 'references'));
  symlinkSync('/etc/hosts', join(target, 'references', 'linked.md'));
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /contains symlink/,
  );
}));

test('an alternate flat owner namespace without direct identity files is not a skill target', () => withMarketplace((root) => {
  mkdirSync(join(root, 'skills', 'alpha', 'nested-skill'), { recursive: true });
  const result = classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }]));
  assert.equal(result.disposition, 'processable');
}));

test('slash refs require the canonical percent-encoded source URL', () => withMarketplace((root) => {
  const plan = selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }]);
  writeTarget(root, 'alpha', {
    sourceRef: 'feature/ready',
    sourceUrl: 'https://github.com/example/source/tree/feature%2Fready/skills/alpha/',
  });
  assert.equal(classify(root, plan, 'feature/ready').disposition, 'all_existing');

  rmSync(join(root, 'skills', 'example', 'alpha'), { recursive: true, force: true });
  writeTarget(root, 'alpha', {
    sourceRef: 'feature/ready',
    sourceUrl: 'https://github.com/example/source/tree/feature/ready/skills/alpha/',
  });
  assert.throws(() => classify(root, plan, 'feature/ready'), /source_url is not canonical/);
}));

test('a symlinked target ancestor fails closed even when the final path is missing', () => withMarketplace((root) => {
  const outside = join(root, 'outside');
  mkdirSync(outside);
  symlinkSync(outside, join(root, 'skills', 'example'));
  assert.throws(
    () => classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }])),
    /symlink path component/,
  );
}));

test('an unrelated flat official slug does not hide an exact namespaced target', () => withMarketplace((root) => {
  writeTarget(root, 'alpha');
  writeTarget(root, 'alpha', {
    layout: 'official',
    repository: 'other/source',
  });
  const result = classify(root, selectionPlan([{ slug: 'alpha', path: 'skills/alpha' }]));
  assert.equal(result.disposition, 'all_existing');
  assert.deepEqual(result.existingTargets, ['skills/example/alpha']);
}));
