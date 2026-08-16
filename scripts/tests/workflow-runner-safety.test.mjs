import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const CHECKER = join(REPO_ROOT, 'scripts', 'check-workflow-runner-safety.mjs');
const ACTION_SHA = 'a'.repeat(40);

function runChecker(root = REPO_ROOT) {
  return spawnSync(process.execPath, [CHECKER, '--root', root], {
    cwd: root,
    encoding: 'utf8',
  });
}

function withWorkflow(source, callback) {
  const root = mkdtempSync(join(tmpdir(), 'workflow-runner-safety-'));
  try {
    const workflowPath = join(root, '.github', 'workflows', 'fixture.yml');
    mkdirSync(dirname(workflowPath), { recursive: true });
    writeFileSync(workflowPath, source);
    callback(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test('all repository workflow event-to-runner boundaries satisfy the static safety policy', () => {
  const result = runChecker();
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
});

test('malicious pull_request workflow cannot select self-hosted or privileged fork execution', () => {
  withWorkflow(
    [
      'name: malicious fork workflow',
      'on:',
      '  pull_request:',
      'permissions:',
      '  contents: write',
      'jobs:',
      '  pwn:',
      '    runs-on: [self-hosted, linux]',
      '    steps:',
      `      - uses: actions/checkout@${ACTION_SHA}`,
      '        with:',
      '          persist-credentials: true',
      '      - env:',
      '          TOKEN: ${{ secrets.APP_PRIVATE_KEY }}',
      '        run: node scripts/tests/pwn.test.mjs',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      const output = `${result.stdout}\n${result.stderr}`;
      assert.notEqual(result.status, 0);
      assert.match(output, /fixture\.yml/);
      assert.match(output, /self-hosted/i);
      assert.match(output, /contents:\s*read|write permission/i);
      assert.match(output, /persist-credentials:\s*false/i);
    },
  );
});

test('job conditions cannot make self-hosted safe for a pull_request workflow', () => {
  withWorkflow(
    [
      'name: negated runner bypass',
      'on:',
      '  pull_request:',
      'jobs:',
      '  pwn:',
      "    if: ${{ !(github.event_name != 'pull_request') }}",
      '    runs-on: self-hosted',
      '    steps:',
      '      - run: node scripts/pwn.mjs',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      assert.notEqual(result.status, 0);
      assert.match(`${result.stdout}\n${result.stderr}`, /self-hosted/i);
    },
  );
});

test('trusted closed merge may share a self-hosted job with exact main recovery', () => {
  withWorkflow(
    [
      'name: merged approval recovery',
      'on:',
      '  pull_request:',
      '    types: [closed]',
      '  workflow_dispatch:',
      '    inputs:',
      '      pr_number:',
      '        required: true',
      'jobs:',
      '  approve:',
      "    if: (github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main') || (github.event.pull_request.merged == true && contains(github.event.pull_request.labels.*.name, 'pending-review'))",
      '    runs-on: self-hosted',
      '    steps:',
      '      - run: echo trusted-merged-pr-metadata',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    },
  );
});

test('GitHub-hosted read-only exact-head pull_request job passes', () => {
  withWorkflow(
    [
      'name: hosted fork validation',
      'on:',
      '  pull_request:',
      'permissions:',
      '  contents: read',
      'jobs:',
      '  test:',
      '    runs-on: ubuntu-latest',
      '    steps:',
      `      - uses: actions/checkout@${ACTION_SHA}`,
      '        with:',
      '          repository: ${{ github.event.pull_request.head.repo.full_name }}',
      '          ref: ${{ github.event.pull_request.head.sha }}',
      '          persist-credentials: false',
      '      - run: node --test scripts/tests/example.test.mjs',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    },
  );
});

test('trusted main push may use self-hosted without making it pull_request reachable', () => {
  withWorkflow(
    [
      'name: trusted writer',
      'on:',
      '  push:',
      '    branches: [main]',
      'jobs:',
      '  write:',
      '    runs-on: self-hosted',
      '    steps:',
      '      - run: echo trusted-default-branch',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    },
  );
});

test('tag and release workflows cannot require a non-default-ref self-hosted runner grant', () => {
  withWorkflow(
    [
      'name: unsafe tag release',
      'on:',
      '  push:',
      '    tags: ["v*"]',
      '  release:',
      '    types: [published]',
      'jobs:',
      '  publish:',
      '    runs-on: self-hosted',
      '    steps:',
      '      - run: echo unsafe-dynamic-tag-ref',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      assert.notEqual(result.status, 0);
      assert.match(`${result.stdout}\n${result.stderr}`, /tag\/release.*GitHub-hosted/i);
    },
  );
});

test('tag release jobs pass on a literal GitHub-hosted runner', () => {
  withWorkflow(
    [
      'name: hosted tag release',
      'on:',
      '  push:',
      '    tags: ["v*"]',
      'jobs:',
      '  publish:',
      '    runs-on: ubuntu-latest',
      '    steps:',
      '      - run: echo hosted-tag-release',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    },
  );
});

test('pull_request_target is forbidden even when fork head is fetched indirectly', () => {
  withWorkflow(
    [
      'name: unsafe target workflow',
      'on:',
      '  pull_request_target:',
      'permissions:',
      '  contents: read',
      'jobs:',
      '  inspect:',
      '    runs-on: self-hosted',
      '    steps:',
      '      - env:',
      '          TOKEN: ${{ secrets.APP_PRIVATE_KEY }}',
      '        run: |',
      '          git init fork-head',
      '          git -C fork-head fetch https://github.com/${{ github.repository }} pull/${{ github.event.pull_request.number }}/head',
      '          git -C fork-head checkout --detach FETCH_HEAD',
      '          node fork-head/scripts/pwn.mjs',
    ].join('\n'),
    (root) => {
      const result = runChecker(root);
      const output = `${result.stdout}\n${result.stderr}`;
      assert.notEqual(result.status, 0);
      assert.match(output, /pull_request_target/i);
      assert.match(output, /forbidden/i);
    },
  );
});
