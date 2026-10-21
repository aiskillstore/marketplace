from __future__ import annotations
import ast
import os
import re

from .models import Finding, Probe, TestRecord
from .ast_utils import (
    call_name,
    is_simple_chain,
    const_truthiness,
    walk_no_nested_funcs,
    is_assertionish_call,
    has_pytest_raises,
    silent_handler,
    split_lines_keepends,
    HelperIndex,
    MUST_NOT_RAISE_RE,
    ASSERT_NAME_RE,
)

def _is_noise_call(node: ast.Call) -> bool:
    """print()/logging.* — never meaningful coverage, so they don't count as
    executable remnants keeping an otherwise-inert test alive."""
    curr = node.func
    while True:
        if isinstance(curr, ast.Attribute):
            if curr.attr in ("logging", "log", "logger"):
                return True
            curr = curr.value
        elif isinstance(curr, ast.Call):
            curr = curr.func
        elif isinstance(curr, ast.Name):
            return curr.id in ("print", "logging", "log", "logger")
        else:
            break
    return False


_UNITTEST_EQ = {"assertEqual", "assertIs"}
_UNITTEST_TRUE = {"assertTrue"}
_UNITTEST_ISINSTANCE = {"assertIsInstance"}
_UNITTEST_NONE = {"assertIsNone", "assertIsNotNone"}

def _unittest_call_to_assert(call: ast.Call, ts: ast.AST | None = None) -> ast.Assert | None:
    """Map self.assert<X>(...) to an equivalent synthetic ast.Assert whose
    .test mirrors the bare-assert form, so classify_assert and the mypy
    probe queue can reason about it. Returns None for unrecognized shapes.
    The synthetic node copies the call's location so findings and probes
    point at the real line. A msg= extra positional/keyword arg trips the
    len(args) checks and simply skips the call — acceptable conservatism."""
    if not (isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "self"):
        return None
    name = call.func.attr
    args = call.args
    t = None
    if name in _UNITTEST_EQ and len(args) == 2:
        t = ast.Compare(left=args[0],
                        ops=[ast.Eq() if name == "assertEqual" else ast.Is()],
                        comparators=[args[1]])
    elif name in _UNITTEST_TRUE and len(args) == 1:
        t = args[0]
    elif name in _UNITTEST_ISINSTANCE and len(args) == 2:
        t = ast.Call(func=ast.Name(id="isinstance", ctx=ast.Load()),
                     args=[args[0], args[1]], keywords=[])
    elif name in _UNITTEST_NONE and len(args) == 1:
        cmp_op = ast.Is() if name == "assertIsNone" else ast.IsNot()
        t = ast.Compare(left=args[0], ops=[cmp_op],
                        comparators=[ast.Constant(value=None)])
    if t is None:
        return None
    a = ast.Assert(test=t, msg=None)
    a._orig_stmt = ts or call
    for n in ast.walk(a):
        ast.copy_location(n, call)
    ast.copy_location(a, call)
    a.end_lineno = call.end_lineno
    return a


def analyze_file(path: str, src: str, tree: ast.Module, root: str,
                 probes: list[Probe], records: list[TestRecord]):
    helpers = HelperIndex(tree)
    lines = src.splitlines()

    def fn_has_cast(fn) -> bool:
        """cast()/type:ignore inside THIS test mean its types may lie — but a
        stray `# type: ignore` elsewhere in the file shouldn't kill all probes."""
        seg = ast.get_source_segment(src, fn) or ""
        return "cast(" in seg or "type: ignore" in seg

    def is_fixture(fn) -> bool:
        for dec in fn.decorator_list:
            func = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "pytest" and func.attr == "fixture":
                return True
            if isinstance(func, ast.Name) and func.id == "fixture":
                return True
        return False

    def tests_in(container, scope_key, class_name=None):
        for n in container:
            if isinstance(n, ast.ClassDef) and n.name.startswith("Test"):
                tests_in(n.body, f"{scope_key}::{n.name}", n.name)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"):
                if not is_fixture(n):
                    analyze_test(n, scope_key, class_name)

    def analyze_test(fn, scope_key, class_name):
        rec = TestRecord(path, fn, fn.name, scope_key)
        records.append(rec)
        body = fn.body

        # unconditionally-skipped test (@pytest.mark.skip / @unittest.skip):
        # it never runs, so it can never fail. Advisory — skips sometimes
        # document future work. skipif is conditional and stays untouched.
        for dec in fn.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Attribute) and target.attr == "skip":
                rec.findings.append(Finding(
                    path, fn.lineno, fn.name, "skipped-test", "advisory", "aggressive",
                    "test is unconditionally skipped — it never runs and can never fail"))
                return

        # skip parametrized-over-everything? no — parametrize is fine, analyze body

        # -- reachability at top level
        unreachable: set[int] = set()
        dead = False
        for s in body:
            if dead:
                unreachable.add(id(s))
            if isinstance(s, (ast.Return, ast.Raise)):
                dead = True

        def top_stmt_of(node):
            for s in body:
                if s is node:
                    return s
                for d in ast.walk(s):
                    if d is node:
                        return s
            return None

        # -- swallowed: asserts inside try: with a silent except — cannot fail
        swallowed_ids: set[int] = set()
        # Everything lexically inside a try: whose handlers are all silent. If
        # it raises, the handler absorbs it, so it can never fail the test and
        # therefore never counts as coverage worth preserving.
        silently_guarded: set[int] = set()
        for d in walk_no_nested_funcs(fn):
            if isinstance(d, ast.Try) and d.handlers and all(silent_handler(h) for h in d.handlers):
                for x in ast.walk(d):
                    silently_guarded.add(id(x))
                for x in ast.walk(ast.Module(body=d.body, type_ignores=[])):
                    if isinstance(x, ast.Assert) or (isinstance(x, ast.Call) and is_assertionish_call(x)):
                        swallowed_ids.add(id(x))

        # -- collect assertion-ish nodes (not descending into nested defs)
        assert_nodes: list[ast.AST] = []
        for d in walk_no_nested_funcs(fn):
            if isinstance(d, ast.Assert) or has_pytest_raises(d):
                assert_nodes.append(d)
            elif isinstance(d, ast.Raise):
                exc = d.exc
                exc_name = None
                if isinstance(exc, ast.Call):
                    exc_name = call_name(exc)
                elif isinstance(exc, ast.Name):
                    exc_name = exc.id
                if exc_name in ("AssertionError", "Exception", "BaseException"):
                    assert_nodes.append(d)
            elif isinstance(d, ast.Call):
                cn = call_name(d)
                if cn is None:
                    continue
                if isinstance(d.func, ast.Attribute) and cn.startswith("assert"):
                    assert_nodes.append(d)          # self.assertX / mock.assert_called*
                elif ASSERT_NAME_RE.match(cn) or cn == "fail":
                    assert_nodes.append(d)
                elif cn in helpers.defs and helpers.fn_asserts(cn):
                    assert_nodes.append(d)          # local helper that asserts
                    rec.helper_asserts += 1

        live = []
        for a in assert_nodes:
            if id(a) in swallowed_ids:
                rec.findings.append(Finding(
                    path, a.lineno, fn.name, "swallowed-assert", "proven", "report-only",
                    f"assertion at line {a.lineno} sits in try: with a silent except — a failure is swallowed"))
                continue
            ts = top_stmt_of(a)
            if ts is not None and id(ts) in unreachable:
                is_fail_marker = False
                if isinstance(a, ast.Call):
                    cn = call_name(a)
                    if cn == "fail" or (isinstance(a.func, ast.Attribute) and a.func.attr == "fail"):
                        is_fail_marker = True
                elif isinstance(a, ast.Raise):
                    is_fail_marker = True

                if is_fail_marker:
                    rec.findings.append(Finding(
                        path, a.lineno, fn.name, "missed-fail", "proven", "report-only",
                        f"fail marker at line {a.lineno} sits after an unconditional return/raise — it can never fire"))
                    continue

                if isinstance(a, ast.Assert) and ts is a:
                    rec.findings.append(Finding(
                        path, a.lineno, fn.name, "dead-assert", "proven", "safe",
                        "sits after an unconditional return/raise — never executes", node=a))
                continue
            live.append(a)

        # -- no-assert / never-asserts / silent-smoke
        doc = ast.get_docstring(fn) or ""
        contract_like = bool(MUST_NOT_RAISE_RE.search(fn.name) or MUST_NOT_RAISE_RE.search(doc))
        if not assert_nodes:
            calls = [d for d in walk_no_nested_funcs(fn) if isinstance(d, ast.Call) and not _is_noise_call(d)]
            if calls and all(id(c) in silently_guarded for c in calls):
                rec.findings.append(Finding(
                    path, fn.lineno, fn.name, "silent-smoke", "proven", "safe",
                    "assertion-free test where every call is wrapped in a try/except with a silent catch — the test can never fail"))
            elif not calls:
                rec.findings.append(Finding(
                    path, fn.lineno, fn.name, "silent-smoke", "proven", "safe",
                    "assertion-free test containing no calls — the test does nothing and can never fail"))
            else:
                if contract_like:
                    rec.findings.append(Finding(
                        path, fn.lineno, fn.name, "no-assert", "advisory", "report-only",
                        "no assertion, but the name/docstring suggests a deliberate must-not-raise contract test — review by hand"))
                else:
                    rec.findings.append(Finding(
                        path, fn.lineno, fn.name, "no-assert", "advisory", "report-only",
                        "assertion-free smoke test — legitimate by design (it checks the code runs "
                        "without raising). ICSE'19 distinguishes smoke tests from rotten tests; only "
                        "worth a look if an assertion was clearly intended here"))
            return
        if not live:
            # Every assertion is dead or swallowed, so the assertions can't
            # fail the test — but an UNGUARDED call still can, by raising.
            # Deleting the test would drop that signal. A call inside a
            # silently-caught try: is not such a signal (the handler absorbs
            # the raise), so it doesn't count; nor does the assertion
            # machinery itself, nor print/logging.
            assert_ids = {id(a) for a in assert_nodes}
            def is_remnant(d):
                if not isinstance(d, ast.Call):
                    return False
                if id(d) in assert_ids:
                    return False
                if id(d) in silently_guarded:
                    return False
                if _is_noise_call(d):
                    return False
                ts = top_stmt_of(d)
                if ts is not None and id(ts) in unreachable:
                    return False
                return True
            remnant = any(is_remnant(d) for d in walk_no_nested_funcs(fn))
            if remnant:
                rec.findings.append(Finding(
                    path, fn.lineno, fn.name, "never-asserts", "advisory", "report-only",
                    "every assertion is dead or swallowed, but an unguarded call remains that "
                    "can still fail this test by raising — deleting it would drop that signal. "
                    "Repair the assertion, or delete by hand once you have confirmed the call "
                    "cannot fail"))
            else:
                rec.findings.append(Finding(
                    path, fn.lineno, fn.name, "never-asserts", "proven", "safe",
                    "every assertion is unreachable or swallowed — the test can never fail"))
            return

        # -- conditional (rotten green): a live assert that may never execute
        # because a guard is never true. To keep this signal clean we flag ONLY
        # the classic vacuous-pass shape and deliberately exclude two common,
        # legitimate patterns that otherwise drown it:
        #   * loop-nested asserts (`for x in items: if ...: assert`) — ordinary
        #     data-driven dispatch, not a rotten green test;
        #   * asserts guarded by a parametrized argument (`if mode: ... else: ...`
        #     where `mode` is a @pytest.mark.parametrize / fixture parameter) —
        #     every branch is exercised across the parametrization.
        param_names: set[str] = set()
        _a = fn.args
        for grp in (_a.posonlyargs, _a.args, _a.kwonlyargs):
            for arg in grp:
                param_names.add(arg.arg)
        if _a.vararg:
            param_names.add(_a.vararg.arg)
        if _a.kwarg:
            param_names.add(_a.kwarg.arg)

        loop_gated_asserts: set[int] = set()
        for d in walk_no_nested_funcs(fn):
            if isinstance(d, (ast.For, ast.AsyncFor, ast.While)):
                for x in ast.walk(d):
                    if isinstance(x, ast.Assert):
                        loop_gated_asserts.add(id(x))

        plain_live_asserts = []
        unittest_asserts = []
        for a in live:
            gated = False
            ts = top_stmt_of(a)
            if ts is not None and ts is not a and id(a) not in loop_gated_asserts:
                for d in [ts, *walk_no_nested_funcs(ts)]:
                    if isinstance(d, ast.If) and any(x is a for x in ast.walk(d)):
                        # skip guards keyed on a test parameter — parametrization
                        # runs every branch, so the assert is not really optional
                        cond_names = {n.id for n in ast.walk(d.test) if isinstance(n, ast.Name)}
                        if cond_names & param_names:
                            break
                        gated = True
                        break
            if gated:
                rec.conditional += 1
                rec.findings.append(Finding(
                    path, a.lineno, fn.name, "conditional-assert", "advisory", "report-only",
                    f"assertion at line {a.lineno} is gated behind an if — it may never execute (rotten green)"))
            elif isinstance(a, ast.Assert) and ts is a:
                plain_live_asserts.append(a)
            else:
                synth = None
                if isinstance(a, ast.Call) and ts is not None \
                        and isinstance(ts, ast.Expr) and ts.value is a:
                    synth = _unittest_call_to_assert(a, ts)
                if synth is not None:
                    unittest_asserts.append(synth)
                else:
                    rec.nonredundant += 1  # helper call, with-raises, etc.

        rec.live_assert_count = len(plain_live_asserts) + len(unittest_asserts)

        # -- try-except without fail (missed-fail)
        for d in walk_no_nested_funcs(fn):
            if isinstance(d, ast.Try) and d.handlers:
                except_has_assert = False
                for h in d.handlers:
                    for x in ast.walk(ast.Module(body=h.body, type_ignores=[])):
                        if isinstance(x, ast.Assert) or (isinstance(x, ast.Call) and is_assertionish_call(x)):
                            except_has_assert = True
                            break
                if except_has_assert:
                    try_has_fail = False
                    for x in ast.walk(ast.Module(body=d.body, type_ignores=[])):
                        if isinstance(x, ast.Call):
                            cn = call_name(x)
                            if cn == "fail" or (isinstance(x.func, ast.Attribute) and x.func.attr == "fail"):
                                try_has_fail = True
                                break
                        elif isinstance(x, ast.Raise):
                            try_has_fail = True
                            break
                    if not try_has_fail:
                        rec.findings.append(Finding(
                            path, d.lineno, fn.name, "missed-fail", "advisory", "report-only",
                            f"try block at line {d.lineno} catches an exception and asserts on it, but lacks a forced fail (e.g. pytest.fail) at the end of the try block — if no exception is thrown, the test will pass silently"))

        # -- missed-skip (conditional early return/skip preceding assertions)
        for i, s in enumerate(body):
            if isinstance(s, ast.If):
                has_early_exit = False
                for x in ast.walk(s):
                    if isinstance(x, ast.Return):
                        has_early_exit = True
                        break
                    elif isinstance(x, ast.Call):
                        cn = call_name(x)
                        if cn == "skip" or (isinstance(x.func, ast.Attribute) and x.func.attr == "skip"):
                            has_early_exit = True
                            break
                if has_early_exit:
                    assertions_after = False
                    for post_s in body[i+1:]:
                        for x in ast.walk(post_s):
                            if isinstance(x, ast.Assert) or (isinstance(x, ast.Call) and is_assertionish_call(x)):
                                assertions_after = True
                                break
                        if assertions_after:
                            break
                    if assertions_after:
                        cond_names = {n.id for n in ast.walk(s.test) if isinstance(n, ast.Name)}
                        if not (cond_names & param_names):
                            rec.findings.append(Finding(
                                path, s.lineno, fn.name, "missed-skip", "advisory", "report-only",
                                f"conditional early return/skip at line {s.lineno} precedes assertions — if the condition is met, the remaining assertions never run (a bare return passes silently; pytest.skip at least reports a skip)"))

        # -- mock stubs in this test: `m.return_value = V`, plus which names are
        #    bare mocks created in-test (m = MagicMock()) — asserting on a direct
        #    call of those provably tests the mock library, not project code
        stubs = {}       # mock name -> ast.dump of V
        bare_mocks = set()
        for s in body:
            if isinstance(s, ast.Assign) and len(s.targets) == 1:
                t = s.targets[0]
                if isinstance(t, ast.Attribute) and t.attr in ("return_value", "side_effect") \
                        and isinstance(t.value, (ast.Name, ast.Attribute)):
                    base = t.value.id if isinstance(t.value, ast.Name) else t.value.attr
                    stubs[base] = ast.dump(s.value)
                elif isinstance(t, ast.Name) and isinstance(s.value, ast.Call):
                    ctor = call_name(s.value)
                    if ctor in ("MagicMock", "Mock", "AsyncMock"):
                        bare_mocks.add(t.id)

        # -- literal locals for local-const-echo: x = 5 (and never rebound)
        # Walk the FULL subtree (including nested functions): a closure can mutate
        # a captured variable via `nonlocal`/`global` (e.g. a call-counter
        # `count = 0; def cb(): nonlocal count; count += 1; ... assert count == 0`),
        # in which case `assert count == <literal>` is real behavioural coverage,
        # not a self-referential arrangement. Counting only top-level assignments
        # would wrongly treat such a counter as an immutable literal.
        assign_counts: dict[str, int] = {}
        const_map: dict[str, object] = {}
        for d in ast.walk(fn):
            targets = []
            if isinstance(d, ast.Assign):
                targets = d.targets
            elif isinstance(d, (ast.AugAssign, ast.AnnAssign)) and d.target is not None:
                targets = [d.target]
            elif isinstance(d, (ast.For, ast.AsyncFor)):
                targets = [d.target]
            elif isinstance(d, ast.NamedExpr):
                targets = [d.target]
            elif isinstance(d, (ast.Global, ast.Nonlocal)):
                # a name rebindable from a nested/other scope is never a fixed literal
                for nm in d.names:
                    assign_counts[nm] = assign_counts.get(nm, 0) + 2
                continue
            elif isinstance(d, (ast.With, ast.AsyncWith)):
                targets = [it.optional_vars for it in d.items if it.optional_vars is not None]
            for t in targets:
                for n in ast.walk(t):
                    if isinstance(n, ast.Name):
                        assign_counts[n.id] = assign_counts.get(n.id, 0) + 1
        for s in body:
            if isinstance(s, ast.Assign) and len(s.targets) == 1 \
                    and isinstance(s.targets[0], ast.Name) and isinstance(s.value, ast.Constant) \
                    and assign_counts.get(s.targets[0].id, 0) == 1:
                const_map[s.targets[0].id] = s.value.value

        # -- broad-raises: `with pytest.raises(Exception)` as the only check
        if rec.nonredundant + len(plain_live_asserts) <= 1:
            for d in walk_no_nested_funcs(fn):
                if isinstance(d, (ast.With, ast.AsyncWith)):
                    for item in d.items:
                        e = item.context_expr
                        if isinstance(e, ast.Call) and call_name(e) == "raises" and e.args:
                            a0 = e.args[0]
                            nm = a0.id if isinstance(a0, ast.Name) else getattr(a0, "attr", None)
                            if nm in ("Exception", "BaseException"):
                                rec.findings.append(Finding(
                                    path, d.lineno, fn.name, "broad-raises", "advisory", "report-only",
                                    "pytest.raises(Exception) is the only check — it passes on ANY bug that raises; "
                                    "narrow the exception type or assert on the message"))

        # -- classify each plain live `assert`
        for a in plain_live_asserts:
            f = classify_assert(a, fn, stubs, fn_has_cast(fn), const_map, bare_mocks, path, probes)
            if f is None:
                rec.nonredundant += 1
            elif f == "QUEUED":
                pass  # a mypy probe will resolve this one (or count it nonredundant)
            else:
                rec.findings.append(f)

        # -- classify recognized unittest assert-methods
        for a in unittest_asserts:
            # throwaway probe list ([], NOT the real `probes`): this stage does
            # not queue mypy probes for unittest asserts, so assertIsInstance/
            # assertIsNotNone produce no finding here — see plan 009's Decision.
            f = classify_assert(a, fn, stubs, fn_has_cast(fn), const_map,
                                bare_mocks, path, [])
            if f is None or f == "QUEUED":
                # f is None → genuinely nonredundant. "QUEUED" → a probe was
                # appended to the throwaway list and can never resolve, so it
                # is nonredundant too.
                rec.nonredundant += 1
            else:
                rec.findings.append(f)

    tests_in(tree.body, os.path.relpath(path, root))
    return records


def classify_assert(a: ast.Assert, fn, stubs, file_has_cast, const_map=None,
                    bare_mocks=None, path=None, probes=None) -> Finding | None | str:
    t = a.test
    const_map = const_map or {}
    bare_mocks = bare_mocks or set()
    probes = probes if probes is not None else []

    # constant-assert
    truth = const_truthiness(t)
    if truth is True:
        return Finding(path, a.lineno, fn.name, "constant-assert", "proven", "safe",
                       f"`assert {ast.unparse(t)}` is a constant truth — can never fail", node=a)

    # boundary-tautology: len(x) >= 0 / len(x) > -1
    if isinstance(t, ast.Compare) and len(t.ops) == 1 \
            and isinstance(t.left, ast.Call) and call_name(t.left) == "len" \
            and isinstance(t.comparators[0], ast.Constant):
        v = t.comparators[0].value
        if (isinstance(t.ops[0], ast.GtE) and v == 0) or (isinstance(t.ops[0], ast.Gt) and v == -1):
            return Finding(path, a.lineno, fn.name, "boundary-tautology", "proven", "safe",
                           "len() can never be negative — the comparison always holds", node=a)

    # local-const-echo: x = 5; ... assert x == 5
    if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], (ast.Eq, ast.Is)):
        l, r = t.left, t.comparators[0]
        for name_side, lit_side in ((l, r), (r, l)):
            if isinstance(name_side, ast.Name) and name_side.id in const_map \
                    and isinstance(lit_side, ast.Constant) \
                    and const_map[name_side.id] == lit_side.value \
                    and type(const_map[name_side.id]) is type(lit_side.value):
                return Finding(path, a.lineno, fn.name, "local-const-echo", "proven", "safe",
                               f"{name_side.id} is bound to the literal {lit_side.value!r} in this test and never "
                               "reassigned — the test asserts its own arrangement", node=a)

    # self-compare-call: assert f(a) == f(a)
    # (skipped when the test name says it's a deliberate determinism check)
    if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], (ast.Eq, ast.Is)) \
            and not is_simple_chain(t.left) and ast.dump(t.left) == ast.dump(t.comparators[0]) \
            and any(isinstance(n, ast.Call) for n in ast.walk(t.left)) \
            and not re.search(r"stable|determin|consistent|idempotent|same|pure", fn.name, re.I):
        return Finding(path, a.lineno, fn.name, "self-compare-call", "advisory", "report-only",
                       f"compares `{ast.unparse(t.left)[:60]}` to an identical expression — equal by "
                       "construction unless nondeterministic", node=a)
    if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], (ast.Eq, ast.Is)):
        l, r = t.left, t.comparators[0]
        if is_simple_chain(l) and ast.dump(l) == ast.dump(r):
            return Finding(path, a.lineno, fn.name, "constant-assert", "proven", "safe",
                           f"compares {ast.unparse(l)} to itself", node=a)
        # mock-echo (proven): assert m() == V where m is a bare in-test mock
        # stubbed with V — this can only test the mock library itself
        for call_side, val_side in ((l, r), (r, l)):
            if isinstance(call_side, ast.Call) and isinstance(call_side.func, ast.Name) \
                    and call_side.func.id in bare_mocks \
                    and stubs.get(call_side.func.id) == ast.dump(val_side):
                return Finding(path, a.lineno, fn.name, "mock-echo", "proven", "safe",
                               f"{call_side.func.id} is a bare mock created in this test and stubbed with "
                               "this exact value — the assertion tests the mock library", node=a)
        # mock-echo (advisory): the asserted value matches a stubbed return_value
        # but flows through other code — might still test real pass-through logic
        for side in (l, r):
            if ast.dump(side) in stubs.values():
                return Finding(path, a.lineno, fn.name, "mock-echo", "advisory", "report-only",
                               "compares against the exact value stubbed into a mock's return_value — "
                               "likely echoes the mock rather than testing logic", node=a)

    # type probes (filled in by the mypy pass)
    if path is not None and probes is not None:
        try:
            lines = split_lines_keepends(open(path, encoding="utf-8", newline="").read())
            raw = lines[a.lineno - 1].rstrip("\r\n")
            indent = len(raw) - len(raw.lstrip())
        except Exception:
            indent = 0

        def queue(kind, expr_node, extra):
            try:
                expr_src = " ".join(ast.unparse(expr_node).split())
            except Exception:
                return None
            if file_has_cast:
                return None  # cast()/type:ignore in file — types may lie, stay silent
            if any(isinstance(n, ast.Call) for n in ast.walk(expr_node)):
                # the checked value is produced by an inline call (e.g.
                # `assert isinstance(fetch(), dict)`); deleting the assertion would
                # also delete that call's execution — real smoke coverage. Only
                # flag assertions whose subject is already-bound (a name/attr).
                return None
            p = Probe(path, a.lineno, indent, expr_src, kind, extra)
            p.finding_slot = (fn.name, a)
            probes.append(p)
            return p

        # assert x is not None
        if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], ast.IsNot) \
                and isinstance(t.comparators[0], ast.Constant) and t.comparators[0].value is None:
            return "QUEUED" if queue("not-none", t.left, None) else None

        # assert isinstance(x, T)
        if isinstance(t, ast.Call) and isinstance(t.func, ast.Name) and t.func.id == "isinstance" \
                and len(t.args) == 2:
            cls = t.args[1]
            names = []
            for c in (cls.elts if isinstance(cls, ast.Tuple) else [cls]):
                if isinstance(c, ast.Name):
                    names.append(c.id)
                elif isinstance(c, ast.Attribute):
                    names.append(c.attr)
            if names:
                return "QUEUED" if queue("isinstance", t.args[0], names) else None
            return None

        # assert type(x) is T  — advisory even when types match (subclass caveat)
        if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], (ast.Is, ast.Eq)) \
                and isinstance(t.left, ast.Call) and isinstance(t.left.func, ast.Name) \
                and t.left.func.id == "type" and len(t.left.args) == 1:
            c = t.comparators[0]
            nm = c.id if isinstance(c, ast.Name) else (c.attr if isinstance(c, ast.Attribute) else None)
            if nm:
                return "QUEUED" if queue("exact-type", t.left.args[0], [nm]) else None
            return None

    return None
