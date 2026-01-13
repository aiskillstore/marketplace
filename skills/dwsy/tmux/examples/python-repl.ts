#!/usr/bin/env bun
import { TmuxManager } from "../lib.js";

const tmux = new TmuxManager();

async function main() {
  console.log("Starting Python REPL...\n");

  const session = await tmux.createSession("python", "PYTHON_BASIC_REPL=1 python3 -q", "task");

  console.log(`\n✅ Session created: ${session.id}`);
  console.log(`\nTo monitor this session:`);
  console.log(`  tmux -S ${session.socket} attach -t ${session.id}`);

  console.log("\nWaiting for Python prompt...");
  const ready = await tmux.waitForText(session.target, ">>>", { timeout: 10 });

  if (ready) {
    console.log("✅ Python REPL is ready!");

    const code = "print('Hello from tmux!')\n2 + 2";
    await tmux.sendKeys(session.target, code);
    await tmux.sendKeys(session.target, "Enter");

    await new Promise(r => setTimeout(r, 1000));

    const output = await tmux.capturePane(session.target, 100);
    console.log("\nOutput:");
    console.log(output);

    await tmux.killSession(session.id);
    console.log("\n✅ Session closed");
  }
}

main().catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});