import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const reusable = readFileSync('.github/workflows/reusable-process-skills.yml', 'utf8');
const approval = readFileSync('.github/workflows/on-pr-merge.yml', 'utf8');

test('submission processing isolates every shard and stages only its frozen plan', () => {
  assert.match(reusable, /RESULT_DIR="\/tmp\/submission-shard-/);
  assert.match(reusable, /process-shard-\$\{\{ github\.run_attempt \}\}-\$\{\{ matrix\.shard \}\}/);
  assert.match(reusable, /--output "\$RESULT_DIR"/);
  assert.match(reusable, /tar -C "\$RESULT_DIR" -czf "\$RESULT_DIR\/\$SHARD_ARCHIVE_NAME"/);
  assert.match(reusable, /planned-slugs\.csv/);
  assert.match(reusable, /tar -xzf "\$SHARD_ARCHIVE" -C "\$SHARD_ROOT" --no-same-owner/);
  assert.match(reusable, /node scripts\/resolve-approved-submission\.mjs/);
  assert.match(reusable, /git add -- "\$\{SUBMISSION_PATHS\[@\]\}"/);
  assert.doesNotMatch(reusable, /--output \./);
  assert.doesNotMatch(reusable, /find pending/);
  assert.doesNotMatch(reusable, /git add pending\//);
  assert.match(reusable, /Downloaded \$\{#SHARD_ARCHIVES\[@\]\}\/\$\{\{ needs\.discover-and-plan\.outputs\.shard_count \}\} shard archive/);
  assert.match(reusable, /Published target already exists; use the explicit update workflow/);
  assert.match(reusable, /produced a skill outside its planned slug set/);
  assert.match(reusable, /produced no successful skills/);
});

test('submission aggregation uses shard-addressed archives and keeps failure closed', () => {
  assert.match(reusable, /SHARD_ARCHIVE_NAME="process-shard-\$\{\{ github\.run_attempt \}\}-\$\{\{ matrix\.shard \}\}\.tar\.gz"/);
  assert.match(reusable, /path: \/tmp\/submission-shard-\$\{\{ github\.run_id \}\}-\$\{\{ github\.run_attempt \}\}-\$\{\{ matrix\.shard \}\}\/process-shard-\$\{\{ github\.run_attempt \}\}-\$\{\{ matrix\.shard \}\}\.tar\.gz/);
  assert.match(reusable, /find "\$ARTIFACTS_DIR" -type f/);
  assert.match(reusable, /-name 'process-shard-\$\{\{ github\.run_attempt \}\}-\*\.tar\.gz'/);
  assert.match(reusable, /Downloaded \$\{#SHARD_ARCHIVES\[@\]\}\/\$\{\{ needs\.discover-and-plan\.outputs\.shard_count \}\} shard archive\(s\)/);
  assert.match(reusable, /Missing or duplicate shard artifact index/);
  assert.match(reusable, /Shard processing did not complete successfully; refusing to aggregate/);
  assert.match(reusable, /No skills were successfully processed/);
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
