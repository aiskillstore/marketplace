#!/usr/bin/env node
import { DEFAULT_STATE, ensureNodeVersion, filterParams, formatChanges, integerArg, loadState, parseArgs, request, saveState } from './lib.mjs';

try {
  ensureNodeVersion();
  const args = parseArgs(process.argv.slice(2), ['state', 'limit']);
  const limit = integerArg(args.limit, '--limit', 1, 100) ?? 100;
  const statePath = args.state || process.env.ME_FEATURED_EVENTS_STATE || DEFAULT_STATE;
  const state = await loadState(statePath);
  if (!state.cursor) throw new Error('Missing cursor in state');
  state.version = 2;

  let output = '';
  if (state.pending_delivery) {
    state.pending_delivery.attempt_count = (state.pending_delivery.attempt_count || 0) + 1;
    state.pending_delivery.last_attempt_at = new Date().toISOString();
    output = state.pending_delivery.message;
    await saveState(statePath, state);
  } else {
    const seen = new Set(state.recent_ids || []);
    const fresh = [];
    let cursor = state.cursor;
    let pages = 0;
    do {
      const data = await request('changes', { ...filterParams(state), cursor, limit });
      for (const event of data.items || []) {
        if (!seen.has(event.id)) {
          fresh.push(event);
          seen.add(event.id);
        }
      }
      if (!data.next_cursor) throw new Error('Missing next_cursor in changes response');
      cursor = data.next_cursor;
      pages += 1;
      if (!data.has_more) break;
      if (pages >= 100) throw new Error('Stopped after 100 pages without reaching the end');
    } while (true);

    output = formatChanges(fresh);
    const recentIds = [...seen].slice(-500);
    state.last_checked_at = new Date().toISOString();
    if (output) {
      state.pending_delivery = {
        message: output,
        next_cursor: cursor,
        recent_ids: recentIds,
        prepared_at: new Date().toISOString(),
        attempt_count: 1,
      };
    } else {
      // No user-visible message needs acknowledgement.
      state.cursor = cursor;
      state.recent_ids = recentIds;
    }
    await saveState(statePath, state);
  }
  if (output) process.stdout.write(`${output}\n`);
} catch (error) {
  process.stderr.write(`me-featured-events poll failed: ${error.message}\n`);
  process.exitCode = 1;
}
