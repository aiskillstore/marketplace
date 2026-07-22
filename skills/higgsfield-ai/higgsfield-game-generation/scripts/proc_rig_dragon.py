# proc_rig_dragon.py — Blender CLI: procedural skeleton from bbox analysis.
#
# Usage:
#   blender -b -P proc_rig_dragon.py -- dragon.glb work.blend
#
# Builds a 16-bone skeleton for a winged quadruped (dragon) purely from
# bounding-box fractions — no mesh-specific magic numbers, so the SAME
# script reruns on the textured mesh later (texture-swap rule, see
# references/procedural-animation.md).
#
# Layout: spine -> chest -> neck -> head; tail x4 (opposite the head);
# wing_L/R x2 (inner+outer); legs x4.
#
# Head-side detection: the half along the body axis with more vertex volume
# in the UPPER part of the bbox is the head side.
#
# For other creatures: change BONES below (recipes in
# references/procedural-animation.md) — the weights and animation scripts
# are bone-list-driven.

import sys

import bpy
from mathutils import Vector


def get_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("usage: blender -b -P proc_rig_dragon.py -- model.glb work.blend")
    args = argv[argv.index("--") + 1:]
    if len(args) != 2:
        raise SystemExit("usage: blender -b -P proc_rig_dragon.py -- model.glb work.blend")
    return args


def main():
    src, dst = get_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if not meshes:
        raise SystemExit("no meshes in input")

    # world bbox
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = hi - lo
    # body axis = longer horizontal axis (x or y)
    body_x = size.x >= size.y

    def P(fb, fs, fz):
        """point from bbox fractions: fb along body axis, fs along side axis, fz up"""
        if body_x:
            return Vector((lo.x + fb * size.x, lo.y + fs * size.y, lo.z + fz * size.z))
        return Vector((lo.x + fs * size.x, lo.y + fb * size.y, lo.z + fz * size.z))

    # --- head side: more vertex volume in the upper half ---
    upper_lo_half = upper_hi_half = 0
    zmid = lo.z + 0.5 * size.z
    for o in meshes:
        mw = o.matrix_world
        for v in o.data.vertices:
            w = mw @ v.co
            if w.z < zmid:
                continue
            t = ((w.x - lo.x) / max(size.x, 1e-9)) if body_x else ((w.y - lo.y) / max(size.y, 1e-9))
            if t < 0.5:
                upper_lo_half += 1
            else:
                upper_hi_half += 1
    head_hi = upper_hi_half >= upper_lo_half
    print(f"head side: {'+' if head_hi else '-'}body-axis "
          f"(upper-half verts {upper_hi_half} vs {upper_lo_half})")

    def B(fb, fs, fz):
        """fraction along body axis, flipped so head is always at fb=1"""
        return P(fb if head_hi else 1.0 - fb, fs, fz)

    # --- bone table: name, head point, tail point, parent ---
    BONES = [
        ("spine",    B(0.45, 0.5, 0.55), B(0.60, 0.5, 0.58), None),
        ("chest",    B(0.60, 0.5, 0.58), B(0.72, 0.5, 0.60), "spine"),
        ("neck",     B(0.72, 0.5, 0.60), B(0.85, 0.5, 0.72), "chest"),
        ("head",     B(0.85, 0.5, 0.72), B(0.97, 0.5, 0.80), "neck"),
        ("tail_1",   B(0.45, 0.5, 0.55), B(0.33, 0.5, 0.52), "spine"),
        ("tail_2",   B(0.33, 0.5, 0.52), B(0.22, 0.5, 0.48), "tail_1"),
        ("tail_3",   B(0.22, 0.5, 0.48), B(0.12, 0.5, 0.44), "tail_2"),
        ("tail_4",   B(0.12, 0.5, 0.44), B(0.03, 0.5, 0.40), "tail_3"),
        ("wing_L_1", B(0.58, 0.5, 0.62), B(0.58, 0.78, 0.70), "chest"),
        ("wing_L_2", B(0.58, 0.78, 0.70), B(0.58, 0.99, 0.72), "wing_L_1"),
        ("wing_R_1", B(0.58, 0.5, 0.62), B(0.58, 0.22, 0.70), "chest"),
        ("wing_R_2", B(0.58, 0.22, 0.70), B(0.58, 0.01, 0.72), "wing_R_1"),
        ("leg_FL",   B(0.62, 0.62, 0.45), B(0.62, 0.64, 0.05), "chest"),
        ("leg_FR",   B(0.62, 0.38, 0.45), B(0.62, 0.36, 0.05), "chest"),
        ("leg_BL",   B(0.42, 0.62, 0.45), B(0.42, 0.64, 0.05), "spine"),
        ("leg_BR",   B(0.42, 0.38, 0.45), B(0.42, 0.36, 0.05), "spine"),
    ]

    arm_data = bpy.data.armatures.new("ProcRig")
    arm = bpy.data.objects.new("ProcRig", arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    ebones = {}
    for name, head, tail, parent in BONES:
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail = head, tail
        if parent:
            eb.parent = ebones[parent]
        ebones[name] = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"skeleton: {len(BONES)} bones")

    bpy.ops.wm.save_as_mainfile(filepath=dst)
    print(f"saved: {dst}")
    print("next: blender -b " + dst + " -P proc_weights.py -- " + dst)


main()
