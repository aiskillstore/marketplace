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

const action = process.argv[2];

if (!action) {
  console.log("Usage: tabs.js <action> [args]");
  console.log("\nActions:");
  console.log("  list              - List all tabs");
  console.log("  new [url]         - Open new tab (optional URL)");
  console.log("  switch <index>    - Switch to tab by index");
  console.log("  close <index>     - Close tab by index");
  console.log("  close-others      - Close all other tabs");
  console.log("\nExamples:");
  console.log('  tabs.js list');
  console.log('  tabs.js new');
  console.log('  tabs.js new "https://example.com"');
  console.log('  tabs.js switch 1');
  console.log('  tabs.js close 0');
  process.exit(1);
}

const b = await puppeteer.connect({
  browserURL: `http://localhost:${port}`,
  defaultViewport: null,
});

try {
  if (action === "list") {
    const pages = await b.pages();
    const activePage = (await b.pages()).at(-1);

    console.log(`Total tabs: ${pages.length}`);
    console.log("=".repeat(80));

    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const url = page.url();
      const title = await page.title();
      const isActive = page === activePage;

      console.log(`[${i}] ${isActive ? '► ' : '  '} ${title}`);
      console.log(`    ${url}`);
    }
  } else if (action === "new") {
    const url = process.argv[3];
    const newPage = await b.newPage();

    if (url) {
      await newPage.goto(url, { waitUntil: 'domcontentloaded' });
      console.log(`✓ Opened new tab: ${url}`);
    } else {
      console.log(`✓ Opened new blank tab`);
    }
  } else if (action === "switch") {
    const index = parseInt(process.argv[3]);
    if (isNaN(index)) {
      console.error("✗ Invalid index");
      process.exit(1);
    }

    const pages = await b.pages();
    if (index < 0 || index >= pages.length) {
      console.error(`✗ Index out of range (0-${pages.length - 1})`);
      process.exit(1);
    }

    await pages[index].bringToFront();
    const title = await pages[index].title();
    console.log(`✓ Switched to tab [${index}]: ${title}`);
  } else if (action === "close") {
    const index = parseInt(process.argv[3]);
    if (isNaN(index)) {
      console.error("✗ Invalid index");
      process.exit(1);
    }

    const pages = await b.pages();
    if (index < 0 || index >= pages.length) {
      console.error(`✗ Index out of range (0-${pages.length - 1})`);
      process.exit(1);
    }

    await pages[index].close();
    console.log(`✓ Closed tab [${index}]`);
  } else if (action === "close-others") {
    const pages = await b.pages();
    const activePage = pages.at(-1);

    for (let i = 0; i < pages.length - 1; i++) {
      if (pages[i] !== activePage) {
        await pages[i].close();
      }
    }

    console.log(`✓ Closed all other tabs`);
  } else {
    console.error(`✗ Unknown action: ${action}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();