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
  console.log("Usage: inspect.js <selector>");
  console.log("\nExamples:");
  console.log('  inspect.js "#button"');
  console.log('  inspect.js ".card"');
  console.log('  inspect.js "div.container"');
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
  const elements = await p.$$eval(selector, (els) => {
    return els.map(el => {
      const rect = el.getBoundingClientRect();
      const styles = window.getComputedStyle(el);

      return {
        tag: el.tagName.toLowerCase(),
        id: el.id || null,
        class: el.className || null,
        text: el.textContent?.trim().slice(0, 100) || null,
        html: el.outerHTML.slice(0, 300),
        visible: rect.width > 0 && rect.height > 0,
        position: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
        styles: {
          display: styles.display,
          visibility: styles.visibility,
          opacity: styles.opacity,
          zIndex: styles.zIndex,
          position: styles.position,
        },
        attributes: Array.from(el.attributes).reduce((acc, attr) => {
          acc[attr.name] = attr.value;
          return acc;
        }, {}),
        children: el.children.length,
      };
    });
  });

  if (elements.length === 0) {
    console.log(`✗ No elements found: ${selector}`);
    process.exit(0);
  }

  console.log(`Found ${elements.length} element(s): ${selector}`);
  console.log("=".repeat(80));

  elements.forEach((el, i) => {
    console.log(`\n[${i + 1}] ${el.tag}${el.id ? '#' + el.id : ''}${el.class ? '.' + el.class.split(' ').join('.') : ''}`);
    console.log("-".repeat(80));

    console.log(`Text: ${el.text || '(empty)'}`);
    console.log(`Visible: ${el.visible ? 'Yes' : 'No'}`);
    console.log(`Position: (${el.position.x}, ${el.position.y}) ${el.position.width}x${el.position.height}`);
    console.log(`Children: ${el.children}`);

    console.log("\nStyles:");
    for (const [key, value] of Object.entries(el.styles)) {
      console.log(`  ${key}: ${value}`);
    }

    if (Object.keys(el.attributes).length > 0) {
      console.log("\nAttributes:");
      for (const [key, value] of Object.entries(el.attributes)) {
        console.log(`  ${key}: ${value}`);
      }
    }

    if (el.html.length >= 300) {
      console.log(`\nHTML: ${el.html}...`);
    }
  });

} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();