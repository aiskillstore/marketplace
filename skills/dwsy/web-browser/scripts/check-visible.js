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
  console.log("Usage: check-visible.js <selector>");
  console.log("\nExamples:");
  console.log('  check-visible.js "#button"');
  console.log('  check-visible.js ".modal"');
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
  const isVisible = await p.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
  }, selector);
  console.log(isVisible ? `✓ ${selector} is visible` : `✗ ${selector} is not visible`);
} catch (error) {
  console.error(`✗ Error checking visibility: ${selector}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();