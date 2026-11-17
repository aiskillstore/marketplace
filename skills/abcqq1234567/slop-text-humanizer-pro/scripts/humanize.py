#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slop Text Humanizer Pro — cloud processing script.

Sends text through the cloud humanizer engine (OpenAI-compatible API).
Modes and mode descriptions live in the cloud: the backend can add, rename,
describe, enable or disable them at any time — always fetch the list fresh
with --list-modes instead of guessing from memory.

Key resolution order:
  1. SK_HAI_KEY env var (personal key) — wins if set
  2. Personal key saved on this machine (~/.slop-text-humanizer-pro/config.json)
  3. Shared free key — fetched automatically from the engine's public config
     endpoint at runtime. The package never ships a key; server-side key
     rotation takes effect instantly.

Errors from the engine (too short / too long / quota drained / bad key) are
passed through to the host AI verbatim — show them to the user as-is.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

ENGINE = "https://1257655569-3o00dbw8fr.ap-singapore.tencentscf.com"
API_URL = ENGINE + "/v1/chat/completions"
MODELS_URL = ENGINE + "/v1/models"
CONFIG_URL = ENGINE + "/api/user/config"
# This skill's dedicated slot on the engine (slot id <= 30 chars)
SLOT_ID = "slop-text-humanizer-pro"

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.expanduser("~"), ".slop-text-humanizer-pro", "config.json")

# Golden Pair recipes: curated two-stage pipelines (stage 1 breaks the AI
# structure, stage 2 rebuilds and polishes — same language in, same language
# out). Single mode is for beginners; combos are for drafts that keep failing.
# Combo agents created in the admin panel also appear in --list-modes.
RECIPES = [
    {
        "id": "structure-first",
        "name": "Structure First",
        "stages": ["wenzi_runs", "wenzi_power"],
        "desc": "Break the AI skeleton first, then rebuild with maximum strength. The author's daily flow; best for heavily AI-flavored drafts.",
    },
    {
        "id": "deep-reshape",
        "name": "Deep Reshape",
        "stages": ["xierun_lian", "wenzi_power"],
        "desc": "Reshape pass first, then a maximum-strength rebuild. For drafts that keep failing after single modes.",
    },
]

NO_KEY_MSG = ("Could not get a key right now (not configured on the engine "
              "side, or network issue). Retry shortly, or set SK_HAI_KEY / "
              "use --save-key with a personal key.")


def out(payload):
    print(json.dumps(payload, ensure_ascii=False))


def utf8_stdout():
    s = sys.stdout
    if s.encoding and s.encoding.lower() not in ("utf-8", "utf8"):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


# ---------- key handling ----------

def load_config(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_saved_key(config_path):
    return str(load_config(config_path).get("api_key", "") or "").strip()


def load_saved_mode(config_path):
    # auto (default: use personal key) / public (temporarily use shared key,
    # personal key kept on file)
    return str(load_config(config_path).get("mode", "") or "").strip()


def save_config(cfg, config_path):
    try:
        d = os.path.dirname(config_path)
        if d:
            os.makedirs(d, exist_ok=True)
        fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)
        try:
            os.chmod(config_path, 0o600)
        except Exception:
            pass
        return True
    except Exception as e:
        out({"success": False, "result": "", "message": "Failed to save key config: %s" % e})
        return False


def fetch_public_key():
    """Fetch the shared free key from the engine's public config endpoint
    (the package never ships a key; server-side rotation takes effect instantly)."""
    try:
        req = urllib.request.Request(CONFIG_URL + "?slot=" + SLOT_ID, method="GET")
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
        return str(data.get("publicKey", "") or "").strip()
    except Exception:
        return ""


def resolve_key(args):
    explicit = (args.api_key or "").replace("Bearer", "").strip()
    if explicit:
        return explicit
    env = os.environ.get("SK_HAI_KEY", "").strip()
    if env:
        return env
    if load_saved_mode(args.config_path) != "public":
        saved = load_saved_key(args.config_path)
        if saved:
            return saved
    return fetch_public_key()


def mask(key):
    return key[:8] + "****" + key[-4:] if len(key) > 16 else "****"


def bad_key_msg():
    return ("This key was rejected by the engine. A personal key must start "
            "with sk-hai-. Check the key, or clear it with --clear-key to "
            "fall back to the shared free key.")


def check_key_format(key):
    # The overseas engine only accepts sk-hai- keys; reject anything else
    # up front so users get a clear message instead of a raw 401.
    if not key.startswith("sk-hai-"):
        out({"success": False, "result": "", "message": bad_key_msg()})
        return False
    return True


# ---------- engine calls ----------

def call_engine(text, model_id, api_key):
    """One pass through the engine. Returns {"success", "result", "message"}.
    Engine errors (char limits, quota drained, bad key) are passed through
    verbatim — the host AI should show them to the user as-is."""
    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": text}],
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    })
    try:
        with urllib.request.urlopen(req, timeout=300) as res:
            data = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8"))
            msg = str((err.get("error") or {}).get("message", "") or "").strip()
        except Exception:
            msg = ""
        return {"success": False, "result": "", "message": msg or ("Engine error HTTP %s" % e.code)}
    except Exception as e:
        return {"success": False, "result": "", "message": "Network request failed: %s" % e}

    err = str((data.get("error") or {}).get("message", "") or "").strip()
    if err:
        return {"success": False, "result": "", "message": err}
    choice = ((data.get("choices") or [{}])[0])
    content = str((((choice.get("message") or {}).get("content"))) or "").strip()
    # Some upstream models wrap output in <think>...</think> reasoning blocks —
    # strip them (and zero-width chars) so the user never sees tag noise.
    content = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.I)
    content = re.sub(r"</?think>", "", content, flags=re.I)
    content = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", content).strip()
    if not content:
        return {"success": False, "result": "", "message": "Engine returned an empty result."}
    return {"success": True, "result": content, "message": "ok"}


def list_modes(api_key):
    """Fetch the live mode list from the engine (names + descriptions).
    Modes are managed in the cloud — always fetch fresh, never guess."""
    req = urllib.request.Request(MODELS_URL, method="GET", headers={
        "Authorization": "Bearer " + api_key,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"success": False, "result": "", "models": [], "message": bad_key_msg() if e.code == 401 else ("Failed to list modes: HTTP %s" % e.code)}
    except Exception as e:
        return {"success": False, "result": "", "models": [], "message": "Failed to list modes: %s" % e}

    items = data.get("data", []) if isinstance(data, dict) else []
    if not items:
        return {"success": False, "result": "", "models": [], "message": "The engine returned no modes."}

    models = []
    lines = ["Available processing modes (%d):" % len(items)]
    for i, m in enumerate(items, 1):
        mid = str(m.get("id", "") or "")
        name = str(m.get("name", "") or "") or mid
        desc = str(m.get("desc", "") or "").strip()
        models.append({"id": mid, "name": name, "desc": desc})
        seg = "%d. %s (mode id: %s)" % (i, name, mid)
        if desc:
            seg += " — " + desc
        lines.append(seg)
    lines.append("Run one with: --mode <mode-id> --input <file-or-text>")
    return {"success": True, "result": "\n".join(lines), "models": models, "message": "ok"}


def list_recipes():
    lines = ["Available Golden Pair recipes (%d):" % len(RECIPES)]
    recipes = []
    for i, r in enumerate(RECIPES, 1):
        pipeline = " -> ".join(r["stages"])
        recipes.append({"id": r["id"], "name": r["name"], "stages": r["stages"], "desc": r["desc"]})
        lines.append("%d. %s (recipe id: %s)  [%s] — %s" % (i, r["name"], r["id"], pipeline, r["desc"]))
    lines.append("Run one with: --recipe <recipe-id> --input <file-or-text>")
    lines.append("Note: combo agents created on the engine side also appear in --list-modes and can be run like any mode.")
    return {"success": True, "result": "\n".join(lines), "recipes": recipes, "message": "ok"}


def run_recipe(recipe, text, api_key):
    """Run a curated two-stage pipeline: stage 1 breaks the AI structure,
    stage 2 rebuilds and polishes. Returns the final text plus per-stage notes."""
    notes = []
    content = text
    for i, mid in enumerate(recipe["stages"], 1):
        r = call_engine(content, mid, api_key)
        if not r["success"]:
            return {"success": False, "result": "",
                    "message": "Recipe '%s' stopped at stage %d (%s): %s"
                               % (recipe["id"], i, mid, r["message"])}
        notes.append("stage %d (%s): ok" % (i, mid))
        content = r["result"]
    return {"success": True, "result": content,
            "message": "recipe '%s' (%s) — %s" % (recipe["id"], " -> ".join(recipe["stages"]), "; ".join(notes))}


# ---------- input ----------

def read_input(value):
    """--input accepts either a UTF-8 file path or the literal text."""
    v = (value or "").strip()
    if not v:
        return None, "Missing --input: pass a UTF-8 file path or the text itself."
    if os.path.exists(v):
        try:
            with open(v, "r", encoding="utf-8") as f:
                return f.read().strip(), ""
        except Exception as e:
            return None, "Could not read file %s: %s" % (v, e)
    if len(v) < 260 and ("\n" not in v) and os.path.splitext(v)[1] and not v.endswith(("。", ".", "!", "?", "！", "？")):
        # looks like a path but the file does not exist
        return None, "File not found: %s" % v
    return v, ""


def main():
    utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Slop Text Humanizer Pro — humanize AI-written text via the cloud engine.")
    parser.add_argument("--list-modes", action="store_true",
                        help="Fetch the live mode list from the engine (always do this before choosing a mode)")
    parser.add_argument("--mode", default="", help="Mode id (see --list-modes)")
    parser.add_argument("--list-recipes", action="store_true",
                        help="List the curated Golden Pair recipes")
    parser.add_argument("--recipe", default="", help="Recipe id (see --list-recipes)")
    parser.add_argument("--input", default="", help="UTF-8 file path or the literal text")
    parser.add_argument("--api-key", default="", help="Key for this run only")
    parser.add_argument("--save-key", default="", help="Save a personal key (sk-hai-...) permanently")
    parser.add_argument("--use", choices=["public", "personal"], default="",
                        help="public=use the shared key for now (personal key kept); personal=switch back")
    parser.add_argument("--show-key", action="store_true", help="Show which key is currently in use (masked)")
    parser.add_argument("--clear-key", action="store_true", help="Delete the saved personal key")
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH,
                        help="Key config file path (default ~/.slop-text-humanizer-pro/config.json)")
    args = parser.parse_args()

    # ---- key management ----
    if args.save_key:
        key = args.save_key.replace("Bearer", "").strip()
        if not key.startswith("sk-hai-"):
            out({"success": False, "result": "", "message": bad_key_msg()})
            return
        if save_config({"api_key": key, "mode": "auto"}, args.config_path):
            out({"success": True, "result":
                 "Personal key saved and enabled: %s (stored in plaintext at %s on this machine "
                 "only; remove anytime with --clear-key, or say \"use the shared key\" to switch "
                 "temporarily — the saved key is kept)." % (mask(key), args.config_path),
                 "message": "ok"})
        return
    if args.use:
        cfg = load_config(args.config_path)
        saved = str(cfg.get("api_key", "") or "").strip()
        if not saved:
            out({"success": False, "result": "", "message":
                 "No personal key saved yet, nothing to switch. To bind one, send your sk-hai- key "
                 "and ask to save it."})
            return
        cfg["mode"] = "public" if args.use == "public" else "auto"
        if save_config(cfg, args.config_path):
            if args.use == "public":
                out({"success": True, "result":
                     "Switched to the shared free key for now (fair-use limits apply). Your personal "
                     "key %s is kept — say \"use my key\" to switch back." % mask(saved), "message": "ok"})
            else:
                out({"success": True, "result":
                     "Switched back to your personal key %s (no shared-key limits)." % mask(saved),
                     "message": "ok"})
        return
    if args.clear_key:
        removed = False
        if os.path.exists(args.config_path):
            try:
                os.remove(args.config_path)
                removed = True
            except Exception as e:
                out({"success": False, "result": "", "message": "Failed to remove %s: %s" % (args.config_path, e)})
                return
        out({"success": True, "result":
             ("Personal key deleted (%s). " % args.config_path if removed else "No saved key found. ")
             + "Back to the shared free key (fair-use limits apply).", "message": "ok"})
        return
    if args.show_key:
        saved = load_saved_key(args.config_path)
        if saved and load_saved_mode(args.config_path) != "public":
            out({"success": True, "result":
                 "In use: %s (personal key, saved at %s)" % (mask(saved), args.config_path), "message": "ok"})
        else:
            pub = fetch_public_key()
            shown = mask(pub) if pub else "(not configured on the engine side)"
            extra = (" (personal key %s kept; say \"use my key\" to switch back)" % mask(saved)
                     if saved else " (fair-use limits apply)")
            out({"success": True, "result": "In use: %s (shared free key from the engine)%s" % (shown, extra),
                 "message": "ok"})
        return
    if args.list_recipes:
        out(list_recipes())
        return
    if args.list_modes:
        key = resolve_key(args)
        if not key:
            out({"success": False, "result": "", "models": [], "message": NO_KEY_MSG})
            return
        if not check_key_format(key):
            return
        out(list_modes(key))
        return

    # ---- main flow: --mode / --recipe ----
    if not args.mode and not args.recipe:
        out({"success": False, "result": "", "message":
             "Missing mode: run --list-modes first, then use --mode <mode-id>; "
             "for combos run --list-recipes and use --recipe <recipe-id>."})
        return
    if args.mode and args.recipe:
        out({"success": False, "result": "", "message": "Use either --mode or --recipe, not both."})
        return

    text, err = read_input(args.input)
    if err:
        out({"success": False, "result": "", "message": err})
        return
    if not text:
        out({"success": False, "result": "", "message": "Input is empty."})
        return

    key = resolve_key(args)
    if not key:
        out({"success": False, "result": "", "message": NO_KEY_MSG})
        return
    if not check_key_format(key):
        return

    if args.recipe:
        recipe = next((r for r in RECIPES if r["id"] == args.recipe.strip()), None)
        if not recipe:
            ids = ", ".join(r["id"] for r in RECIPES)
            out({"success": False, "result": "", "message":
                 "Unknown recipe '%s'. Available: %s (see --list-recipes)" % (args.recipe.strip(), ids)})
            return
        out(run_recipe(recipe, text, key))
        return

    out(call_engine(text, args.mode.strip(), key))


if __name__ == "__main__":
    main()
