# Prompts behind the kept samples — variant pen (速写本 · 细笔)

Every sample: Qwen-Image 2.1 Q6 on ComfyUI, euler / simple, 20 steps, CFG 1.0, 1024×1024, then `scripts/inkpost.py`.

Rounds: r1 tested CFG 1 vs CFG 3 + negative (CFG 3 heavier, 2× slower — rejected). r2 introduced CORE + sub-style blocks. r3 added "0.8 mm felt-tip" for B and a D block. r4 replaced CORE with the scrappier wording now in SKILL.md and fixed D. Samples from r2/r3 used the earlier CORE; regenerate with the current CORE for new work.

## A · Bold marker object study

### A-01-steam-engine (source run r2-steam-A, seed 22, 120 s)

```
A small stationary steam engine: a spoked flywheel, a horizontal cylinder and a chimney, on a plinth. Drawn with a thick black felt-tip marker: heavy uneven outlines, chunky bold simplified forms, the object fills the page and is cropped by the page edge, a few areas filled solid black with thin white highlight stripes left unfilled. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines of even medium weight, a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### A-02-jet-engine (source run r3-jet-A, seed 31, 120 s)

```
A jet engine seen from the front three-quarter, big round intake with fan blades, chunky nacelle, redesigned as a simple retro-futurist object. Drawn with a thick black felt-tip marker: heavy uneven outlines, chunky bold simplified forms, the object fills the page and is cropped by the page edge, a few areas filled solid black with thin white highlight stripes left unfilled. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### A-03-camera (source run r4-camera-A, seed 41, 119 s)

```
A chunky retro camera with a big round lens, a flash window and a shutter button, seen from three-quarter above. Drawn with a thick black felt-tip marker: heavy uneven outlines, chunky bold forms, drawn too big for the page so one side runs off the edge, a few areas filled solid black with thin white highlight stripes left unfilled. Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### A-04-webb-telescope (source run r4-webb-A, seed 45, 120 s)

```
The James Webb space telescope: a big honeycomb mirror of hexagons, a secondary mirror on three struts, stacked sunshield layers below. Drawn with a thick black felt-tip marker: heavy uneven outlines, chunky bold forms, drawn too big for the page so one side runs off the edge, a few areas filled solid black with thin white highlight stripes left unfilled. Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

## B · Fine-pen construction study

### B-01-tokamak (source run r3-tokamak-B, seed 33, 117 s)

```
A tokamak fusion reactor simplified into a chunky doughnut ring wrapped by eight D-shaped magnet coils, a quarter cut away to show the hollow inside, small pipes and a ladder at the base for scale. Drawn with a 0.8 mm black felt-tip pen: firm dark lines of even weight, no thin faint lines, three-quarter view from slightly above, two or three perspective construction lines extending past the object. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### B-02-kettle (source run r4-kettle-B, seed 44, 117 s)

```
An electric kettle with a round dial and a water-level window, drawn twice: one big three-quarter view and one small side view. Drawn with a 0.8 mm black felt-tip pen: firm dark lines, no thin faint lines, three-quarter view from slightly above, two or three perspective construction lines extending past the object. Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### B-03-jet-engine (source run r2-jet-B, seed 21, 119 s)

```
A turbofan jet engine with its side cowling opened, fan blades at the front, simplified into a few big parts. Drawn with a 0.5 mm black fineliner: three-quarter view from slightly above, a few faint perspective construction lines extending past the object. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines of even medium weight, a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

## C · Annotated function / UI page

### C-01-fusion-console (source run r3-console-C, seed 35, 120 s)

```
Ideas for a control panel of a fusion reactor: three small wireframe screens drawn as boxes with lines and dials, a row of chunky switches, a big round gauge, handwritten notes 'plasma temp', 'coil current', 'too many buttons?' and arrows. Drawn with a 0.8 mm black felt-tip pen, firm dark lines, with short handwritten notes in messy lowercase English and arrows pointing at parts. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### C-02-webb-notes (source run r2-webb-C, seed 23, 118 s)

```
The James Webb space telescope: hexagonal gold mirror segments drawn as a honeycomb of outlines, the layered sunshield below. Handwritten labels 'mirror', 'sunshield', 'L2 ->'. Drawn with a 0.5 mm black fineliner, with short handwritten notes in messy lowercase English and arrows pointing at parts. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines of even medium weight, a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

## D · Thumbnail scatter page

### D-01-small-electronics (source run r4-radios-D, seed 43, 118 s)

```
Ideas for small electronics: pocket radios, a cube speaker, a cassette recorder, an alarm clock, a handheld game console, a walkie-talkie with an antenna, headphones. Drawn with a 0.8 mm black felt-tip pen: twenty to thirty tiny thumbnail sketches of different shapes and types, no two alike, mixed sizes from very small to medium, tilted at different angles, scattered unevenly across the page like a brainstorm, not in a grid, some with a hatched side or a solid black part, two tiny handwritten words. Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### D-02-space-hardware (source run r4-rockets-D, seed 42, 121 s)

```
Ideas for space hardware: slim rockets, round satellites with solar panels, space telescopes with dish mirrors, small landers on legs, a space helmet. Drawn with a 0.8 mm black felt-tip pen: twenty to thirty tiny thumbnail sketches of different shapes and types, no two alike, mixed sizes from very small to medium, tilted at different angles, scattered unevenly across the page like a brainstorm, not in a grid, some with a hatched side or a solid black part, two tiny handwritten words. Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

## E · Small scene

### E-01-desk (source run r3-desk-E, seed 38, 118 s)

```
A desk with a boxy computer terminal, a potted plant with a few leaves, a desk lamp and a small radio. Drawn with a 0.8 mm black felt-tip pen: firm dark lines of even weight, a small corner of a room, simplified, objects drawn as simple boxes and cylinders. Page from a product designer's daily sketchbook, drawn quickly in black ink on plain white paper. Simplified, slightly naive shapes, boxy forms with rounded corners. Outlines a little wobbly, overshooting at the corners. A few loose diagonal hatch lines on one side only; cross-hatching only inside speaker grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. Few lines, no feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

### E-02-person-radio (source run r4-person-E, seed 46, 119 s)

```
A person sitting cross-legged on the floor, tuning a big boxy radio with an antenna, seen from the side. Drawn with a 0.8 mm black felt-tip pen: firm dark lines, simplified, objects drawn as simple boxes and cylinders, no background. Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```
