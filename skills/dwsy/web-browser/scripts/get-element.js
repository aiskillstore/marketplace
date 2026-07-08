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

if (!selector) {
  console.log("Usage: get-element.js <selector>");
  console.log("\nExamples:");
  console.log('  get-element.js "#button"');
  console.log('  get-element.js ".card"');
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
  const info = await p.$eval(selector, (el) => {
    const rect = el.getBoundingClientRect();
    const attrs = {};
    try {
      if (el.attributes) {
        for (let i = 0; i < el.attributes.length; i++) {
          attrs[el.attributes[i].name] = el.attributes[i].value;
        }
      }
    } catch (e) {
      // Ignore attributes error
    }

    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      class: el.className || null,
      text: el.textContent?.trim().slice(0, 200) || null,
      html: el.outerHTML?.slice(0, 500) || null,
      visible: rect.width > 0 && rect.height > 0,
      position: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      },
      attributes: attrs,
    };
  });

  console.log(`Element: ${selector}`);
  console.log("=".repeat(50));

  if (!info) {
    console.error("✗ Element info is null");
    process.exit(1);
  }

  console.log(`Tag: ${info.tag}`);
  console.log(`ID: ${info.id || '(none)'}`);
  console.log(`Class: ${info.class || '(none)'}`);
  console.log(`Text: ${info.text || '(empty)'}`);
  console.log(`Visible: ${info.visible ? 'Yes' : 'No'}`);
  console.log(`Position: (${info.position.x}, ${info.position.y}) ${info.position.width}x${info.position.height}`);

  if (info.html) {
    console.log(`\nHTML: ${info.html}`);
  }

  if (Object.keys(info.attributes).length > 0) {
    console.log(`\nAttributes:`);
    for (const [k, v] of Object.entries(info.attributes)) {
      console.log(`  ${k}: ${v}`);
    }
  }
} catch (error) {
  console.error(`✗ Error getting element: ${selector}`);
  console.error(`  ${error.message}`);
  process.exit(1);
}

await b.disconnect();