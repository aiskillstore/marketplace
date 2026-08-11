# MrBeast text overlay & bake (HTML/CSS + canvas)

How to lay a MrBeast-style headline over the image and "bake" it into a flat PNG.
Two layers: (1) a **live HTML/CSS preview** to tune the text in a browser, (2) a
**canvas bake** — the same look re-rendered to pixels at the image's native resolution.

This is the implementation of the 5 overlay styles named in the skill's Text policy. The
overlay is the DEFAULT delivery for headline text (zero generation credits, always legible);
baking text INTO the generation is the fallback, only on an explicit ask.

## What makes text "MrBeast-y"

Not one trick but a stack of six — remove any one and it falls apart.

| Trait | Value | Why |
|---|---|---|
| Font | **Anton** (or Anton SC), one weight, reads `900`-heavy | fat condensed grotesk — the signature |
| Case | **ALL CAPS** | maximum density and aggression |
| Stroke | manual, **thick** (8–14% of cap size), drawn UNDER the fill | separates letters from any background |
| Shadow | hard, dark, offset down, blur shifted | "sticker" depth |
| Color | white / yellow→orange→red gradient / acid lime `#D4FF3F` | punchy contrast, reads in the feed |
| Tracking | tight (`-0.01…-0.02em`), line-height `0.9` | letters lock together like a logo |

Placement rules:
- **2–4 words max.** A headline, not a sentence.
- **Not on the face.** Text in a free quarter (bottom / corner / side).
- **Large.** Cap height 12–18% of frame height. When in doubt, bigger.
- **Margins:** keep text within the frame with comfortable padding, off the extreme edges.

## Layer 1 — live HTML/CSS preview

Feed the background into `--bg`, put the text in `<h1>`, tune it in a browser.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: url('photo.jpg');   /* local path or image URL */
    --W: 1280px;              /* frame size (16:9 = 1280×720) */
    --H: 720px;
  }
  * { margin: 0; box-sizing: border-box; }
  #poster {
    position: relative;
    width: var(--W); height: var(--H);
    background: var(--bg) center/cover no-repeat;
    overflow: hidden;
    font-family: 'Anton', sans-serif;
  }
  /* text block — bottom-center, comfortable margin */
  #headline {
    position: absolute;
    left: 50%; bottom: 6%;
    transform: translateX(-50%);
    text-align: center;
    line-height: 0.9;
    letter-spacing: -0.01em;
    text-transform: uppercase;
    white-space: pre-line;         /* line breaks via \n in the text */
  }
  #headline .line {
    font-size: 120px;              /* ≈16% of 720 */
    color: #fff;
    /* CRITICAL: paint-order draws the stroke UNDER the fill — otherwise it eats the letters */
    -webkit-text-stroke: 14px #000;
    paint-order: stroke fill;
    /* hard "sticker" shadow */
    text-shadow: 0 8px 0 rgba(0,0,0,.35), 0 14px 24px rgba(0,0,0,.55);
  }
</style>
</head>
<body>
  <div id="poster">
    <div id="headline">
      <div class="line">I SPENT</div>
      <div class="line" style="color:#D4FF3F">100 DAYS</div>
    </div>
  </div>
</body>
</html>
```

> `paint-order: stroke fill` is critical. Without it the stroke paints ON TOP and "eats" half
> the letter — the #1 bug in 90% of home-made MrBeast text.

## 5 proven presets (swap the `.line` block) — same 5 as the skill's Text policy

### Beast — white + thick black stroke (default)
```css
.line { color:#fff; -webkit-text-stroke:14px #000; paint-order:stroke fill;
        text-shadow:0 8px 0 rgba(0,0,0,.35), 0 14px 24px rgba(0,0,0,.55); }
```

### Fire — yellow→orange→red gradient
```css
.line { -webkit-text-stroke:14px #1a0a00; paint-order:stroke fill;
        background:linear-gradient(#FFE24B 0%, #FF9A1F 45%, #FF2E2E 100%);
        -webkit-background-clip:text; background-clip:text; color:transparent;
        filter:drop-shadow(0 0 22px rgba(255,120,0,.55)) drop-shadow(0 10px 0 rgba(0,0,0,.4)); }
```

### Neon Lime — acid lime + glow
```css
.line { color:#D4FF3F; -webkit-text-stroke:12px #0a1400; paint-order:stroke fill;
        text-shadow:0 0 26px rgba(180,255,40,.7), 0 10px 0 rgba(0,0,0,.4); }
```

### Clean Glass — Inter 800 on a frosted pill
```css
#headline { font-family:'Inter',sans-serif; }
.line { font-weight:800; color:#fff; letter-spacing:-0.02em;
        background:rgba(20,20,25,.45); backdrop-filter:blur(16px);
        padding:.12em .5em; border-radius:.2em;
        box-shadow:0 20px 60px rgba(0,0,0,.5); }
```

### Marker — black Anton on lime line-boxes
```css
.line { color:#0a0a0a; background:#D4FF3F; box-decoration-break:clone;
        padding:0 .18em; box-shadow:0 8px 0 rgba(0,0,0,.5); }
```

## Layer 2 — bake to PNG (canvas)

The same look, re-rendered in canvas at native resolution — a clean PNG, zero dependencies.
**Important: wait for the font to load (`document.fonts.load`) BEFORE the first draw, or it
bakes the system font.**

```html
<canvas id="c"></canvas>
<script>
async function bake({ src, lines, W, H, out='baked.png' }) {
  // 1) load Anton BEFORE drawing
  const fontLink = document.createElement('link');
  fontLink.rel = 'stylesheet';
  fontLink.href = 'https://fonts.googleapis.com/css2?family=Anton&display=swap';
  document.head.appendChild(fontLink);
  await document.fonts.load('120px "Anton"');
  await document.fonts.ready;

  // 2) background
  const img = new Image();
  img.crossOrigin = 'anonymous';        // else toDataURL fails on CORS (for URLs)
  await new Promise((res, rej) => { img.onload = res; img.onerror = rej; img.src = src; });

  const cv = document.getElementById('c');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  // cover-fit the image
  const s = Math.max(W / img.width, H / img.height);
  const dw = img.width * s, dh = img.height * s;
  ctx.drawImage(img, (W - dw) / 2, (H - dh) / 2, dw, dh);

  // 3) text
  const fontPx = Math.round(H * 0.16);   // ≈16% of frame height
  const lineH  = fontPx * 0.9;
  const stroke = Math.round(fontPx * 0.11);
  ctx.font = `${fontPx}px "Anton"`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  ctx.letterSpacing = '-2px';            // tight tracking (Chrome/Edge)

  const cx = W / 2;
  const totalH = lines.length * lineH;
  let y = H * 0.94 - totalH + lineH;     // block pinned to the bottom, comfortable margin

  for (const ln of lines) {
    // hard shadow
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.55)';
    ctx.shadowBlur = 24; ctx.shadowOffsetY = 14;
    // paint-order: stroke FIRST
    ctx.lineWidth = stroke;
    ctx.strokeStyle = '#000';
    ctx.lineJoin = 'round';               // no sharp spikes on thick-stroke corners
    ctx.miterLimit = 2;
    ctx.strokeText(ln.text, cx, y);
    ctx.restore();

    // fill on top (white / gradient)
    if (ln.gradient) {
      const g = ctx.createLinearGradient(0, y - fontPx, 0, y);
      ln.gradient.forEach(([stop, col]) => g.addColorStop(stop, col));
      ctx.fillStyle = g;
    } else {
      ctx.fillStyle = ln.color || '#fff';
    }
    ctx.fillText(ln.text, cx, y);
    y += lineH;
  }

  // 4) export
  cv.toBlob(b => {
    const a = document.createElement('a');
    a.download = out; a.href = URL.createObjectURL(b); a.click();
  }, 'image/png');
}

// example call
bake({
  src: 'photo.jpg',
  W: 1280, H: 720,
  lines: [
    { text: 'I SPENT', color: '#fff' },
    { text: '100 DAYS', gradient: [[0,'#FFE24B'],[0.5,'#FF9A1F'],[1,'#FF2E2E']] },
  ],
});
</script>
```

Mechanics that are easy to forget:
- **`strokeText` before `fillText`** — stroke under fill (the equivalent of `paint-order: stroke fill`).
- **`document.fonts.load(...)` + `await document.fonts.ready`** before the first draw — else the first frame bakes the system font.
- **`lineJoin='round'`** — removes sharp artifacts on the corners of a thick stroke.
- **`img.crossOrigin='anonymous'`** only when the background is a URL; for a local file
  (`<input type=file>` → `URL.createObjectURL`) it isn't needed and CORS doesn't block.
- Draw the shadow inside `save()/restore()`, else `shadowBlur` bleeds onto the fill and smears the color.

## 4K / retina export

For a sharp PNG larger than the preview, compute everything from the image's NATIVE size,
not from the preview viewport:

```js
bake({ src: '4k_render.png', W: 3840, H: 2160, lines: [...] });
```

Cap size, stroke and margins are all tied to `H` (in percent), so at 2160px everything scales itself.

## Font menu (Anton is the default — these are the overrides)

If the user asks for a different font, pick from this menu (all on Google Fonts, so they
load through the same mechanism as Anton). Named font → use it; "something else / not Anton"
→ pick the closest fit below and say which you chose.

**A — Top 3 on YouTube (punchy display, the Anton alternates)**

| Font | Google Fonts weight | Vibe / use |
|---|---|---|
| Bebas Neue | 400 (reads bold) | tall narrow ALL-CAPS — the #1 Anton alternative, maximum cap height |
| Oswald | 600–700 | condensed grotesk, a touch softer than Anton |
| Archivo Black | 400 (ultra-bold) | blocky, wide, very loud headline |

**B — 5 most-used bold workhorses**

| Font | Weight | Vibe / use |
|---|---|---|
| Montserrat | 900 (Black) | clean geometric sans, modern headline |
| Poppins | 800 (ExtraBold) | rounded geometric, friendly |
| Roboto Condensed | 700 (Bold) | neutral condensed workhorse |
| Inter | 800 | modern UI sans (same face as the Clean Glass preset) |
| Barlow Condensed | 800 (ExtraBold) | condensed, energetic |

**C — 5 aesthetic (girls' vlogs / soft-elegant)**

| Font | Weight | Vibe / use |
|---|---|---|
| Playfair Display | 700–900 | elegant high-contrast serif — classic "aesthetic" title |
| Cormorant Garamond | 600–700 | delicate refined serif, editorial feel |
| DM Serif Display | 400 | high-end display serif |
| Fraunces | 600–900 | soft "old-style" serif, trendy |
| Sacramento | 400 (script) | handwritten script — ACCENT / secondary line only, never the hero word (a script fails the ~120px legibility test as the main headline) |

**How to swap (keep everything else):**
- HTML/CSS: `#headline { font-family: '<Family>', sans-serif; }` and set `.line { font-weight: <w>; }`; update the Google-Fonts `<link>` to that family.
- Canvas: `await document.fonts.load('120px "<Family>"')` and `ctx.font = \`<weight> ${fontPx}px "<Family>"\``.
- Stroke / shadow / `paint-order` / tracking stay as in the presets — only the family (and weight) change.

**Stroke caveat by font class:** heavy condensed faces (Anton, Bebas Neue, Oswald, Archivo Black)
take the full 8–14% stroke. The delicate serifs and the script (Playfair, Cormorant, DM Serif,
Fraunces, Sacramento) CLOG with a thick stroke — drop it to 3–6% (or none) and lean on a soft
drop-shadow for separation instead. Sacramento (and any script) is an accent line, not the punch word.

## Quick check before baking

- [ ] Font **Anton**, ALL CAPS, 2–4 words.
- [ ] Stroke manual and **thick**, drawn under the fill (`paint-order` / `strokeText` first).
- [ ] Text does **not** cover the face; sits in a free quarter.
- [ ] Text within the frame, off the extreme edges (comfortable padding).
- [ ] One punchy color: white / fire gradient / lime — one per headline.
- [ ] Waited for the font to load before `fillText`.
