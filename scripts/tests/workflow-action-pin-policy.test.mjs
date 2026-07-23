import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import {
  findWorkflowUsesViolations,
  scanWorkflowDirectory,
} from '../check-workflow-action-pins.mjs';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const CHECKER = join(REPO_ROOT, 'scripts', 'check-workflow-action-pins.mjs');
const FULL_SHA = '0123456789abcdef0123456789abcdef01234567';
const DOCKER_DIGEST = 'a'.repeat(64);
const CHECKOUT_SHA = 'fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09';

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
  assert.match(violations[0].message, /Flow-style/);
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

test('CLI defaults to .github/workflows and exits nonzero with actionable diagnostics', () => {
  const root = mkdtempSync(join(tmpdir(), 'workflow-action-pin-policy-cli-'));
  try {
    const workflows = join(root, '.github', 'workflows');
    mkdirSync(workflows, { recursive: true });
    writeFileSync(
      join(workflows, 'invalid.yml'),
      'name: fixture\njobs:\n  test:\n    steps:\n      - uses: actions/checkout@v5\n',
    );

    const result = spawnSync(process.execPath, [CHECKER], {
      cwd: root,
      encoding: 'utf8',
    });

    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /\.github\/workflows\/invalid\.yml:5:/);
    assert.match(result.stderr, /actions\/checkout@v5/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('validate-marketplace gates write-capable validation on the read-only pin policy', () => {
  const workflow = readFileSync(
    join(REPO_ROOT, '.github', 'workflows', 'validate-marketplace.yml'),
    'utf8',
  );
  const requiredPaths = [
    '.github/workflows/**',
    '.github/dependabot.yml',
    'scripts/check-workflow-action-pins.mjs',
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

  const policyJob = workflow.match(/^  action-pin-policy:\n[\s\S]*?(?=^  \S)/m)?.[0];
  assert.ok(policyJob, 'missing action-pin-policy job');
  assert.equal(policyJob.match(/^    permissions:/gm)?.length, 1);
  assert.match(policyJob, /^    permissions:\n      contents: read\n    steps:$/m);
  const checkoutStep = `      - name: Checkout repository
        uses: actions/checkout@${CHECKOUT_SHA} # v5
        with:
          persist-credentials: false`;
  assert.ok(policyJob.includes(checkoutStep));
  assert.match(
    policyJob,
    /^      - name: Test workflow action pin policy\n        run: node --test scripts\/tests\/workflow-action-pin-policy\.test\.mjs$/m,
  );
  assert.match(
    policyJob,
    /^      - name: Enforce workflow action pin policy\n        run: node scripts\/check-workflow-action-pins\.mjs$/m,
  );

  const validateJob = workflow.match(/^  validate:\n[\s\S]*/m)?.[0];
  assert.ok(validateJob, 'missing validate job');
  assert.match(validateJob, /^  validate:\n    needs: action-pin-policy$/m);
  assert.match(
    validateJob,
    /^    permissions:\n      contents: write(?:\s+#.*)?\n      pull-requests: write(?:\s+#.*)?$/m,
  );
  assert.match(
    validateJob,
    /^      - name: Generate GitHub App Token\n        id: app-token\n        uses: actions\/create-github-app-token@[0-9a-f]{40}(?: #.*)?$/m,
  );
});

test('Dependabot updates root GitHub Actions pins weekly', () => {
  const dependabot = readFileSync(
    join(REPO_ROOT, '.github', 'dependabot.yml'),
    'utf8',
  );
  assert.match(
    dependabot,
    /^version: 2\nupdates:\n  - package-ecosystem: "github-actions"\n    directory: "\/"\n    schedule:\n      interval: "weekly"$/m,
  );
});
