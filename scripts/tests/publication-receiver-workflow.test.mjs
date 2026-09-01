import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parse } from 'yaml';
import test from 'node:test';

const source = readFileSync('.github/workflows/on-pr-merge.yml', 'utf8');
const workflow = parse(source);

test('post-merge publication accepts the exact bot merger and binds dispatch correlation', () => {
  assert.match(source, /github-actions\\\[bot\\\]/);
  assert.match(source, /^run-name:.*Publication.*inputs\.correlation_id/m);
  assert.match(workflow['run-name'], /Publish merged PR #\{0\}.*\}\}$/);
  assert.match(source, /correlation_id:/);
  assert.match(source, /required: true/);
  assert.match(source, /EXPECTED_CORRELATION_ID="submission-pr-\$\{PR_NUMBER\}-\$\{HEAD_SHA\}-\$\{MERGE_COMMIT_SHA\}"/);
  assert.match(source, /\[ "\$CORRELATION_ID" = "\$EXPECTED_CORRELATION_ID" \]/);
});

test('publication receiver serializes one correlation and verifies the durable outbox before writes', () => {
  assert.equal(workflow.concurrency.group, 'publication-${{ inputs.correlation_id }}');
  assert.equal(workflow.concurrency['cancel-in-progress'], false);
  const outboxGuard = source.indexOf('Verify durable publication dispatch outbox');
  const appToken = source.indexOf('Generate GitHub App Token');
  assert.ok(outboxGuard > 0 && outboxGuard < appToken);
  assert.match(source, /agentcrew-dispatch-outbox\/publication/);
  assert.match(source, /length > 0 and length <= 8/);
  assert.match(source, /object\.sha == \$merge_sha/);
  assert.match(source, /Existing durable publication status refuses duplicate execution/);
  assert.match(source, /steps\.publication_claim\.outputs\.owns_reservation == 'true'/);
  assert.match(source, /Idempotency-Key: publication-resolved-/);
});
