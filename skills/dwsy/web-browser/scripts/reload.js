#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");

if (!existsSync(portFile)) {
  console.error("✗ Browser not started. Run 'node scripts/start.js' first.");
  process.exit(1);
}

const port = parseInt(readFileSync(portFile, "utf-8").trim());

const options = process.argv.slice(2);
const forceCache = options.includes("--force-cache");
const forceNoCache = options.includes("--force-no-cache");

if (!forceCache && !forceNoCache && options.length > 0) {
  console.log("Usage: reload.js [options]");
  console.log("\nOptions:");
  console.log("  --force-cache    - Force using cached resources");
  console.log("  --force-no-cache - Force reload without cache");
  console.log("\nExamples:");
  console.log('  reload.js');
  console.log('  reload.js --force-cache');
  console.log('  reload.js --force-no-cache');
  process.exit(1);
}

const b = await puppeteer.connect({
  browserURL: `http://localhost:${port}`,
  defaultViewport: null,
});

const p = (await b.pages()).at(-1);

if (!p) {
  console.error("✗ No active tab found");
  process.exit(1);
}

try {
  let waitUntil = 'networkidle0';

  if (forceCache) {
    waitUntil = 'load';
  } else if (forceNoCache) {
    await p.setCacheEnabled(false);
    await p.reload({ waitUntil: 'networkidle0' });
    await p.setCacheEnabled(true);
    console.log("✓ Reloaded page (no cache)");
    await b.disconnect();
    process.exit(0);
  }

  await p.reload({ waitUntil });
  console.log(`✓ Reloaded page`);
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();