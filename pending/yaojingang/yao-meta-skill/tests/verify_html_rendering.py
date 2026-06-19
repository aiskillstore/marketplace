#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from html_rendering import html_text  # noqa: E402


def main() -> None:
    assert html_text(None) == ""
    assert html_text(0) == "0"
    assert html_text(False) == "False"
    assert html_text("") == ""
    assert html_text("<tag data-x=\"1\">&</tag>") == "&lt;tag data-x=&quot;1&quot;&gt;&amp;&lt;/tag&gt;"
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
