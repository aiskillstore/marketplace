# merge_anim_glbs.py — Blender CLI: merge single-clip GLBs (Meshy outputs)
# into one multi-clip GLB, with the MANDATORY root-bone scale fix.
#
# Usage:
#   blender -b -P merge_anim_glbs.py -- \
#       rigged.glb walk.glb:Walk run.glb:Run idle.glb:Idle attack.glb:Attack out.glb
#
# rigged.glb       — Meshy rigged_character_glb_url (mesh + skeleton, base)
# clipN.glb:Name   — Meshy animation GLBs (same skeleton), clip renamed to Name
# out.glb          — merged result
#
# VERIFIED BUG this script fixes: Meshy *library* animations (POST
# /openapi/v1/animations) can bake a scale factor into the root bone's scale
# channel (observed: Hips scale 1.176 on idle while walk/run from the rig
# were 1.0) — the character visibly grows when the clip plays. Fix: zero the
# scale keys to 1.0 AND divide the same clip's root translation keys by the
# same factor (otherwise the character floats above ground).

import struct
import json
import sys

import bpy

SCALE_TOL = 0.02  # treat |scale-1| > 2% as the baked-scale bug


def get_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit(__doc__)
    args = argv[argv.index("--") + 1:]
    if len(args) < 3:
        raise SystemExit(__doc__)
    return args[0], args[1:-1], args[-1]


def import_clip(path, clip_name):
    """Import an animation GLB, keep its action (renamed), delete its objects."""
    before_objs = set(bpy.data.objects)
    before_acts = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=path)
    new_acts = [a for a in bpy.data.actions if a not in before_acts]
    if not new_acts:
        raise SystemExit(f"{path}: no animation found")
    act = max(new_acts, key=lambda a: len(a.fcurves))
    act.name = clip_name
    act.use_fake_user = True  # survive object deletion
    for extra in new_acts:
        if extra is not act:
            bpy.data.actions.remove(extra)
    bpy.ops.object.select_all(action="DESELECT")
    for o in set(bpy.data.objects) - before_objs:
        o.select_set(True)
    bpy.ops.object.delete()
    return act


def root_bone_name(arm):
    for b in arm.data.bones:
        if b.parent is None:
            return b.name
    raise SystemExit("armature has no root bone")


def fix_root_scale(act, root):
    """Detect & fix baked root scale; returns the factor or None."""
    scale_curves = [fc for fc in act.fcurves
                    if fc.data_path == f'pose.bones["{root}"].scale']
    if not scale_curves:
        return None
    vals = [kp.co.y for fc in scale_curves for kp in fc.keyframe_points]
    if not vals:
        return None
    factor = sum(vals) / len(vals)
    if abs(factor - 1.0) <= SCALE_TOL:
        return None
    for fc in scale_curves:
        for kp in fc.keyframe_points:
            kp.co.y = 1.0
            kp.handle_left.y = 1.0
            kp.handle_right.y = 1.0
        fc.update()
    for fc in act.fcurves:
        if fc.data_path == f'pose.bones["{root}"].location':
            for kp in fc.keyframe_points:
                kp.co.y /= factor
                kp.handle_left.y /= factor
                kp.handle_right.y /= factor
            fc.update()
    return factor


def main():
    base_path, clip_args, out_path = get_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bpy.ops.import_scene.gltf(filepath=base_path)
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not armatures:
        raise SystemExit("base GLB has no armature — use the rigged_character GLB")
    arm = armatures[0]
    base_acts = list(bpy.data.actions)  # base may carry its own clip(s)

    clips = []
    for spec in clip_args:
        if ":" in spec:
            path, name = spec.rsplit(":", 1)
        else:
            path, name = spec, spec.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        clips.append(import_clip(path, name))
        print(f"imported clip '{name}' from {path}")

    root = root_bone_name(arm)
    for act in clips + base_acts:
        factor = fix_root_scale(act, root)
        if factor:
            print(f"FIXED baked root scale in '{act.name}': {factor:.4f} -> 1.0 "
                  f"(translation divided by the same factor)")

    # all actions -> NLA tracks on the base armature
    if arm.animation_data is None:
        arm.animation_data_create()
    ad = arm.animation_data
    ad.action = None
    for act in clips + base_acts:
        track = ad.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, max(int(act.frame_range[0]), 0), act)
    print(f"NLA: {len(clips) + len(base_acts)} clips on '{arm.name}' (root bone: {root})")

    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_yup=True,
        export_apply=False,
    )

    # stdlib OPAQUE/doubleSided patch (the "inverted normals" fix)
    MAGIC, CHUNK_JSON = 0x46546C67, 0x4E4F534A
    with open(out_path, "rb") as f:
        data = f.read()
    chunks, off = [], 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunks.append((ctype, data[off + 8: off + 8 + clen]))
        off += 8 + clen
    body = b""
    for ctype, payload in chunks:
        if ctype == CHUNK_JSON:
            g = json.loads(payload.decode("utf-8"))
            for m in g.get("materials", []):
                m["alphaMode"] = "OPAQUE"
                m.pop("alphaCutoff", None)
                m["doubleSided"] = True
            payload = json.dumps(g, separators=(",", ":")).encode("utf-8")
        pad = (4 - len(payload) % 4) % 4
        payload += (b" " if ctype == CHUNK_JSON else b"\x00") * pad
        body += struct.pack("<II", len(payload), ctype) + payload
    with open(out_path, "wb") as f:
        f.write(struct.pack("<III", MAGIC, 2, 12 + len(body)) + body)

    print(f"done: {out_path}")
    print("verify with: python3 glb_inspect.py " + out_path +
          "  (all clips present, root scale == 1.0 everywhere)")


main()
