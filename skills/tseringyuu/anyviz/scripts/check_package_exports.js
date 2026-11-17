'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const anyviz = require('..');
const packageJson = require('../package.json');

assert.ok(anyviz.guides, 'anyviz.guides should be exposed');

const expectedGuides = {
  chartSelection: 'guides/chart-selection.md',
  colorGuide: 'guides/color-guide.md',
  academicPublication: 'guides/academic-publication.md',
  consistencyRules: 'guides/consistency-rules.md',
  customizationGuide: 'guides/customization-guide.md',
  legendLayout: 'guides/legend-layout.md',
  accessibility: 'guides/accessibility.md',
};

for (const [key, relativePath] of Object.entries(expectedGuides)) {
  const expectedPath = path.join(anyviz.root, relativePath);
  const exportKey = `./${relativePath}`;
  assert.strictEqual(anyviz.guides[key], expectedPath, `${key} should resolve to ${relativePath}`);
  assert.ok(fs.existsSync(anyviz.guides[key]), `${key} guide should exist on disk`);
  assert.strictEqual(packageJson.exports[exportKey], exportKey, `${exportKey} should be exposed in package.json exports`);
}

console.log('anyviz package exports verified');
