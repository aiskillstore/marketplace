from __future__ import annotations
import os

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".tox",
             ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs"}

# reveal_type() shadow copies written next to each test file by mypy_pass.
# They are removed in a finally:, but a SIGKILL mid-run can strand one — and a
# stranded `_cap_obv_shadow_foo_test.py` matches the `*_test.py` arm below, so
# without this guard the next scan collects it as a real test file.
SHADOW_PREFIX = "_cap_obv_shadow_"

def is_test_filename(name: str) -> bool:
    if name.startswith(SHADOW_PREFIX):
        return False
    return name.startswith("test_") and name.endswith(".py") or name.endswith("_test.py")

def find_test_files(root: str) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            if is_test_filename(f):
                out.append(os.path.join(dirpath, f))
    return sorted(out)
