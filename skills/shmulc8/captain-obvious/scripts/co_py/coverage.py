from __future__ import annotations
import json
import os

def load_coverage(path: str, root: str):
    """Load line coverage (the dynamic signal ICSE'19 uses to separate rotten
    from good). Supports coverage.py json, lcov (DA: records), and istanbul
    coverage-final.json. Returns {(relpath, line): hits} or None."""
    try:
        raw = open(path, encoding="utf-8").read()
    except OSError:
        return None
    cov: dict[tuple[str, int], int] = {}

    def put(absf: str, line: int, hits: int):
        rel = os.path.relpath(absf, root).replace(os.sep, "/")
        key = (rel, line)
        cov[key] = max(cov.get(key, 0), hits)

    def absol(p: str) -> str:
        return p if os.path.isabs(p) else os.path.join(root, p)

    stripped = raw.lstrip()
    if stripped[:1] in ("{", "["):
        try:
            data = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            return None
        if isinstance(data, dict) and isinstance(data.get("files"), dict):   # coverage.py json
            for p, d in data["files"].items():
                for ln in d.get("executed_lines", []):
                    put(absol(p), ln, 1)
                for ln in d.get("missing_lines", []):
                    put(absol(p), ln, 0)
        elif isinstance(data, dict):                                          # istanbul json
            for p, d in data.items():
                if not isinstance(d, dict) or "statementMap" not in d or "s" not in d:
                    continue
                for sid, loc in d["statementMap"].items():
                    ln = (loc or {}).get("start", {}).get("line")
                    if ln is None:
                        continue
                    put(absol(d.get("path", p)), ln, d["s"].get(sid, 0))
    else:                                                                     # lcov
        cur = None
        for line in raw.splitlines():
            if line.startswith("SF:"):
                cur = absol(line[3:].strip())
            elif line.startswith("DA:") and cur:
                parts = line[3:].split(",")
                try:
                    put(cur, int(parts[0]), int(parts[1]))
                except (ValueError, IndexError):
                    continue
            elif line.startswith("end_of_record"):
                cur = None
    return cov or None
