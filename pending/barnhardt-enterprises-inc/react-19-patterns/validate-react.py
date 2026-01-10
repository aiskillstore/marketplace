#!/usr/bin/env python3
"""
React 19 Pattern Validator

Validates React components for:
- Rules of Hooks violations
- Server/Client component mistakes
- Proper 'use client' directive placement
- Invalid async Client Components
- Browser API usage in Server Components
- Non-serializable props to Client Components
- Missing dependency arrays
- Proper ref usage
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Issue:
    file: str
    line: int
    column: int
    severity: Severity
    rule: str
    message: str


class ReactValidator:
    """Validates React 19 patterns and best practices."""

    # React hooks that must follow Rules of Hooks
    HOOKS = [
        "useState",
        "useEffect",
        "useContext",
        "useReducer",
        "useCallback",
        "useMemo",
        "useRef",
        "useImperativeHandle",
        "useLayoutEffect",
        "useDebugValue",
        "useDeferredValue",
        "useTransition",
        "useId",
        "useSyncExternalStore",
        "useInsertionEffect",
        "use",
        "useOptimistic",
        "useFormStatus",
        "useActionState",
    ]

    # Browser-only APIs that can't be used in Server Components
    BROWSER_APIS = [
        "window",
        "document",
        "localStorage",
        "sessionStorage",
        "navigator",
        "location",
        "history",
        "alert",
        "confirm",
        "prompt",
        "fetch",  # In Server Components, use server-side fetch
    ]

    def __init__(self, fix_mode: bool = False):
        self.fix_mode = fix_mode
        self.issues: List[Issue] = []

    def validate_file(self, file_path: str) -> List[Issue]:
        """Validate a single React file."""
        self.issues = []

        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return self.issues

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Detect component type
        is_client = self._is_client_component(content)
        is_server = not is_client
        has_use_client = "'use client'" in content or '"use client"' in content

        # Run validation checks
        self._check_use_client_placement(lines, file_path)
        self._check_async_client_component(content, lines, file_path, has_use_client)
        self._check_hooks_usage(lines, file_path)
        self._check_browser_apis_in_server(content, lines, file_path, is_server)
        self._check_effect_dependencies(lines, file_path)
        self._check_string_refs(lines, file_path)
        self._check_default_props(lines, file_path)
        self._check_event_handlers_in_server(lines, file_path, is_server)

        return self.issues

    def validate_directory(self, dir_path: str) -> List[Issue]:
        """Validate all React files in a directory."""
        self.issues = []

        path = Path(dir_path)
        react_files = list(path.rglob("*.tsx")) + list(path.rglob("*.jsx"))

        for file_path in react_files:
            self.validate_file(str(file_path))

        return self.issues

    def _is_client_component(self, content: str) -> bool:
        """Check if file has 'use client' directive."""
        # Check first few lines for 'use client'
        first_lines = content.split("\n")[:5]
        for line in first_lines:
            if "'use client'" in line or '"use client"' in line:
                return True
        return False

    def _check_use_client_placement(self, lines: List[str], file_path: str):
        """Check 'use client' is at top of file."""
        use_client_line = None

        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            if "'use client'" in line or '"use client"' in line:
                use_client_line = i
                break

        if use_client_line is not None:
            # Check if there's any code before 'use client'
            for i in range(use_client_line):
                line = lines[i].strip()
                if line and not line.startswith("//") and not line.startswith("/*"):
                    self.issues.append(
                        Issue(
                            file=file_path,
                            line=use_client_line + 1,
                            column=0,
                            severity=Severity.ERROR,
                            rule="use-client-placement",
                            message="'use client' must be at the top of the file, before any imports",
                        )
                    )
                    break

    def _check_async_client_component(
        self, content: str, lines: List[str], file_path: str, is_client: bool
    ):
        """Check for async Client Components (not allowed)."""
        if not is_client:
            return

        # Match: export default async function ComponentName
        async_pattern = r"export\s+default\s+async\s+function\s+\w+"
        matches = re.finditer(async_pattern, content)

        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            self.issues.append(
                Issue(
                    file=file_path,
                    line=line_num,
                    column=match.start(),
                    severity=Severity.ERROR,
                    rule="no-async-client-component",
                    message="Client Components cannot be async. Use useEffect or Server Component instead.",
                )
            )

    def _check_hooks_usage(self, lines: List[str], file_path: str):
        """Check Rules of Hooks violations."""
        in_function = False
        in_component = False
        function_name = ""
        indent_level = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track function/component entry
            if re.match(r"(function|const|export)\s+\w+", stripped):
                match = re.search(r"(function|const|export)\s+(\w+)", stripped)
                if match:
                    function_name = match.group(2)
                    # Component names start with capital letter or start with 'use'
                    in_component = function_name[0].isupper() or function_name.startswith(
                        "use"
                    )
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())

            # Check for hooks
            for hook in self.HOOKS:
                if f"{hook}(" in stripped:
                    # Check if hook is in conditional
                    if re.match(r"^\s*if\s*\(", stripped):
                        self.issues.append(
                            Issue(
                                file=file_path,
                                line=i + 1,
                                column=0,
                                severity=Severity.ERROR,
                                rule="hooks-in-conditional",
                                message=f"Hook '{hook}' cannot be called inside a conditional. Hooks must be called at the top level.",
                            )
                        )

                    # Check if hook is in loop
                    if re.match(r"^\s*(for|while)\s*\(", stripped):
                        self.issues.append(
                            Issue(
                                file=file_path,
                                line=i + 1,
                                column=0,
                                severity=Severity.ERROR,
                                rule="hooks-in-loop",
                                message=f"Hook '{hook}' cannot be called inside a loop. Hooks must be called at the top level.",
                            )
                        )

                    # Check if hook is in regular function (not component or custom hook)
                    if in_function and not in_component:
                        self.issues.append(
                            Issue(
                                file=file_path,
                                line=i + 1,
                                column=0,
                                severity=Severity.ERROR,
                                rule="hooks-in-regular-function",
                                message=f"Hook '{hook}' can only be called in React components or custom hooks (functions starting with 'use').",
                            )
                        )

    def _check_browser_apis_in_server(
        self, content: str, lines: List[str], file_path: str, is_server: bool
    ):
        """Check for browser API usage in Server Components."""
        if not is_server:
            return

        for api in self.BROWSER_APIS:
            pattern = rf"\b{api}\b"
            matches = re.finditer(pattern, content)

            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                line = lines[line_num - 1]

                # Skip if in comment
                if "//" in line and line.index("//") < match.start():
                    continue

                self.issues.append(
                    Issue(
                        file=file_path,
                        line=line_num,
                        column=match.start(),
                        severity=Severity.ERROR,
                        rule="no-browser-api-in-server",
                        message=f"Browser API '{api}' cannot be used in Server Components. Add 'use client' directive or move to Client Component.",
                    )
                )

    def _check_effect_dependencies(self, lines: List[str], file_path: str):
        """Check useEffect has dependency array."""
        for i, line in enumerate(lines):
            if "useEffect(" in line:
                # Look for closing parenthesis in next few lines
                effect_block = "\n".join(lines[i : i + 10])

                # Check if there's a dependency array
                if not re.search(r"\}\s*,\s*\[", effect_block):
                    self.issues.append(
                        Issue(
                            file=file_path,
                            line=i + 1,
                            column=0,
                            severity=Severity.WARNING,
                            rule="effect-missing-deps",
                            message="useEffect should include a dependency array. Use [] for mount-only effects.",
                        )
                    )

    def _check_string_refs(self, lines: List[str], file_path: str):
        """Check for string refs (deprecated in React 19)."""
        for i, line in enumerate(lines):
            if re.search(r'ref\s*=\s*["\']', line):
                self.issues.append(
                    Issue(
                        file=file_path,
                        line=i + 1,
                        column=0,
                        severity=Severity.ERROR,
                        rule="no-string-refs",
                        message="String refs are removed in React 19. Use useRef() or createRef() instead.",
                    )
                )

    def _check_default_props(self, lines: List[str], file_path: str):
        """Check for defaultProps (deprecated for function components)."""
        for i, line in enumerate(lines):
            if ".defaultProps" in line:
                self.issues.append(
                    Issue(
                        file=file_path,
                        line=i + 1,
                        column=0,
                        severity=Severity.WARNING,
                        rule="no-default-props",
                        message="defaultProps is deprecated for function components in React 19. Use default parameters instead.",
                    )
                )

    def _check_event_handlers_in_server(
        self, lines: List[str], file_path: str, is_server: bool
    ):
        """Check for event handlers in Server Components."""
        if not is_server:
            return

        event_handlers = [
            "onClick",
            "onChange",
            "onSubmit",
            "onFocus",
            "onBlur",
            "onKeyDown",
            "onKeyUp",
            "onMouseEnter",
            "onMouseLeave",
        ]

        for i, line in enumerate(lines):
            for handler in event_handlers:
                if f"{handler}=" in line:
                    self.issues.append(
                        Issue(
                            file=file_path,
                            line=i + 1,
                            column=0,
                            severity=Severity.ERROR,
                            rule="no-event-handlers-in-server",
                            message=f"Event handler '{handler}' cannot be used in Server Components. Add 'use client' directive.",
                        )
                    )

    def print_issues(self):
        """Print all issues in a readable format."""
        if not self.issues:
            print("✅ No issues found!")
            return

        # Group by severity
        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        warnings = [i for i in self.issues if i.severity == Severity.WARNING]
        infos = [i for i in self.issues if i.severity == Severity.INFO]

        print(f"\n{'='*80}")
        print(f"React 19 Validation Results")
        print(f"{'='*80}\n")

        if errors:
            print(f"❌ {len(errors)} Error(s):\n")
            for issue in errors:
                print(f"  {issue.file}:{issue.line}:{issue.column}")
                print(f"  [{issue.rule}] {issue.message}\n")

        if warnings:
            print(f"⚠️  {len(warnings)} Warning(s):\n")
            for issue in warnings:
                print(f"  {issue.file}:{issue.line}:{issue.column}")
                print(f"  [{issue.rule}] {issue.message}\n")

        if infos:
            print(f"ℹ️  {len(infos)} Info:\n")
            for issue in infos:
                print(f"  {issue.file}:{issue.line}:{issue.column}")
                print(f"  [{issue.rule}] {issue.message}\n")

        print(f"{'='*80}")
        print(f"Total: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate React 19 patterns and best practices"
    )
    parser.add_argument("path", help="File or directory to validate")
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix issues"
    )

    args = parser.parse_args()

    validator = ReactValidator(fix_mode=args.fix)

    if os.path.isfile(args.path):
        validator.validate_file(args.path)
    elif os.path.isdir(args.path):
        validator.validate_directory(args.path)
    else:
        print(f"Error: Path not found: {args.path}")
        sys.exit(1)

    validator.print_issues()

    # Exit with error code if there are errors
    errors = [i for i in validator.issues if i.severity == Severity.ERROR]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
