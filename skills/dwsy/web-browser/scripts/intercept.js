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
  console.log("Usage: intercept.js <action> [args]");
  console.log("\nActions:");
  console.log("  block <pattern>         - Block requests matching pattern");
  console.log("  mock <pattern> <json>   - Mock response for matching requests");
  console.log("  log <pattern>           - Log requests matching pattern");
  console.log("  clear                   - Clear all intercepts");
  console.log("\nExamples:");
  console.log('  intercept.js block "*.png"');
  console.log('  intercept.js block "*.jpg"');
  console.log('  intercept.js mock "/api/data" \'{"result":"success"}\'');
  console.log('  intercept.js log "/api/*"');
  console.log('  intercept.js clear');
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
  if (action === "block") {
    const pattern = process.argv[3];
    if (!pattern) {
      console.error("✗ Pattern required");
      process.exit(1);
    }

    await p.setRequestInterception(true);

    p.on('request', (req) => {
      if (req.url().includes(pattern)) {
        req.abort();
        console.log(`Blocked: ${req.url()}`);
      } else {
        req.continue();
      }
    });

    console.log(`✓ Blocking requests matching: ${pattern}`);
  } else if (action === "mock") {
    const pattern = process.argv[3];
    const json = process.argv[4];

    if (!pattern || !json) {
      console.error("✗ Pattern and JSON required");
      process.exit(1);
    }

    await p.setRequestInterception(true);

    p.on('request', (req) => {
      if (req.url().includes(pattern)) {
        req.respond({
          status: 200,
          contentType: 'application/json',
          body: json,
        });
        console.log(`Mocked: ${req.url()}`);
      } else {
        req.continue();
      }
    });

    console.log(`✓ Mocking requests matching: ${pattern}`);
  } else if (action === "log") {
    const pattern = process.argv[3];
    if (!pattern) {
      console.error("✗ Pattern required");
      process.exit(1);
    }

    await p.setRequestInterception(true);

    p.on('request', (req) => {
      if (req.url().includes(pattern)) {
        console.log(`[Request] ${req.method()} ${req.url()}`);
        console.log(`  Headers: ${JSON.stringify(req.headers(), null, 2)}`);
      }
      req.continue();
    });

    p.on('response', (res) => {
      if (res.url().includes(pattern)) {
        console.log(`[Response] ${res.status()} ${res.url()}`);
        console.log(`  Headers: ${JSON.stringify(res.headers(), null, 2)}`);
      }
    });

    console.log(`✓ Logging requests matching: ${pattern}`);
  } else if (action === "clear") {
    await p.setRequestInterception(false);

    try {
      const listeners = p.eventNames();
      if (listeners) {
        listeners.forEach(event => {
          p.removeAllListeners(event);
        });
      }
    } catch (e) {
      // eventNames may not be available in all versions
    }

    console.log("✓ Cleared all intercepts");
  } else {
    console.error(`✗ Unknown action: ${action}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();