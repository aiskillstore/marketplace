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

if (!type) {
  console.log("Usage: clear-data.js <type>");
  console.log("\nTypes:");
  console.log("  cookies         - Clear all cookies");
  console.log("  localStorage    - Clear localStorage");
  console.log("  sessionStorage  - Clear sessionStorage");
  console.log("  cache           - Clear browser cache");
  console.log("  all             - Clear everything");
  console.log("\nExamples:");
  console.log('  clear-data.js cookies');
  console.log('  clear-data.js localStorage');
  console.log('  clear-data.js all');
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
  const client = await p.target().createCDPSession();

  if (type === "cookies" || type === "all") {
    await client.send('Network.clearBrowserCookies');
    console.log("✓ Cleared cookies");
  }

  if (type === "localStorage" || type === "all") {
    await p.evaluate(() => localStorage.clear());
    console.log("✓ Cleared localStorage");
  }

  if (type === "sessionStorage" || type === "all") {
    await p.evaluate(() => sessionStorage.clear());
    console.log("✓ Cleared sessionStorage");
  }

  if (type === "cache" || type === "all") {
    await client.send('Network.clearBrowserCache');
    console.log("✓ Cleared browser cache");
  }

  if (type === "all") {
    console.log("\n✓ All data cleared");
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();