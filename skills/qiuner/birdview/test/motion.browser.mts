import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { renderArchitecture } from '../src/render.mjs';
import { architecture, activity } from './fixtures.mjs';

const { chromium }: typeof import('playwright') = await import(process.env.BIRDVIEW_PLAYWRIGHT_PATH
  ? pathToFileURL(process.env.BIRDVIEW_PLAYWRIGHT_PATH).href : 'playwright');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-motion-'));
const browser = await chromium.launch();
try {
  const file = path.join(dir, 'viewer.html');
  fs.writeFileSync(file, renderArchitecture(
    architecture(fs.readFileSync(new URL('../examples/system.architecture.json', import.meta.url), 'utf8')),
    activity(fs.readFileSync(new URL('../examples/harness.activity.jsonl', import.meta.url), 'utf8')),
  ));
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(file).href);
  await page.locator('#nodes .node').first().hover();
  assert.equal(await page.evaluate(() => {
    const dot = [...document.querySelectorAll('.flow-dot')].find(el => el.getAnimations().length);
    if (!dot) throw new Error('Expected an animated relation');
    const animation = dot.getAnimations()[0];
    document.dispatchEvent(new Event('visibilitychange'));
    return dot.getAnimations()[0] === animation;
  }), true);
  assert.equal(await page.locator('.edge').first().evaluate(el => getComputedStyle(el).transitionDuration), '0.15s');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.waitForFunction(() => [...document.querySelectorAll('.flow-dot')].every(el => !el.getAnimations().length));
  await page.locator('#guide-launch').click();
  await page.locator('#guide-next').click();
  assert.equal(await page.locator('#guide-card').evaluate(el => el.getAnimations().length), 0);
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  // Two immediate clicks must retarget, not stack animations or lose the step.
  const active = await page.locator('#guide-next').evaluate(el => {
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 }));
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 }));
    return document.getElementById('guide-card')?.getAnimations().length;
  });
  assert.equal(active, 1);
  await page.locator('#guide-prev').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.locator('#guide-card').evaluate(el => el.getAnimations().length), 0);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#guide-dialog').isVisible(), false);
  assert.deepEqual(errors, []);
  console.log('Motion: flow continuity, reduced motion, rapid retargeting and keyboard immediacy passed.');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
