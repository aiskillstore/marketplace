---
name: explainer-high-energy
description: Make a 12–20 second high-energy motion-graphics promo for any product, rendered from code to MP4 with synthesised music. Fast beat-locked scene changes, kinetic typography, a shape that carries across every transition, a HUD frame. Use when someone wants a hype reel, teaser, launch sting or showreel-style promo for a product, app or brand.
---

# High-energy explainer

A 12–20 second hype piece that hits like a showreel. Every half-second something lands on the beat, but it never feels like random cuts, because **a shape carries the eye across every transition**: a spark becomes a line, the line floods the screen into the next background, a full stop detaches and becomes the ball the next scene is built around.

You write it as one HTML page that renders any frame from a time value, then render it to MP4 with motion blur and a synthesised soundtrack.

## Step 1: Get the brief (one message, then go)

Ask everything in **one** message, then work on your own. Only the product is required; for anything left blank, decide yourself and say what you chose.

1. **Product**: name, and what it does in a few sentences. A website URL is even better.
2. **The one thing** the viewer must remember (e.g. "type an idea, get a live app").
3. **Brand**: colours, fonts, logo file, or "use the website". If none, use the default palette below.
4. **Format**: 16:9 (1920×1080) or 9:16 (1080×1920). Default 16:9.
5. **Length**: default is given below for this style.
6. **Music**: their own track (a file path), or let you synthesise one. Default: synthesise.
7. **Direction** (optional): scenes they want, a tagline, a call to action, anything to avoid.

If they gave a URL, read it (web fetch) for the product's real wording, features, colours and font names before writing anything. Use their real words for UI labels and taglines.

**Never invent facts.** No made-up customer counts, revenue, ratings, testimonials or quotes. Numbers only if the user or the website states them; otherwise use relative bars, progress and placeholder skeleton lines. Example content inside the UI (a prompt, a file name, a project name, prices on a receipt) is fine and should be believable; claims about the product itself (stats, user counts, ratings, offers like "free") are not. Calls to action use only a URL or offer the user or the website gave; with none, end on the name and tagline.

**Logos.** Use a logo only if the user supplies the file or it is their own product and they asked for it. Otherwise write the name as text in the brand font. Third-party logos (integrations) only if supplied; otherwise neutral rounded tiles with the name.

Default length for this style: **15 seconds** (128 BPM, 8 bars). Range 12–20.

## Step 2: Plan the scenes, then build

### The structure (6–8 scenes of 1.5–3 s, on a 120–140 BPM grid)

Pick from these scene types and map the product onto them. Write the beat sheet first (scene, start time on the beat grid, what carries in, what carries out, sound).

1. **Spark open** (dark). Near-black canvas with a faint grid. A tiny accent mark appears, pulses, stretches into a thin horizontal line across the frame with a small mono label (`product / launch — 2026`), wobbles once, then the line **expands vertically into a full-screen flood** of the accent colour. That flood is the next background.
2. **Brand slam.** The product name in a heavy grotesk, all caps, huge, letters revealed by masks on consecutive 1/16 beats, a small mono kicker above (`INTRODUCING — 2026`) and an italic serif line below (what it is, 2–4 words). The weight can morph thin → black. The full stop or a letter's dot **detaches and grows** into the shape that starts the next scene.
3. **Kinetic triplet.** The value proposition as three short words or phrases, **two beats each** (three for a handwritten word, so it can be read), each with its own treatment and its own background, swapped hard on the beat (inside this scene the swaps are the rhythm, so they do not count as cuts): dark on cream; accent on black with the word repeated as an outline pattern filling the frame; white on electric blue inside viewfinder corner brackets with a tiny `1920 × 1080` label; a last word in handwritten script that draws itself on. Each word enters with a fast blur/slide and lands with a slight overshoot.
4. **Signature visual.** One "how did they make that" moment that symbolises the product: a 3D field of cubes rippling from the centre (drawn on canvas with your own perspective projection, coloured by height with the palette), a generative particle flow that condenses into a ring and bursts outward, or a liquid blob morphing between shapes. Pick the one that fits the product's idea (building blocks → cubes, data/AI → particles, flexibility → liquid). The camera tilts or orbits slowly while it plays.
5. **Product micro-moment.** One real interaction from the product as a floating UI card, tilted slightly in 3D with two ghost cards stacked behind it: the cursor flicks a toggle, presses the main button, a progress bar fills in the accent colour with a percentage, the button turns to `Done ✓`, a toast slides in at the top right. Use the product's real labels.
6. **Proof (only if real numbers exist).** A big count-up (`+312%` style, digits blurring while they spin), a donut ring, staggered bars rising with one accent bar, a line drawing over them with a tooltip. No real numbers → skip this scene or show the product's real capabilities as a list that slams in.
7. **Liquid/morph bridge.** The shape from the previous scene collapses to a dot, the dot becomes a ring pulse on dark, which becomes the dot in the logo.
8. **End card** (hold 2 s). Logo or name with the accent dot, italic serif tagline, a tracked mono line typing in letter by letter (the real URL or call to action if given, e.g. `PRODUCT.COM`; otherwise a short line from the brief), a hairline rule.

Not every product needs every scene; 6 strong ones beat 8 weak ones. Keep to **one idea per scene**.

### Rules that make it feel expensive

- **Transitions are objects, not cuts.** Every scene hands over to the next through a shape (flood, wipe by a growing bar, a dot that grows into the next background, a word that zooms through the camera). A hard cut between scenes is allowed only on a downbeat, at most twice.
- **Everything lands on the grid.** Big changes on beats, typography on 1/8 or 1/16 notes. Overshoot slightly (`z` ≈ 0.6–0.7) for impacts, then settle.
- **HUD frame on every scene:** thin corner brackets, `SCENE 02 / 07` top right, a category label bottom left in tiny mono (`KINETIC TYPE`, `PRODUCT`, `DATA`), and a running timecode bottom right with a red dot. Small (12–14 px at 1080p) and about 50% opacity; it should feel like a camera viewfinder.
- **Texture:** a soft radial vignette on every flat background, very subtle film grain (pre-generate a few seeded grain tiles at load and cycle them), and real motion blur.
- **Type:** a heavy grotesk for slams (e.g. Inter Tight 900 or Archivo Black), an italic serif for the human line (Instrument Serif italic), a mono for HUD and captions (JetBrains Mono or Geist Mono). If the brand has fonts, use theirs for the name and keep the mono for the HUD.
- **Default palette:** ink `#0B0B10`, accent `#FF4F1A`, cream `#EDEBE4`, electric blue `#2F47FF`, white. The brand's main colour replaces the accent and its second colour replaces the blue; a one-colour brand uses a deep shade of its colour as the second.
- **Banned:** stock-template looks, glows on everything, emoji, more than 3 colours in one scene (not counting black and white), text smaller than readable at a glance, any scene without motion.

### Sound

128 BPM (or the user's track). Punchy: kick on every beat, clap on 2 and 4, a sub bass following the scene roots, a filtered riser into the brand slam and the end card, an impact (low boom + noise burst) on each flood, short tonal blips on each typed word, a whoosh (band-passed noise sweep) on every carried transition, a soft ring-out on the end card. Mix the music under the hits.

## How the page must be built

One self-contained HTML file (inline CSS and JS; images only if the user supplied them). Draw with DOM + CSS transforms, SVG, or one full-screen canvas, whatever fits.

**The page contract**
- `window.VIDEO = {w, h, duration}` and `window.seek(t)`, a **pure function of time**: it sets every element for time `t` (seconds). No CSS transitions or animations, no `setTimeout`, no state carried from the previous frame. Any frame must render correctly on its own, in any order. Measuring layout inside `seek` (e.g. `offsetLeft`, `measureText`) is fine; it is deterministic.
- Randomness (grain, particles, noise in audio) comes from a seeded generator, never `Math.random`.
- Anything that needs a history (a camera that lags behind a moving object, a simulation) is **baked once at load**: step it from 0 to `duration` at 1/240 s, store the values, and have `seek` read them back with interpolation. For loops, start the simulation from the state the loop begins in (see the style's seam rule).
- **Loops:** `seek(t)` uses `t % duration`; effects that straddle the seam (a landing squash, a sound tail) are drawn or mixed at both ends.
- With `?render` in the URL: no controls, no preview scaling; the stage is exactly `w × h` at the top-left. Without it: the stage is scaled with CSS to fit the window and the preview controls are shown.
- **Fonts: embed them.** Download the woff2 files (Google Fonts or the brand's) and inline them as base64 `@font-face`, so the render never falls back silently. For a weight morph, use a variable font with a range (`wght@100..900`).
- **Layers:** give scene layers transparent backgrounds and let one stage background behind them provide the base colour, so a later layer never hides an earlier one by accident. Absolutely positioned text gets `white-space: nowrap`.
- **Speed:** large CSS `filter: blur()` and big blurred gradients are very slow to screenshot. Draw gradients and glows on a canvas once at load (or as an image) and move that.

**Helpers: paste these and build everything on them**

```js
// damped spring step response 0 -> 1. w = speed (8 slow, 14 normal, 22 snappy), z = damping (1 = no overshoot)
function spring(t, w = 14, z = 0.82) {
  if (t <= 0) return 0;
  if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
}
// a value that changes target many times, springing to each: track(start, [[time, value, w?, z?], ...]) -> f(t)
const track = (v0, keys) => t => { let v = v0, p = v0; for (const [tk, val, w, z] of keys) { v += (val - p) * spring(t - tk, w, z); p = val; } return v; };
// precise eased keyframes (best for camera moves): kf([[t0, v0], [t1, v1, easeFn?], ...]) -> f(t)
const kf = keys => t => { if (t <= keys[0][0]) return keys[0][1]; for (let i = 1; i < keys.length; i++) { const [a, va] = keys[i - 1], [b, vb, e = ease] = keys[i]; if (t <= b) return lerp(va, vb, e((t - a) / (b - a))); } return keys[keys.length - 1][1]; };
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => (x = clamp(x), x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);   // easeInOutCubic
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));      // 0..1 progress of t through [a, b]
const rng = s => () => (s = (s + 0x6D2B79F5) | 0, s = Math.imul(s ^ (s >>> 15), 1 | s), s ^= s + Math.imul(s ^ (s >>> 7), 61 | s), ((s ^ (s >>> 14)) >>> 0) / 4294967296);
```

- Typing: the visible string is `full.slice(0, n(t))` with a caret blinking from `t`. Count-ups: format `lerp(a, b, ease(seg(t, …)))`.
- A **camera** is a wrapper element with `transform: translate() scale() rotate()` driven by `kf` or `track`.

**Sound**
- `window.buildAudio(ctx)` schedules the whole soundtrack (music + effects) from time 0 on whatever `AudioContext` or `OfflineAudioContext` it is given, using the same timeline numbers as the visuals. Synthesise with oscillators, filtered noise (from a seeded buffer) and envelopes. If the user gave a music file, load it with `fetch` + `decodeAudioData`, set the beat grid to its tempo (measure it), and add only the effects on top.
- **Preview playback:** on the first play, render the soundtrack once into a buffer, then play from any scrubbed position. The clock drives `seek`:

```js
let buf, ac, src, startAt = 0, offset = 0, playing = false;
async function play() {
  ac ??= new AudioContext();
  if (!buf) { const off = new OfflineAudioContext(2, Math.ceil(48000 * VIDEO.duration), 48000); await buildAudio(off); buf = await off.startRendering(); }
  src = ac.createBufferSource(); src.buffer = buf; src.connect(ac.destination);
  src.start(0, offset % VIDEO.duration); startAt = ac.currentTime; playing = true;
}
function pause() { if (!playing) return; offset += ac.currentTime - startAt; src.stop(); playing = false; }
function now() { return playing ? (offset + ac.currentTime - startAt) % VIDEO.duration : offset; }
(function loop() { seek(now()); requestAnimationFrame(loop); })();   // the scrubber sets offset (pause, set, play)
```

- Put the beat sheet as a comment at the top of the script: one row per moment with its time, what happens, and which sound.

## Step 3: Check, render, deliver

Setup once in the working folder: `npm i playwright`, then `npx playwright install chromium` if Chromium isn't installed yet; ffmpeg must be on the PATH. Save the script at the bottom of this file as `render.mjs`.

1. **Stills.** `node render.mjs demo.html check.png --stills 0.5,1.2,…` with one time per row of the beat sheet (the sheet is at readable size, 3 per row). Look at it. Fix anything clipped, overlapping, unreadable, off-brand, badly framed or empty. Check again.
2. **Draft.** `node render.mjs demo.html draft.mp4 30 1 4` (fast: 30 fps, no motion blur, 4 parallel workers; set the last number to the machine's core count). This is the **review copy**: send it to the user with the HTML and ask for changes before the final.
3. **Final.** `node render.mjs demo.html demo.mp4 60 8 8`. Motion blur multiplies render time by the subframe count; a 60 s final can take 20–60 minutes on a laptop, so say so before starting. It writes `demo.mp4` (audio normalised to about −16 LUFS) and `demo_silent.mp4`.
4. **Deliver** the HTML (they can scrub it live), the MP4s, and a short note: the beat sheet, what is placeholder, and what to change for a second version. Offer one alternative direction in a sentence.

```js
// render.mjs: turn a seek(t) page into an MP4 with motion blur and its own audio.
//   node render.mjs page.html out.mp4 [fps=60] [subframes=4] [workers=4]
//   node render.mjs page.html sheet.png --stills 0.5,1.2,3   (full-size contact sheet for checking)
// Optional: window.buildAudio(ctx) schedules the soundtrack on any (Offline)AudioContext.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , html, out, a3 = '60', a4 = '4', a5 = '4'] = process.argv;
if (!html || !out) { console.log('usage: node render.mjs page.html out.mp4 [fps] [subframes] [workers]'); process.exit(1); }
const run = (args) => new Promise((res, rej) => { const p = spawn('ffmpeg', args, { stdio: 'inherit' }); p.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()); });
const url = pathToFileURL(path.resolve(html)).href + '?render';
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'], ...(proxy ? { proxy: { server: proxy } } : {}) });

// Read the size first, then open every page at exactly that size (pages that measure themselves on load stay correct).
const probe = await browser.newPage();
await probe.goto(url);
await probe.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
const V = await probe.evaluate(() => window.VIDEO);
await probe.close();

async function openPage() {
  const page = await browser.newPage({ viewport: { width: V.w, height: V.h }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
  // load every declared font, even ones only used by scenes hidden at t=0
  const bad = await page.evaluate(async () => {
    await Promise.all([...document.fonts].map(f => f.load().catch(() => {})));
    await document.fonts.ready;
    return [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family);
  });
  if (bad.length) console.warn('WARNING: fonts did not load (fallback in use):', [...new Set(bad)].join(', '), '- embed them as base64.');
  return page;
}
const shot = async (page, t) => { await page.evaluate(t => window.seek(t), t); return page.screenshot({ type: 'jpeg', quality: 95 }); };

if (a3 === '--stills') {
  const page = await openPage();
  const times = a4.split(',').map(Number), dir = out + '.frames';
  mkdirSync(dir, { recursive: true });
  for (let i = 0; i < times.length; i++) writeFileSync(`${dir}/${String(i).padStart(3, '0')}.jpg`, await shot(page, times[i]));
  await browser.close();
  const cols = Math.min(3, times.length), rows = Math.ceil(times.length / cols);
  await run(['-v', 'error', '-y', '-framerate', '1', '-i', `${dir}/%03d.jpg`, '-vf', `scale=${Math.min(960, V.w)}:-1,tile=${cols}x${rows}:padding=6:color=gray`, '-frames:v', '1', out]);
  rmSync(dir, { recursive: true });
  console.log('stills ->', out); process.exit(0);
}

const fps = +a3, sub = Math.max(1, +a4), workers = Math.max(1, +a5), N = Math.round(V.duration * fps);
const base = out.replace(/\.mp4$/, ''), silent = base + '_silent.mp4';
const vf = sub > 1 ? ['-vf', `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB)`] : [];
const t0 = Date.now(); let doneFrames = 0;
const per = Math.ceil(N / workers), segs = [];
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const a = w * per, b = Math.min(N, a + per); if (a >= b) return;
  const seg = `${base}_seg${w}.mp4`; segs[w] = seg;
  const page = await openPage();
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps * sub), '-i', '-', ...vf,
    '-r', String(fps), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = new Promise(r => ff.on('close', r));
  for (let f = a; f < b; f++) {
    for (let s = 0; s < sub; s++) {             // 180-degree shutter: sub-frames spread over half a frame
      const buf = await shot(page, (f + (sub > 1 ? (s / sub) * 0.5 : 0)) / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    if (++doneFrames % 30 === 0) process.stdout.write(`\r${doneFrames}/${N} frames  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await closed; await page.close();
}));
const list = base + '_segs.txt';
writeFileSync(list, segs.filter(Boolean).map(s => `file '${path.resolve(s)}'`).join('\n'));
await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]);
segs.filter(Boolean).forEach(s => rmSync(s)); rmSync(list);
console.log(`\nvideo -> ${silent}  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);

const page = await openPage();
const hasAudio = await page.evaluate(() => typeof window.buildAudio === 'function');
if (hasAudio) {
  const b64 = await page.evaluate(async (dur) => {
    const sr = 48000, ctx = new OfflineAudioContext(2, Math.ceil(sr * dur), sr);
    await window.buildAudio(ctx);
    const b = await ctx.startRendering(), L = b.getChannelData(0), R = b.getChannelData(b.numberOfChannels > 1 ? 1 : 0);
    const i16 = new Int16Array(L.length * 2);
    for (let i = 0; i < L.length; i++) { i16[2 * i] = Math.max(-1, Math.min(1, L[i])) * 32767; i16[2 * i + 1] = Math.max(-1, Math.min(1, R[i])) * 32767; }
    const u8 = new Uint8Array(i16.buffer); let s = '';
    for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return btoa(s);
  }, V.duration);
  const pcm = base + '.pcm'; writeFileSync(pcm, Buffer.from(b64, 'base64'));
  await run(['-v', 'error', '-y', '-i', silent, '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', pcm,
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out]);
  rmSync(pcm); console.log('with audio ->', out);
}
await browser.close();
```
