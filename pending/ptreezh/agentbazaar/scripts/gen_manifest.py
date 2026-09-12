#!/usr/bin/env python3
"""Generate MANIFEST.json for the agentbazaar skill (SkillsCatalog v1 schema)."""
import hashlib
import json
import os
import datetime

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # skill root = scripts/..
files_order = [
    ("SKILL.md", "manifest"),
    ("references/protocol-cheat.md", "reference"),
    ("references/acceptance-guide.md", "reference"),
    ("references/errors.md", "reference"),
    ("scripts/ab-register.sh", "script"),
    ("scripts/ab-publish.sh", "script"),
    ("scripts/ab-claim.sh", "script"),
    ("scripts/ab-submit.sh", "script"),
    ("scripts/ab-review.sh", "script"),
    ("scripts/ab-loop.sh", "script"),
]

entries = []
hashes = []
total_bytes = 0
for path, ftype in files_order:
    with open(os.path.join(root, path), "rb") as f:
        data = f.read()
    h = hashlib.sha256(data).hexdigest()
    entries.append({"path": path, "size": len(data), "sha256": h, "type": ftype})
    hashes.append(h)
    total_bytes += len(data)

integrity = hashlib.sha256("".join(hashes).encode()).hexdigest()

manifest = {
    "$schema": "https://agentskills.io/schemas/manifest.v1.json",
    "manifestVersion": "1.0",
    "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
    "generator": "agentbazaar/1.0.0",
    "skill": {"name": "agentbazaar", "version": "1.0.0"},
    "integrity": {"algorithm": "sha256", "hash": integrity},
    "files": entries,
    "externalReferences": [
        {
            "url": "https://github.com/ptreezh/agentmarket/blob/main/PROTOCOL.md",
            "file": "SKILL.md",
            "line": 11,
            "type": "unknown",
        },
        {
            "url": "https://github.com/ptreezh/agentmarket/blob/main/tools/L0-DSL.md",
            "file": "references/acceptance-guide.md",
            "line": 10,
            "type": "unknown",
        },
    ],
    "structure": {
        "maxDepth": 2,
        "totalFiles": len(entries),
        "totalBytes": total_bytes,
        "folders": ["references", "scripts"],
    },
    "license": {"spdxId": "apache-2.0"},
}

with open(os.path.join(root, "MANIFEST.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"MANIFEST.json regenerated: {len(entries)} files, {total_bytes} bytes, sha256={integrity}")
