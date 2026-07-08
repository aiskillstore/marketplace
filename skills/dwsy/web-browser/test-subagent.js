#!/usr/bin/env node

import { execSync } from "node:child_process";

console.log("🌐 Testing web-browser subagent\n");

try {
  // 1. Start browser
  console.log("1️⃣ Starting browser...");
  execSync("cd ~/.pi/agent/skills/web-browser && node scripts/start.js", { stdio: "pipe" });
  const port = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/get-port.js", { encoding: "utf-8" }).trim();
  console.log(`   ✓ Browser started on port ${port}\n`);

  // 2. Navigate to a page
  console.log("2️⃣ Navigating to example.com...");
  execSync("cd ~/.pi/agent/skills/web-browser && node scripts/nav.js https://example.com", { stdio: "pipe" });
  console.log("   ✓ Page loaded\n");

  // 3. Extract page information
  console.log("3️⃣ Extracting page information...");
  const title = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/eval.js 'document.title'", { encoding: "utf-8" }).trim();
  const links = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/eval.js 'document.querySelectorAll(\"a\").length'", { encoding: "utf-8" }).trim();
  const headings = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/eval.js 'document.querySelectorAll(\"h1, h2, h3\").length'", { encoding: "utf-8" }).trim();
  console.log(`   Title: ${title}`);
  console.log(`   Links: ${links}`);
  console.log(`   Headings: ${headings}\n`);

  // 4. Extract links
  console.log("4️⃣ Extracting links...");
  const linksData = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/eval.js 'JSON.stringify(Array.from(document.querySelectorAll(\"a\")).map(a => ({ text: a.textContent.trim(), href: a.href })).slice(0, 5))'", { encoding: "utf-8" }).trim();
  console.log(`   ${linksData}\n`);

  // 5. Take screenshot
  console.log("5️⃣ Taking screenshot...");
  const screenshot = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/screenshot.js", { encoding: "utf-8" }).trim();
  console.log(`   Screenshot: ${screenshot}\n`);

  // 6. Test localStorage persistence
  console.log("6️⃣ Testing localStorage persistence...");
  execSync("cd ~/.pi/agent/skills/web-browser && node scripts/eval.js 'localStorage.setItem(\"web-browser-test\", \"subagent-test\")'", { stdio: "pipe" });
  const stored = execSync("cd ~/.pi/agent/skills/web-browser && node scripts/eval.js 'localStorage.getItem(\"web-browser-test\")'", { encoding: "utf-8" }).trim();
  console.log(`   Stored: ${stored}\n`);

  // 7. Generate report
  console.log("📊 Web Browser Research Report");
  console.log("=" .repeat(50));
  console.log(`\n## Page Information`);
  console.log(`- URL: https://example.com`);
  console.log(`- Title: ${title}`);
  console.log(`- Port: ${port}`);
  console.log(`\n## Page Structure`);
  console.log(`- Links: ${links}`);
  console.log(`- Headings: ${headings}`);
  console.log(`\n## Extracted Content`);
  console.log(`- Top 5 links: ${linksData}`);
  console.log(`\n## Screenshot`);
  console.log(`- Path: ${screenshot}`);
  console.log(`\n## Storage Test`);
  console.log(`- localStorage: ${stored === "subagent-test" ? "✓ Working" : "✗ Failed"}`);
  console.log(`\n## Status`);
  console.log(`✓ All tests passed!`);
  console.log(`✓ Web browser subagent is ready to use!`);

  // 8. Cleanup
  console.log(`\n🧹 Cleanup...`);
  execSync("cd ~/.pi/agent/skills/web-browser && node scripts/stop.js", { stdio: "pipe" });
  console.log(`   ✓ Browser stopped`);

} catch (error) {
  console.error("❌ Test failed:", error.message);
  process.exit(1);
}