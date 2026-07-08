#!/usr/bin/env bun
/**
 * Complete TUI Demo
 * This script demonstrates all TUI features with example sessions
 */

import { TmuxManager } from './lib.ts';

async function main() {
  const tmux = new TmuxManager();

  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║     Tmux TUI - Interactive Session Management Demo          ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  console.log('Creating example sessions...\n');

  // Create different types of sessions
  const sessions = [
    {
      name: 'dev-server',
      command: 'echo "Development server running on http://localhost:3000" && sleep 60',
      category: 'service',
    },
    {
      name: 'build-process',
      command: 'echo "Building project..." && sleep 30 && echo "Build complete!"',
      category: 'task',
    },
    {
      name: 'test-runner',
      command: 'echo "Running tests..." && sleep 45 && echo "All tests passed!"',
      category: 'task',
    },
  ];

  for (const session of sessions) {
    const created = await tmux.createSession(session.name, session.command, session.category as any);
    console.log(`✅ Created ${session.category}: ${created.id}`);
  }

  console.log('\n─────────────────────────────────────────────────────────────\n');
  console.log('Now launching TUI with the following features:\n');
  console.log('📋 Session List');
  console.log('   - View all sessions with color-coded status');
  console.log('   - Auto-refresh every 5 seconds\n');
  console.log('⌨️ Keyboard Shortcuts');
  console.log('   [↑/↓] Navigate through sessions');
  console.log('   [r]   Refresh session list');
  console.log('   [n]   Create new session');
  console.log('   [c]   Capture output from selected session');
  console.log('   [s]   Show detailed session status');
  console.log('   [a]   Show attach command');
  console.log('   [k]   Kill session (with confirmation)');
  console.log('   [q]   Exit TUI\n');
  console.log('🎨 Color Coding');
  console.log('   Status: 🟢 running | 🟡 idle | 🔴 exited');
  console.log('   Category: 🔵 task | 🟣 service | 🟦 agent\n');
  console.log('─────────────────────────────────────────────────────────────\n');
  console.log('Starting TUI...\n');

  // Wait a moment for sessions to start
  await new Promise(resolve => setTimeout(resolve, 500));

  // Display current sessions
  const list = await tmux.listSessions();
  console.log('Current Sessions:');
  console.log('─────────────────────────────────────────────────────────────');
  for (const session of list) {
    const statusEmoji = session.status === 'running' ? '🟢' : session.status === 'idle' ? '🟡' : '🔴';
    console.log(`${statusEmoji} ${session.id}`);
    console.log(`   Command: ${session.command}`);
    console.log(`   Status: ${session.status}\n`);
  }

  console.log('To launch the interactive TUI, run:\n');
  console.log('  bun tui.ts\n');
  console.log('─────────────────────────────────────────────────────────────\n');
  console.log('💡 Tips:');
  console.log('   - Press [c] to see output from each session');
  console.log('   - Press [s] to check session status');
  console.log('   - Press [a] to get the attach command for interactive access');
  console.log('   - Press [k] to clean up sessions when done\n');
  console.log('Press Ctrl+C to exit this demo.\n');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});