#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");

if (!existsSync(portFile)) {
  console.error("✗ Browser not started. Run 'node scripts/start.js' first.");
  process.exit(1);
}

const port = parseInt(readFileSync(portFile, "utf-8").trim());

const outputPath = process.argv[2];
const format = process.argv[3] || "A4";

if (!outputPath) {
  console.log("Usage: pdf.js <output-path> [format]");
  console.log("\nFormats:");
  console.log("  A4    - A4 paper size (default)");
  console.log("  A3    - A3 paper size");
  console.log("  Letter - Letter paper size");
  console.log("  Legal - Legal paper size");
  console.log("\nExamples:");
  console.log('  pdf.js ./page.pdf');
  console.log('  pdf.js ./page.pdf A4');
  console.log('  pdf.js ~/Downloads/report.pdf Letter');
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
  const pdf = await p.pdf({
    path: outputPath,
    format: format,
    printBackground: true,
    margin: {
      top: '1cm',
      right: '1cm',
      bottom: '1cm',
      left: '1cm'
    }
  });

  console.log(`✓ PDF saved: ${outputPath}`);
  console.log(`  Size: ${(pdf.length / 1024).toFixed(2)} KB`);
  console.log(`  Format: ${format}`);
} catch (error) {
  console.error(`✗ Failed to generate PDF: ${error.message}`);
  process.exit(1);
}

await b.disconnect();