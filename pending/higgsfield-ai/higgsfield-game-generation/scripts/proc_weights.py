# proc_weights.py — distance-based skin weights for procedural rigs.
#
# Usage (after proc_rig_dragon.py):
#   blender -b work.blend -P proc_weights.py -- work.blend
#
# WHY NOT parent_set(type='ARMATURE_AUTO'): bone heat fails on generated
# meshes ("failed to find solution...") and in headless mode can SILENTLY
# produce all-zero weights -> the exported GLB has skins:0. This script
# assigns every vertex to its 2 NEAREST BONES (distance from the vertex to
# the bone head-tail segment) with inverse-distance blending. Crude but
# stable on any topology; fine for stylized/low-poly creatures.
#
# Hard-fails if any mesh ends up with 0 weighted vertices.

import sys

import bpy
from mathutils import Vector


def seg_dist(p, a, b):
    """distance from point p to segment ab"""
    ab = b - a
    L2 = ab.length_squared
    if L2 < 1e-12:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length


def main():
    out = None
    if "--" in sys.argv:
        rest = sys.argv[sys.argv.index("--") + 1:]
        out = rest[0] if rest else None

    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if not armatures or not meshes:
        raise SystemExit("scene must contain an armature and meshes (run proc_rig first)")
    arm = armatures[0]

    # bone segments in world space
    segs = []
    mw = arm.matrix_world
    for b in arm.data.bones:
        segs.append((b.name, mw @ b.head_local, mw @ b.tail_local))

    K = 2  # nearest bones per vertex
    for obj in meshes:
        groups = {}
        for name, _, _ in segs:
            groups[name] = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
        omw = obj.matrix_world
        weighted = 0
        for v in obj.data.vertices:
            p = omw @ v.co
            dists = sorted(((seg_dist(p, a, b), name) for name, a, b in segs))[:K]
            inv = [(1.0 / max(d, 1e-6), name) for d, name in dists]
            total = sum(w for w, _ in inv)
            for w, name in inv:
                groups[name].add([v.index], w / total, "REPLACE")
            weighted += 1
        print(f"weights '{obj.name}': {weighted}/{len(obj.data.vertices)} verts")
        if weighted == 0:
            raise SystemExit("0 weighted verts — aborting")

        obj.parent = arm
        if not any(m.type == "ARMATURE" for m in obj.modifiers):
            mod = obj.modifiers.new("Armature", "ARMATURE")
            mod.object = arm

    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"saved: {out}")
    print("next: blender -b work.blend -P proc_anim_dragon.py -- out.glb")


main()
