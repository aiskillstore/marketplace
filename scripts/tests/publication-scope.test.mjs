import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { publicationInScope, assertPublicationInScope } from '../publication-scope.mjs';

const cutoff = '2026-11-04T14:23:00.928Z';
test('publication uses original creation time, not a later update or merge', () => {
  for (const created_at of ['2026-11-04T14:22:59Z', cutoff, '2026-11-04T14:23:00Z']) {
    const pr = { created_at, updated_at: '2026-11-05T00:00:00Z', merged_at: '2026-11-05T00:00:00Z' };
    assert.equal(publicationInScope(pr), false);
    assert.throws(() => assertPublicationInScope(pr), /publication scope/);
  }
  assert.equal(publicationInScope({ created_at: '2026-11-04T14:23:00.929Z' }), true);
  assert.doesNotThrow(() => assertPublicationInScope({ created_at: '2026-11-04T15:59:31Z' }));
});
test('missing or malformed creation evidence fails closed', () => {
  for (const created_at of [undefined, null, '', 'tomorrow', '2026-11-05', '2026-99-99T00:00:00Z']) {
    assert.throws(() => publicationInScope({ created_at }), /creation timestamp/);
  }
});
test('single receiver executes the same strict cutoff with GitHub second-precision timestamps', () => {
  const workflow = readFileSync(new URL('../../.github/workflows/on-pr-merge.yml', import.meta.url), 'utf8');
  const expression = workflow.match(/jq -e --argjson scope "\$SCOPE" '([\s\S]*?)' <<< "\$PR"/)[1];
  const scope = readFileSync(new URL('../publication-scope.json', import.meta.url), 'utf8');
  for (const [created_at, expected] of [['2026-11-04T14:23:00Z', false], ['2026-11-04T14:23:01Z', true], ['2026-11-04T14:22:59Z', false], ['garbage', false]]) {
    const result = spawnSync('jq', ['-e', '--argjson', 'scope', scope, expression], { input: JSON.stringify({ created_at }), encoding: 'utf8' });
    assert.equal(result.status === 0, expected, result.stderr);
  }
});
test('all publication writers check scope before reservations or writes', () => {
  const batch = readFileSync(new URL('../publish-approved-batch.mjs', import.meta.url), 'utf8');
  assert.ok(batch.indexOf('assertPublicationInScope(pr)') > 0);
  assert.ok(batch.indexOf('assertPublicationInScope(pr)') < batch.indexOf('const identity = publicationIdentity(pr)'));
  const continuation = readFileSync(new URL('../continue-merged-publications.mjs', import.meta.url), 'utf8');
  assert.match(continuation, /new Set\(owners\.values\(\)\)\]\.filter\(publicationInScope\)/);
  const workflow = readFileSync(new URL('../../.github/workflows/on-pr-merge.yml', import.meta.url), 'utf8');
  assert.ok(workflow.indexOf('scripts/publication-scope.json') > 0);
  assert.ok(workflow.indexOf('scripts/publication-scope.json') < workflow.indexOf('id: publication_claim'));
  assert.match(workflow, /Publication is outside the approved creation-time scope/);
});
