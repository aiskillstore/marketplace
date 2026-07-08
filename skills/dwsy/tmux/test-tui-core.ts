#!/usr/bin/env bun
/**
 * Non-interactive test for TUI core functionality
 * This script tests the TUI components without launching the interactive interface
 */

import { TmuxManager } from './lib.ts';

async function testTUI() {
  const tmux = new TmuxManager();
  let passed = 0;
  let failed = 0;

  console.log('=== TUI Core Functionality Tests ===\n');

  // Test 1: Sync sessions
  console.log('Test 1: Sync sessions with tmux...');
  try {
    await tmux.syncWithTmux();
    console.log('✅ Sync successful');
    passed++;
  } catch (err) {
    console.log(`❌ Sync failed: ${err.message}`);
    failed++;
  }

  // Test 2: List sessions
  console.log('\nTest 2: List sessions...');
  try {
    const sessions = await tmux.listSessions();
    console.log(`✅ Found ${sessions.length} session(s)`);
    if (sessions.length > 0) {
      console.log('   Sample session:', sessions[0].id);
    }
    passed++;
  } catch (err) {
    console.log(`❌ List failed: ${err.message}`);
    failed++;
  }

  // Test 3: Create session
  console.log('\nTest 3: Create test session...');
  try {
    const session = await tmux.createSession(
      'tui-test',
      'echo "TUI Test" && sleep 5',
      'task'
    );
    console.log(`✅ Created session: ${session.id}`);
    passed++;

    // Test 4: Capture output
    console.log('\nTest 4: Capture session output...');
    try {
      const output = await tmux.capturePane(session.target, 200);
      console.log(`✅ Captured ${output.length} characters`);
      passed++;
    } catch (err) {
      console.log(`❌ Capture failed: ${err.message}`);
      failed++;
    }

    // Test 5: Get status
    console.log('\nTest 5: Get session status...');
    try {
      const status = await tmux.getSessionStatus(session.target);
      console.log(`✅ Session status: ${status}`);
      passed++;
    } catch (err) {
      console.log(`❌ Status check failed: ${err.message}`);
      failed++;
    }

    // Cleanup
    console.log('\nTest 6: Cleanup test session...');
    try {
      await tmux.killSession(session.id);
      console.log(`✅ Killed session: ${session.id}`);
      passed++;
    } catch (err) {
      console.log(`❌ Kill failed: ${err.message}`);
      failed++;
    }
  } catch (err) {
    console.log(`❌ Create failed: ${err.message}`);
    failed++;
  }

  // Summary
  console.log('\n=== Test Summary ===');
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Total: ${passed + failed}`);

  if (failed === 0) {
    console.log('\n✅ All tests passed! TUI core functionality is working.');
    console.log('\nYou can now launch the interactive TUI:');
    console.log('  bun tui.ts');
  } else {
    console.log('\n❌ Some tests failed. Please check the errors above.');
    process.exit(1);
  }
}

testTUI().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});