import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { present } from './fixtures.mjs';

const { chromium }: typeof import('playwright') = await import(process.env.BIRDVIEW_PLAYWRIGHT_PATH
  ? pathToFileURL(process.env.BIRDVIEW_PLAYWRIGHT_PATH).href : 'playwright');
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(new URL('../docs/index.html', import.meta.url).href);
    for (const lang of ['en', 'zh']) {
      if (lang === 'zh') await page.locator('#language').click();
      assert.equal(await page.locator('html').getAttribute('lang'), lang === 'zh' ? 'zh-CN' : 'en');
      for (const agent of ['codex', 'claude-code', 'deepseek']) {
        await page.locator('#install-agent').selectOption(agent);
        const root = agent === 'deepseek' ? '$HOME/.dsh/skills/birdview' : agent === 'claude-code' ? '$HOME/.claude/skills/birdview' : '$HOME/.agents/skills/birdview';
        const install = present(await page.locator('#install-command').textContent());
        assert.equal(install, agent === 'deepseek' ? `git clone https://github.com/Qiuner/birdview.git "${root}"` : `npx skills add Qiuner/birdview --skill birdview --agent ${agent} --global --copy --yes`);
        assert.equal(await page.locator('#check-command').textContent(), `npm --prefix "${root}" ci\nnode "${root}/scripts/birdview.mjs" doctor`);
        assert.match(present(await page.locator('#install-guide').getAttribute('href')), lang === 'zh' ? /installation\.zh\.md$/ : /installation\.md$/);
        await page.evaluate(() => Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
          writeText: async (text: string) => { document.documentElement.setAttribute('data-copied', text); },
        } }));
        await page.locator('[data-copy="install-command"]').click();
        assert.equal(await page.locator('html').getAttribute('data-copied'), install);
        assert.equal(await page.locator('#copy-status').textContent(), lang === 'zh' ? '已复制。' : 'Copied.');
        await page.evaluate(() => Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
          writeText: async () => { throw new Error('Permission denied'); },
        } }));
        await page.locator('[data-copy="check-command"]').click();
        assert.match(present(await page.locator('#copy-status').textContent()), lang === 'zh' ? /复制失败/ : /Could not copy/);
      }
    }
  }
  assert.deepEqual(errors, []);
  console.log('Site: desktop/mobile, both languages, three agents and clipboard success/failure passed.');
} finally {
  await browser.close();
}
