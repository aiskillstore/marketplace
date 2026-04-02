#!/usr/bin/env python3
"""
SkillScan v1.1.5 — OpenClaw Skill security scanner.
Supports Windows / macOS / Linux. All temp files use the standard tempfile module.

Usage (invoked by the agent via bash):
  python scanner.py first-run            # First install: list installed skills and ask to scan
  python scanner.py scan <path>          # Scan a single skill (.zip or directory)
  python scanner.py scan-all            # Scan all installed skills
  python scanner.py upgrade             # Auto-upgrade
"""

import sys, os, json, time, zipfile, hashlib, shutil, tempfile, uuid, platform, base64
import urllib.request, urllib.error, urllib.parse
from pathlib import Path
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCANNER_VERSION = "1.1.5"

BASE_URL   = "https://skillscan.tokauth.com"
API_SEARCH = f"{BASE_URL}/oapi/v1/skill-scan/search"
API_UPLOAD = f"{BASE_URL}/oapi/v1/skill-scan/upload"
API_RESULT = f"{BASE_URL}/oapi/v1/skill-scan/result"
UPDATE_URL = os.environ.get("SKILL_SCANNER_UPDATE_URL",
                            f"{BASE_URL}/downloads/SkillScan/manifest")

POLL_INTERVAL = 20   # Poll interval (seconds)
POLL_TIMEOUT  = 180  # Max wait time (seconds)

# First-run marker file (in the same directory as scanner.py)
STATE_FILE = Path(__file__).parent / ".first_run_done"

# Auto-update check marker file and interval (7 days)
LAST_UPDATE_CHECK_FILE = Path(__file__).parent / ".last_update_check"
AUTO_UPDATE_INTERVAL = 1 * 24 * 3600  # 1 day (seconds)

# Client info file (generated on first run, reused afterwards)
CLIENT_INFO_FILE = Path(__file__).parent / ".client_info"

# Files and directories to skip during scanning, hashing, and packing
SKIP_FILES = {".first_run_done", ".last_update_check", ".client_info", "cloud_report.json", ".DS_Store"}
SKIP_DIRS  = {".git", "__pycache__", ".venv", "node_modules", ".idea", ".vscode", ".clawhub"}

# Resolve the root directory of SkillScan itself (parent of scripts/)
SELF_ROOT = Path(__file__).parent.parent.resolve()


# Skill installation paths (cross-platform)
def skill_install_paths():
    # type: () -> list
    """Auto-enumerate OpenClaw and local skill paths across platforms."""
    home = Path.home()
    oc_dir = home / ".openclaw"
    candidates = [
        # OpenClaw standard paths
        oc_dir / "skills",
        oc_dir / "workspace/skills",
        # Shared agent skill paths
        home / ".agents/skills",
        home / ".config/agents/skills",
        # Agent-specific global paths
        home / ".gemini/antigravity/skills",
        home / ".gemini/skills",
        home / ".augment/skills",
        home / ".claude/skills",
        home / ".codex/skills",
        home / ".commandcode/skills",
        home / ".continue/skills",
        home / ".snowflake/cortex/skills",
        home / ".config/crush/skills",
        home / ".cursor/skills",
        home / ".deepagents/agent/skills",
        home / ".factory/skills",
        home / ".firebender/skills",
        home / ".copilot/skills",
        home / ".config/goose/skills",
        home / ".junie/skills",
        home / ".iflow/skills",
        home / ".kilocode/skills",
        home / ".kiro/skills",
        home / ".kode/skills",
        home / ".mcpjam/skills",
        home / ".vibe/skills",
        home / ".mux/skills",
        home / ".config/opencode/skills",
        home / ".openhands/skills",
        home / ".pi/agent/skills",
        home / ".qoder/skills",
        home / ".qwen/skills",
        home / ".roo/skills",
        home / ".trae/skills",
        home / ".trae-cn/skills",
        home / ".codeium/windsurf/skills",
        home / ".zencoder/skills",
        home / ".neovate/skills",
        home / ".pochi/skills",
        home / ".adal/skills",
        home / ".npm-global/lib/node_modules/openclaw/skills",
        # Container default paths
        Path("/mnt/skills/public"),
        Path("/mnt/skills/private"),
        Path("/mnt/skills/user"),
        # User dev/download paths
        home / "Downloads/skills",
    ]

    # Windows-specific paths
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(Path(appdata) / "OpenClaw/skills")

    # Dynamically scan extensions: .openclaw/extensions/{xxxx}/skills
    if oc_dir.exists():
        ext_root = oc_dir / "extensions"
        if ext_root.exists():
            for sub in ext_root.iterdir():
                if sub.is_dir():
                    s_dir = sub / "skills"
                    if s_dir.exists():
                        candidates.append(s_dir)

    # Include script run path and workspace
    candidates.append(Path.cwd() / "skills")
    candidates.append(Path(__file__).parent.parent / "skills")

    # Deduplicate and filter non-existent paths
    seen = set()
    result = []
    for p in candidates:
        try:
            abs_p = p.resolve()
            if abs_p.exists() and abs_p not in seen:
                result.append(p)
                seen.add(abs_p)
        except Exception:
            continue
    return result

RISK_EMOJI = {"SAFE":"✅","LOW":"⚠️ ","MEDIUM":"🟡","HIGH":"🔴","CRITICAL":"☠️ "}


# ─────────────────────────────────────────────────────────────────────────────
# Client Info (X-Client-Info)
# ─────────────────────────────────────────────────────────────────────────────

def _get_mac_address():
    """Try to get the MAC address; return empty string on failure."""
    try:
        import uuid as _uuid
        mac_int = _uuid.getnode()
        # getnode() returns a random value (bit 8 set) when it can't get the real MAC
        if (mac_int >> 40) & 1:
            return ""
        mac_str = ":".join(("%012X" % mac_int)[i:i+2] for i in range(0, 12, 2))
        return mac_str
    except Exception:
        return ""


def _build_client_info():
    """Build client info dict and persist to file; reuse on subsequent runs."""
    # If a record file already exists, read it
    if CLIENT_INFO_FILE.exists():
        try:
            data = json.loads(CLIENT_INFO_FILE.read_text(encoding="utf-8"))
            if data.get("client_id"):
                return data
        except Exception:
            pass

    # First run: generate new client info
    info = {
        "client_id": str(uuid.uuid4()),
        "os": platform.system() or "",
        "platform": platform.machine() or "",
        "os_version": platform.release() or "",
        "client": "SkillScanner/%s" % SCANNER_VERSION,
    }

    mac = _get_mac_address()
    if mac:
        info["mac"] = mac

    # Python version as extra
    info["extra"] = {
        "python": platform.python_version(),
    }

    # Persist
    try:
        CLIENT_INFO_FILE.write_text(
            json.dumps(info, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass

    return info


def _get_client_info_header():
    """Return Base64-encoded X-Client-Info header value; empty string on failure."""
    try:
        info = _build_client_info()
        json_str = json.dumps(info, ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
        return encoded
    except Exception:
        return ""

# ─────────────────────────────────────────────────────────────────────────────
# Output Helpers
# ─────────────────────────────────────────────────────────────────────────────

def banner(title: str):
    w = 58
    print(f"\n{'═'*w}")
    print(f"  {title}")
    print(f"{'═'*w}")

def divider(title: str = ""):
    if title:
        print(f"\n  ── {title} {'─'*(48-len(title))}")
    else:
        print(f"  {'─'*52}")

def log(msg: str):
    print(f"  {msg}", flush=True)

def ask(prompt: str) -> str:
    """Read user input (compatible with non-interactive environments)."""
    try:
        return input(f"\n  {prompt} ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""

# ─────────────────────────────────────────────────────────────────────────────
# HTTP Helpers
# ─────────────────────────────────────────────────────────────────────────────

def http_get(url: str) -> dict:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))

def http_post(url: str, payload: dict) -> dict:
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


# ─────────────────────────────────────────────────────────────────────────────
# Skill Utilities
# ─────────────────────────────────────────────────────────────────────────────

def skill_name_from_dir(skill_dir: Path) -> str:
    md = skill_dir / "SKILL.md"
    if md.exists():
        for line in md.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s.startswith("name:"):
                return s.split(":", 1)[1].strip().strip("\"'")
    return skill_dir.name

def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def calculate_dir_sha256(directory: Path) -> str:
    """Calculate SHA256 hash of a skill directory (based on all file contents + relative paths).
    Excludes _meta.json and files/dirs in SKIP_FILES/SKIP_DIRS."""
    file_hashes = []
    for file_path in sorted(directory.rglob('*')):
        if not file_path.is_file():
            continue
        if file_path.name == '_meta.json':
            continue
        rel = file_path.relative_to(directory)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if file_path.name in SKIP_FILES:
            continue
        rel_path = str(rel)
        file_hash = hashlib.sha256()
        file_hash.update(rel_path.encode('utf-8'))
        file_hash.update(b'\x00')
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                file_hash.update(chunk)
        file_hashes.append(file_hash.hexdigest())
    file_hashes.sort()
    final_hash = hashlib.sha256()
    for h in file_hashes:
        final_hash.update(h.encode('utf-8'))
        final_hash.update(b'\x00')
    return final_hash.hexdigest()

def collect_files(skill_dir: Path) -> dict:
    """Collect files for scanning, skipping redundant or sensitive directories."""
    exts = {".md",".py",".js",".ts",".sh",".yaml",".yml",".json",".txt"}
    out = {}
    for p in sorted(skill_dir.rglob("*")):
        if any(part in SKIP_DIRS for part in p.relative_to(skill_dir).parts):
            continue
        if p.is_file() and p.name not in SKIP_FILES:
            if p.suffix.lower() in exts or p.name == "SKILL.md":
                try:
                    out[str(p.relative_to(skill_dir))] = \
                        p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pass
    return out

def pack_zip(skill_dir: Path) -> bytes:
    """Pack a skill directory into a zip byte stream, excluding redundant directories."""
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(skill_dir.rglob("*")):
            if any(part in SKIP_DIRS for part in p.relative_to(skill_dir).parts):
                continue
            if p.is_file() and p.name not in SKIP_FILES:
                zf.write(p, p.relative_to(skill_dir))
    return buf.getvalue()

def unpack_zip(zip_path: Path) -> Path:
    """Extract a .zip to a system temp directory. Returns the extraction path. Prevents zip-slip."""
    tmp = Path(tempfile.mkdtemp(prefix="skillscan-"))
    log(f"📦 Extracting {zip_path.name}  →  {tmp}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            dest = (tmp / member).resolve()
            if not str(dest).startswith(str(tmp.resolve())):
                raise ValueError(f"zip-slip path rejected: {member}")
        zf.extractall(tmp)
    return tmp

def find_installed_skills():
    # type: () -> list
    """Find all installed skill directories (first-level subdirectories containing SKILL.md).
    Excludes SkillScan itself."""
    found = set()
    for base in skill_install_paths():
        if not base.exists():
            continue
        for md in base.rglob("SKILL.md"):
            skill_path = md.parent
            try:
                rel = skill_path.relative_to(base)
                if len(rel.parts) == 1:
                    resolved = skill_path.resolve()
                    # Skip self
                    if resolved == SELF_ROOT:
                        continue
                    found.add(resolved)
            except ValueError:
                pass
    return sorted(found)


# ─────────────────────────────────────────────────────────────────────────────
# Scan Core (3 steps)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_result(resp, sha256):
    """Internal: extract core data from API response, handling SHA256 wrapping/nested result."""
    # 1. Handle API response keyed by SHA256 (e.g. { "sha256": { "status": "success", "data": {...} } })
    if sha256 and sha256 in resp:
        resp = resp[sha256]

    # 2. Extract data body (data or result)
    data = resp.get("data") or resp.get("result") or resp

    # 3. Handle nested result inside data
    if isinstance(data, dict) and "result" in data:
        inner = data["result"]
        if isinstance(inner, dict):
            # Merge sibling metadata (analysis_level/reason etc.) into result
            for k, v in data.items():
                if k != "result" and k not in inner:
                    inner[k] = v
            return inner

    return data if isinstance(data, dict) and (data.get("verdict") or data.get("is_safe") is not None or data.get("analysis_level")) else None


def cloud_search(dir_sha256):
    """Step 1: Query scan cache by dir_sha256. Returns result dict or None."""
    extra_headers = {}
    ci = _get_client_info_header()
    if ci:
        extra_headers["X-Client-Info"] = ci

    url = "%s?%s" % (API_SEARCH, urllib.parse.urlencode({"dir_sha256": dir_sha256}))
    try:
        headers = {}
        headers.update(extra_headers)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode("utf-8", errors="replace"))
        res = _extract_result(resp, dir_sha256)
        if res:
            log("   ✅ Cache hit (dir_sha256 %s…)" % dir_sha256[:16])
            return res
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise RuntimeError("Search API error HTTP %d" % e.code)
    except urllib.error.URLError as e:
        raise RuntimeError("Cannot connect to server: %s" % e)
    return None


def cloud_upload(skill_dir, name, dir_hash):
    """Step 2: Upload skill (multipart/form-data), returns task_no."""
    # Pack the entire directory for full code context
    zip_data = pack_zip(skill_dir)
    filename = "%s.zip" % name

    # Build multipart/form-data boundary
    boundary = "----WebKitFormBoundary%s" % uuid.uuid4().hex

    # Manually construct multipart byte stream (no requests library needed)
    parts = []
    parts.append(("--%s" % boundary).encode())
    parts.append(('Content-Disposition: form-data; name="file"; filename="%s"' % filename).encode())
    parts.append(b"Content-Type: application/zip")
    parts.append(b"")
    parts.append(zip_data)
    parts.append(("--%s--" % boundary).encode())
    parts.append(b"")  # trailing newline

    body = b"\r\n".join(parts)

    headers = {
        "Content-Type": "multipart/form-data; boundary=%s" % boundary,
        "Content-Length": str(len(body)),
        "Accept": "application/json"
    }

    # Add X-Client-Info header
    ci = _get_client_info_header()
    if ci:
        headers["X-Client-Info"] = ci

    log("   📤 Uploading: %s (%.1f KB)..." % (filename, len(zip_data) / 1024.0))
    req = urllib.request.Request(API_UPLOAD, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        raise RuntimeError("Upload failed HTTP %d: %s" % (e.code, err_body))

    task_no = (resp.get("data") or {}).get("task_no") or resp.get("task_no") or resp.get("taskNo") or resp.get("task_id") or ""
    if not task_no:
        raise RuntimeError("Upload succeeded but no valid task_no in response: %s" % resp)

    log("   ✅ Upload complete, task_no: %s" % task_no)
    return str(task_no)


def cloud_poll(task_no: str) -> dict:
    """Step 3: Poll until complete or timeout. Queries every 20s.
    status: 0=pending, 1=scanning, 2=completed, 3=failed, 4=cancelled
    """
    url = f"{API_RESULT}?{urllib.parse.urlencode({'task_no': task_no})}"
    deadline = time.time() + POLL_TIMEOUT
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        elapsed = int(time.time() - (deadline - POLL_TIMEOUT))
        try:
            resp = http_get(url)
            data = resp.get("data") or resp
            status = data.get("status")

            if status == 2:  # completed
                print()
                log(f"   ✅ Scan complete (attempt {attempt}, {elapsed}s elapsed)")
                return _extract_result(resp, "") or resp
            elif status == 3:  # failed
                print()
                err_msg = data.get("error_message") or resp.get("message", "unknown error")
                raise RuntimeError(f"Analysis failed: {err_msg}")
            elif status == 4:  # cancelled
                print()
                raise RuntimeError("Scan task was cancelled")
            else:
                # 0=pending, 1=scanning -> keep waiting
                status_text = data.get("status_text", "processing")
                print(f"   ⏳ [{status_text}] attempt {attempt}, {elapsed}s / {POLL_TIMEOUT}s elapsed",
                      end="\r", flush=True)
                time.sleep(POLL_INTERVAL)
        except (RuntimeError, ValueError):
            raise
        except Exception as e:
            raise RuntimeError(f"Poll error: {e}")
    print()
    raise RuntimeError(f"Timeout ({POLL_TIMEOUT}s), task_no={task_no}, please retry later")


def cloud_check(skill_dir: Path) -> dict:
    """Run full security scan on a skill directory, return normalized result."""
    md = skill_dir / "SKILL.md"
    if not md.exists():
        raise FileNotFoundError(f"SKILL.md not found: {skill_dir}")

    name       = skill_name_from_dir(skill_dir)
    dir_hash   = calculate_dir_sha256(skill_dir)
    log(f"🔍 Scanning: {name}")
    log(f"   dir_sha256: {dir_hash}")

    log(f"🔎 [1/3] Checking scan cache...")
    raw = cloud_search(dir_hash)

    if raw is None:
        log(f"   ℹ️  No cache record, submitting new scan task")
        log(f"📤 [2/3] Uploading skill for analysis...")
        task_no = cloud_upload(skill_dir, name, dir_hash)
        log(f"⏳ [3/3] Waiting for analysis (polling every {POLL_INTERVAL}s, max {POLL_TIMEOUT}s)...")
        raw = cloud_poll(task_no)
    else:
        log(f"   ⏭️  Skipping upload, using cached result")

    return _normalize(raw, name, dir_hash)


def _normalize(raw: dict, name: str, dir_hash: str) -> dict:
    """Normalize scan result:
    1. Extract is_safe (bool) and max_severity (str).
    2. Map API-specific fields (analysis_reason, analysis_suggestion) to standard fields.
    """
    is_safe = raw.get("is_safe")

    # Severity field priority: max_severity > analysis_level > verdict > level
    v_raw = (raw.get("max_severity") or raw.get("analysis_level") or
             raw.get("verdict") or raw.get("risk_level") or
             raw.get("level") or "UNKNOWN").upper()

    # Combined verdict logic
    if is_safe is True and v_raw in ("UNKNOWN", "SAFE"):
        verdict = "SAFE"
    elif is_safe is False and v_raw in ("UNKNOWN", "SAFE"):
        verdict = "CRITICAL"  # Explicitly marked unsafe -> critical
    else:
        verdict = v_raw

    return {
        "skill_name":    name,
        "dir_sha256":    dir_hash,
        "verdict":       verdict,
        "confidence":    raw.get("confidence") or raw.get("score"),
        "threat_labels": raw.get("threat_labels") or raw.get("tags") or [],
        "summary":       raw.get("analysis_reason") or raw.get("summary") or raw.get("description") or "",
        "findings":      raw.get("findings") or raw.get("issues") or [],
        "recommendation":raw.get("analysis_suggestion") or raw.get("recommendation") or raw.get("action") or "",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Result Display
# ─────────────────────────────────────────────────────────────────────────────

def print_result(r: dict):
    verdict  = r.get("verdict","UNKNOWN")
    emoji    = RISK_EMOJI.get(verdict,"❓")
    conf     = r.get("confidence")
    labels   = r.get("threat_labels",[])
    summary  = r.get("summary","")
    findings = r.get("findings",[])
    rec      = r.get("recommendation","")
    conf_str = f"  confidence {float(conf):.0%}" if conf is not None else ""

    divider()
    log(f"{emoji} Result: {verdict}{conf_str}")
    if summary:
        log(f"📋 {summary}")
    if labels:
        log(f"🏷️  Threat labels: {', '.join(labels)}")
    if findings:
        SEV = {"LOW":"🔵","MEDIUM":"🟡","HIGH":"🔴","CRITICAL":"☠️"}
        log(f"🔍 Findings ({len(findings)} items):")
        for f in findings:
            sev  = str(f.get("severity","")).upper()
            desc = f.get("description") or f.get("detail") or str(f)
            rid  = f.get("id") or ""
            tag  = f"[{rid}] " if rid else ""
            log(f"   {SEV.get(sev,'⚪')} {tag}{desc}")
    if rec:
        log(f"💡 Recommendation: {rec}")
    divider()

# ─────────────────────────────────────────────────────────────────────────────
# Prompt: malicious detected -> ask whether to delete
# ─────────────────────────────────────────────────────────────────────────────

def prompt_delete(skill_path: Path, result: dict) -> bool:
    """When result is HIGH/CRITICAL, ask user whether to delete the skill.
    skill_path is the original install path (not temp dir).
    Returns True if deleted.
    """
    verdict = result.get("verdict","")
    if verdict not in ("HIGH","CRITICAL"):
        return False

    if not skill_path or not skill_path.exists():
        return False

    emoji = RISK_EMOJI.get(verdict,"🔴")
    log(f"\n{emoji} This skill is marked as [{verdict}] high risk by security scan.")
    log(f"   Path: {skill_path}")

    answer = ask("Delete this skill now? [y/n]")
    if answer in ("y","Y","yes","Yes"):
        try:
            if skill_path.is_dir():
                shutil.rmtree(skill_path)
            else:
                skill_path.unlink()
            log(f"✅ Deleted: {skill_path}")
            return True
        except Exception as e:
            log(f"❌ Delete failed: {e} (please delete manually)")
            return False
    else:
        log(f"⚠️  Skipped deletion. Use this skill with caution.")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: first-run (first install)
# ─────────────────────────────────────────────────────────────────────────────

def cmd_first_run():
    """First install: list installed skills, ask user to scan, show results."""
    if STATE_FILE.exists():
        log("ℹ️  First-run scan already completed. Use scan-all to rescan.")
        return

    banner("🛡️  SkillScan First-Run Check")
    log("Welcome to SkillScan!")
    log("Searching for installed skills...\n")

    skills = find_installed_skills()
    if not skills:
        log("✅ No installed skills found, nothing to scan.")
        STATE_FILE.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
        return

    # Print installed skill list
    log(f"Found {len(skills)} installed skill(s):\n")
    for i, s in enumerate(skills, 1):
        log(f"  {i:2d}.  {s.name}")

    answer = ask("Run security scan on all listed skills? [y/n]")
    if answer not in ("y","Y","yes","Yes"):
        log("Skipped. You can run scan-all anytime to rescan.")
        STATE_FILE.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
        return

    # Scan one by one
    results = []
    for idx, skill_path in enumerate(skills, 1):
        divider(f"[{idx}/{len(skills)}] {skill_path.name}")
        tmp = None
        try:
            # Copy to temp dir (source may be read-only)
            tmp = Path(tempfile.mkdtemp(prefix="skillscan-"))
            scan_dir = tmp / skill_path.name
            shutil.copytree(skill_path, scan_dir)

            r = cloud_check(scan_dir)
            print_result(r)

            # High risk -> ask to delete (targeting original install path)
            prompt_delete(skill_path, r)
            results.append(r)

        except RuntimeError as e:
            log(f"❌ Scan failed: {e}")
            results.append({"skill_name": skill_path.name,
                             "verdict": "ERROR", "threat_labels": [],
                             "summary": str(e)[:100]})
        finally:
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)

    _print_summary(results)
    STATE_FILE.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: scan (single skill)
# ─────────────────────────────────────────────────────────────────────────────

def cmd_scan(path_str: str):
    skill_path = Path(path_str)
    if not skill_path.exists():
        log(f"❌ Path not found: {skill_path}")
        sys.exit(1)

    banner(f"Skill Security Scan  v{SCANNER_VERSION}")

    tmp = None
    original_path = skill_path if skill_path.is_dir() else None
    try:
        if skill_path.is_file():
            if skill_path.suffix.lower() not in (".zip",):
                log(f"❌ Unsupported format: {skill_path.suffix} (use .zip)")
                sys.exit(1)
            tmp = unpack_zip(skill_path)
            scan_dir = tmp
        else:
            scan_dir = skill_path

        result = cloud_check(scan_dir)
        print_result(result)

        # High risk -> ask to delete
        if original_path:
            prompt_delete(original_path, result)
        elif skill_path.is_file() and result.get("verdict") in ("HIGH","CRITICAL"):
            # Zip file: ask to delete source file
            prompt_delete(skill_path, result)

        v = result.get("verdict","UNKNOWN")
        sys.exit(0 if v in ("SAFE","LOW") else 1 if v=="MEDIUM" else 2)

    except RuntimeError as e:
        log(f"\n❌ Scan failed: {e}")
        sys.exit(3)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: scan-all
# ─────────────────────────────────────────────────────────────────────────────

def cmd_scan_all():
    banner(f"Full Skill Security Scan  v{SCANNER_VERSION}")

    skills = find_installed_skills()
    if not skills:
        log("ℹ️  No installed skills detected.")
        return

    log(f"Found {len(skills)} installed skill(s):\n")
    for i, s in enumerate(skills, 1):
        log(f"  {i:2d}.  {s.name:<30}  {s}")

    answer = ask("Start security scan? [y/n]")
    if answer not in ("y","Y","yes","Yes"):
        log("Cancelled.")
        return

    results = []
    for idx, skill_path in enumerate(skills, 1):
        divider(f"[{idx}/{len(skills)}] {skill_path.name}")
        tmp = None
        try:
            tmp = Path(tempfile.mkdtemp(prefix="skillscan-"))
            scan_dir = tmp / skill_path.name
            shutil.copytree(skill_path, scan_dir)

            r = cloud_check(scan_dir)
            v = r.get("verdict","UNKNOWN")
            log(f"{RISK_EMOJI.get(v,'❓')} Scan complete: {v}")
            if r.get("threat_labels"):
                log(f"   Threat labels: {', '.join(r['threat_labels'])}")

            # High risk: ask to delete
            prompt_delete(skill_path, r)
            results.append(r)

        except RuntimeError as e:
            log(f"❌ Scan failed: {e}")
            results.append({"skill_name": skill_path.name, "verdict":"ERROR",
                             "threat_labels":[], "summary":str(e)[:100]})
        finally:
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)

    _print_summary(results)

# ─────────────────────────────────────────────────────────────────────────────
# Summary Table
# ─────────────────────────────────────────────────────────────────────────────

def _print_summary(results):
    banner("📊 Scan Summary")
    print(f"  {'Skill Name':<28} {'Result':<12} {'Threat Labels'}")
    divider()
    for r in results:
        v      = r.get("verdict","?")
        name   = r.get("skill_name","?")[:27]
        labels = ", ".join(r.get("threat_labels",[]))[:20] or "-"
        print(f"  {name:<28} {RISK_EMOJI.get(v,'❓')}{v:<10}  {labels}")

    safes   = [r for r in results if r["verdict"] in {"SAFE","LOW"}]
    mediums = [r for r in results if r["verdict"] == "MEDIUM"]
    highs   = [r for r in results if r["verdict"] in {"HIGH","CRITICAL"}]
    errors  = [r for r in results if r["verdict"] in {"ERROR","UNKNOWN"}]

    print()
    log(f"Total {len(results)}  |  ✅ Safe {len(safes)}  "
        f"🟡 Suspicious {len(mediums)}  🔴 Dangerous {len(highs)}  ❓ Error {len(errors)}")
    if highs:
        log(f"\n⚠️  High-risk skills: {', '.join(r['skill_name'] for r in highs)}")
    elif not mediums and not errors:
        log("\n🎉 All skills passed security scan.")


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand: upgrade
# ─────────────────────────────────────────────────────────────────────────────

def cmd_upgrade():
    banner("SkillScan Auto-Upgrade")
    log(f"Current version: {SCANNER_VERSION}")
    log(f"Update source: {UPDATE_URL}")
    try:
        manifest = http_get(UPDATE_URL)
    except Exception as e:
        log(f"❌ Failed to fetch update manifest: {e}")
        return

    latest = manifest.get("version", SCANNER_VERSION)
    if (tuple(int(x) for x in latest.split(".")) <=
        tuple(int(x) for x in SCANNER_VERSION.split("."))):
        log(f"✅ Already up to date ({SCANNER_VERSION})")
        return

    log(f"New version found: {SCANNER_VERSION} → {latest}")
    log(f"Changelog: {manifest.get('changelog','(none)')}")

    download_url = manifest.get("download_url", "")
    if not download_url:
        log("⚠️  No download URL in manifest, skipping upgrade")
        return

    # Download new version zip
    log(f"📥 Downloading: {download_url}")
    try:
        req = urllib.request.Request(download_url)
        with urllib.request.urlopen(req, timeout=60) as r:
            zip_data = r.read()
    except Exception as e:
        log(f"❌ Download failed: {e}")
        return

    # SHA256 verification
    expected_sha = manifest.get("sha256", "")
    if expected_sha:
        actual_sha = hashlib.sha256(zip_data).hexdigest()
        if actual_sha != expected_sha:
            log(f"❌ SHA256 mismatch, upgrade aborted (expected {expected_sha[:16]}…, got {actual_sha[:16]}…)")
            return
        log(f"   ✅ SHA256 verified")

    # Backup current skill directory
    skill_root = Path(__file__).parent.parent
    backup_dir = skill_root.parent / f"SkillScan-backup-{SCANNER_VERSION}"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    shutil.copytree(skill_root, backup_dir)
    log(f"📦 Backed up to: {backup_dir}")

    # Extract and replace files
    tmp = Path(tempfile.mkdtemp(prefix="skillupgrade-"))
    try:
        zip_path = tmp / "update.zip"
        zip_path.write_bytes(zip_data)
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Security check: prevent zip-slip
            for member in zf.namelist():
                dest = (tmp / "extracted" / member).resolve()
                if not str(dest).startswith(str((tmp / "extracted").resolve())):
                    raise ValueError(f"zip-slip path rejected: {member}")
            zf.extractall(tmp / "extracted")

        # Overwrite skill directory with new files
        extracted = tmp / "extracted"
        for item in extracted.rglob("*"):
            if not item.is_file():
                continue
            rel = item.relative_to(extracted)
            target = skill_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            log(f"   ✅ Updated: {rel}")

        log(f"🎉 Upgraded to v{latest}")
    except Exception as e:
        log(f"❌ Upgrade failed: {e}")
        log(f"   You can restore from backup: {backup_dir}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def auto_upgrade_if_needed():
    """Auto-check for updates every 7 days, runs silently."""
    try:
        if LAST_UPDATE_CHECK_FILE.exists():
            last_check = float(LAST_UPDATE_CHECK_FILE.read_text(encoding="utf-8").strip())
            if time.time() - last_check < AUTO_UPDATE_INTERVAL:
                return  # Not time to check yet
        log("🔄 Checking for updates...")
        manifest = http_get(UPDATE_URL)
        latest = manifest.get("version", SCANNER_VERSION)
        if (tuple(int(x) for x in latest.split(".")) <=
            tuple(int(x) for x in SCANNER_VERSION.split("."))):
            log(f"   ✅ Already up to date ({SCANNER_VERSION})")
        else:
            log(f"   New version found: {SCANNER_VERSION} → {latest}, auto-updating...")
            cmd_upgrade()
        LAST_UPDATE_CHECK_FILE.write_text(str(time.time()), encoding="utf-8")
    except Exception as e:
        log(f"   ⚠️ Auto-update check failed: {e} (normal operation unaffected)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    # Check for auto-update on every run (once every 7 days)
    auto_upgrade_if_needed()

    cmd = sys.argv[1]
    if cmd == "first-run":
        cmd_first_run()
    elif cmd == "scan":
        if len(sys.argv) < 3:
            log("Usage: scanner.py scan <skill_path>")
            sys.exit(1)
        cmd_scan(sys.argv[2])
    elif cmd == "scan-all":
        cmd_scan_all()
    elif cmd == "upgrade":
        cmd_upgrade()
    else:
        log(f"Unknown command: {cmd}")
        log("Available commands: first-run / scan <path> / scan-all / upgrade")
        sys.exit(1)

if __name__ == "__main__":
    main()
