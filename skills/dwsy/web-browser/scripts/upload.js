#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");

if (!existsSync(portFile)) {
  console.error("✗ Browser not started. Run 'node scripts/start.js' first.");
  process.exit(1);
}

const port = parseInt(readFileSync(portFile, "utf-8").trim());

const selector = process.argv[2];
const filePath = process.argv[3];

if (!selector || !filePath) {
  console.log("Usage: upload.js <selector> <file-path>");
  console.log("\nExamples:");
  console.log('  upload.js "#file-input" "/path/to/file.txt"');
  console.log('  upload.js "input[type=file]" "./image.png"');
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
  const absolutePath = resolve(filePath);

  await p.waitForSelector(selector, { timeout: 5000 });
  const fileInput = await p.$(selector);

  if (!fileInput) {
    console.error(`✗ Element not found: ${selector}`);
    process.exit(1);
  }

  await fileInput.uploadFile(absolutePath);
  console.log(`✓ Uploaded file to ${selector}: ${absolutePath}`);
} catch (error) {
  console.error(`✗ Failed to upload file: ${error.message}`);
  process.exit(1);
}

await b.disconnect();