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

const expectedUrl = process.argv[2];
const timeout = parseInt(process.argv[3]) || 30000;

if (!expectedUrl) {
  console.log("Usage: wait-for-url.js <expected-url> [timeout]");
  console.log("\nExamples:");
  console.log('  wait-for-url.js "https://example.com/dashboard"');
  console.log('  wait-for-url.js "/success" 5000');
  console.log('  wait-for-url.js "example.com"');
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
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const currentUrl = p.url();
    if (currentUrl.includes(expectedUrl)) {
      console.log(`✓ URL changed to: ${currentUrl}`);
      await b.disconnect();
      process.exit(0);
    }
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error(`Timeout after ${timeout}ms`);
} catch (error) {
  console.error(`✗ Timeout waiting for URL to contain: ${expectedUrl}`);
  console.error(`  Current URL: ${p.url()}`);
  process.exit(1);
}