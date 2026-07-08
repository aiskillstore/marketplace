#!/usr/bin/env node

import { execSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

console.log("🛑 Stopping web-browser...");

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");

function killByPort(port) {
  try {
    const pids = execSync(`lsof -ti tcp:${port}`, { encoding: "utf-8" })
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);

    if (pids.length === 0) return false;

    for (const pid of pids) {
      try {
        process.kill(Number(pid), "SIGTERM");
      } catch {
        // ignore
      }
    }
    return true;
  } catch {
    return false;
  }
}

let stopped = false;

if (existsSync(portFile)) {
  const port = Number.parseInt(readFileSync(portFile, "utf-8").trim(), 10);
  if (Number.isFinite(port)) {
    stopped = killByPort(port) || stopped;
  }
}

try {
  execSync("pkill -f 'scraping-web-browser'", { stdio: "ignore" });
  stopped = true;
} catch {
  // ignore
}

try {
  execSync("pkill -f 'chrome-headless-shell.*remote-debugging-port'", { stdio: "ignore" });
  stopped = true;
} catch {
  // ignore
}

try {
  execSync("pkill -f 'chromium.*remote-debugging-port'", { stdio: "ignore" });
  stopped = true;
} catch {
  // ignore
}

if (stopped) {
  console.log("✓ Browser stopped");
} else {
  console.log("✓ Browser was not running");
}

console.log("💡 Tip: Port info is preserved, next start will use the same port");
console.log("   To reset port, remove ~/.cache/scraping-web-browser/port.txt");
