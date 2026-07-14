import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildShardPlan,
  extractShard,
} from '../plan-cache-invalidation.mjs';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const PLANNER = join(REPO_ROOT, 'scripts', 'plan-cache-invalidation.mjs');

function makeSlugs(count) {
  return Array.from(
    { length: count },
    (_, index) => `skill-${String(index).padStart(5, '0')}`,
  );
}

function parseOutputs(path) {
  const outputs = {};
  for (const line of readFileSync(path, 'utf8').trim().split('\n').filter(Boolean)) {
    const separator = line.indexOf('=');
    assert.notEqual(separator, -1, `Invalid GITHUB_OUTPUT line: ${line}`);
    outputs[line.slice(0, separator)] = line.slice(separator + 1);
  }
  return outputs;
}

test('planner maps 1, 100, 101, and 5263 slugs to bounded shards', () => {
  for (const [slugCount, expectedShardCount] of [
    [1, 1],
    [100, 1],
    [101, 2],
    [5263, 53],
  ]) {
    const plan = buildShardPlan(makeSlugs(slugCount), {
      shardSize: 100,
      maxShards: 256,
    });

    assert.equal(plan.slugCount, slugCount);
    assert.equal(plan.shardCount, expectedShardCount);
    assert.equal(plan.matrix.include.length, expectedShardCount);
    assert.ok(plan.shards.every((shard) => shard.length >= 1 && shard.length <= 100));
    assert.ok(
      plan.matrix.include.every(
        (entry, shard) => Object.keys(entry).length === 1 && entry.shard === shard,
      ),
      'matrix entries must contain only the shard id',
    );
  }
});

test('planner and extractor are deterministic and exactly-once across the artifact', () => {
  const expected = makeSlugs(5263);
  const artifactOrder = [...expected].reverse();
  artifactOrder.splice(200, 0, expected[100], expected[300]);

  const first = buildShardPlan(artifactOrder, { shardSize: 100, maxShards: 256 });
  const second = buildShardPlan([...artifactOrder].reverse(), {
    shardSize: 100,
    maxShards: 256,
  });

  assert.deepEqual(first.matrix, second.matrix);
  assert.deepEqual(first.slugs, expected);
  assert.deepEqual(second.slugs, expected);

  const extracted = first.matrix.include.flatMap(({ shard }) =>
    extractShard(first.slugs, shard, 100));
  assert.deepEqual(extracted, expected);
  assert.equal(new Set(extracted).size, expected.length);
  assert.ok(first.shards.every((shard) => shard.length >= 1 && shard.length <= 100));
});

test('empty artifact is a successful no-op', () => {
  const plan = buildShardPlan([], { shardSize: 100, maxShards: 256 });

  assert.equal(plan.slugCount, 0);
  assert.equal(plan.shardCount, 0);
  assert.deepEqual(plan.slugs, []);
  assert.deepEqual(plan.shards, []);
  assert.deepEqual(plan.matrix, { include: [] });
});

test('planner enforces 100 slugs per shard and the GitHub 256-job matrix limit', () => {
  const boundary = buildShardPlan(makeSlugs(25_600), {
    shardSize: 100,
    maxShards: 256,
  });
  assert.equal(boundary.shardCount, 256);

  assert.throws(
    () => buildShardPlan(makeSlugs(25_601), { shardSize: 100, maxShards: 256 }),
    /requires 257 shards, exceeding matrix limit 256/,
  );
  assert.throws(
    () => buildShardPlan(makeSlugs(101), { shardSize: 101, maxShards: 256 }),
    /shard-size must be between 1 and 100/,
  );
  assert.throws(
    () => buildShardPlan(makeSlugs(1), { shardSize: 100, maxShards: 257 }),
    /max-shards must be between 1 and 256/,
  );
});

test('plan CLI writes only shard ids and counts to GITHUB_OUTPUT', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'cache-plan-test-'));
  const slugsFile = join(tmp, 'synced-slugs.txt');
  const githubOutput = join(tmp, 'github-output');
  const secretSlug = 'private-slug-must-stay-in-artifact';
  writeFileSync(slugsFile, `${secretSlug}\n${makeSlugs(100).join('\n')}\n`);

  const result = spawnSync(
    process.execPath,
    [
      PLANNER,
      'plan',
      '--slugs-file',
      slugsFile,
      '--shard-size',
      '100',
      '--max-shards',
      '256',
    ],
    {
      encoding: 'utf8',
      env: { ...process.env, GITHUB_OUTPUT: githubOutput },
    },
  );

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  const outputs = parseOutputs(githubOutput);
  assert.equal(outputs.slug_count, '101');
  assert.equal(outputs.shard_count, '2');
  assert.deepEqual(JSON.parse(outputs.matrix), {
    include: [{ shard: 0 }, { shard: 1 }],
  });
  assert.doesNotMatch(readFileSync(githubOutput, 'utf8'), new RegExp(secretSlug));
  assert.doesNotMatch(`${result.stdout}${result.stderr}`, new RegExp(secretSlug));
});

test('extract CLI materializes only the selected bounded shard from the artifact', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'cache-extract-test-'));
  const slugsFile = join(tmp, 'synced-slugs.txt');
  const outputFile = join(tmp, 'shard.txt');
  const slugs = makeSlugs(101).reverse();
  writeFileSync(slugsFile, `${slugs.join('\n')}\n`);

  const result = spawnSync(
    process.execPath,
    [
      PLANNER,
      'extract',
      '--slugs-file',
      slugsFile,
      '--shard-size',
      '100',
      '--shard-id',
      '1',
      '--output',
      outputFile,
    ],
    { encoding: 'utf8' },
  );

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(readFileSync(outputFile, 'utf8').trim().split('\n'), ['skill-00100']);
  assert.doesNotMatch(`${result.stdout}${result.stderr}`, /skill-00100/);
});
