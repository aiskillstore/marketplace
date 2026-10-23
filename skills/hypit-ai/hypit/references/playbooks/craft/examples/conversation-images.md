# Podcast and interview image direction examples

These are English renditions of production prompts, with output aspect ratio moved to the model
parameter. They retain the strong aesthetic direction, specific wardrobe, setting and spatial choices
that made the examples useful. Each case states its own inputs; use its relationships without treating
the character, product or prop inventory as a conversation template. Some images were generated
separately and imported as files.

## Shared capture language

Use `phone-ugc-v1` from `@hypit/gpt-image-kits` for this photographic language. Its fixed paragraph is:

```text
A photograph captured as a single frame from a video actually shot on an iPhone, with the texture of real iPhone footage. The image looks real, without an oily, overprocessed finish. The background is clearly visible, with no depth-of-field blur. Skin texture is natural and fine, and the lighting is natural. The image is coherent and free of visual artifacts.
```

When adapting these production directions with the current Kit, arrange person and appearance in
`person`, the camera encounter in `shot`, and the surrounding place in `setting`. Include reference
responsibilities where they apply. A derived view can stay brief where its references already
establish the facts; the `person` and `setting` blocks can be omitted. The Kit supplies Capture once.
Set the output aspect ratio, such as `9:16`, on the model. Connect the stated reference images as
actual model inputs. The historical directions below retain their production wording and order.

These renditions preserve complete production directions as evidence, including additional
time-of-day, brightness, exposure, or lighting language that belonged to those particular shots.
For a new phone-video image, begin with the current Craft and the Kit, then carry such direction when
the intended scene itself needs that visible fact.

## Restaurant podcast views

### Main host: establish a person and a place together

Inputs: text only. The character's beauty, muscular contrast, styling and relaxed social situation
belong together. The table at lower left balances her placement on the right and helps establish
where her off-screen partner might sit.

```text
Generate a close half-body podcast photograph. The woman sits toward the right of the frame, her
body turned slightly left, looking left as though talking with someone outside the frame. Her face
is largely visible from the front, with natural light on it. She sits back on a comfortable fabric
sofa with her legs crossed.

The setting is the inviting outdoor seating area of a Korean street-side restaurant. Behind her
are a beautiful dark wooden exterior wall with a grainy texture, coral-red architectural details,
some plants and other tables. A half-eaten strawberry bingsu sits on the table at the lower left.
A podcast microphone extends from the left, labeled HYPIT in a well-designed uppercase typeface.

She is a muscular woman with extraordinarily beautiful Japanese-American features: very large,
beautiful eyes, very fair skin, a small refined face with smooth facial planes, and the beauty of
a Korean girl-group idol. She has long straight black hair with blunt bangs and wears beautiful
blue contact lenses.

Her physique creates a striking contrast: a powerfully built, muscular body in a black strapless
top with an angel-wing pattern. Her arms are muscular, with clearly visible veins and muscle
definition. She wears relaxed, light-colored tweed trousers with an asymmetric striped pattern.
Her shoulders are very broad and her head-to-shoulder proportions are excellent. She is close to
the camera while remaining contained within the frame.
```

### Other host: a complementary view of the same place

Input 1: main-host image. The parent's useful world is retained; the other host, gaze, microphone
entry and visible background sector change. “Symmetrical” describes the conversational relationship,
not a horizontally flipped copy of the same wall.

```text
Generate a fully symmetrical counterpart to the reference podcast half-body photograph, keeping the
pose and composition correspondingly symmetrical. The person now sits toward the left and looks right.
The microphone extends from the right and still reads HYPIT. Keep the lighting natural.

The setting is still outside the same Korean restaurant, but the background contains a different
set of objects because the camera now looks toward the other side of the space.

Replace the woman with a skinny American high-school boy who looks like a nerd. He wears a
light-colored printed T-shirt with an abstract little-devil graphic, black trousers and a cool
necklace. His curly hair is messy and he wears black-framed glasses, but his face is still handsome.
```

### Main host holding the product

Input 1: main-host image. Input 2: the actual app icon. Screen-left and screen-right describe hands
as seen by the viewer, avoiding an ambiguous “her left” across camera views.

```text
Keep the natural lighting throughout the image and the microphone position completely unchanged.
The woman holds a phone whose screen displays a square image: the icon in reference image 2.
She still looks left, as though talking to the person there. She raises the phone with the hand on
the right side of the image and points at it with the hand on the left side of the image.
```

### Other host holding the product

Input 1: other-host image. Input 2: the same icon. Derive this from his view, not from the woman's
product pose; her camera geometry does not become his merely because both hold the same phone.

```text
Keep the natural lighting throughout the image and the microphone position completely unchanged.
The boy holds a phone whose screen displays a square image: the icon in reference image 2.
He still looks right, as though talking to the person there, and raises the phone with the hand
on the left side of the image.
```

## Main host in everyday life

Each image below takes the main-host image as input 1 and the relevant company/product logo as
input 2. These are independent branches. They preserve her recognizable beauty and strong physique
while changing the situation, clothing, camera and setting.

### Company reception selfie

```text
Generate a raised-arm selfie. The woman from the reference is at a company's reception area,
turning toward her raised phone to take the photograph. She has changed into a light-gray sleeveless
lightweight sports cardigan with a hood, over a coral-red bandeau top. She wears both the hood and
a baseball cap. She makes a lively expression and a peace sign.

There is a suggestion of other people inside the company. Her physique and arms remain powerful,
and she is still strikingly beautiful. The company logo is the logo in reference image 2.
The lighting looks like real light in the room, including the light on her face.
```

### Playful mirror selfie in a shop

```text
Generate a mirror selfie. The woman from the reference stands inside a small street-side shop,
holding her phone toward a mirror. She has changed into an expensive coral-red tank top and wears
gray-black over-ear headphones. Her other hand holds a refined art object whose design comes from
the logo in reference image 2.

She makes a lively expression with her mouth slightly open, as though playfully about to eat the
object. Her physique remains powerful, her arms are very muscular, and she is still exceptionally
beautiful. Her phone has a cute CASETiFY case with a little rabbit pattern. She looks at the phone
screen. Some of the world outside is visible through the window.

The lighting looks real, including the light on her face. The composition is lively rather than stiff.
```

### Low-angle study scene

```text
Generate a low-angle photograph. The woman from the reference is in her study at home. The phone
appears to be placed on the desk, looking up at her as she studies seriously on a laptop.
She has changed into a cute coral-red camisole-style bib-overall outfit, with a white hair clip
holding back part of her hair. She is still exceptionally beautiful.

The laptop is light-colored, and the logo on its back is the logo from reference image 2 in coral red.
The room has a warm, modern Korean interior. Real afternoon sunlight illuminates the home with
bright golden light, and her face also has believable natural illumination.
```

## Optional split-screen opening

Inputs: both final host views. The output shape remains a model parameter.

```text
Create a top-and-bottom split screen, with the boy in the upper half and the woman in the lower
half. Both are close views focused on their upper bodies.
```

The references already establish the people and setting, so this direction can stay short. The
corresponding video action gives the silent woman a small posture adjustment and an attentive look;
that motion belongs in video direction, not a longer still-image description.

## Street interview views

### Shared scene: establish both people before choosing a close view

Inputs: text only. This example creates the encounter, microphone relationship, car and gaze axis
in one image. Its specific luxury styling serves this character; it is not a street-interview rule.

```text
Generate a close street-interview photograph. On a wealthy street in New York, a matte light-green
Porsche is parked at the curb. Near the center-left stands a mob wife beside the front of the car,
partly facing the camera. Her sunglasses rest on her forehead and her hands are at chest height.
The car's nose points left; the Porsche badge is visible between the two people near the bottom
of the image.

She has luxurious black hair in long loose waves, wears an expensive-looking dark fur coat over a
leopard-print strapless mini dress, and has a gold-inlaid cross necklace. The hand on the left side
holds an exceptionally expensive Hermès bag. She is about twenty, very young and extraordinarily
beautiful, with Japanese-Italian features, very fair skin and a clear, refined, affluent presence.
Her beauty is on the level of a Hollywood film star.

On the right is a cheerful young American college man, seen side-on by the camera. He wears a funny
backward cap, a coral-red designer graphic T-shirt, a spiked belt and fashionable flared jeans.
He is handsome, with curly strands escaping the cap. Both people are framed through roughly the
upper seventy percent of their bodies. He holds a microphone labeled HYPIT toward the woman's mouth.
There are no other people in the image.
```

### Guest close view

Input 1: shared scene. Change the attention and crop while inheriting the person and encounter.

```text
Focus the image on the woman from the reference. Place her in the center of the frame, looking
toward the right side of the image.
```

### Interviewer close view

Input 1: shared scene, independently of the guest closeup. The remaining piece of the woman keeps
his close view connected to the encounter.

```text
Focus the image on the man from the reference. Place him in the center, slightly larger in frame.
He continues looking left and holding up the microphone in the same pose. Part of the woman's
body remains visible at the left side of the image.
```

## What to transfer to another production

Transfer the decision, not the decorative inventory: start with a useful person in a world, derive
the views needed, state what each parent preserves, and connect authoritative references where the
production needs exact private or factual identity.
The podcast branches change camera, prop state or daily situation for different reasons. The
interview branches change attention while keeping a shared encounter. Neither graph asks for a
chain of generated video end frames, and neither requires redrawing all materials for every generated clip.
