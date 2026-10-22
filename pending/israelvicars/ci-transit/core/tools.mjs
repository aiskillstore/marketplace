// core/tools.mjs: the browser and ffmpeg that core/setup.mjs chose, recorded in .transit-cache/setup.json.
// Every script launches Chromium and runs ffmpeg through here, so a reused system Chrome or a reused
// Playwright cache from another project is used the same way everywhere.
//   TRANSIT_BROWSER=/path/to/chrome | chrome | msedge | bundled   overrides the recorded choice
// Determinism: two renders on the same machine with the same browser build are byte-identical. Different
// browsers or builds (system Chrome vs Playwright's headless shell, or another version) can rasterize text
// slightly differently, so hashes are only comparable per machine+browser.
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const MARKER = join(ROOT, '.transit-cache', 'setup.json');
const marker = () => { try { return JSON.parse(readFileSync(MARKER, 'utf8')); } catch { return {}; } };

// {kind:'bundled'} | {kind:'channel', value:'chrome'} | {kind:'executable', value:'/path'}
export function browserChoice() {
  const env = process.env.TRANSIT_BROWSER;
  if (env) return env === 'bundled' ? { kind: 'bundled' } : /^(chrome|chrome-beta|msedge|msedge-beta|chromium)$/.test(env) ? { kind: 'channel', value: env } : { kind: 'executable', value: env };
  return marker().browser || { kind: 'bundled' };
}
export const launchOptions = (c = browserChoice()) => c.kind === 'channel' ? { channel: c.value } : c.kind === 'executable' ? { executablePath: c.value } : {};

export async function launchBrowser(opts = {}) {
  const { chromium } = await import('playwright-core');
  return chromium.launch({ ...launchOptions(), ...opts });
}

export const ffmpegBin = () => process.env.TRANSIT_FFMPEG || marker().ffmpeg?.ffmpeg || 'ffmpeg';

// Runs ffmpeg with an argument array (never a shell) and returns stdout + stderr as text, even when it exits non-zero.
export function ffmpegText(args) {
  const r = spawnSync(ffmpegBin(), ['-hide_banner', ...args], { encoding: 'utf8', maxBuffer: 1 << 26 });
  if (r.error) throw new Error(`cannot run ffmpeg (${ffmpegBin()}): ${r.error.code || r.error.message}`);
  return (r.stdout || '') + (r.stderr || '');
}
// Decoded video frame count from ffmpeg's own progress line (replaces ffprobe -count_frames).
export function countFrames(file) {
  const out = ffmpegText(['-nostdin', '-i', file, '-map', '0:v:0', '-f', 'null', '-']);
  const all = [...out.matchAll(/frame=\s*(\d+)/g)];
  if (!all.length) throw new Error(`ffmpeg reported no frames for ${file}`);
  return Number(all[all.length - 1][1]);
}
