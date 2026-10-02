#!/usr/bin/env node
// un-editorial-check entry point. All behaviour lives in lib/; this file only
// wires argv to the CLI and re-exports the surface tests rely on.
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import process from 'node:process';

import { run, VERSION, HELP, SKILL_ROOT } from '../lib/cli.mjs';
import { loadCatalogue } from '../lib/config.mjs';

export { run, VERSION, HELP };

/** rules/catalogue.json — the single source of rule metadata. */
export const CATALOGUE = loadCatalogue(SKILL_ROOT).catalogue;

function invokedDirectly() {
  const argv1 = process.argv[1];
  if (!argv1) return false;
  try {
    return pathToFileURL(fs.realpathSync(argv1)).href === import.meta.url;
  } catch {
    return false;
  }
}

if (invokedDirectly()) {
  const result = run(process.argv.slice(2));
  // --url runs asynchronously: the promise resolves to the same exit code.
  if (result && typeof result.then === 'function') {
    result.then((code) => { process.exitCode = code ?? 0; });
  } else {
    process.exitCode = result;
  }
}
