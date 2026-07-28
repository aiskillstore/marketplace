import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { resolveSubmissionSource } from '../resolve-submission-source.mjs';
import {
  discoverSubmissionSkills,
  validateSlugAliasRegistry,
} from '../discover-submission-skills.mjs';
import { validateSelectionPlan } from '../submission-selection-plan.mjs';

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

test('root SKILL.md blob keeps the explicit root sentinel and cannot be overridden by a manifest', () => {
  const result = resolveSubmissionSource({
    githubUrl: 'https://github.com/example/repo/blob/main/SKILL.md',
    defaultRef: 'main',
    refsText: refs([MAIN_SHA, 'refs/heads/main']),
  });
  assert.equal(result.skillPath, '.');
  assert.equal(result.explicitPath, true);
});

test('a root SKILL.md blob selects only the root skill and ignores nested repository skills', () => withDirectory((root) => {
  mkdirSync(join(root, '.codex-plugin'), { recursive: true });
  mkdirSync(join(root, 'skills', 'nested'), { recursive: true });
  mkdirSync(join(root, 'skills', '-unsafe'), { recursive: true });
  writeFileSync(join(root, '.codex-plugin', 'plugin.json'), JSON.stringify({ name: 'fixture', skills: './skills/' }));
  writeFileSync(join(root, 'SKILL.md'), '---\nname: root-blob\n---\n');
  writeFileSync(join(root, 'skills', 'nested', 'SKILL.md'), '---\nname: nested\n---\n');
  writeFileSync(join(root, 'skills', '-unsafe', 'SKILL.md'), '---\nname: ignored-invalid-path\n---\n');
  symlinkSync(join(root, 'outside'), join(root, 'skills', 'nested', 'untrusted-link'));
  const result = discoverSubmissionSkills({ sourceDir: root, skillPath: '.', explicitPath: true });
  assert.deepEqual(result.scope, { reason: 'explicit_path', path: '.' });
  assert.deepEqual(result.skills, [{ slug: 'root-blob', path: '.' }]);
  assert.equal(result.stats.physicalSkillFiles, 3);
  assert.equal(result.stats.selectedSkillFiles, 1);
  assert.equal(result.stats.ignoredSkillFiles, 2);
}));

test('a frozen Hyperframes-shaped fixture produces one authoritative 19-skill plan and only ignored identical mirrors', () => withDirectory((root) => {
  const publicSlugs = [
    'embedded-captions', 'faceless-explainer', 'figma', 'general-video',
    'hyperframes-animation', 'hyperframes-cli', 'hyperframes-core', 'hyperframes-creative',
    'hyperframes-keyframes', 'hyperframes-registry', 'hyperframes', 'media-use',
    'motion-graphics', 'music-to-video', 'pr-to-video', 'product-launch-video',
    'remotion-to-hyperframes', 'slideshow', 'talking-head-recut',
  ];
  const localMirrors = ['captions-overlay', 'changelog-video', 'cut-the-curve', 'motion-doctrine', 'oversized-cursor', 'seam-craft'];
  mkdirSync(join(root, '.codex-plugin'), { recursive: true });
  writeFileSync(join(root, '.codex-plugin', 'plugin.json'), JSON.stringify({ name: 'hyperframes-fixture', skills: './skills/' }));
  for (const slug of publicSlugs) {
    mkdirSync(join(root, 'skills', slug), { recursive: true });
    writeFileSync(join(root, 'skills', slug, 'SKILL.md'), `---\nname: ${slug}\n---\n`);
  }
  for (const slug of localMirrors) {
    for (const host of ['.agents', '.claude']) {
      mkdirSync(join(root, host, 'skills', slug, 'scripts'), { recursive: true });
      writeFileSync(join(root, host, 'skills', slug, 'SKILL.md'), `---\nname: ${slug}\n---\n`);
      writeFileSync(join(root, host, 'skills', slug, 'scripts', 'run.mjs'), 'export const fixture = true;\n');
    }
  }
  const result = discoverSubmissionSkills({ sourceDir: root, repository: 'heygen-com/hyperframes' });
  assert.deepEqual(result.stats, {
    physicalSkillFiles: 31,
    selectedSkillFiles: 19,
    ignoredSkillFiles: 12,
    identicalMirrorGroups: 6,
    conflictingMirrorGroups: 0,
  });
  assert.deepEqual(result.skills.map(({ slug }) => slug), publicSlugs);
  const plan = validateSelectionPlan({
    schemaVersion: 1,
    repository: 'heygen-com/hyperframes',
    sourceCommit: MAIN_SHA,
    scope: result.scope,
    skills: result.skills,
  });
  assert.equal(plan.skills.length, 19);
  assert.equal([plan].length, 1, '19 skills remain a single shard below the workflow threshold');
}));

for (const unsafe of ['bad\npath', 'bad\rpath', 'bad\u0001path', 'bad\u0085path', 'bad\u007fpath', '-leading', '../escape', '/absolute', 'quote;$(touch p)', 'windows:stream', 'CON.txt']) {
  test(`selection plans reject unsafe path ${JSON.stringify(unsafe)}`, () => {
    assert.throws(() => validateSelectionPlan({
      schemaVersion: 1,
      repository: 'example/repo',
      sourceCommit: MAIN_SHA,
      scope: { path: 'skills', reason: 'conventional_skills' },
      skills: [{ slug: 'demo', path: unsafe }],
    }));
  });
}

test('selection plan repository accepts canonical punctuation but rejects leading punctuation', () => {
  const base = {
    schemaVersion: 1,
    sourceCommit: MAIN_SHA,
    scope: { path: 'skills', reason: 'conventional_skills' },
    skills: [{ slug: 'demo', path: 'skills/demo' }],
  };
  assert.equal(validateSelectionPlan({ ...base, repository: 'owner.name/repo_name' }).repository, 'owner.name/repo_name');
  for (const repository of ['-owner/repo', 'owner/-repo', '.owner/repo', 'owner/.repo']) {
    assert.throws(() => validateSelectionPlan({ ...base, repository }));
  }
});

test('selection plans reject overlapping parent and child skill paths', () => {
  const base = {
    schemaVersion: 1,
    repository: 'starchild-ai-agent/official-skills',
    sourceCommit: MAIN_SHA,
    scope: { path: 'monad', reason: 'explicit_path' },
  };
  assert.throws(() => validateSelectionPlan({
    ...base,
    skills: [
      { slug: 'monad', path: 'monad' },
      { slug: 'addresses', path: 'monad/addresses' },
    ],
  }), /selection plan skill paths overlap: monad and monad\/addresses/);
});

test('repository-root discovery honors the Codex plugin publication scope and reports ignored mirrors', () => withDirectory((root) => {
  mkdirSync(join(root, '.codex-plugin'), { recursive: true });
  mkdirSync(join(root, 'skills', 'public-one'), { recursive: true });
  mkdirSync(join(root, 'skills', 'public-two'), { recursive: true });
  mkdirSync(join(root, '.agents', 'skills', 'local-only', 'scripts'), { recursive: true });
  mkdirSync(join(root, '.claude', 'skills', 'local-only', 'scripts'), { recursive: true });
  writeFileSync(join(root, '.codex-plugin', 'plugin.json'), JSON.stringify({
    name: 'fixture',
    skills: './skills/',
  }));
  writeFileSync(join(root, 'skills', 'public-one', 'SKILL.md'), '---\nname: public-one\n---\n');
  writeFileSync(join(root, 'skills', 'public-two', 'SKILL.md'), '---\nname: public-two\n---\n');
  for (const host of ['.agents', '.claude']) {
    writeFileSync(join(root, host, 'skills', 'local-only', 'SKILL.md'), '---\nname: local-only\n---\n');
    writeFileSync(join(root, host, 'skills', 'local-only', 'scripts', 'run.mjs'), 'export const local = true;\n');
  }

  const result = discoverSubmissionSkills({
    sourceDir: root,
    repository: 'example/repository',
  });

  assert.deepEqual(result.scope, { reason: 'codex_plugin_manifest', path: 'skills' });
  assert.deepEqual(result.skills, [
    { slug: 'public-one', path: 'skills/public-one' },
    { slug: 'public-two', path: 'skills/public-two' },
  ]);
  assert.deepEqual(result.stats, {
    physicalSkillFiles: 4,
    selectedSkillFiles: 2,
    ignoredSkillFiles: 2,
    identicalMirrorGroups: 1,
    conflictingMirrorGroups: 0,
  });
  assert.equal(result.mirrorGroups.length, 1);
  assert.deepEqual(result.mirrorGroups[0].paths, [
    '.agents/skills/local-only',
    '.claude/skills/local-only',
  ]);
  assert.equal(result.mirrorGroups[0].identical, true);
  assert.match(result.mirrorGroups[0].treeHash, /^[0-9a-f]{64}$/);
}));

test('repository-root discovery falls back to the conventional skills directory', () => withDirectory((root) => {
  mkdirSync(join(root, 'skills', 'public-skill'), { recursive: true });
  mkdirSync(join(root, '.agents', 'skills', 'local-only'), { recursive: true });
  writeFileSync(join(root, 'skills', 'public-skill', 'SKILL.md'), '# Public\n');
  writeFileSync(join(root, '.agents', 'skills', 'local-only', 'SKILL.md'), '# Local\n');

  const result = discoverSubmissionSkills({ sourceDir: root });

  assert.deepEqual(result.scope, { reason: 'conventional_skills', path: 'skills' });
  assert.deepEqual(result.skills, [{ slug: 'public-skill', path: 'skills/public-skill' }]);
}));

test('legacy repository fallback collapses only complete identical project-local mirrors', () => withDirectory((root) => {
  for (const host of ['.agents', '.claude']) {
    mkdirSync(join(root, host, 'skills', 'mirrored', 'scripts'), { recursive: true });
    writeFileSync(join(root, host, 'skills', 'mirrored', 'SKILL.md'), '---\nname: mirrored\n---\n');
    writeFileSync(join(root, host, 'skills', 'mirrored', 'scripts', 'run.mjs'), 'export const value = 1;\n');
  }

  const result = discoverSubmissionSkills({ sourceDir: root });

  assert.deepEqual(result.scope, { reason: 'repository_fallback', path: '.' });
  assert.deepEqual(result.skills, [{ slug: 'mirrored', path: '.agents/skills/mirrored' }]);
  assert.deepEqual(result.stats, {
    physicalSkillFiles: 2,
    selectedSkillFiles: 1,
    ignoredSkillFiles: 1,
    identicalMirrorGroups: 1,
    conflictingMirrorGroups: 0,
  });
}));

test('legacy repository fallback rejects project-local mirrors with different complete trees', () => withDirectory((root) => {
  for (const host of ['.agents', '.claude']) {
    mkdirSync(join(root, host, 'skills', 'mirrored', 'scripts'), { recursive: true });
    writeFileSync(join(root, host, 'skills', 'mirrored', 'SKILL.md'), '---\nname: mirrored\n---\n');
  }
  writeFileSync(join(root, '.agents', 'skills', 'mirrored', 'scripts', 'run.mjs'), 'export const value = 1;\n');
  writeFileSync(join(root, '.claude', 'skills', 'mirrored', 'scripts', 'run.mjs'), 'export const value = 2;\n');

  assert.throws(
    () => discoverSubmissionSkills({ sourceDir: root }),
    /conflicting project-local mirror slug: mirrored/,
  );
}));

test('an authority-scoped submission records a three-way partial local mirror as ignored diagnostics', () => withDirectory((root) => {
  mkdirSync(join(root, 'skills', 'public'), { recursive: true });
  writeFileSync(join(root, 'skills', 'public', 'SKILL.md'), '---\nname: public\n---\n');
  for (const host of ['.agents', '.claude', '.codex']) {
    mkdirSync(join(root, host, 'skills', 'local', 'scripts'), { recursive: true });
    writeFileSync(join(root, host, 'skills', 'local', 'SKILL.md'), '---\nname: local\n---\n');
    writeFileSync(join(root, host, 'skills', 'local', 'scripts', 'run.mjs'), host === '.codex' ? 'export const value = 2;\n' : 'export const value = 1;\n');
  }
  const result = discoverSubmissionSkills({ sourceDir: root });
  assert.deepEqual(result.skills, [{ slug: 'public', path: 'skills/public' }]);
  assert.equal(result.stats.conflictingMirrorGroups, 1);
  assert.equal(result.stats.ignoredSkillFiles, 3);
  assert.equal(result.mirrorGroups[0].identical, false);
}));

test('an explicit project-local path wins over repository publication manifests', () => withDirectory((root) => {
  mkdirSync(join(root, '.codex-plugin'), { recursive: true });
  mkdirSync(join(root, 'skills', 'public-skill'), { recursive: true });
  mkdirSync(join(root, '.agents', 'skills', 'local-only'), { recursive: true });
  writeFileSync(join(root, '.codex-plugin', 'plugin.json'), JSON.stringify({
    name: 'fixture',
    skills: './skills/',
  }));
  writeFileSync(join(root, 'skills', 'public-skill', 'SKILL.md'), '# Public\n');
  writeFileSync(join(root, '.agents', 'skills', 'local-only', 'SKILL.md'), '---\nname: local-only\n---\n');

  const result = discoverSubmissionSkills({
    sourceDir: root,
    skillPath: '.agents/skills/local-only',
    explicitPath: true,
  });

  assert.deepEqual(result.scope, { reason: 'explicit_path', path: '.agents/skills/local-only' });
  assert.deepEqual(result.skills, [{ slug: 'local-only', path: '.agents/skills/local-only' }]);
}));

test('repository-root discovery rejects an unsafe or missing manifest scope', () => withDirectory((root) => {
  mkdirSync(join(root, '.codex-plugin'), { recursive: true });
  writeFileSync(join(root, '.codex-plugin', 'plugin.json'), JSON.stringify({
    name: 'fixture',
    skills: '../outside',
  }));
  assert.throws(
    () => discoverSubmissionSkills({ sourceDir: root }),
    /Codex plugin skills path/,
  );

  writeFileSync(join(root, '.codex-plugin', 'plugin.json'), JSON.stringify({
    name: 'fixture',
    skills: './missing/',
  }));
  assert.throws(
    () => discoverSubmissionSkills({ sourceDir: root }),
    /declared publication scope does not exist/,
  );
}));

test('explicit paths with no SKILL.md fail while a repository-level empty scan remains an explicit no-op candidate', () => withDirectory((root) => {
  mkdirSync(join(root, 'empty'));
  assert.throws(() => discoverSubmissionSkills({
    sourceDir: root,
    skillPath: 'empty',
    explicitPath: true,
  }), /contains no SKILL\.md/);
  assert.deepEqual(discoverSubmissionSkills({ sourceDir: root }), {
    schemaVersion: 2,
    explicitPath: false,
    skillPath: '',
    scope: { reason: 'repository_fallback', path: '.' },
    stats: {
      physicalSkillFiles: 0,
      selectedSkillFiles: 0,
      ignoredSkillFiles: 0,
      identicalMirrorGroups: 0,
      conflictingMirrorGroups: 0,
    },
    mirrorGroups: [],
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
