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
const text = process.argv[3];
const options = process.argv[4] === "--clear" ? { clear: true } : {};

if (!selector || !text) {
  console.log("Usage: type.js <selector> <text> [--clear]");
  console.log("\nExamples:");
  console.log('  type.js "#username" "john@example.com"');
  console.log('  type.js "#password" "secret123"');
  console.log('  type.js "#search" "query" --clear');
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

  if (options.clear) {
    await p.click(selector);
    await p.keyboard.down("Control");
    await p.keyboard.press("A");
    await p.keyboard.up("Control");
    await p.keyboard.press("Backspace");
  }

  await p.type(selector, text);
  console.log(`✓ Typed into ${selector}: "${text}"`);
} catch (error) {
  console.error(`✗ Failed to type into: ${selector}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();