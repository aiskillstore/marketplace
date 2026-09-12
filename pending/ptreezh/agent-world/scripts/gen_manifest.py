#!/usr/bin/env python3
"""Generate MANIFEST.json for the agent-world skill (SkillsCatalog v1 schema)."""
import hashlib
import json
import os
import datetime

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # skill root = scripts/..
files_order = [
    ("SKILL.md", "manifest"),
    ("references/platform-registry.md", "reference"),
    ("references/interaction-playbook.md", "reference"),
    ("references/credential-handling.md", "reference"),
    ("references/skill-routes.md", "reference"),
    ("scripts/check_status.py", "script"),
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
    "generator": "agent-world/1.0.0",
    "skill": {"name": "agent-world", "version": "1.0.0"},
    "integrity": {"algorithm": "sha256", "hash": integrity},
    "files": entries,
    "externalReferences": [
        {
            "url": "https://github.com/ptreezh/agentmarket/blob/main/docs/agent-world-map.md",
            "file": "SKILL.md",
            "line": 15,
            "type": "unknown",
        }
    ],
    "structure": {
        "maxDepth": 2,
        "totalFiles": len(entries),
        "totalBytes": total_bytes,
        "folders": ["references", "scripts"],
    },
    "license": {"spdxId": "apache-2.0"},
}

out = os.path.join(root, "MANIFEST.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print("MANIFEST.json written:", out)
print("integrity:", integrity)
print("files:", len(entries), "bytes:", total_bytes)
