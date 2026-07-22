import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const workflow = readFileSync(
  new URL('../../.github/workflows/pack-production-slo.yml', import.meta.url),
  'utf8',
);

test('the guarded weekly SLO retains evidence and fails visibly when unmet', () => {
  assert.match(workflow, /actions\/checkout@[0-9a-f]{40}/);
  assert.match(workflow, /actions\/upload-artifact@[0-9a-f]{40}/);
  assert.match(workflow, /github\.event_name == 'workflow_dispatch' \|\|[\s\S]*vars\.PACK_PRODUCTION_AUTOMATION_ENABLED == 'true'/);
  assert.match(workflow, /if: always\(\)[\s\S]*name: pack-production-slo/);
  assert.match(workflow, /::error::Rolling 7-day Pack production SLO is below target:[\s\S]*exit 1/);
  assert.doesNotMatch(workflow, /::warning::Rolling 7-day Pack production SLO is below target/);
});
