# Video Visual Patterns

These patterns are distilled from the public Awesome-Nano-Banana-images gallery and adapted for short-video production. They are not copied prompts. Use them as reusable structures.

## Pattern 1: Character Consistency Pack

Use for Q-style IP, cute animals, vegetable characters, child-facing characters, or recurring narrators.

Output:

- Identity lock
- Three-view sheet
- Expression sheet
- Pose/action sheet
- Transparent cutout
- Sticker pack

Prompt skeleton:

```text
Create a consistent character design sheet for [character].
Keep the same face shape, body proportion, color palette, clothing/accessories, and rendering style across all panels.
Include front view, side view, back view, six expressions, and six simple actions.
Clean bright background, child-friendly cute IP style, clear silhouette, no text.
```

Chinese adaptation:

```text
为[角色]制作一套统一角色设定图。所有画面必须保持同一个角色：脸型、身体比例、主色、服装、配饰和绘制风格都不能变化。
包含正面、侧面、背面、6个表情、6个动作。背景干净明亮，适合短视频和儿童向内容，轮廓清楚，不要文字。
```

## Pattern 2: Short-Video Storyboard

Use when a script or topic needs keyframes for image-to-video generation.

Default structure:

1. Hook frame
2. Conflict frame
3. Action frame
4. Result frame
5. Ending or call-to-action frame

Continuity lock:

```text
All frames must keep the same character identity, same art style, same color palette, same world setting, and consistent lighting.
```

Prompt skeleton:

```text
Create frame [number] of a 5-frame short-video storyboard.
Scene beat: [beat].
Character: [identity lock].
Action: [action].
Emotion: [emotion].
Camera: [close-up / medium shot / wide shot / low angle / top view].
Style: [style].
Leave clean empty space for later title overlay. No text in the image.
```

## Pattern 3: Cover Or Poster

Use for Douyin, Xiaohongshu, WeChat video cover, and AI/parenting article cover.

Cover needs:

- One instantly readable subject
- Strong facial expression or action
- Visual conflict
- Empty title area
- Phone-size readability

Prompt skeleton:

```text
Create a vertical 9:16 short-video cover image.
Main subject: [subject].
Visual hook: [conflict or surprise].
Composition: subject occupies 55-70% of the frame, clean blank area at the top/right for title overlay.
Style: [style], bright lighting, high readability on phone screen.
No text, no logo, no watermark.
```

## Pattern 4: Expression And Pose Control

Use when the user has a fixed character but needs more scenes.

Prompt skeleton:

```text
Using the uploaded reference character, keep identity unchanged.
Change only the expression to [expression] and the pose to [pose].
Keep clothing, face, proportions, colors, and illustration style identical.
Clean background, no text.
```

Common expressions:

- curious
- surprised
- shy
- proud
- worried
- happy
- determined
- sleepy

Common actions:

- waving
- holding a small prop
- pointing at something
- running
- sitting
- looking back
- jumping
- whispering

## Pattern 5: Transparent Asset Cutout

Use for thumbnails, compositing, motion graphics, and video editing overlays.

Prompt skeleton:

```text
Extract or generate [subject] as a clean transparent-background PNG-style asset.
Keep the full body/object visible, centered, clean edges, no shadow unless requested, no text.
```

If transparency is not supported, ask for a plain solid background that can be keyed out:

```text
Use a pure white or pure green background, centered subject, clean outline, no text.
```

## Pattern 6: Prop And Material Sheet

Use for repeated objects in video scenes.

Prompt skeleton:

```text
Create a prop sheet for [object].
Include front view, side view, top view, close-up material detail, and one in-scene usage example.
Keep one consistent style and color palette. Clean layout, no text.
```

## Pattern 7: Educational Or Child-Friendly Visual

Use for parenting, literacy, gentle explainer, children's content.

Prompt skeleton:

```text
Create a warm child-friendly educational visual about [topic].
Use soft rounded shapes, bright natural colors, clear subject hierarchy, simple scene, safe and gentle expression.
Avoid fear, medical imagery, harsh contrast, clutter, and any text unless requested.
```

## Pattern 8: Visual QA

After generating prompts, include this checklist:

- Character identity remains consistent.
- Main subject is readable on a phone screen.
- Prompt states aspect ratio and use case.
- The image leaves title space if it is a cover.
- The prompt says no text when text should be added later.
- Style, lighting, palette, and world setting are locked.
- Each storyboard frame changes action/beat, not the whole visual identity.
