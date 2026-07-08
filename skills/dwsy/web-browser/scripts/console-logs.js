#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");
const logFile = join(profileDir, "console.log");

if (!existsSync(portFile)) {
  console.error("✗ Browser not started. Run 'node scripts/start.js' first.");
  process.exit(1);
}

const port = parseInt(readFileSync(portFile, "utf-8").trim());

const b = await puppeteer.connect({
  browserURL: `http://localhost:${port}`,
  defaultViewport: null,
});

const page = (await b.pages()).at(-1);

if (!page) {
  console.error("✗ No active tab found");
  process.exit(1);
}

// Listen for console events
page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [${type.toUpperCase()}] ${text}\n`;
  
  console.log(logEntry);
  writeFileSync(logFile, logEntry, { flag: 'a' });
});

page.on('pageerror', error => {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [ERROR] ${error.message}\n`;
  
  console.log(logEntry);
  writeFileSync(logFile, logEntry, { flag: 'a' });
});

console.log("✓ Console logging started. Press Ctrl+C to stop.");
console.log("Logs are being saved to:", logFile);

// Keep the script running
let running = true;
process.on('SIGINT', async () => {
  console.log("\n✓ Stopping console logging...");
  running = false;
  try {
    await b.disconnect();
  } catch (e) {}
  process.exit(0);
});

// Simple keep-alive
const runLoop = async () => {
  while (running) {
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
};
runLoop();