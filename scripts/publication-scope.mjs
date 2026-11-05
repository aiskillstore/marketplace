import { readFileSync } from 'node:fs';

// One repository-owned scope for the planner and both publication receivers.
// This excludes cancelled work; it does not bypass dependency/effect checks.
const scope = JSON.parse(readFileSync(new URL('./publication-scope.json', import.meta.url), 'utf8'));
function timestamp(value, label) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value)
    || !Number.isFinite(Date.parse(value))) throw new Error(`Invalid ${label}`);
  const ms = Date.parse(value);
  if (new Date(ms).toISOString() !== (value.includes('.') ? value : value.replace('Z', '.000Z'))) {
    throw new Error(`Invalid ${label}`);
  }
  return ms;
}
const createdAfter = timestamp(scope.createdAfter, 'publication scope');
export function publicationInScope(pr) {
  return timestamp(pr.created_at, 'PR creation timestamp') > createdAfter;
}
export function assertPublicationInScope(pr) {
  if (!publicationInScope(pr)) throw new Error('PR is outside the approved publication scope');
}
