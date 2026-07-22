#!/usr/bin/env python3
"""glb_inspect.py — stdlib-only GLB animation/skin inspector.

Prints: animation clip count + names, skins/meshes/images/materials,
material alphaMode (warns on non-OPAQUE), and per-clip root-node scale
ranges (catches the Meshy library-animation baked-scale bug, e.g. Hips
scale 1.176 on one clip while others are 1.0).

A correct character GLB: skins >= 1, expected clip count, all alphaMode
OPAQUE, every clip's root scale ~= 1.0. If clips == 1 and the name contains
"T-Pose", the NLA-tracks export step was skipped.

Usage:
    python3 glb_inspect.py model.glb
"""
import json
import struct
import sys

MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

COMPONENT_FMT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, _ = struct.unpack_from("<III", data, 0)
    if magic != MAGIC or version != 2:
        raise SystemExit(f"{path}: not a GLB v2 file")
    gltf, binchunk = None, b""
    off = 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        payload = data[off + 8: off + 8 + clen]
        if ctype == CHUNK_JSON:
            gltf = json.loads(payload.decode("utf-8"))
        elif ctype == CHUNK_BIN:
            binchunk = payload
        off += 8 + clen
    return gltf, binchunk


def accessor_values(gltf, binchunk, idx):
    acc = gltf["accessors"][idx]
    if "min" in acc and "max" in acc:
        return acc["min"], acc["max"], None
    bv = gltf["bufferViews"][acc["bufferView"]]
    fmt = COMPONENT_FMT[acc["componentType"]]
    ncomp = TYPE_COUNT[acc["type"]]
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride") or ncomp * struct.calcsize(fmt)
    vals = []
    for i in range(acc["count"]):
        vals.append(struct.unpack_from("<" + fmt * ncomp, binchunk, base + i * stride))
    mins = [min(v[c] for v in vals) for c in range(ncomp)]
    maxs = [max(v[c] for v in vals) for c in range(ncomp)]
    return mins, maxs, vals


def find_skeleton_roots(gltf):
    """Joint nodes whose parent is not itself a joint (per skin)."""
    joints = set()
    for skin in gltf.get("skins", []):
        joints.update(skin.get("joints", []))
    parented = {}
    for ni, node in enumerate(gltf.get("nodes", [])):
        for child in node.get("children", []):
            parented[child] = ni
    return {j for j in joints if parented.get(j) not in joints}


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    gltf, binchunk = read_glb(sys.argv[1])
    anims = gltf.get("animations", [])
    print(f"file:       {sys.argv[1]}")
    print(f"meshes:     {len(gltf.get('meshes', []))}")
    print(f"skins:      {len(gltf.get('skins', []))}")
    print(f"images:     {len(gltf.get('images', []))}")
    print(f"materials:  {len(gltf.get('materials', []))}")
    for i, mat in enumerate(gltf.get("materials", [])):
        mode = mat.get("alphaMode", "OPAQUE")
        ds = mat.get("doubleSided", False)
        flag = "" if mode == "OPAQUE" else "   <-- WARNING: not OPAQUE (three.js depth-sorting artifacts)"
        print(f"  material[{i}] '{mat.get('name', '?')}': alphaMode={mode} doubleSided={ds}{flag}")
    print(f"animations: {len(anims)}")

    roots = find_skeleton_roots(gltf)
    warnings = []
    for a in anims:
        name = a.get("name", "?")
        scale_note = ""
        for ch in a.get("channels", []):
            tgt = ch.get("target", {})
            if tgt.get("path") != "scale" or tgt.get("node") not in roots:
                continue
            sampler = a["samplers"][ch["sampler"]]
            mins, maxs, _ = accessor_values(gltf, binchunk, sampler["output"])
            lo, hi = min(mins), max(maxs)
            if abs(lo - 1.0) > 1e-3 or abs(hi - 1.0) > 1e-3:
                node_name = gltf["nodes"][tgt["node"]].get("name", tgt["node"])
                scale_note = (f"   <-- WARNING: root '{node_name}' scale in "
                              f"[{lo:.4f}, {hi:.4f}] != 1.0 (Meshy baked-scale bug; "
                              f"re-run merge_anim_glbs.py or fix manually)")
                warnings.append(name)
        print(f"  clip: {name}{scale_note}")

    if len(anims) == 1 and "t-pose" in anims[0].get("name", "").lower().replace("_", "-"):
        print("WARNING: single clip named like T-Pose — NLA-tracks export step was skipped")
    if not gltf.get("skins"):
        print("WARNING: skins == 0 — weight transfer failed (check data_transfer direction: source must be ACTIVE)")
    if warnings:
        sys.exit(2)


if __name__ == "__main__":
    main()
