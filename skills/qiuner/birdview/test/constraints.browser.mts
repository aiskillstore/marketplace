import { architecture, activity, present } from './fixtures.mjs';
import type { Architecture, ActivityEvent } from '../src/contracts/models.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { renderArchitecture, type RenderOptions } from '../src/render.mjs';

const { chromium }: typeof import('playwright') = await import(process.env.BIRDVIEW_PLAYWRIGHT_PATH ? pathToFileURL(process.env.BIRDVIEW_PLAYWRIGHT_PATH).href : 'playwright');
const map = architecture(fs.readFileSync(new URL('../examples/system.architecture.json', import.meta.url), 'utf8'));
const events = activity(fs.readFileSync(new URL('../examples/harness.activity.jsonl', import.meta.url), 'utf8'));
const output = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-constraints-'));
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const load = async (data: Architecture, records: ActivityEvent[], options: RenderOptions = {}) => {
    await page.goto('about:blank');
    const file = path.join(output, 'constraints.html');
    fs.writeFileSync(file, renderArchitecture(data, records, { simulation: true, ...options }));
    await page.goto(pathToFileURL(file).href + '#lang=zh');
    await page.locator('#show-constraints').waitFor();
    if (await page.locator('#guide-dismiss').isVisible()) await page.locator('#guide-dismiss').click();
  };
  const unscanned = structuredClone(map);
  delete unscanned.constraints;
  delete unscanned.constraintDiscovery;
  await load(unscanned, []);
  assert.match(await page.locator('#show-constraints').textContent() || '', /未扫描/);
  await page.locator('#show-constraints').click();
  assert.match(await page.locator('.constraint-empty').textContent() || '', /不能判断/);
  await page.locator('#language').selectOption('en');
  assert.match(await page.locator('#show-constraints').textContent() || '', /Not scanned/);
  const scanned = { ...unscanned, constraintDiscovery: present(map.constraintDiscovery) };
  await load(scanned, []);
  assert.match(await page.locator('#show-constraints').textContent() || '', /待整理/);
  await page.locator('#show-constraints').click();
  assert.match(await page.locator('.constraint-empty').textContent() || '', /不代表没有约束/);
  await load(map, events);
  await page.locator('#show-constraints').click();
  assert.equal(await page.locator('.constraint-row').count(), 6);
  await page.locator('[data-constraint="cancel-propagation"]').click();
  assert.equal(await page.locator('#nodes .constraint-highlight').count(), 3);
  assert.match(present(await page.locator('.constraint-detail').textContent()), /模拟方案/);
  await page.locator('.constraint-source summary').click();
  assert.match(present(await page.locator('.constraint-source p').textContent()), /DeepSeek Harness @ 7a0b7682/);
  await page.screenshot({ path: path.join(output, 'desktop-zh-dark.png') });
  await page.locator('#activity-next').click();
  assert.doesNotMatch(present(await page.locator('.constraint-detail').textContent()), /模拟方案/);
  assert.match(present(await page.locator('.constraint-detail').textContent()), /未验证/);
  await page.locator('[data-view="compare"]').click();
  assert.equal(await page.locator('#overview-nodes .constraint-highlight').count(), 3);
  await page.locator('[data-view="architecture"]').click();
  assert.doesNotMatch(present(await page.locator('.constraint-detail').textContent()), /本次方案|验证结果/);
  await page.locator('#constraint-filter').selectOption('attention');
  assert.equal(await page.locator('.constraint-row').count(), 0);
  assert.match(present(await page.locator('.constraint-empty').textContent()), /未记录约束/);
  await page.locator('#constraint-filter').selectOption('module');
  await page.locator('#map [data-module="tools"]').click();
  assert.equal(await page.locator('.constraint-row').count(), 5);
  await page.locator('#show-details').click();
  await page.locator('#module-constraints button').first().click();
  assert.equal(await page.locator('#constraints-panel').isVisible(), true);
  await page.locator('#language').selectOption('en');
  await page.locator('#theme').click();
  await page.screenshot({ path: path.join(output, 'desktop-en-light.png') });
  assert.match(present(await page.locator('#constraints-panel').textContent()), /Await child termination/);
  await page.locator('#guide-launch').click();
  await page.locator('#guide-skip').click();
  assert.equal(await page.locator('#constraints-panel').isVisible(), true);
  assert.equal(await page.locator('#nodes .constraint-highlight').count(), 3);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#show-constraints').getAttribute('aria-expanded'), 'false');
  assert.equal(await page.locator('#nodes .constraint-highlight').count(), 0);
  await page.locator('#show-constraints').click();
  await page.locator('#constraint-filter').selectOption('applicable');
  for (const width of [390, 768]) {
    await page.setViewportSize({ width, height: 844 });
    for (const lang of ['zh', 'en']) {
      await page.locator('#language').selectOption(lang);
      const bounds = present(await page.locator('aside').boundingBox());
      assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= width + 1);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      assert.equal(await page.locator('#constraints-panel').evaluate(el => el.scrollWidth <= el.clientWidth + 1), true);
      await page.screenshot({ path: path.join(output, `${width}-${lang}.png`) });
    }
  }
  const relationshipMap = structuredClone(map);
  Object.assign(present(present(relationshipMap.constraints)[0]), { scope: 'relationships', modules: [], relationships: [present(map.relationships.find(relation => relation.visibility === 'detail')).id] });
  await page.setViewportSize({ width: 1440, height: 900 });
  await load(relationshipMap, []);
  await page.locator('#show-constraints').click();
  await page.locator('[data-constraint="cancel-propagation"]').click();
  assert.equal(await page.locator('#connections .constraint-highlight').count(), 1);
  assert.equal(await page.locator('#connections .constraint-highlight').isVisible(), true);
  const checkedEvents = structuredClone(events);
  present(checkedEvents[0]).checks = [{ command: 'node test.mjs', status: 'passed', exitCode: 0, summary: 'Fictional test coverage.' }];
  Object.assign(present(present(present(checkedEvents[0]).constraintReviews)[0]), { status: 'supported', evidence: 'Fictional cancellation check.', checkIndexes: [0] });
  await load(map, checkedEvents);
  await page.locator('#show-constraints').click();
  await page.locator('[data-constraint="cancel-propagation"]').click();
  assert.match(present(await page.locator('.constraint-detail').textContent()), /node test.mjs/);
  await page.locator('#activity-next').click();
  assert.doesNotMatch(present(await page.locator('.constraint-detail').textContent()), /node test.mjs/);
  assert.match(present(await page.locator('.constraint-detail').textContent()), /未验证/);
  const conflictMap = structuredClone(map);
  Object.assign(present(present(conflictMap.constraints)[3]), { origin: 'inferred', applicability: 'uncertain' });
  Object.assign(present(present(conflictMap.constraints)[0]), { applicability: 'conflict', conflictsWith: ['honest-verification'] });
  Object.assign(present(present(conflictMap.constraints)[1]), { applicability: 'conflict', conflictsWith: ['cancel-propagation'] });
  present(present(present(conflictMap.constraints)[0]).evidence[0]).note = '<img src=x onerror=alert(1)>';
  await load(conflictMap, []);
  await page.locator('#show-constraints').click();
  await page.locator('#constraint-filter').selectOption('attention');
  await page.locator('[data-constraint="cancel-propagation"]').click();
  await page.locator('.constraint-source summary').click();
  assert.equal(await page.locator('.constraint-source img').count(), 0);
  await page.locator('.constraint-detail .constraint-module-link').click();
  assert.equal(await page.locator('[data-constraint="honest-verification"]').getAttribute('aria-pressed'), 'true');
  const legacy = architecture(fs.readFileSync(new URL('../examples/architecture.json', import.meta.url), 'utf8'));
  await load(legacy, []);
  await page.locator('#show-constraints').click();
  assert.match(present(await page.locator('#constraints-panel').textContent()), /未记录本地约束检查/);
  const repository = path.join(output, 'repository');
  fs.mkdirSync(repository);
  const git = (...args: string[]): string => execFileSync('git', args, { cwd: repository, encoding: 'utf8', windowsHide: true }).trim();
  git('init', '-q');
  git('config', 'user.name', 'Birdview test');
  git('config', 'user.email', 'birdview@example.invalid');
  git('config', 'commit.gpgsign', 'false');
  git('config', 'core.hooksPath', path.join(repository, 'no-hooks'));
  fs.writeFileSync(path.join(repository, 'rules.md'), 'Wait for children.\n');
  fs.writeFileSync(path.join(repository, 'worker.ts'), 'export const worker = 1;\n');
  git('add', '.');
  git('commit', '-qm', 'Fixture baseline');
  const baseline = git('rev-parse', 'HEAD');
  const tracked = structuredClone(map);
  Object.assign(present(present(tracked.constraints)[0]), {
    baselineCommit: baseline,
    explanation: '取消请求不等于清理完成。',
    evidence: [{ path: 'rules.md', note: 'Fixture source.', quote: '<script>unsafe()</script> Wait for children.' }],
    code: [{ path: 'worker.ts', symbol: 'worker', note: 'Fixture worker.' }]
  });
  present(present(tracked.constraints)[0]!.translations).en!.explanation = 'A cancellation request is not completed cleanup.';
  fs.appendFileSync(path.join(repository, 'worker.ts'), '// changed\n');
  const reviewed = structuredClone(checkedEvents);
  Object.assign(present(present(present(reviewed[0]).constraintReviews)[0]), { checkedAt: '2026-09-18T00:00:00Z', gitCommit: baseline });
  await load(tracked, reviewed, { repository });
  await page.locator('#show-constraints').click();
  await page.locator('#constraint-filter').selectOption('review');
  assert.equal(await page.locator('.constraint-row').count(), 1);
  await page.locator('[data-constraint="cancel-propagation"]').click();
  assert.match(await page.locator('.constraint-freshness').textContent() || '', /待复核/);
  assert.match(await page.locator('.constraint-state').textContent() || '', /有证据支持/);
  assert.match(await page.locator('.constraint-detail').textContent() || '', /worker.ts|复核记录/);
  assert.equal(await page.locator('.constraint-source blockquote').isVisible(), true);
  assert.equal(await page.locator('.constraint-source script').count(), 0);
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 900 });
    for (const lang of ['zh', 'en']) {
      await page.locator('#language').selectOption(lang);
      assert.equal(await page.locator('#constraints-panel').evaluate(el => el.scrollWidth <= el.clientWidth + 1), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    }
  }
  assert.deepEqual(errors, []);
  console.log(`Constraint browser checks passed. Screenshots: ${output}`);
} finally {
  await browser.close();
}
