#!/usr/bin/env node
import { DEFAULT_STATE, ensureNodeVersion, loadState, parseArgs, saveState } from './lib.mjs';

try {
  ensureNodeVersion();
  const args = parseArgs(process.argv.slice(2), ['state', 'status', 'error']);
  const statePath = args.state || process.env.ME_FEATURED_EVENTS_STATE || DEFAULT_STATE;
  const status = args.status;
  if (!['success', 'failed'].includes(status)) throw new Error('--status must be success or failed');

  const state = await loadState(statePath);
  const pending = state.pending_delivery;
  if (!pending) throw new Error('No pending delivery to record');
  state.version = 2;

  if (status === 'success') {
    if (!pending.next_cursor) throw new Error('Pending delivery has no next_cursor');
    state.cursor = pending.next_cursor;
    state.recent_ids = pending.recent_ids || state.recent_ids || [];
    state.last_delivery_status = 'success';
    state.last_delivered_at = new Date().toISOString();
    delete state.pending_delivery;
  } else {
    pending.failure_count = (pending.failure_count || 0) + 1;
    pending.last_failure_at = new Date().toISOString();
    if (args.error) pending.last_error = String(args.error).slice(0, 500);
    state.last_delivery_status = 'failed';
  }

  await saveState(statePath, state);
} catch (error) {
  process.stderr.write(`me-featured-events delivery feedback failed: ${error.message}\n`);
  process.exitCode = 1;
}
