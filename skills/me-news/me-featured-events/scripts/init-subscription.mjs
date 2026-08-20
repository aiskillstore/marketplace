#!/usr/bin/env node
import { csv, DEFAULT_STATE, ensureNodeVersion, filterParams, formatUpcoming, loadStateIfExists, parseArgs, request, saveState, timezoneArg } from './lib.mjs';

function sameValues(left, right) {
  return JSON.stringify([...left].sort()) === JSON.stringify([...right].sort());
}

try {
  ensureNodeVersion();
  const args = parseArgs(process.argv.slice(2), ['state', 'types', 'regions', 'timezone']);
  const statePath = args.state || process.env.ME_FEATURED_EVENTS_STATE || DEFAULT_STATE;
  const existing = await loadStateIfExists(statePath);
  const pending = existing?.initialization_status === 'pending' ? existing : null;
  const typeIds = pending && args.types === undefined ? pending.type_ids || [] : csv(args.types);
  const regionIds = pending && args.regions === undefined ? pending.region_ids || [] : csv(args.regions);
  const timezone = timezoneArg(args.timezone) || pending?.timezone || 'Asia/Shanghai';

  if (pending && !sameValues(typeIds, pending.type_ids || [])) {
    throw new Error('Cannot change --types while resuming initialization');
  }
  if (pending && !sameValues(regionIds, pending.region_ids || [])) {
    throw new Error('Cannot change --regions while resuming initialization');
  }
  if (pending && timezone !== pending.timezone) {
    throw new Error('Cannot change --timezone while resuming initialization');
  }

  const options = await request('options');
  const allowedTypes = new Set(options.types.map((item) => item.value));
  const allowedRegions = new Set(options.regions.map((item) => item.value));
  for (const value of typeIds) if (!allowedTypes.has(value)) throw new Error(`Unsupported type: ${value}`);
  for (const value of regionIds) if (!allowedRegions.has(value)) throw new Error(`Unsupported region: ${value}`);

  let state = pending;
  if (!state) {
    const baseline = await request('changes', { limit: 100 });
    if (!baseline.next_cursor) throw new Error('Missing next_cursor in changes response');
    state = {
      version: 2,
      type_ids: typeIds,
      region_ids: regionIds,
      cursor: baseline.next_cursor,
      recent_ids: [],
      timezone,
      initialization_status: 'pending',
      initialization_started_at: new Date().toISOString(),
    };
    // Persist the baseline before any later request can fail.
    await saveState(statePath, state);
  }

  const upcoming = await request('upcoming', { ...filterParams(state), limit: 20 });
  const output = formatUpcoming(upcoming.items || []);
  state.initialization_status = 'complete';
  state.initialized_at = new Date().toISOString();
  await saveState(statePath, state);
  if (output) process.stdout.write(`${output}\n`);
} catch (error) {
  process.stderr.write(`me-featured-events init failed: ${error.message}\n`);
  process.exitCode = 1;
}
