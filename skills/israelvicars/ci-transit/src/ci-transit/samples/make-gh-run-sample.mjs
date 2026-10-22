import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, 'gh-run-sample.json');
const t = (s) => `2026-10-16T12:${String(s).padStart(2, '0')}:00Z`;
const step = (name, number, startedAt, completedAt, conclusion = 'success') => ({
  name, number, status: conclusion === 'skipped' ? 'completed' : 'completed', conclusion,
  startedAt: t(startedAt), completedAt: t(completedAt),
});
const job = (name, databaseId, startedAt, completedAt, conclusion, steps) => ({
  name, databaseId, status: 'completed', conclusion, startedAt: t(startedAt), completedAt: t(completedAt), steps,
});

const run = {
  _comment: 'SYNTHETIC hand-built GitHub Actions run for fictional repo acme-labs/nebula-shop.',
  databaseId: 240016,
  name: 'CI',
  displayTitle: 'Pipeline for fictional Nebula Shop',
  headBranch: 'main',
  event: 'push',
  status: 'completed',
  conclusion: 'failure',
  createdAt: t(0), startedAt: t(1), updatedAt: t(18),
  url: 'https://github.example.invalid/acme-labs/nebula-shop/actions/runs/240016',
  workflowName: 'CI',
  attempt: 2,
  jobs: [
    job('lint', 240101, 2, 5, 'success', [
      step('Install dependencies', 1, 2, 3), step('ESLint', 2, 3, 5),
    ]),
    job('test (node 20)', 240102, 6, 11, 'success', [
      step('Install dependencies', 1, 6, 7), step('Run unit tests', 2, 7, 11),
    ]),
    job('test (node 22)', 240103, 6, 12, 'failure', [
      step('Install dependencies', 1, 6, 7), step('Run unit tests', 2, 7, 12, 'failure'),
    ]),
    job('build', 240104, 13, 16, 'success', [
      step('Bundle application', 1, 13, 16),
    ]),
    job('deploy-preview', 240105, 17, 17, 'skipped', []),
  ],
  needs: {
    lint: [],
    'test (node 20)': [],
    'test (node 22)': [],
    build: ['lint', 'test (node 20)', 'test (node 22)'],
    'deploy-preview': ['build'],
  },
};

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify(run, null, 2) + '\n');
console.log(`wrote ${out}`);
