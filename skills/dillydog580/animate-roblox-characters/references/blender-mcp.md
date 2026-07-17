# Blender MCP Operations

Read this file before sending Blender commands.

## Capability contract

Require an MCP tool that can execute arbitrary Python inside the open Blender process. Common compatible shapes include `execute_blender_code` and `blender_python_exec`. Tool names are not stable across MCP implementations, so discover capabilities rather than hard-coding one server name.

Use exactly one persistent interactive Blender GUI process for the complete task. Before mutation, call `session_guard.inspect_session()` through MCP and require `ok: true` and `mode: persistent-gui`. Do not start Blender through a shell, `subprocess`, OS application launcher, or an MCP helper that creates a disposable process. Do not use `--background`, call `bpy.ops.wm.quit_blender()`, or terminate Blender after export. A native renderer/image-library crash during process teardown cannot be recovered by Python.

Viewport screenshots are useful but optional. When no screenshot tool exists, use `animation_tools.render_pose_views()` to render deterministic front and side review images through Blender itself.

Pose-review cameras/lights may be created during blocking only inside the export-excluded `Review` collection. The final GIF camera and three-light setup remain Phase 7 work after export.

Do not enable Blender MCP asset-download features, API keys, or external model services. Use only the pinned `fetch_assets.py` path for the mandatory R6 asset. Bind Blender MCP to localhost, pin the manifest version, and disable all prompt, code, screenshot, and usage telemetry. Arbitrary Python execution is equivalent to local code execution with Blender's user privileges.

## Calling the bundled modules

Resolve the installed skill directory at runtime; never paste a developer's absolute path into generated files or documentation.

For MCPs that accept inline Python, use the equivalent of:

```python
import sys
sys.path.insert(0, SKILL_SCRIPTS_DIRECTORY)
from animation_tools import inspect_scene
__result__ = inspect_scene()
```

For MCPs that accept a script path, call the bundled module directly if the skill directory is an approved script root. If safe mode restricts script paths, copy the module into the animation project's working directory first.

All public functions return JSON-serializable dictionaries with these stable top-level keys when relevant:

- `ok`
- `rig_type`
- `armature`
- `bones`
- `metrics`
- `artifacts`
- `warnings`
- `errors`

Treat `ok: false`, non-empty `errors`, or a required `unverified` metric as a failed step.

## Safe transaction order

1. Run `session_guard.inspect_session()` and reject background/not-in-Blender modes.
2. Run `inspect_scene()` before mutation.
3. If the scene contains unrelated work, save an incremented working copy.
4. Run `authentic_rig.inspect_authenticity()` on the selected armature. Animate only when `authentic_ready` is true.
5. If no authentic rig exists, install/copy the pinned premade R6 rig or transfer a premade Studio R15 as described in `roblox-rigs-export.md`. Never generate a substitute.
6. Run `apply_pose()` with a single pose or coherent body-group batch.
7. Require the returned transforms and review renders before the next batch.
8. Run `polish_curves()` only after blocking.
9. Run `audit_action(audit_stage="BLOCKING")` after blocking so intentional constant keys are permitted while hierarchy, mesh-keying, and other supplied checks still run. After polish and immediately before export, run `audit_action(audit_stage="FINAL", loop_required=..., contacts_required=...)`; final mode requires both booleans explicitly and rejects every constant or linear key.
10. Retarget only between two verified authentic Roblox rigs, then visually verify the target.
11. Save the working `.blend`, then use `export_rbxanim()` for Motor6D rigs or `export_fbx()` for verified skinned rigs.

Do not send a long monolithic script that creates the whole animation without checkpoints. A tool call may insert several coordinated keys for one pose, but it must return and be inspected before continuing.

## Pose payload

`apply_pose()` accepts a dictionary shaped like:

```python
{
    "armature": "Roblox_R15_Armature",
    "frame": 1,
    "interpolation": "CONSTANT",
    "bones": {
        "LowerTorso": {"rotation_degrees": [0, 0, -5]},
        "LeftUpperLeg": {"rotation_degrees": [18, 0, 0]},
        "CTRL_LeftFoot_IK": {"location": [0, 0, 0]},
        "QuaternionControl": {"rotation_quaternion": [1, 0, 0, 0]}
    },
    "render_directory": OUTPUT_REVIEW_DIRECTORY,
    "pose_label": "contact-left",
    "review_front_direction": [0, -1, 0]
}
```

Locations are local pose-bone offsets. Euler rotations use the bone's configured rotation order unless an explicit valid Euler `rotation_mode` is supplied. Quaternion rotations use normalized WXYZ order. Never include a name that was not returned by inspection. R6 V2.22 defaults to visible forward `+Y`; every other rig requires `review_front_direction` established from visual inspection.

## Visual critique requirements

Transforms alone cannot establish pose quality. Inspect both returned review images and explicitly evaluate:

- Front view: support base, center of mass, hip/shoulder counter-angle, symmetry, negative space, limb separation, and readable silhouette.
- Side view: forward lean, spine curve, heel/toe contact, knee direction, arm arc, head lead/drag, and whether the body appears grounded.

If image inspection and numerical transforms disagree, trust the evaluated image and correct the pose.

## Existing rigs

Never rename an existing user's bones merely to match a template. Build a role map from discovered names and hierarchy. Preserve `__PrimaryArmature`, the associated rig-named `__*Meta` empty carrying `RigMeta` in the shared `RIG:` collection, importer custom properties, orientation textures, and control shapes. If constraints exist, key controls; if a verified FK rig has no controls, key the deform pose bones directly. Never generate or substitute a character model.

## Failures

- Missing Python execution: stop before mutation and explain that Blender MCP is required.
- Background or disposable Blender process: stop before mutation and request an open GUI/MCP session. Never retry by launching another Blender process.
- Blender disappears or MCP disconnects during render: preserve completed files, do not auto-relaunch Blender, and ask the user to reopen the last saved working copy. Retry with Blender 4.5 LTS if the persistent GUI session remains unstable.
- Missing premade authentic target: obtain the pinned R6 or Studio R15; if it cannot be obtained or verified, stop before keyframing.
- Multiple plausible armatures: report exact names and request the target.
- Missing review render: retry once with Blender-rendered views, then mark visual review unverified.
- Export operator error: preserve the `.blend`, report the operator error, and do not claim an `.rbxanim` or FBX exists.
- Studio unavailable: complete Blender output and provide import notes without treating Studio as a failure.
