# Infographic

**Use when:** the image has to carry drawn text — feature callouts, spec labels, dimension markers,
comparison halves, or whatever else this product needs spelled out.

## What this mode is

A product photograph with graphics drawn onto it that state what the picture alone cannot: feature
callouts, specs and dimensions, what is in the box, a before-and-after, a side-by-side comparison, a
how-to sequence. The graphics are part of the delivered image, not added afterwards.

**In frame:** the product, plus drawn text, lines, numbers or panels.
**Avoid:** text that only repeats what is already printed on the product; claims the brand cannot
stand behind; so much text that nothing is emphasised.

## Read the product first

Start from the object. From the reference, establish which physical parts a label could point at and
which of them are visible together from a single angle. Write the callout list before choosing the
camera angle, because the angle has to show every labelled feature at once.

## Prompt template

Two parts. The first is fixed and goes into every prompt unchanged. The second is what you write.

**Fixed — include whenever a reference photo is attached:**

    The attached image is the exact product. Do not modify, regenerate or redraw it. Its shape,
    colour, label, text, texture and design all stay as they are, and it keeps the state it is in —
    closed stays closed, open stays open. Build only the scene around it.

**Written — the scene only, in this order:**

This mode routes to `gpt-image-2`, which wants short labelled segments on separate lines rather than
one paragraph. Quote every string exactly as it must appear.

**Artifact type:** which kind of image this is — a labelled product, a dimension drawing, a contents
layout, a before-and-after, a side-by-side comparison, a how-to sequence. Naming the artifact buys
layout discipline that describing a scene does not.

**Shot type and camera angle:** the view, chosen so every feature a label points at is visible at
once.

**Background and lighting:** the surface behind the product, a broad soft key, and deep depth of
field so every landing point holds sharp. Strip the graphics off and it still has to read as a
product photograph.

**Copy:** the exact words drawn on the image, in quotes. A few words per label rather than a
sentence, eight labels at most — past eight the ranking flattens and nothing stands out over the rest.

**Label placement:** which physical part each label names, kept unobscured, and a text position clear
of every feature, never over the detail it names. Only point a label at a part you know it refers to.
Where you can't tell, ask the user rather than pointing at a guess.

**Leader lines:** short, crossing nothing, angled off horizontal and off vertical and off any product
edge beside them, ending on the feature with a level elbow under the label.

**Graphic style:** typeface, line weight and how the arrows terminate, held fixed across a set.

**Scale or comparison device:** for a size claim, an object the viewer already knows the size of,
placed in the product's plane. For halves or steps, they match in everything except the one thing
being compared.

Every claim drawn on the frame is one the brand can stand behind. No invented badge.

**Rules for the written part**

- Say nothing about the product itself — no colour, no material, no parts. The fixed block and the
  reference photo carry all of it.
- **Writing the light:**
  - Where it comes from and how it behaves, never what it reveals. A lighting sentence that reaches
    for a ridge, a grain, a seam, a pore, a scratch or a sheen has stopped describing light and
    started describing the product, and the surface gets redrawn to match it.
  - Position and size, never the fixture producing it. A softbox, strip, dish or stand written into
    a prompt is an object in the frame and will be rendered standing there. A source belonging to
    the scene — a window, a lamp, a candle — is set dressing and can be named.
  - One sentence per source, two sources at most. Each extra sentence is another opening for the
    product to get described.
- Concrete and named: "warm mid-grey seamless paper", not "a neutral background".
- Labelled lines, not one paragraph. Quote every drawn string exactly.
- Describe only what is visible from the angle you asked for.
