import assert from 'node:assert/strict';
import { checkArchitecture, checkActivity } from '../src/contracts/parse.mjs';

export function architecture(text: string) {
  const value: unknown = JSON.parse(text);
  assert.ok(checkArchitecture(value), JSON.stringify(checkArchitecture.errors));
  return value;
}

export function activity(text: string) {
  return text.trim().split(/\r?\n/).map(line => {
    const value: unknown = JSON.parse(line);
    assert.ok(checkActivity(value), JSON.stringify(checkActivity.errors));
    return value;
  });
}

export function present<T>(value: T | null | undefined): T {
  assert.ok(value !== null && value !== undefined, 'Expected fixture value to exist');
  return value;
}
