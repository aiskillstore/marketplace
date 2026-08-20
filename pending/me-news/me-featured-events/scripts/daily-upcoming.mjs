#!/usr/bin/env node
import { dateArg, DEFAULT_STATE, ensureNodeVersion, filterParams, formatUpcoming, integerArg, loadState, parseArgs, request } from './lib.mjs';

try {
  ensureNodeVersion();
  const args = parseArgs(process.argv.slice(2), ['state', 'hours', 'limit', 'start-date', 'end-date']);
  const hours = integerArg(args.hours, '--hours', 1, 8784);
  const limit = integerArg(args.limit, '--limit', 1, 100) ?? 20;
  const startDate = dateArg(args['start-date'], '--start-date');
  const endDate = dateArg(args['end-date'], '--end-date');
  const statePath = args.state || process.env.ME_FEATURED_EVENTS_STATE || DEFAULT_STATE;
  const hasDateRange = Boolean(startDate || endDate);
  if (hasDateRange && !(startDate && endDate)) {
    throw new Error('--start-date and --end-date must be provided together');
  }
  if (hasDateRange && hours !== undefined) throw new Error('--hours cannot be combined with a date range');
  if (hasDateRange && endDate < startDate) throw new Error('--end-date must not be earlier than --start-date');
  if (hasDateRange) {
    const days = (Date.parse(`${endDate}T00:00:00Z`) - Date.parse(`${startDate}T00:00:00Z`)) / 86_400_000 + 1;
    if (days > 366) throw new Error('date range must not exceed 366 days');
  }
  const state = await loadState(statePath);
  const upcoming = await request('upcoming', {
    ...filterParams(state),
    hours: hasDateRange ? undefined : hours,
    start_date: startDate,
    end_date: endDate,
    limit,
  });
  const output = formatUpcoming(upcoming.items || []);
  if (output) process.stdout.write(`${output}\n`);
} catch (error) {
  process.stderr.write(`me-featured-events daily check failed: ${error.message}\n`);
  process.exitCode = 1;
}
