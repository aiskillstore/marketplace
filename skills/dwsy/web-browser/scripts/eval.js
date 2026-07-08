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

const code = process.argv.slice(2).join(" ");
if (!code) {
  console.log("Usage: eval.js 'code'");
  console.log("\nExamples:");
  console.log('  eval.js "document.title"');
  console.log("  eval.js \"document.querySelectorAll('a').length\"");
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

let result;

try {
  result = await p.evaluate((c) => {
    const AsyncFunction = (async () => {}).constructor;
    // Check if code looks like an expression or statement
    // If it has semicolons or starts with keywords, treat as statement
    const trimmedCode = c.trim();
    const isStatement = /^[a-zA-Z_$]/.test(trimmedCode) &&
                        (trimmedCode.includes(';') ||
                         trimmedCode.includes('{') ||
                         trimmedCode.startsWith('if ') ||
                         trimmedCode.startsWith('for ') ||
                         trimmedCode.startsWith('while ') ||
                         trimmedCode.startsWith('const ') ||
                         trimmedCode.startsWith('let ') ||
                         trimmedCode.startsWith('var ') ||
                         trimmedCode.startsWith('return '));

    if (isStatement) {
      // Execute as statement
      return new AsyncFunction(c)();
    } else {
      // Execute as expression
      return new AsyncFunction(`return (${c})`)();
    }
  }, code);
} catch (e) {
  console.log("Failed to evaluate expression");
  console.log(`  Expression: ${code}`);
  console.log(e);
  process.exit(1);
}

if (Array.isArray(result)) {
  for (let i = 0; i < result.length; i++) {
    if (i > 0) console.log("");
    for (const [key, value] of Object.entries(result[i])) {
      console.log(`${key}: ${value}`);
    }
  }
} else if (typeof result === "object" && result !== null) {
  for (const [key, value] of Object.entries(result)) {
    console.log(`${key}: ${value}`);
  }
} else {
  console.log(result);
}

await b.disconnect();
