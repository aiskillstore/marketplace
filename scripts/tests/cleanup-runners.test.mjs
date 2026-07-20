import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const workflow = readFileSync(
  new URL('../../.github/workflows/cleanup-runners.yml', import.meta.url),
  'utf8'
);
const guard = readFileSync(
  new URL('../runner-disk-guard.sh', import.meta.url),
  'utf8'
);
const service = readFileSync(
  new URL('../../ops/systemd/marketplace-runner-disk-guard.service', import.meta.url),
  'utf8'
);
const timer = readFileSync(
  new URL('../../ops/systemd/marketplace-runner-disk-guard.timer', import.meta.url),
  'utf8'
);
const testWorkflow = readFileSync(
  new URL('../../.github/workflows/test-recalculate-scores.yml', import.meta.url),
  'utf8'
);

test('runner cleanup bounds Docker maintenance to old build cache under pressure', () => {
  assert.match(workflow, /usage" -lt 90/);
  assert.match(workflow, /docker builder prune --all --force --filter "until=\$\{age_hours\}h"/);
  assert.doesNotMatch(workflow, /docker (system|image|volume|container) prune/);
  assert.match(workflow, /images, containers, and volumes were preserved/);
  assert.match(workflow, /permissions: \{\}/);
  assert.match(workflow, /age_days must be a positive integer/);
});

test('host guard can reclaim shared Docker build cache before Actions setup', () => {
  assert.match(guard, /flock -n 9/);
  assert.match(guard, /docker builder prune --all --force --filter "until=\$\{age_hours\}h"/);
  assert.doesNotMatch(guard, /docker (system|image|volume|container) prune/);
  assert.match(service, /ExecStart=\/usr\/local\/sbin\/marketplace-runner-disk-guard/);
  assert.match(service, /Nice=19/);
  assert.match(timer, /OnUnitActiveSec=15min/);
  assert.match(timer, /Persistent=true/);
  assert.match(testWorkflow, /- "scripts\/runner-disk-guard\.sh"/);
  assert.match(testWorkflow, /- "ops\/systemd\/\*\*"/);
  assert.match(testWorkflow, /sparse-checkout: \|\n\s+\.github\n\s+governance\/fresh-canonical-audit\n\s+ops\/systemd\n\s+scripts/);
});
