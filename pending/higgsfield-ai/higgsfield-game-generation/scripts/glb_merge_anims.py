#!/usr/bin/env python3
"""glb_merge_anims.py — stdlib-only merger of single-clip GLBs (Meshy outputs)
into one multi-clip GLB. No Blender required.

Designed for Meshy: rigged.glb (mesh+skeleton from /rigging) + N animation
GLBs from the same rig task (identical node names). Animations are remapped
into the base file by NODE NAME, so it also works across re-exports as long
as bone names match.

Includes the two mandatory Meshy post-fixes from the skill:
  * root-bone baked-scale bug: if a clip's root scale channel != 1.0
    (observed 1.176 on idle), scale values are rewritten to 1.0 and the same
    clip's root translation is divided by the factor;
  * materials forced to alphaMode OPAQUE + doubleSided (the "inverted
    normals" lookalike).

Usage:
    python3 glb_merge_anims.py base.glb walk.glb:Walk run.glb:Run \
            idle.glb:Idle attack.glb:Attack out.glb

Verify the result with glb_inspect.py (clip count, skins>=1, root scale 1.0).
"""
import json
import struct
import sys

MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942
COMP_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
SCALE_TOL = 0.02


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, _ = struct.unpack_from("<III", data, 0)
    if magic != MAGIC or version != 2:
        raise SystemExit(f"{path}: not a GLB v2")
    gltf, binc = None, b""
    off = 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        payload = data[off + 8: off + 8 + clen]
        if ctype == CHUNK_JSON:
            gltf = json.loads(payload.decode("utf-8"))
        elif ctype == CHUNK_BIN:
            binc = payload
        off += 8 + clen
    return gltf, bytearray(binc)


def write_glb(path, gltf, binc):
    if gltf.get("buffers"):
        gltf["buffers"][0]["byteLength"] = len(binc)
    j = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    j += b" " * ((4 - len(j) % 4) % 4)
    b = bytes(binc) + b"\x00" * ((4 - len(binc) % 4) % 4)
    total = 12 + 8 + len(j) + 8 + len(b)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", MAGIC, 2, total))
        f.write(struct.pack("<II", len(j), CHUNK_JSON) + j)
        f.write(struct.pack("<II", len(b), CHUNK_BIN) + b)


def accessor_bytes(gltf, binc, idx):
    acc = gltf["accessors"][idx]
    bv = gltf["bufferViews"][acc["bufferView"]]
    n = COMP_SIZE[acc["componentType"]] * TYPE_COUNT[acc["type"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return acc, bytes(binc[start: start + acc["count"] * n])


def append_accessor(base, base_bin, acc, raw):
    while len(base_bin) % 4:
        base_bin.append(0)
    bv_idx = len(base.setdefault("bufferViews", []))
    base["bufferViews"].append({"buffer": 0, "byteOffset": len(base_bin),
                                "byteLength": len(raw)})
    base_bin.extend(raw)
    new_acc = {k: acc[k] for k in
               ("componentType", "count", "type", "min", "max", "normalized")
               if k in acc}
    new_acc["bufferView"] = bv_idx
    acc_idx = len(base.setdefault("accessors", []))
    base["accessors"].append(new_acc)
    return acc_idx


def node_names(gltf):
    return {n.get("name", f"node_{i}"): i for i, n in enumerate(gltf.get("nodes", []))}


def root_joints(gltf):
    joints = set()
    for skin in gltf.get("skins", []):
        joints.update(skin.get("joints", []))
    parent = {}
    for ni, n in enumerate(gltf.get("nodes", [])):
        for c in n.get("children", []):
            parent[c] = ni
    return {j for j in joints if parent.get(j) not in joints}


def f32_list(raw):
    return list(struct.unpack(f"<{len(raw)//4}f", raw))


def f32_bytes(vals):
    return struct.pack(f"<{len(vals)}f", *vals)


def merge_clip(base, base_bin, donor, donor_bin, clip_name):
    names = node_names(base)
    merged = 0
    for anim in donor.get("animations", []):
        new_anim = {"name": clip_name if len(donor.get("animations", [])) == 1
                    else anim.get("name", clip_name),
                    "samplers": [], "channels": []}
        for smp in anim["samplers"]:
            in_acc, in_raw = accessor_bytes(donor, donor_bin, smp["input"])
            out_acc, out_raw = accessor_bytes(donor, donor_bin, smp["output"])
            new_anim["samplers"].append({
                "input": append_accessor(base, base_bin, in_acc, in_raw),
                "output": append_accessor(base, base_bin, out_acc, out_raw),
                "interpolation": smp.get("interpolation", "LINEAR")})
        skipped = 0
        for ch in anim["channels"]:
            tgt = ch["target"]
            dn = donor["nodes"][tgt["node"]].get("name")
            if dn not in names:
                skipped += 1
                continue
            new_anim["channels"].append({"sampler": ch["sampler"],
                                         "target": {"node": names[dn],
                                                    "path": tgt["path"]}})
        if skipped:
            print(f"  '{new_anim['name']}': skipped {skipped} channels (no matching node name)")
        if not new_anim["channels"]:
            print(f"  '{new_anim['name']}': NO matching channels — skeletons incompatible?")
            continue
        base.setdefault("animations", []).append(new_anim)
        merged += 1
        print(f"  merged clip '{new_anim['name']}' "
              f"({len(new_anim['channels'])} channels)")
    return merged


def fix_root_scale(base, base_bin):
    roots = root_joints(base)
    for anim in base.get("animations", []):
        scale_ch = [c for c in anim.get("channels", [])
                    if c["target"]["path"] == "scale" and c["target"]["node"] in roots]
        for ch in scale_ch:
            smp = anim["samplers"][ch["sampler"]]
            acc = base["accessors"][smp["output"]]
            bv = base["bufferViews"][acc["bufferView"]]
            start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
            n = acc["count"] * 3
            vals = f32_list(bytes(base_bin[start: start + n * 4]))
            mean = sum(vals) / len(vals)
            if abs(mean - 1.0) <= SCALE_TOL:
                continue
            print(f"FIX root scale in '{anim.get('name')}': mean {mean:.4f} -> 1.0")
            base_bin[start: start + n * 4] = f32_bytes([1.0] * n)
            acc.pop("min", None); acc.pop("max", None)
            for ch2 in anim["channels"]:
                if (ch2["target"]["path"] == "translation"
                        and ch2["target"]["node"] == ch["target"]["node"]):
                    smp2 = anim["samplers"][ch2["sampler"]]
                    acc2 = base["accessors"][smp2["output"]]
                    bv2 = base["bufferViews"][acc2["bufferView"]]
                    s2 = bv2.get("byteOffset", 0) + acc2.get("byteOffset", 0)
                    n2 = acc2["count"] * 3
                    tv = f32_list(bytes(base_bin[s2: s2 + n2 * 4]))
                    base_bin[s2: s2 + n2 * 4] = f32_bytes([v / mean for v in tv])
                    acc2.pop("min", None); acc2.pop("max", None)
                    print(f"    translation of same root divided by {mean:.4f}")


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    base_path, out_path = sys.argv[1], sys.argv[-1]
    base, base_bin = read_glb(base_path)
    print(f"base: {base_path} ({len(base.get('animations', []))} clips, "
          f"{len(base.get('skins', []))} skins)")
    for spec in sys.argv[2:-1]:
        if ":" in spec:
            path, name = spec.rsplit(":", 1)
        else:
            path, name = spec, spec.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        donor, donor_bin = read_glb(path)
        print(f"donor: {path} -> '{name}'")
        merge_clip(base, base_bin, donor, donor_bin, name)
    fix_root_scale(base, base_bin)
    for m in base.get("materials", []):
        m["alphaMode"] = "OPAQUE"
        m.pop("alphaCutoff", None)
        m["doubleSided"] = True
    write_glb(out_path, base, base_bin)
    print(f"done: {out_path} ({len(base.get('animations', []))} clips)")


if __name__ == "__main__":
    main()
