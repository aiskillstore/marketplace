import assert from 'node:assert/strict';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { basename, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { test } from 'node:test';

const workflow = readFileSync('.github/workflows/monitor-skill-sources.yml', 'utf8');
const runtimeFiles = [
  '.github/actions/download-skillstore-cli/action.yml',
  '.github/workflows/monitor-skill-sources.yml',
];

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: 'utf8', ...options });
  if (result.status !== 0 && !options.allowFailure) {
    assert.fail(`${command} ${args.join(' ')} failed (${result.status})\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`);
  }
  return result;
}

function extractRunBlock(stepName) {
  const lines = workflow.split('\n');
  const nameIndex = lines.findIndex((line) => line.trim() === `- name: ${stepName}`);
  assert.notEqual(nameIndex, -1, `missing workflow step: ${stepName}`);
  const stepIndent = lines[nameIndex].search(/\S/);
  let runIndex = -1;
  for (let index = nameIndex + 1; index < lines.length; index += 1) {
    const indent = lines[index].search(/\S/);
    if (indent !== -1 && indent <= stepIndent) break;
    if (lines[index].trim() === 'run: |') {
      runIndex = index;
      break;
    }
  }
  assert.notEqual(runIndex, -1, `missing run block for: ${stepName}`);
  const runIndent = lines[runIndex].search(/\S/);
  const body = [];
  for (let index = runIndex + 1; index < lines.length; index += 1) {
    const indent = lines[index].search(/\S/);
    if (indent !== -1 && indent <= runIndent) break;
    body.push(lines[index].length > runIndent + 2 ? lines[index].slice(runIndent + 2) : '');
  }
  return body.join('\n');
}

function createFixture() {
  const root = mkdtempSync(join(tmpdir(), 'source-monitor-runtime-'));
  const seed = join(root, 'seed');
  const origin = join(root, 'origin.git');
  const runnerWorkspace = join(root, 'runner-workspace');
  const workspace = join(runnerWorkspace, 'marketplace');
  const runnerTemp = join(root, 'runner-temp');
  const diagnosticDir = join(runnerTemp, 'source-monitor-diagnostics-test');
  mkdirSync(seed, { recursive: true });
  mkdirSync(runnerWorkspace, { recursive: true });
  mkdirSync(runnerTemp, { recursive: true });
  run('git', ['init', '-q', seed]);
  run('git', ['-C', seed, 'config', 'user.name', 'Fixture']);
  run('git', ['-C', seed, 'config', 'user.email', 'fixture@example.com']);
  const files = {
    '.github/actions/download-skillstore-cli/action.yml': 'name: fixture action\n',
    '.github/workflows/monitor-skill-sources.yml': 'name: fixture workflow\n',
    'README.md': 'fixture\n',
  };
  for (const [path, content] of Object.entries(files)) {
    const absolute = join(seed, path);
    mkdirSync(join(absolute, '..'), { recursive: true });
    writeFileSync(absolute, content);
  }
  run('git', ['-C', seed, 'add', '.']);
  run('git', ['-C', seed, 'commit', '-qm', 'fixture']);
  const head = run('git', ['-C', seed, 'rev-parse', 'HEAD']).stdout.trim();
  run('git', ['clone', '--bare', '-q', seed, origin]);
  run('git', ['clone', '-q', origin, workspace]);
  return { root, origin, runnerWorkspace, runnerTemp, workspace, diagnosticDir, head };
}

test('source monitor clears inherited sparse state and verifies an immutable full checkout', () => {
  const fixture = createFixture();
  try {
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'init', '--cone']);
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'set', '.github/workflows']);
    assert.equal(existsSync(join(fixture.workspace, runtimeFiles[0])), false);
    writeFileSync(join(fixture.workspace, 'stale-runner-file'), 'stale\n');

    run('bash', ['-c', extractRunBlock('Clear inherited source monitor checkout')], {
      cwd: fixture.workspace,
      env: {
        ...process.env,
        GITHUB_WORKSPACE: fixture.workspace,
        RUNNER_WORKSPACE: fixture.runnerWorkspace,
        RUNNER_TEMP: fixture.runnerTemp,
        GITHUB_REPOSITORY: `aiskillstore/${basename(fixture.workspace)}`,
        DIAGNOSTIC_DIR: fixture.diagnosticDir,
      },
    });

    assert.deepEqual(readdirSync(fixture.workspace), []);
    assert.match(readFileSync(join(fixture.diagnosticDir, 'pre-checkout.txt'), 'utf8'), /skip_worktree_count=/);
    run('git', ['clone', '-q', '--no-local', fixture.origin, fixture.workspace]);
    run('bash', ['-c', extractRunBlock('Verify immutable source monitor runtime')], {
      cwd: fixture.workspace,
      env: {
        ...process.env,
        GITHUB_WORKSPACE: fixture.workspace,
        EXPECTED_WORKFLOW_SHA: fixture.head,
        DIAGNOSTIC_DIR: fixture.diagnosticDir,
      },
    });
    assert.match(readFileSync(join(fixture.diagnosticDir, 'post-checkout.txt'), 'utf8'), new RegExp(`actual_head=${fixture.head}`));
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('source monitor runtime preflight rejects missing, modified, symlinked, skip-worktree, and wrong-head files', () => {
  const fixture = createFixture();
  try {
    const preflight = extractRunBlock('Verify immutable source monitor runtime');
    const base = {
      cwd: fixture.workspace,
      env: {
        ...process.env,
        GITHUB_WORKSPACE: fixture.workspace,
        EXPECTED_WORKFLOW_SHA: fixture.head,
        DIAGNOSTIC_DIR: fixture.diagnosticDir,
      },
    };
    for (const file of runtimeFiles) {
      const absolute = join(fixture.workspace, file);
      rmSync(absolute);
      assert.notEqual(run('bash', ['-c', preflight], { ...base, allowFailure: true }).status, 0);
      run('git', ['-C', fixture.workspace, 'checkout', '--', file]);
      writeFileSync(absolute, 'tampered\n');
      assert.notEqual(run('bash', ['-c', preflight], { ...base, allowFailure: true }).status, 0);
      run('git', ['-C', fixture.workspace, 'checkout', '--', file]);
      rmSync(absolute);
      symlinkSync(join(fixture.workspace, 'README.md'), absolute);
      assert.notEqual(run('bash', ['-c', preflight], { ...base, allowFailure: true }).status, 0);
      rmSync(absolute);
      run('git', ['-C', fixture.workspace, 'checkout', '--', file]);
    }
    run('git', ['-C', fixture.workspace, 'update-index', '--skip-worktree', runtimeFiles[0]]);
    assert.notEqual(run('bash', ['-c', preflight], { ...base, allowFailure: true }).status, 0);
    run('git', ['-C', fixture.workspace, 'update-index', '--no-skip-worktree', runtimeFiles[0]]);
    assert.notEqual(run('bash', ['-c', preflight], {
      ...base,
      env: { ...base.env, EXPECTED_WORKFLOW_SHA: '0000000000000000000000000000000000000000' },
      allowFailure: true,
    }).status, 0);
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('source monitor binds checkout and artifacts to immutable runtime evidence', () => {
  assert.ok(workflow.indexOf('name: Initialize source monitor diagnostics') < workflow.indexOf('name: Generate GitHub App Token'));
  assert.match(workflow, /ref: \$\{\{ github\.workflow_sha \}\}/);
  assert.match(workflow, /fetch-depth: 1/);
  assert.match(workflow, /persist-credentials: false/);
  assert.match(workflow, /minimum-version: 2\.14\.5/);
  assert.match(workflow, /require-checksum: true/);
  assert.match(workflow, /\$\{\{ runner\.temp \}\}\/source-monitor-diagnostics-\$\{\{ github\.run_id \}\}\//);
  assert.match(workflow, /name: Upload monitor evidence\n\s+if: always\(\)/);
  for (const file of runtimeFiles) assert.match(workflow, new RegExp(file.replaceAll('.', '\\.')));
});
