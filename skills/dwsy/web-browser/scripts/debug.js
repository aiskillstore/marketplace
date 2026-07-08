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
  console.log("Browser Debug Information");
  console.log("=".repeat(50));

  const pageInfo = await p.evaluate(() => {
    return {
      url: window.location.href,
      title: document.title,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
      scroll: {
        x: window.scrollX,
        y: window.scrollY,
        max: document.body.scrollHeight,
      },
      cookies: document.cookie,
      localStorage: Object.keys(localStorage).length,
      sessionStorage: Object.keys(sessionStorage).length,
    };
  });

  console.log(`URL: ${pageInfo.url}`);
  console.log(`Title: ${pageInfo.title}`);
  console.log(`User Agent: ${pageInfo.userAgent}`);
  console.log(`\nViewport: ${pageInfo.viewport.width}x${pageInfo.viewport.height}`);
  console.log(`Scroll: ${pageInfo.scroll.x}, ${pageInfo.scroll.y} / ${pageInfo.scroll.max}`);
  console.log(`Cookies: ${pageInfo.cookies ? "Set" : "None"}`);
  console.log(`localStorage: ${pageInfo.localStorage} keys`);
  console.log(`sessionStorage: ${pageInfo.sessionStorage} keys`);

  const errors = await p.evaluate(() => {
    const logs = [];
    const originalError = console.error;
    console.error = (...args) => logs.push(args.join(' '));
    return logs;
  });

  if (errors.length > 0) {
    console.log(`\nConsole Errors: ${errors.length}`);
    errors.forEach(err => console.log(`  - ${err}`));
  }

  const browserInfo = await b.version();
  console.log(`\nBrowser: ${browserInfo}`);

  const allPages = await b.pages();
  console.log(`Total Tabs: ${allPages.length}`);

} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();