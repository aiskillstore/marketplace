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

const direction = process.argv[2];
const amount = parseInt(process.argv[3]) || 100;

if (!direction) {
  console.log("Usage: scroll.js <direction> [amount]");
  console.log("\nDirections:");
  console.log("  up       - Scroll up by amount pixels (default: 100)");
  console.log("  down     - Scroll down by amount pixels (default: 100)");
  console.log("  left     - Scroll left by amount pixels (default: 100)");
  console.log("  right    - Scroll right by amount pixels (default: 100)");
  console.log("  top      - Scroll to top of page");
  console.log("  bottom   - Scroll to bottom of page");
  console.log("  element  - Scroll to element (requires selector as 3rd arg)");
  console.log("\nExamples:");
  console.log('  scroll.js down 500');
  console.log('  scroll.js bottom');
  console.log('  scroll.js element "#section"');
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
  if (direction === "top") {
    await p.evaluate(() => window.scrollTo(0, 0));
    console.log("✓ Scrolled to top");
  } else if (direction === "bottom") {
    await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    console.log("✓ Scrolled to bottom");
  } else if (direction === "up") {
    await p.evaluate((amt) => window.scrollBy(0, -amt), amount);
    console.log(`✓ Scrolled up ${amount}px`);
  } else if (direction === "down") {
    await p.evaluate((amt) => window.scrollBy(0, amt), amount);
    console.log(`✓ Scrolled down ${amount}px`);
  } else if (direction === "left") {
    await p.evaluate((amt) => window.scrollBy(-amt, 0), amount);
    console.log(`✓ Scrolled left ${amount}px`);
  } else if (direction === "right") {
    await p.evaluate((amt) => window.scrollBy(amt, 0), amount);
    console.log(`✓ Scrolled right ${amount}px`);
  } else if (direction === "element") {
    const selector = process.argv[3];
    if (!selector) {
      console.error("✗ Selector required for element scroll");
      process.exit(1);
    }
    await p.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, selector);
    console.log(`✓ Scrolled to element: ${selector}`);
  } else {
    console.error(`✗ Unknown direction: ${direction}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();