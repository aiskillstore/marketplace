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

const reusable = readFileSync('.github/workflows/reusable-process-skills.yml', 'utf8');
const caller = readFileSync('.github/workflows/process-submission.yml', 'utf8');
const runtimeFiles = [
  'schemas/skill-report.schema.json',
  'governance/submission-slug-aliases.json',
  '.github/actions/download-skillstore-cli/action.yml',
  '.github/workflows/reusable-process-skills.yml',
  'scripts/resolve-submission-source.mjs',
  'scripts/discover-submission-skills.mjs',
  'scripts/process-submission-shard.mjs',
  'scripts/submission-selection-plan.mjs',
  'scripts/submission-shard-contract.mjs',
  'scripts/aggregate-submission-shards.mjs',
  'scripts/resolve-approved-submission.mjs',
];

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: 'utf8',
    ...options,
  });
  if (result.status !== 0 && !options.allowFailure) {
    assert.fail(
      `${command} ${args.join(' ')} failed (${result.status})\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`
    );
  }
  return result;
}

function extractRunBlock(workflow, stepName) {
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
    const line = lines[index];
    const indent = line.search(/\S/);
    if (indent !== -1 && indent <= runIndent) break;
    body.push(line.length > runIndent + 2 ? line.slice(runIndent + 2) : '');
  }
  return body.join('\n');
}

function createFixture() {
  const root = mkdtempSync(join(tmpdir(), 'submission-runtime-'));
  const seed = join(root, 'seed');
  const origin = join(root, 'origin.git');
  const runnerWorkspace = join(root, 'runner-workspace');
  const workspace = join(runnerWorkspace, 'marketplace');
  const runnerTemp = join(root, 'runner-temp');

  mkdirSync(seed, { recursive: true });
  mkdirSync(runnerWorkspace, { recursive: true });
  mkdirSync(runnerTemp, { recursive: true });
  run('git', ['init', '-q', seed]);
  run('git', ['-C', seed, 'config', 'user.name', 'Fixture']);
  run('git', ['-C', seed, 'config', 'user.email', 'fixture@example.com']);

  const files = {
    'schemas/skill-report.schema.json': '{"type":"object"}\n',
    'governance/submission-slug-aliases.json': '{"schemaVersion":1,"aliases":[]}\n',
    '.github/actions/download-skillstore-cli/action.yml': 'name: fixture action\n',
    '.github/workflows/reusable-process-skills.yml': 'name: fixture workflow\n',
    'scripts/resolve-submission-source.mjs': 'export const source = true;\n',
    'scripts/discover-submission-skills.mjs': 'export const discover = true;\n',
    'scripts/process-submission-shard.mjs': 'export const process = true;\n',
    'scripts/submission-selection-plan.mjs': 'export const selectionPlan = true;\n',
    'scripts/submission-shard-contract.mjs': 'export const contract = true;\n',
    'scripts/aggregate-submission-shards.mjs': "import './resolve-approved-submission.mjs';\n",
    'scripts/resolve-approved-submission.mjs': 'export const resolve = true;\n',
    'skills/example/SKILL.md': '---\nname: example\n---\n',
  };
  for (const [path, content] of Object.entries(files)) {
    const fullPath = join(seed, path);
    mkdirSync(join(fullPath, '..'), { recursive: true });
    writeFileSync(fullPath, content);
  }
  run('git', ['-C', seed, 'add', '.']);
  run('git', ['-C', seed, 'commit', '-qm', 'fixture']);
  const head = run('git', ['-C', seed, 'rev-parse', 'HEAD']).stdout.trim();
  run('git', ['clone', '--bare', '-q', seed, origin]);
  run('git', ['clone', '-q', origin, workspace]);

  return { root, origin, runnerWorkspace, runnerTemp, workspace, head };
}

test('process checkout clears inherited sparse state before cloning the immutable workflow head', () => {
  const fixture = createFixture();
  try {
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'init', '--cone']);
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'set', '.github']);
    assert.equal(existsSync(join(fixture.workspace, 'schemas/skill-report.schema.json')), false);
    writeFileSync(join(fixture.workspace, 'stale-runner-file'), 'stale\n');

    const reset = extractRunBlock(reusable, 'Clear inherited marketplace checkout');
    run('bash', ['-c', reset], {
      cwd: fixture.workspace,
      env: {
        ...process.env,
        GITHUB_WORKSPACE: fixture.workspace,
        RUNNER_WORKSPACE: fixture.runnerWorkspace,
        RUNNER_TEMP: fixture.runnerTemp,
        GITHUB_REPOSITORY: `aiskillstore/${basename(fixture.workspace)}`,
      },
    });

    assert.deepEqual(readdirSync(fixture.workspace), []);
    run('git', ['clone', '-q', '--no-local', fixture.origin, fixture.workspace]);
    assert.equal(existsSync(join(fixture.workspace, 'schemas/skill-report.schema.json')), true);
    assert.equal(run('git', ['-C', fixture.workspace, 'config', '--bool', 'core.sparseCheckout'], { allowFailure: true }).stdout.trim(), '');

    assert.match(reusable, /ref: \$\{\{ github\.workflow_sha \}\}/);
    assert.match(reusable, /fetch-depth: 1/);
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('runtime preflight rejects every missing, modified, symlinked, or skip-worktree runtime and a mismatched head', () => {
  const fixture = createFixture();
  try {
    const preflight = extractRunBlock(reusable, 'Verify immutable processing runtime');
    const baseOptions = {
      cwd: fixture.workspace,
      env: {
        ...process.env,
        GITHUB_WORKSPACE: fixture.workspace,
        EXPECTED_WORKFLOW_SHA: fixture.head,
      },
    };

    run('bash', ['-c', preflight], baseOptions);

    for (const file of runtimeFiles) {
      const absolute = join(fixture.workspace, file);
      rmSync(absolute);
      assert.notEqual(run('bash', ['-c', preflight], { ...baseOptions, allowFailure: true }).status, 0, `${file} missing passed`);
      run('git', ['-C', fixture.workspace, 'checkout', '--', file]);

      writeFileSync(absolute, 'tampered\n');
      assert.notEqual(run('bash', ['-c', preflight], { ...baseOptions, allowFailure: true }).status, 0, `${file} tamper passed`);
      run('git', ['-C', fixture.workspace, 'checkout', '--', file]);

      rmSync(absolute);
      symlinkSync(join(fixture.workspace, 'skills/example/SKILL.md'), absolute);
      assert.notEqual(run('bash', ['-c', preflight], { ...baseOptions, allowFailure: true }).status, 0, `${file} symlink passed`);
      rmSync(absolute);
      run('git', ['-C', fixture.workspace, 'checkout', '--', file]);
    }

    run('git', ['-C', fixture.workspace, 'update-index', '--skip-worktree', runtimeFiles[0]]);
    assert.notEqual(run('bash', ['-c', preflight], { ...baseOptions, allowFailure: true }).status, 0);
    run('git', ['-C', fixture.workspace, 'update-index', '--no-skip-worktree', runtimeFiles[0]]);

    const wrongHeadOptions = {
      ...baseOptions,
      env: { ...baseOptions.env, EXPECTED_WORKFLOW_SHA: '0000000000000000000000000000000000000000' },
      allowFailure: true,
    };
    assert.notEqual(run('bash', ['-c', preflight], wrongHeadOptions).status, 0);
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('all submission entrypoints and the aggregation import closure are immutable and execute from GITHUB_WORKSPACE', () => {
  for (const file of runtimeFiles) assert.match(reusable, new RegExp(file.replaceAll('.', '\\.')));
  assert.match(reusable, /node "\$GITHUB_WORKSPACE\/scripts\/process-submission-shard\.mjs"/);
  assert.match(reusable, /node "\$GITHUB_WORKSPACE\/scripts\/submission-shard-contract\.mjs"/);
  assert.match(reusable, /node "\$GITHUB_WORKSPACE\/scripts\/aggregate-submission-shards\.mjs"/);
  assert.match(reusable, /require-checksum: true/);
  assert.match(reusable, /minimum-version: 2\.15\.0/);
  assert.match(reusable, /Rollout pin: selection-plan processing requires the exact 2\.15\.0 contract/);
  assert.match(reusable, /trap cleanup_input_plan EXIT/);
  assert.match(reusable, /--slug-aliases-file "\$GITHUB_WORKSPACE\/governance\/submission-slug-aliases\.json"/);
  assert.match(reusable, /--selection-plan "\$INPUT_PLAN"/);
  assert.match(reusable, /SELECTION_PLAN_JSON:/);
  assert.match(readFileSync('scripts/process-submission-shard.mjs', 'utf8'), /'--selection-plan', join\(config\.resultDir, 'selection-plan\.json'\)/);
  assert.equal((reusable.match(/"scripts\/submission-selection-plan\.mjs"/g) ?? []).length, 3,
    'discovery, processing, and aggregation immutable runtime lists must all include the plan validator');
  assert.match(
    readFileSync('scripts/aggregate-submission-shards.mjs', 'utf8'),
    /from '\.\/resolve-approved-submission\.mjs'/,
  );
});

test('clone step accepts repository-root false and explicit-path true without weakening type validation', () => {
  const clone = extractRunBlock(reusable, 'Clone source repository');
  const explicitPathFilter = [
    'if (.explicitPath | type) == "boolean" then',
    '.explicitPath',
    'else',
    'error("explicitPath must be a boolean")',
    'end',
  ].join('\n');

  assert.match(clone, /EXPLICIT_PATH=\$\(jq -r '/);
  assert.doesNotMatch(clone, /EXPLICIT_PATH=\$\(jq -er '/);

  for (const [explicitPath, expected] of [[false, 'false'], [true, 'true']]) {
    const result = run('jq', ['-r', explicitPathFilter], {
      input: JSON.stringify({ explicitPath }),
    });
    assert.equal(result.stdout.trim(), expected);
  }

  const invalid = run('jq', ['-r', explicitPathFilter], {
    input: JSON.stringify({ explicitPath: 'false' }),
    allowFailure: true,
  });
  assert.notEqual(invalid.status, 0);
});

test('repository dispatch caller preserves reusable failure and callback status contracts', () => {
  assert.match(caller, /notify:\n\s+needs: process-skills\n\s+if: always\(\) && github\.event_name == 'repository_dispatch'/);
  assert.match(caller, /name: Notify skillstore - PR created\n\s+if: needs\.process-skills\.outputs\.pr_url/);
  assert.match(caller, /name: Notify skillstore - Failed\n\s+if: needs\.process-skills\.result == 'failure'/);
  assert.match(caller, /"event": "failed"/);
  assert.doesNotMatch(caller, /continue-on-error:\s*true/);
});
