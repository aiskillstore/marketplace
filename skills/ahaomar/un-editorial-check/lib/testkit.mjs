// Test-only harness for rule development. The CLI never imports this file.
//
// It runs the real extraction pipeline (extractFile) and the real rule engine
// (runEditorialRules) over text, with a caller-supplied rule registry and
// metadata merged over the shipped catalogue — so a rule under development is
// exercised through exactly the production code path: suppression, config
// enablement, severity resolution, dedupe and sort.
//
//   import { scanText } from '../lib/testkit.mjs';
//   const findings = scanText('Some copy.', {
//     extraRules: HS_RULES,   // { 'UE-HS001': ruleFn, ... }
//     extraMeta: HS_META,     // { 'UE-HS001': { category, confidence, severity } }
//     file: 'copy.txt',       // extension picks the extractor
//   });

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { extractFile } from './extract.mjs';
import { loadCatalogue, loadBaselineProfile, validateConfig, makeContext } from './config.mjs';
import { runEditorialRules } from './rules.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function scan(source, { extraRules = {}, extraMeta = {}, file = 'copy.txt', rawCfg = {} } = {}) {
  const { meta: baseMeta, ids } = loadCatalogue(ROOT);
  const extraIds = Object.keys(extraMeta);
  const knownIds = [...ids, ...extraIds.filter((id) => !ids.includes(id))];
  const meta = { ...baseMeta, ...extraMeta };
  const cfg = validateConfig(rawCfg, { knownIds });
  const baseline = loadBaselineProfile(ROOT, knownIds);
  const ctx = makeContext({ cfg, baseline, meta });
  const units = extractFile(file, source, { renderTargets: ctx.cfg.renderTargets });
  return runEditorialRules(units, ctx, extraRules);
}

/**
 * Extract `text` as `file` would be, run `extraRules` merged over the shipped
 * registry, and return the findings (sorted, deduped — same as production).
 * Production rules still run too, so callers can assert both directions:
 * "my rule fires here" and "nothing else fires on my fixtures".
 */
export function scanText(text, options = {}) {
  return scan(text, options);
}

/** Same, reading the file from disk. */
export function scanPath(filePath, options = {}) {
  return scan(fs.readFileSync(filePath, 'utf8'), { ...options, file: options.file ?? filePath });
}

/** Rule ids found, sorted and deduped — the shape expected.json asserts on. */
export function idsOf(findings) {
  return [...new Set(findings.map((f) => f.ruleId))].sort();
}
