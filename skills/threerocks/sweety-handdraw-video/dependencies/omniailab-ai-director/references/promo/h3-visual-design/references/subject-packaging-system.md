---
name: omniailab-promo-h3-visual-design-subject-packaging-system
description: 「Universal Subject Packaging System」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：This file is the shared source of truth for product, person, logo, sce
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Universal Subject Packaging System

This file is the shared source of truth for product, person, logo, scene, mixed, original-footage, and talking-head packaging. Use it to decide what must stay fixed, what can be rebuilt, and which stage mode the prompt should use.

## 1. One Shared Object

Use one compact object first:

```text
PACKAGING_SUBJECT = {
  subject_type: product | person | logo | scene | mixed | unknown,
  logo_layout_type: pure_logo | logo_with_cover_anchor | not_logo | unknown,
  identity_lock: [the real features that must survive],
  source_background_policy: preserve | remove | rebuild | partial,
  space_mode: preserve_source_space | rebuild_editorial_space | hybrid_local_set,
  stage_mode: product_hero_stage | person_editorial_stage | logo_motion_stage | scene_rebuild_stage | preserve_original_packaging,
  camera_anchor: [what the camera should orbit, hold, or rebuild around],
  lighting_anchor: [what the light should reveal or follow],
  typography_relation_set: [at least two of front / mid / back / occlude / attach / surround / mirror / floor / wall / frame / portal],
  effect_source: [where the motion/effect starts],
  effect_destination: [where it settles, returns, or becomes the next composition state],
  composition_states: [1–5 states based on duration]
}
```

If the subject is mixed, choose one primary subject and one supporting subject. The primary subject sets the stage; the supporting subject can only assist.

When `subject_type=product`, build this source-grounded object before choosing any effect:

```text
PRODUCT_PROTECTED_LAYER = {
  silhouette: [complete visible outer contour],
  component_inventory: [all visible components and their count],
  assembly_relationships: [how visible components connect, overlap, hinge, or align],
  material_map: [source-visible material per region],
  transparency_map: [source-visible transparent / translucent / opaque regions],
  controls_logo_geometry: [visible controls, openings, marks, and Logo geometry]
}
```

Treat this as an independent protected render layer and an internal quality check in every space mode and style. It is not a story topic, screen-copy source or visible label. Source-visible values are the only truth: do not remove, duplicate, detach, dissolve, fold, slice, hollow out, or reconnect product components. A product region may be transparent only when that same region is visibly transparent in the source. Refraction, frosted glass, fracture, scan, 3D type, portal, collage, and glitch belong to added packaging layers, background/foreground carriers, light, shadow, or reflection—not to the product body.

## 2. Universal Route

IDENTIFY -> CHOOSE SPACE MODE -> PRESERVE / HYBRID / REBUILD -> RELATE -> RESOLVE

- IDENTIFY: decide subject type and lock the identity facts.
- CHOOSE SPACE MODE: confirm whether the source environment stays, changes locally, or becomes a new editorial world. Subject type never decides this automatically.
- PRESERVE / HYBRID / REBUILD: keep the original frame, rebuild one local surface, or build a coherent world/editorial space.
- RELATE: place the coordinated type cast, graphic carrier, camera, light, and effects in at least two visible relationships to the subject.
- RESOLVE: return the text/effect to a readable end state, back to the source, or transform one carrier into the next composition state.

## 3. Space Route First

| space_mode | source environment | camera/subject permission | packaging power |
|---|---|---|---|
| preserve_source_space | keep the environment, composition and spatial skeleton | video camera/cuts stay fixed; image does not gain new subject angles | type-camera motion, perspective type, occlusion, frames, panels, repetition fields, color accents, localized light/effects |
| rebuild_editorial_space | source background may be removed or rebuilt | robotic-arm moves, orbit, turntable, push, rise, macro and portal pass-through are available | subject, camera, light, stage, type and music form one high-impact sequence |
| hybrid_local_set | keep the main environment; rebuild one local plane/zone | limited local camera change that preserves scene continuity | one wall/floor/glass/paper/light/type portal bridges the real scene and the graphic system |

All three routes use the same TYPE CAST, COLOR SCRIPT, GRAPHIC KIT, SPACE BINDING and composition-state system. Preserve is a permission boundary, not a simpler visual tier.

## 4. Subject Mode Map

| subject_type | rebuild-stage mode | keep fixed | packaging relation |
|---|---|---|---|
| product | product_hero_stage | protected silhouette, component inventory, assembly relationships, material map, transparency map, controls/Logo geometry | rebuild a showcase stage and show source-consistent angles |
| person | person_editorial_stage | face, hair, body shape, clothes, gesture, lip movement, gaze | build an editorial space around the person |
| logo | logo_motion_stage | glyph structure, proportions, spacing, color, legibility; optional cover anchor identity | keep the logo readable, then animate or materialize it around a clear cover anchor when present |
| scene | scene_rebuild_stage | spatial skeleton, ground, back plane, vanishing direction, key objects | rebuild the world and let text live inside it |
| mixed | mixed_stage | primary identity first, supporting identity second | keep one clear owner of the frame |
| unknown | ask one question | none yet | do not guess the subject |

When `space_mode=preserve_source_space`, use `preserve_original_packaging` for every subject type and keep the subject-specific identity lock. When `space_mode=hybrid_local_set`, use the subject recipe only inside the confirmed local zone.

## 5. Stage Recipes

### product_hero_stage

- Preserve the complete `PRODUCT_PROTECTED_LAYER`; product motion and camera motion may reveal source-consistent views but may not rebuild the product itself.
- Remove ordinary source clutter.
- Build one coherent stage with a floor, a back plane, a negative-space zone, and a transition surface.
- Use product motion, camera motion, light sweep, micro detail, turntable, orbit, macro push, or controlled rise.
- Build 3–5 composition states for a 15-second result: full product identity, 3/4 or side angle, material/detail macro, full-frame type takeover, final product/type coexistence.
- Make type, frames, panels and light share the same trigger as the product or camera. Use at least two relations: background wall/floor type, an independent foreground frame, an external typographic portal, or one brief depth exchange at a non-critical outer contour. Keep product and type on separate depth layers with clear spacing; for mascot/product covers, let the subject sit in the midground, the main title live on the back wall or a distant plane, and foreground cards/marks carry the smaller support text. After any brief edge occlusion, restore both as complete readable forms.

### person_editorial_stage

- Preserve face, hair, body, clothes, hands, gesture, mouth, and emotional tempo.
- Choose an editorial space: studio block, paper plane, mirror plane, gallery, color field, or architectural void.
- Text can follow the shoulder line, hand direction, body contour, gaze direction, floor/wall perspective or camera path. Include one background pass and one foreground/frame relationship; do not reduce the design to side labels.
- Keep lip movement and important gestures readable before any text expansion or occlusion.

### logo_motion_stage

- Preserve the logo as a logo.
- First infer `logo_layout_type` from the reference; do not ask the user. Use `pure_logo` when the source is only a Logo/wordmark/symbol plus background, texture or abstract marks. Use `logo_with_cover_anchor` when a person, mascot, product, object, sculpture, animal or scene element is prominent, central/foreground, overlaps the wordmark, or controls cover depth.
- If `logo_layout_type=pure_logo`, build motion from glyph contour, counters, stroke direction, spacing, material, scan fields and full reassembly; do not invent a person/product anchor.
- If `logo_layout_type=logo_with_cover_anchor`, keep `subject_mode=logo_motion_stage` and add `COVER_ANCHOR_LOCK`: the verified Logo/name remains the typographic owner, while the visible person/object becomes the cover anchor. Preserve its silhouette, face/material/pose and depth relationship; do not treat it as disposable background.
- Start from a fully readable version, then build a 3–4 state sequence: complete mark with cover anchor when present → logo-only geometry/scan field → verified name/glyph full-frame state → complete reassembly with anchor and wordmark.
- Use the real outer contour, counters/negative space, spacing, stroke direction or components to generate frames, dividers, repetition fields, masks, floor/wall planes and transitions.
- Treat the verified Logo and official name as Display A/B. Add supporting text only when it comes from the whitelist and has real semantics; generic words such as `FRAME / STAR / MOTION / FUTURE / SYSTEM` are not default decoration.
- Allow reveal, trace, split, reassemble, outline, material mapping, scan pass or spatial projection while preserving at least one complete readable state.
- Do not fill every state by repeating the same readable Logo/name at multiple scales. When whitelist text is sparse, use non-readable marks, crops, counters, scan slits, silhouettes, grain, shadows and brief macro cuts for density; keep readable repetitions countable and purposeful.

### scene_rebuild_stage

- Preserve the spatial skeleton: ground, wall, ceiling line, major objects, depth order, and vanishing direction.
- Rebuild the world first, then place text into it.
- Text can become wall paint, floor mark, glass reflection, fog, light band, signboard, projection, architectural frame or camera portal. Bind at least one type layer to a real plane and another to a different depth.
- Always write: world_name, floor, back_plane, depth_layers, subject_anchor, negative_space, transition_surface, lighting_anchor, camera_anchor.

### preserve_original_packaging

```text
PRESERVE_ORIGINAL_FOOTAGE（视频）: 保持原片主体、背景、构图、相机、剪辑、速度、色彩、光线、声音和已有字幕。
PRESERVE_SOURCE_FRAME（图片）: 保持原图主体、构图、空间骨架、关键物件、透视、色彩和光线；不把原环境替换成展示舞台。
TYPE LAYER STACK: Base Caption / Display A / Display B / Utility / Carrier / Depth-Occlusion / Texture-Light / Marks。
```

- For video, keep the original footage unchanged in subject, environment, framing, camera, cuts, speed, color, lighting, and sound.
- For images, keep the original frame, environment, spatial skeleton, key objects, perspective, color and lighting; do not invent new subject angles.
- Add only typography layers and localized effects.
- Build `Base Caption / Display A / Display B / Utility / Carrier / Depth-Occlusion / Texture-Light / Marks` as the new layer stack.
- The text layers may simulate type dolly, lateral truck, counter-orbit, parallax, focus swap or crop reveal; the footage camera remains the source camera, but the composite may use up to two 2%–3% punch-ins or lateral drift of the protected panel with matched parallax.
- For 13–15 seconds, use 3–5 packaging states tied to real cuts, actions, surfaces, perspective lines, edges or audio cues; each state may contain multiple coordinated layers with one dominant movement.
- For real-estate, retail, e-commerce and lived-in scenes, bind type to existing walls, floors, glass, shelves, doors, windows, shadows and vanishing directions. Use the real environment as the stage manual.

## 6. Talking-Head / Speech-Led Packaging

When the subject is a speaker or the user wants voice-led packaging, keep identity, face, mouth, hands, performance, framing and original audio. The final visual package must be generated by MiniMax H3; transcription supplies exact words and timing only, never the visual result.

```text
TALKING_HEAD_LAYER_STACK: CAPTION_TRACK / KEYWORD_HERO_TRACK / EVIDENCE_CARD_TRACK / SPEAKER_MINI_HEAD / EDITORIAL_MARK_TRACK / DEPTH-MOTION / SFX_CUE
SPEECH_BEAT_MAP:
- BEAT N｜source time=[真实时间]｜exact phrase=[逐字原句]｜semantic role=[hook/claim/evidence/example/comparison/process/conclusion]
  Viewer focus: [观看与理解目标]
  Visual evidence: [真实表情/手势/物件/上传素材/准确卡片/图形关系]
  Type and card: [准确文字、字体角色和版式]
  Motion and sound: [编辑层微运动、进入 cue、可读停留、触感音效]
  Transition contract: [上一版式出镜] → [转场类型与 0.12–0.35 秒] → [语义承接] → [下一构图和观察点]
```

- 按真实语句、停顿和重音划分 3–5 个节拍，不等分时间，也不改写口播迁就动画；每个节拍必须写 `Visual evidence`、`Type and card`、`Motion and sound`，不能只写“字幕出现”。
- `CAPTION_TRACK` 是口播的稳定底座：按真实语速一条一条推进，单次只显示一个完整意群/一句话，不把前后多句同时堆在画面里；短句保持一行，长句可折成 1–2 行，行距、字重和断行服务可读性。同一底部字幕区最多连续使用一个状态，随后必须换位或清空给 Hero/卡片让空间。
- `KEYWORD_HERO_TRACK` 从真实重音、观点、数字或结论取 2–6 字，15 秒至少两次以明显不同的 Display 角色做 65%–110% 大字接管，分别进入人物后景、前景、侧栏或跨画面版式；不能只轻微放大、换色或加下划线。
- `EVIDENCE_CARD_TRACK` 至少一次使用来源明确的素材弹窗：优先原视频可截取的局部画面/人物动作/环境细节做 crop 或 PiP，其次使用用户上传的图片、数字、引语、步骤或比较卡；必须写清“素材来源→证明哪句台词→卡片比例/位置→停留→退出”。没有可靠素材时才退回准确文字卡，不虚构复杂图表、地图、UI、截图、身份或 B-roll。
- `SPEAKER_MINI_HEAD` 用于卡片或关键词接管画面时保持口播人物存在：可把说话人从主画面缩到左上/右上角 12%–22% 的 protected mini-head 小窗，脸、口型和神态仍清楚，小窗只做陪伴/旁白位；主视觉让位给关键词 Hero、素材弹窗或分屏，不把人物糊成头像贴纸，也不改变原表演。
- `EDITORIAL_MARK_TRACK` 只用一套下划线、指针、点、框、纸条、分隔线、图标、涂鸦或局部光效，由真实发音、停顿、手势或切点触发并回收。
- 锁定原片仍保持原镜头内容，但必须安排 2 次以内的 2%–3% 合成层轻推近/轻横移/前后景视差，并在 0.3–0.8 秒内缓起缓停；不得改变脸、口型、手势或表演。不能把“原片镜头不动”解释成整条片完全静止。
- 13–15 秒必须形成 `single-line caption base → keyword hero → source-derived evidence popup/PiP → speaker mini-head + layout swap/final editorial cover` 至少 3 种版式；至少一次人物在后景、字体在前景，另一次人物缩到角落小窗或字体退后让卡片成为主焦点。对白始终在前，但每个 Keyword Hero、Evidence Card、SPEAKER_MINI_HEAD、合成层轻推近和版式换位各自绑定一个 3–5 个以内的短触感音效；不逐字配音效，也不让同一种粗黑体、黑色圆角框或底部位置贯穿全片。
- Never turn speech packaging into a product demo or a brand ad by default.

## 7. Scene Packaging Checklist

For scene packaging, never say only “a designed space”.

Always specify:

- world_name
- floor
- back_plane
- depth_layers
- vanishing_direction
- transition_surface
- subject_anchor
- negative_space
- lighting_anchor
- camera_anchor

If those are missing, the scene is still vague. In preserve mode, describe the existing values; in rebuild mode, design the new values.

For preserved real-estate, interior, exhibition, retail or architectural footage:

```text
SPATIAL_MOTIF_MAP:
- clip N: camera_vector / primary_axis / vanishing_direction / attach_plane / occluder / negative_space / entry_edge / exit_edge / light_path
- shared_motif: [跨片共享的一条竖轴/水平边/曲线/圆形/画框边/光路]；全片唯一 motion spine
TYPE PATH: DISCOVER → ATTACH → TRACK → OCCLUDE → TRANSFER → SETTLE
TEXT ARC: master_title=[一个]；supporting_lines=[2–3 条空间关系/观看路径]；scene_labels=[3–5 个真实物件/材质/区域/光线标签]
```

- Build a `SPATIAL_MOTIF_MAP` for every source clip: camera vector, primary architectural axis, vanishing direction, attach plane, occluder, negative-space zone, entry edge, exit edge and light path.
- Find one shared motif across clips—a vertical axis, horizontal seam, curve, circle, frame edge or light path—and use it as the only motion spine. If no motif repeats, use one restrained edge-transfer system; do not invent unrelated stickers for continuity.
- Choreograph one continuous path: `DISCOVER → ATTACH → TRACK → OCCLUDE → TRANSFER → SETTLE`. Type must inherit camera motion and plane perspective; screen-space floating labels do not count as spatial typography.
- Use one master title, two or three distinct supporting lines about the spatial relationship or viewing path, and three to five Chinese/English editorial labels grounded in visible objects, materials, zones or light. Keep every line semantically distinct under one copy angle; do not generate an unrelated poetic slogan or an isolated generic English filler for every room.
- Protect architecture and art. Use one full-frame or near-full-frame Hero at most; let other states breathe with medium and small type attached to real surfaces.
- Adapt every selected style to the architecture. Refined interiors reject thick black/white outlines, hard sticker shadows, bubble lettering, random dots/starbursts and repeated bounce motions unless the user explicitly asks for a childlike sticker treatment beyond the style label itself.
- Use restrained establishment → medium spatial title → one 55%–85% Hero/depth exchange → quiet resolve. Other titles stay at 20%–55%, use 2–4 layers, keep the source palette with one sampled accent, and derive graphics only from the shared motif or real architecture.

## 8. Logo Packaging Checklist

- Did the prompt explicitly judge `logo_layout_type=pure_logo` or `logo_layout_type=logo_with_cover_anchor` from the source instead of asking the user?
- Keep the logo fully readable at least once.
- If `logo_with_cover_anchor`, does the final prompt lock the anchor as a protected visual center instead of ignoring it or letting type push it out of frame?
- If `pure_logo`, does the prompt rely on real glyph geometry rather than adding fake product/person anchors?
- Decide whether the logo is static, split, traced, materialized, or projected.
- Keep spacing, proportion, and alignment under control.
- Use the Logo/official name as the main typography material whenever possible; do not place generic English tags around it to simulate design.
- Derive at least one frame/panel/pattern from real Logo geometry and at least one full-frame state from the verified name or glyph structure.
- Include at least one logo-only or glyph-geometry state before returning to the anchored cover; do not keep the same full cover composition for the entire clip.

## 9. Person Packaging Checklist

- Lock the face first.
- Do not break lip sync, gesture meaning, or identity.
- Place text in the body’s energy field: shoulder, hand, gaze, or movement path.
- If the user wants original footage untouched, use preserve_original_packaging instead of rebuilding a new editorial scene.

## 10. Product Packaging Checklist

- Build and lock `PRODUCT_PROTECTED_LAYER` first.
- Do not invent hidden parts.
- Keep silhouette, visible component count, assembly relationships, material map, transparency map, controls and Logo geometry source-consistent in every state. Never make an opaque source region transparent.
- Treat a source-visible brand mark as product identity. Repeat it as large composition text only when it remains exact, is semantically appropriate and does not turn the piece into a fabricated advertisement.
- If the product is supplied only as a category word or pure text concept, keep `FACTS_FOR_COPY` sparse and let `SCENE_PACKAGING_COPY` expand into a coherent concept narrative or sensory metaphor grounded in the subject; do not present imagined comfort, sound quality, performance, material grade, technical function or user testimony as verified fact.
- Keep typography and product on independent depth layers with visible spacing. Allow at most one brief occlusion on a non-critical outer contour; never cover a connection, control, Logo or identifying feature, and restore the complete product and complete text immediately afterward.
- Apply plastic, glass, fracture, scan, 3D blocks, collage and portals only outside the protected product layer. Product motion may translate or rotate the intact object; it may not become a slice field, a type carrier, a portal or a source of detached fragments.
- Run `PRODUCT_STRUCTURE_CONFLICT_SCAN` before dispatch. If the Prompt cuts/detaches components, changes their count or assembly, makes an opaque region transparent, uses product structure/negative space as a portal, folds the product into type, or fuses it with typography, rewrite that action onto an independent carrier, background/foreground layer, light, shadow or reflection.
- Keep the protection check out of `SCENE_PACKAGING_COPY`, `COPY_DECK` and `TEXT_WHITELIST`; phrases such as “结构完整”“组件关系”“透明度保持” describe an internal guardrail, never the product's narrative or on-screen text.
- In rebuild mode for 9–15 seconds, show full view, 3/4 or side view, and one real detail/macro.
- In preserve mode, use only the angles and detail already present in the source; create power through type-camera motion, perspective, occlusion, carriers, color states and local light instead of inventing new product shots.
- Use text as wall/floor/independent frame/external portal/foreground/background across at least two relationships; do not derive a portal from product structure or place every word in negative space as a label.

## 11. Prompt Fragments

Use these fragments inside the main H3 prompt:

```text
subject_type: [product/person/logo/scene/mixed]
identity_lock: [required real features]
stage_mode: [matching mode]
space_mode: [preserve_source_space/rebuild_editorial_space/hybrid_local_set]
camera_anchor: [camera behavior]
lighting_anchor: [light behavior]
typography_relation: [text relation to the subject]
effect_source -> effect_destination
composition_states: [count and state progression]
```

For scene prompts, explicitly write the spatial skeleton. For person prompts, explicitly write face/hair/body/gesture. For logo prompts, explicitly write legibility and geometry. For original footage, explicitly write what stays unchanged.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
