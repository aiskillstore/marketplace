// Command contract tests — plain node:assert, run with: node tests/command-contract.mjs
//
// Covers the contract in .feedbacks/PHASE4-CONTRACT.md §4: the canonical command
// source exists and names itself, every pinned string of §2 is embedded byte for
// byte, and the flow keeps its order — the never-modify law first, then the scan
// invocation, then the approval question, then the apply flag.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const commandFile = path.join(root, 'commands', 'un-diplomatic-agent.md');

// --- the command source exists, names itself and is not empty ---------------

assert(fs.existsSync(commandFile), 'commands/un-diplomatic-agent.md must exist');
const source = fs.readFileSync(commandFile, 'utf8');
assert(source.trim().length > 0, 'the command source must not be empty');

const firstHeading = source.split('\n').find(line => line.startsWith('#'));
assert(firstHeading, 'the command source must open with a heading');
assert(firstHeading.includes('un-diplomatic-agent'),
  'the first heading must mention un-diplomatic-agent');

// --- pinned strings, copied verbatim from §2 of the contract ----------------

const P1 = 'Never modify a file before the user has explicitly approved the corrections.';
const P2 = 'npx un-editorial-check <paths> --report un-editorial-review.pdf';
const P3 = 'Apply these corrections?';
const P4 = '--fix --apply';
const P5 = 'If `proposed` is null, do not improvise — ask the user what should be written instead.';
const P6 = 'Never claim the copy is clean unless the exit code is 0.';

for (const [name, pinned] of [['P1', P1], ['P2', P2], ['P3', P3], ['P4', P4], ['P5', P5], ['P6', P6]]) {
  assert(source.includes(pinned), `${name} must appear verbatim in the command source`);
}

// --- ordering by first appearance: law, scan, gate, apply -------------------

const idx = pinned => source.indexOf(pinned);
assert(idx(P1) >= 0 && idx(P2) >= 0 && idx(P3) >= 0 && idx(P4) >= 0,
  'the ordered pins must all be present before their order is checked');
assert(idx(P1) < idx(P2), 'P1 must appear before the scan invocation P2');
assert(idx(P2) < idx(P3), 'the scan P2 must appear before the approval question P3');
assert(idx(P3) < idx(P4), 'the approval question P3 must appear before the apply flag P4');

console.log('ok — command contract: file, heading, pinned P1–P6, order P1 < P2 < P3 < P4');
