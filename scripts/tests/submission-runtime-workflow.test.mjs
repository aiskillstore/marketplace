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
const approvalCaller = readFileSync('.github/workflows/approve-submission.yml', 'utf8');
const publicationProvenance = readFileSync('.github/workflows/publication-provenance.yml', 'utf8');
const cliCompatibilityDescription =
  'Reserved compatibility input; submission processing is pinned to CLI 2.15.12';
const runtimeFiles = [
  'schemas/skill-report.schema.json',
  'governance/submission-slug-aliases.json',
  '.github/actions/download-skillstore-cli/action.yml',
  '.github/workflows/reusable-process-skills.yml',
  'scripts/resolve-submission-source.mjs',
  'scripts/discover-submission-skills.mjs',
  'scripts/classify-submission-targets.mjs',
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

function extractNamedBlock(workflow, name) {
  const lines = workflow.split('\n');
  const nameIndex = lines.findIndex((line) => line.trim() === name);
  assert.notEqual(nameIndex, -1, `missing workflow block: ${name}`);

  const blockIndent = lines[nameIndex].search(/\S/);
  let endIndex = lines.length;
  for (let index = nameIndex + 1; index < lines.length; index += 1) {
    const indent = lines[index].search(/\S/);
    if (indent !== -1 && indent <= blockIndent) {
      endIndex = index;
      break;
    }
  }
  return lines.slice(nameIndex, endIndex).join('\n');
}

function createFixture() {
  const root = mkdtempSync(join(tmpdir(), 'submission-runtime-'));
  const seed = join(root, 'seed');
  const githubServer = join(root, 'github');
  const origin = join(githubServer, 'aiskillstore', 'marketplace.git');
  const runnerWorkspace = join(root, 'runner-workspace');
  const workspace = join(runnerWorkspace, 'marketplace');
  const runnerTemp = join(root, 'runner-temp');

  mkdirSync(seed, { recursive: true });
  mkdirSync(join(origin, '..'), { recursive: true });
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
    'scripts/classify-submission-targets.mjs': 'export const classify = true;\n',
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

  return { root, githubServer, origin, runnerWorkspace, runnerTemp, workspace, head };
}

test('discovery checkout fetches only immutable runtime blobs before exact target materialization', () => {
  const fixture = createFixture();
  try {
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'init', '--cone']);
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'set', '.github']);
    assert.equal(existsSync(join(fixture.workspace, 'schemas/skill-report.schema.json')), false);
    writeFileSync(join(fixture.workspace, 'stale-runner-file'), 'stale\n');

    const reset = extractRunBlock(reusable, 'Clear inherited marketplace checkout');
    assert.doesNotMatch(
      reset,
      /sparse-checkout disable/,
      'clearing a partial clone must not hydrate omitted blobs before deletion',
    );
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
    const checkout = extractRunBlock(reusable, 'Checkout immutable discovery runtime');
    run('bash', ['-c', checkout], {
      cwd: fixture.runnerTemp,
      env: {
        ...process.env,
        GITHUB_WORKSPACE: fixture.workspace,
        GITHUB_SERVER_URL: `file://${fixture.githubServer}`,
        GITHUB_REPOSITORY: 'aiskillstore/marketplace',
        GITHUB_RUN_ATTEMPT: '1',
        GITHUB_RUN_ID: '1',
        EXPECTED_WORKFLOW_SHA: fixture.head,
        RUNNER_TEMP: fixture.runnerTemp,
        SUBMISSION_RUNTIME_SPARSE_PATHS: runtimeFiles.map((file) => `/${file}`).join('\n'),
      },
    });
    assert.equal(run('git', ['-C', fixture.workspace, 'rev-parse', 'HEAD']).stdout.trim(), fixture.head);
    for (const file of runtimeFiles) assert.equal(existsSync(join(fixture.workspace, file)), true, `${file} missing`);
    assert.equal(existsSync(join(fixture.workspace, 'skills/example/SKILL.md')), false);
    assert.equal(run('git', ['-C', fixture.workspace, 'config', '--bool', 'core.sparseCheckout']).stdout.trim(), 'true');
    assert.match(checkout, /for CHECKOUT_ATTEMPT in 1 2 3/);
    assert.match(checkout, /--filter=blob:none/);
    assert.match(checkout, /sparse-checkout set --no-cone --stdin/);

    const materialize = extractRunBlock(reusable, 'Materialize exact Marketplace candidate paths');
    run('bash', ['-c', materialize], {
      cwd: fixture.workspace,
      env: {
        ...process.env,
        FULL_SELECTION_PLAN: JSON.stringify({
          schemaVersion: 1,
          repository: 'aiskillstore/source',
          sourceCommit: fixture.head,
          scope: { reason: 'conventional_skills', path: 'skills' },
          skills: [{ slug: 'example', path: 'skills/example' }],
        }),
        GITHUB_WORKSPACE: fixture.workspace,
        GITHUB_RUN_ATTEMPT: '1',
        GITHUB_RUN_ID: '1',
        RUNNER_TEMP: fixture.runnerTemp,
      },
    });
    assert.equal(existsSync(join(fixture.workspace, 'skills/example/SKILL.md')), true);
    assert.match(materialize, /for MATERIALIZE_ATTEMPT in 1 2 3/);
    assert.match(materialize, /sparse-checkout add --stdin/);
    assert.match(materialize, /ls-tree HEAD/);
    assert.match(materialize, /symlink or non-directory path component/);
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('runtime preflight rejects every missing, modified, symlinked runtime and a mismatched head', () => {
  const fixture = createFixture();
  try {
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'init', '--no-cone']);
    run('git', ['-C', fixture.workspace, 'sparse-checkout', 'set', '--no-cone', '--stdin'], {
      input: `${runtimeFiles.map((file) => `/${file}`).join('\n')}\n`,
    });
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
  assert.match(reusable, /node "\$GITHUB_WORKSPACE\/scripts\/classify-submission-targets\.mjs"/);
  assert.match(reusable, /require-checksum: true/);
  assert.match(reusable, /minimum-version: 2\.15\.12/);
  assert.match(reusable, /Dependency gate: do not merge before cli-v2\.15\.12 is released/);
  assert.match(reusable, /trap cleanup_input_plan EXIT/);
  assert.match(reusable, /--slug-aliases-file "\$GITHUB_WORKSPACE\/governance\/submission-slug-aliases\.json"/);
  assert.match(reusable, /--selection-plan "\$INPUT_PLAN"/);
  assert.match(reusable, /SELECTION_PLAN_JSON:/);
  assert.match(readFileSync('scripts/process-submission-shard.mjs', 'utf8'), /'--selection-plan', join\(config\.resultDir, 'selection-plan\.json'\)/);
  assert.equal((reusable.match(/"scripts\/submission-selection-plan\.mjs"/g) ?? []).length, 3,
    'discovery, processing, and aggregation immutable runtime lists must all include the plan validator');
  assert.equal((reusable.match(/"scripts\/classify-submission-targets\.mjs"/g) ?? []).length, 3,
    'discovery, processing, and aggregation immutable runtime lists must all include the target classifier');
  assert.match(
    readFileSync('scripts/aggregate-submission-shards.mjs', 'utf8'),
    /from '\.\/resolve-approved-submission\.mjs'/,
  );
});

test('aggregation retries a transient fresh-clone failure without reusing a partial checkout', () => {
  const aggregation = extractRunBlock(reusable, 'Merge results and create PR');

  assert.match(aggregation, /for CLONE_ATTEMPT in 1 2 3/);
  assert.match(aggregation, /rm -rf "\$WORK_DIR"/);
  assert.match(aggregation, /git clone --depth 1 --filter=blob:none --no-checkout/);
  assert.match(aggregation, /for MATERIALIZE_ATTEMPT in 1 2 3/);
  assert.match(aggregation, /sparse-checkout set --no-cone --stdin/);
  assert.match(aggregation, /ls-tree HEAD/);
  assert.match(aggregation, /symlink or non-directory path component/);
  assert.match(aggregation, /sleep "\$\(\(CLONE_ATTEMPT \* 5\)\)"/);
  assert.match(aggregation, /exit 1/);
});

test('all submission audit entrypoints pass the existing HELM credential through the reusable secret contract', () => {
  for (const [name, workflow] of [
    ['repository dispatch', caller],
    ['manual approval', approvalCaller],
  ]) {
    const processJob = extractNamedBlock(workflow, 'process-skills:');
    const forwardedSecrets = extractNamedBlock(processJob, 'secrets:');
    assert.match(processJob, /uses: \.\/\.github\/workflows\/reusable-process-skills\.yml/);
    assert.match(
      forwardedSecrets,
      /^\s*HELM_API_KEY: \$\{\{ secrets\.HELM_API_KEY \}\}$/m,
      `${name} must forward the repository HELM_API_KEY`,
    );
    assert.equal(
      (workflow.match(/secrets\.HELM_API_KEY/g) ?? []).length,
      1,
      `${name} must expose HELM_API_KEY only to the reusable workflow call`,
    );
  }

  const workflowCall = extractNamedBlock(reusable, 'workflow_call:');
  const secretContract = extractNamedBlock(workflowCall, 'secrets:');
  const helmContract = extractNamedBlock(secretContract, 'HELM_API_KEY:');
  assert.match(helmContract, /^\s*HELM_API_KEY:\n\s+required: true$/);
});

test('HELM credential is injected only into the Process shard step environment', () => {
  const processShard = extractNamedBlock(reusable, '- name: Process shard ${{ matrix.shard }}');
  const processEnvironment = extractNamedBlock(processShard, 'env:');

  assert.match(
    processEnvironment,
    /^\s*HELM_API_KEY: \$\{\{ secrets\.HELM_API_KEY \}\}$/m,
  );
  assert.equal(
    (reusable.match(/secrets\.HELM_API_KEY/g) ?? []).length,
    1,
    'only the Process shard step may read the reusable HELM secret',
  );
  assert.equal(
    (reusable.match(/^\s*HELM_API_KEY:/gm) ?? []).length,
    2,
    'HELM_API_KEY may appear only in workflow_call.secrets and the Process shard env',
  );
});

test('submission processing compatibility inputs and CLI download are pinned to 2.15.12', () => {
  for (const [name, workflow] of [
    ['repository dispatch', caller],
    ['manual approval', approvalCaller],
    ['reusable workflow', reusable],
  ]) {
    const cliInput = extractNamedBlock(workflow, 'cli_version:');
    assert.match(
      cliInput,
      new RegExp(`description: '${cliCompatibilityDescription.replaceAll('.', '\\.')}'`),
      `${name} compatibility input must describe the fixed CLI dependency`,
    );
    assert.match(cliInput, /default: '2\.15\.12'/);
  }

  const download = extractNamedBlock(reusable, '- name: Download Skillstore CLI');
  assert.match(download, /version: '2\.15\.12'/);
  assert.match(download, /minimum-version: 2\.15\.12/);
  assert.doesNotMatch(download, /inputs\.cli_version|version: ['"]?latest/);
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

test('submission source metadata lookup retries transient GitHub failures', () => {
  const clone = extractRunBlock(reusable, 'Clone source repository');

  assert.match(clone, /for SOURCE_METADATA_ATTEMPT in 1 2 3/);
  assert.match(clone, /DEFAULT_REF=\$\(gh api "repos\/\$OWNER_REPO" --jq '\.default_branch'\)/);
  assert.match(clone, /git ls-remote --heads --tags .* > "\$REFS_FILE"/);
  assert.match(clone, /Source metadata lookup failed; retrying attempt/);
  assert.match(clone, /test -s "\$REFS_FILE"/);
});

test('submission checkout verifies and fetches the exact resolved commit', () => {
  const clone = extractRunBlock(reusable, 'Clone source repository');
  assert.match(clone, /REF_TYPE=\$\(jq -er '\.refType'/);
  assert.match(clone, /gh api "repos\/\$OWNER_REPO\/commits\/\$REF_SHA" --jq '\.sha'/);
  assert.match(clone, /git -C "\$SOURCE_DIR" fetch --no-tags --depth 1 origin "\$REF_SHA"/);
  assert.match(clone, /git -C "\$SOURCE_DIR" checkout --detach FETCH_HEAD/);
  assert.doesNotMatch(clone, /git clone --depth 1 --branch/);
});

test('publication PR admission accepts only trusted bot-owned publication branches', () => {
  assert.match(publicationProvenance, /publication-admission:/);
  assert.match(publicationProvenance, /AUTHOR_ID.*github\.event\.pull_request\.user\.id/);
  assert.match(publicationProvenance, /AUTHOR_LOGIN.*github\.event\.pull_request\.user\.login/);
  assert.match(publicationProvenance, /HEAD_REPOSITORY.*github\.event\.pull_request\.head\.repo\.full_name/);
  assert.match(publicationProvenance, /pending:submission\/\*:pending\/\*/);
  assert.match(publicationProvenance, /skills:skill-source-monitor\/\*:skills\/\*/);
  assert.match(publicationProvenance, /A PR cannot mix pending and published Skill changes/);
});

test('repository dispatch caller preserves reusable failure and callback status contracts', () => {
  assert.match(caller, /notify:\n\s+needs: process-skills\n\s+if: always\(\) && github\.event_name == 'repository_dispatch'/);
  assert.match(caller, /name: Notify skillstore - PR created\n\s+if: needs\.process-skills\.outputs\.pr_url/);
  assert.match(caller, /name: Notify skillstore - Failed\n\s+if: needs\.process-skills\.result == 'failure'/);
  assert.match(caller, /"event": "failed"/);
  assert.match(caller, /needs\.process-skills\.outputs\.outcome == 'rejected'/);
  assert.match(caller, /event: "rejected"/);
  assert.match(caller, /outcome: "rejected"/);
  assert.match(caller, /reason_code: \$reason_code/);
  assert.match(caller, /reason: \$reason/);
  assert.match(caller, /processed_count: 0/);
  assert.match(caller, /curl --fail-with-body/);
  assert.match(caller, /--retry 3/);
  assert.doesNotMatch(
    extractRunBlock(caller, 'Notify skillstore - Rejected because all targets exist'),
    /\|\|\s+echo/,
  );
  assert.doesNotMatch(caller, /continue-on-error:\s*true/);
});

test('existing-target classification is a pre-CLI gate with a handled rejection output', () => {
  const classifyIndex = reusable.indexOf('- name: Classify submission targets');
  const planIndex = reusable.indexOf('- name: Plan processing strategy');
  const processIndex = reusable.indexOf('\n  process:');
  assert.ok(classifyIndex > reusable.indexOf('- name: Discover skills (fast - no AI)'));
  assert.ok(classifyIndex < planIndex);
  assert.ok(planIndex < processIndex);
  const startedIndex = reusable.indexOf('- name: Notify skillstore - Processing started');
  assert.ok(startedIndex > classifyIndex);
  assert.match(reusable, /inputs\.is_manual_approval == false && steps\.targets\.outputs\.disposition == 'processable'/);
  assert.match(reusable, /if: steps\.targets\.outputs\.disposition == 'processable'/);
  assert.match(reusable, /target_disposition == 'processable' && needs\.discover-and-plan\.outputs\.shard_count != '0'/);
  assert.match(reusable, /target_disposition == 'all_existing' && 'rejected'/);
  assert.match(
    readFileSync('scripts/classify-submission-targets.mjs', 'utf8'),
    /all_selected_targets_already_published/,
  );
  assert.match(reusable, /existing_targets:/);
  assert.match(reusable, /FULL_SELECTION_PLAN: \$\{\{ steps\.targets\.outputs\.processing_plan \}\}/);
  assert.doesNotMatch(reusable, /--source-ref/);
  const latePendingGuard = reusable.indexOf('Pending path already exists on main');
  const latePublishedGuard = reusable.indexOf('Frozen update target is missing or unsafe');
  const lateCopy = reusable.indexOf('cp -R "$MERGED_RESULTS/$pending_dir"');
  assert.ok(latePendingGuard > 0 && latePendingGuard < lateCopy);
  assert.ok(latePublishedGuard > latePendingGuard && latePublishedGuard < lateCopy);
  assert.match(reusable, /Unexpected published target collision/);
  assert.match(reusable, /UPDATE_TARGETS: \$\{\{ needs\.discover-and-plan\.outputs\.update_targets \}\}/);
  assert.match(reusable, /Update target and snapshot sets do not match/);
  assert.match(reusable, /CURRENT_TREE_HASH=\$\(node "\$GITHUB_WORKSPACE\/scripts\/resolve-approved-submission\.mjs"/);
  assert.match(reusable, /\[ "\$CURRENT_TREE_HASH" = "\$EXPECTED_TREE_HASH" \]/);
  assert.match(reusable, /previous_tree_hash = \$treeHash/);
  assert.match(reusable, /previous_source_ref = \$sourceRef/);
});
