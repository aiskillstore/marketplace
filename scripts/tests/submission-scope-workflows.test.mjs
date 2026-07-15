import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const reusable = readFileSync('.github/workflows/reusable-process-skills.yml', 'utf8');
const approval = readFileSync('.github/workflows/on-pr-merge.yml', 'utf8');

test('submission processing isolates every shard and stages only its frozen plan', () => {
  assert.match(reusable, /RESULT_DIR="\/tmp\/submission-shard-/);
  assert.match(reusable, /process-shard-\$\{\{ github\.run_attempt \}\}-\$\{\{ matrix\.shard \}\}/);
  assert.match(reusable, /--output "\$RESULT_DIR"/);
  assert.match(reusable, /tar -C "\$RESULT_DIR" -czf "\$RESULT_DIR\/shard-results\.tar\.gz"/);
  assert.match(reusable, /tar -xzf "\$SHARD_ARCHIVE" -C "\$SHARD_ROOT" --no-same-owner/);
  assert.match(reusable, /node scripts\/resolve-approved-submission\.mjs/);
  assert.match(reusable, /git add -- "\$\{SUBMISSION_PATHS\[@\]\}"/);
  assert.doesNotMatch(reusable, /--output \./);
  assert.doesNotMatch(reusable, /find pending/);
  assert.doesNotMatch(reusable, /git add pending\//);
  assert.match(reusable, /Downloaded \$\{#SHARD_DIRS\[@\]\}\/\$\{\{ needs\.discover-and-plan\.outputs\.shard_count \}\} shard artifact/);
  assert.match(reusable, /Published target already exists; use the explicit update workflow/);
});

test('merged approval scope comes only from immutable PR changed files', () => {
  assert.match(approval, /pulls\/\$PR_NUMBER\/files\?per_page=100/);
  assert.match(approval, /node scripts\/resolve-approved-submission\.mjs/);
  assert.match(approval, /mapfile -t SKILL_PATHS/);
  assert.match(approval, /Refusing to overwrite existing published target/);
  assert.match(approval, /git diff --quiet "\$MERGE_COMMIT_SHA" HEAD -- "\$PENDING_DIR"/);
  assert.match(approval, /PUSHED=false/);
  assert.match(approval, /test "\$PUSHED" = true/);
  assert.doesNotMatch(approval, /cherry-pick HEAD@\{1\} \|\| true/);
  assert.doesNotMatch(approval, /find pending/);
  assert.doesNotMatch(approval, /rm -rf "\$TARGET_DIR"/);
});
