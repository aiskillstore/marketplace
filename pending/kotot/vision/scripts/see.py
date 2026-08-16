#!/usr/bin/env python3
"""
see.py - Give a non-vision model "eyes" by delegating image understanding
to any OpenAI-compatible vision model.

Stdlib only (no pip install). Config comes from environment variables, or a
.claude/settings.json "env" block (searched from the current directory upward,
then ~/.claude); an explicit environment variable wins. Variable names match
the Loveacup/vision-mcp-server MCP so they're familiar:

  VISION_BASE_URL   Full chat/completions endpoint, e.g.
                    http://localhost:1234/v1/chat/completions
                    (NOTE: include the full /v1/chat/completions path)
  VISION_MODEL      Model name, e.g. Qwen3-VL-32B / gpt-4o / glm-4v ...
  VISION_API_KEY    API key (optional for local servers; any placeholder works)
  VISION_MAX_TOKENS Max response tokens (optional, default 4096)
  VISION_TEMPERATURE Sampling temperature (optional, default 0.2)
  VISION_DETAIL     low | high | auto (optional, default auto)
  VISION_TIMEOUT    Request timeout seconds (optional, default 120)

Usage:
  python3 see.py <image_path_or_url> ["question / instruction"]
  python3 see.py screenshot.png "What error is shown in this screenshot?"
  python3 see.py chart.png "Extract every label and value as a table"
  python3 see.py https://example.com/photo.jpg "Describe this image"
  python3 see.py --dry-run shot.png "test"     # build request but don't send

Output: plain text answer on stdout. On failure: message on stderr, exit 1.
"""

import sys
import os
import re
import json
import base64
import mimetypes
import urllib.request
import urllib.error

DEFAULT_PROMPT = "Describe this image in detail. If it contains text, transcribe it."


def die(msg, code=1):
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(code)


def _settings_candidates():
    """Yield .claude/settings(.local).json paths, highest precedence first:
    the project dir (CLAUDE_PROJECT_DIR, then cwd walked upward), then the
    user-global ~/.claude."""
    bases = []
    proj = os.environ.get("CLAUDE_PROJECT_DIR")
    if proj:
        bases.append(proj)
    d = os.getcwd()
    while True:
        bases.append(d)
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    bases.append(os.path.expanduser("~"))
    seen = set()
    for base in bases:
        for name in ("settings.local.json", "settings.json"):
            path = os.path.join(base, ".claude", name)
            if path not in seen:
                seen.add(path)
                yield path


def _load_settings_env():
    """Collect VISION_* config from .claude/settings.json files. Reads the
    `env` block (Claude Code's format), with top-level keys as a fallback.
    Nearer / more-local files win. Returns (config_dict, loaded_paths)."""
    config = {}
    loaded = []
    for path in _settings_candidates():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            continue
        except (ValueError, OSError) as e:
            sys.stderr.write("[see.py] Warning: skipping %s: %s\n" % (path, e))
            continue
        if not isinstance(data, dict):
            continue
        loaded.append(path)
        env_block = data.get("env") if isinstance(data.get("env"), dict) else {}
        for src in (env_block, data):
            for k, v in src.items():
                if k.startswith("VISION_") and k not in config and isinstance(v, (str, int, float)):
                    config[k] = str(v)
    return config, loaded


# Some hosting platforms (e.g. OpenClaw) hand tools their credentials via a
# plain dotenv file rather than settings.json. /root/.openclaw/.env is checked
# first (absolute, works regardless of what $HOME resolves to for whatever
# process actually runs this script), then ~/.openclaw/.env.
_OPENCLAW_ENV_PATHS = ("/root/.openclaw/.env", "~/.openclaw/.env")


def _load_openclaw_env():
    """Collect VISION_* config from OpenClaw-style dotenv files. Returns
    (config_dict, loaded_paths); first path that defines a key wins."""
    config = {}
    loaded = []
    seen_paths = set()
    for raw_path in _OPENCLAW_ENV_PATHS:
        path = os.path.abspath(os.path.expanduser(raw_path))
        if path in seen_paths or not os.path.isfile(path):
            continue
        seen_paths.add(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue
        loaded.append(path)
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("\"'")
            if k.startswith("VISION_") and k not in config:
                config[k] = v
    return config, loaded


def is_url(s):
    return bool(re.match(r"^https?://", s, re.IGNORECASE))


def to_image_url(src):
    """Return a value usable as OpenAI image_url.url: pass http(s) URLs through,
    convert local files to a base64 data URL."""
    if is_url(src):
        return src
    if not os.path.isfile(src):
        die("Image not found: %s\n(Pass a local file path or an http(s) URL.)" % src)
    mime, _ = mimetypes.guess_type(src)
    if not mime or not mime.startswith("image/"):
        # Fall back by extension; default to png.
        ext = os.path.splitext(src)[1].lower().lstrip(".")
        mime = "image/" + (ext if ext in ("png", "jpeg", "jpg", "gif", "webp", "bmp") else "png")
        if mime == "image/jpg":
            mime = "image/jpeg"
    with open(src, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def main(argv):
    args = [a for a in argv if a != "--dry-run"]
    dry_run = "--dry-run" in argv or os.environ.get("VISION_DRY_RUN") == "1"

    if len(args) < 1:
        die("Usage: python3 see.py <image_path_or_url> [\"question\"]")

    image_src = args[0]
    prompt = args[1] if len(args) > 1 else DEFAULT_PROMPT

    settings_env, settings_files = _load_settings_env()
    openclaw_env, openclaw_files = _load_openclaw_env()

    def cfg(name, default=""):
        """Env var wins; then .claude/settings.json; then an OpenClaw-style
        dotenv file (see _load_openclaw_env)."""
        val = os.environ.get(name, "")
        if val == "":
            val = settings_env.get(name, "")
        if val == "":
            val = openclaw_env.get(name, default)
        return val

    base_url = cfg("VISION_BASE_URL").strip()
    model = cfg("VISION_MODEL").strip()
    api_key = cfg("VISION_API_KEY").strip()
    max_tokens = int(cfg("VISION_MAX_TOKENS", "4096"))
    temperature = float(cfg("VISION_TEMPERATURE", "0.2"))
    detail = cfg("VISION_DETAIL", "auto").strip() or "auto"
    timeout = float(cfg("VISION_TIMEOUT", "120"))

    missing = [n for n, v in (("VISION_BASE_URL", base_url), ("VISION_MODEL", model)) if not v]
    if missing:
        die("Missing required config: %s\n"
            "Provide it as an environment variable, or in a .claude/settings.json \"env\" block.\n"
            "  Env:  export VISION_BASE_URL=http://localhost:1234/v1/chat/completions\n"
            "        export VISION_MODEL=Qwen3-VL-32B\n"
            "  File: .claude/settings.json ->\n"
            "        { \"env\": { \"VISION_BASE_URL\": \"...\", \"VISION_MODEL\": \"...\", \"VISION_API_KEY\": \"...\" } }"
            % ", ".join(missing))

    if "/chat/completions" not in base_url:
        sys.stderr.write(
            "[see.py] Warning: VISION_BASE_URL does not contain '/chat/completions'. "
            "It should be the full endpoint, e.g. http://host:port/v1/chat/completions\n")

    image_url = to_image_url(image_src)

    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url, "detail": detail}},
            ],
        }],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if dry_run:
        preview = json.loads(json.dumps(payload))
        u = preview["messages"][0]["content"][1]["image_url"]["url"]
        if u.startswith("data:"):
            preview["messages"][0]["content"][1]["image_url"]["url"] = u[:40] + "...<base64 %d chars>" % len(u)
        sys.stderr.write("[dry-run] POST %s\n" % base_url)
        config_files = settings_files + openclaw_files
        if config_files:
            sys.stderr.write("[dry-run] config sources: %s\n" % ", ".join(config_files))
        sys.stderr.write(json.dumps(preview, ensure_ascii=False, indent=2) + "\n")
        return 0

    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key

    req = urllib.request.Request(base_url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        detail_body = e.read().decode("utf-8", "replace") if hasattr(e, "read") else ""
        die("Vision API HTTP %s: %s\n%s" % (e.code, e.reason, detail_body[:2000]))
    except urllib.error.URLError as e:
        die("Could not reach VISION_BASE_URL (%s): %s\n"
            "Check the endpoint is running and the URL is correct." % (base_url, e.reason))
    except Exception as e:  # noqa
        die("Request failed: %s" % e)

    try:
        obj = json.loads(body)
        text = obj["choices"][0]["message"]["content"]
    except Exception:
        die("Unexpected response shape from vision endpoint:\n" + body[:2000])

    if isinstance(text, list):  # some servers return content as parts
        text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
    print(text.strip() if isinstance(text, str) else str(text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
