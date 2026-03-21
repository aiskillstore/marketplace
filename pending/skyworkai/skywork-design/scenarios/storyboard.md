# Storyboard

## Triggers

storyboard, scene breakdown, shot list, animatic, shot planning, visual script, frame-by-frame

## Defaults

- **Aspect ratio**: `16:9`
- **Resolution**: `2K`

## Consistency Strategy

Storyboards live or die on visual consistency — the same characters, locations, and style must carry across every frame.

**If the user provides reference images** (character designs, mood boards, style references):
1. Use them as `--input-image` for every subsequent frame
2. Extract and document the visual DNA: art style, color palette, character features, lighting mood
3. Repeat these descriptors verbatim in every frame prompt

**If the user provides NO reference images**:
1. Begin with Phase 1 (story breakdown) and Phase 2 (reference sheet generation) below — do NOT skip to frame generation
2. The reference sheets become the source of truth for all subsequent frames

## Workflow

### Phase 1: Story Breakdown

Analyze the narrative and produce a shot list before generating any images. Define:

- **Scene count and sequence** — number of frames, scene transitions, pacing
- **Character bible** — each main character with exact appearance descriptors: name, age, build, hair color/style, skin tone, clothing (color, material, fit), distinguishing features (scars, glasses, accessories). Be exhaustively specific — vague descriptors cause drift
- **Location directory** — each recurring location with architectural style, lighting conditions, color atmosphere, key props
- **Art style lock** — choose ONE style phrase and use it verbatim in every prompt (e.g., "Makoto Shinkai anime style with soft volumetric lighting" or "Moebius-inspired line art with flat pastel colors"). Never paraphrase or vary the style description

### Phase 2: Reference Sheet Generation

Generate reference sheets **before** any storyboard frames. These anchor visual consistency.

1. **Character sheets**: For each main character — full body, front-facing, neutral pose, plain background. Include 3/4 view and profile if the character appears in many frames. Name: `...-char-[name].png`
2. **Location sheets**: For each recurring location — wide establishing view with characteristic lighting. Name: `...-location-[name].png`
3. **Style reference**: If the art style is complex, generate one standalone "style sample" frame to use as visual anchor

### Phase 3: Frame-by-Frame Generation

Generate each frame sequentially. For every frame:

- Pass relevant character/location sheets via `--input-image`
- For multiple characters in one frame, pass all relevant sheets as multiple `-i` arguments
- **Copy-paste** the exact character description and style phrase from Phase 1 — do not rephrase
- Describe the shot composition using cinematic language: camera angle, distance, framing
- Name: `...-shot-01.png`, `...-shot-02.png`, ...

### Phase 4: Review and Revise

Re-generate inconsistent frames using `--input-image` from both the character sheet and the nearest consistent frame. Reference two anchors simultaneously for maximum consistency.

## Design Thinking

1. **Serve the story, not the art** — Every frame exists to advance the narrative. Ask: what must the viewer understand from this frame? If a frame doesn't convey new information or emotion, it shouldn't exist
2. **Control pacing through composition** — Wide establishing shots slow the pace and set context; close-ups accelerate emotion and tension; medium shots carry dialogue. Vary shot types to create rhythm
3. **Plan transitions** — Adjacent frames should flow visually. If frame 5 ends on a character looking right, frame 6 should have the subject of their gaze on the left. Continuity of eye-line and spatial direction matters
4. **Emotion through camera language** — Low angles convey power/menace; high angles convey vulnerability; Dutch angles convey unease; eye-level conveys neutrality. Choose deliberately
5. **Less is more** — A 12-frame storyboard that tells a clear story beats a 30-frame board with redundant shots. Edit ruthlessly before generating

## Aesthetics Guidelines

- **Style coherence is absolute**: Every frame must look like it was drawn by the same artist. The style phrase from Phase 1 is sacred — never modify, abbreviate, or "improve" it across frames
- **Color continuity**: Establish a scene-level color palette (warm interiors, cool exteriors, etc.) and maintain it. Dramatic shifts in color should only occur at intentional story beats (e.g., flashback = desaturated, climax = high contrast)
- **Consistent character scale**: Characters should maintain proportional relationships across frames. If character A is taller than B in frame 1, this must hold in frame 10
- **Lighting as storytelling**: Match lighting to emotional tone — soft diffused light for calm moments, harsh directional light for conflict, silhouette for mystery. Describe the lighting direction and quality in every frame prompt
- **Compositional clarity**: Each frame should have a clear focal point. Use the rule of thirds. The viewer's eye should never wander aimlessly — lead it with contrast, positioning, or character gaze direction
- **Negative space for text/annotation**: If the storyboard will include dialogue or action notes, leave intentional space (typically bottom 15%) for text overlay

## Prompt Rules

- Copy-paste the art style phrase identically into every frame prompt — never paraphrase
- Copy-paste full character descriptions into each frame where that character appears
- Always pass reference sheets via `--input-image` — verbal description alone causes drift
- Use cinematic shot terminology: "wide shot", "close-up", "over-the-shoulder", "POV shot", "two-shot"
- Describe lighting direction and quality explicitly: "warm golden key light from upper left, cool blue fill from right"
- When a frame includes dialogue, enclose the spoken text in quotation marks within the prompt (e.g., `a speech bubble saying "Let's go!"`). Define the speech bubble style once in Phase 1 (shape, font style) based on the art direction, and reuse that description verbatim across all frames
