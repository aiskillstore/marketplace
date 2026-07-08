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

const searchText = process.argv[2];
const options = process.argv.slice(3);
const caseSensitive = options.includes("--case-sensitive");

if (!searchText) {
  console.log("Usage: find-text.js <text> [options]");
  console.log("\nOptions:");
  console.log("  --case-sensitive  - Case sensitive search");
  console.log("\nExamples:");
  console.log('  find-text.js "Hello World"');
  console.log('  find-text.js "Error" --case-sensitive');
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
  const results = await p.evaluate((text, isCaseSensitive) => {
    const matches = [];

    function searchNode(node, path = []) {
      if (node.nodeType === Node.TEXT_NODE) {
        const content = isCaseSensitive ? node.textContent : node.textContent.toLowerCase();
        const search = isCaseSensitive ? text : text.toLowerCase();

        let index = content.indexOf(search);
        while (index !== -1) {
          const rect = node.parentElement?.getBoundingClientRect();
          if (rect && rect.width > 0 && rect.height > 0) {
            matches.push({
              text: node.textContent.substring(index, index + text.length),
              context: node.textContent.substring(Math.max(0, index - 20), index + text.length + 20),
              position: {
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height),
              },
              tag: node.parentElement?.tagName.toLowerCase(),
              id: node.parentElement?.id || null,
            });
          }
          index = content.indexOf(search, index + 1);
        }
      }

      for (const child of node.childNodes) {
        searchNode(child, [...path, node]);
      }
    }

    searchNode(document.body);
    return matches;
  }, searchText, caseSensitive);

  if (results.length === 0) {
    console.log(`✗ No matches found for: "${searchText}"`);
    process.exit(0);
  }

  console.log(`Found ${results.length} match(es) for: "${searchText}"`);
  console.log("=".repeat(80));

  results.forEach((match, i) => {
    console.log(`\n[${i + 1}] "${match.text}"`);
    console.log(`Context: ...${match.context}...`);
    console.log(`Position: (${match.position.x}, ${match.position.y})`);
    console.log(`Element: ${match.tag}${match.id ? '#' + match.id : ''}`);
  });

} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();