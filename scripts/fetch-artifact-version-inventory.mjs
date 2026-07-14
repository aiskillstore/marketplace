#!/usr/bin/env node

import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const PAGE_SIZE = 1000;
const SELECT = [
  'slug',
  'plugin_path',
  'marketplace_commit_sha',
  'content_hash',
  'tree_hash',
  'artifact_revision',
  'current_artifact_version_id',
  'status',
  'public_eligible',
  'published_at',
  'updated_at',
].join(',');

function fail(message) {
  throw new Error(message);
}

export async function fetchArtifactVersionInventory({ supabaseUrl, serviceKey, fetchImpl = fetch }) {
  if (!/^https:\/\//.test(supabaseUrl || '')) fail('SUPABASE_URL must be HTTPS');
  if (!serviceKey) fail('SUPABASE_SERVICE_KEY is required');

  const rows = [];
  let expectedTotal = null;
  for (let start = 0; ; start += PAGE_SIZE) {
    const url = new URL('/rest/v1/skills', supabaseUrl);
    url.searchParams.set('select', SELECT);
    url.searchParams.set('order', 'slug.asc');
    const response = await fetchImpl(url, {
      headers: {
        apikey: serviceKey,
        Authorization: `Bearer ${serviceKey}`,
        'Accept-Profile': 'skillstore',
        Prefer: 'count=exact',
        Range: `${start}-${start + PAGE_SIZE - 1}`,
        'Range-Unit': 'items',
      },
    });
    if (!response.ok) fail(`Production inventory request failed: HTTP ${response.status}`);
    const contentRange = response.headers.get('content-range');
    const match = contentRange?.match(/^(\d+)-(\d+)\/(\d+)$/);
    if (!match) fail(`Production inventory returned invalid Content-Range: ${contentRange ?? '<missing>'}`);
    const total = Number(match[3]);
    if (expectedTotal === null) expectedTotal = total;
    if (total !== expectedTotal) fail('Production inventory count changed during pagination');

    const page = await response.json();
    if (!Array.isArray(page)) fail('Production inventory response is not an array');
    rows.push(...page);
    if (rows.length >= expectedTotal) break;
    if (page.length === 0) fail('Production inventory pagination ended before the exact count');
  }
  if (rows.length !== expectedTotal) {
    fail(`Production inventory count mismatch: expected ${expectedTotal}, received ${rows.length}`);
  }
  return { schemaVersion: 1, count: rows.length, rows };
}

export async function main(argv = process.argv.slice(2)) {
  const outputIndex = argv.indexOf('--output');
  const output = outputIndex >= 0 ? argv[outputIndex + 1] : null;
  if (!output) fail('--output is required');
  const inventory = await fetchArtifactVersionInventory({
    supabaseUrl: process.env.SUPABASE_URL,
    serviceKey: process.env.SUPABASE_SERVICE_KEY,
  });
  writeFileSync(resolve(output), `${JSON.stringify(inventory, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify({ count: inventory.count })}\n`);
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) {
  main().catch((error) => {
    process.stderr.write(`artifact inventory fetch failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
