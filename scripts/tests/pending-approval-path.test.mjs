import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const RESOLVER = join(REPO_ROOT, 'scripts', 'resolve-pending-skill-path.mjs');
const WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'on-pr-merge.yml');
const TEST_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'test-recalculate-scores.yml');

function writeSkill(root, pendingPath, { author = 'acme', name = 'demo-skill' } = {}) {
  const dir = join(root, pendingPath);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'SKILL.md'), `---\nname: ${name}\ndescription: test fixture\n---\n\n# Fixture\n`);
  writeFileSync(join(dir, 'skill-report.json'), `${JSON.stringify({
    schema_version: '2.0',
    skill: { author },
  }, null, 2)}\n`);
  return dir;
}

function resolvePending(root) {
  return spawnSync(process.execPath, [RESOLVER, '--repo', root, '--format', 'json'], {
    encoding: 'utf8',
  });
}

function withFixture(callback) {
  const root = mkdtempSync(join(tmpdir(), 'pending-approval-path-'));
  try {
    return callback(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function fileManifest(root) {
  const manifest = {};
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(path);
      } else if (entry.isFile()) {
        const key = relative(root, path).split('\\').join('/');
        manifest[key] = createHash('sha256').update(readFileSync(path)).digest('hex');
      }
    }
  };
  walk(root);
  return Object.fromEntries(Object.entries(manifest).sort(([a], [b]) => a.localeCompare(b)));
}

function manifestFromGit(commit, root) {
  const paths = spawnSync('git', ['ls-tree', '-rz', '--name-only', commit, '--', root], {
    cwd: REPO_ROOT,
    encoding: 'buffer',
  });
  assert.equal(paths.status, 0, paths.stderr.toString());
  const manifest = {};
  for (const rawPath of paths.stdout.toString('utf8').split('\0').filter(Boolean)) {
    const contents = spawnSync('git', ['show', `${commit}:${rawPath}`], {
      cwd: REPO_ROOT,
      encoding: 'buffer',
    });
    assert.equal(contents.status, 0, contents.stderr.toString());
    const key = rawPath.slice(`${root}/`.length);
    manifest[key] = createHash('sha256').update(contents.stdout).digest('hex');
  }
  return Object.fromEntries(Object.entries(manifest).sort(([a], [b]) => a.localeCompare(b)));
}

test('flat pending resolves author from trusted report and slug from SKILL frontmatter', () => withFixture((root) => {
  writeSkill(root, 'pending', {
    author: 'zx029w',
    name: 'zhuangxiu-fangan-zhenduan',
  });

  const result = resolvePending(root);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), [{
    source: 'pending',
    target: 'skills/zx029w/zhuangxiu-fangan-zhenduan',
    author: 'zx029w',
    slug: 'zhuangxiu-fangan-zhenduan',
    layout: 'flat',
  }]);
}));

test('legacy nested pending/author/slug remains compatible', () => withFixture((root) => {
  writeSkill(root, 'pending/101-skills/character-design-sheet', {
    author: '101-skills',
    name: 'character-design-sheet',
  });

  const result = resolvePending(root);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), [{
    source: 'pending/101-skills/character-design-sheet',
    target: 'skills/101-skills/character-design-sheet',
    author: '101-skills',
    slug: 'character-design-sheet',
    layout: 'nested',
  }]);
}));

test('flat and legacy nested pending skills can coexist, with nested moves first', () => withFixture((root) => {
  writeSkill(root, 'pending', { author: 'flat-owner', name: 'flat-skill' });
  writeSkill(root, 'pending/nested-owner/nested-skill', {
    author: 'nested-owner',
    name: 'nested-skill',
  });

  const result = resolvePending(root);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(
    JSON.parse(result.stdout).map(({ source, target, layout }) => ({ source, target, layout })),
    [
      {
        source: 'pending/nested-owner/nested-skill',
        target: 'skills/nested-owner/nested-skill',
        layout: 'nested',
      },
      {
        source: 'pending',
        target: 'skills/flat-owner/flat-skill',
        layout: 'flat',
      },
    ],
  );
}));

test('empty author and empty slug fail closed', () => {
  for (const fixture of [
    { author: '', name: 'valid-skill', expected: /author.*empty/i },
    { author: 'valid-author', name: '', expected: /slug.*empty/i },
  ]) {
    withFixture((root) => {
      writeSkill(root, 'pending', fixture);
      const result = resolvePending(root);
      assert.notEqual(result.status, 0, `fixture unexpectedly passed: ${JSON.stringify(fixture)}`);
      assert.match(result.stderr, fixture.expected);
    });
  }
});

test('reserved pending/pending destination fails closed', () => withFixture((root) => {
  writeSkill(root, 'pending', { author: 'pending', name: 'pending' });

  const result = resolvePending(root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /pending\/pending.*forbidden/i);
}));

test('author or slug path traversal fails closed', () => {
  for (const fixture of [
    { author: '../outside', name: 'valid-skill' },
    { author: 'valid-author', name: '../outside' },
    { author: 'valid-author', name: 'nested\\outside' },
  ]) {
    withFixture((root) => {
      writeSkill(root, 'pending', fixture);
      const result = resolvePending(root);
      assert.notEqual(result.status, 0, `fixture unexpectedly passed: ${JSON.stringify(fixture)}`);
      assert.match(result.stderr, /(author|slug).*(unsafe|path)/i);
    });
  }
});

test('Windows reserved names and aliasing suffixes fail closed', () => {
  for (const fixture of [
    { author: 'CON', name: 'valid-skill' },
    { author: 'con.txt', name: 'valid-skill' },
    { author: 'LPT1', name: 'valid-skill' },
    { author: 'valid-author.', name: 'valid-skill' },
    { author: 'valid-author ', name: 'valid-skill' },
    { author: 'valid-author', name: 'aux' },
    { author: 'valid-author', name: "'valid-skill '" },
  ]) {
    withFixture((root) => {
      writeSkill(root, 'pending', fixture);
      const result = resolvePending(root);
      assert.notEqual(result.status, 0, `fixture unexpectedly passed: ${JSON.stringify(fixture)}`);
      assert.match(result.stderr, /(reserved|trailing|unsafe path)/i);
    });
  }
});

test('workflow validates every pending skill with the resolver before moving it', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  assert.match(workflow, /resolve-pending-skill-path\.mjs/);
  assert.doesNotMatch(workflow, /cut -d['"]\/['"] -f2/);
  assert.match(workflow, /RESOLUTIONS=\$\(node .*--format tsv\)/);
});

test('CI tracks and syntax-checks the resolver and approval workflow', () => {
  const workflow = readFileSync(TEST_WORKFLOW, 'utf8');
  assert.match(workflow, /scripts\/resolve-pending-skill-path\.mjs/);
  assert.match(workflow, /\.github\/workflows\/on-pr-merge\.yml/);
  assert.match(workflow, /node --check scripts\/resolve-pending-skill-path\.mjs/);
});

test('all misplaced flat approvals are migrated byte-for-byte without overwriting each other', () => {
  const misplaced = join(REPO_ROOT, 'skills', 'pending', 'pending');
  const migrations = [
    {
      target: 'skills/zx029w/zhuangxiu-fangan-zhenduan',
      sourceCommit: '55cd0348a52ef7dfd14434b3f8905140e247b3fb',
      fileCount: 11,
    },
    {
      target: 'skills/wuhenwt/zhuangxiu-yusuan-jisuanqi',
      sourceCommit: '28651d7af52ddbe5cf5bda460ae8a7b943a3c1cd',
      fileCount: 12,
    },
    {
      target: 'skills/xia0229/yinbi-gongcheng-quanliucheng-guanzhuanjia',
      sourceCommit: '441dc53dabf71ef7b525ad93d32a9575d8e6024b',
      fileCount: 9,
    },
  ];

  assert.equal(existsSync(misplaced), false, 'misplaced skills/pending/pending must be removed');
  for (const migration of migrations) {
    const target = join(REPO_ROOT, migration.target);
    assert.equal(existsSync(target), true, `corrected path must exist: ${migration.target}`);
    const expected = manifestFromGit(migration.sourceCommit, 'skills/pending/pending');
    const actual = fileManifest(target);
    assert.equal(Object.keys(actual).length, migration.fileCount, migration.target);
    assert.deepEqual(actual, expected, migration.target);
  }
});
