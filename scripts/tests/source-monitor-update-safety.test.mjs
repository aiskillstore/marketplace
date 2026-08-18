import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, relative, sep } from 'node:path';
import { test } from 'node:test';

import { calculateCanonicalTreeHash } from '../resolve-approved-submission.mjs';
import { verifySourceMonitorUpdate } from '../verify-source-monitor-update.mjs';

function write(path, content) {
  mkdirSync(join(path, '..'), { recursive: true });
  writeFileSync(path, content);
}

function report({
  slug,
  sourceUrl = `https://github.com/example/repo/tree/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/skills/${slug}`,
  sourceRef = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
  contentHash = `${slug.charCodeAt(0).toString(16).padStart(2, '0')}`.repeat(32),
  treeHash = `${slug.charCodeAt(slug.length - 1).toString(16).padStart(2, '0')}`.repeat(32),
  riskLevel = 'safe',
  isBlocked = false,
  safeToPublish = true,
  license = 'MIT',
} = {}) {
  return JSON.stringify({
    schema_version: '2.0',
    meta: {
      slug,
      source_url: sourceUrl,
      source_ref: sourceRef,
      upstream_commit_sha: sourceRef,
      content_hash: contentHash,
      tree_hash: treeHash,
    },
    skill: { name: slug, license },
    security_audit: {
      risk_level: riskLevel,
      is_blocked: isBlocked,
      safe_to_publish: safeToPublish,
      agent_auto_install_policy: isBlocked ? 'blocked' : 'allowed',
      manual_install_policy: isBlocked ? 'allowed_with_warning' : 'allowed',
    },
  }, null, 2);
}

function bindReport(root, directory, options) {
  const skillPath = join(directory, 'SKILL.md');
  const skillDirectory = relative(root, directory).split(sep).join('/');
  write(join(directory, 'skill-report.json'), report({
    ...options,
    contentHash: createHash('sha256').update(readFileSync(skillPath)).digest('hex'),
    treeHash: calculateCanonicalTreeHash(root, skillDirectory),
  }));
}

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'source-monitor-update-safety-'));
  execFileSync('git', ['init', '-q'], { cwd: root });
  execFileSync('git', ['config', 'user.name', 'Fixture'], { cwd: root });
  execFileSync('git', ['config', 'user.email', 'fixture@example.com'], { cwd: root });
  return root;
}

function commit(root) {
  execFileSync('git', ['add', '.'], { cwd: root });
  execFileSync('git', ['commit', '-qm', 'fixture'], { cwd: root });
}

test('accepts a coherent source-monitor payload update', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'owner', 'coherent');
    write(join(dir, 'SKILL.md'), '# Coherent\n\nSee [guide](references/guide.md) and `ooxml/scripts/pack.py`.\n');
    write(join(dir, 'references', 'guide.md'), '# Old\n');
    write(join(dir, 'ooxml', 'scripts', 'pack.py'), '# pack\n');
    bindReport(root, dir, { slug: 'owner-coherent' });
    commit(root);

    write(join(dir, 'references', 'guide.md'), '# New\n');
    bindReport(root, dir, {
      slug: 'owner-coherent',
      sourceRef: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
      sourceUrl: 'https://github.com/example/repo/tree/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/skills/coherent',
    });

    const result = verifySourceMonitorUpdate({ repositoryRoot: root });
    assert.equal(result.changedSkills, 1);
    assert.equal(result.deletedPaths, 0);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('accepts a coherent flat published skill update', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'flat-skill');
    write(join(dir, 'SKILL.md'), '# Flat\n');
    write(join(dir, 'references', 'guide.md'), '# Old\n');
    bindReport(root, dir, { slug: 'flat-skill' });
    commit(root);

    write(join(dir, 'references', 'guide.md'), '# New\n');
    bindReport(root, dir, { slug: 'flat-skill' });

    const result = verifySourceMonitorUpdate({ repositoryRoot: root });
    assert.equal(result.changedSkills, 1);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rejects deletion of a path still referenced by SKILL.md', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'owner', 'dangling');
    write(join(dir, 'SKILL.md'), '# Dangling\n\nFollow `references/guide.md`.\n');
    write(join(dir, 'references', 'guide.md'), '# Guide\n');
    bindReport(root, dir, { slug: 'owner-dangling' });
    commit(root);

    rmSync(join(dir, 'references', 'guide.md'));
    bindReport(root, dir, {
      slug: 'owner-dangling',
      sourceRef: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
      sourceUrl: 'https://github.com/example/repo/tree/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/skills/dangling',
    });

    assert.throws(
      () => verifySourceMonitorUpdate({ repositoryRoot: root }),
      /SKILL\.md references missing path: skills\/owner\/dangling\/references\/guide\.md/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rejects a package lifecycle or bin target that no longer exists', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'owner', 'package-skill');
    write(join(dir, 'SKILL.md'), '# Package\n');
    write(join(dir, 'scripts', 'install.js'), 'console.log("install");\n');
    write(join(dir, 'package.json'), JSON.stringify({
      bin: { 'package-skill': 'scripts/install.js' },
      scripts: { postinstall: 'node scripts/install.js' },
      files: ['scripts/install.js'],
      license: 'Apache-2.0',
    }, null, 2));
    bindReport(root, dir, { slug: 'owner-package-skill', license: 'Apache-2.0' });
    commit(root);

    rmSync(join(dir, 'scripts', 'install.js'));
    bindReport(root, dir, {
      slug: 'owner-package-skill',
      sourceRef: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
      sourceUrl: 'https://github.com/example/repo/tree/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/skills/package-skill',
      license: 'MIT',
    });

    assert.throws(
      () => verifySourceMonitorUpdate({ repositoryRoot: root }),
      /package target is missing: skills\/owner\/package-skill\/scripts\/install\.js/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rejects contradictory audit policy between flat and namespaced identical source trees', () => {
  const root = fixture();
  try {
    const shared = {
      sourceUrl: 'https://github.com/example/repo/tree/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/skill',
      sourceRef: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      contentHash: '1'.repeat(64),
      treeHash: '2'.repeat(64),
    };
    for (const [slug, segments] of [
      ['flat-alias-one', ['flat-alias-one']],
      ['owner-alias-two', ['owner', 'alias-two']],
    ]) {
      const dir = join(root, 'skills', ...segments);
      write(join(dir, 'SKILL.md'), '# Alias\n');
      bindReport(root, dir, { slug, ...shared, riskLevel: 'safe' });
    }
    commit(root);

    const changed = join(root, 'skills', 'flat-alias-one');
    bindReport(root, changed, { slug: 'flat-alias-one', ...shared, riskLevel: 'medium' });

    assert.throws(
      () => verifySourceMonitorUpdate({ repositoryRoot: root }),
      /identical source tree has contradictory audit policy: flat-alias-one, owner-alias-two/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rejects an unreviewed destructive shrink of a published skill', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'owner', 'shrunk');
    write(join(dir, 'SKILL.md'), '# Shrunk\n');
    for (let index = 0; index < 10; index += 1) {
      write(join(dir, 'references', `${index}.md`), `# ${index}\n`);
    }
    bindReport(root, dir, { slug: 'owner-shrunk' });
    commit(root);

    for (let index = 0; index < 9; index += 1) {
      rmSync(join(dir, 'references', `${index}.md`));
    }
    bindReport(root, dir, {
      slug: 'owner-shrunk',
      sourceRef: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
      sourceUrl: 'https://github.com/example/repo/tree/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/skills/shrunk',
    });

    assert.throws(
      () => verifySourceMonitorUpdate({ repositoryRoot: root }),
      /destructive source update requires explicit review: skills\/owner\/shrunk deleted=9 baseline=12/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rejects an untracked change outside published skill directories', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'owner', 'bounded');
    write(join(dir, 'SKILL.md'), '# Bounded\n');
    bindReport(root, dir, { slug: 'owner-bounded' });
    commit(root);

    write(join(dir, 'SKILL.md'), '# Bounded\n\nUpdated.\n');
    bindReport(root, dir, { slug: 'owner-bounded' });
    write(join(root, 'scripts', 'injected.mjs'), 'throw new Error("unexpected");\n');

    assert.throws(
      () => verifySourceMonitorUpdate({ repositoryRoot: root }),
      /source monitor changed path outside published skills: scripts\/injected\.mjs/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rejects a payload-only update with a stale report tree hash', () => {
  const root = fixture();
  try {
    const dir = join(root, 'skills', 'owner', 'stale-binding');
    write(join(dir, 'SKILL.md'), '# Stale binding\n');
    write(join(dir, 'references', 'guide.md'), '# Old\n');
    bindReport(root, dir, { slug: 'owner-stale-binding' });
    commit(root);

    write(join(dir, 'references', 'guide.md'), '# New\n');

    assert.throws(
      () => verifySourceMonitorUpdate({ repositoryRoot: root }),
      /source monitor must rebind skill report: skills\/owner\/stale-binding/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
