# Interaction rules

The illustration plays its intro (draw-on, then the hero's move), then becomes something the user can handle.
Interaction turns on only after the intro lands.

## One hero, the rest still

- Name the hero before building: the one part that carries the message. It is the `hi` part. If the object has a
  control that drives another part (a camera's shutter button drives the lens and shutter), the control is the hero:
  hover is the half-press (the lens hunts focus), click is the full press (the shutter fires).
- **The hero can be a family** of identical parts that each work the same way: the keys of a keyboard, piano keys,
  buttons on a panel, drawers in a cabinet. Then every member answers the pointer, one at a time (hover presses or
  opens the one under the pointer; click does its full action). One member may carry the `hi` tone as the accent
  (the keyboard's Enter); the rest keep their tones. The frame or case still stays still.
- Only the hero has its own response. Every other part moves only with the whole object, when the user turns or
  zooms the view.
- The hero's response is what the real part does when touched or approached:

| Object | Hero | Hover | Click or tap |
|---|---|---|---|
| Camera | shutter button | half-press: the focus ring hunts | the shutter fires, the lever winds on |
| Compass | needle | turns toward the pointer, like a magnet, on the spring | swings off about 90° and settles back |
| Safe / chest | lid | lifts a little, as if unlatched | opens fully, then closes |
| Key | key | turns a quarter in the lock | turns fully and back |
| Keyboard | every key (a family), Enter as the `hi` accent | the key under the pointer presses down on the spring | its cap lifts to show the switch, then drops back |
| Balance | beam | tips toward the side under the pointer | swings and settles level |
| Theodolite | alidade and telescope | turns to sight the pointer | sweeps a bearing and returns |

  If the hero has no natural response, choose another hero or another object.
- On leave, the hero springs back to rest.

## Turning and zooming the view

- **Turn:** a click-drag, or a one-finger drag on touch, orbits the camera around the object. Clamp azimuth to ±40°
  and elevation to 15° to 60° around the rest view, and damp it with the spring. On release the view stays for
  about 2 s, then springs back to rest, so the drawing always returns to its composed view.
- **Zoom:** the wheel or a two-finger pinch, 0.8× to 2.5×, toward the pointer (orthographic zoom plus a pan). Lines
  stay 1 px at every zoom. A double-click or double-tap resets the view.
- **Do not fight the page.** On a full-screen illustration the wheel may zoom. On an illustration embedded in a
  scrolling page, the wheel zooms only with Ctrl or a pinch (the kernel does this under `?embed=1`), so scrolling still
  scrolls. Put `touch-action: none` on the canvas only.

## Hit testing

Raycast against the hero's fill mesh. Give it a generous, invisible hit area (a disc over the compass card, a box
around a key), so a thin part is easy to catch.

## Hints

The cursor is the only hint: `grab` / `grabbing` over the object, `pointer` over the hero. No text, tooltips,
handles or UI chrome.

## Reduced motion

Direct manipulation still works (the user is driving it), but with no springs or overshoot: the hero snaps to its
target and the view stays where it was left.

## In the kernel

Figures are built on the kernel (https://linejig.com/kernel/linejig.js), which wires orbit, zoom, hit testing, cursors and reduced motion.
The figure registers hit areas while it draws (`K.hit(id, poly)`, nearest last) and names its hero:

```js
HERO: { onHover(id, p, K) {}, onLeave(id, K) {}, onClick(id, p, K) {}, action: 'compose', opened(st, K) {} }
```

`id` is the hit area's id, so a family hero gets one per member. `K.hover` and `K.pointer` are there each frame for a
hero that follows the pointer (the needle, the focus ring).

## The action event

A hero's click can hand off to the host page: an empty state's "compose", an onboarding step's "continue". Give the
hero `action: '<id>'` and `opened(st)`, true once its move reaches its open state (the lid open, the cap lifted).
At that moment the kernel posts `{type: 'action', id, figure}` to the parent when embedded, and dispatches a
`linejig:action` CustomEvent on the window when standalone. Without `opened`, it fires one tween (700 ms) after
the click. The host owns the words (the gallery shows the manifest's `action.label` as a button); the drawing never
does.

## Turntable mode

`?mode=turntable`, or the `mode` message: no hand, and after the intro the object turns slowly about its vertical
axis, ±35° over 40 s (or one full turn in 40 s with `turntable: 'full'`, only for a figure whose back is finished).
For loading screens and screen-recorded loops. Reduced motion holds it still.

## Open finished, click from the host, keyboard

- `?intro=none` (any figure) opens the figure finished and live, with no intro played. `def.intro: 'none'` and
  `fig.setIntro('none')` do the same. With none, `?freeze=MS` counts from the finished state. `none` is never listed in
  the `intros` the figure reports, so menus built from that list stay as they were.
- Embed message in: `{type: 'click', id?}` clicks the hero as a pointer press would (id defaults to the hero), and
  `{type: 'intro', value: 'none'}` jumps to the finished figure. The `ready` message carries `click: true`, so a host
  can check for the click message before relying on it.
- The `createFigure` result has `setIntro(name | 'none')` and `click(id?)`. A def can carry `name` (used for the
  aria-label) and `HERO.label` (the action's wording).
- Keyboard: a figure with `HERO.action` that is interactive and takes pointer events is a button. Tab focuses it and
  shows the hover state with a 2 px ink focus ring around the object; Enter or Space clicks; Escape or blur leaves.
  Turntable, freeze and `pointer-events: none` hosts get no tab stop. A cross-origin host that disables pointer events
  on the iframe should also set `tabindex="-1"` on it.
