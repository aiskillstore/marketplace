// render.mjs: freeze an HTML animation at t = i / fps and save every frame as a PNG.
// Based on the renderer in Florence's "Opus 5.5 Motion Lab" article, with fixes:
//   - viewport comes from --width/--height, else window.STAGE, else the page's first <canvas>
//     (the article hardcoded 1200x675 and silently cropped anything else)
//   - the page's requestAnimationFrame loop is frozen during capture, so a preview loop
//     cannot overwrite the frame between renderAt(t) and the screenshot (the article's version
//     produced different PNGs on repeat runs when the page had a rAF loop)
//   - old NNNN.png frames are removed first (only those files, never the folder's other contents),
//     so stale frames from a longer earlier render never end up in the MP4/GIF
//   - --frames renders only named stills (for the review loop), --scale renders at 2x
//
// usage:
//   node render.mjs <file.html> [seconds=6] [fps=24] [options]
//   node render.mjs anim.html 4 24
//   node render.mjs anim.html 4 24 --width 1080 --height 1350
//   node render.mjs anim.html 4 24 --frames 0,24,48,72 --out out/stills
// options:
//   --width N --height N   viewport in CSS px (default: window.STAGE, then <canvas>, then 1200x675)
//   --scale N              deviceScaleFactor, e.g. 2 for crisp text (PNG is W*N x H*N)
//   --frames a,b,c         only these frame numbers (no folder wipe, existing files are overwritten)
//   --out DIR              output folder (default out/frames)
import { launchBrowser } from './tools.mjs';
import { pathToFileURL } from 'node:url';
import { clearFrames, prepareFramesDir } from './fsguard.mjs';
import { resolve, join } from 'node:path';

const pos = [], opt = {};
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[++i];
  else pos.push(argv[i]);
}
const [file = 'anim.html', secs = '6', fps = '24'] = pos;
const FPS = Number(fps), N = Math.round(Number(secs) * FPS);   // frames 0 to N-1, never N
const OUT = opt.out || 'out/frames';
const SCALE = Number(opt.scale) || 1;
const only = opt.frames ? opt.frames.split(',').map(Number) : null;
if (!(FPS > 0) || !(N > 0)) { console.error('seconds and fps must be positive numbers'); process.exit(1); }

// only Transit's own frame files are removed (core/fsguard.mjs); unsafe folders are refused
try { if (!only) clearFrames(OUT); prepareFramesDir(OUT); }
catch (e) { console.error(`transit: ${e.message}`); process.exit(1); }

const browser = await launchBrowser();
const context = await browser.newContext({ viewport: { width: 1200, height: 675 }, deviceScaleFactor: SCALE });
// Runs before any page script: tell the page it is being rendered, and wrap rAF so it can be frozen.
await context.addInitScript(() => {
  window.__RENDER_MODE = true;
  const raf = window.requestAnimationFrame.bind(window);
  window.__origRAF = raf;
  window.requestAnimationFrame = (cb) => (window.__RENDER_FREEZE ? 0 : raf(cb));
});
const page = await context.newPage();
await page.goto(pathToFileURL(resolve(file)).href, { waitUntil: 'networkidle' });
await page.evaluate(async () => { await document.fonts.ready; });

// Size: CLI args win, then window.STAGE {width,height}, then the first canvas.
let width = Number(opt.width), height = Number(opt.height);
if (!width || !height) {
  const detected = await page.evaluate(() => {
    if (window.STAGE && window.STAGE.width) return { width: window.STAGE.width, height: window.STAGE.height };
    const c = document.querySelector('canvas');
    if (!c) return null;
    const r = c.getBoundingClientRect();
    return { width: Math.round(r.width) || c.width, height: Math.round(r.height) || c.height };
  });
  width = width || detected?.width || 1200;
  height = height || detected?.height || 675;
}
await page.setViewportSize({ width, height });

// Freeze the page's own animation loop, then let any in-flight frame finish.
await page.evaluate(() => new Promise((done) => {
  window.__RENDER_FREEZE = true;
  window.__origRAF(() => window.__origRAF(done));
}));

const list = only || Array.from({ length: N }, (_, i) => i);
for (const i of list) {
  await page.evaluate((t) => {
    if (window.renderAt) window.renderAt(t);
    document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t * 1000; });
  }, i / FPS);
  await page.screenshot({ path: join(OUT, `${String(i).padStart(4, '0')}.png`) });
}
await browser.close();
console.log(`rendered ${list.length} frame(s) at ${width}x${height}${SCALE !== 1 ? ` @${SCALE}x` : ''} to ${OUT}` +
  (only ? '' : ` (frames 0..${N - 1} = ${secs} s x ${FPS} fps)`));
