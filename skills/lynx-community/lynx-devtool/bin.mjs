#!/usr/bin/env node
// Copyright 2026 The Lynx Authors. All rights reserved.
// Licensed under the Apache License Version 2.0 that can be found in the
// LICENSE file in the root directory of this source tree.

import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const packageJson = JSON.parse(
  readFileSync(new URL('./package.json', import.meta.url), 'utf8'),
);
if (typeof packageJson.version !== 'string') {
  throw new TypeError(
    '@lynx-js/skill-lynx-devtool has no valid package version',
  );
}

const result = spawnSync(
  process.platform === 'win32' ? 'npx.cmd' : 'npx',
  ['-y', `agent-lynx@${packageJson.version}`, ...process.argv.slice(2)],
  { stdio: 'inherit' },
);

if (result.error) {
  throw result.error;
}
if (result.signal) {
  process.kill(process.pid, result.signal);
} else {
  process.exitCode = result.status ?? 1;
}
