from __future__ import annotations
import ast
import re

ASSERT_NAME_RE = re.compile(r"^(assert|expect|verify|check|should)", re.I)
MUST_NOT_RAISE_RE = re.compile(
    r"(not?[_ ]raise|noop|no[_ ]op|silent|swallow|graceful|does[_ ]not[_ ]throw)", re.I)

def split_lines_keepends(text: str) -> list[str]:
    r"""Split on \n / \r\n / \r ONLY — the exact line terminators the ast
    module counts — keeping the terminator on each line. str.splitlines()
    also splits on \f, \v, \x1c-\x1e, \x85,  ,  , which ast
    does not, so indexing splitlines() output by ast line numbers corrupts
    files containing those bytes."""
    lines = []
    start = i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\n":
            lines.append(text[start:i + 1])
            i += 1
            start = i
        elif c == "\r":
            j = i + 2 if i + 1 < n and text[i + 1] == "\n" else i + 1
            lines.append(text[start:j])
            i = j
            start = i
        else:
            i += 1
    if start < n:
        lines.append(text[start:])
    return lines

def call_name(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None

def is_simple_chain(node: ast.AST) -> bool:
    """Name or dotted attribute chain — no calls, no subscripts."""
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Attribute):
        return is_simple_chain(node.value)
    return False

def const_truthiness(node: ast.AST):
    """True/False if node is a constant with known truthiness, else None."""
    if isinstance(node, ast.Constant):
        return bool(node.value)
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        l, r = node.left, node.comparators[0]
        if isinstance(l, ast.Constant) and isinstance(r, ast.Constant):
            op = node.ops[0]
            try:
                if isinstance(op, ast.Eq):
                    return l.value == r.value
                if isinstance(op, ast.Is):
                    return l.value is r.value
            except Exception:
                return None
    return None

def walk_no_nested_funcs(node: ast.AST):
    """Yield descendants without descending into nested function/class defs."""
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            yield from walk_no_nested_funcs(child)

def is_assertionish_call(node: ast.Call) -> bool:
    name = call_name(node)
    if name is None:
        return False
    if ASSERT_NAME_RE.match(name):
        return True
    if name in ("fail", "raises"):
        return True
    return False

def has_pytest_raises(node: ast.AST) -> bool:
    if isinstance(node, (ast.With, ast.AsyncWith)):
        for item in node.items:
            e = item.context_expr
            if isinstance(e, ast.Call) and call_name(e) in ("raises", "warns", "deprecated_call"):
                return True
    return False

def silent_handler(h: ast.ExceptHandler) -> bool:
    return all(isinstance(s, ast.Pass) or
               (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and
                call_name(s.value) in ("print",))
               for s in h.body)

class HelperIndex:
    """Same-file helper resolution: a test that calls _check_result(...) which
    contains asserts is NOT assertion-free. Transitive, cycle-safe."""

    def __init__(self, tree: ast.Module):
        self.defs: dict[str, ast.AST] = {}
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defs[n.name] = n
        self._memo: dict[str, bool] = {}

    def fn_asserts(self, name: str, depth: int = 0) -> bool:
        if name in self._memo:
            return self._memo[name]
        if depth > 3 or name not in self.defs:
            return False
        self._memo[name] = False  # cycle guard
        node = self.defs[name]
        result = False
        for d in walk_no_nested_funcs(node):
            if isinstance(d, ast.Assert) or has_pytest_raises(d):
                result = True
                break
            if isinstance(d, ast.Call):
                if is_assertionish_call(d):
                    result = True
                    break
                cn = call_name(d)
                if cn and cn in self.defs and self.fn_asserts(cn, depth + 1):
                    result = True
                    break
        self._memo[name] = result
        return result
