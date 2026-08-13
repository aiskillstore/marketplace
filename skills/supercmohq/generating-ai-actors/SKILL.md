---
name: generating-ai-actors
description: Generates one photorealistic person as a single image — an AI actor, influencer, presenter or model. The image is reusable, so passing it into any later generation brings the same face, hair and build back and one person can hold across a whole set of images or videos. Use when the user wants an AI actor, or when something needs a person and no photo of one was supplied.
license: Apache-2.0
metadata:
  version: "0.4.0"
  category: creative
  summary: "Casts a distinct, demographic-specific AI actor as a reusable identity reference, allowing you to reliably feature the exact same brand face across an entire multi-asset image and video campaign."
---

# The actor

Generate an image of an AI actor.

Anything the brief specifies wins. The defaults below fill gaps only.

## Workflow

### Step 1: Cast the person

An adult, always. Fill a younger brief with an adult and say so.

Keep casual words for young people out of the prompt altogether, even where the person described is
plainly an adult. They trip the image model's content filter and lose the generation.

Decide each of these deliberately rather than leaving it to the model, which returns the same face
every time.

**Who they are** — gender, age, ethnicity, build. An age anywhere from early twenties to late
sixties, a build anywhere from slight to athletic, broad or full.

**How they look.** This is what makes them recognisable when the image is reused, so it carries the
most weight. Take the face feature by feature.

**The examples below are a starting point, not the choices on offer.** Reach past them, decide each
line separately, and don't cast the same combination twice.

- **Face shape, jaw and chin** — oval, square, heart, long, round, diamond, oblong, pear, inverted
  triangle. The jaw strong and angular, or soft and tapered. The chin with a deep cleft or a subtle
  dimple.
- **Cheekbones** — high and sharp, soft and low, broad, prominent, sculpted, subtle and flushed,
  apple-cheeked, hollowed beneath, or slightly asymmetrical.
- **Eyes, shape and set** — almond, round, hooded, monolid, downturned, upturned, deep-set, wide-set,
  or close-set.
- **Eyes, colour** — emerald green, stormy grey, hazel with gold flecks, amber, pale ice blue, deep
  mahogany brown, heterochromia, violet-blue, moss green, or near-black.
- **Eyebrows** — thick and bushy, neatly arched, thin and straight, feathered and wild, bleached,
  dark and heavy, soft and sparse, subtly unibrowed, sharp and angular, or softly rounded.
- **Nose, bridge and tip** — straight, aquiline, upturned, wide and flat, snub, button, Roman,
  bulbous-tipped, or slightly crooked from a healed break.
- **Mouth** — full evenly, thin on top and full on the bottom, wide and generous, small and tight, a
  sharp Cupid's bow, a flat Cupid's bow, a resting smirk, downturned corners, slightly parted at
  rest, or soft and pillowy.
- **Skin texture and tone** — smooth and glass-like, visible pores, sun-weathered with deep crow's
  feet, scattered natural hyperpigmentation, subtle acne scarring, porcelain pale, rich deep bronze,
  rosy-cheeked, olive with gold undertones, or naturally dewy.
- **Hair, colour** — auburn, bright copper, honey blonde, icy platinum, salt-and-pepper, henna red,
  jet black, ash brown, silver-white, or a faded pastel wash.
- **Hair, length and how it's worn** — a military buzz crop, a jaw-length asymmetrical bob, a blunt
  shoulder cut, flowing past the waist, a shaved undercut, a messy top-knot, a slicked-back low bun,
  intricate protective braids, heavy blunt bangs, or a sweeping curtain fringe.
- **Hair, texture** — poker-straight, loose beachy waves, tight coiled ringlets, fine and flyaway,
  thick and heavy, coarse, silky, a soft frizzy halo, locs, or naturally bald.
- **Facial hair** — clean-shaven, a heavy five-o'clock shadow, a neatly trimmed goatee, a full thick
  beard, a pencil moustache, a handlebar moustache, a soul patch, scattered stubble, a sculpted
  chinstrap, or heavy mutton chops.
- **Glasses** — none, thick black acetate frames, thin round wire frames, rimless, browline frames,
  oversized geometric frames, tortoiseshell cat-eye, clear acrylic, vintage aviators, or subtly
  tinted lenses.
- **Makeup** — none at all, lip balm and brushed brows only, everyday concealer and mascara, sharp
  winged eyeliner, a bold matte red lip, a heavy smoky eye, graphic neon liner, fully contoured
  evening glam, a sheer lip tint, or faux freckles.
- **One distinguishing feature, or none** — freckles dusted across the nose, deep cheek dimples, a
  small silver septum piercing, a small scar through the eyebrow, a jagged scar on the chin, a gold
  tooth, a subtle neck tattoo, or a small nose stud. Never a mole or a beauty mark.

Keep the face attractive and the build well-proportioned.

**Say in the prompt that the person is invented.** Open the subject with it, in these words or close
to them: *"a wholly fictional, non-identifiable person — not a real or public figure, and not
resembling any actual individual."*

**What they're wearing** — the garments and how they sit on the body, any accessories or jewellery, and how the whole thing is put together.

**The top is closed, whatever the brief asks for.** Every description should put the neckline high
and the chest fully covered. Anything cut low or strappy is only ever worn with a closed layer over
it, never by itself.

Write that coverage as what is there, not as what isn't: *"a round-neck T-shirt"*, *"a fully buttoned
V-neck cardigan"*. Describing what to leave off — the plunge, the skin, the gap — tends to put exactly
that in the picture, so phrase the whole line as presence.

### Step 2: Set the scene

A place the brief names is the place. Otherwise pick one that fits how the actor will be used, indoors
or out.

Then describe it — the surfaces, the objects, and what fills the space. A name alone gives the model
nothing to build the room from.

- **The setting** — where they are, and what surrounds them.
- **What's behind them** — what falls in frame, as it happens to be rather than arranged.
- **Colours** — the ones that dominate.
- **Time of day and weather**, where they show.
- **The light** — where it comes from, its quality, and what it catches. Default to plain, neutral
  daytime light with no warm tint — ordinary daylight colour, not a sunset glow — unless the brief
  asks otherwise. No studio lighting, no plain backdrop.

### Step 3: Set the shot

- A self-portrait on a phone's front camera.
- Head and shoulders fill the frame, at arm's length.
- Framing slightly tilted, not quite centred.
- Looking into the lens, face turned toward it. Not sideways, not in profile, not glancing off to
  one side.
- Small-sensor grain, real skin, no retouching, subject sharp and background falling away on its own.
- Hands empty

Keep out: *portrait*, *editorial*, *studio*, *posed*, *retouched*, *magazine-style*, any
professional camera, tripod or lighting rig, 

### Step 4: Write the prompt in this order

Write the prompt as prose in this order — one paragraph is enough.

1. **Subject** — from Step 1
2. **Location** — from Step 2
3. **Composition** — from Step 3

### Step 5: Generate and hand back

One `image_generate` call, `nano-banana-pro` at `3:4` unless the brief named a model or shape.
Generate once — never a second version to compare.

The image is polled for you, but it can come back as `{status: "pending", …}` — a job handle, not a
failure. Pass that exact handle to `job_status` to retrieve the finished image, and again if it is
still pending. **Never re-run a pending generation** with `image_generate`; that starts a new,
separately-billed job.

Hand back the image. 

## Edge cases

- **Safety / NSFW rejection** → name a workable stand-in for whatever tripped the filter — cover the
  wardrobe, change the setting — and resubmit. Identical inputs fail identically, so change something.
  If it keeps refusing, switch to `seedream-5`. After a second rejection, tell the user which
  element is blocked instead of retrying blind.
- **A video model refuses the image as a possible likeness of a real person** → rewording the prompt
  changes nothing. Generate a different person — a different face, not a retouch of the same one. If
  it happens again, change the video model rather than the actor.
- **`error: "no_provider_configured"`** → relay the tool's `hint`.
