#!/usr/bin/env bun
/**
 * Example: Using TUI to manage development workflow
 * This script demonstrates a typical development workflow using the TUI
 */

import { TmuxManager } from './lib.ts';

async function main() {
  const tmux = new TmuxManager();

  console.log('=== Development Workflow Example ===\n');

  // Step 1: Start development server
  console.log('Step 1: Starting development server...');
  const devServer = await tmux.createSession(
    'dev-server',
    'npm run dev',
    'service'
  );
  console.log(`✅ Started: ${devServer.id}`);

  // Step 2: Start build watcher
  console.log('\nStep 2: Starting build watcher...');
  const buildWatcher = await tmux.createSession(
    'build-watch',
    'npm run build:watch',
    'task'
  );
  console.log(`✅ Started: ${buildWatcher.id}`);

  // Step 3: Start test runner
  console.log('\nStep 3: Starting test runner...');
  const testRunner = await tmux.createSession(
    'test-runner',
    'npm run test:watch',
    'task'
  );
  console.log(`✅ Started: ${testRunner.id}`);

  console.log('\n=== All services started ===\n');
  console.log('Now launch TUI to manage these sessions:');
  console.log('  bun tui.ts\n');
  console.log('What you can do in TUI:');
  console.log('  - Press [c] to capture output from any session');
  console.log('  - Press [s] to check session status');
  console.log('  - Press [a] to get attach command for interactive access');
  console.log('  - Press [r] to refresh session status');
  console.log('  - Press [k] to stop a session when done');
  console.log('  - Press [q] to exit TUI\n');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});