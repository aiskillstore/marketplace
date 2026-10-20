---
name: explainer-engaging
description: Make a 10–30 second continuous-shot explainer for any product, rendered from code to MP4 with sound. One hero element (a ball, a cursor, a file, a message) travels through the product's workflow laid out as stations on one big canvas; the camera follows it, each station reacts as it passes, then the camera pulls out to reveal the whole journey. Use when someone wants an engaging, story-driven, one-take explainer or a loopable product animation.
---

# Engaging explainer

A one-take visual story. A single **hero element** (in the reference style, a white ball that starts as a toggle's knob) travels through a chain of small interface "stations", and each station reacts to it: it rolls along a slider and pushes it to 100, falls off the end and bounces down a stack of notifications that pop up as it passes, lands on a keyboard and bounces key to key typing a word, hits return and is launched back into the air. The camera **never cuts**: it keeps the hero near the centre and zooms in for each interaction, and at the climax it pulls far out so the viewer sees the whole course laid out at once, before diving back in to where it all started.

For a product, the stations are the **steps of its workflow**, laid out spatially on one canvas, and the hero is the thing that moves through that workflow. The pull-out is the "now you get how it works" moment.

You write it as one HTML page that renders any frame from a time value, then render it to MP4 with motion blur and a soundtrack.

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

Also ask for (optional): the **workflow in 3–6 steps** (what the user does → what the product does → the result). If they gave a URL, derive it from the site.

Default length for this style: **12 seconds**, seamless loop. Range 10–30 (longer = more stations, not slower stations).

## Step 2: Design the course, then build

### 1. Choose the hero

The hero is one simple, readable object the product's story is about, and it never disappears or gets replaced (it may change shape for a moment, then return): a ball/knob (default, works for anything), a text caret or cursor, a file or document tile, a message bubble, a coin or order, a data point. It should fit a station's interface naturally (a knob, a thumb, a key cap, a pin).

### 2. Map the workflow onto stations

Each step becomes one station: a compact real interface element that the hero physically interacts with, and that **visibly changes because of it**. Draw from these mechanics:

| Mechanic | The hero... | The station reacts |
|---|---|---|
| Toggle / button | is the knob, or presses it | switches on, colour fills |
| Slider / progress | rolls along it as the thumb | value counts up in a tooltip, track fills |
| Notification stack | falls and bounces on each card | each card pops in as it is hit, with a message that narrates the story |
| Keyboard / input | bounces key to key | each key presses down, letters appear in the input above |
| List / table | slides down the rows | each row highlights, ticks, or sorts |
| Chart | becomes the line's leading dot | the line draws behind it, bars rise as it passes |
| Chat | rides in as a bubble | the reply types out |
| Deploy / send button | is launched by it | a toast or URL appears |

The station labels and messages tell the story in a few words each, with some wit (the reference uses `Slider · Reached 100`, `Gravity · Something is falling`, `Messages · What now?`, then types `retry`). For a product, write them from its real workflow (e.g. a coding tool: prompt typed → `Agent · Writing 12 files` → progress → `Preview · Ready` → Deploy pressed → `Live at myapp.app`).

### 3. Lay out the world

Place the stations on **one large canvas** (about 3× the frame), in the order the hero visits them, so the path zig-zags (right along the top, down through the middle, across the bottom). Gravity should make sense: falls go down, launches go up. Leave each station's spot fixed for the whole video. The world is a dark canvas with a faint dot grid that moves with the camera (the grid is what makes the camera moves readable).

### 4. Script the hero's path

The hero's position is a pure function of time, built from segments between **contact points** (each contact is on a beat):

- **Rolling/sliding** along a station: position by `ease` or a spring along the track; the station's value is derived from the hero's position.
- **Hops and falls** between contacts: a parabola (`x` linear in time, `y = y0 + v·t + ½·g·t²`, solve `v` so it lands on the next contact at the beat). Gravity constant across the whole video.
- **Impacts:** squash on contact (scale 1.25 × 0.8 for about 60 ms, spring back), stretch along the velocity in flight (up to 1.15 × 0.9), plus a small push-down of whatever was hit.
- **The launch:** the last station fires the hero up and back toward the start in one long arc, while every station **resets in reverse** behind it (values count down, notifications dismiss, the input clears) so the loop closes. Run the launch arc in **slow motion**: first choose the apex height you want (the top of the course), which fixes the real flight time under your gravity, then warp time so that flight fills the reveal window, slowest at the apex (often 5–10× there; e.g. speed `1 − 0.9·sin(πu)^0.6` over the arc). Schedule the station resets **during the reveal hold**, after the viewer has seen the full course, not at the moment of launch.
- **Seam:** put the loop point at the hero's landing on the first station. `seek(duration)` must look exactly like `seek(0)`; the landing squash and key press also show at time 0. For sound, render the soundtrack inside `buildAudio` into your own slightly longer `OfflineAudioContext`, fold the tail past `duration` back onto the start, and play that buffer into the given context.
- **Gravity is side-on.** Lay the stations out so falls make sense from the side: notification cards form a staircase (each card offset sideways by more than its width, so the hero never passes through one), and the keyboard is seen head-on with the hero hopping between keys in small arcs.
- **The empty slot:** when the hero was part of a station (a knob, a thumb) and leaves, the station keeps a dim outline of the slot it left, which fills again when the hero returns.

### 5. The camera

The camera is the hard part; get it right before polishing anything else.

- **Follow:** camera target = a blend of the hero position (plus a lead of about 0.15 s of its velocity) and a fixed **anchor** for the current station, smoothed by a critically damped spring (`w` ≈ 6) so it never jerks on impacts. Weight toward the anchor about 0.7 during an interaction (the station stays framed), 0.15 during falls and hops (the hero leads), 0.85 on the payoff hold. The smoothing needs history, so **bake it at load** (see the page contract), starting at time 0 from the first station's fixed framing and blending into following over the first 0.8 s. The hero never leaves the middle half of the frame.
- **Zoom:** tight during each interaction: the station fills about half the frame width and the hero is **50–70 px on screen** (at 1080p). Slightly wider during falls and hops so the next station is already visible. Frame the station, not empty canvas.
- **The payoff hold:** before the launch, hold on the final result (the toast, the live URL) for 0.4–0.6 s, fully in frame.
- **The reveal:** on the launch, the camera stops following and eases to a fixed framing that fits the whole course (about 0.3×), with a slight 3D tilt (`perspective` + `rotateX` of 15–25°) for depth. Hold about 1 s while the hero arcs across it; scale the hero up and give it a soft halo so it stays the brightest, most visible thing (at least 24 px on screen). Then **dive** to a fixed framing of the first station, timed so the hero lands there as the camera arrives, and blend back into following.
- Real motion blur: the hero and the world smear on fast moves; that is part of the look.

### Look

- **Default palette** (dark iOS-like): canvas `#0C0C0E`, dot grid `#1E1E22`, surfaces `#1C1C1F` / `#2C2C2E`, text `#F2F2F7`, secondary `#8E8E93`, accent `#0A84FF`, hero white `#FFFFFF`. Brand colours replace the accent; the hero stays the brightest thing on screen. A light variant (canvas `#F2F2F4`, hero = accent) is fine if the brand is light.
- Real-looking system UI: toggles, sliders with tick marks, notification cards with an app icon square, a title, a body line and `now`; a keyboard with key caps and a return key. Font: SF-like (Inter or Geist).
- A cursor may start the chain (clicks the first station) and then gets out of the way.
- **Banned:** cuts, fades to black, text overlays that explain what is happening (the stations' own labels are the only text), more than one hero, stations that do not react, physics that look floaty.

### Sound

A tight, minimal groove at 110–120 BPM (soft kick, clicky hats, a muted pluck bass), and the **hero's contacts are the main instrument**: each impact plays a short pitched tick or marimba note (pitch rises as the story advances), key presses click, slider movement plays fine ticks that speed up with the value, notifications get a soft pop, the launch gets a whoosh up and the dive a whoosh down. Every sound lands exactly on its visual contact.

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
