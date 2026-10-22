// core/render.mjs: trace file -> out/<name>/{transit.html, frames/, anim.mp4, anim.gif, contact.png}
// Frame-exact: the page's rAF loop is frozen and every frame is renderAt(i / fps).
// usage: node core/render.mjs <trace.json> [--name NAME | --out-dir DIR] [--frames DIR] [build options...]
//   build options include --strict / --share, --keep-uuids, --keep-ci-titles, --no-scrub (see core/scrub.mjs)
import { execFileSync } from 'node:child_process';
import { ensureSetup } from './setup.mjs';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { build } from './build.mjs';
import { parseArgs, runCli, UserError } from './cli.mjs';
import { assertSafeOutputDir, safeName } from './fsguard.mjs';

await runCli(async () => {
  const { opt, pos } = parseArgs(process.argv.slice(2));
  if (!pos[0]) throw new UserError('usage: node core/render.mjs <trace.json> [--name NAME | --out-dir DIR] [--strict]');
  const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
  const name = opt['out-dir'] ? String(opt.name || 'trace') : safeName(String(opt.name || 'trace'));
  const dir = assertSafeOutputDir(resolve(opt['out-dir'] || join(ROOT, 'out', name)), 'output folder');
  const frames = resolve(opt.frames || join(dir, 'frames'));
  assertSafeOutputDir(frames, 'frames folder');
  // build first: a bad input file fails here with a one-line reason, before any setup or download
  const { out: html } = build(resolve(pos[0]), { ...opt, out: join(dir, 'transit.html') });
  await ensureSetup({ need: ['deps', 'browser', 'ffmpeg'] });
  const { launchBrowser } = await import('./tools.mjs');
  const browser = await launchBrowser();
  const page = await browser.newPage();
  await page.goto(pathToFileURL(html).href + '?paused=1');
  const { seconds, fps, msPerSec } = await page.evaluate(() => window.VIZ);
  await browser.close();
  console.log(`${name}: ${seconds.toFixed(3)} s at ${fps} fps, 1 s of video = ${msPerSec} ms of trace`);
  const run = (args) => execFileSync(process.execPath, args, { cwd: ROOT, stdio: 'inherit' });   // arg arrays, no shell
  run(['core/render-frames.mjs', html, String(seconds), String(fps), '--out', frames]);
  if (opt['frames-only']) return;
  for (const k of ['mp4', 'gif', 'sheet']) run(['core/export.mjs', k, '--fps', String(fps), '--frames', frames, '--out', dir]);
});
