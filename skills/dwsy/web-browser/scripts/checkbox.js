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

const selector = process.argv[2];
const action = process.argv[3];

if (!selector || !action) {
  console.log("Usage: checkbox.js <selector> <action>");
  console.log("\nActions:");
  console.log("  check    - Check the checkbox/radiobutton");
  console.log("  uncheck  - Uncheck the checkbox");
  console.log("  toggle   - Toggle current state");
  console.log("\nExamples:");
  console.log('  checkbox.js "#terms" check');
  console.log('  checkbox.js "#newsletter" uncheck');
  console.log('  checkbox.js "[name=privacy]" toggle');
  process.exit(1);
}

if (!["check", "uncheck", "toggle"].includes(action)) {
  console.error("✗ Invalid action. Must be: check, uncheck, or toggle");
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
  await p.waitForSelector(selector, { timeout: 5000 });

  const isChecked = await p.$eval(selector, (el) => el.checked);

  if (action === "check") {
    if (isChecked) {
      console.log(`✓ ${selector} is already checked`);
    } else {
      await p.$eval(selector, (el) => el.checked = true);
      console.log(`✓ Checked: ${selector}`);
    }
  } else if (action === "uncheck") {
    if (!isChecked) {
      console.log(`✓ ${selector} is already unchecked`);
    } else {
      await p.$eval(selector, (el) => el.checked = false);
      console.log(`✓ Unchecked: ${selector}`);
    }
  } else if (action === "toggle") {
    if (isChecked) {
      await p.$eval(selector, (el) => el.checked = false);
      console.log(`✓ Toggled: ${selector} (unchecked)`);
    } else {
      await p.$eval(selector, (el) => el.checked = true);
      console.log(`✓ Toggled: ${selector} (checked)`);
    }
  }
} catch (error) {
  console.error(`✗ Failed to ${action}: ${selector}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();