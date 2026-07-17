import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { resolveSubmissionSource } from '../resolve-submission-source.mjs';
import {
  discoverSubmissionSkills,
  validateSlugAliasRegistry,
} from '../discover-submission-skills.mjs';

const MAIN_SHA = '1'.repeat(40);
const READY_SHA = '2'.repeat(40);

function refs(...entries) {
  return `${entries.map(([sha, ref]) => `${sha}\t${ref}`).join('\n')}\n`;
}

function withDirectory(fn) {
  const root = mkdtempSync(join(tmpdir(), 'submission-source-'));
  try {
    return fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test('tree URLs resolve the exact non-default ref before percent-decoding the skill path', () => {
  const result = resolveSubmissionSource({
    githubUrl: 'https://github.com/example/repo/tree/skillstore-ready/skills/localize%20china',
    defaultRef: 'main',
    refsText: refs(
      [MAIN_SHA, 'refs/heads/main'],
      [READY_SHA, 'refs/heads/skillstore-ready'],
    ),
  });
  assert.deepEqual(result, {
    schemaVersion: 1,
    owner: 'example',
    repo: 'repo',
    ref: 'skillstore-ready',
    refType: 'heads',
    refSha: READY_SHA,
    skillPath: 'skills/localize china',
    explicitPath: true,
    normalizedUrl: 'https://github.com/example/repo/tree/skillstore-ready/skills/localize%20china',
  });
});

test('slash refs are encoded for the CLI and ambiguous ref/path splits fail closed', () => {
  const slash = resolveSubmissionSource({
    githubUrl: 'https://github.com/example/repo/tree/feature/ready/skills/demo',
    defaultRef: 'main',
    refsText: refs([MAIN_SHA, 'refs/heads/main'], [READY_SHA, 'refs/heads/feature/ready']),
  });
  assert.equal(slash.ref, 'feature/ready');
  assert.equal(slash.skillPath, 'skills/demo');
  assert.equal(slash.normalizedUrl, 'https://github.com/example/repo/tree/feature%2Fready/skills/demo');

  assert.throws(() => resolveSubmissionSource({
    githubUrl: 'https://github.com/example/repo/tree/feature/ready/skills/demo',
    defaultRef: 'main',
    refsText: refs(
      [MAIN_SHA, 'refs/heads/main'],
      [MAIN_SHA, 'refs/heads/feature'],
      [READY_SHA, 'refs/heads/feature/ready'],
    ),
  }), /ambiguous across refs/);
});

test('repository URLs use the exact default head and unsafe encoded paths are rejected', () => {
  const result = resolveSubmissionSource({
    githubUrl: 'https://github.com/example/repo.git',
    defaultRef: 'main',
    refsText: refs([MAIN_SHA, 'refs/heads/main']),
  });
  assert.equal(result.explicitPath, false);
  assert.equal(result.normalizedUrl, 'https://github.com/example/repo/tree/main');

  assert.throws(() => resolveSubmissionSource({
    githubUrl: 'https://github.com/example/repo/tree/main/skills/%2e%2e/secret',
    defaultRef: 'main',
    refsText: refs([MAIN_SHA, 'refs/heads/main']),
  }), /unsafe path segment/);
});

test('explicit paths with no SKILL.md fail while a repository-level empty scan remains an explicit no-op candidate', () => withDirectory((root) => {
  mkdirSync(join(root, 'empty'));
  assert.throws(() => discoverSubmissionSkills({
    sourceDir: root,
    skillPath: 'empty',
    explicitPath: true,
  }), /contains no SKILL\.md/);
  assert.deepEqual(discoverSubmissionSkills({ sourceDir: root }), {
    schemaVersion: 1,
    explicitPath: false,
    skillPath: '',
    skills: [],
  });
}));

test('valid root-level names produce the same planned slug while malformed root frontmatter fails before CLI execution', () => withDirectory((root) => {
  writeFileSync(join(root, 'SKILL.md'), '---\nname: flops-compute-prices\ndescription: "GPU prices: verified"\n---\n');
  assert.deepEqual(discoverSubmissionSkills({ sourceDir: root }).skills, [
    { slug: 'flops-compute-prices', path: '.' },
  ]);

  writeFileSync(join(root, 'SKILL.md'), '---\nname: flops-compute-prices\ndescription: GPU prices Keywords: verified\n---\n');
  assert.throws(
    () => discoverSubmissionSkills({ sourceDir: root }),
    /invalid YAML plain scalar/,
  );
}));

test('pure Chinese path and frontmatter use an exact repository-bound alias', () => withDirectory((root) => {
  mkdirSync(join(root, '装修方案诊断'));
  writeFileSync(join(root, '装修方案诊断', 'SKILL.md'), '---\nname: 装修方案诊断\ndescription: 安全诊断\n---\n');
  const registry = {
    schemaVersion: 1,
    aliases: [{
      repository: 'zx029w/zhuangxiu-skills',
      path: '装修方案诊断',
      expectedName: '装修方案诊断',
      baseSlug: 'zhuangxiu-fangan-zhenduan',
    }],
  };

  assert.deepEqual(discoverSubmissionSkills({
    sourceDir: root,
    skillPath: '装修方案诊断',
    explicitPath: true,
    repository: 'zx029w/zhuangxiu-skills',
    slugAliasRegistry: registry,
  }).skills, [{ slug: 'zhuangxiu-fangan-zhenduan', path: '装修方案诊断' }]);

  assert.throws(() => discoverSubmissionSkills({
    sourceDir: root,
    skillPath: '装修方案诊断',
    explicitPath: true,
    repository: 'zx029w/zhuangxiu-skills',
  }), /no verified path alias/);
}));

test('aliases cannot override ASCII identities and exact expected names fail closed', () => withDirectory((root) => {
  mkdirSync(join(root, 'skill'));
  writeFileSync(join(root, 'skill', 'SKILL.md'), '---\nname: ascii-skill\n---\n');
  const registry = {
    schemaVersion: 1,
    aliases: [{
      repository: 'example/skills',
      path: 'skill',
      expectedName: 'ascii-skill',
      baseSlug: 'different-skill',
    }],
  };
  assert.throws(() => discoverSubmissionSkills({
    sourceDir: root,
    repository: 'example/skills',
    slugAliasRegistry: registry,
  }), /override an existing ASCII identity/);

  writeFileSync(join(root, 'skill', 'SKILL.md'), '---\nname: 中文名称\n---\n');
  assert.throws(() => discoverSubmissionSkills({
    sourceDir: root,
    repository: 'example/skills',
    slugAliasRegistry: registry,
  }), /name does not match/);
}));

test('multi-skill alias and ASCII collisions fail instead of choosing an order-dependent identity', () => withDirectory((root) => {
  mkdirSync(join(root, '中文技能'));
  mkdirSync(join(root, 'ascii'));
  writeFileSync(join(root, '中文技能', 'SKILL.md'), '---\nname: 中文技能\n---\n');
  writeFileSync(join(root, 'ascii', 'SKILL.md'), '---\nname: shared-slug\n---\n');
  const registry = {
    schemaVersion: 1,
    aliases: [{
      repository: 'example/skills',
      path: '中文技能',
      expectedName: '中文技能',
      baseSlug: 'shared-slug',
    }],
  };
  assert.throws(() => discoverSubmissionSkills({
    sourceDir: root,
    repository: 'example/skills',
    slugAliasRegistry: registry,
  }), /duplicate discovered skill slug/);
}));

test('alias registry rejects duplicate paths, canonical slugs, and unsafe paths', () => {
  const base = {
    repository: 'example/skills',
    path: '中文技能',
    expectedName: '中文技能',
    baseSlug: 'zhongwen-jineng',
  };
  assert.throws(() => validateSlugAliasRegistry({
    schemaVersion: 1,
    aliases: [base, { ...base }],
  }), /duplicate slug alias path/);
  assert.throws(() => validateSlugAliasRegistry({
    schemaVersion: 1,
    aliases: [base, { ...base, path: '另一个技能' }],
  }), /duplicate slug alias baseSlug/);
  assert.throws(() => validateSlugAliasRegistry({
    schemaVersion: 1,
    aliases: [{ ...base, path: '../escape' }],
  }), /unsafe path segment/);
  assert.throws(() => validateSlugAliasRegistry({
    schemaVersion: 1,
    aliases: [],
    extra: true,
  }), /unknown or missing fields/);
});

test('ASCII discovery remains unchanged when aliases belong to another repository and scope', () => withDirectory((root) => {
  mkdirSync(join(root, 'demo'));
  writeFileSync(join(root, 'demo', 'SKILL.md'), '---\nname: Demo Skill\n---\n');
  assert.deepEqual(discoverSubmissionSkills({
    sourceDir: root,
    repository: 'example/skills',
    slugAliasRegistry: {
      schemaVersion: 1,
      aliases: [{
        repository: 'other/skills',
        path: '中文技能',
        expectedName: '中文技能',
        baseSlug: 'zhongwen-jineng',
      }],
    },
  }).skills, [{ slug: 'demo-skill', path: 'demo' }]);
}));
