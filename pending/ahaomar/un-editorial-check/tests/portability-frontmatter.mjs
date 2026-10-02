import assert from 'node:assert/strict';
import fs from 'node:fs';
import { validatePortableFrontmatter } from '../scripts/validate-portability.mjs';

const valid = `---
name: un-editorial-check
description: Checks editorial content.
license: MIT
compatibility: Requires Node.js 18 or later.
metadata:
  version: "1.0.0"
---
Body`;

const cases = [
  ['missing opening frontmatter', 'name: x'],
  ['missing closing frontmatter', '---\nname: x'],
  ['unknown field', valid.replace('license: MIT', 'unknown: value')],
  ['duplicate top-level key', valid.replace('license: MIT', 'license: MIT\nlicense: Apache-2.0')],
  ['empty field', valid.replace('license: MIT', 'license:')],
  ['unquoted unsafe scalar', valid.replace('license: MIT', 'license: [MIT]')],
  ['unquoted scalar with comment text', valid.replace('description: Checks editorial content.', 'description: hello # ignored')],
  ['unquoted scalar with trailing hash', valid.replace('description: Checks editorial content.', 'description: hello #')],
  ['unquoted scalar with colon construct', valid.replace('description: Checks editorial content.', 'description: hello: world')],
  ['unquoted scalar with colon without whitespace', valid.replace('description: Checks editorial content.', 'description: hello:world')],
  ['unquoted scalar with trailing colon', valid.replace('description: Checks editorial content.', 'description: hello:')],
  ['unquoted scalar with leading dash indicator', valid.replace('description: Checks editorial content.', 'description: - hello')],
  ['unquoted scalar with leading question-mark indicator', valid.replace('description: Checks editorial content.', 'description: ? hello')],
  ['unquoted scalar with leading comma flow indicator', valid.replace('description: Checks editorial content.', 'description: , hello')],
  ['malformed quoted scalar', valid.replace('description: Checks editorial content.', 'description: "unterminated')],
  ['tabs', valid.replace('license: MIT', 'license:\tMIT')],
  ['control character', valid.replace('license: MIT', 'license: M\u0001IT')],
  ['name too long', valid.replace('un-editorial-check', 'a'.repeat(65))],
  ['name uppercase', valid.replace('un-editorial-check', 'Un-editorial-check')],
  ['consecutive name hyphens', valid.replace('un-editorial-check', 'un--editorial')],
  ['empty description', valid.replace('description: Checks editorial content.', 'description: ""')],
  ['description too long', valid.replace('description: Checks editorial content.', `description: "${'x'.repeat(1025)}"`)],
  ['compatibility too long', valid.replace('compatibility: Requires Node.js 18 or later.', `compatibility: "${'x'.repeat(501)}"`)],
  ['metadata before another field', valid.replace('metadata:\n  version: "1.0.0"', 'metadata:\n  version: "1.0.0"\nlicense: MIT')],
  ['metadata duplicate key', valid.replace('  version: "1.0.0"', '  version: "1.0.0"\n  version: "2.0.0"')],
  ['metadata non-string', valid.replace('  version: "1.0.0"', '  version: 1.0')],
  ['nested metadata', valid.replace('  version: "1.0.0"', '  nested:\n    value: "x"')],
  ['metadata without value', valid.replace('  version: "1.0.0"', '  version:')],
  ['indented top-level field', valid.replace('license: MIT', '  license: MIT')],
  ['list value', valid.replace('license: MIT', 'license:\n  - MIT')]
];

assert.deepEqual(validatePortableFrontmatter(valid), [], 'valid restricted portable subset');
assert.deepEqual(
  validatePortableFrontmatter(valid.replace('description: Checks editorial content.', 'description: "hello: world # quoted"')),
  [],
  'quoted scalars may contain YAML-significant characters'
);
for (const [label, fixture] of cases) {
  const errors = validatePortableFrontmatter(fixture);
  assert(errors.length > 0, `${label} should fail`);
}

for (const file of ['README.md', 'COMPATIBILITY.md', 'MAINTAINING.md', '.github/workflows/ci.yml']) {
  assert(!fs.readFileSync(new URL(`../${file}`, import.meta.url), 'utf8').includes('skills check'), `${file} contains stale command reference`);
}

console.log('ok — restricted portable frontmatter validator and stale-command guard');
