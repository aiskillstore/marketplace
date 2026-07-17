# Authentic Roblox Rigs and Export

Read this before importing, selecting, or exporting a character.

## R6: the colored/labeled workflow

The intended premade rig is Aeresei's [R6 IK + FK Blender Rig V2.22](https://devforum.roblox.com/t/r6-ik-fk-blender-rig-v222/3586405), not a six-box approximation. Verified identifiers include:

- `__PrimaryArmature` with `_Rbx_R6_Rig_` marker.
- `InternalArmature` with Roblox parts `HumanoidRootPart`, `Torso`, `Head`, `Left Arm`, `Right Arm`, `Left Leg`, and `Right Leg`.
- `MasterControl`, `LowerTorso-FK`, limb `*-IK`/`*-FK` controls, pole targets, grab points, and head target.
- Custom viewport control shapes and body-type variants.
- Orientation-colored/labeled body surfaces and the Rig Texture utility.
- Active Rig, Rig Settings, Utilities, Accessories, and weapon-sync scripts.

Install it with `fetch_assets.py`, copy the cached master, open with script auto-execution disabled, and call `activate_verified_r6_v222()`. The first activation requires the exact pinned master and creates a machine-local lineage key; the working `.blend` stores only a random lineage identifier and its HMAC. Renamed backups remain verifiable on the same user account. A reopened working copy must pass that HMAC plus pinned text-hash and structure checks before a new same-session receipt is issued. Animate `__PrimaryArmature` controls only. The matching Studio `.rbxm` is part of the pinned download and contains no Script/LocalScript/ModuleScript instances.

## R15 and custom avatars

For R15, use the actual premade Roblox Studio R15 or the requested player's existing character:

1. Discover the Studio MCP and Creator Store plugin capabilities. Report a missing capability as a blocker; do not claim it exists merely because the workflow expects it.
2. Hash-verify and register the bundled Cautioned 2.6.3 Blender extension, with its online features and live sync disabled. Confirm its import, rebuild, and export operators, then run the in-Blender workflow-aware toolchain audit for `r15-bootstrap`.
3. Through Roblox Studio MCP, create a stock premade R15 with Studio's rig builder when no target exists, or select the user's actual R15 character. Inspect the selected model's hierarchy before transfer.
4. Use Cautioned's [Blender Animations (ultimate edition)](https://create.roblox.com/store/asset/16708835782/Blender-Animations-ultimate-edition) from the Creator Store.
5. Prefer a temporary live-sync transfer. Start the Cautioned localhost server only for this transfer, initiate transfer of the selected Studio character through the installed Creator Store plugin, and wait until Blender contains the reconstructed armature and exactly one associated rig-named `__*Meta` empty carrying the `RigMeta` property in the same `RIG:` master collection (often `__RigMeta`). Stop the live-sync server immediately after the transfer finishes or fails.
6. If live sync cannot complete, use the Creator Store plugin's file-based OBJ transfer path. A local file dialog may require one user click, but the AI chooses and validates the selected Studio character, then passes the resulting OBJ to `authentic_rig.import_motor6d_obj(path)` in the persistent Blender MCP session. Require the reconstructed armature and its unambiguous associated `__*Meta` empty before continuing.
7. Preserve the associated metadata empty, object names, textures, accessories, and bone properties such as `is_transformable`, `transform`, `transform1`, and `nicetransform`.
8. Inspect and classify the imported armature before the first keyframe. Use `.rbxanim` for this metadata-backed Motor6D path.

Do not invent plugin button names or claim a successful transfer from a command invocation alone; verify the resulting Blender objects and metadata. The AI performs all importing, control mapping, posing, keyframing, polishing, auditing, and export work. Never delegate animation work to the user.

For the skinned/FBX route, export or receive the actual Studio R15 rather than substituting a generic humanoid. Import it with auto-execution disabled, inspect the visible character, confirm an armature-deformed mesh and the expected hierarchy, and establish its Studio origin. Matching R15 bone names and a mesh are not sufficient proof. Only after those checks, call `mark_verified_skinned_rig(armature_name, source)` with `studio-rig-builder`, `studio-export`, or `user-verified-studio-export`. Do not set the provenance property directly. This route exports FBX and does not use Motor6D mapping.

Do not use Roblox's skeleton-only project template as the visible character. Do not generate replacement body geometry.

## Stud-to-scene-unit calibration

Contact drift is specified in Roblox studs, while Blender reports scene-space distances. Before auditing planted contacts on an imported rig, determine `scene_units_per_stud` from evidence tied to that exact import:

1. Measure a known distance on the selected character or a temporary reference in Studio and record it in studs.
2. Measure the corresponding distance in the imported Blender scene, or use an explicitly known uniform import scale.
3. Compute `scene_units_per_stud = blender_scene_distance / studio_distance_studs`. Require positive, finite values and repeat the measurement if the axes or import scaling are ambiguous.
4. Pass that value to `animation_tools.audit_action()` whenever contact intervals are audited. The audit converts the `0.02`-stud contact limit to scene units and should report both quantities.

For locomotion, make the required checks explicit rather than allowing omitted loop/contact inputs to pass:

```python
animation_tools.audit_action(
    armature_name=armature_name,
    action_name=action_name,
    loop_start=loop_start,
    loop_end=loop_end,
    contact_intervals=contact_intervals,
    contact_drift_threshold=0.02,  # studs
    scene_units_per_stud=scene_units_per_stud,
    loop_required=True,
    contacts_required=True,
)
```

For a grounded one-shot, pass `loop_required=False`, `contacts_required=True`, and every intended support-contact interval. Pass `contacts_required=False` only for an action with no planted interval at all. Every final audit must provide both booleans explicitly; omission fails.

Do not infer this conversion from the label “R15,” from character height, or from a visual guess. Recalibrate after any import-scale change.

## Motor6D part rigs: `.rbxanim`

Use `.rbxanim` for classic R6/R15 part rigs and the R6 V2.22 workflow:

1. Preserve the Cautioned/Roblox mapping metadata.
2. Animate only verified pose controls.
3. Keep the internal/deform armature constrained to the external controls.
4. Export the explicitly named action and audited frame range with `authentic_rig.export_rbxanim()` through `object.rbxanims_bake_file`.
5. Import/play the result through the matching Studio plugin.

Generic FBX export is not a substitute for Motor6D mapping.

## Skinned Roblox rigs: FBX

Use FBX only after inspection verifies an armature-deformed Roblox skinned character and its expected R15 hierarchy. Follow Roblox's [Blender guidance](https://create.roblox.com/docs/art/blender):

- Unit system `None`; rotation in degrees.
- `Z Forward`, `Y Up`.
- Select only the authentic armature and driven meshes.
- Disable leaf bones.
- Bake at one sample per frame with no simplification.
- Export exactly one active action; disable NLA-strip/all-action export.
- Export deform bones only, with evaluated control motion baked onto them.

## Authenticity results

`authentic_rig.inspect_authenticity()` recognizes:

- `community-r6-ik-fk-control-rig`: usable only after verified activation, full control/body structure, embedded-script hashes, and local working-copy lineage checks pass; Motor6D/`.rbxanim`.
- `studio-motor6d-import`: usable only with associated Cautioned/Studio metadata and verified operators; Motor6D/`.rbxanim`.
- `studio-or-fbx-skinned-r15`: usable only after visible-mesh inspection and explicit Studio-source verification; FBX.
- `generated-or-repository-proxy`: forbidden.
- `unknown` or `verify-before-export`: stop and verify.

Exact bone names must still be discovered at runtime.

## Studio validation

When Studio MCP and the imported animation are available:

1. Confirm the target hierarchy and rig type.
2. Load the animation on the target `Animator`.
3. Play several repetitions for loops.
4. Capture the viewport and inspect console output.
5. Fix ownership, permission, hierarchy, mapping, or playback errors before completion.

A local file dialog or publish permission may require one user authorization. Never delegate posing, keyframing, rigging, or curve polish.
