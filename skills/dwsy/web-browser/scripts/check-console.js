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

const url = process.argv[2];

const browser = await puppeteer.connect({
  browserURL: `http://localhost:${port}`,
  defaultViewport: null,
});

const page = (await browser.pages()).at(-1);

if (!page) {
  console.error("✗ No active tab found");
  process.exit(1);
}

// Collect console messages
const consoleMessages = [];

page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
  consoleMessages.push(`[${type.toUpperCase()}] ${text}`);
});

page.on('pageerror', error => {
  consoleMessages.push(`[ERROR] ${error.message}`);
});

// Navigate to the page if URL provided
const currentUrl = page.url();
console.log(`Current URL: ${currentUrl}`);

if (url && url !== currentUrl) {
  await page.goto(url, { waitUntil: 'networkidle0' });
  console.log(`Navigated to ${url}`);
}

// Wait a bit for any async errors
await new Promise(r => setTimeout(r, 2000));

// Print console messages
if (consoleMessages.length > 0) {
  console.log("\n=== Console Messages ===");
  consoleMessages.forEach(msg => console.log(msg));
} else {
  console.log("\nNo console messages captured");
}

await browser.disconnect();