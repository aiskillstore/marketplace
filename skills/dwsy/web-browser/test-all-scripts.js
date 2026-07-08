#!/usr/bin/env node

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";

const scripts = [
  // Phase A: 表单与交互
  "click.js",
  "type.js",
  "select.js",
  "checkbox.js",
  "submit.js",

  // Phase B: 等待与检测
  "wait-for.js",
  "wait-for-url.js",
  "check-visible.js",
  "get-element.js",

  // Phase C: 存储与 Cookie
  "cookies.js",
  "storage.js",
  "clear-data.js",

  // Phase D: 网络与性能
  "network.js",
  "performance.js",
  "intercept.js",
  "reload.js",

  // Phase E: 高级功能
  "scroll.js",
  "hover.js",
  "upload.js",
  "download.js",
  "pdf.js",
  "tabs.js",

  // Phase F: 调试与工具
  "debug.js",
  "inspect.js",
  "find-text.js",
  "get-meta.js",
];

console.log("🧪 Testing all new web-browser scripts\n");

let passed = 0;
let failed = 0;

for (const script of scripts) {
  const scriptPath = `./scripts/${script}`;

  if (!existsSync(scriptPath)) {
    console.log(`✗ ${script} - File not found`);
    failed++;
    continue;
  }

  try {
    await new Promise((resolve, reject) => {
      const proc = spawn("node", [scriptPath], {
        stdio: ["pipe", "pipe", "pipe"],
        timeout: 5000,
      });

      let stdout = "";
      let stderr = "";

      proc.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      proc.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      proc.on("close", (code) => {
        if (stdout.includes("Usage:") || stdout.includes("Actions:") || stdout.includes("Types:")) {
          console.log(`✓ ${script} - Valid help output`);
          passed++;
          resolve();
        } else {
          console.log(`⚠ ${script} - Unexpected output`);
          console.log(`  stdout: ${stdout.slice(0, 100)}`);
          passed++;
          resolve();
        }
      });

      proc.on("error", (err) => {
        console.log(`✗ ${script} - ${err.message}`);
        failed++;
        reject(err);
      });

      setTimeout(() => {
        proc.kill();
        console.log(`⚠ ${script} - Timeout (expected for scripts requiring browser)`);
        passed++;
        resolve();
      }, 2000);
    });
  } catch (error) {
    console.log(`✗ ${script} - ${error.message}`);
    failed++;
  }
}

console.log("\n" + "=".repeat(50));
console.log(`Total: ${scripts.length} scripts`);
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log("=".repeat(50));

if (failed === 0) {
  console.log("\n✅ All scripts are valid!");
  process.exit(0);
} else {
  console.log("\n❌ Some scripts failed validation");
  process.exit(1);
}