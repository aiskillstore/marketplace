# Roblox–Blender Toolchain

Read this during Phase 0. The machine-readable source and hash inventory is `assets/toolchain-manifest.json`.

## Required stack

| Component | Purpose | Policy |
|---|---|---|
| Blender 4.5+ | Pose Mode, Graph Editor, rendered review, export | Install from Blender.org. Blender 4.5 LTS is recommended because the R6 asset targets that line and a persistent LTS GUI avoids disposable-process teardown instability. |
| Blender MCP 1.6.4 | AI control through Blender Python | External MIT package. Localhost only; telemetry and remote asset integrations off. |
| Pillow `>=10,<13` | Shared-palette GIF encoding and verification | External HPND Python library. Read local PNG renders and write the preview GIF only. |
| R6 IK + FK Blender Rig V2.22 | Premade visible R6 model, colored/labeled controls, IK/FK, panels | Mandatory for generic R6 work. Fetch only from Aeresei's original DevForum attachments with `fetch_assets.py`. Do not mirror it in Git because no redistribution license is stated. |
| Premade Studio R15 | Actual visible R15 target | Mandatory for R15. Use Studio's rig builder or the user's existing character, then export it. Never replace it with generated geometry. |
| Cautioned Blender Animations 2.6.3 | Import/export, mapping, IK/control support, `.rbxanim` | Bundled unmodified signed-release zip under GPL-3.0-or-later; SHA-256 verified. |
| Blender Animations (ultimate edition) | Studio side of the Motor6D transfer | Install only from Cautioned's Creator Store listing. |
| Roblox Studio MCP | R15 bootstrap and optional playback validation | Use Roblox's built-in MCP. |

## Premade-model rule

There is no repository-generated Roblox model and no block-proxy fallback.

- R6 begins from the actual V2.22 author rig. It contains `__PrimaryArmature`, `InternalArmature`, `MasterControl`, IK/FK limb controls, custom control shapes, body variants, colored orientation faces, and the Active Rig/Rig Settings/Utilities/Rig Texture panels seen in the reference workflow.
- R15 begins from a premade Roblox Studio character. Cautioned's Studio and Blender tools reconstruct the actual target and preserve Motor6D mapping.
- A custom avatar begins from that avatar's Studio export. Preserve appearance, accessories, joint metadata, and texture mapping.
- Roblox's official R15 “rig and attachments” project is skeleton/reference material only. It is not a visible-player substitute.

If the requested premade rig cannot be obtained or verified, stop before keyframing.

## Pinned R6 installation

Run with network authorization:

```sh
python3 animate-roblox-characters/scripts/fetch_assets.py --component r6-ik-fk-v222
```

The downloader accepts only allowlisted HTTPS hosts, writes through a temporary file, checks byte size and SHA-256, and refuses to overwrite an unverified local file. It installs the asset into the ignored `assets/external/` cache. Always copy the cached master into the animation project before editing.

Open the copied exact master with Blender script auto-execution disabled. Then call `authentic_rig.activate_verified_r6_v222()`. First activation verifies the complete pinned `.blend` and every embedded text block before registering the UI/control scripts. It also creates a random 32-byte key in the version-independent per-user `.animate-roblox-characters` configuration directory and stores only a random lineage identifier plus its HMAC in the working `.blend`. Blender 4.5 and newer releases on the same user account share this key. On crash recovery, the helper requires that local HMAC and revalidates the pinned scripts and control/body structure before issuing a same-session receipt. The key is never bundled, logged, or written into an animation file. Never click “Allow Execution” on an unverified copy.

The HMAC is bound to the random lineage identifier rather than a filename. Save after any activation result with `lineage_updated: true`; afterward, incremented backups and same-session Save As copies remain directly verifiable on the same user account.

If the per-user lineage key is unavailable after a machine/account migration, do not bypass the check or copy custom properties. Open the old file with script auto-execution disabled, inspect it, load only its named armature Action datablock into a fresh exact-master working copy, activate that fresh copy, and repeat the pose/curve/audit/export checks before delivery.

## Cautioned 2.6.3 security boundary

The bundled `rbx_anims_v2.6.3.zip` is the unmodified current GitHub release. Static review found:

- Roblox OAuth and asset-delivery networking.
- A live-sync HTTP server bound to `127.0.0.1`.
- Permissive CORS on that optional local server.
- No process-spawning imports in the release.

`authentic_rig.enable_bundled_addon()` verifies the zip and registers it without starting OAuth or the live-sync server. Keep online access, auto-connect, and live sync off during ordinary authoring. When Studio transfer requires live sync, start it only for that operation, do not browse untrusted sites while it is running, and stop it immediately afterward.

## Blender MCP boundary

Blender MCP intentionally allows arbitrary local Python execution:

1. Bind it to loopback only.
2. Verify the pinned package hash from the manifest.
3. Disable telemetry and third-party asset download integrations.
4. Open one interactive Blender GUI and keep that process alive throughout inspection, animation, rendering, export, and saving.
5. Run `session_guard.inspect_session()` through MCP and require `mode: persistent-gui` before mutation.
6. Never invoke Blender with `--background`, spawn it as a child process, or call Blender's quit operator.
7. Save an incremented working copy before mutation.
8. Execute repository modules or short reviewed pose blocks only.
9. Never expose Blender MCP or the Cautioned live-sync port to a LAN or the internet.

## Audits

```sh
python3 animate-roblox-characters/scripts/toolchain.py --repository-only
python3 animate-roblox-characters/scripts/toolchain.py --audit-pillow
python3 animate-roblox-characters/scripts/toolchain.py --audit-archive <addon.zip>
python3 animate-roblox-characters/scripts/toolchain.py --audit-addon <candidate.py>
```

Run the first audit for offline repository readiness. Run `--audit-pillow` with the external Python environment that will execute `build_animation_preview.py`; require `ok: true` and record its exact `pillow_version`. Pillow is deliberately verified outside Blender because GIF encoding is external and Blender's bundled Python need not contain Pillow. After discovering external capabilities and classifying the rig, run the full audit through the persistent Blender MCP Python session. Pass `blender_mcp_available=True` only after an actual Blender MCP arbitrary-Python call succeeds; importing `bpy` by itself does not prove MCP connectivity. Runtime readiness requires both this external MCP attestation and an in-process persistent-GUI Blender check.

Do not run the workflow-aware readiness audit as an ordinary shell command: a shell process is outside Blender and must fail the in-process check. The CLI keeps workflow and capability switches for controlled embedding and test harnesses, but the in-process call below is the sole runtime-readiness procedure.

`r15-bootstrap` is the only named workflow gate in this version. It additionally requires Studio MCP, the Creator Store animation plugin, and all three bundled add-on operators (`rbxanim_import`, `rbxanim_rebuild`, and `rbxanim_export`); an unavailable operator is an error. Pass each availability boolean as true only after that capability has actually been verified. A missing attestation is a failed workflow requirement, not an optional warning. The audit verifies availability claims—it does not replace object and metadata inspection after transfer. For R6 or skinned-FBX paths, omit `required_workflow`, retain the verified Blender MCP and Pillow attestations, and explicitly verify the relevant source and export path: the pinned V2.22 hashes plus the `rbxanim_export` operator for R6, or verified Studio provenance, an armature-deformed mesh, and `bpy.ops.export_scene.fbx` for skinned FBX.

The in-process equivalent for the default R15 path is:

```python
toolchain.full_audit(
    required_workflow="r15-bootstrap",
    blender_mcp_available=True,
    pillow_available=True,
    pillow_version="12.3.0",  # Use the exact version reported by --audit-pillow.
    studio_mcp_available=True,
    creator_plugin_available=True,
)
```

Pass `blender_mcp_available=True` only from code already executing through the discovered Blender MCP connection. Pass the Pillow values only after the separate external audit succeeds; the in-Blender audit consumes that attestation and does not import Pillow. For a non-R15 path, call `toolchain.full_audit(blender_mcp_available=True, pillow_available=True, pillow_version="12.3.0")` through that connection using the exact reported version, then perform the explicit rig and exporter checks described above.

For an untrusted `.blend`, disable Blender's script auto-execution, open the file in the persistent GUI, and call `inspect_blend_security.inspect_current_file()` through MCP. Static review reduces risk but does not prove arbitrary third-party code safe.
