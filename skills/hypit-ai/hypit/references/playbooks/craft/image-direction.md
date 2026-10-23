# Directing generated images

An image model can paint the visual world the work needs: a person in a camera view, a lived-in place, a product, an icon, or a fantastical event seen through ordinary footage. Each request directs a complete picture. The author gives it a subject, aesthetic force and visible relationships; the model realizes the details that make those choices into an image. References bring selected visual facts into that same act of painting.

For the common phone-video portrait, the [phone-UGC Kit](#use-a-concrete-capture-direction) supplies tested capture wording; the author directs the person, camera encounter and place. The [complete examples](examples/image-direction.md) show prompts alongside their results.

## Two ideas behind every sentence

**A capable painter has visual habits.** “A person at a desk” leaves the face, styling, encounter and room to the model’s usual associations. A casting noun, the kind and strength of beauty, a hairstyle or the social character of a place can shift the whole picture. Choose the few dimensions that matter to this work and direct them clearly; the model can complete the rest.

**A few decisive strokes carry the picture.** For a presenter that may be an arresting face and a clear camera encounter; for a product, its defining form and use; for an icon, a readable visual idea; for a place, a few telling objects and spatial relationships. These choices establish more than a long inventory of incidental details. Spend words where they change the image and let the model complete the rest. “Few” describes the number of important decisions, not a word limit. The [balcony portrait](examples/image-direction.md#japanese-sailor-on-an-apartment-balcony) shows the difference between authored anchors and details the model supplied.

When the work calls for a presenter people want to watch, direct attractiveness with conviction at the character’s actual age. Photographic credibility and exceptional beauty can coexist. Fatigue, comedy or a difficult expression can also be part of the character or moment when the story calls for them.

## Four paragraphs, four responsibilities

For a phone-UGC image establishing a person in a scene, the tested starting shape is the Kit’s fixed **Capture** paragraph followed by **Person**, **Shot** and **Setting**. These are directing responsibilities, not a form to fill attribute by attribute. A reference may already settle a person or place, while a different kind of image may need a different shape altogether.

| Part | What the author decides |
| --- | --- |
| Capture | The photographic language; [the Kit](#use-a-concrete-capture-direction) supplies the tested phone-video wording. |
| Person | Who this is, why they are compelling, and the few appearance choices that make them particular. |
| Shot | What they are doing, whom they address, and how the camera meets their face, body and surroundings. |
| Setting | Where this happens, with a palette and visible details that make the place feel inhabited. |

The parts influence each other: an outfit contributes to the palette; a table can make an offset framing feel natural. Keep each paragraph focused without treating the boundaries as walls.

## Seven questions for a presenter image

For a complete person-and-place image, these questions help find the high-value decisions:

1. What kind of captured image is this?
2. Who is this person, and what kind and strength of appeal should they have?
3. Which appearance choices make them recognizable rather than generic?
4. What ongoing activity or disposition can the next video moment continue?
5. How does the camera frame this encounter, including face, body, gaze and useful space?
6. What visible relationships make the place and the person belong together?
7. Which colors give the whole image its intended character?

One phrase can answer several questions; some are already answered by the brief or a reference. They are a way to notice what matters in this picture, not seven required sentences.

## Cast the person with force

When casting an adult presenter in this GPT Image 2 phone-video direction, start with **girl** or **boy** followed by the actual adult age. This tested wording has produced appealing, lifelike adult faces; the noun steers the portrait while the explicit age and role still define the person. For example: *a Chinese girl in her mid-forties, exceptionally beautiful, with the presence of a leading actress of her generation*; *an Indian boy in his late thirties, strikingly handsome, with the easy confidence of a leading actor in his late thirties*. When a reference establishes the person’s appearance, let it carry that identity into the current picture.

Give beauty or handsomeness both **strength and kind**. *Exceptionally, strikingly beautiful, with the looks of a top Japanese idol* carries more direction than *attractive*; a different age, culture or role calls for its own equally strong comparison. Cultural background, visual appeal and a social or aesthetic type—jirai-kei, soft goth, clean girl, a particular kind of founder—can work together, but only the choices that define this character need words. A role alone rarely casts the face.

Choose a few visible anchors that realize that direction: hair around the face, eye makeup or gaze, a memorable garment or accessory. For a half-body human presenter, *very broad shoulders and excellent head-to-shoulder proportions* is a useful structural anchor against the large-head, narrow-shoulder look. Its value is the proportion, not an instruction to expose every part of the shoulders.

A portrait can establish a person’s identity, a chosen appearance cue or a useful camera view. Direct what the current picture carries from it and what changes in the camera view, styling or setting. [Reference relationships](generated-dependencies.md) show how an image can anchor another complete view while its person, composition and visible environment change.

## Choose an idle state for the encounter

A reusable character image gives the video a state it can continue. Speaking toward the viewer with a free hand gesturing is an ongoing activity, not a frozen pose; an alluring, curious or teasing presence can persist through several beats. A wide laugh or a startled face commits the image to one instant, which is useful when that instant is the shot’s subject. Let the intended performance decide.

For a direct-to-viewer presenter, *the face points straight toward the lens, with no head tilt or rotation* gives a dependable starting view while the body can turn and the hands can work. Podcast partners or interviewees instead have a gaze relationship with each other. Their reference images should establish that relationship, with faces readable from the camera angle the work needs.

## Frame the image for what it will become

Direct framing, camera distance, body arrangement, face angle and placement as one encounter. A close half-body presenter can make the face, shoulders and gesture legible; a wider view can carry an action or a second person. Place the face where the later composition needs it, while describing only the physical scene the image model should paint. A table, another person or a doorway may make an offset position natural when it also belongs to the story. An offset can also be a straightforward camera choice.

For a camera view that will sit alongside later MG, direct the photographed scene the viewer will see. An icon painted on a sign or phone screen belongs to that image and travels with it. A ranking icon meant to appear or move independently can be made as its own image Resource; a component can then place and animate that Resource, or draw the icon itself. Describe the person’s actual interaction with people and objects in their scene. Choose the source view for the body, gestures and setting the performance needs; [spatial fitting and crop](../../production/spatial.md) can present it in other viewports. [Graphic composition](graphic-compositions.md#give-material-and-graphics-room-together) owns its relationship with surrounding content.

## Establish the place with a few details

A setting should carry a social world, not serve as a color field behind the face. Name the recognizable place and a few details that explain why this person is there: café seating and a half-finished dessert, a record shelf continuing into an aisle, a classroom door and student posters. A view through a window or an opening behind the person can give the scene distance. Choose objects for their story and visual character, then let the model complete the ordinary remainder.

Give the place a deliberate palette. *Coral red and yellow* or *terracotta and green* can be carried by the actual architecture, clothing, plants and objects rather than painted as a uniform wall. A broad light or dark field can gain interest from the place’s real surfaces and contents—wood grain, tiles, shopfronts, foliage—when those belong to the scene. Describe color as color and material; the Kit already supplies natural-light capture language. Time of day, weather or a particular light event earns a place in the prompt when the story or reference depends on seeing it.

## Use a concrete capture direction

For a phone-video frame, `@hypit/gpt-image-kits/phone-ugc-v1` preserves the tested iPhone capture paragraph. Keep that paragraph intact while directing the picture’s content in ordinary prose. A fantastical person can still inhabit a photographed world; an illustration, product render or other visual goal calls for capture language that serves that goal.

The Kit assembles `person`, `shot` and `setting` after the fixed paragraph:

```svml
<import as="text" from="@hypit/text@1"/>
<import as="ugc" source="@hypit/gpt-image-kits/phone-ugc-v1"/>

<text:Render id="portrait-prompt" template={ugc.phone-ugc-v1}>
  <text:Set name="person" text={portrait-person}/>
  <text:Set name="shot" text={portrait-shot}/>
  <text:Set name="setting" text={portrait-setting}/>
</text:Render>
```

These slots carry paragraphs, not individual appearance fields; the Kit allows `person` or `setting` to be omitted when a reference already supplies those facts. Pass `{portrait-prompt}` to the image Surface and connect reference images there. GPT Image 2 is the usual choice for this direction; `2K` often serves a full-screen picture or video reference, while `1K` can serve an inset. Aspect ratio and resolution are model parameters, not prompt words. The Kit package README owns its assembly interface.

## Let references supply the facts they own

A supplied portrait can establish identity; a camera view can establish a shared place; a product image can establish the product. Say what each reference contributes and what the current picture should show, and connect the actual images on the Source. When references already provide the difficult visual facts, the prompt can concentrate on the new encounter or viewpoint. The model paints that whole view, carrying forward the facts the work needs and realizing the new ones.

Carry the phone-video capture direction into another view when the work keeps the same photographic world. [Reference relationships](generated-dependencies.md) owns multi-view branches; [transformations](../../creation/transformations.md) owns a face or product swap across the video.

The finished prompt should read as one picture with a clear subject, visible relationships and visual character, with words spent on the decisions that make it useful to this work. The examples preserve complete prompts as evidence of those particular pictures, not as sentences to transfer unchanged into every new one.
