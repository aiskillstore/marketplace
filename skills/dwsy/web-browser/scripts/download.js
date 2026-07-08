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

const action = process.argv[2];

if (!action) {
  console.log("Usage: download.js <action> [args]");
  console.log("\nActions:");
  console.log("  start <pattern>        - Start auto-downloading files matching pattern");
  console.log("  click <selector>       - Click element to trigger download");
  console.log("  list                   - List downloaded files");
  console.log("  clear                  - Clear downloads");
  console.log("\nExamples:");
  console.log('  download.js start "*.pdf"');
  console.log('  download.js click "#download-btn"');
  console.log('  download.js list');
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
  const client = await p.target().createCDPSession();

  if (action === "start") {
    const pattern = process.argv[3] || "*";

    await client.send('Page.setDownloadBehavior', {
      behavior: 'allow',
      downloadPath: tmpdir()
    });

    console.log(`✓ Auto-download enabled for pattern: ${pattern}`);
    console.log(`  Download path: ${tmpdir()}`);
  } else if (action === "click") {
    const selector = process.argv[3];
    if (!selector) {
      console.error("✗ Selector required");
      process.exit(1);
    }

    await client.send('Page.setDownloadBehavior', {
      behavior: 'allow',
      downloadPath: tmpdir()
    });

    await p.waitForSelector(selector, { timeout: 5000 });
    await p.click(selector);

    await new Promise(r => setTimeout(r, 2000));

    console.log(`✓ Download triggered from: ${selector}`);
    console.log(`  Check ${tmpdir()} for downloaded files`);
  } else if (action === "list") {
    const files = await p.evaluate(() => {
      return Array.from(document.querySelectorAll('a[href]'))
        .filter(a => a.href.match(/\.(pdf|zip|tar|gz|txt|csv|xls|xlsx|doc|docx)$/i))
        .map(a => ({
          text: a.textContent?.trim(),
          url: a.href
        }));
    });

    console.log(`Downloadable links: ${files.length}`);
    console.log("=".repeat(80));
    files.forEach((f, i) => {
      console.log(`[${i + 1}] ${f.text}`);
      console.log(`    ${f.url}`);
    });
  } else if (action === "clear") {
    await client.send('Page.setDownloadBehavior', {
      behavior: 'deny'
    });
    console.log("✓ Auto-download disabled");
  } else {
    console.error(`✗ Unknown action: ${action}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();