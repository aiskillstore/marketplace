#!/usr/bin/env bun
import { TmuxManager } from "../lib.js";

const tmux = new TmuxManager();

async function main() {
  console.log("Starting development server...\n");

  const session = await tmux.createSession(
    "dev-server",
    "echo 'Starting HTTP server on port 8080...' && python3 -m http.server 8080",
    "service"
  );

  console.log(`\n✅ Session created: ${session.id}`);
  console.log(`\nTo monitor this session:`);
  console.log(`  tmux -S ${session.socket} attach -t ${session.id}`);
  console.log(`\nOr capture output:`);
  console.log(`  tmux -S ${session.socket} capture-pane -p -J -t ${session.target} -S -200`);

  console.log("\nWaiting for server to start...");
  const ready = await tmux.waitForText(session.target, "Serving HTTP", { timeout: 10 });

  if (ready) {
    console.log("\n✅ Server is ready!");

    const output = await tmux.capturePane(session.target, 100);
    console.log("\nServer output:");
    console.log(output);

    console.log("\n📝 Service is running in the background.");
    console.log("To stop it later, run:");
    console.log(`  bun ~/.pi/agent/skills/tmux/lib.ts kill ${session.id}`);
  }
}

main().catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});