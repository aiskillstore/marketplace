import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const schema = JSON.parse(readFileSync('schemas/skill-report.schema.json', 'utf8'));
const testWorkflow = readFileSync('.github/workflows/test-recalculate-scores.yml', 'utf8');
const meta = schema.properties.meta;

test('strict report schema declares the complete CLI upstream metadata contract', () => {
  assert.equal(meta.additionalProperties, false);
  assert.deepEqual(meta.properties.upstream_version_raw.type, ['string', 'null']);
  assert.deepEqual(meta.properties.upstream_version_normalized.type, ['string', 'null']);
  assert.deepEqual(meta.properties.upstream_version_source, {
    type: 'string',
    enum: ['metadata.version', 'version', 'conflict', 'none'],
    description: 'Authoritative field from which the upstream version was derived',
  });
  assert.deepEqual(meta.properties.upstream_version_status, {
    type: 'string',
    enum: ['valid', 'missing', 'invalid', 'conflict', 'not_bumped', 'regressed'],
    description: 'Version-governance result for the observed upstream version',
  });
  assert.deepEqual(meta.properties.upstream_commit_sha.type, ['string', 'null']);
  assert.equal(meta.properties.upstream_commit_sha.pattern, '^[a-f0-9]{40}$');
});

test('script unit workflow checks out and watches the report schema fixture', () => {
  assert.match(testWorkflow, /sparse-checkout: \|[\s\S]*\n\s+schemas\n/);
  assert.equal(
    (testWorkflow.match(/- "schemas\/skill-report\.schema\.json"/g) ?? []).length,
    2,
    'pull_request and push must both run schema contract tests when the fixture changes',
  );
});
