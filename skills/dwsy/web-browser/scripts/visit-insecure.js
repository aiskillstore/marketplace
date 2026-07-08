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

if (!url) {
  console.log("Usage: visit-insecure.js <url>");
  console.log("  Navigates to URL ignoring SSL certificate errors");
  process.exit(1);
}

const b = await puppeteer.connect({
  browserURL: `http://localhost:${port}`,
  defaultViewport: null,
});

// Get existing context and set ignoreHTTPSErrors via CDP
const target = b.target();
const cdp = await target.createCDPSession();

// Enable security domain and ignore certificate errors
await cdp.send('Security.setIgnoreCertificateErrors', { ignore: true });

const pages = await b.pages();
const p = pages.at(-1) ?? await b.newPage();

// Navigate with longer timeout and wait for network idle
await p.goto(url, { 
  waitUntil: "networkidle2",
  timeout: 60000 
});

console.log("✓ Navigated to:", url);

await b.disconnect();
