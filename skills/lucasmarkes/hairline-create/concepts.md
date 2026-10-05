# From an idea to a concept

A concept is three things: **an object**, **what the pointer does to it**, and **what the read-out says**. It fits on one line. If it does not, it is not ready to build.

## Finding it

1. **Find the object.** Something you could put on a desk: a tray, a belt, a platter, a stack, a board of pegs. Not a diagram. A deploy pipeline is not boxes and arrows; it might be a flight of canal locks.
2. **Find what gives it away.** For each kind of part, name the two or three features that make it what it is, each something the object would really have. A car: a cabin narrower than its body, a windscreen that slopes, wheels. A lighthouse: a tower that tapers, a lantern on top, a gallery round it. A part with none of them is a rounded block, and a row of rounded blocks is nothing in particular. Keep the list: you draw from it, and the look checks the small picture against it.
3. **Find the variable.** Every idea has one number or one choice that matters: how far, which one, how fast, how long. That is what the pointer gets.
4. **Give the pointer that variable.** Where it is sets a position (continuous); what it is over sets a choice (discrete). The answer should be what a hand would expect from the object.
5. **Design the rest.** What does the object look like when nobody touches it? It must already be a composition, and already say what the figure is about.
6. **Choose the read-out's words.** A few characters naming what is under the pointer: `cell 4·2`, `08`, `lock 3`. And `rest`.
7. **Choose the slider's number.** One number that makes the answer weaker or stronger: a radius, a stagger, a gap, a rate. Its three values go in `range`.

## Six answers already proven

The package's six figures each answer the pointer a different way. A new figure usually borrows one.

| Answer | In the package | The pointer | The clock | The slider |
| --- | --- | --- | --- | --- |
| **A field** | Terrain: pillars rise near the pointer | sets a position on the ground; height falls off with distance | a spring per part | the radius |
| **One of many** | Riffle: the card under the pointer stands up | picks an item; its neighbours part, staggered outwards | tweens | the stagger |
| **Scrub and pick** | Exploded: a window comes apart in layers | x scrubs the gap, y picks a layer, which gets the bright edge | a spring for the gap | the gap |
| **Paint and decay** | Phosphor: a dot matrix you can draw on | excites what it passes; the marks fade; an idle loop returns | a decay per dot | the afterglow |
| **Dilate time** | Slow: crates ride a belt through a gate | the world keeps moving, hovering slows it so it can be read | a spring on the rate | the rate |
| **Push the camera** | Turntable: a platter you flick round | pushes; friction bleeds the spin; detents catch it | friction, then a spring | the coast |

`examples/terrain.js` is the first and `examples/riffle.js` the second, in full.

## A weak concept

Drop it, or fix it before building, when:

- **It is dead at rest.** Nothing to look at until touched.
- **It needs words.** Without a label nobody would know what it is.
- **It holds more than one idea.** Two gestures, two variables, two objects.
- **The pointer has no reason.** The figure would be the same as a loop.
- **It is a diagram.** Boxes, arrows and lines between them are not an object.
- **It is an icon.** The literal symbol of the idea (a padlock for security) has nothing to answer with.
- **It depends on colour.** The palette is one stroke in four weights.
- **It will not read at 240px.** Too many parts, or parts too small.

## An example

For "a deploy pipeline":

> **Locks.** A flight of canal locks stepping down, each a basin. The pointer picks a lock; its gates open and its water drops to the next, staggered from the pointer. The read-out names the stage: `lock 3`.
>
> **Marble run.** A wooden frame with three ramps zigzagging down it, one ramp a stage, and marbles always rolling down them and lifted back to the top. The run never stops; hovering slows it so a marble can be followed, and the one under the pointer is bright. The read-out names its stage: `ramp 2`.
>
> **Cabinet.** A server cabinet of twelve blades, a few half out where the last update stopped. The pointer's height sets where the update is; the blades near it slide out, the farther the less, and the one under it is bright. The read-out names the slot: `blade 7`.

Each has an object, a gesture and a read-out; each is one idea; each is something at rest.
