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

const selector = process.argv[2];
const value = process.argv[3];

if (!selector || !value) {
  console.log("Usage: select.js <selector> <value>");
  console.log("\nExamples:");
  console.log('  select.js "#country" "United States"');
  console.log('  select.js "select[name=language]" "JavaScript"');
  console.log('  select.js ".dropdown" "Option 1"');
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
  await p.waitForSelector(selector, { timeout: 5000 });
  await p.select(selector, value);
  console.log(`✓ Selected "${value}" in ${selector}`);
} catch (error) {
  console.error(`✗ Failed to select in: ${selector}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();