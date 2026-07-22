# proc_anim_dragon.py — sine-based idle/fly clips baked to keyframes.
#
# Usage (after proc_rig_dragon.py + proc_weights.py):
#   blender -b work.blend -P proc_anim_dragon.py -- dragon_anim.glb
#
# Pure math, no mocap: every clip is a sum of sinusoids per bone, baked to
# keyframes (every 2 frames @ 24 fps) and exported via NLA tracks.
#
#   fly (2 s loop):  wings +/-35-45deg with the OUTER segment lagging the
#                    inner by ~0.2 of the cycle (flex illusion); body bobs in
#                    COUNTER-phase to the downstroke; legs tucked (constant);
#                    traveling wave down the tail.
#   idle (4 s loop): chest breathing, head sway, tail micro-wave, wing
#                    micro-adjust.
#
# Other creatures: swap the MOVES tables (gait recipes in
# references/procedural-animation.md — quadruped diagonal pairs, serpentine
# traveling wave, slime squash & stretch, etc.).

import math
import struct
import json
import sys

import bpy

FPS = 24
STEP = 2  # bake every 2 frames


def get_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("usage: blender -b work.blend -P proc_anim_dragon.py -- out.glb")
    rest = argv[argv.index("--") + 1:]
    if len(rest) != 1:
        raise SystemExit("usage: blender -b work.blend -P proc_anim_dragon.py -- out.glb")
    return rest[0]


def deg(d):
    return math.radians(d)


# MOVES: bone -> list of (channel, axis, amplitude, phase, constant_offset)
# channel: "rot" (rotation_euler, radians) or "loc" (location, blender units)
# value(t) = offset + amplitude * sin(2*pi*t + phase),  t in [0,1) cycle phase

FLY_SECONDS = 2.0
FLY = {
    "wing_L_1": [("rot", 0, deg(40), 0.0, 0.0)],
    "wing_R_1": [("rot", 0, deg(40), math.pi, 0.0)],          # mirrored
    "wing_L_2": [("rot", 0, deg(25), -0.2 * 2 * math.pi, 0.0)],  # outer lags inner
    "wing_R_2": [("rot", 0, deg(25), math.pi - 0.2 * 2 * math.pi, 0.0)],
    "spine":    [("loc", 2, 0.06, math.pi, 0.0)],             # bob counter-phase
    "chest":    [("rot", 0, deg(4), math.pi, 0.0)],
    "tail_1":   [("rot", 0, deg(6), 0.00, 0.0)],
    "tail_2":   [("rot", 0, deg(8), -0.6, 0.0)],              # wave: growing lag
    "tail_3":   [("rot", 0, deg(10), -1.2, 0.0)],
    "tail_4":   [("rot", 0, deg(12), -1.8, 0.0)],
    "leg_FL":   [("rot", 0, 0.0, 0.0, deg(35))],              # tucked, constant
    "leg_FR":   [("rot", 0, 0.0, 0.0, deg(35))],
    "leg_BL":   [("rot", 0, 0.0, 0.0, deg(40))],
    "leg_BR":   [("rot", 0, 0.0, 0.0, deg(40))],
}

IDLE_SECONDS = 4.0
IDLE = {
    "chest":    [("rot", 0, deg(2.5), 0.0, 0.0)],             # breathing
    "neck":     [("rot", 2, deg(4), 0.7, 0.0)],               # slow sway
    "head":     [("rot", 2, deg(3), 1.2, 0.0)],
    "tail_1":   [("rot", 2, deg(3), 0.0, 0.0)],
    "tail_2":   [("rot", 2, deg(4), -0.6, 0.0)],
    "tail_3":   [("rot", 2, deg(5), -1.2, 0.0)],
    "tail_4":   [("rot", 2, deg(6), -1.8, 0.0)],
    "wing_L_1": [("rot", 0, deg(2), 0.0, deg(5))],
    "wing_R_1": [("rot", 0, deg(2), math.pi, deg(5))],
}


def bake_action(arm, name, moves, seconds):
    frames = int(seconds * FPS)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for bone_name, channels in moves.items():
        pb = arm.pose.bones.get(bone_name)
        if pb is None:
            print(f"  (skip missing bone '{bone_name}')")
            continue
        pb.rotation_mode = "XYZ"
        for f in range(1, frames + 1, STEP):
            t = (f - 1) / frames  # cycle phase 0..1
            for channel, axis, amp, phase, offset in channels:
                val = offset + amp * math.sin(2 * math.pi * t + phase)
                if channel == "rot":
                    pb.rotation_euler[axis] = val
                    pb.keyframe_insert("rotation_euler", index=axis, frame=f)
                else:
                    pb.location[axis] = val
                    pb.keyframe_insert("location", index=axis, frame=f)
        # close the loop exactly
        for channel, axis, amp, phase, offset in channels:
            val = offset + amp * math.sin(phase)
            if channel == "rot":
                pb.rotation_euler[axis] = val
                pb.keyframe_insert("rotation_euler", index=axis, frame=frames + 1)
            else:
                pb.location[axis] = val
                pb.keyframe_insert("location", index=axis, frame=frames + 1)
    arm.animation_data.action = None
    print(f"baked '{name}': {frames} frames ({seconds}s @ {FPS}fps)")
    return act


def main():
    out_path = get_args()
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not armatures:
        raise SystemExit("no armature — run proc_rig + proc_weights first")
    arm = armatures[0]
    if arm.animation_data is None:
        arm.animation_data_create()
    bpy.context.scene.render.fps = FPS

    actions = [
        bake_action(arm, "idle", IDLE, IDLE_SECONDS),
        bake_action(arm, "fly", FLY, FLY_SECONDS),
    ]

    ad = arm.animation_data
    ad.action = None
    for act in actions:
        track = ad.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, max(int(act.frame_range[0]), 0), act)

    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_yup=True,
        export_apply=False,
    )

    # stdlib OPAQUE/doubleSided patch
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
    print("QC: render phase grid at non-uniform cycle fractions "
          "(0.0, 0.23, 0.41, 0.68, 0.87) — see references/procedural-animation.md")


main()
