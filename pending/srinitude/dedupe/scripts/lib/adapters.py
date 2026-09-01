"""Adapter-specific identity functions for dedupe reports."""
import hashlib
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .core import canonical_json, normalize_scalar, normalize_text

SKILL_DIRS = ("references", "templates", "scripts", "assets", "examples", "evals")


def record_key(item, request):
    if not isinstance(item, dict):
        raise ValueError("record items must be JSON objects")
    fields = request.get("key_fields")
    if not isinstance(fields, list) or not fields:
        raise ValueError("record key_fields must be a non-empty array")
    missing = [field for field in fields if field not in item]
    if missing:
        raise ValueError(f"record is missing key fields: {missing}")
    policy = request.get("normalization", {})
    return canonical_json([normalize_scalar(item[field], policy) for field in fields])


def normalize_url(value, policy):
    if not isinstance(value, str):
        raise ValueError("URL items must be strings")
    parts = urlsplit(value)
    if not parts.scheme or not parts.hostname:
        raise ValueError(f"URL must be absolute: {value}")
    if parts.username or parts.password:
        raise ValueError("URLs with user information are not supported")
    scheme = parts.scheme.lower()
    port = parts.port
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = parts.hostname.lower() + (f":{port}" if port and not default_port else "")
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    dropped = set(policy.get("drop_query_params", []))
    pairs = [(key, value) for key, value in pairs if key not in dropped]
    if policy.get("sort_query", False):
        pairs.sort()
    fragment = "" if policy.get("strip_fragment", False) else parts.fragment
    return urlunsplit((scheme, netloc, parts.path, urlencode(pairs), fragment))


def file_bytes(path, request):
    candidate = Path(path)
    if candidate.is_symlink() and not request.get("follow_symlinks", False):
        raise ValueError(f"symlink requires follow_symlinks authority: {path}")
    if not candidate.is_file():
        raise ValueError(f"file not found: {path}")
    return candidate.read_bytes()


def file_key(path, request):
    content = file_bytes(path, request)
    if request.get("mode", "exact") == "exact":
        return hashlib.sha256(content).hexdigest()
    if request.get("mode") == "normalized":
        text = content.decode(request.get("encoding", "utf-8"))
        return normalize_text(text, request.get("normalization", {}))
    raise ValueError(f"unsupported file mode: {request.get('mode')}")


def file_provenance(path, request):
    candidate = Path(path)
    content = file_bytes(path, request)
    stat = candidate.stat()
    return {"path": str(candidate), "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content), "device": stat.st_dev, "inode": stat.st_ino,
            "symlink": candidate.is_symlink()}


def skill_files(path):
    root = Path(path)
    if not (root / "SKILL.md").is_file():
        raise ValueError(f"skill has no SKILL.md: {path}")
    files = [root / "SKILL.md"]
    for name in SKILL_DIRS:
        support = root / name
        if support.is_dir():
            files.extend(item for item in support.rglob("*")
                         if item.is_file() and "__pycache__" not in item.parts
                         and item.suffix != ".pyc")
    if any(item.is_symlink() for item in files):
        raise ValueError(f"skill packet contains a symlink: {path}")
    return root, sorted(files)


def skill_packet(path):
    root, files = skill_files(path)
    digest = hashlib.sha256()
    for item in files:
        digest.update(item.relative_to(root).as_posix().encode("utf-8") + b"\0")
        digest.update(item.read_bytes())
    return digest.hexdigest(), len(files)


def skill_fields(path):
    lines = (Path(path) / "SKILL.md").read_text(encoding="utf-8").splitlines()
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line and not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def skill_provenance(path):
    digest, count = skill_packet(path)
    fields = skill_fields(path)
    return {"path": str(Path(path)), "name": fields.get("name", ""),
            "version": fields.get("version", ""), "packet_sha256": digest,
            "packet_file_count": count}


def list_key(item, request):
    if isinstance(item, (dict, list)):
        return f"{type(item).__name__}:{canonical_json(item)}"
    normalized = normalize_scalar(item, request.get("normalization", {}))
    return f"{type(item).__name__}:{normalized}"


def comparison_key(item, request):
    adapter = request.get("adapter")
    mode = request.get("mode", "exact")
    if adapter == "file":
        return file_key(item, request)
    if adapter == "skill" and mode == "exact":
        return skill_packet(item)[0]
    if mode == "exact":
        return canonical_json(item)
    if adapter == "list" and mode == "normalized":
        return list_key(item, request)
    if adapter == "text" and mode in {"normalized", "similarity"}:
        return normalize_text(item, request.get("normalization", {}))
    if adapter == "record" and mode == "normalized":
        return record_key(item, request)
    if adapter == "url" and mode == "normalized":
        return normalize_url(item, request.get("url_policy", {}))
    raise ValueError(f"unsupported adapter or mode: {adapter}/{mode}")
