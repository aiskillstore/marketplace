"""Map a shell command to a coarse workload category.

Only the category and an allowlisted tool name ever leave this module. Command
text is never stored or reported.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional, Tuple, Union

SHELLS = {"powershell", "pwsh", "cmd", "bash", "sh", "zsh", "fish", "wsl"}
PAYLOAD_FLAGS = {"-c", "-lc", "-cl", "-ic", "-command", "/c", "/k"}

PRIORITY = [
    "test",
    "build_compile",
    "dependency_install",
    "container_vm",
    "dev_server",
    "script_runtime",
    "vcs_local",
    "network",
    "wait",
    "file_search_read",
    "system_query",
    "other_tool",
]
_RANK = {c: i for i, c in enumerate(PRIORITY)}

FAMILIES = {
    "git", "gh", "npm", "pnpm", "yarn", "bun", "node", "deno", "npx", "tsc", "vite", "webpack",
    "esbuild", "eslint", "prettier", "jest", "vitest", "playwright", "python", "py", "pip", "uv",
    "poetry", "pytest", "ruff", "mypy", "cargo", "rustc", "go", "dotnet", "msbuild", "make",
    "cmake", "ninja", "gcc", "clang", "gradle", "mvn", "java", "docker", "kubectl", "wsl",
    "powershell", "pwsh", "bash", "sh", "curl", "wget", "ssh", "rsync", "winget", "choco", "scoop",
    "brew", "apt", "apt-get", "ls", "cat", "grep", "rg", "find", "sed", "awk", "tar", "zip",
    "robocopy", "sleep", "start-sleep", "get-content", "get-childitem", "select-string", "swift",
    "xcodebuild", "ruby", "bundle", "php", "composer",
}

_SKIP_PREFIX = {"sudo", "time", "env", "corepack", "call", "command", "exec", "nohup", "builtin", "do", "then", "else"}
_TRIVIAL = re.compile(
    r"^(?:(?:cd|pushd|popd|set-location|sl|export|source|echo|write-host|write-output|printf|true|false|"
    r"foreach|for|while|until|if|elif|else|elseif|try|catch|finally|function|param|switch|return|exit|"
    r"done|fi|esac)\b|set(?=\s|$)|\$\S+\s*=|\[\w|\.\s|:$)",
    re.I,
)

_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", re.S)
_HERESTR = re.compile(r"@(['\"]).*?\1@", re.S)
_QUOTED = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"")
_SPLIT = re.compile(r"&&|\|\||[;|\n{}]")
_ENVASSIGN = re.compile(r"^(?:[A-Za-z_]\w*=\S*\s+)+")
_PKG_OPTS = re.compile(
    r"(?<=\s)(?:--(?:filter|prefix|dir|workspace|cwd)|-[FC])(?:=|\s+)\S+|(?<=\s)(?:--?[a-z][a-z-]*)(?=\s)",
    re.I,
)

_PRE = (
    r"(?:npx\s+(?:-y\s+|--yes\s+)?|bunx\s+|pnpm\s+(?:exec|dlx)\s+|yarn\s+|uv\s+run\s+|"
    r"poetry\s+run\s+|py(?:\s+-\S+)*\s+-m\s+|python3?\s+-m\s+)?"
)


def _r(pattern: str) -> "re.Pattern[str]":
    return re.compile(pattern, re.I)


_RULES = [
    ("test", _r(r"^" + _PRE + r"(?:pytest|py\.test|jest|vitest|mocha|ava|tox|nox|rspec|ctest|phpunit|unittest|playwright\s+test)\b")),
    ("test", _r(r"^(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|e2e|vitest|jest)\S*")),
    ("test", _r(r"^(?:cargo|go|dotnet|swift|flutter|deno|bun|mvn|gradle|\./gradlew|gradlew)\s+(?:nextest\s+run|test)\b")),
    ("test", _r(r"^node\s+--test\b")),
    ("build_compile", _r(r"^cargo\s+(?:build|check|clippy|doc|fmt|bench|install|rustc)\b")),
    ("build_compile", _r(r"^go\s+(?:build|vet|install|generate)\b")),
    ("build_compile", _r(r"^dotnet\s+(?:build|publish|msbuild|pack)\b")),
    ("build_compile", _r(r"^(?:\./)?(?:gradlew?|mvnw?)\b(?!\s+test)")),
    ("build_compile", _r(r"^" + _PRE + r"(?:vite\s+build|next\s+build|nuxt\s+build|astro\s+build|tauri\s+build|electron-builder|electron-forge|pyinstaller|tsc|swc|esbuild|rollup|webpack(?!\s+serve)|parcel\s+build|turbo|nx|eslint|prettier|biome|ruff|mypy|pyright|black|isort|flake8|pylint|compileall)\b")),
    ("build_compile", _r(r"^(?:make|nmake|cmake|ninja|msbuild|xcodebuild|bazel|buck2?|meson|scons|gcc|g\+\+|cc|c\+\+|clang\+*|rustc|javac|kotlinc|ld|link|cl)\b")),
    ("build_compile", _r(r"^(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:build|compile|bundle|lint|typecheck|type-check|tsc|check|format|pack|dist|package|make|prebuild|postbuild)\S*")),
    ("dependency_install", _r(r"^(?:npm|pnpm|yarn|bun)\s+(?:install|i|add|ci|update|upgrade|up|remove|rm|uninstall|dedupe|rebuild|link|prune)\b")),
    ("dependency_install", _r(r"^(?:pip3?\s+(?:install|download|uninstall)|python3?\s+-m\s+pip\s+\S+|uv\s+(?:pip\s+install|sync|add|lock)|poetry\s+(?:install|add|update)|pipx\s+install|conda\s+(?:install|create|update)|mamba\s+install)\b")),
    ("dependency_install", _r(r"^(?:cargo\s+(?:fetch|add|update|vendor)|go\s+(?:get|mod\s+(?:download|tidy))|dotnet\s+(?:restore|add\s+package|tool\s+install)|bundle\s+install|gem\s+install|composer\s+(?:install|update)|nuget)\b")),
    ("dependency_install", _r(r"^(?:winget|choco|scoop|brew|apt|apt-get|dnf|yum|pacman|zypper|snap|apk)\b")),
    ("container_vm", _r(r"^(?:docker|docker-compose|podman|kubectl|vagrant|qemu\S*|multipass|limactl|minikube|helm)\b")),
    ("container_vm", _r(r"^wsl\s+--(?:shutdown|install|update|unregister|import|export|terminate|set-version|mount)\b")),
    ("dev_server", _r(r"^(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:dev|start|serve|watch|preview|storybook)\S*")),
    ("dev_server", _r(r"^" + _PRE + r"(?:vite|next\s+dev|nuxt\s+dev|astro\s+dev|webpack\s+serve|http-server|serve|live-server|nodemon|ts-node-dev|uvicorn|gunicorn|flask\s+run|http\.server|hugo\s+server|jekyll\s+serve)\b")),
    ("dev_server", _r(r"^(?:python3?\s+manage\.py\s+runserver|rails\s+s(?:erver)?|php\s+-s)\b")),
    ("network", _r(r"^git\s+(?:-C\s+\S+\s+)?(?:clone|fetch|pull|push|submodule|lfs|ls-remote)\b")),
    ("vcs_local", _r(r"^git\b")),
    ("network", _r(r"^(?:curl|wget|invoke-webrequest|iwr|invoke-restmethod|irm|ssh|scp|sftp|rsync|ping|nslookup|tracert|nc|telnet|test-netconnection|httpie|aria2c|ftp|gh|az|aws|gcloud|vercel|netlify|firebase|wrangler|supabase|flyctl)\b")),
    ("wait", _r(r"^(?:sleep|start-sleep|timeout|pause|wait|read-host)\b")),
    ("script_runtime", _r(r"^(?:python3?|py|node|deno|bun|ruby|perl|php|lua|julia|rscript|java|tsx|ts-node|dotnet\s+run|go\s+run|cargo\s+run|powershell|pwsh|npx|uv\s+run|poetry\s+run)\b")),
    ("script_runtime", _r(r"^(?:\./\S+|\.\\\S+|&\s*\S+|(?:bash|sh|zsh)\s+\S+\.sh\b)")),
    ("file_search_read", _r(r"^(?:ls|dir|cat|type|head|tail|wc|grep|egrep|fgrep|rg|ag|find|fd|tree|stat|file|du|df|pwd|realpath|readlink|which|where|get-content|gc|get-childitem|gci|select-string|sls|test-path|get-item|get-itemproperty|resolve-path|measure-object|get-location|sort|uniq|cut|tr|awk|sed|jq|diff|cmp|md5sum|sha\d*sum|get-filehash|certutil|more|less|cp|copy|copy-item|mv|move|move-item|mkdir|md|new-item|rm|del|remove-item|touch|ln|chmod|ren|rename-item|robocopy|xcopy|tar|unzip|zip|expand-archive|compress-archive|7z|attrib|icacls)\b")),
    ("system_query", _r(r"^(?:get-ciminstance|get-wmiobject|wmic|systeminfo|get-process|tasklist|taskkill|stop-process|get-service|get-command|get-host|get-date|hostname|whoami|uname|ver|env|printenv|get-psdrive|get-netipaddress|netstat|ipconfig|reg|get-counter|get-eventlog|powercfg|nproc|free|lscpu)\b")),
]


def _head(token: str) -> str:
    t = token.strip("\"'").replace("\\", "/").rsplit("/", 1)[-1].lower()
    return t[:-4] if t.endswith(".exe") else t


def to_text(command: Union[str, Iterable[str], None]) -> str:
    if isinstance(command, (list, tuple)):
        parts = [str(x) for x in command]
        if parts and _head(parts[0]) in SHELLS:
            for i, p in enumerate(parts[1:], 1):
                if p.lower() in PAYLOAD_FLAGS:
                    return " ".join(parts[i + 1:])
        return " ".join(parts)
    return str(command or "")


_PAYLOAD = re.compile(r"(?:^|\s)(?:-lc|-cl|-ic|-c|-command|/c|/k)\s+(.*)$", re.I | re.S)
_WSL_ADMIN = re.compile(r"^\s*wsl(?:\.exe)?\s+--(?:shutdown|install|update|unregister|import|export|terminate|set-version|mount)\b", re.I)


def unwrap(text: str) -> str:
    for _ in range(4):
        m = re.match(r"\s*(\S+)", text)
        if not m or _head(m.group(1)) not in SHELLS:
            break
        if _WSL_ADMIN.match(text):
            return re.sub(r"^\s*wsl(?:\.exe)?", "wsl", text, flags=re.I)
        pm = _PAYLOAD.search(text)
        if pm:
            body = pm.group(1).strip()
            if body[:1] in ("'", '"'):
                end = body.rfind(body[0])
                body = body[1:end] + body[end + 1:] if end > 0 else body[1:]
            text = body
            continue
        if _head(m.group(1)) == "wsl":
            text = re.sub(r"^\s*\S+\s*", "", text)
            text = re.sub(r"^(?:(?:-d|--distribution|-u|--user)\s+\S+\s*|(?:-e|--exec)\s+|--\s+)+", "", text)
            continue
        break
    return text


def _segments(text: str) -> list:
    t = _HEREDOC.sub(" ", text)
    t = _HERESTR.sub(" ", t)
    t = _QUOTED.sub(" ", t)
    return [s.strip() for s in _SPLIT.split(t) if s.strip()]


def _normalize_segment(seg: str) -> str:
    seg = _ENVASSIGN.sub("", seg)
    toks = seg.split()
    while toks and _head(toks[0]) in _SKIP_PREFIX:
        toks = toks[1:]
    if not toks:
        return ""
    seg = " ".join(toks)
    first = _head(toks[0])
    if first in ("npm", "pnpm", "yarn", "bun") and len(toks) > 1:
        rest = _PKG_OPTS.sub("", " " + " ".join(toks[1:]) + " ").strip()
        seg = first + " " + rest
    else:
        seg = first + (" " + " ".join(toks[1:]) if len(toks) > 1 else "")
    return seg.lower()


def _classify_segment(seg: str) -> Optional[str]:
    if not seg or not re.search(r"[A-Za-z]", seg) or _TRIVIAL.match(seg):
        return None
    for cat, rx in _RULES:
        if rx.match(seg):
            return cat
    return "other_tool"


def classify(command: Union[str, Iterable[str], None]) -> Tuple[str, str]:
    text = unwrap(to_text(command))
    best: Optional[str] = None
    family = ""
    for raw in _segments(text):
        seg = _normalize_segment(raw)
        cat = _classify_segment(seg)
        if cat is None:
            continue
        if best is None or _RANK[cat] < _RANK[best]:
            best = cat
            fam = seg.split(" ", 1)[0]
            family = fam if fam in FAMILIES else ""
    if best is None:
        return "system_query", ""
    return best, family
