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

const type = process.argv[2];
const value = process.argv[3];
const timeout = parseInt(process.argv[4]) || 30000;

if (!type || !value) {
  console.log("Usage: wait-for.js <type> <value> [timeout]");
  console.log("\nTypes:");
  console.log("  selector  - Wait for CSS selector to be present");
  console.log("  visible   - Wait for element to be visible");
  console.log("  hidden    - Wait for element to be hidden");
  console.log("  text      - Wait for text to appear on page");
  console.log("  url       - Wait for URL to contain text");
  console.log("\nExamples:");
  console.log('  wait-for.js selector "#result"');
  console.log('  wait-for.js visible ".loading"');
  console.log('  wait-for.js hidden ".spinner"');
  console.log('  wait-for.js text "Success"');
  console.log('  wait-for.js url "/dashboard" 5000');
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
  if (type === "selector" || type === "visible") {
    await p.waitForSelector(value, { visible: type === "visible", timeout });
    console.log(`✓ Found ${type}: ${value}`);
  } else if (type === "hidden") {
    await p.waitForSelector(value, { hidden: true, timeout });
    console.log(`✓ Element hidden: ${value}`);
  } else if (type === "text") {
    await p.waitForFunction(
      (text) => document.body.innerText.includes(text),
      { timeout },
      value
    );
    console.log(`✓ Found text: "${value}"`);
  } else if (type === "url") {
    await p.waitForFunction(
      (text) => window.location.href.includes(text),
      { timeout },
      value
    );
    console.log(`✓ URL contains: "${value}"`);
  } else {
    console.error(`✗ Unknown type: ${type}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Timeout waiting for ${type}: ${value}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();