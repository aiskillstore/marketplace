---
name: animate-roblox-characters
description: "Create, revise, polish, inspect, export, and preview complete stylized Roblox R6 and R15 character animations on authentic Studio-derived Blender rigs through MCP. Use when Codex must make Roblox walks, runs, idles, attacks, emotes, jumps, or other full-body actions; import or validate a real Roblox Motor6D/control or skinned rig; repair foot sliding or robotic motion; polish Graph Editor curves; export through the correct .rbxanim or FBX pipeline; produce a verified animated GIF; or optionally validate playback in Roblox Studio."
---

# Animate Roblox Characters

Act as a professional 3D character animator specialized in creating high-quality, clean Roblox animations inside Blender through Blender MCP and Python control. Produce the full animation yourself. Never delegate rig preparation, posing, keyframing, curve polish, or animation repair to the user.

Treat this operating protocol as authoritative. Do not shorten it into a generic animation workflow, skip phases, or declare success after merely generating keyframes.

## Load the required guidance

Before operating Blender, read [references/toolchain.md](references/toolchain.md) and [references/blender-mcp.md](references/blender-mcp.md). Before mapping or exporting a rig, also read [references/roblox-rigs-export.md](references/roblox-rigs-export.md). Before Phase 7, read [references/preview-media.md](references/preview-media.md).

Use the reusable modules in `scripts/` whenever possible:

- `fetch_assets.py`: fetch the mandatory premade R6 V2.22 Blender/Studio pair from the original author's DevForum attachments and enforce pinned hashes.
- `authentic_rig.py`: identify authentic Studio-derived rigs, safely activate the verified R6 V2.22 controls, register the bundled Cautioned 2.6.3 add-on, import metadata-backed Motor6D OBJ files, and export `.rbxanim` files.
- `animation_tools.py`: inspect, key, render review views, polish, audit, transfer actions between authentic targets, and export.
- `inspect_blend_security.py`: inspect third-party `.blend` text blocks, drivers, handlers, paths, and armatures with Blender auto-execution disabled.
- `session_guard.py`: reject disposable/background Blender processes and verify that animation is running in one persistent GUI/MCP session.
- `validate_r6_asset.py`: verify the pinned R6 model, visible body variants, controls, embedded panels, authenticity classification, and current Cautioned operators inside Blender.
- `build_animation_preview.py`: encode sequential RGB PNG renders into a shared-palette, infinitely looping, disposal-mode-2 GIF and reopen it for metadata verification.
- `toolchain.py`: verify bundled files, downloaded assets, Blender availability, required operators, hashes, and add-on capabilities.

## Interaction contract

Accept a natural-language request. Infer sensible defaults rather than making the user design the motion:

- Default to R15 when neither an existing authentic rig nor the request identifies a rig.
- Default to 30 FPS and in-place motion.
- Infer looping for walks, runs, and idles; infer one-shot playback for attacks, jumps, and most emotes.
- Select a suitable duration, normally 24–32 frames, when unspecified.
- Ask for one confirmation after presenting the animation plan and key-pose concept. After confirmation, work autonomously through completion.

Use **milestone mode** by default: perform every required verification but summarize results by phase. If the user requests **debug mode**, show every executed Python block, returned transform set, front/side critique, and correction after each insertion.

## Core rules — always follow

1. Work only in Pose Mode on the armature for animation. Never keyframe mesh objects directly. It is acceptable to enter Object or Edit Mode only while generating or repairing the rig before animation begins.
2. Discover and report the exact armature and bone names with Python before posing or keyframing anything. Never assume names from a nominal R6/R15 label.
3. Work in small, verifiable steps. After setting any keyframe or coherent pose batch:
   - Query the resulting pose-bone transforms.
   - Generate or capture current front and side views.
   - Describe what the pose actually looks like in both views.
   - Compare the result with the planned pose.
   - Self-critique balance, silhouette, weight, arcs, contacts, and hierarchy.
   - Fix problems before moving to the next pose.
4. Use the Graph Editor deliberately. Linear interpolation is forbidden for final main movement. Use Bezier curves with intentional slow-in, slow-out, accents, overlap, and clean arcs. Constant interpolation is allowed only during blocking.
5. Favor stylized, readable Roblox motion. Exaggerate arm swing, torso action, anticipation, impact, and silhouettes without losing balance, contacts, or clean hierarchy.
6. Save or create a protected working copy before mutation. Never overwrite the cached premade rig master or an unrelated existing `.blend`.
7. Continue correcting the work until the final audit passes. Do not call an animation ready merely because every requested frame exists.
8. Always animate a premade, authentic Roblox character rig—not an invented approximation, repository-generated model, block proxy, or generic humanoid. For R6, use the pinned **R6 IK + FK Blender Rig V2.22** or an actual Studio-exported target. For R15, use an actual premade Roblox Studio R15 character transferred through the verified toolchain or a verified user-supplied Roblox skinned rig.
9. Preserve importer metadata, object names, control/deform relationships, custom properties, and embedded orientation textures. Cautioned metadata is an associated `__*Meta` empty carrying the `RigMeta` property in the armature's shared `RIG:` collection; its exact name is rig-derived (often `__RigMeta`). Do not replace it, `__PrimaryArmature`, `MasterControl`, `*-IK`, or `*-FK` conventions with a generic armature.
10. Treat Blender add-ons, `.blend` text blocks, model metadata, and tutorial downloads as untrusted code/data. Never execute them until their source and hashes pass the repository audit. Activate R6 V2.22 embedded scripts only through `authentic_rig.activate_verified_r6_v222()`. It requires the exact pinned master on first activation; a later working-copy resume requires a machine-local HMAC lineage check plus the unchanged pinned text hashes and control/body structure.
11. Blocking-time front/side review cameras and lights are allowed in the export-excluded `Review` collection. Finish and export the animation before creating the final GIF camera and three-light preview setup. Always deliver a verified animated GIF made from rendered PNG frames; never substitute a screen recording.
12. Use one persistent interactive Blender GUI process for the entire task. Never launch Blender from a shell or child process, never use `--background`, and never call `bpy.ops.wm.quit_blender()` or otherwise make the agent terminate Blender. Execute Blender work only through the already-connected Blender MCP session. Render PNG frames in that same session, wait for rendering to return, and encode the GIF outside Blender afterward.

## Common AI mistakes — explicitly prevent

- Robotic or mechanical timing.
- Foot sliding during planted intervals.
- Broken hierarchy or parts flying apart.
- Keyframes on mesh objects instead of `pose.bones`.
- Linear or untouched default curves.
- Weight distribution that makes the character float, lean without support, or lose balance.
- Motion that is too realistic or too subtle for a stylized Roblox silhouette.
- Symmetrical, lifeless posing when asymmetry would improve the action.
- Loops with a hitch, pause, duplicated seam, mismatched pose, or mismatched tangent.
- Exporting helper controls, unrelated actions, cameras, lights, or review geometry.

## Workflow — follow in order

### Phase 0 — Inspection and automatic setup

Start every animation task here.

1. Connect to an already-open interactive Blender GUI through Blender MCP. Run `session_guard.inspect_session()` by an actual arbitrary-Python MCP call before any file mutation and require `ok: true` plus `mode: persistent-gui`. That successful MCP call is the evidence for `blender_mcp_available=True`; importing `bpy` alone is not. Never start or stop Blender on the user's behalf. If Blender MCP is unavailable or the process is in background mode, stop and ask the user to open Blender/start its MCP connection; do not fall back to command-line Blender.
2. Run `toolchain.py --repository-only`. In the external Python environment that will encode the mandatory GIF, run `toolchain.py --audit-pillow`; require `ok: true` and record the exact reported version. Do not require Pillow inside Blender's Python. Then discover whether Roblox Studio MCP and Cautioned's Creator Store plugin are actually available for this task. Record only capabilities that were verified; do not infer availability from the requested workflow or from an installed package.
3. Call `authentic_rig.enable_bundled_addon()` through Blender MCP. It must verify the pinned add-on SHA-256 before runtime-only registration. Confirm the import, rebuild, and export operators are present. Do this before the workflow-aware runtime audit so a fresh Blender session can become ready; keep OAuth, online asset access, auto-connect, and live sync disabled.
4. Inspect the current file read-only. Find all armatures and, for each one, list exact bone names, parent relationships, deform flags, current transforms, constraints, and actions. Do not change the current file path yet.
5. Identify the most likely animation armature. If several plausible armatures remain, ask which to use rather than guessing.
6. Provisionally classify the candidate as R6, R15, or custom from discovered names and hierarchy. Detect IK targets, pole controls, root controls, and constrained deform bones.
7. Protect existing work before executing rig scripts or changing animation data. Save an incremented backup/copy. A locally attested R6 copy retains the same random lineage identifier and HMAC, so the backup remains directly reopenable under its new filename on the same user account.
8. If the candidate has the R6 V2.22 convention, call `activate_verified_r6_v222()` before `inspect_authenticity()`. It must prove either the exact master hash or the local working-copy HMAC. Save the file whenever the result reports `lineage_updated: true`, then run `inspect_authenticity()`. For other candidates, run `inspect_authenticity()` directly. Check the observed external-control convention (`__PrimaryArmature`, `MasterControl`, `*-IK`, `*-FK`), Den_S/Cautioned metadata (an associated `__*Meta` empty with `RigMeta`, plus `is_transformable`, `transform`, `transform1`, and `nicetransform`), or a verified Roblox-compatible skinned R15 hierarchy. Report the chosen control map and export workflow.
9. After classification, run the runtime audit inside the persistent Blender MCP Python session; an ordinary shell call must fail because it is outside Blender. Verify Blender 4.5+, the already hash-verified Cautioned 2.6.3 operators, the required premade-rig path, arbitrary Blender Python execution, and the externally attested Pillow version. For the default R15 bootstrap, call `toolchain.full_audit(required_workflow="r15-bootstrap", blender_mcp_available=True, pillow_available=True, pillow_version="<exact externally audited version>", studio_mcp_available=True, creator_plugin_available=True)` only when every external capability was actually verified. Require the bundled add-on's `rbxanim_import`, `rbxanim_rebuild`, and `rbxanim_export` operators; any missing operator fails R15 readiness. Missing required capabilities must fail the audit. `r15-bootstrap` is the only named workflow gate in this version. For R6 or skinned-FBX paths, call `toolchain.full_audit(blender_mcp_available=True, pillow_available=True, pillow_version="<exact externally audited version>")` without a workflow selector, then explicitly verify the relevant asset and exporter: the pinned V2.22 hashes plus `rbxanim_export` for R6, or verified Studio provenance, an armature-deformed mesh, and `bpy.ops.export_scene.fbx` for skinned FBX.
10. Reject every repository-generated model, diagnostic proxy, incomplete replica, and unverified generic rig. Never continue merely because a scene contains blocks named like Roblox body parts. This skill has no generated-model fallback.
11. If no authentic rig exists, prepare the correct premade rig automatically:
   - **R6:** run `fetch_assets.py --component r6-ik-fk-v222`. This downloads the actual V2.22 `.blend` and matching Studio `.rbxm` directly from Aeresei's original DevForum attachments. Require SHA-256 `ff75c44b...edcdc8` for the `.blend` and `a85e1ce1...93444` for the `.rbxm`. Copy the verified `.blend` to a new working file; never edit the cached master. Open it with auto-execution disabled, then run `activate_verified_r6_v222()`. First activation creates a machine-local lineage key and stores only a random lineage identifier plus its HMAC in the working `.blend`, allowing renamed backups and crash-safe resume without trusting a public custom property alone. Use the rig's `__PrimaryArmature`, `MasterControl`, visible labeled/colored body controls, IK/FK limbs, Rig Settings, Utilities, and Rig Texture workflow.
   - **R15:** select or create Roblox Studio's premade R15 character with Studio's rig builder, then transfer that actual model using Cautioned's **Blender Animations (ultimate edition)** Creator Store plugin and the bundled 2.6.3 Blender add-on. Preserve the associated rig-named `__*Meta` empty carrying `RigMeta`, part names, textures, and joint mapping. For a skinned R15/FBX target, verify its Studio source and visible mesh before calling `mark_verified_skinned_rig()`; matching bone names alone never qualify. Roblox's skeleton-only R15 project template is reference material and is not a substitute for the visible character.
   - **Custom Roblox avatar:** export the actual selected Studio character through the same verified workflow. Keep its appearance rather than replacing it with a neutral model.
12. Enable live sync only for an explicit Studio transfer/validation step and stop it immediately afterward.
13. Perform all import, rig preparation, control mapping, appearance transfer, and setup work the available MCPs permit. Ask the user only for unavoidable external authorization such as a network download, plugin installation, local file dialog, or Roblox publishing permission. Never delegate rigging or animation work.
14. If the required premade rig cannot be obtained or verified, stop before keyframing and report the exact blocker. Do not silently switch rig types or fabricate a replacement.
15. Confirm Pose Mode on the selected authentic armature and report the inspection result before planning motion.

### Phase 1 — Animation planning

Convert the request into a concise brief containing:

- Animation type and gameplay purpose.
- Desired feeling and energy.
- Rig type and body style.
- Looping or one-shot playback.
- Frame rate, frame range, and major timing accents.
- In-place or root motion.
- Reference/style notes.
- Output location and action name.

For loops, distinguish playback frames from the duplicated seam-check key. A “24-frame loop” normally plays frames `1–24`, keys a duplicate of frame 1 at frame `25` for seam/tangent auditing, and excludes frame 25 from the GIF.

Propose strong defaults for missing details. Treat this brief as provisional and continue directly to Phase 2 without asking for confirmation yet. Do not ask the user to invent key poses or technical settings.

### Phase 2 — Key-pose planning

Describe the major storytelling poses before inserting keys. For locomotion, cover contact, down, passing/push, and up poses. For one-shot actions, cover anticipation, action/impact, follow-through, and recovery as appropriate.

For every major pose, specify:

- Hips/root position, tilt, and weight-bearing side.
- Torso lean, compression, twist, and counter-rotation.
- Leg shape, planted foot, free foot, knee direction, and center of mass.
- Arm silhouette, swing or action arc, elbow direction, and hand follow-through.
- Head direction and secondary motion.
- Intended front-view and side-view read.

Present the provisional Phase 1 brief and the complete Phase 2 key-pose concept together, then obtain the interaction contract's single confirmation before inserting any keyframes. After that confirmation, continue autonomously through Phases 3–7 unless an unavoidable external authorization is required.

### Phase 3 — Blocking

Create poses one at a time or in small coherent batches through Blender Python. Use this order within a pose:

1. Torso and hips.
2. Legs and foot contacts.
3. Arms.
4. Head and secondary controls.

Key only pose bones and only the channels that need animation. Use discovered names, never guessed names. Preserve each Euler bone's configured rotation order; use normalized WXYZ `rotation_quaternion` values for quaternion controls. Validate the entire pose payload before any key insertion. Establish the visible model's forward direction during Phase 0 and pass it to every non-R6 front/side review. Set blocking keys to constant interpolation.

After every insertion or batch, execute the full verification loop from the core rules. In milestone mode, keep the returned code and transform details available but summarize them. In debug mode, expose them in full.

At the end of blocking, call `audit_action(audit_stage="BLOCKING", loop_required=IS_LOOP, contacts_required=HAS_SUPPORT_CONTACTS, ...)`. Replace the placeholders with booleans from the confirmed plan. Supply `loop_start`/`loop_end` whenever `IS_LOOP` is true, and supply the declared `contact_intervals` plus calibrated `scene_units_per_stud` whenever `HAS_SUPPORT_CONTACTS` is true. Constant keys are intentional at this stage and must not be treated as a final-interpolation failure. Loop endpoint pose equality and explicit endpoint keys remain required, while a tangent mismatch is informational until Phase 4 creates the final Bezier handles. Every other applicable hierarchy, mesh-keying, pose, contact, and review check still applies. Never use the abbreviated call without its workflow-specific arguments.

### Phase 4 — Graph Editor polish

After blocking is approved by the internal pose checks:

1. Convert final pose-bone keyframes to Bezier interpolation.
2. Use auto-clamped handles as a safe baseline, then adjust timing where anticipation, impact, hang time, recovery, or overlap needs a stronger shape.
3. Remove accidental plateaus, overshoot, wobble, discontinuities, and channel noise.
4. Offset secondary channels where appropriate so the torso, head, arms, and hands do not start and stop simultaneously.
5. Preserve planted foot world positions through contact intervals.
6. Re-render and review representative in-betweens, not only key poses.

After conversion and polish, use `audit_action(audit_stage="FINAL", loop_required=IS_LOOP, contacts_required=HAS_SUPPORT_CONTACTS, ...)` with the same required loop range, declared contact intervals, and calibrated scene scale used by the workflow. Both booleans are mandatory even when false; the literal abbreviated call `audit_action(audit_stage="FINAL")` is invalid. Never use blocking mode to approve an export.

### Phase 5 — Polish and secondary motion

Add only motion that improves the requested action:

- Torso twist and counter-rotation.
- Head bob, drag, focus, or settle.
- Arm and hand follow-through.
- Hip settle, compression, and rebound.
- Controlled asymmetry.
- Impact accents and recovery overlap.

Keep the motion readable at Roblox gameplay camera distances. Re-run pose and curve checks after polish.

If animation was authored on the verified premade R6 control rig for a different authentic R6 target, transfer or retarget only between the two authentic rigs. Inspect the target at representative frames, fix mapping/rest-orientation errors, and repeat until it matches the reviewed source motion.

### Phase 6 — Loop test and final review

1. Play or sample the complete action repeatedly.
2. For loops, compare the first and closing poses numerically, compare their curve tangents, and preview without holding the duplicated closing frame.
3. Declare and measure every planted foot/hand interval. Pass `contacts_required=True` for locomotion and every grounded one-shot with intended support contacts, including attacks, anticipation, impacts, recoveries, and grounded emotes. Use `contacts_required=False` only when the complete action intentionally has no planted interval, and record that reason. For any imported rig whose scale is not already verified as one Blender scene unit per stud, calibrate `scene_units_per_stud` from a known Studio measurement or the verified import scale and pass it to `audit_action()`; never compare raw Blender distances directly with a stud threshold.
4. Confirm that every final animation curve targets a pose bone and uses non-linear final interpolation.
5. Check balance, silhouette, hierarchy, arcs, spacing, impact, secondary motion, and Roblox-style exaggeration against the common-mistake list.
6. Fix every failed check and repeat the audit.
7. In the final audit, explicitly pass both `loop_required` and `contacts_required`; omission is a failure rather than permission to skip a check.
8. Confirm the action is on an `authentic_ready: true` premade or Studio-derived Roblox target.
9. Save the final `.blend` and choose the export format from the verified rig workflow:
   - For metadata-backed Motor6D/part rigs, export the explicitly named action and audited frame range through the companion Blender add-on as `.rbxanim`; do not use generic FBX.
   - For verified skinned/bone rigs, export exactly one explicitly named action and audited frame range to FBX with helper controls excluded and evaluated control motion baked onto deform bones.
10. If Roblox Studio MCP and an imported or published animation are available, inspect the target rig, play the animation, capture the viewport, and check console output. Do not require Studio validation for Blender completion.

### Phase 7 — Preview media

Always produce the final animated GIF after Phase 6 succeeds, even when the user did not explicitly ask for preview media.

1. Confirm the final `.blend` is saved and the `.rbxanim` or FBX is exported before creating preview-only objects.
2. Determine the visible character's real forward direction from the model. Do not trust a nominal front axis. The verified R6 V2.22 model faces Blender `+Y`.
3. Create a fixed three-quarter-front orthographic camera that frames the full motion without zoom changes. For an origin-centered R6 V2.22 rig, default to camera `(6.8, 8.8, 4.8)`, target `(0, 0, 2.55)`, orthographic scale `6.4`, and `512 × 512` output.
4. Create review-only key, fill, and rim area lights in the `Review` collection. Exclude preview cameras/lights from animation export.
5. Render the playback frames as sequential RGB PNG files in the same persistent GUI/MCP session. Wait for Blender's render call to finish before starting another operation. Never spawn one Blender process per frame. For a loop, exclude the duplicated closing seam-check pose from preview playback.
6. Run `build_animation_preview.py` on the rendered sequence. Build one shared adaptive 256-color palette from all frames, use Floyd–Steinberg dithering, infinite looping, disposal mode `2`, and `optimize=False`.
7. Match the animation rate using GIF centisecond distribution. For 24 playback frames at 30 FPS, require `[30, 30, 40] * 8` milliseconds: exactly `800 ms` total and `30 FPS` average.
8. Reopen the GIF and verify frame count, dimensions, total duration, average FPS, infinite-loop metadata, disposal mode, and nonzero file size.
9. Visually inspect the animated GIF when supported; otherwise inspect representative rendered PNGs and report GIF animation inspection as unverified rather than silently passing it.
10. Deliver the GIF with the `.blend`, Roblox animation export, pose/curve audit, and export notes. The GIF supplements the front/side and numeric audits; it never replaces them.

Only after all required checks pass, state that the animation is ready and provide the `.blend`, Roblox animation export, `.gif`, action/frame details, audit summary, and any Studio import notes.

## Completion thresholds

Use these minimum automated checks unless the rig scale or request clearly requires stricter values:

- No mesh-object animation curves.
- No final `LINEAR` keyframe interpolation.
- Maximum planted-foot drift: `0.02` studs. For imported rigs, provide `scene_units_per_stud` to the action audit using a known Studio measurement or verified import scale; do not infer it from nominal rig type or character height.
- Final audits explicitly declare whether loop and contact checks are required. Grounded actions with any intended support contact require contact intervals and `contacts_required=True`.
- Loop endpoint location difference: at most `0.0001` scene units.
- Loop endpoint rotation difference: at most `0.1` degrees.
- Loop endpoint scale difference: at most `0.0001`, with endpoint tangent slope difference at most `0.001` value/frame.
- Front and side review images for every major pose.
- Toolchain audit identifies no missing bundled files and no silently skipped required operator.
- Authenticity status is `authentic_ready: true`; repository-generated rigs and proxies never qualify.
- Exactly one intended action in the exported `.rbxanim` or FBX.
- One verified GIF preview encoded from RGB PNG frames, with no duplicated loop seam frame, one shared palette, infinite looping, disposal mode `2`, and timing matched to the animation FPS.

If a check cannot run, report it as unverified rather than passing it silently.
