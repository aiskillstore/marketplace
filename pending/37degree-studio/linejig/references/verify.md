# Verify

## Capture frozen frames

ES modules from a CDN work from `file://`, but if the page loads other local files, serve it:

```sh
python3 -m http.server 5391 --bind 127.0.0.1 &   # from the folder holding the page
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
  --window-size=1440,900 --virtual-time-budget=8000 --enable-logging=stderr --v=0 \
  --screenshot=/ABS/PATH/f-0700.png \
  "http://127.0.0.1:5391/index.html?freeze=700" 2>&1 | grep -i "CONSOLE"
kill %1
```

- Capture the start, middle and end of each move (for example `freeze=300`, `900`, `1600`) and the settled state
  (`freeze=4000`), plus `?reduced=1`.
- Capture at desktop width in both palettes (`--force-dark-mode`, or a `?theme=light|dark` hook on the page).
- Capture the click state with `?click=ID@MS` (the hero member's hit id, clicked at MS; it works under `?freeze`).
- Under the kernel, frames are driven by timers while `?freeze` is set and the hand never turns on, so drive hover
  and drag checks in the browser pane, not headless.
- **Blank frozen frames** in headless Chrome: create the renderer with `preserveDrawingBuffer: true` when
  `?freeze` is set, and render once more in a final `requestAnimationFrame`. The kernel does both. A frame PNG of
  only a few KB is blank; check before judging it.
- Headless Chrome will not size a window below about 500 px wide. Check phone width (375 × 812) in the browser pane
  with a viewport resize instead.
- Any `Uncaught` line in the console output is a failure. Ignore Chrome's own `cv_display_link` noise.

## Look for

- Lines all the same width, including at phone size and on high-density screens.
- One `hi` part only, and the tone ramp reading clearly: `hi` > `edge` > `mid` > `lo` (measure on real pixels).
- No part smaller than about 4% of the drawing's width; no stray detail.
- Near parts hiding far ones cleanly, with no lines showing through fills and no z-fighting on edges.
- The object inside the plate at every frame of the move.
- No text anywhere in the illustration.
- No horizontal scroll at 375 px.
