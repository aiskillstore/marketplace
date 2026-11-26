# Using it with what you already have

Two common starts: a product built on a component library, and an illustration or SVG the user already has. Both
end in an ordinary figure on the kernel, so every rule in `SKILL.md` still holds. This file names only settings the
kernel really has; its header comment (https://linejig.com/kernel/linejig.js) is the authority.

## On top of a component library (shadcn/ui and similar)

A figure is a small page. Either embed a gallery figure (`https://linejig.com/<id>/index.html`) in an iframe, or
build a figure page of your own on the kernel and serve it from the project. Either way the host talks to it through
the address and through messages.

### Theme tokens to plate and ink

| Kernel input | Where it comes from | How to pass it |
|---|---|---|
| Plate (the ground every face is filled with) | the surface the figure sits on: `--card` inside a Card, `--background` on the page, `--muted` in a muted well | `?plate=<light>,<dark>`: two six-digit hex values without `#`, light then dark (defaults `f7f7f8,111111`) |
| Ink (`hi`, `edge`, `mid`, `lo`) | nothing: keep the kernel's grey ramp | not an address setting |
| Style | line art, the default, or Brand, Dots, Readout or Pencil with the brand colour from `--primary` once the user confirms it (`SKILL.md`, "Style") | `?style=<id>` and `?brand=<hex>` |

- Tokens are often OKLCH or HSL (`--primary: oklch(0.205 0 0)`). The kernel takes hex, so convert the computed colour
  (in the browser, `getComputedStyle(el).backgroundColor` on an element that uses the token gives `rgb(...)`; turn
  that into hex) for both the light and the dark theme.
- **Ink stays grey.** The tones are measured for contrast against the plate, so do not tint them to the page's
  foreground. On a figure page you own, they are the CSS variables `--hi --edge --mid --lo` from `linejig.css`;
  override them only if the user asks, per theme, keeping `hi > edge > mid > lo` in contrast against the plate, and
  measure the rendered pixels.
- `?plate=` is read once at load, in an iframe page. To change the plate later, reload the frame with a new address.

### Sizing in cards

- The drawing fits a 5:4 plate inside whatever box it gets; 400 by 320 is the natural shape and any other shape adds
  margin. In a card, give the frame `width: 100%; aspect-ratio: 5 / 4; border: 0` and let the card's padding frame it.
- Keep `embed=1` on every embed: the wheel and a vertical swipe then scroll the page instead of zooming the object.
- Add `loading="lazy"` and a `title` that names the object. Each frame is its own WebGL context, so keep three or
  four live figures per page at most and show a still for the rest.
- The figure never draws words. Headings, body text and the call to action are the card's: put the label of the
  hero's action on a Button in the card footer, and also run it when the figure posts `action`.

### Dark mode

- Without `?theme=` a figure follows the visitor's system setting. shadcn/ui (and most `next-themes` setups) switch
  with a `dark` class on `<html>` instead, so the figure must be told: start it with `?theme=light` or `?theme=dark`
  from the current class, and post `{type: 'theme', value}` whenever the class changes.
- Post only after the figure has sent `ready`, and always to the origin `https://linejig.com` (or your own origin
  for a self-hosted figure page). Check `e.origin` and `e.source` on everything you receive.

### A React component, as a sketch

```jsx
import { useEffect, useRef } from 'react';

const ORIGIN = 'https://linejig.com';
const hex = (rgb) => rgb.match(/\d+/g).slice(0, 3).map((n) => (+n).toString(16).padStart(2, '0')).join('');

export function LinejigFigure({ id, title, plate = 'f7f7f8,111111', style = 'lineart', brand, onAction }) {
  const ref = useRef(null);
  const dark = () => document.documentElement.classList.contains('dark');
  useEffect(() => {
    const frame = ref.current;
    const send = (m) => frame?.contentWindow?.postMessage(m, ORIGIN);
    let ready = false;
    const onMessage = (e) => {
      if (e.origin !== ORIGIN || e.source !== frame.contentWindow) return;
      if (e.data.type === 'ready') { ready = true; send({ type: 'theme', value: dark() ? 'dark' : 'light' }); }
      if (e.data.type === 'action') onAction?.(e.data.id);
    };
    const watch = new MutationObserver(() => ready && send({ type: 'theme', value: dark() ? 'dark' : 'light' }));
    watch.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    addEventListener('message', onMessage);
    return () => { removeEventListener('message', onMessage); watch.disconnect(); };
  }, [onAction]);
  const q = new URLSearchParams({ embed: '1', style, plate, theme: dark() ? 'dark' : 'light' });
  if (brand) q.set('brand', brand.replace('#', ''));
  return <iframe ref={ref} src={`${ORIGIN}/${id}/index.html?${q}`} title={title} loading="lazy"
    style={{ width: '100%', aspectRatio: '5 / 4', border: 0 }} />;
}
```

Use it inside a Card's content, with the words in the card and the action on a Button:
`<LinejigFigure id="empty-inbox" title="Letter tray" plate="ffffff,0a0a0a" onAction={openComposer} />`. `hex()`
turns a computed `rgb(...)` into the six digits the address wants. The `plate` values here are examples:
read the real ones from the project's tokens.

## Starting from the user's own illustration or SVG

The kernel draws only its own primitives: footprints extruded into rounded prisms (`K.rrect`, `K.circ`, `K.box`,
`K.turn`, then `K.solid`) and raw lines (`K.add`). It has no SVG import and no image tracing, so the user's artwork is
a reference you read and rebuild by hand, never a file the kernel loads.

1. **Check the source.** Use the user's own drawing, or one they have the right to use. Never trace a generated
   picture (`SKILL.md`, "What stays out").
2. **Name the object and its parts.** What is it, what are its 8 to 12 parts, and which outline features make it
   recognisable at thumbnail size? Drop every word, number, logo, texture, gradient and small detail in the source.
3. **Rebuild each part as a footprint.** A rectangle or rounded rectangle becomes `K.rrect` (or `K.box` for a part
   with a bevel), a circle becomes `K.circ`, a turned shape gets `K.turn`. For a free-form outline, sample the path
   into points and build a ring of `{ u, v, nu, nv }` (position and outward normal), the footprint format the kernel
   uses. Give each part a height (`w0`, `w1`) and a frame (`K.axes`), since an SVG is flat and the figure is not.
4. **Place it in the one camera.** The view is always the 2:1 axonometric; a front-on SVG is redrawn in it, not
   kept front-on. Set `fit.points` to the most extreme pose.
5. **Choose the hero part.** The part the message is about (`references/styles.md`, "Which part takes the colour"):
   it is the `hi` part. Drop the source's colours; the drawing is white, black and grey.
6. **Give it hover and click.** Register its hit area with `K.hit(id, poly)` (the silhouette `K.solid` returns works),
   give `HERO` its `onHover`, `onLeave` and `onClick` with the move the real part makes (`references/interaction.md`),
   and an `action` with `opened(st)` if a click should hand off to the host page.
7. **Plan the intro** with an `ASSEMBLY` table (`references/motion.md`, "Planning the stack"), then render and check
   it like any other figure (`references/verify.md`), side by side with the source so the user can compare.
