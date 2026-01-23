#!/usr/bin/env node

// Use playwright-core which uses pre-installed browsers from the Docker image
const { chromium } = require("playwright-core");

async function main() {
  const [url, action = "text", selector = "body"] = process.argv.slice(2);

  if (!url) {
    console.error("Error: URL is required");
    console.error("Usage: node run.js <url> [action] [selector]");
    process.exit(1);
  }

  console.log("Starting Playwright...");
  console.log(`URL: ${url}`);
  console.log(`Action: ${action}`);
  console.log(`Selector: ${selector}`);

  let browser;
  try {
    // Find Chromium in the Microsoft Playwright image
    const fs = require("node:fs");
    const path = require("node:path");

    let executablePath;
    const msPlaywrightDir = "/ms-playwright";

    if (fs.existsSync(msPlaywrightDir)) {
      const dirs = fs.readdirSync(msPlaywrightDir);
      const chromiumDir = dirs.find((d) => d.startsWith("chromium-"));
      if (chromiumDir) {
        executablePath = path.join(msPlaywrightDir, chromiumDir, "chrome-linux", "chrome");
      }
    }

    console.log(`Using browser at: ${executablePath || "default"}`);

    browser = await chromium.launch({
      headless: true,
      ...(executablePath ? { executablePath } : {}),
    });

    const context = await browser.newContext();
    const page = await context.newPage();

    console.log(`Navigating to ${url}...`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
    console.log("Page loaded successfully");

    switch (action) {
      case "screenshot": {
        const buffer = await page.screenshot({ fullPage: true });
        // Output base64 encoded screenshot
        console.log("SCREENSHOT_START");
        console.log(buffer.toString("base64"));
        console.log("SCREENSHOT_END");
        break;
      }
      case "html": {
        const element = await page.locator(selector);
        const html = await element.innerHTML();
        console.log(html);
        break;
      }
      default: {
        const element = await page.locator(selector);
        const text = await element.textContent();
        console.log(text?.trim() || "");
        break;
      }
    }
  } catch (error) {
    console.error("Playwright Error:", error.message);
    if (error.stack) {
      console.error("Stack trace:");
      console.error(error.stack);
    }
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

main();
