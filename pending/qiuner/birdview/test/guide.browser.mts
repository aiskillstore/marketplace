import { architecture, activity, present } from './fixtures.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { renderArchitecture } from '../src/render.mjs';
const { chromium }: typeof import('playwright') = await import(process.env.BIRDVIEW_PLAYWRIGHT_PATH ? pathToFileURL(process.env.BIRDVIEW_PLAYWRIGHT_PATH).href : 'playwright');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-guide-'));
const map = architecture(fs.readFileSync(new URL('../examples/system.architecture.json', import.meta.url), 'utf8'));
const events = activity(fs.readFileSync(new URL('../examples/harness.activity.jsonl', import.meta.url), 'utf8'));
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const file = path.join(dir, 'guide.html');
  fs.writeFileSync(file, renderArchitecture(map, events));
  await page.goto(pathToFileURL(file).href + '#lang=zh');
  await page.locator('#actual').click();
  const state = () => page.evaluate(() => {
    const step = document.getElementById('activity-step');
    const map = document.getElementById('map');
    const fit = document.getElementById('fit');
    const workspace = document.querySelector('.workspace');
    const disclosure = document.getElementById('activity-disclosure');
    if (!(step instanceof HTMLSelectElement) || !map || !fit || !workspace || !(disclosure instanceof HTMLDetailsElement)) throw new Error('Missing guide state elements');
    return { mode: document.querySelector('[data-view][aria-pressed="true"]')?.getAttribute('data-view'), index: step.value, selected: document.querySelector('#map .node.selected')?.getAttribute('data-module'), zoom: map.style.transform, fitting: fit.getAttribute('aria-pressed'), inspector: workspace.classList.contains('inspector-open'), disclosure: disclosure.open };
  });
  const before = await state();
  await page.locator('#guide-launch').click();
  assert.match(present(await page.locator('#guide-count').textContent()), /1 \/ 5/);
  for (let i = 0; i < 5; i++) {
    const box = present(await page.locator('#guide-card').boundingBox());
    assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= 1441 && box.y + box.height <= 901);
    await page.locator('#guide-next').click();
  }
  assert.deepEqual(await state(), before);
  await page.locator('#guide-launch').click();
  await page.locator('#guide-next').click();
  await page.keyboard.press('Escape');
  assert.deepEqual(await state(), before);
  assert.equal(await page.locator('#guide-launch').evaluate(el => el === document.activeElement), true);
  await page.reload();
  assert.equal(await page.locator('#guide-invite').isVisible(), false);
  await page.locator('#language').selectOption('en');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('#guide-launch').click();
  for (let i = 0; i < 5; i++) {
    const box = present(await page.locator('#guide-card').boundingBox());
    assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= 391 && box.y + box.height <= 845);
    assert.match(present(await page.locator('#guide-count').textContent()), /Step/);
    await page.locator('#guide-next').click();
  }
  fs.writeFileSync(file, renderArchitecture(map));
  await page.reload();
  await page.locator('#guide-launch').click();
  assert.match(present(await page.locator('#guide-count').textContent()), /1 of 2/);
  await page.locator('#guide-next').click();
  await page.locator('#guide-skip').click();
  assert.equal(await page.locator('#guide-dialog').isVisible(), false);
  assert.deepEqual(errors, []);
  console.log('Guide: 5/2 steps, Chinese/English, desktop/mobile, completion/Escape, state/focus restoration and persistent dismissal passed.');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
