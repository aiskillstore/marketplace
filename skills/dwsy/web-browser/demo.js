#!/usr/bin/env node

import { execSync } from "node:child_process";

console.log("🌐 Web Browser Skill - Quick Start Demo\n");

try {
  // 1. Start browser
  console.log("1️⃣ Starting browser...");
  execSync("node scripts/start.js", { stdio: "pipe" });
  console.log("   ✓ Browser started\n");

  // 2. Navigate to a page
  console.log("2️⃣ Navigating to example.com...");
  execSync("node scripts/nav.js https://example.com", { stdio: "pipe" });
  console.log("   ✓ Page loaded\n");

  // 3. Get page title
  console.log("3️⃣ Getting page title...");
  const title = execSync("node scripts/eval.js 'document.title'", { encoding: "utf-8" }).trim();
  console.log(`   Title: ${title}\n`);

  // 4. Set and get localStorage
  console.log("4️⃣ Testing localStorage...");
  execSync('node scripts/eval.js \'localStorage.setItem("demo", "hello from web-browser")\'', { stdio: "pipe" });
  const stored = execSync('node scripts/eval.js \'localStorage.getItem("demo")\'', { encoding: "utf-8" }).trim();
  console.log(`   Stored value: ${stored}\n`);

  // 5. Take screenshot
  console.log("5️⃣ Taking screenshot...");
  const screenshot = execSync("node scripts/screenshot.js", { encoding: "utf-8" }).trim();
  console.log(`   Screenshot saved to: ${screenshot}\n`);

  console.log("✅ Demo completed!");
  console.log("\n📝 What happened:");
  console.log("  - Started independent browser instance");
  console.log("  - Navigated to example.com");
  console.log("  - Read page title");
  console.log("  - Set and retrieved localStorage");
  console.log("  - Took a screenshot");
  console.log("\n💡 Tip: Your main Chrome browser was NOT affected!");

} catch (error) {
  console.error("❌ Error:", error.message);
  process.exit(1);
}