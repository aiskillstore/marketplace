// scripts/export.mjs: turn out/frames/*.png into an MP4, a single-palette GIF, a contact sheet,
// and a loop check. Works on macOS, Linux and Windows (needs only node + ffmpeg, see core/setup.mjs).
//
// usage: node core/export.mjs [all|mp4|gif|sheet|loop] [--fps 24] [--frames out/frames] [--out out]
//
// Runs the article's ffmpeg commands with these fixes:
//   - GIF is scaled to fit inside 1200x1080 (X's GIF limit is 1280x1080; the article's
//     scale=1200:-1 made a 1200x1200 GIF for square input and also upscaled 1080 px sources)
//   - contact sheet always shows 12 frames spread across the whole clip (the article's
//     "every 12th frame" left 4 black cells on a 4 s / 24 fps loop) and adds -update 1,
//     which ffmpeg 7 asks for when writing a single image
//   - loop check also measures the seam: SSIM(frame N-1, frame 0) vs the median
//     SSIM of neighbouring frames, so you get a number, not just a video to eyeball
import { execFileSync } from 'node:child_process';
import { readdirSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { ffmpegBin, countFrames } from './tools.mjs';

const argv = process.argv.slice(2);
const what = argv[0] && !argv[0].startsWith('--') ? argv[0] : 'all';
const opt = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[++i];
const FPS = Number(opt.fps) || 24;
const FR = opt.frames || 'out/frames';
const OUT = opt.out || 'out';
mkdirSync(OUT, { recursive: true });

if (!existsSync(FR)) { console.error(`no ${FR}: run render.mjs first`); process.exit(1); }
const files = readdirSync(FR).filter((f) => /^\d{4}\.png$/.test(f)).sort();
const N = files.length;
if (!N) { console.error(`no frames in ${FR}`); process.exit(1); }
const pattern = join(FR, '%04d.png');
const ff = (args) => execFileSync(ffmpegBin(), ['-hide_banner', '-loglevel', 'error', '-y', ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
const probeFrames = countFrames;   // ffmpeg's own frame count; no ffprobe

console.log(`${N} frames in ${FR} at ${FPS} fps = ${(N / FPS).toFixed(3)} s`);

if (what === 'all' || what === 'mp4') {
  const f = join(OUT, 'anim.mp4');
  ff(['-framerate', String(FPS), '-i', pattern, '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
    '-crf', '18', '-movflags', '+faststart', f]);
  console.log(`mp4   ${f} (${probeFrames(f)} frames)`);
}

if (what === 'all' || what === 'gif') {
  const f = join(OUT, 'anim.gif');
  const vf = "scale='min(1200,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease:flags=lanczos," +
    'split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle';
  ff(['-framerate', String(FPS), '-i', pattern, '-vf', vf, '-loop', '0', f]);
  console.log(`gif   ${f} (${probeFrames(f)} frames${N > 350 ? ', WARNING: X caps GIFs at 350 frames' : ''})`);
}

if (what === 'all' || what === 'sheet') {
  const f = join(OUT, 'contact.png');
  const step = Math.max(1, Math.floor(N / 12));
  const vf = `select='not(mod(n\\,${step}))*lt(n\\,${step * 12})',scale=400:-1,tile=4x3:padding=4:color=white`;
  ff(['-framerate', String(FPS), '-i', pattern, '-vf', vf, '-frames:v', '1', '-update', '1', f]);
  console.log(`sheet ${f} (frames ${Array.from({ length: Math.min(12, N) }, (_, i) => i * step).join(', ')}; left to right, top to bottom)`);
}

if (what === 'all' || what === 'loop') {
  const mp4 = join(OUT, 'anim.mp4');
  if (existsSync(mp4)) {
    const f = join(OUT, 'loop_check.mp4');
    ff(['-stream_loop', '2', '-i', mp4, '-c', 'copy', f]);
    console.log(`loop  ${f} (3 plays back to back, watch the seam)`);
  }
  // SSIM between each frame and the next (N-1 values), then the seam: frame N-1 vs frame 0.
  const ssim = (args) => execFileSync(ffmpegBin(), ['-hide_banner', '-loglevel', 'error', ...args,
    '-lavfi', 'ssim=stats_file=-', '-f', 'null', '-'], { maxBuffer: 1 << 26 }).toString()
    .trim().split('\n').map((l) => Number((l.match(/All:([\d.]+)/) || [])[1])).filter((x) => !Number.isNaN(x));
  const inner0 = N > 1 ? ssim(['-framerate', String(FPS), '-i', pattern,
    '-framerate', String(FPS), '-start_number', '1', '-i', pattern]) : [];
  const seam0 = ssim(['-i', join(FR, files[N - 1]), '-i', join(FR, files[0])]);
  const s = [...inner0.slice(0, N - 1), ...seam0];
  if (s.length === N) {
    const seam = s[N - 1], before = s[N - 2], after = s[0];
    const inner = s.slice(0, N - 1).sort((x, y) => x - y), median = inner[Math.floor(inner.length / 2)];
    console.log(`seam  SSIM(frame ${N - 1} -> 0) = ${seam.toFixed(4)}; steps around it: ${N - 2}->${N - 1} ${before.toFixed(4)}, 0->1 ${after.toFixed(4)}; clip median ${median.toFixed(4)}`);
    // Heuristic: a pop at the seam shows up as a much bigger change than the steps on either side.
    const jump = 1 - seam, local = Math.max(1 - before, 1 - after);
    if (seam > 0.99999) console.log('seam  WARNING: frame N-1 is identical to frame 0, you probably rendered frame N (first frame shown twice)');
    else if (jump > 3 * local + 0.002) console.log(`seam  CHECK: the cut from frame ${N - 1} to 0 is a bigger change than its neighbours, look at frames ${N - 2}, ${N - 1}, 0, 1`);
    else console.log('seam  OK: the last frame flows into frame 0 like any other step');
  } else {
    console.log(`seam  could not parse SSIM output (${s.length} values for ${N} frames)`);
  }
}
