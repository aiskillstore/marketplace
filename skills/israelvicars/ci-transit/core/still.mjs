import { ensureSetup } from './setup.mjs'; import { pathToFileURL } from 'node:url'; import { resolve } from 'node:path';
await ensureSetup({ need: ['deps', 'browser'] });
const { launchBrowser } = await import('./tools.mjs');
const [file, ...ts] = process.argv.slice(2);
const b = await launchBrowser(); const p = await b.newPage({ viewport: { width: 1200, height: 900 } });
const errs = []; p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => m.type() === 'error' && errs.push(m.text()));
await p.goto(pathToFileURL(resolve(file)).href + '?paused=1'); await p.evaluate(() => document.fonts.ready);
console.log(JSON.stringify(await p.evaluate(() => ({ s: window.VIZ && window.VIZ.seconds, f: document.fonts.check('700 14px "Transit Sans"') }))), errs);
for (const t of ts) { await p.evaluate((t) => window.renderAt(t), Number(t)); await p.screenshot({ path: `/tmp/still-${t}.png` }); }
await b.close();
