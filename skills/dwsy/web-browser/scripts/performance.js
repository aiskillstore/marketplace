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
  const metrics = await p.metrics();

  console.log("Performance Metrics");
  console.log("=".repeat(50));

  const categories = {
    "Navigation": ["Timestamp", "NavigationStart", "FetchStart", "DomainLookupStart", "DomainLookupEnd", "ConnectStart", "ConnectEnd", "SecureConnectionStart", "RequestStart", "ResponseStart", "ResponseEnd", "DomContentLoaded", "DomComplete", "LoadEventStart", "LoadEventEnd"],
    "Timing": ["FirstPaint", "FirstContentfulPaint", "FirstMeaningfulPaint", "FirstInputDelay", "Interactive", "TotalBlockingTime"],
    "Memory": ["JSHeapUsedSize", "JSHeapTotalSize"],
  };

  for (const [category, keys] of Object.entries(categories)) {
    console.log(`\n${category}:`);
    for (const key of keys) {
      const value = metrics[key];
      if (value !== undefined) {
        if (key.includes("Size")) {
          console.log(`  ${key}: ${(value / 1024 / 1024).toFixed(2)} MB`);
        } else if (value > 0) {
          console.log(`  ${key}: ${value.toFixed(2)} ms`);
        } else {
          console.log(`  ${key}: ${value}`);
        }
      }
    }
  }

  const timing = await p.evaluate(() => {
    const t = performance.timing;
    return {
      dns: t.domainLookupEnd - t.domainLookupStart,
      tcp: t.connectEnd - t.connectStart,
      ttfb: t.responseStart - t.requestStart,
      download: t.responseEnd - t.responseStart,
      domProcessing: t.domComplete - t.domLoading,
      domContentLoaded: t.domContentLoadedEventEnd - t.domContentLoadedEventStart,
      pageLoad: t.loadEventEnd - t.navigationStart,
    };
  });

  console.log("\nTiming Breakdown:");
  console.log("=".repeat(50));
  for (const [key, value] of Object.entries(timing)) {
    console.log(`  ${key}: ${value.toFixed(2)} ms`);
  }

} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();