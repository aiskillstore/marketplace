#!/usr/bin/env bun
import { TmuxManager } from "../lib.js";

const tmux = new TmuxManager();

async function main() {
  console.log("Starting long-running task...\n");

  const session = await tmux.createSession(
    "long-task",
    "for i in {1..10}; do echo 'Progress: $i/10'; sleep 1; done; echo 'Task completed!'",
    "task"
  );

  console.log(`\n✅ Session created: ${session.id}`);
  console.log(`\nTo monitor this session in real-time:`);
  console.log(`  tmux -S ${session.socket} attach -t ${session.id}`);
  console.log(`\nOr capture output:`);
  console.log(`  tmux -S ${session.socket} capture-pane -p -J -t ${session.target} -S -200`);

  console.log("\nWaiting for task completion...");
  const completed = await tmux.waitForText(session.target, "Task completed", { timeout: 20 });

  if (completed) {
    console.log("\n✅ Task completed!");

    const output = await tmux.capturePane(session.target, 200);
    console.log("\nFinal output:");
    console.log(output);

    await tmux.killSession(session.id);
    console.log("\n✅ Session closed");
  }
}

main().catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});