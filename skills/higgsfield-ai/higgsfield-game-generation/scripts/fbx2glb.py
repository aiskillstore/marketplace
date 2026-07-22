# fbx2glb.py — Blender CLI: FBX -> GLB preserving ALL animation clips.
#
# Usage:
#   blender -b -P fbx2glb.py -- input.fbx output.glb
#
# Why this exists (the critical pitfall): a naive import_scene.fbx +
# export_scene.gltf exports only ONE clip — the active action (e.g.
# "Rig|T-Pose") — even when 76 actions imported. Fix: push every action onto
# its own NLA track and export with export_animation_mode='NLA_TRACKS'.
#
# Also baked in:
#   - strips "Rig|" / "Armature|" / "mixamo.com|" prefixes -> clean clip
#     names for Three.js (Idle, Walking_A, ...)
#   - normals_make_consistent(inside=False) on every mesh + outward sanity
#     check (FBX imports often arrive with some normals inverted)
#   - forces materials to OPAQUE / not backface-culled (FBX import loves to
#     set blended transparency -> glTF alphaMode BLEND -> looks like
#     inverted normals in Three.js). A stdlib post-patch of the GLB JSON
#     chunk runs as a safety net (works regardless of Blender version
#     differences in material API).

import struct
import json
import sys

import bpy


def get_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("usage: blender -b -P fbx2glb.py -- input.fbx output.glb")
    args = argv[argv.index("--") + 1:]
    if len(args) != 2:
        raise SystemExit("usage: blender -b -P fbx2glb.py -- input.fbx output.glb")
    return args[0], args[1]


def clean_action_name(name):
    if "|" in name:
        name = name.split("|")[-1]
    return name


def push_all_actions_to_nla():
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not armatures:
        print("WARNING: no armature found — exporting without skeletal animation")
        return
    arm = armatures[0]
    if arm.animation_data is None:
        arm.animation_data_create()
    ad = arm.animation_data
    ad.action = None  # active action would otherwise shadow the NLA stack
    already = {strip.action for t in ad.nla_tracks for strip in t.strips}
    n = 0
    for act in list(bpy.data.actions):
        if act in already:
            continue
        act.name = clean_action_name(act.name)
        act.use_fake_user = True
        track = ad.nla_tracks.new()
        track.name = act.name
        start = int(act.frame_range[0])
        track.strips.new(act.name, max(start, 0), act)
        n += 1
    print(f"NLA: pushed {n} actions onto tracks of '{arm.name}'")


def fix_normals():
    from mathutils import Vector
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        # sanity check: mean dot(poly normal, poly center - centroid) > 0
        me = obj.data
        if not me.polygons:
            continue
        centroid = Vector((0, 0, 0))
        for v in me.vertices:
            centroid += v.co
        centroid /= len(me.vertices)
        s = 0.0
        for p in me.polygons:
            d = (p.center - centroid)
            if d.length > 1e-9:
                s += p.normal.dot(d.normalized())
        s /= len(me.polygons)
        flag = "" if s > 0 else "   <-- WARNING: normals look inward"
        print(f"normals '{obj.name}': outward score {s:.3f}{flag}")


def force_opaque_materials():
    for mat in bpy.data.materials:
        try:
            mat.blend_method = "OPAQUE"  # pre-4.2 / legacy EEVEE path
        except Exception:
            pass
        try:
            mat.surface_render_method = "DITHERED"  # 4.2+ EEVEE Next path
        except Exception:
            pass
        try:
            mat.use_backface_culling = False  # -> doubleSided: true
        except Exception:
            pass


# --- stdlib GLB JSON-chunk patch (safety net, mirrors scripts/glb_patch.py) ---

def patch_glb_opaque(path):
    MAGIC, CHUNK_JSON = 0x46546C67, 0x4E4F534A
    with open(path, "rb") as f:
        data = f.read()
    magic, version, _ = struct.unpack_from("<III", data, 0)
    if magic != MAGIC or version != 2:
        print(f"patch: {path} is not GLB v2, skipping")
        return
    chunks, off = [], 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunks.append((ctype, data[off + 8: off + 8 + clen]))
        off += 8 + clen
    out = []
    for ctype, payload in chunks:
        if ctype == CHUNK_JSON:
            g = json.loads(payload.decode("utf-8"))
            for m in g.get("materials", []):
                m["alphaMode"] = "OPAQUE"
                m.pop("alphaCutoff", None)
                m["doubleSided"] = True
            payload = json.dumps(g, separators=(",", ":")).encode("utf-8")
        out.append((ctype, payload))
    body = b""
    for ctype, payload in out:
        pad = (4 - len(payload) % 4) % 4
        payload += (b" " if ctype == CHUNK_JSON else b"\x00") * pad
        body += struct.pack("<II", len(payload), ctype) + payload
    with open(path, "wb") as f:
        f.write(struct.pack("<III", MAGIC, 2, 12 + len(body)) + body)
    print(f"patch: forced OPAQUE/doubleSided in {path}")


def main():
    src, dst = get_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=src)
    print(f"imported: {src} — actions: {len(bpy.data.actions)}, "
          f"meshes: {sum(1 for o in bpy.data.objects if o.type == 'MESH')}")

    push_all_actions_to_nla()
    fix_normals()
    force_opaque_materials()

    bpy.ops.export_scene.gltf(
        filepath=dst,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_yup=True,
        export_apply=False,  # applying modifiers would break the armature binding
    )
    patch_glb_opaque(dst)
    print(f"done: {dst}")
    print("verify with: python3 glb_inspect.py " + dst)


main()
