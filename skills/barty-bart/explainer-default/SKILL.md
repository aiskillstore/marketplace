---
name: explainer-default
description: Make a clean 45–90 second product demo video for any software product, rendered from code to MP4 with music. Airy light canvas, short centred lines the camera pushes into, the product's own UI rebuilt and shown up close as it is used (typing, results, tables, clicks), integrations, and a logo close. Use when someone wants a product demo, launch video, feature walkthrough or "how it works" video for an app, SaaS or tool.
---

# Default explainer

A calm, premium product demo, the kind a well-funded startup puts on its homepage. Its whole trick is restraint: a bright, airy canvas, one short line of text at a time, and the product's own interface rebuilt cleanly and filmed **up close** while it is being used. The camera does the storytelling: it pushes into a line of text, rides along with typing, pulls back to reveal the result, and glides to the next feature.

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

Also ask for (optional): the **3–5 features or workflow steps** to show, and anything the product connects to (integrations). If they gave a URL, take these from the site.

Default length for this style: **60 seconds**. Range 45–90. Budget by length (drop optional sections first):

| Length | Features | Optional sections |
|---|---|---|
| 45 s | 2–3, about 9 s each | proof or integrations, not both |
| 60 s | 3–4, about 10 s each | one of proof / integrations |
| 90 s | 4–5, about 12 s each | both |

## Step 2: Write the script, then build

### The structure

Write the script and beat sheet first: every line of on-screen text, which UI moment follows it, and its time; add the times up against the budget above. On-screen text is the only "voice", so it has to tell the story by itself.

**How scenes and camera fit together:** each scene (a title line, a UI moment) is its own layer with its **own camera**. Inside a scene the camera pushes, rides and pulls back; between scenes the outgoing layer dissolves with a short blur (0.3–0.4 s) into the next one, which is already moving.

1. **Open (0–5 s).** Plain light canvas. A small word fades up in the centre: `Introducing`. It dissolves into the brand moment: the soft brand gradient sweeps in (silk-like diagonal light bands drifting slowly) with the logo or name centred, small.
2. **The problem or the ask (≈5 s).** A short line that the viewer recognises (`Still building prospect lists by hand?`), or go straight to the product's input: a large rounded input box, empty with placeholder text, suggestion chips underneath.
3. **Feature chapters (3–5, about 8–15 s each).** Each one is:
   - **A title line**: one short sentence, small (about 28 px at 1080p), centred on the plain canvas. It types or fades in word by word. Then the **camera pushes in** on it until the line spans about 75% of the frame width, and **one key word or short phrase gets a highlight**: a soft brand-colour box sweeping left to right behind it (`Call the decision maker. Directly.`).
   - **The UI moment**: the product's real interface, rebuilt as clean vector UI (not screenshots), cropped to only the part that matters and shown big. The camera is close enough that the element fills most of the frame, and it rides along with the action: text typing into the input (the camera follows the caret; measure the text with `measureText` to know where it is), an agent's steps ticking off one by one (spinner → check, `Found 247 matches`), result cards stacking up with the far ones blurred (depth of field), a table filling row by row, the cursor clicking a cell button and the value revealing, a new column being added and each cell "thinking" with a shimmer before its value appears, a popover opening with reasoning and sources.
   - **The pull-back**: after the action, the camera eases out to show the whole screen for a beat, so the viewer understands where they are, then glides on.
4. **Proof (optional, only real numbers).** A sentence with a number that counts up, the number highlighted (`Backed by a database of 300M+ profiles`), over a subtle dotted globe or grid.
5. **Integrations (optional).** `Built for your existing workflow.` in the centre while 8–12 app tiles (rounded squares, real logos only if supplied; repeat the integrations if there are few) float in from the edges at different depths: near ones larger and slightly blurred, far ones small and sharp, all drifting with parallax. Here the text scales up on its own instead of a camera push, so the tiles stay in frame.
6. **Closer.** On the brand gradient: one sentence with a rotating highlighted word that cycles through the use cases (`Do all your [prospecting / research / outreach] in Product.`), then, only if the product really has one, another way to use it (e.g. `Or just ask Claude` for a product with a Claude connector), then the tagline with its key phrase highlighted.
7. **End card (3 s).** Logo or name on the brand gradient, URL or call to action small below.

### Rules that make it feel premium

- **One thing at a time.** Never more than one line of text plus one UI element on screen. Text and UI almost never share the frame: text scene, then UI scene.
- **The camera is the editor.** No hard cuts. Every scene change is a camera move (push in, pull out, glide) or a soft blur-dissolve on the plain canvas. Camera moves are smooth eases (`ease` over 0.6–1.2 s) or heavily damped springs (`z` ≥ 0.95); nothing bounces.
- **Real UI, made clean.** Rebuild the product's interface from what you know of it (or its website): its real layout, labels, colours, fonts and corner radii, simplified to what the scene needs. Content inside it is believable example data that fits the product. Soft shadows, 1 px borders, generous whitespace.
- **Cursor:** a normal macOS-style arrow, moving on gentle curves, arriving a beat before it clicks, with a small press dip and a soft ripple on the clicked control. Hover states change.
- **Type:** the brand's font if known; otherwise Inter or Geist. Small, regular weight for title lines (they become big through the camera, not the font size). Tight letter-spacing on large text.
- **Default palette:** canvas `#F7F7F8`, text `#111114`, secondary `#8A8A94`, UI surfaces white with `#E7E7EC` borders, brand accent `#2E6BFF`, highlight box = accent at 15–20% opacity. Brand gradient: white → pale accent → accent, as slow diagonal silk bands (draw them on a canvas, not with CSS blur). Brand colours replace the accent.
- **Pacing:** each title line holds about 2 s after it lands; UI moments run at real speed (typing at about 25 characters per second), with pauses of 0.5 s after each result so the viewer can read it.
- **Banned:** busy backgrounds behind UI, more than one accent colour, bouncy easing, emoji, big drop shadows, glassmorphism everywhere, invented metrics or testimonials.

### Sound

An uplifting, gentle bed at 100–110 BPM (soft piano or pluck chords, light percussion entering after the open, a lift into the closer), quiet and warm. Sound effects small: key ticks while typing, soft clicks, a light "tick" per completed step, a soft whoosh on big camera moves, a gentle chime on the end card. The music should sit like a background in a well-made product video, not drive it.

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
3. **Final.** `node render.mjs demo.html demo.mp4 60 4 8`. Motion blur multiplies render time by the subframe count; a 60 s final can take 20–60 minutes on a laptop, so say so before starting. It writes `demo.mp4` (audio normalised to about −16 LUFS) and `demo_silent.mp4`.
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
