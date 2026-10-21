from __future__ import annotations
import ast
import os

class Finding:
    def __init__(self, file, line, test, category, level, deletable, reason, node=None):
        self.file, self.line, self.test = file, line, test
        self.category, self.level, self.deletable = category, level, deletable
        self.reason, self.node = reason, node

    def to_dict(self, root):
        return {
            "file": os.path.relpath(self.file, root),
            "line": self.line,
            "test": self.test,
            "category": self.category,
            "level": self.level,
            "deletable": self.deletable,
            "reason": self.reason
        }


class Probe:
    """A type question for mypy: what is the type of `expr` just before `line`?"""
    def __init__(self, file, line, indent, expr_src, kind, extra):
        self.file, self.line, self.indent = file, line, indent
        self.expr_src, self.kind, self.extra = expr_src, kind, extra
        self.revealed: str | None = None
        self.finding_slot = None  # (test_record, assert_node) to fill on success


class TestRecord:
    def __init__(self, file, node, name, scope_key):
        self.file, self.node, self.name, self.scope_key = file, node, name, scope_key
        self.findings: list[Finding] = []
        self.live_assert_count = 0
        self.nonredundant = 0      # live assertions we could not prove useless
        self.helper_asserts = 0    # assertions living in called helpers
        self.conditional = 0
        self.is_duplicate = False
        self.body_key = None
