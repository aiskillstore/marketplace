# Writing a clip

A clip is a small HTML fragment in `motion/clips/NN-name.html`. `engine/build.py` wraps it with the engine, fonts and a cursor into one self-contained page, where `seek(t)` draws the frame at time `t`. Every style is a pure function of `t`: no CSS transitions, no timers, no state carried between frames. That is what makes frame-by-frame rendering with motion blur possible.

## Fragment skeleton

```html
<title>04 Master prompt</title>
<style>/* clip-specific CSS */</style>

<div data-slot="world">  <!-- optional: elements beside the shape (a drop target, a folder tab) --> </div><!--/world-->
<div data-slot="shape">
  <!-- one layer per state; .L layers are anchored inside the shape -->
  <div class="L" id="Lnotes"> … </div>
  <div class="L" id="Ldoc"> … </div>
</div><!--/shape-->

<script>
M.scene({
  W:1920, H:1080, T:10,            // frame size (match the video) and clip length in seconds
  bg:'#E9E7E2',                    // canvas colour; null = transparent (panel clip → render to .mov)
  center:[960,540],                // screen point the camera centres on (move it for panels)
  intro:0.15,                      // shape pops in at this time; null = already on screen
  SH:{                             // the states the one shape morphs through
    notes:{w:780,h:560,r:36,bg:'#FFFFFF',cam:1.3},
    doc:{w:600,h:720,r:28,bg:'#FFFFFF',cam:1.2},
  },
  start:'notes', SEQ:[[5.1,'doc']],               // [clip-local time, state] – put each on its word
  layers:[
    {el:'Lnotes', tin:0.15, tout:5.1, anchor:'t'}, // anchor 'c' centre (default), 't' top-centre, 'l' left-centre
    {el:'Ldoc', tin:5.1, tout:null, anchor:'t', update:(t,g)=>{ /* per-frame content, e.g. typing */ }},
  ],
  cursor:{size:44, clicks:[2.3], drags:[[6.9,7.8]], keys:[[0,760,460],[1.2,760,460],[1.9,330,250]]},
  geom:(t,g)=>g,     // optional: change geometry (e.g. follow the cursor while dragged, g.fx/g.fy camera focus)
  extra:(t,g)=>{},   // optional: per-frame work outside layers (world elements, indicators)
});
</script>
```

Coordinates are **world pixels**. The shape is centred at world (0,0) unless `geom` moves it (`g.cx`, `g.cy`). The camera draws world → screen as `center + cam × (world − focus)`. Choose `cam` per state so the state fills the frame: roughly 1.2–1.6 for cards, 1.8–2.2 for pills. The cursor keeps a constant size on screen.

Layer content is positioned relative to its anchor, e.g. `left:-330px; top:40px` inside an `anchor:'t'` layer = 330px left of centre, 40px below the shape's top edge. Top-anchored content rides the top edge when the shape grows.

## Engine API (`window.M`)

| Call | What it does |
|---|---|
| `M.track(v0, [[t, value, spring?], …])` | A value that changes target many times: the sum of one closed-form spring per change. Returns `t => value`. |
| `M.ctrack('#hex', [[t,'#hex'], …])` | The same for colours. Returns `t => 'rgb(...)'`. |
| `M.MORPH`, `M.FAST`, `M.SLOW`, `M.SOFT`, `M.CAM`, `M.INSTANT` | Spring presets `[stiffness ω, damping ζ]`. FAST/SLOW for leading/trailing edges; INSTANT for invisible resets. |
| `M.vis(t, tin, tout, {din, lin, lout})` | Content swap: exit blurs out fast, enter waits `din` then blurs in over `lin`. Returns `{o, blur, s, a, b}`. |
| `M.apply(el, v)` | Applies a `vis` result to an element (opacity, blur, scale). |
| `M.path([[t,x,y], …])` | Cursor or any point path, eased between keys with a slight human arc. |
| `M.crossTimes(f, t0, t1, thresholds)` | When a rising value first crosses each threshold. Use it to trigger springs from a dragged value. |
| `M.icon(name, size, colour, strokeW?)` | Icon from the set in `M.IC`, with stroke normalised so all icons match. |
| `M.setText(el, s)` | Set text only when it changed (cheap per frame). |
| `M.eo`, `M.eio`, `M.clamp`, `M.lerp`, `M.S` | Easing and spring helpers. |

Icons in `M.IC`: arrow, check, x, plus, folder, terminal, file, pencil, coin, clock, chip, sparkle, castle, search. Add more as 24-grid stroke paths (e.g. from Lucide, ISC licence).

## Patterns (see `examples/opus-aoe2/`)

| Pattern | How | Example |
|---|---|---|
| Pill → card → control | SH states + layers with tin/tout | 01 |
| Liquid indicator | Two `M.track`s for left/right edges; the edge moving forward uses `M.FAST`, the trailing one `M.SLOW` | 01 (levels), 02 (effort) |
| Typing | `PROMPT.slice(0, n)` with `n` from time, and a caret | 02 |
| Rows or bars appearing on words | Per-row `M.vis(t, wordTime, …)` + width or height from a spring | 02, 04, 05 |
| Direct manipulation | While the cursor is held, the value comes from its position; on release it springs from where it was | 03 (slider) |
| Drag and drop | `geom` sets `g.cx/cy` from the cursor while held; a world-slot drop target; `g.fx` moves the camera focus | 04 |
| Transparent panel | `bg:null`, `center` in the empty area, light shapes | 02 |

## Interaction vocabulary

Map what the speaker says onto these:
- primary action (pill + click)
- progress (loader, bars, lanes)
- confirmation (check, toast)
- live status (island)
- detail card with a drag
- slider with rubber band
- toggle
- tabs
- chart with tooltip
- search and filter list
- file → drag → drop target
- terminal typing
- side-by-side comparison
- chapter card

## plan.json

```json
{
  "title": "Opus 5.5 · Age of Empires II",
  "video": "work/source.mp4",
  "fps": "30000/1001",
  "clips": [
    {"id":"01","title":"Opus 5.5 drop","line":"“Opus 5.5 just came out …”","in":0.30,"out":6.75,"kind":"full","file":"out/01-opus-drop_0m00s30.mp4"},
    {"id":"02","title":"Folder → Claude Code → four builds","line":"“I created a blank folder …”","in":6.75,"out":22.5,"kind":"panel","file":"out/02-pip-builds_0m06s75.mov"}
  ],
  "notes": ["The typed prompt and the cost/time/tokens bars are illustrative."]
}
```

Paths are relative to `plan.json`. `out` is when the clip leaves the timeline; if the clip is shorter, the composite holds its last frame.
