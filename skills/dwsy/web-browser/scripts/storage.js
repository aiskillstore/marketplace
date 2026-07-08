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
  console.log("Usage: storage.js <action> [args]");
  console.log("\nActions:");
  console.log("  list                    - List all storage (localStorage + sessionStorage)");
  console.log("  get <type> <key>        - Get value from storage");
  console.log("  set <type> <key> <value> - Set value in storage");
  console.log("  delete <type> <key>     - Delete value from storage");
  console.log("  clear <type>            - Clear storage");
  console.log("\nTypes:");
  console.log("  local   - localStorage");
  console.log("  session - sessionStorage");
  console.log("\nExamples:");
  console.log('  storage.js list');
  console.log('  storage.js get local "token"');
  console.log('  storage.js set local "user" \'{"name":"John"}\'');
  console.log('  storage.js delete session "temp"');
  console.log('  storage.js clear local');
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
    const storage = await p.evaluate(() => {
      const local = {};
      const session = {};

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        local[key] = localStorage.getItem(key);
      }

      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        session[key] = sessionStorage.getItem(key);
      }

      return { local, session };
    });

    console.log("localStorage:");
    console.log(`  Keys: ${Object.keys(storage.local).length}`);
    for (const [key, value] of Object.entries(storage.local)) {
      console.log(`  ${key}: ${value}`);
    }

    console.log("\nsessionStorage:");
    console.log(`  Keys: ${Object.keys(storage.session).length}`);
    for (const [key, value] of Object.entries(storage.session)) {
      console.log(`  ${key}: ${value}`);
    }
  } else if (action === "get") {
    const type = process.argv[3];
    const key = process.argv[4];

    if (!type || !key) {
      console.error("✗ Type and key required");
      process.exit(1);
    }

    const value = await p.evaluate((t, k) => {
      const storage = t === "local" ? localStorage : sessionStorage;
      return storage.getItem(k);
    }, type, key);

    console.log(`${type}Storage["${key}"]: ${value}`);
  } else if (action === "set") {
    const type = process.argv[3];
    const key = process.argv[4];
    const value = process.argv[5];

    if (!type || !key || value === undefined) {
      console.error("✗ Type, key, and value required");
      process.exit(1);
    }

    await p.evaluate((t, k, v) => {
      const storage = t === "local" ? localStorage : sessionStorage;
      storage.setItem(k, v);
    }, type, key, value);

    console.log(`✓ Set ${type}Storage["${key}"] = "${value}"`);
  } else if (action === "delete") {
    const type = process.argv[3];
    const key = process.argv[4];

    if (!type || !key) {
      console.error("✗ Type and key required");
      process.exit(1);
    }

    await p.evaluate((t, k) => {
      const storage = t === "local" ? localStorage : sessionStorage;
      storage.removeItem(k);
    }, type, key);

    console.log(`✓ Deleted ${type}Storage["${key}"]`);
  } else if (action === "clear") {
    const type = process.argv[3];

    if (!type) {
      console.error("✗ Type required");
      process.exit(1);
    }

    await p.evaluate((t) => {
      const storage = t === "local" ? localStorage : sessionStorage;
      storage.clear();
    }, type);

    console.log(`✓ Cleared ${type}Storage`);
  } else {
    console.error(`✗ Unknown action: ${action}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();