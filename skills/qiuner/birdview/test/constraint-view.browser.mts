import { architecture } from './fixtures.mjs';
import type { ReviewedConstraintCatalog } from '../src/constraint-types.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { renderArchitecture } from '../src/render.mjs';
import { renderConstraintCatalog } from '../src/render-constraints.mjs';

const { chromium }: typeof import('playwright') = await import(process.env.BIRDVIEW_PLAYWRIGHT_PATH ? pathToFileURL(process.env.BIRDVIEW_PLAYWRIGHT_PATH).href : 'playwright');
const map = architecture(fs.readFileSync(new URL('../examples/system.architecture.json', import.meta.url), 'utf8'));
const revision = 'a'.repeat(40);
const catalog: ReviewedConstraintCatalog = {
  schema: 'birdview.constraint-catalog/v1',
  project: { name: map.project.name, revision },
  coverage: { checkedAt: '2026-09-20', snapshot: revision, shallow: false, entries: ['AGENTS.md'], checkedPaths: ['AGENTS.md'], excluded: [], unresolved: [], uninspectedPaths: [], semanticReview: 'complete', limitations: [] },
  references: [],
  ruleReview: { scope: 'Browser test fixture only', sourcePaths: ['AGENTS.md'], reviewedAt: '2026-09-20', implementationVerification: 'unverified' },
  architectureBinding: { mapId: map.mapId, mapRevision: map.revision, sourceRevision: revision },
  sources: [{ id: 'root-agents', kind: 'instruction', path: 'AGENTS.md', scope: '.', discoveredFrom: null, applicability: 'reviewed', text: 'Check work.', sections: [], history: { complete: true, version: 1, lastEdited: '2026-09-20', commit: revision } }],
  rules: [0, 1].map(index => ({ id: `check-${index}`, name: `检查${index}`, category: 'testing', sourcePath: 'AGENTS.md', line: 1, endLine: 1, condition: '修改时', explanation: '执行检查', verification: '检查输出', applicability: 'conditional' as const, modules: index === 0 ? [map.modules[0]!.id] : [] })),
};
const output = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-integrated-'));
const file = path.join(output, 'index.html');
fs.writeFileSync(file, renderArchitecture(map, [], { constraintCatalog: catalog }));
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(file).href + '#lang=zh');
  if (await page.locator('#guide-dismiss').isVisible()) await page.locator('#guide-dismiss').click();
  const tabs = page.locator('#project-views button');
  await tabs.nth(1).click();
  const graph = page.locator('#constraint-view');
  await graph.locator('.cv-card').first().waitFor();
  const cardSize = await graph.locator('.cv-card').first().boundingBox();
  assert.ok(cardSize && cardSize.width > 150 && cardSize.height >= 75 && cardSize.height <= 77);
  await graph.locator('.cv-card[data-id="category-testing"]').click();
  await graph.locator('.cv-card[data-id="check-0"]').click();
  assert.equal(await graph.locator('.cv-card[data-id="project"]').evaluate(node => node.classList.contains('cv-muted-branch')), true);
  assert.equal(await graph.locator('.cv-card[data-id="category-testing"]').evaluate(node => node.classList.contains('cv-muted-branch')), false);
  assert.equal(await graph.locator('.cv-edge.cv-relevant').count(), 1);
  await graph.locator('.cv-reader-close').click();
  await graph.locator('.cv-grouping').selectOption('directories');
  await graph.locator('.cv-search').fill('检查1');
  await graph.locator('.cv-tree-row[data-id="check-1"]').click();
  assert.match(await graph.locator('.cv-reader-body').textContent() || '', /Check work/);
  await graph.locator('.cv-card[data-id="check-1"]').press('Shift+Enter');
  assert.equal(await graph.locator('.cv-dialog').isVisible(), true);
  await page.keyboard.press('Escape');
  assert.equal(await graph.locator('.cv-dialog').isVisible(), false);
  await graph.locator('.cv-grouping').selectOption('topics');
  await page.setViewportSize({ width: 390, height: 844 });
  if (await graph.locator('.cv-directory').isVisible()) await graph.locator('.cv-directory-heading button').click();
  await graph.locator('.cv-fit').click();
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  assert.ok((await graph.locator('.cv-viewport').boundingBox())!.height > 350);

  const branches = structuredClone(catalog);
  branches.rules.push({ ...catalog.rules[0]!, id: 'secure-check', category: 'security' });
  const branchFile = path.join(output, 'branches.html');
  fs.writeFileSync(branchFile, renderConstraintCatalog(branches));
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(pathToFileURL(branchFile).href);
  const testing = page.locator('.cv-card[data-id="category-testing"]');
  const position = await testing.boundingBox();
  await testing.click();
  assert.deepEqual(await testing.boundingBox(), position);
  await page.locator('.cv-card[data-id="category-security"]').click();
  assert.equal(await page.locator('.cv-card[data-id="check-0"]').count(), 0);
  assert.equal(await page.locator('.cv-card[data-id="secure-check"]').count(), 1);
  assert.deepEqual(await testing.boundingBox(), position);
  await testing.dblclick();
  assert.equal(await page.locator('.cv-dialog').isVisible(), true);
  await page.locator('.cv-dialog-close').click();
  assert.deepEqual(errors, []);
  console.log(`Constraint view checks passed. ${output}`);
} finally {
  await browser.close();
}
