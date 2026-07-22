# rig_transfer.py — Blender CLI: static GLB + rigged donor FBX -> animated GLB.
#
# Usage:
#   blender -b -P rig_transfer.py -- target_static.glb donor.fbx out.glb
#
# Borrows the skeleton + ALL animations from a rigged donor (KayKit knight,
# any Mixamo rig) and binds them to a generated static mesh (sam_3_3d /
# Meshy preview). One donor animates unlimited generated characters.
#
# CRITICAL PITFALLS baked in (do not regress):
#   1. parent_set(type='ARMATURE_AUTO') (bone heat) FAILS on image-to-3D
#      meshes ("failed to find solution for one or more bones") — the
#      topology is photogrammetry-style. We use Data Transfer of vertex
#      weights from the donor's body meshes instead (VGROUP_WEIGHTS,
#      POLYINTERP_NEAREST).
#   2. data_transfer direction: with use_reverse_transfer=False it goes
#      ACTIVE -> SELECTED. The weight SOURCE (donor mesh) must be ACTIVE.
#      Getting it backwards silently produces 0 weighted verts and skins:0
#      in the export — we hard-fail on that.
#   3. Targets must be humanoid, in T-pose matching the donor's rest pose.
#
# Quality limits (state honestly): depends on donor/target proportion
# similarity; thin dangling parts (capes, skirts) inherit approximate
# weights.

import struct
import json
import sys

import bpy
from mathutils import Vector


def get_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("usage: blender -b -P rig_transfer.py -- target.glb donor.fbx out.glb")
    args = argv[argv.index("--") + 1:]
    if len(args) != 3:
        raise SystemExit("usage: blender -b -P rig_transfer.py -- target.glb donor.fbx out.glb")
    return args


def world_bbox(objs):
    pts = []
    for o in objs:
        for c in o.bound_box:
            pts.append(o.matrix_world @ Vector(c))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def clean_action_name(name):
    return name.split("|")[-1] if "|" in name else name


def main():
    target_path, donor_path, out_path = get_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # --- donor ---
    bpy.ops.import_scene.fbx(filepath=donor_path)
    donor_objs = list(bpy.data.objects)
    armatures = [o for o in donor_objs if o.type == "ARMATURE"]
    if not armatures:
        raise SystemExit("donor has no armature")
    arm = armatures[0]
    donor_meshes = [o for o in donor_objs if o.type == "MESH"]
    if not donor_meshes:
        raise SystemExit("donor has no meshes (need them as weight source)")
    print(f"donor: armature '{arm.name}' ({len(arm.data.bones)} bones), "
          f"{len(donor_meshes)} meshes, {len(bpy.data.actions)} actions")

    # --- target ---
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=target_path)
    target_meshes = [o for o in set(bpy.data.objects) - before if o.type == "MESH"]
    if not target_meshes:
        raise SystemExit("target GLB contains no meshes")

    # --- scale & align donor armature (and meshes, used as weight source) ---
    d_lo, d_hi = world_bbox(donor_meshes)
    t_lo, t_hi = world_bbox(target_meshes)
    scale = (t_hi.z - t_lo.z) / max(d_hi.z - d_lo.z, 1e-9)
    d_center = (d_lo + d_hi) / 2
    t_center = (t_lo + t_hi) / 2
    for o in [arm] + donor_meshes:
        o.scale *= scale
    bpy.context.view_layer.update()
    d_lo, d_hi = world_bbox(donor_meshes)
    d_center = (d_lo + d_hi) / 2
    offset = Vector((t_center.x - d_center.x, t_center.y - d_center.y, t_lo.z - d_lo.z))
    for o in [arm] + donor_meshes:
        o.location += offset
    bpy.context.view_layer.update()
    print(f"aligned donor: scale x{scale:.3f}, offset {tuple(round(v, 3) for v in offset)}")

    # apply transforms so weights/armature bind in final space
    bpy.ops.object.select_all(action="DESELECT")
    for o in [arm] + donor_meshes + target_meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # --- join donor meshes into one weight source ---
    bpy.ops.object.select_all(action="DESELECT")
    for o in donor_meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = donor_meshes[0]
    if len(donor_meshes) > 1:
        bpy.ops.object.join()
    source = bpy.context.view_layer.objects.active

    # --- weight transfer: source must be ACTIVE, target SELECTED ---
    for tmesh in target_meshes:
        bpy.ops.object.select_all(action="DESELECT")
        tmesh.select_set(True)
        source.select_set(True)
        bpy.context.view_layer.objects.active = source  # ACTIVE = weight source!
        bpy.ops.object.data_transfer(
            use_reverse_transfer=False,       # ACTIVE -> SELECTED
            data_type="VGROUP_WEIGHTS",
            vert_mapping="POLYINTERP_NEAREST",
            layers_select_src="ALL",
            layers_select_dst="NAME",
            mix_mode="REPLACE",
        )
        weighted = sum(1 for v in tmesh.data.vertices if any(g.weight > 0 for g in v.groups))
        print(f"weights '{tmesh.name}': {weighted}/{len(tmesh.data.vertices)} verts")
        if weighted == 0:
            raise SystemExit("0 weighted verts — transfer direction wrong or meshes not overlapping; aborting (would export skins:0)")

        # bind to armature WITHOUT auto weights
        tmesh.parent = arm
        mod = tmesh.modifiers.new("Armature", "ARMATURE")
        mod.object = arm

    # --- drop donor mesh, keep armature + actions ---
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.ops.object.delete()

    # --- normals fix on target ---
    for obj in target_meshes:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

    # --- all actions -> NLA tracks ---
    if arm.animation_data is None:
        arm.animation_data_create()
    ad = arm.animation_data
    ad.action = None
    n = 0
    for act in list(bpy.data.actions):
        act.name = clean_action_name(act.name)
        act.use_fake_user = True
        track = ad.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, max(int(act.frame_range[0]), 0), act)
        n += 1
    print(f"NLA: {n} clips")

    # --- materials + export ---
    for mat in bpy.data.materials:
        for attr, val in (("blend_method", "OPAQUE"),
                          ("surface_render_method", "DITHERED"),
                          ("use_backface_culling", False)):
            try:
                setattr(mat, attr, val)
            except Exception:
                pass

    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_yup=True,
        export_apply=False,
    )

    # stdlib OPAQUE patch (safety net)
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
    print("verify with: python3 glb_inspect.py " + out_path + "  (skins must be >= 1)")


main()
