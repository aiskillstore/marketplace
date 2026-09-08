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

test('publication receiver serializes one correlation and verifies the exact durable outbox attempt before writes', () => {
  assert.equal(workflow.concurrency.group, 'publication-${{ inputs.correlation_id }}');
  assert.equal(workflow.concurrency['cancel-in-progress'], false);
  assert.equal(workflow.on.workflow_dispatch.inputs.outbox_attempt.required, true);
  const outboxGuard = source.indexOf('Verify durable publication dispatch outbox');
  const appToken = source.indexOf('Generate GitHub App Token');
  assert.ok(outboxGuard > 0 && outboxGuard < appToken);
  assert.match(source, /agentcrew-dispatch-outbox\/publication/);
  assert.match(source, /length > 0 and length <= 8/);
  assert.match(source, /object\.sha == \$merge_sha/);
  assert.match(source, /EXACT_OUTBOX_REF=.*OUTBOX_ATTEMPT/);
  assert.match(source, /ATTEMPT_CONTEXT="agentcrew\/publication-attempt\/\$DIGEST\/\$OUTBOX_ATTEMPT"/);
  assert.match(source, /Existing durable publication attempt status refuses duplicate execution/);
  assert.match(source, /if \[ "\$CORRELATION_STATE" = success \]/);
  assert.match(source, /Authoritative publication success refuses retry/);
  assert.match(source, /if \[ "\$CORRELATION_STATE" = pending \]/);
  assert.match(source, /Existing in-flight publication refuses unknown-effect replay/);
  assert.match(source, /-f state=failure -f context="\$ATTEMPT_CONTEXT"/);
  assert.match(source, /-f state=success -f context="\$ATTEMPT_CONTEXT"/);
  assert.match(source, /steps\.publication_claim\.outputs\.owns_reservation == 'true'/);
  assert.match(source, /Idempotency-Key: publication-resolved-/);
});

test('publication receiver materializes report-only roots without scanning shared pending', () => {
  assert.match(source, /\$NF == "SKILL\.md" \|\| \$NF == "skill-report\.json"/);
  assert.match(source, /Merged PR contains no canonical pending publication identity file/);
  assert.match(source, /git diff --quiet "\$MERGE_COMMIT_SHA" HEAD -- "\$PENDING_DIR"/);
  assert.doesNotMatch(source, /find pending/);
});
