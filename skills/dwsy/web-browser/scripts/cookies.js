#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync, writeFileSync } from "node:fs";
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
  console.log("Usage: cookies.js <action> [args]");
  console.log("\nActions:");
  console.log("  list                    - List all cookies");
  console.log("  get <name>              - Get specific cookie");
  console.log("  set <name> <value>      - Set cookie");
  console.log("  delete <name>           - Delete cookie");
  console.log("  clear                   - Clear all cookies");
  console.log("  export <file>           - Export cookies to file");
  console.log("  import <file>           - Import cookies from file");
  console.log("\nExamples:");
  console.log('  cookies.js list');
  console.log('  cookies.js get "session"');
  console.log('  cookies.js set "token" "abc123"');
  console.log('  cookies.js delete "session"');
  console.log('  cookies.js clear');
  console.log('  cookies.js export cookies.json');
  console.log('  cookies.js import cookies.json');
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
  if (action === "list") {
    const cookies = await p.cookies();
    console.log(`Total cookies: ${cookies.length}`);
    console.log("=".repeat(80));
    cookies.forEach(c => {
      console.log(`Name: ${c.name}`);
      console.log(`Value: ${c.value}`);
      console.log(`Domain: ${c.domain}`);
      console.log(`Path: ${c.path}`);
      console.log(`Expires: ${c.expires ? new Date(c.expires * 1000).toISOString() : 'Session'}`);
      console.log(`Secure: ${c.secure} | HttpOnly: ${c.httpOnly} | SameSite: ${c.sameSite}`);
      console.log("-".repeat(80));
    });
  } else if (action === "get") {
    const name = process.argv[3];
    if (!name) {
      console.error("✗ Cookie name required");
      process.exit(1);
    }
    const cookies = await p.cookies();
    const cookie = cookies.find(c => c.name === name);
    if (cookie) {
      console.log(`Name: ${cookie.name}`);
      console.log(`Value: ${cookie.value}`);
      console.log(`Domain: ${cookie.domain}`);
      console.log(`Path: ${cookie.path}`);
      console.log(`Expires: ${cookie.expires ? new Date(cookie.expires * 1000).toISOString() : 'Session'}`);
    } else {
      console.log(`✗ Cookie not found: ${name}`);
    }
  } else if (action === "set") {
    const name = process.argv[3];
    const value = process.argv[4];
    if (!name || !value) {
      console.error("✗ Cookie name and value required");
      process.exit(1);
    }
    await p.setCookie({ name, value, url: p.url() });
    console.log(`✓ Set cookie: ${name}`);
  } else if (action === "delete") {
    const name = process.argv[3];
    if (!name) {
      console.error("✗ Cookie name required");
      process.exit(1);
    }
    await p.deleteCookie({ name });
    console.log(`✓ Deleted cookie: ${name}`);
  } else if (action === "clear") {
    const client = await p.target().createCDPSession();
    await client.send('Network.clearBrowserCookies');
    console.log("✓ Cleared all cookies");
  } else if (action === "export") {
    const file = process.argv[3] || "cookies.json";
    const cookies = await p.cookies();
    writeFileSync(file, JSON.stringify(cookies, null, 2));
    console.log(`✓ Exported ${cookies.length} cookies to ${file}`);
  } else if (action === "import") {
    const file = process.argv[3];
    if (!file) {
      console.error("✗ File path required");
      process.exit(1);
    }
    const cookies = JSON.parse(readFileSync(file, "utf-8"));
    await p.setCookie(...cookies);
    console.log(`✓ Imported ${cookies.length} cookies from ${file}`);
  } else {
    console.error(`✗ Unknown action: ${action}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();