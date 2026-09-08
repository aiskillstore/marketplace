import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import {
  materializeChangedSkills,
  parseChangedSkillPaths,
} from '../materialize-changed-skills.mjs';

function git(repositoryRoot, args) {
  return execFileSync('git', args, { cwd: repositoryRoot, encoding: 'utf8' }).trim();
}

function write(repositoryRoot, relativePath, contents) {
  const fullPath = join(repositoryRoot, relativePath);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

function makeRepository() {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'materialize-skills-'));
  git(repositoryRoot, ['init', '--initial-branch=main']);
  git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
  git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);

  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v1\n');
  write(repositoryRoot, 'skills/owner/demo/examples/skill-report.json', '{"example":true}\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":1}\n');
  write(repositoryRoot, 'skills/owner/untouched/SKILL.md', '# Untouched\n');
  write(repositoryRoot, 'skills/owner/untouched/skill-report.json', '{"revision":1}\n');
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', 'base']);

  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v2\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":2}\n');
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', 'updated report']);

  return { repositoryRoot, commit: git(repositoryRoot, ['rev-parse', 'HEAD']) };
}

test('parses unique repository-relative skill paths and rejects unsafe inputs', () => {
  assert.deepEqual(
    parseChangedSkillPaths('owner/zeta,owner/alpha owner/zeta'),
    ['owner/alpha', 'owner/zeta'],
  );

  for (const invalid of [
    '',
    '/owner/demo',
    'skills/owner/demo',
    '../owner/demo',
    'owner/../demo',
    'owner\\demo',
  ]) {
    assert.throws(() => parseChangedSkillPaths(invalid), /no changed|invalid changed/);
  }
});

test('restores only selected paths from an exact commit through skip-worktree state', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v3 at mutable HEAD\n');
    write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":3}\n');
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'newer mutable head']);

    const demoFiles = [
      'skills/owner/demo/SKILL.md',
      'skills/owner/demo/skill-report.json',
    ];
    git(repositoryRoot, ['update-index', '--skip-worktree', ...demoFiles]);
    rmSync(join(repositoryRoot, 'skills/owner/demo'), { recursive: true });

    write(repositoryRoot, 'skills/owner/untouched/local-only.txt', 'keep me\n');
    write(repositoryRoot, 'skills/owner/demo/stale-untracked.txt', 'remove me\n');

    assert.deepEqual(
      materializeChangedSkills({ repositoryRoot, commit, skills: ['owner/demo'] }),
      ['skills/owner/demo'],
    );
    assert.equal(readFileSync(join(repositoryRoot, 'skills/owner/demo/SKILL.md'), 'utf8'), '# Demo v2\n');
    assert.equal(
      readFileSync(join(repositoryRoot, 'skills/owner/demo/skill-report.json'), 'utf8'),
      '{"revision":2}\n',
    );
    assert.equal(existsSync(join(repositoryRoot, 'skills/owner/demo/stale-untracked.txt')), false);
    assert.equal(
      readFileSync(join(repositoryRoot, 'skills/owner/untouched/local-only.txt'), 'utf8'),
      'keep me\n',
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('fails before mutation when a selected path has no published report at the pinned commit', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    write(repositoryRoot, 'skills/owner/not-published/local-only.txt', 'preserve on preflight failure\n');

    assert.throws(
      () => materializeChangedSkills({
        repositoryRoot,
        commit,
        skills: ['owner/demo', 'owner/not-published'],
      }),
      /published report is missing/,
    );
    assert.equal(
      readFileSync(join(repositoryRoot, 'skills/owner/not-published/local-only.txt'), 'utf8'),
      'preserve on preflight failure\n',
    );
    assert.equal(readFileSync(join(repositoryRoot, 'skills/owner/demo/SKILL.md'), 'utf8'), '# Demo v2\n');
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('rejects symbolic commit names instead of materializing mutable HEAD', () => {
  const { repositoryRoot } = makeRepository();
  try {
    assert.throws(
      () => materializeChangedSkills({ repositoryRoot, commit: 'HEAD', skills: ['owner/demo'] }),
      /exact 40-character SHA/,
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('rejects reserved published identities before materialization', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    assert.throws(
      () => materializeChangedSkills({ repositoryRoot, commit, skills: ['pending/demo'] }),
      /invalid or reserved path identity/,
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('selected report lookup does not enumerate or validate unrelated report trees', () => {
  const { repositoryRoot } = makeRepository();
  try {
    write(repositoryRoot, 'skills/unrelated/nested/invalid/skill-report.json', '{}\n');
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'unrelated report outside canonical roots']);
    const commit = git(repositoryRoot, ['rev-parse', 'HEAD']);
    assert.deepEqual(materializeChangedSkills({ repositoryRoot, commit, skills: ['owner/demo'] }), ['skills/owner/demo']);
    assert.equal(readFileSync(join(repositoryRoot, 'skills/owner/demo/skill-report.json'), 'utf8'), '{"revision":2}\n');
  } finally { rmSync(repositoryRoot, { recursive: true, force: true }); }
});

test('partial clone prefetches selected blobs together and preserves unrelated sparse content', () => {
  const { repositoryRoot: source, commit } = makeRepository();
  const clone = mkdtempSync(join(tmpdir(), 'materialize-partial-'));
  try {
    git(source, ['config', 'uploadpack.allowFilter', 'true']);
    git(source, ['config', 'uploadpack.allowAnySHA1InWant', 'true']);
    git(clone, ['clone', '--filter=blob:none', '--no-checkout', `file://${source}`, '.']);
    git(clone, ['sparse-checkout', 'set', '--no-cone', '/README.md']);
    git(clone, ['checkout', 'main']);
    // Frozen preflight may have already downloaded some selected blobs.
    git(clone, ['cat-file', '-p', `${commit}:skills/owner/demo/SKILL.md`]);
    const beforeHead = git(clone, ['rev-parse', 'HEAD']);
    const trace = join(tmpdir(), `materialize-fetch-${process.pid}.jsonl`);
    const previous = process.env.GIT_TRACE2_EVENT;
    process.env.GIT_TRACE2_EVENT = trace;
    try { materializeChangedSkills({repositoryRoot:clone,commit,skills:['owner/demo']}); }
    finally { if(previous === undefined)delete process.env.GIT_TRACE2_EVENT;else process.env.GIT_TRACE2_EVENT=previous; }
    const commands=readFileSync(trace,'utf8').trim().split('\n').map(JSON.parse).filter(e=>e.event==='start').map(e=>e.argv);
    rmSync(trace,{force:true});
    assert.ok(commands.find(args=>args.includes('fetch'))?.includes('fetch.negotiationAlgorithm=noop'), 'blob wants must not enter commit negotiation');
    assert.equal(commands.filter(args=>args.includes('fetch')).length,1,'one bulk fetch; restore must not trigger per-blob fetches');
    assert.equal(readFileSync(join(clone,'skills/owner/demo/SKILL.md'),'utf8'),'# Demo v2\n');
    assert.equal(existsSync(join(clone,'skills/owner/untouched/SKILL.md')),false);
    assert.equal(git(clone,['rev-parse','HEAD']),beforeHead);
  } finally { rmSync(source,{recursive:true,force:true});rmSync(clone,{recursive:true,force:true}); }
});
