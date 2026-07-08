#!/usr/bin/env node

import { spawn, execSync } from "node:child_process";
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { randomInt } from "node:crypto";
import { join } from "node:path";
import puppeteer from "puppeteer-core";

const useChrome = process.argv.includes("--chrome");
if (process.argv[2] && process.argv[2] !== "--chrome") {
  console.log("Usage: start.js [--chrome]");
  console.log("\nOptions:");
  console.log("  --chrome    Prefer Google Chrome");
  process.exit(1);
}

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");

execSync(`mkdir -p "${profileDir}"`, { stdio: "ignore" });

function cmdExists(cmd) {
  try {
    execSync(`command -v ${cmd}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function firstExisting(paths) {
  for (const p of paths) {
    if (p && existsSync(p)) return p;
  }
  return null;
}

function resolveBrowserPath() {
  const envPreferred = process.env.AGENT_BROWSER_EXECUTABLE_PATH || process.env.PUPPETEER_EXECUTABLE_PATH;
  if (envPreferred && existsSync(envPreferred)) return envPreferred;

  // Linux commands in PATH
  const linuxCmds = useChrome
    ? ["google-chrome-stable", "google-chrome", "chromium", "chromium-browser"]
    : ["chromium", "chromium-browser", "google-chrome-stable", "google-chrome"];

  for (const cmd of linuxCmds) {
    if (cmdExists(cmd)) {
      try {
        return execSync(`command -v ${cmd}`, { encoding: "utf-8" }).trim();
      } catch {
        // continue
      }
    }
  }

  // Known absolute paths (Linux/macOS + local workspace)
  const candidates = useChrome
    ? [
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/opt/google/chrome/chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/root/.cache/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-linux64/chrome-headless-shell",
        "/root/.pi/gateway/workspaces/default/chrome-headless-shell/linux-131.0.6778.204/chrome-headless-shell-linux64/chrome-headless-shell",
      ]
    : [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/root/.cache/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-linux64/chrome-headless-shell",
        "/root/.pi/gateway/workspaces/default/chrome-headless-shell/linux-131.0.6778.204/chrome-headless-shell-linux64/chrome-headless-shell",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/opt/google/chrome/chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
      ];

  return firstExisting(candidates);
}

let port;
if (existsSync(portFile)) {
  port = Number.parseInt(readFileSync(portFile, "utf-8").trim(), 10);
  console.log(`📖 Using saved port: ${port}`);
} else {
  port = randomInt(9222, 10000);
  writeFileSync(portFile, String(port));
  console.log(`🎲 Generated random port: ${port}`);
}

const browserPath = resolveBrowserPath();
if (!browserPath) {
  console.error("❌ No browser executable found!");
  console.error("   Set AGENT_BROWSER_EXECUTABLE_PATH or install chromium/google-chrome.");
  process.exit(1);
}

const browserName = browserPath.includes("chrome") ? "Chrome/Chromium" : "Browser";

// Browser already running?
try {
  const browser = await puppeteer.connect({
    browserURL: `http://localhost:${port}`,
    defaultViewport: null,
    timeout: 2000,
  });
  await browser.disconnect();
  console.log(`✓ ${browserName} already running on :${port}`);
  process.exit(0);
} catch {
  // not running
}

const browserArgs = [
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profileDir}`,
  "--profile-directory=Default",
  "--no-first-run",
  "--no-default-browser-check",
  "--disable-background-networking",
  "--disable-background-timer-throttling",
  "--disable-backgrounding-occluded-windows",
  "--disable-renderer-backgrounding",
  "--disable-features=TranslateUI,BlinkGenPropertyTrees",
  "--disable-web-security",
  "--disable-features=VizDisplayCompositor",
  "--proxy-server=direct://",
  "--no-proxy-server",
];

if (typeof process.getuid === "function" && process.getuid() === 0) {
  browserArgs.push("--no-sandbox", "--disable-setuid-sandbox");
}

console.log(`🚀 Starting: ${browserPath}`);
console.log(`📂 Profile: ${profileDir}`);
console.log(`🔌 Port: ${port}`);

const browserProcess = spawn(browserPath, browserArgs, {
  detached: true,
  stdio: "ignore",
});
browserProcess.unref();

console.log(`🎯 Process ID: ${browserProcess.pid}`);

let connected = false;
for (let i = 0; i < 40; i++) {
  try {
    const browser = await puppeteer.connect({
      browserURL: `http://localhost:${port}`,
      defaultViewport: null,
      timeout: 1500,
    });
    await browser.disconnect();
    connected = true;
    break;
  } catch {
    await new Promise((r) => setTimeout(r, 500));
  }
}

if (!connected) {
  console.error(`✗ Failed to connect to browser on :${port}`);
  process.exit(1);
}

console.log(`✓ Browser started on :${port}`);
