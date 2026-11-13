#!/usr/bin/env python3
"""go-public helper. Standard library only.

  python3 share.py check   workflow.json            validate the workflow
  python3 share.py try     workflow.json [N]        run example N (default 1) through the real AI, print each step
  python3 share.py build   workflow.json page.html  write the single-file page
  python3 share.py publish page.html               publish (first time) or update (same link) the page
  python3 share.py delete                           take the published page down

publish/delete keep the page id and its private edit token in .go-public.json in the
current folder. Never put that token in the page or in a public repo.
"""
import json, os, re, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
API = os.environ.get("GO_PUBLIC_API", "https://onetagai.com")
DEMO_KEY = "ot_demo000000000000000000000"  # shared demo key, only for `try`
STATE = ".go-public.json"
VAR = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")

def die(msg):
    print("error: " + msg, file=sys.stderr); sys.exit(1)

def load(path):
    try: wf = json.load(open(path))
    except Exception as e: die(f"{path} is not valid JSON: {e}")
    problems = []
    if not str(wf.get("title", "")).strip(): problems.append("title is empty")
    inputs, steps = wf.get("inputs") or [], wf.get("steps") or []
    if not inputs: problems.append("inputs is empty: a visitor needs something to fill in")
    if not steps: problems.append("steps is empty")
    known = set()
    for f in inputs:
        if not re.fullmatch(r"[\w-]+", str(f.get("id", ""))): problems.append(f"input id {f.get('id')!r} must be letters, digits, _ or -")
        if f.get("type", "textarea") not in ("textarea", "text", "select"): problems.append(f"input {f.get('id')}: type must be textarea, text or select")
        if f.get("type") == "select" and not f.get("options"): problems.append(f"input {f.get('id')}: select needs options")
        if not f.get("label"): problems.append(f"input {f.get('id')}: label is empty")
        known.add(f.get("id"))
    for i, s in enumerate(steps, 1):
        sid = s.get("id")
        if not re.fullmatch(r"[\w-]+", str(sid or "")): problems.append(f"step {i}: id must be letters, digits, _ or -")
        if not str(s.get("prompt", "")).strip(): problems.append(f"step {sid}: prompt is empty")
        for field in ("prompt", "system", "input"):
            for name in VAR.findall(str(s.get(field) or "")):
                if name not in known: problems.append(f"step {sid}: {{{{{name}}}}} in {field} is not an input or an earlier step")
        if sid in known: problems.append(f"step id {sid} is already used")
        known.add(sid)
    if not any(s.get("show") for s in steps): problems.append("no step has show: true, so visitors would see nothing")
    for j, ex in enumerate(wf.get("examples") or [], 1):
        if not isinstance(ex.get("values"), dict): problems.append(f"example {j}: values must be an object of input id -> text")
    if problems: die("workflow problems:\n  - " + "\n  - ".join(problems))
    return wf

def ask(prompt, system, inp, max_tokens):
    body = {"key": DEMO_KEY, "prompt": prompt, "system": system or None, "max_tokens": max_tokens, "via": "go-public"}
    if inp: body["input"] = inp
    req = urllib.request.Request(API + "/v1/ask", json.dumps(body).encode(), {"Content-Type": "application/json", "Origin": "http://localhost"})
    try: return json.load(urllib.request.urlopen(req, timeout=120))["text"]
    except urllib.error.HTTPError as e:
        die(f"AI call failed ({e.code}): {e.read().decode()[:300]}")

def cmd_try(path, n="1"):
    wf = load(path)
    exs = wf.get("examples") or []
    if not exs: die("add at least one example to try (examples: [{label, values}])")
    ex = exs[int(n) - 1]
    vars = {k: str(v) for k, v in ex["values"].items()}
    fill = lambda t: VAR.sub(lambda m: vars.get(m.group(1), ""), str(t or ""))
    for s in wf["steps"]:
        out = ask(fill(s["prompt"]), fill(s.get("system")), fill(s.get("input")) if s.get("input") else None, s.get("maxTokens", 800))
        vars[s["id"]] = out
        print(f"--- step {s['id']}{' (shown)' if s.get('show') else ''} ---\n{out}\n")

def cmd_build(path, out):
    wf = load(path)
    page = open(os.path.join(HERE, "template.html")).read()
    data = json.dumps(wf, ensure_ascii=False, indent=2).replace("</", "<\\/")
    title = wf["title"].replace("&", "&amp;").replace("<", "&lt;")
    page = page.replace("__WORKFLOW_JSON__", data).replace("__TITLE__", title)
    open(out, "w").write(page)
    print(f"wrote {out} ({len(page.encode()):,} bytes)")

def call(method, url, body=None, token=None):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, json.dumps(body).encode() if body is not None else None, h, method=method)
    try: return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        die(f"{method} {url} failed ({e.code}): {e.read().decode()[:300]}")

def cmd_publish(page):
    html = open(page).read()
    if "ONETAG_PAGE_KEY" not in html: die("the page has no ONETAG_PAGE_KEY placeholder; build it with share.py build")
    title = (re.search(r"<title>(.*?)</title>", html, re.S) or [None, "AI page"])[1].strip()
    body = {"html": html, "title": title, "via": "go-public"}
    state = json.load(open(STATE)) if os.path.exists(STATE) else None
    if state:
        r = call("PUT", f"{API}/api/pages/{state['id']}", body, state["edit_token"])
        print(f"updated: {state['url']}")
    else:
        r = call("POST", f"{API}/api/pages", body)
        json.dump({"id": r["id"], "url": r["url"], "edit_token": r["edit_token"], "claim_url": r.get("claim_url")}, open(STATE, "w"), indent=1)
        os.chmod(STATE, 0o600)
        print(f"published: {r['url']}")
        print(f"limits: {json.dumps(r.get('limits', {}))}")
    gi = ".gitignore"
    if os.path.isdir(".git") and STATE not in (open(gi).read() if os.path.exists(gi) else ""):
        open(gi, "a").write("\n" + STATE + "\n"); print(f"added {STATE} to .gitignore")

def cmd_delete():
    if not os.path.exists(STATE): die(f"no {STATE} here, so nothing published from this folder")
    state = json.load(open(STATE))
    call("DELETE", f"{API}/api/pages/{state['id']}", None, state["edit_token"])
    os.remove(STATE); print(f"deleted {state['url']}")

if __name__ == "__main__":
    a = sys.argv[1:]
    cmds = {"check": lambda p: (load(p), print("ok")), "try": cmd_try, "build": cmd_build, "publish": cmd_publish, "delete": cmd_delete}
    if not a or a[0] not in cmds: print(__doc__); sys.exit(1)
    cmds[a[0]](*a[1:])
