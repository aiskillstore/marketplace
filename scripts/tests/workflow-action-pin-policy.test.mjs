import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  cpSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import {
  findWorkflowUsesReferences,
  findWorkflowUsesViolations,
  scanWorkflowDirectory,
} from '../check-workflow-action-pins.mjs';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const CHECKER = join(REPO_ROOT, 'scripts', 'check-workflow-action-pins.mjs');
const FULL_SHA = '0123456789abcdef0123456789abcdef01234567';
const DOCKER_DIGEST = 'a'.repeat(64);

function violationsFor(uses) {
  return findWorkflowUsesViolations(`jobs:\n  test:\n    uses: ${uses}\n`, 'fixture.yml');
}

test('rejects mutable GitHub action and reusable workflow references', () => {
  for (const uses of [
    'actions/checkout@v5',
    'actions/checkout@main',
    'actions/checkout@0123456',
    'example/automation/.github/workflows/reusable.yml@main',
  ]) {
    const violations = violationsFor(uses);
    assert.equal(violations.length, 1, `${uses} must be rejected`);
    assert.equal(violations[0].file, 'fixture.yml');
    assert.equal(violations[0].line, 3);
  }
});

test('rejects mutable external uses in YAML flow-style mappings', () => {
  const workflow = 'steps: [{ uses: actions/checkout@v5 }]\n';
  const violations = findWorkflowUsesViolations(workflow, 'flow-style.yml');

  assert.equal(violations.length, 1);
  assert.equal(violations[0].file, 'flow-style.yml');
  assert.equal(violations[0].line, 1);
  assert.equal(violations[0].uses, 'actions/checkout@v5');
  assert.match(violations[0].message, /40-character commit SHA/);
});

test('validates block-style uses keys with whitespace before the colon', () => {
  const workflow = `
steps:
  - uses : actions/checkout@v5
  - uses : actions/setup-node@${FULL_SHA}
`;
  const violations = findWorkflowUsesViolations(workflow, 'spaced-key.yml');

  assert.equal(violations.length, 1);
  assert.equal(violations[0].line, 3);
  assert.equal(violations[0].uses, 'actions/checkout@v5');
});

test('validates quoted block-style uses keys', () => {
  const workflow = `
steps:
  - "uses": actions/checkout@v5
  - 'uses': actions/setup-node@main
  - "uses": actions/setup-node@${FULL_SHA}
  - "\\u0075ses": actions/github-script@v8
  - "\\x75ses": actions/upload-artifact@v4
`;
  const violations = findWorkflowUsesViolations(workflow, 'quoted-key.yml');

  assert.deepEqual(
    violations.map(({ line, uses }) => ({ line, uses })),
    [
      { line: 3, uses: 'actions/checkout@v5' },
      { line: 4, uses: 'actions/setup-node@main' },
      { line: 6, uses: 'actions/github-script@v8' },
      { line: 7, uses: 'actions/upload-artifact@v4' },
    ],
  );
});

test('fails closed for multiline quoted mapping keys', () => {
  const workflow = String.raw`steps:
  - "u\
      ses": actions/checkout@v5
`;
  const violations = findWorkflowUsesViolations(workflow, 'multiline-key.yml');

  assert.ok(violations.length > 0);
  assert.equal(violations[0].line, 2);
  assert.equal(violations[0].uses, '<yaml-parse-error>');
  assert.match(violations[0].message, /YAML parse error/);
});

test('cannot hide mutable uses behind YAML properties or explicit mapping keys', () => {
  const workflow = `
steps:
  - &checkout uses: actions/checkout@v5
  - !!str uses: actions/setup-node@main
  - ? uses
    : actions/github-script@v8
  - ? >-
      uses
    : actions/upload-artifact@v4
`;
  const violations = findWorkflowUsesViolations(workflow, 'mapping-forms.yml');

  assert.deepEqual(
    violations.map(({ line, uses }) => ({ line, uses })),
    [
      { line: 3, uses: 'actions/checkout@v5' },
      { line: 4, uses: 'actions/setup-node@main' },
      { line: 5, uses: 'actions/github-script@v8' },
      { line: 7, uses: 'actions/upload-artifact@v4' },
    ],
  );
});

test('flow anchor and tagged mapping keys are structurally recognized as uses', () => {
  const workflow = [
    'jobs:',
    '  test:',
    '    steps: [ { &action_key uses: actions/checkout@v5 }, { !!str uses: actions/setup-node@main } ]',
  ].join('\n');
  const violations = findWorkflowUsesViolations(workflow, 'flow-properties.yml');

  assert.deepEqual(
    violations.map(({ line, uses }) => ({ line, uses })),
    [
      { line: 3, uses: 'actions/checkout@v5' },
      { line: 3, uses: 'actions/setup-node@main' },
    ],
  );
});

test('malformed YAML fails closed with file and line diagnostics', () => {
  const violations = findWorkflowUsesViolations('jobs:\n  test:\n    runs: [', 'broken.yml');

  assert.ok(violations.length > 0);
  assert.equal(violations[0].file, 'broken.yml');
  assert.equal(violations[0].line, 3);
  assert.match(violations[0].message, /YAML parse error/i);
});

test('dynamic and non-scalar uses values fail closed', () => {
  const workflow = [
    'jobs:',
    '  test:',
    '    steps:',
    '      - uses: ${{ matrix.action }}',
    '      - uses: [actions/checkout@v5]',
  ].join('\n');
  const violations = findWorkflowUsesViolations(workflow, 'dynamic.yml');

  assert.equal(violations.length, 2);
  assert.match(violations[0].message, /dynamic|literal|owner\/repository|full 40-character commit SHA/i);
  assert.match(violations[1].message, /non-scalar/i);
});

test('ignores comments and shell strings in block scalar run steps', () => {
  const workflow = `
# steps: [{ uses: actions/checkout@v5 }]
steps:
  - run: |
      uses: actions/checkout@v5
      echo "steps: [{ uses: actions/setup-node@main }]"
      # uses: example/action@main
`;

  assert.deepEqual(findWorkflowUsesViolations(workflow, 'run-step.yml'), []);
});

test('accepts full GitHub commit pins, local actions, and local reusable workflows', () => {
  const workflow = `
jobs:
  action:
    steps:
      - uses: actions/checkout@${FULL_SHA}
      - uses: actions/setup-node@${FULL_SHA} # v5
      - uses: ./.github/actions/download-skillstore-cli
  reusable:
    uses: ./.github/workflows/reusable.yml
`;

  assert.deepEqual(findWorkflowUsesViolations(workflow, 'valid.yml'), []);
});

test('requires Docker image references to use a full sha256 digest', () => {
  assert.equal(violationsFor('docker://alpine:3.20').length, 1);
  assert.deepEqual(
    violationsFor(`docker://alpine@sha256:${DOCKER_DIGEST}`),
    [],
  );
});

test('recursively scans yml and yaml files and reports file plus line', () => {
  const root = mkdtempSync(join(tmpdir(), 'workflow-action-pin-policy-'));
  try {
    mkdirSync(join(root, 'nested'), { recursive: true });
    writeFileSync(
      join(root, 'valid.yml'),
      `steps:\n  - uses: actions/checkout@${FULL_SHA} # v5\n`,
    );
    writeFileSync(
      join(root, 'nested', 'invalid.yaml'),
      'name: fixture\nsteps:\n  - uses: actions/setup-node@main\n',
    );
    writeFileSync(join(root, 'nested', 'ignored.txt'), 'uses: actions/checkout@v5\n');

    const violations = scanWorkflowDirectory(root);
    assert.equal(violations.length, 1);
    assert.equal(violations[0].file, join(root, 'nested', 'invalid.yaml'));
    assert.equal(violations[0].line, 3);
    assert.equal(violations[0].uses, 'actions/setup-node@main');
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CLI scans workflows and local action manifests by default', () => {
  const root = mkdtempSync(join(tmpdir(), 'workflow-action-pin-policy-cli-'));
  try {
    const workflows = join(root, '.github', 'workflows');
    const actions = join(root, '.github', 'actions', 'fixture');
    mkdirSync(workflows, { recursive: true });
    mkdirSync(actions, { recursive: true });
    writeFileSync(
      join(workflows, 'valid.yml'),
      `name: fixture\njobs:\n  test:\n    steps:\n      - uses: actions/checkout@${FULL_SHA}\n`,
    );
    writeFileSync(
      join(actions, 'action.yml'),
      'name: fixture\nruns:\n  using: composite\n  steps:\n    - uses: actions/setup-node@main\n',
    );

    const result = spawnSync(process.execPath, [CHECKER], {
      cwd: root,
      encoding: 'utf8',
    });

    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /\.github\/actions\/fixture\/action\.yml:5:/);
    assert.match(result.stderr, /actions\/setup-node@main/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

for (const fixture of [
  {
    name: 'manifest symlink',
    link: '.github/actions/demo/action.yml',
    target: '../../../../support/action.yml',
    targetPath: 'support/action.yml',
    targetSource: `name: demo\nruns:\n  using: composite\n  steps:\n    - uses: actions/checkout@${FULL_SHA}\n`,
  },
  {
    name: 'directory symlink',
    link: '.github/actions/linked',
    target: '../../support/action-dir',
    targetPath: 'support/action-dir/action.yml',
    targetSource: `name: demo\nruns:\n  using: composite\n  steps:\n    - uses: actions/checkout@${FULL_SHA}\n`,
  },
  {
    name: 'dangling symlink',
    link: '.github/workflows/dangling.yml',
    target: '../../missing.yml',
  },
]) {
  test(`${fixture.name} fails closed with its concrete path`, () => {
    const root = mkdtempSync(join(tmpdir(), 'workflow-action-pin-policy-symlink-'));
    try {
      const linkPath = join(root, fixture.link);
      mkdirSync(dirname(linkPath), { recursive: true });
      if (fixture.targetPath) {
        const targetPath = join(root, fixture.targetPath);
        mkdirSync(dirname(targetPath), { recursive: true });
        writeFileSync(targetPath, fixture.targetSource);
      }
      symlinkSync(fixture.target, linkPath);

      const result = spawnSync(process.execPath, [CHECKER], {
        cwd: root,
        encoding: 'utf8',
      });

      assert.notEqual(result.status, 0);
      assert.match(`${result.stdout}\n${result.stderr}`, new RegExp(fixture.link.replaceAll('.', '\\.')));
      assert.match(`${result.stdout}\n${result.stderr}`, /symlink/i);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
}

test('pull_request validation executes fork head only on GitHub-hosted read-only jobs', () => {
  const workflow = readFileSync(
    join(REPO_ROOT, '.github', 'workflows', 'validate-marketplace.yml'),
    'utf8',
  );
  const recalculateTests = readFileSync(
    join(REPO_ROOT, '.github', 'workflows', 'test-recalculate-scores.yml'),
    'utf8',
  );
  const requiredPaths = [
    '.github/workflows/**',
    '.github/actions/**',
    '.github/dependabot.yml',
    'package.json',
    'package-lock.json',
    'scripts/check-workflow-action-pins.mjs',
    'scripts/check-workflow-runner-safety.mjs',
    'scripts/tests/**',
  ];

  for (const event of ['push', 'pull_request']) {
    const paths = workflow.match(
      new RegExp(`^  ${event}:\\n[\\s\\S]*?^    paths:\\n([\\s\\S]*?)(?=^  \\S)`, 'm'),
    )?.[1];
    assert.ok(paths, `missing ${event}.paths`);
    for (const requiredPath of requiredPaths) {
      assert.ok(
        paths.includes(`      - "${requiredPath}"`),
        `${event}.paths must include ${requiredPath}`,
      );
    }
  }

  assert.doesNotMatch(workflow, /^  pull_request_target:/m);
  assert.match(workflow, /^permissions:\n  contents: read$/m);
  assert.match(
    workflow,
    /^  AUTO_FIX_ENABLED: \$\{\{ \(github\.event_name == 'push' \|\| github\.event_name == 'workflow_dispatch'\) && github\.ref == 'refs\/heads\/main' \}\}$/m,
  );

  const policyJob = workflow.match(/^  action-pin-policy:\n[\s\S]*?(?=^  \S)/m)?.[0];
  assert.ok(policyJob, 'missing action-pin-policy job');
  assert.match(policyJob, /^    runs-on: ubuntu-latest$/m);
  assert.match(policyJob, /uses: actions\/checkout@[0-9a-f]{40} # v5/);
  assert.match(
    policyJob,
    /repository: \$\{\{ github\.event_name == 'pull_request' && github\.event\.pull_request\.head\.repo\.full_name \|\| github\.repository \}\}/,
  );
  assert.match(
    policyJob,
    /ref: \$\{\{ github\.event_name == 'pull_request' && github\.event\.pull_request\.head\.sha \|\| github\.sha \}\}/,
  );
  assert.match(policyJob, /persist-credentials: false/);
  assert.match(policyJob, /uses: actions\/setup-node@[0-9a-f]{40} # v5/);
  assert.match(policyJob, /run: npm ci --ignore-scripts/);
  assert.match(policyJob, /scripts\/tests\/workflow-action-pin-policy\.test\.mjs/);
  assert.match(policyJob, /scripts\/tests\/workflow-runner-safety\.test\.mjs/);
  assert.match(policyJob, /run: node scripts\/check-workflow-action-pins\.mjs/);
  assert.match(policyJob, /run: node scripts\/check-workflow-runner-safety\.mjs/);

  const validateJob = workflow.match(/^  validate:\n[\s\S]*/m)?.[0];
  assert.ok(validateJob, 'missing validate job');
  assert.match(validateJob, /^  validate:\n    needs: action-pin-policy$/m);
  assert.match(validateJob, /^    runs-on: ubuntu-latest$/m);
  assert.match(validateJob, /^    permissions:\n      contents: read\n      pull-requests: read$/m);
  assert.match(
    validateJob,
    /^      - name: Generate GitHub App Token\n        if: env\.AUTO_FIX_ENABLED == 'true' && github\.event_name != 'pull_request'\n/m,
  );
  const workspaceSetup = validateJob.match(
    /^      - name: Setup isolated temporary workspace\n[\s\S]*?(?=^      - name:)/m,
  )?.[0];
  assert.ok(workspaceSetup, 'missing isolated workspace setup');
  assert.match(workspaceSetup, /if \[ "\$EVENT_NAME" = "pull_request" \]; then/);
  assert.match(workspaceSetup, /fetch --no-tags --depth 1 pull-head "\$HEAD_SHA"/);
  assert.match(workspaceSetup, /checkout --detach "\$HEAD_SHA"/);

  assert.match(recalculateTests, /^  pull_request:/m);
  assert.doesNotMatch(recalculateTests, /^  pull_request_target:/m);
  assert.match(recalculateTests, /^permissions:\n  contents: read$/m);
  assert.match(recalculateTests, /^    runs-on: ubuntu-latest$/m);
  assert.match(
    recalculateTests,
    /repository: \$\{\{ github\.event_name == 'pull_request' && github\.event\.pull_request\.head\.repo\.full_name \|\| github\.repository \}\}/,
  );
  assert.match(
    recalculateTests,
    /ref: \$\{\{ github\.event_name == 'pull_request' && github\.event\.pull_request\.head\.sha \|\| github\.sha \}\}/,
  );
  assert.match(recalculateTests, /persist-credentials: false/);
});

test('workflow contract tests do not contain any current Dependabot-managed action SHA', () => {
  const manifestRoots = [
    join(REPO_ROOT, '.github', 'workflows'),
    join(REPO_ROOT, '.github', 'actions'),
  ];
  const manifestFiles = [];
  const walk = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) walk(path);
      else if (entry.isFile() && /\.ya?ml$/i.test(entry.name)) manifestFiles.push(path);
    }
  };
  for (const root of manifestRoots) walk(root);

  const currentShas = new Set();
  for (const file of manifestFiles) {
    const source = readFileSync(file, 'utf8');
    for (const reference of findWorkflowUsesReferences(source, file)) {
      if (reference.uses.startsWith('./') || reference.uses.startsWith('docker://')) continue;
      const match = reference.uses.match(/@([0-9a-f]{40})$/i);
      if (match) currentShas.add(match[1].toLowerCase());
    }
  }
  assert.ok(currentShas.size > 0, 'expected current external Action pins');

  const contractTests = readdirSync(TEST_DIR, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.test.mjs'))
    .map((entry) => entry.name);
  for (const file of contractTests) {
    const source = readFileSync(join(TEST_DIR, file), 'utf8')
      .replaceAll('\\/', '/')
      .toLowerCase();
    for (const sha of currentShas) {
      assert.equal(
        source.includes(sha),
        false,
        `${file} must validate the full-SHA shape without freezing current pin ${sha}`,
      );
    }
  }
});

test(
  'bulk checkout pin replacement keeps workflow contract tests green',
  { skip: process.env.ACTION_PIN_MUTATION_CHILD === '1' },
  () => {
    const root = mkdtempSync(join(tmpdir(), 'workflow-action-pin-mutation-'));
    try {
      for (const relativePath of ['.github', 'governance', 'ops', 'schemas', 'scripts']) {
        cpSync(join(REPO_ROOT, relativePath), join(root, relativePath), { recursive: true });
      }
      for (const file of ['package.json', 'package-lock.json']) {
        cpSync(join(REPO_ROOT, file), join(root, file));
      }
      symlinkSync(join(REPO_ROOT, 'node_modules'), join(root, 'node_modules'), 'dir');

      const replacementSha = 'f'.repeat(40);
      const rewritePins = (directory) => {
        for (const entry of readdirSync(directory, { withFileTypes: true })) {
          const path = join(directory, entry.name);
          if (entry.isDirectory()) rewritePins(path);
          else if (entry.isFile() && /\.ya?ml$/i.test(entry.name)) {
            const content = readFileSync(path, 'utf8');
            writeFileSync(
              path,
              content.replace(/actions\/checkout@[0-9a-f]{40}/gi, `actions/checkout@${replacementSha}`),
            );
          }
        }
      };
      rewritePins(join(root, '.github'));

      const result = spawnSync(
        process.execPath,
        [
          '--test',
          'scripts/tests/artifact-version-backfill.test.mjs',
          'scripts/tests/generate-packs-workflow.test.mjs',
          'scripts/tests/pack-evaluator-bwrap-userns.test.mjs',
          'scripts/tests/score-cache-closure.test.mjs',
          'scripts/tests/workflow-action-pin-policy.test.mjs',
        ],
        {
          cwd: root,
          encoding: 'utf8',
          env: { ...process.env, ACTION_PIN_MUTATION_CHILD: '1' },
        },
      );
      assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  },
);

test('Dependabot updates root GitHub Actions pins weekly without automatic major upgrades', () => {
  const dependabot = readFileSync(
    join(REPO_ROOT, '.github', 'dependabot.yml'),
    'utf8',
  );
  assert.match(
    dependabot,
    /^version: 2\nupdates:\n  - package-ecosystem: "github-actions"\n    directory: "\/"\n    schedule:\n      interval: "weekly"\n    ignore:\n      - dependency-name: "\*"\n        update-types:\n          - "version-update:semver-major"$/m,
  );
});
