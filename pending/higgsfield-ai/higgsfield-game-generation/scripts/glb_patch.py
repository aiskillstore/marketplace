#!/usr/bin/env python3
"""glb_patch.py — stdlib-only GLB material patcher.

Forces alphaMode: OPAQUE + doubleSided: true on every material by rewriting
the JSON chunk of a binary glTF. Use on any GLB you did not export yourself
(Meshy outputs, downloaded assets) — FBX-derived exports love to carry
alphaMode: BLEND, which in Three.js renders back faces over front faces and
looks exactly like inverted normals.

Usage:
    python3 glb_patch.py input.glb [output.glb]
(in-place if output omitted)
"""
import json
import struct
import sys

MAGIC = 0x46546C67  # 'glTF'
CHUNK_JSON = 0x4E4F534A  # 'JSON'


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != MAGIC or version != 2:
        raise SystemExit(f"{path}: not a GLB v2 file")
    chunks = []
    off = 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunks.append((ctype, data[off + 8: off + 8 + clen]))
        off += 8 + clen
    return chunks


def write_glb(path, chunks):
    body = b""
    for ctype, payload in chunks:
        pad = (4 - len(payload) % 4) % 4
        payload = payload + (b" " if ctype == CHUNK_JSON else b"\x00") * pad
        body += struct.pack("<II", len(payload), ctype) + payload
    with open(path, "wb") as f:
        f.write(struct.pack("<III", MAGIC, 2, 12 + len(body)) + body)


def patch_materials(gltf):
    changed = []
    for i, mat in enumerate(gltf.get("materials", [])):
        before = (mat.get("alphaMode", "OPAQUE"), mat.get("doubleSided", False))
        mat["alphaMode"] = "OPAQUE"
        mat.pop("alphaCutoff", None)
        mat["doubleSided"] = True
        if before != ("OPAQUE", True):
            changed.append((i, mat.get("name", f"material_{i}"), before))
    return changed


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    chunks = read_glb(src)
    out = []
    changed = None
    for ctype, payload in chunks:
        if ctype == CHUNK_JSON:
            gltf = json.loads(payload.decode("utf-8"))
            changed = patch_materials(gltf)
            payload = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
        out.append((ctype, payload))
    write_glb(dst, out)
    if changed is None:
        raise SystemExit("no JSON chunk found — corrupt GLB?")
    if changed:
        for i, name, before in changed:
            print(f"patched material[{i}] '{name}': {before} -> ('OPAQUE', True)")
    else:
        print("all materials already OPAQUE/doubleSided")
    print(f"written: {dst}")


if __name__ == "__main__":
    main()
