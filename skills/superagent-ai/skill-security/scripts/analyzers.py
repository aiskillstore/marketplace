"""
analyzers.py — deterministic detection engine for skill-security.

Everything here is fast, offline, and dependency-free. It runs as Stage 1
(high recall). The agent running the skill is Stage 2 (semantic judgment): it
reads findings + the actual content and decides true vs false positive, and
performs the frontmatter<->behavior contract check that static rules can only
hint at.

Finding rule_id prefixes:
  PI  prompt injection / instruction manipulation (in SKILL.md + text)
  CT  contract / tool-poisoning / trigger abuse (skill-native)
  EX  data exfiltration (scripts)
  SC  supply chain / remote code / obfuscation
  AST python dangerous calls (ast-based)
  TT  taint flows (source -> sink)
  RA  rogue / persistence / memory poisoning
  YR  yara matches (added by scan.py via yara_lite)
"""

from __future__ import annotations

import ast
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

# files we treat as "executable" (drives the 1.3x risk multiplier and AST/shell passes)
EXECUTABLE_EXTS = {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".ps1"}
TEXT_EXTS = {".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"}
# skip these entirely
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".so", ".dylib", ".pyc", ".woff", ".ttf", ".ico"}
MAX_FILE_BYTES = 2_000_000


@dataclass
class Finding:
    rule_id: str
    title: str
    category: str
    severity: str
    confidence: float
    file: str
    line: int
    evidence: str
    explanation: str = ""

    def dict(self) -> dict:
        return asdict(self)


@dataclass
class Component:
    file: str
    kind: str
    lines: int
    executable: bool


@dataclass
class ScanInput:
    root: Path
    files: list[Path] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# file discovery
# --------------------------------------------------------------------------- #
def discover(root: Path) -> ScanInput:
    root = Path(root)
    files: list[Path] = []
    if root.is_file():
        files = [root]
        root = root.parent
    else:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix.lower() in BINARY_EXTS:
                continue
            try:
                if p.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            files.append(p)
    return ScanInput(root=root, files=files)


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def classify(p: Path) -> tuple[str, bool]:
    ext = p.suffix.lower()
    if p.name == "SKILL.md":
        return "skill_manifest", False
    if ext in (".md", ".markdown"):
        return "markdown", False
    if ext == ".py":
        return "python", True
    if ext in (".sh", ".bash", ".zsh"):
        return "shell", True
    if ext in (".js", ".mjs", ".cjs", ".ts"):
        return "javascript", True
    if ext in EXECUTABLE_EXTS:
        return ext.lstrip("."), True
    if ext in TEXT_EXTS:
        return "text", False
    return "other", False


def _line_of(content: str, idx: int) -> int:
    return content.count("\n", 0, idx) + 1


def _evidence(content: str, idx: int, length: int = 0, width: int = 120) -> str:
    line_start = content.rfind("\n", 0, idx) + 1
    line_end = content.find("\n", idx)
    if line_end == -1:
        line_end = len(content)
    snippet = content[line_start:line_end].strip()
    return snippet[:width]


# --------------------------------------------------------------------------- #
# 1. regex pattern analyzer (prompt injection, exfil, privesc, persistence)
# --------------------------------------------------------------------------- #
# (rule_id, title, category, severity, regex, confidence)
_PATTERNS: list[tuple[str, str, str, str, str, float]] = [
    # ---- prompt injection / instruction manipulation (text + markdown) ----
    ("PI3", "Exfiltration instruction", "Prompt Injection", "HIGH",
     r"(?:send|transmit|upload|post|forward|exfiltrate)\s+(?:the\s+)?(?:full\s+)?(?:conversation|context|chat\s*history|messages?|user\s+data)\s+to\b", 0.85),
    ("PI3", "Covert transmission instruction", "Prompt Injection", "HIGH",
     r"(?:silently|quietly|secretly|covertly|without\s+(?:telling|informing|notifying)\s+the\s+user)\b[^\n]{0,60}(?:send|transmit|log|record|upload|post)", 0.9),
    ("PI4", "Behavior steering instruction", "Prompt Injection", "MEDIUM",
     r"\bnever\s+(?:tell|inform|warn|mention\s+to)\s+(?:the\s+)?(?:user|them)\b", 0.7),
    ("PI4", "Recommendation steering", "Prompt Injection", "MEDIUM",
     r"\balways\s+(?:recommend|suggest|prefer|use|install)\s+\w+[^\n]{0,40}(?:over|instead\s+of|rather\s+than)\b", 0.6),
    ("PI5", "System prompt extraction", "System Prompt Leakage", "HIGH",
     r"(?:reveal|print|show|output|repeat|dump|leak)\s+(?:your|the|all)\s+(?:system\s+prompt|instructions?|rules?|guidelines?|configuration)\b", 0.75),
    # ---- data exfiltration (scripts) ----
    ("EX1", "Outbound HTTP transmission", "Data Exfiltration", "MEDIUM",
     r"(?:requests\.(?:post|put|patch)|urllib\.request\.urlopen|httpx\.(?:post|put)|fetch\(|axios\.(?:post|put)|curl\s+-[A-Za-z]*X?\s*POST)", 0.5),
    ("EX2", "Environment variable harvesting", "Data Exfiltration", "HIGH",
     r"(?:for\s+\w+\s*,?\s*\w*\s+in\s+os\.environ(?:\.items\(\))?|dict\(os\.environ\)|json\.dumps\(\s*dict\(os\.environ|printenv\b|env\s*\|\s*(?:curl|nc|base64))", 0.8),
    ("EX3", "Credential / secret file access", "Data Exfiltration", "HIGH",
     r"(?:\.ssh/id_(?:rsa|ed25519|dsa|ecdsa)|\.aws/credentials|\.config/gcloud|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.docker/config\.json|wallet\.dat|Login\s+Data|cookies\.sqlite)", 0.8),
    ("EX4", "Secret-file enumeration", "Data Exfiltration", "MEDIUM",
     r"(?:glob\.glob|rglob|os\.walk|find\s+[^\n]{0,40})[^\n]{0,40}(?:\*\.(?:pem|key|env)|id_rsa|\.env|credentials)", 0.65),
    # ---- supply chain / remote code / obfuscation ----
    ("SC1", "Remote code fetch-and-execute (curl|bash)", "Supply Chain", "HIGH",
     r"(?:curl|wget)\s+[^\n|]{0,200}\|\s*(?:sudo\s+)?(?:ba)?sh\b", 0.9),
    ("SC1", "PowerShell download cradle", "Supply Chain", "HIGH",
     r"(?:iwr|Invoke-WebRequest|Net\.WebClient[^\n]{0,40}DownloadString)[^\n]{0,80}\|\s*(?:iex|Invoke-Expression)", 0.9),
    ("SC1", "eval over fetched content", "Supply Chain", "CRITICAL",
     r"(?:exec|eval)\s*\(\s*(?:requests\.get|urllib[^\n]{0,30}urlopen|httpx\.get)\s*\([^)]*\)[^\n]{0,20}\.(?:text|content|read)", 0.9),
    ("SC2", "Obfuscated decode-and-execute", "Supply Chain", "HIGH",
     r"(?:exec|eval)\s*\(\s*(?:base64\.b64decode|bytes\.fromhex|codecs\.decode|zlib\.decompress|gzip\.decompress)\s*\(", 0.85),
    # ---- privilege escalation ----
    ("EX5", "Sudo / root invocation", "Privilege Escalation", "MEDIUM",
     r"(?:^|\s)sudo\s+(?:-S\s+)?(?!--version|--help)\S", 0.5),
    # ---- rogue / persistence ----
    ("RA2", "Persistence mechanism", "Rogue Agent", "HIGH",
     r"(?:crontab\s+-|>>?\s*[^\n]{0,40}\.(?:bashrc|zshrc|profile|bash_profile)|LaunchAgents/|/etc/init\.d/|systemctl\s+enable|>>?\s*[^\n]{0,40}authorized_keys)", 0.7),
    ("RA1", "Runtime self-modification of skill files", "Rogue Agent", "HIGH",
     r"(?:open|write_text|with\s+open)\s*\([^)]*(?:SKILL\.md|__file__)[^)]*[,)]\s*(?:[\"']a[\"']|[\"']w[\"'])", 0.7),
    ("RA3", "Writes to agent memory / rules files", "Memory Poisoning", "CRITICAL",
     r"(?:>>?|open\s*\([^)]*[\"']a[\"']|write_text|append)[^\n]{0,60}(?:CLAUDE\.md|AGENTS\.md|GEMINI\.md|\.cursorrules|\.claude/(?:memory|CLAUDE\.md))", 0.8),
    # ---- excessive agency ----
    ("CT5", "Auto-approve / permission bypass flag", "Excessive Agency", "HIGH",
     r"(?:dangerously[_-]?skip[_-]?permissions|--?yes\b[^\n]{0,30}--?force|auto[_-]?approve|bypass[_-]?permissions|--no-?confirm)", 0.6),
]

_COMPILED_PATTERNS = [
    (rid, title, cat, sev, re.compile(rx, re.IGNORECASE | re.MULTILINE), conf)
    for rid, title, cat, sev, rx, conf in _PATTERNS
]

# rule_ids that only make sense in instruction/markdown content (not scripts)
_TEXT_ONLY_RULES = {"PI3", "PI4", "PI5"}
# rule_ids that only make sense in executable scripts
_CODE_ONLY_RULES = {"EX1", "EX2", "EX4", "SC2", "EX5", "RA1"}


def scan_patterns(path_str: str, kind: str, content: str) -> list[Finding]:
    out: list[Finding] = []
    is_code = kind in ("python", "shell", "javascript", "rb", "pl", "ps1")
    for rid, title, cat, sev, rx, conf in _COMPILED_PATTERNS:
        if rid in _TEXT_ONLY_RULES and is_code:
            continue
        if rid in _CODE_ONLY_RULES and not is_code:
            continue
        for m in rx.finditer(content):
            out.append(Finding(rid, title, cat, sev, conf, path_str,
                               _line_of(content, m.start()), _evidence(content, m.start())))
            if len(out) > 200:
                return out
    return out


# --------------------------------------------------------------------------- #
# 2. python AST analyzer (dangerous calls + dangerous chains)
# --------------------------------------------------------------------------- #
_DANGEROUS_BUILTINS = {"exec", "eval", "compile", "__import__"}
_OS_EXEC_FAMILY = {"system", "popen", "execl", "execle", "execlp", "execv", "execve", "execvp", "spawn", "spawnl"}


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        parts = []
        cur: ast.AST = f
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return ""


_DYNAMIC_SOURCE_HINTS = ("requests.", "urllib", "httpx", "socket", "subprocess.", "os.", "b64decode", "fromhex", "decompress")


def _chain_has_dynamic_source(node: ast.AST) -> str | None:
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            if any(h in name for h in _DYNAMIC_SOURCE_HINTS):
                return name
    return None


def scan_python_ast(path_str: str, content: str) -> list[Finding]:
    out: list[Finding] = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return out  # not valid python (could be a template); skip AST, regex still runs

    def emit(rid, title, sev, conf, line, ev):
        out.append(Finding(rid, title, "Dangerous Code", sev, conf, path_str, line, ev))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        line = getattr(node, "lineno", 1)
        ev = _evidence(content, _offset_of_line(content, line))
        if name in ("exec", "eval"):
            src = _chain_has_dynamic_source(node)
            if src:
                emit("AST8", f"Dangerous execution chain: {name}() over {src}", "CRITICAL", 0.9, line, ev)
            else:
                emit("AST1" if name == "exec" else "AST2", f"{name}() call", "HIGH", 0.75, line, ev)
        elif name == "compile":
            emit("AST6", "compile() call", "MEDIUM", 0.5, line, ev)
        elif name == "__import__":
            emit("AST3", "Dynamic __import__()", "HIGH", 0.6, line, ev)
        elif name.startswith("subprocess."):
            shell_true = any(
                isinstance(kw, ast.keyword) and kw.arg == "shell"
                and isinstance(kw.value, ast.Constant) and kw.value.value is True
                for kw in node.keywords
            )
            if shell_true:
                emit("AST4", "subprocess call with shell=True", "HIGH", 0.7, line, ev)
            else:
                emit("AST4", "subprocess call", "MEDIUM", 0.5, line, ev)
        elif name.startswith("os.") and name.split(".")[-1] in _OS_EXEC_FAMILY:
            emit("AST5", f"{name}() shell/exec call", "HIGH", 0.7, line, ev)
        elif name == "getattr" and len(node.args) >= 2 and not isinstance(node.args[1], ast.Constant):
            emit("AST7", "Dynamic getattr() with non-literal name", "MEDIUM", 0.5, line, ev)
    return out


def _offset_of_line(content: str, line: int) -> int:
    pos = 0
    for _ in range(line - 1):
        nxt = content.find("\n", pos)
        if nxt == -1:
            return pos
        pos = nxt + 1
    return pos


# --------------------------------------------------------------------------- #
# 3. taint tracking (intra-procedural, python) — source -> sink
# --------------------------------------------------------------------------- #
_SOURCE_PATTERNS = {
    "env": re.compile(r"os\.environ|getenv|os\.getenv"),
    "file": re.compile(r"\.read\(\)|open\([^)]*\)\.read|read_text|read_bytes"),
    "net_in": re.compile(r"requests\.get|urlopen|recv\(|input\(|\.json\(\)"),
}
_SINK_PATTERNS = {
    "net_out": re.compile(r"requests\.(post|put|patch)|urlopen\([^)]*data|httpx\.(post|put)|\.send\(|socket"),
    "exec": re.compile(r"\bexec\(|\beval\(|os\.system|subprocess|popen"),
    "file_write": re.compile(r"open\([^)]*['\"][aw]['\"]|write_text|write_bytes"),
}
_SECRET_NAME = re.compile(r"(?:key|token|secret|password|passwd|credential|cookie|session|env)", re.IGNORECASE)


class _TaintVisitor(ast.NodeVisitor):
    """Track variables assigned from sources, then flag when they reach a sink."""

    def __init__(self, content: str, path_str: str):
        self.content = content
        self.path = path_str
        self.tainted: dict[str, str] = {}  # var -> source kind
        self.findings: list[Finding] = []

    def _src_kind(self, node: ast.AST) -> str | None:
        try:
            seg = ast.get_source_segment(self.content, node) or ""
        except Exception:  # noqa: BLE001
            seg = ""
        for kind, rx in _SOURCE_PATTERNS.items():
            if rx.search(seg):
                return kind
        return None

    def visit_Assign(self, node: ast.Assign) -> None:
        kind = self._src_kind(node.value)
        if kind:
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    self.tainted[tgt.id] = kind
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        try:
            seg = ast.get_source_segment(self.content, node) or ""
        except Exception:  # noqa: BLE001
            seg = ""
        line = getattr(node, "lineno", 1)
        ev = _evidence(self.content, _offset_of_line(self.content, line))

        sink = None
        for sk, rx in _SINK_PATTERNS.items():
            if rx.search(seg):
                sink = sk
                break
        if sink:
            # direct: source expression appears inside the same sink call
            direct_src = self._src_kind(node)
            # variable-mediated: a tainted var name appears in the call args
            used_taint = None
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and child.id in self.tainted:
                    used_taint = self.tainted[child.id]
                    break
            src_kind = direct_src or used_taint
            has_secret = bool(_SECRET_NAME.search(seg))
            if src_kind == "env" and sink == "net_out":
                self.findings.append(Finding("TT1", "Credential/env flows to network sink", "Data Exfiltration", "CRITICAL", 0.85, self.path, line, ev))
            elif has_secret and sink == "net_out":
                self.findings.append(Finding("TT1", "Secret value flows to network sink", "Data Exfiltration", "CRITICAL", 0.8, self.path, line, ev))
            elif src_kind == "file" and sink == "net_out":
                self.findings.append(Finding("TT2", "File contents flow to network sink", "Data Exfiltration", "HIGH", 0.75, self.path, line, ev))
            elif src_kind == "net_in" and sink == "exec":
                self.findings.append(Finding("TT3", "External input flows to code-execution sink", "Privilege Escalation", "CRITICAL", 0.85, self.path, line, ev))
        self.generic_visit(node)


def scan_taint(path_str: str, content: str) -> list[Finding]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    v = _TaintVisitor(content, path_str)
    v.visit(tree)
    # dedupe by (rule_id, line)
    seen = set()
    uniq = []
    for f in v.findings:
        key = (f.rule_id, f.line)
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


# --------------------------------------------------------------------------- #
# 4. shell + javascript heuristics (regex-based; no AST in stdlib for these)
# --------------------------------------------------------------------------- #
_SHELL_JS_PATTERNS: list[tuple[str, str, str, str, float]] = [
    ("AST4", "Node child_process exec", "HIGH",
     r"(?:child_process|require\(['\"]child_process['\"]\))[^\n]{0,40}\.(?:exec|execSync|spawn)\(", 0.6),
    ("AST2", "JavaScript eval()", "HIGH", r"\beval\s*\(", 0.6),
    ("AST2", "JS Function constructor", "MEDIUM", r"new\s+Function\s*\(", 0.55),
    ("EX1", "Node outbound request", "MEDIUM", r"(?:fetch|axios\.(?:post|put)|https?\.request)\(", 0.45),
    ("AST5", "Shell command substitution of remote", "HIGH",
     r"\$\((?:curl|wget)\b[^)]*\)", 0.7),
]
_COMPILED_SHELL_JS = [(rid, t, s, re.compile(rx, re.IGNORECASE), c) for rid, t, s, rx, c in _SHELL_JS_PATTERNS]


def scan_shell_js(path_str: str, content: str) -> list[Finding]:
    out: list[Finding] = []
    for rid, title, sev, rx, conf in _COMPILED_SHELL_JS:
        for m in rx.finditer(content):
            out.append(Finding(rid, title, "Dangerous Code", sev, conf, path_str,
                               _line_of(content, m.start()), _evidence(content, m.start())))
    return out


# --------------------------------------------------------------------------- #
# 5. frontmatter / contract / unicode / trigger abuse (skill-native)
# --------------------------------------------------------------------------- #
_ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad", "\u034f"}
_RTL_OVERRIDE = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069"}
_OVERBROAD_TRIGGERS = re.compile(
    r"\b(?:always|whenever\s+possible|for\s+(?:every|all|any)\s+(?:task|request|query|message)|in\s+all\s+cases|no\s+matter\s+what)\b",
    re.IGNORECASE,
)


def _script_of(ch: str) -> str:
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return ""
    for s in ("LATIN", "CYRILLIC", "GREEK", "ARMENIAN", "HEBREW", "ARABIC", "CJK"):
        if s in name:
            return s
    return ""


def _mixed_script(word: str) -> bool:
    scripts = {s for ch in word if (s := _script_of(ch))}
    return len(scripts) > 1


def parse_frontmatter(content: str) -> tuple[dict, str, int]:
    """Return (frontmatter_dict, body, body_start_line). Minimal YAML — flat keys only."""
    if not content.startswith("---"):
        return {}, content, 1
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content, 1
    fm_block = content[3:end].strip("\n")
    body_start = content.find("\n", end + 4)
    body = content[body_start + 1 :] if body_start != -1 else ""
    body_start_line = content.count("\n", 0, body_start) + 2 if body_start != -1 else 1
    fm: dict[str, str] = {}
    cur_key = None
    for line in fm_block.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            cur_key = m.group(1)
            fm[cur_key] = m.group(2).strip().strip("'\"")
        elif cur_key and line.strip():
            fm[cur_key] = (fm.get(cur_key, "") + " " + line.strip()).strip()
    return fm, body, body_start_line


def scan_frontmatter(path_str: str, content: str) -> list[Finding]:
    out: list[Finding] = []
    fm, body, _ = parse_frontmatter(content)

    # CT2 — unicode deception anywhere in the manifest
    for i, ch in enumerate(content):
        if ch in _ZERO_WIDTH:
            out.append(Finding("CT2", "Zero-width / invisible character in skill content",
                              "Tool Poisoning", "HIGH", 0.7, path_str, _line_of(content, i),
                              f"U+{ord(ch):04X} at offset {i}"))
            break
    for i, ch in enumerate(content):
        if ch in _RTL_OVERRIDE:
            out.append(Finding("CT2", "Bidirectional/RTL override character (text-spoofing)",
                              "Tool Poisoning", "HIGH", 0.8, path_str, _line_of(content, i),
                              f"U+{ord(ch):04X} at offset {i}"))
            break
    # homoglyph check on name/description
    for fld in ("name", "description"):
        val = fm.get(fld, "")
        for word in re.findall(r"\S+", val):
            if _mixed_script(word):
                out.append(Finding("CT2", f"Mixed-script (homoglyph) token in {fld}: {word!r}",
                                  "Tool Poisoning", "HIGH", 0.75, path_str, 1, word[:80]))
                break

    # CT3 — trigger abuse in the description
    desc = fm.get("description", "")
    for m in _OVERBROAD_TRIGGERS.finditer(desc):
        out.append(Finding("CT3", "Overly broad trigger in description",
                          "Trigger Abuse", "MEDIUM", 0.5, path_str, 1, m.group(0)))
        break

    # CT4 — over-broad allowed-tools / permissions
    tools = fm.get("allowed-tools", "") or fm.get("allowed_tools", "")
    perms = fm.get("permissions", "")
    combined = f"{tools} {perms}".strip()
    if combined and re.search(r"""(?:^|[\s,\[\"'])(?:\*|all|any)(?:$|[\s,\]\"'])|Bash\(\*\)""", combined, re.IGNORECASE):
        out.append(Finding("CT4", "Wildcard / unrestricted permissions declared",
                          "Excessive Agency", "MEDIUM", 0.6, path_str, 1, combined[:80]))

    # PI2 — hidden HTML comment instructions in the body
    for m in re.finditer(r"<!--(.*?)-->", body, re.DOTALL):
        inner = m.group(1)
        if re.search(r"(?:ignore|instruction|system|exfiltrat|send|POST|secret|api[_-]?key|password)", inner, re.IGNORECASE):
            out.append(Finding("PI2", "Hidden instruction in HTML comment",
                              "Prompt Injection", "HIGH", 0.7, path_str,
                              _line_of(body, m.start()), inner.strip()[:100]))
            break
    return out


# --------------------------------------------------------------------------- #
# 6. supply-chain dependency analysis (unpinned, typosquat)
# --------------------------------------------------------------------------- #
_TOP_PACKAGES = {
    "requests", "numpy", "pandas", "flask", "django", "boto3", "urllib3", "pyyaml",
    "click", "pytest", "scipy", "pillow", "cryptography", "lodash", "express",
    "react", "axios", "chalk", "commander", "dotenv", "openai", "anthropic",
}


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def scan_dependencies(path_str: str, name: str, content: str) -> list[Finding]:
    out: list[Finding] = []
    pkgs: list[tuple[str, str, int]] = []  # (pkg, raw, line)
    if name in ("requirements.txt", "requirements.in"):
        for i, line in enumerate(content.splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            pkg = re.split(r"[<>=!~\[ ]", s, 1)[0].strip().lower()
            pinned = "==" in s
            pkgs.append((pkg, s, i))
            if not pinned and pkg:
                out.append(Finding("SC3", f"Unpinned dependency: {pkg}", "Supply Chain", "LOW", 0.5, path_str, i, s[:80]))
    elif name == "package.json":
        for m in re.finditer(r'"([^"]+)"\s*:\s*"([\^~]?[\dvx*][^"]*|\*|latest)"', content):
            pkg, ver = m.group(1), m.group(2)
            line = _line_of(content, m.start())
            pkgs.append((pkg.lower(), f"{pkg}: {ver}", line))
            if ver in ("*", "latest") or ver.startswith(("^", "~")):
                out.append(Finding("SC3", f"Unpinned dependency: {pkg} ({ver})", "Supply Chain", "LOW", 0.45, path_str, line, f"{pkg}: {ver}"))

    for pkg, raw, line in pkgs:
        for top in _TOP_PACKAGES:
            d = _levenshtein(pkg, top)
            if 0 < d <= 1 and len(pkg) >= 4:
                out.append(Finding("SC4", f"Possible typosquat of '{top}': '{pkg}'", "Supply Chain", "HIGH", 0.6, path_str, line, raw[:80]))
                break
    return out
