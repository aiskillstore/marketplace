---
name: gpuslider
description: Add an image or video slider, carousel or gallery with GPU shader transitions (liquid, burn, glitch…), effects under the pointer, or a lightbox, using gpuslider. Use when the user asks for a slider, carousel, hero slideshow, image gallery or lightbox in plain JS, React or Next.js, or for WebGL/WebGPU image transitions.
---

# gpuslider

A 4.7 KB image slider drawn on the GPU: WebGPU, else WebGL 2, else the page moves the slides, and without a script it scrolls and snaps. Layout is CSS; everything else is a plugin.

The full API ships with the package: read `node_modules/gpuslider/DOCS.md` before going past what is here. Do not guess option or effect names.

## Install

```sh
npm install gpuslider
```

## Plain JS

```html
<div class="gs" id="photos" aria-label="Photos">
	<div class="gs-track">
		<div class="gs-slide"><img class="gs-media" src="a.jpg" alt=""></div>
		<div class="gs-slide"><img class="gs-media" src="b.jpg" alt=""></div>
	</div>
</div>
```

```js
import { createSlider } from 'gpuslider';
import { controls, keyboard, stack } from 'gpuslider/plugins';
import { canvas } from 'gpuslider/canvas';
import { liquid } from 'gpuslider/effects';
import 'gpuslider/style.css';

createSlider( document.getElementById( 'photos' ), {
	loop: true,
	plugins: [ stack(), controls(), keyboard(), canvas( { effects: [ liquid() ] } ) ],
} );
```

## React and Next.js

`gpuslider/react` already says `'use client'` and renders on the server without layout shift.

```jsx
import { Slider, Slide } from 'gpuslider/react';
import { controls } from 'gpuslider/plugins';
import { canvas } from 'gpuslider/canvas';
import { stretch } from 'gpuslider/effects';
import 'gpuslider/style.css';

<Slider loop plugins={ [ controls(), canvas( { effects: [ stretch() ] } ) ] } aria-label="Photos">
	{ photos.map( ( p ) => (
		<Slide key={ p.src }><img className="gs-media" src={ p.src } alt={ p.alt } /></Slide>
	) ) }
</Slider>
```

Options of the core are props. `plugins` is read once, when the slider is made; pass `remake={ [ deps ] }` to make it again.

## What to pick

- **One slide at a time with a transition:** `stack()` plus one transition in the effects: `liquid`, `ripple`, `glitch`, `burn`, `pixelate`, `swirl`, `lens`, `fluted`, `warp`, `zoom`, `mosaic`, `blocks`, `fold`, `signal`, `push`, `chroma`, `kaleido`, `displace`, `datamosh`, `wind`, `distance`.
- **A row of slides:** no `stack()`; slides per view and gap are CSS (`--gs-per-view: 2.5; --gs-gap: 12px;`, in media queries for responsive) or `perView` / `gap`. Effects that move with speed: `stretch`, `split`, `jelly`, `bend`, `parallax`, `slab`. Layouts: `coverflow`, `fan`, `pile`, `wave`, `dome`, `unweave` (with `align: 'center'`).
- **Under the pointer:** `glass`, `waves`, `spotlight`, `magnify`, `pixels`, `reveal`, `tilt`, `smear`, `shift`, `cells`. Any number of effects combine, in the order given.
- **Lightbox:** `lightbox()` from `gpuslider/lightbox`.

## Rules

- Images on another origin need CORS for the canvas: `crossorigin="anonymous"` and a server that sends the header, or serve them from the same origin.
- Give the slides a height or an `aspect-ratio`. Never size or move `.gs-slide` from a script; the slider measures them.
- Squircle corners are CSS (`border-radius` with `corner-shape: squircle`); the canvas draws the same corners.
- Try it first without installing: https://stackblitz.com/github/niklasp/gpuslider/tree/main/examples/starter
- Docs: https://gpuslider.com/docs/
