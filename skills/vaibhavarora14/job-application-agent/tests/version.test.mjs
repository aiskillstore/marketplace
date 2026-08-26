import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import { SKILL_VERSION as telemetryVersion } from '../scripts/telemetry-client.mjs';
import { SKILL_VERSION } from '../scripts/version.mjs';

test('the packaged skill and telemetry report the npm package version', async () => {
  const manifest = JSON.parse(await readFile(new URL('../../package.json', import.meta.url), 'utf8'));
  assert.equal(SKILL_VERSION, manifest.version);
  assert.equal(telemetryVersion, manifest.version);
});
