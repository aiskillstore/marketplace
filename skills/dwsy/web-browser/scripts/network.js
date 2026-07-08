#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync, writeFileSync } from "node:fs";
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
  console.log("Usage: network.js <action> [args]");
  console.log("\nActions:");
  console.log("  start                   - Start monitoring network requests");
  console.log("  stop                    - Stop monitoring and return results");
  console.log("  capture <url>           - Monitor requests while navigating to URL");
  console.log("  export <file>           - Export captured requests to file");
  console.log("\nExamples:");
  console.log('  network.js start');
  console.log('  network.js stop');
  console.log('  network.js capture "https://example.com"');
  console.log('  network.js export requests.json');
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

const requests = [];
const responses = [];

try {
  if (action === "start") {
    p.on('request', req => {
      requests.push({
        method: req.method(),
        url: req.url(),
        resourceType: req.resourceType(),
        headers: req.headers(),
      });
    });

    p.on('response', res => {
      responses.push({
        url: res.url(),
        status: res.status(),
        headers: res.headers(),
      });
    });

    console.log("✓ Started monitoring network requests");
    console.log("  Run 'network.js stop' to view results");
  } else if (action === "stop") {
    console.log(`Requests: ${requests.length}`);
    console.log("=".repeat(80));

    requests.forEach((req, i) => {
      console.log(`[${i + 1}] ${req.method} ${req.resourceType}`);
      console.log(`    URL: ${req.url}`);
      const resp = responses.find(r => r.url === req.url);
      if (resp) {
        console.log(`    Status: ${resp.status}`);
      }
      console.log();
    });

    const failed = responses.filter(r => r.status >= 400);
    if (failed.length > 0) {
      console.log("\nFailed Requests:");
      console.log("=".repeat(80));
      failed.forEach(r => {
        console.log(`  ${r.status} - ${r.url}`);
      });
    }
  } else if (action === "capture") {
    const url = process.argv[3];
    if (!url) {
      console.error("✗ URL required");
      process.exit(1);
    }

    p.on('request', req => {
      requests.push({
        method: req.method(),
        url: req.url(),
        resourceType: req.resourceType(),
        headers: req.headers(),
      });
    });

    p.on('response', res => {
      responses.push({
        url: res.url(),
        status: res.status(),
        headers: res.headers(),
      });
    });

    await p.goto(url, { waitUntil: 'networkidle0' });

    console.log(`Captured ${requests.length} requests`);
    console.log("=".repeat(80));

    requests.forEach((req, i) => {
      console.log(`[${i + 1}] ${req.method} ${req.resourceType}`);
      console.log(`    URL: ${req.url}`);
      const resp = responses.find(r => r.url === req.url);
      if (resp) {
        console.log(`    Status: ${resp.status}`);
      }
      console.log();
    });
  } else if (action === "export") {
    const file = process.argv[3] || "requests.json";
    const data = { requests, responses };
    writeFileSync(file, JSON.stringify(data, null, 2));
    console.log(`✓ Exported ${requests.length} requests to ${file}`);
  } else {
    console.error(`✗ Unknown action: ${action}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();