#!/usr/bin/env bun
/**
 * Test script for tmux TUI
 * Creates a few test sessions and then launches the TUI
 */

import { TmuxManager } from './lib.ts';

async function main() {
  const tmux = new TmuxManager();

  console.log('Creating test sessions...');

  // Create test sessions
  await tmux.createSession('test-echo', 'echo "Hello from tmux" && sleep 30', 'task');
  console.log('✅ Created test-echo session');

  await tmux.createSession('test-sleep', 'echo "Sleeping for 60 seconds..." && sleep 60', 'task');
  console.log('✅ Created test-sleep session');

  await tmux.createSession('test-server', 'echo "Server running..." && sleep 120', 'service');
  console.log('✅ Created test-server session');

  console.log('\nTest sessions created successfully!');
  console.log('Now launching TUI...\n');

  // Wait a moment for sessions to start
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Launch TUI
  console.log('To launch TUI, run:');
  console.log('  bun tui.ts');
  console.log('\n按 [q] 或 [Esc] 退出 TUI/Press [q] or [Esc] to exit the TUI');
  console.log('按 [k] 终止会话（需确认）/Press [k] to kill a session (requires confirmation)');
  console.log('按 [r] 刷新会话列表/Press [r] to refresh the session list');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});