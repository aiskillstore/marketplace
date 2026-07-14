#!/usr/bin/env node

import { appendFileSync, readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

function parsePositiveInteger(value, name, maximum) {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) {
    throw new Error(`${name} must be a positive integer`);
  }
  if (maximum !== undefined && parsed > maximum) {
    throw new Error(`${name} must be between 1 and ${maximum}`);
  }
  return parsed;
}

export function normalizeSlugs(input) {
  const values = Array.isArray(input)
    ? input
    : String(input ?? '').split(/[\s,]+/);

  return [...new Set(values.map((slug) => String(slug).trim()).filter(Boolean))].sort();
}

export function extractShard(input, shardId, shardSize) {
  const normalized = normalizeSlugs(input);
  const parsedShardId = Number(shardId);
  const parsedShardSize = parsePositiveInteger(shardSize, 'shard-size', 100);

  if (!Number.isSafeInteger(parsedShardId) || parsedShardId < 0) {
    throw new Error('shard-id must be a non-negative integer');
  }

  const start = parsedShardId * parsedShardSize;
  const shard = normalized.slice(start, start + parsedShardSize);
  if (shard.length === 0) {
    throw new Error(`shard ${parsedShardId} is outside the artifact plan`);
  }
  return shard;
}

export function buildShardPlan(input, { shardSize = 100, maxShards = 256 } = {}) {
  const parsedShardSize = parsePositiveInteger(shardSize, 'shard-size', 100);
  const parsedMaxShards = parsePositiveInteger(maxShards, 'max-shards', 256);
  const slugs = normalizeSlugs(input);
  const shardCount = Math.ceil(slugs.length / parsedShardSize);

  if (shardCount > parsedMaxShards) {
    throw new Error(
      `cache invalidation requires ${shardCount} shards, exceeding matrix limit ${parsedMaxShards}`,
    );
  }

  const shards = Array.from({ length: shardCount }, (_, shard) =>
    extractShard(slugs, shard, parsedShardSize));
  const matrix = {
    include: Array.from({ length: shardCount }, (_, shard) => ({ shard })),
  };

  return {
    matrix,
    shardCount,
    shardSize: parsedShardSize,
    shards,
    slugCount: slugs.length,
    slugs,
  };
}

function readOption(args, name, { required = false, fallback } = {}) {
  const index = args.indexOf(name);
  if (index === -1) {
    if (required) throw new Error(`missing required option ${name}`);
    return fallback;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) {
    throw new Error(`missing value for ${name}`);
  }
  return args[index + 1];
}

function readArtifact(path) {
  return normalizeSlugs(readFileSync(path, 'utf8'));
}

function appendOutput(name, value) {
  const outputPath = process.env.GITHUB_OUTPUT;
  if (!outputPath) {
    throw new Error('GITHUB_OUTPUT is required for plan mode');
  }
  appendFileSync(outputPath, `${name}=${value}\n`);
}

function runPlan(args) {
  const slugsFile = readOption(args, '--slugs-file', { required: true });
  const shardSize = parsePositiveInteger(
    readOption(args, '--shard-size', { fallback: '100' }),
    'shard-size',
    100,
  );
  const maxShards = parsePositiveInteger(
    readOption(args, '--max-shards', { fallback: '256' }),
    'max-shards',
    256,
  );
  const plan = buildShardPlan(readArtifact(slugsFile), { shardSize, maxShards });

  appendOutput('matrix', JSON.stringify(plan.matrix));
  appendOutput('shard_count', plan.shardCount);
  appendOutput('slug_count', plan.slugCount);
  console.log(
    `Cache invalidation plan: ${plan.slugCount} slug(s), ${plan.shardCount} bounded shard(s)`,
  );
}

function runExtract(args) {
  const slugsFile = readOption(args, '--slugs-file', { required: true });
  const output = readOption(args, '--output', { required: true });
  const shardSize = parsePositiveInteger(
    readOption(args, '--shard-size', { fallback: '100' }),
    'shard-size',
    100,
  );
  const shardId = readOption(args, '--shard-id', { required: true });
  const shard = extractShard(readArtifact(slugsFile), shardId, shardSize);

  writeFileSync(output, `${shard.join('\n')}\n`, { mode: 0o600 });
  console.log(`Materialized cache invalidation shard ${shardId} (${shard.length} slug(s))`);
}

function main() {
  const [command, ...args] = process.argv.slice(2);
  switch (command) {
    case 'plan':
      runPlan(args);
      break;
    case 'extract':
      runExtract(args);
      break;
    default:
      throw new Error('usage: plan-cache-invalidation.mjs <plan|extract> [options]');
  }
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::${error.message}`);
    process.exitCode = 1;
  }
}
