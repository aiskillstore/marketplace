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

if (!selector) {
  console.log("Usage: hover.js <selector>");
  console.log("\nExamples:");
  console.log('  hover.js "#menu"');
  console.log('  hover.js ".dropdown"');
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
  await p.hover(selector);
  console.log(`✓ Hovered over: ${selector}`);
} catch (error) {
  console.error(`✗ Failed to hover over: ${selector}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();