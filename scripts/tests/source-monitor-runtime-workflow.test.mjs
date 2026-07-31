import assert from 'node:assert/strict';
import {
  chmodSync,
  copyFileSync,
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
import { calculateCanonicalTreeHash } from '../resolve-approved-submission.mjs';

const workflow = readFileSync('.github/workflows/monitor-skill-sources.yml', 'utf8');
const runtimeFiles = [
  '.github/actions/download-skillstore-cli/action.yml',
  '.github/workflows/monitor-skill-sources.yml',
  'scripts/rebind-skill-report-hashes.mjs',
  'scripts/verify-source-monitor-selection.mjs',
];

test('source monitor shares the production governance writer mutex', () => {
  assert.match(workflow, /scan:\n(?:.*\n){0,8}\s+concurrency:\n\s+# Source monitoring[\s\S]{0,260}group: production-skill-score-writes/);
  assert.match(workflow, /group: production-skill-score-writes\n\s+cancel-in-progress: false/);
});

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
    'scripts/rebind-skill-report-hashes.mjs': 'export const fixture = true;\n',
    'scripts/verify-source-monitor-selection.mjs': 'export const fixture = true;\n',
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
  const cleanup = extractRunBlock('Clear inherited source monitor checkout');
  assert.doesNotMatch(cleanup, /sparse-checkout disable|git reset --hard/);
  const fixture = createFixture();
  try {
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'init', '--cone']);
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'set', '.github/workflows']);
    assert.equal(existsSync(join(fixture.workspace, runtimeFiles[0])), false);
    writeFileSync(join(fixture.workspace, 'stale-runner-file'), 'stale\n');

    run('bash', ['-c', cleanup], {
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
  assert.match(workflow, /version: 2\.15\.8/);
  assert.match(workflow, /minimum-version: 2\.14\.5/);
  assert.match(workflow, /require-checksum: true/);
  assert.match(workflow, /\$\{\{ runner\.temp \}\}\/source-monitor-diagnostics-\$\{\{ github\.run_id \}\}\//);
  assert.match(workflow, /name: Upload monitor evidence\n\s+if: always\(\)/);
  for (const file of runtimeFiles) assert.match(workflow, new RegExp(file.replaceAll('.', '\\.')));
});

test('source monitor verifies every explicit requested slug before later workflow steps', () => {
  const monitor = extractRunBlock('Run source monitor');
  assert.match(monitor, /A slug-scoped update PR requires expected_upstream_commit/);
  assert.match(monitor, /if \[ "\$CREATE_PR" = "true" \] && \[ -n "\$SLUGS" \]; then/);
  assert.match(monitor, /CMD\+=\(--updateLocal\)/);
  assert.match(monitor, /if \[ -n "\$SLUGS" \]; then/);
  assert.match(monitor, /node "\$GITHUB_WORKSPACE\/scripts\/verify-source-monitor-selection\.mjs"/);
  assert.match(monitor, /--requested "\$SLUGS"/);
  assert.match(monitor, /--jsonl "\$JSONL_FILE"/);
  assert.match(monitor, /--expected-upstream-commit "\$EXPECTED_UPSTREAM_COMMIT"/);
  assert.ok(
    monitor.indexOf('verify-source-monitor-selection.mjs') < monitor.indexOf('jsonl_file=$JSONL_FILE'),
    'explicit selection verification must run before publishing step outputs',
  );
});

test('source monitor binds every changed report to its packaged tree before creating a PR', () => {
  const binding = extractRunBlock('Bind source monitor reports to packaged trees');
  assert.match(binding, /git diff --no-renames --name-only -z --diff-filter=ACMRT HEAD/);
  assert.match(binding, /skills\/\*\*\/SKILL\.md/);
  assert.match(binding, /skills\/\*\*\/skill-report\.json/);
  assert.match(binding, /scripts\/rebind-skill-report-hashes\.mjs/);
  assert.match(binding, /--skill-paths-file/);
  assert.match(binding, /--diff-filter=D/);
  assert.ok(
    workflow.indexOf('name: Bind source monitor reports to packaged trees')
      < workflow.indexOf('name: Create source monitor PR'),
    'packaged report hashes must be rebound before the source monitor PR is created',
  );
});

test('source monitor commits upstream files hidden by a copied skill .gitignore', () => {
  const root = mkdtempSync(join(tmpdir(), 'source-monitor-ignored-files-'));
  const workspace = join(root, 'workspace');
  const skillDirectory = 'skills/owner/demo';
  const absoluteSkillDirectory = join(workspace, skillDirectory);
  try {
    mkdirSync(join(workspace, 'scripts'), { recursive: true });
    mkdirSync(absoluteSkillDirectory, { recursive: true });
    copyFileSync('scripts/rebind-skill-report-hashes.mjs', join(workspace, 'scripts/rebind-skill-report-hashes.mjs'));
    copyFileSync('scripts/resolve-approved-submission.mjs', join(workspace, 'scripts/resolve-approved-submission.mjs'));
    writeFileSync(join(absoluteSkillDirectory, 'SKILL.md'), '# old\n');
    writeFileSync(join(absoluteSkillDirectory, 'skill-report.json'), `${JSON.stringify({
      meta: {
        source_url: 'https://github.com/owner/repository',
        source_ref: 'main',
        content_hash: 'old',
        tree_hash: 'old',
      },
    })}\n`);
    run('git', ['init', '-q', workspace]);
    run('git', ['-C', workspace, 'config', 'user.name', 'Fixture']);
    run('git', ['-C', workspace, 'config', 'user.email', 'fixture@example.com']);
    run('git', ['-C', workspace, 'add', '.']);
    run('git', ['-C', workspace, 'commit', '-qm', 'fixture']);

    writeFileSync(join(absoluteSkillDirectory, '.gitignore'), 'references/\n');
    writeFileSync(join(absoluteSkillDirectory, 'SKILL.md'), '# updated\n');
    mkdirSync(join(absoluteSkillDirectory, 'references'));
    writeFileSync(join(absoluteSkillDirectory, 'references', 'ignored.md'), 'tracked upstream resource\n');

    run('bash', ['-c', extractRunBlock('Bind source monitor reports to packaged trees')], {
      cwd: workspace,
      env: { ...process.env, RUNNER_TEMP: root, GITHUB_RUN_ID: '1234', DRY_RUN: 'false', CREATE_PR: 'true' },
    });

    const staged = run('git', ['-C', workspace, 'diff', '--cached', '--name-only']).stdout.trim().split('\n');
    assert.ok(staged.includes(`${skillDirectory}/references/ignored.md`));
    assert.ok(staged.includes(`${skillDirectory}/skill-report.json`));
    run('git', ['-C', workspace, 'commit', '-qm', 'source monitor update']);
    const committed = run('git', ['-C', workspace, 'ls-tree', '-r', '--name-only', 'HEAD']).stdout.trim().split('\n');
    assert.ok(committed.includes(`${skillDirectory}/references/ignored.md`));
    const report = JSON.parse(readFileSync(join(absoluteSkillDirectory, 'skill-report.json'), 'utf8'));
    assert.equal(report.meta.tree_hash, calculateCanonicalTreeHash(workspace, skillDirectory));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('final summary reports scoped local updates as no-write while scheduled scans keep writes enabled', () => {
  const summary = extractRunBlock('Final summary').replaceAll('${{ github.run_id }}', '1234');
  const cases = [
    {
      name: 'scoped local update PR',
      env: { DRY_RUN: 'false', CREATE_PR: 'true', SLUGS: 'owner-one' },
      expected: '- Supabase writes: disabled',
    },
    {
      name: 'scheduled full scan',
      env: { DRY_RUN: 'false', CREATE_PR: 'true', SLUGS: '' },
      expected: '- Supabase writes: enabled',
    },
  ];

  for (const fixture of cases) {
    const root = mkdtempSync(join(tmpdir(), 'source-monitor-summary-'));
    try {
      const output = join(root, 'summary.md');
      run('bash', ['-c', summary], {
        env: {
          ...process.env,
          ...fixture.env,
          GITHUB_STEP_SUMMARY: output,
          CONCURRENCY: '8',
          WRITE_CONCURRENCY: '2',
          MAX_UPDATES_PER_RUN: '100',
          CHECKOUT_CACHE_DIR: '/tmp/source-monitor-cache',
          ARCHIVE_MISSING: 'false',
          DELETE_ARCHIVED: 'false',
        },
      });
      assert.match(readFileSync(output, 'utf8'), new RegExp(fixture.expected), fixture.name);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  }
});

test('a scoped update PR requires a pinned upstream commit and does not write Supabase', () => {
  const root = mkdtempSync(join(tmpdir(), 'source-monitor-scoped-update-'));
  const workspace = join(root, 'workspace');
  const argsFile = join(root, 'args.txt');
  const expectedCommit = '458df4c41294655f76e551100a9b634114209bb9';
  try {
    mkdirSync(join(workspace, 'scripts'), { recursive: true });
    copyFileSync('scripts/verify-source-monitor-selection.mjs', join(workspace, 'scripts', 'verify-source-monitor-selection.mjs'));
    const skillDirectory = join(workspace, 'skills', 'owner', 'one');
    const reportPath = join(skillDirectory, 'skill-report.json');
    const skillPath = join(skillDirectory, 'SKILL.md');
    mkdirSync(skillDirectory, { recursive: true });
    writeFileSync(reportPath, '{"meta":{"slug":"owner-one","upstream_commit_sha":null}}\n');
    writeFileSync(skillPath, '# old\n');
    const fakeCli = join(workspace, 'skillstore-cli');
    writeFileSync(fakeCli, `#!/usr/bin/env bash
set -euo pipefail
if [ "\${1:-}" = "--version" ]; then
  echo "2.15.0"
  exit 0
fi
if [ "\${1:-}" = "skill" ] && [ "\${2:-}" = "monitor-upstream" ] && [ "\${3:-}" = "--help" ]; then
  echo "--writeConcurrency --checkoutCacheDir"
  exit 0
fi
printf '%s\\n' "$*" > "$FAKE_ARGS"
jsonl=''
summary=''
while [ "$#" -gt 0 ]; do
  case "$1" in
    --jsonlFile) jsonl="$2"; shift 2 ;;
    --summaryFile) summary="$2"; shift 2 ;;
    *) shift ;;
  esac
done
printf '{"slug":"owner-one","scan_status":"updated","upstream_commit_sha":"%s"}\\n' "$FAKE_COMMIT" > "$jsonl"
printf '{"meta":{"slug":"owner-one","upstream_commit_sha":"%s"}}\\n' "$FAKE_COMMIT" > "$FAKE_REPORT"
printf '# updated\\n' > "$FAKE_SKILL"
cat > "$summary" <<'SUMMARY'
| Observed updated skills | 1 |
| Selected updated skills for this run | 1 |
| Applied updated skills | 1 |
| Failed selected updates | 0 |
| Deferred updated skills | 0 |

### Local Actions

- updated: owner-one (skills/owner/one)
SUMMARY
`);
    chmodSync(fakeCli, 0o755);
    run('git', ['init', '-q', workspace]);
    run('git', ['-C', workspace, 'config', 'user.name', 'Fixture']);
    run('git', ['-C', workspace, 'config', 'user.email', 'fixture@example.com']);
    run('git', ['-C', workspace, 'add', '.']);
    run('git', ['-C', workspace, 'commit', '-qm', 'fixture']);
    writeFileSync(join(workspace, '.git', 'info', 'exclude'), '/source-monitor-results/\n', { flag: 'a' });
    const baseEnv = {
      ...process.env,
      GITHUB_WORKSPACE: workspace,
      GITHUB_RUN_ID: '1234',
      GITHUB_OUTPUT: join(root, 'github-output'),
      GH_TOKEN: 'fixture',
      SLUGS: 'owner-one',
      LIMIT: '1',
      CONCURRENCY: '1',
      WRITE_CONCURRENCY: '1',
      MAX_UPDATES_PER_RUN: '1',
      CHECKOUT_CACHE_DIR: join(root, 'cache'),
      DRY_RUN: 'false',
      CREATE_PR: 'true',
      ARCHIVE_MISSING: 'false',
      CONFIRM_ARCHIVE: 'false',
      DELETE_ARCHIVED: 'false',
      MIN_MISSING_AGE_HOURS: '24',
      MODEL: '',
      EXPECTED_UPSTREAM_COMMIT: expectedCommit,
      FAKE_ARGS: argsFile,
      FAKE_COMMIT: expectedCommit,
      FAKE_REPORT: reportPath,
      FAKE_SKILL: skillPath,
    };
    const monitor = extractRunBlock('Run source monitor');
    const result = run('bash', ['-c', monitor], { cwd: workspace, env: baseEnv });
    assert.match(result.stdout, /Verified exact source monitor selection: 1\/1/);
    const invoked = readFileSync(argsFile, 'utf8');
    assert.match(invoked, /--updateLocal/);
    assert.doesNotMatch(invoked, /(^|\s)--write(\s|$)/);

    rmSync(argsFile);
    const rejected = run('bash', ['-c', monitor], {
      cwd: workspace,
      env: { ...baseEnv, EXPECTED_UPSTREAM_COMMIT: '' },
      allowFailure: true,
    });
    assert.notEqual(rejected.status, 0);
    assert.match(rejected.stdout + rejected.stderr, /requires expected_upstream_commit/);
    assert.equal(existsSync(argsFile), false, 'CLI must not execute without the expected commit');

    const helperArgs = [
      join(workspace, 'scripts', 'verify-source-monitor-selection.mjs'),
      '--requested', 'owner-one',
      '--jsonl', join(workspace, 'source-monitor-results', 'skill-source-monitor-1234.jsonl'),
      '--expected-upstream-commit', expectedCommit,
      '--require-local-updates',
      '--summary', join(workspace, 'source-monitor-results', 'skill-source-monitor-1234.md'),
      '--repository-root', workspace,
    ];
    writeFileSync(skillPath, '# old\n');
    const reportOnly = run('node', helperArgs, { cwd: workspace, allowFailure: true });
    assert.notEqual(reportOnly.status, 0);
    assert.match(reportOnly.stderr, /produced no payload file changes/);
    writeFileSync(skillPath, '# updated\n');

    const unsafeLink = join(skillDirectory, 'unsafe-link');
    symlinkSync('SKILL.md', unsafeLink);
    const symlinked = run('node', helperArgs, { cwd: workspace, allowFailure: true });
    assert.notEqual(symlinked.status, 0);
    assert.match(symlinked.stderr, /changed a symbolic link/);
    rmSync(unsafeLink);

    const controlPath = join(skillDirectory, 'control\npath');
    writeFileSync(controlPath, 'unsafe\n');
    const controlled = run('node', helperArgs, { cwd: workspace, allowFailure: true });
    assert.notEqual(controlled.status, 0);
    assert.match(controlled.stderr, /unsafe changed path/);
    rmSync(controlPath);

    writeFileSync(join(workspace, 'README.md'), 'unauthorized\n');
    const unauthorized = run('node', helperArgs, { cwd: workspace, allowFailure: true });
    assert.notEqual(unauthorized.status, 0);
    assert.match(unauthorized.stderr, /changed an unauthorized path: README\.md/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
