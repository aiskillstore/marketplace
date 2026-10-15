#!/usr/bin/env python3
"""
distill.py — OPTIONAL. Auto-draft principle entries from staged posts using Claude.

Reads each staging/prompts/<id>.md produced by update.py (which already embeds the
distillation spec + the post text + the paths of its images), sends it to Claude
with the images attached, and writes a reviewable draft to staging/drafts/<id>.md.

This is a convenience for hands-off/CI use. The primary flow is to run the same
staging/prompts/<id>.md through Claude Code (or any agent) yourself and review the
result. Either way, a HUMAN reviews the draft before it goes into references/.

Requires:  pip install anthropic   and   ANTHROPIC_API_KEY set (or `ant auth login`).
"""

import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
S_PROMPTS = HERE / "staging" / "prompts"
S_MEDIA = HERE / "staging" / "media"
S_DRAFTS = HERE / "staging" / "drafts"

MODEL = "claude-opus-4-8"  # default per Anthropic guidance; change only if you must
MEDIA_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
               ".gif": "image/gif", ".webp": "image/webp"}


def main():
    try:
        import anthropic
        from pydantic import BaseModel
    except ImportError:
        sys.exit("ERROR: `pip install anthropic` (bundles pydantic) to use distill.py.")

    class Draft(BaseModel):
        theme_slug: str
        entry_markdown: str

    prompts = sorted(S_PROMPTS.glob("*.md")) if S_PROMPTS.exists() else []
    if not prompts:
        sys.exit("No staged prompts found. Run `python update.py` first.")
    S_DRAFTS.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()

    for pf in prompts:
        tid = pf.stem
        content = []
        for img in sorted(S_MEDIA.glob(f"{tid}__*")):
            mt = MEDIA_TYPES.get(img.suffix.lower())
            if not mt:
                continue  # skip video/unknown; the text notes it
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": mt,
                "data": base64.standard_b64encode(img.read_bytes()).decode()}})
        content.append({"type": "text", "text": pf.read_text()})

        try:
            resp = client.messages.parse(
                model=MODEL, max_tokens=2000,
                system=("Follow the distillation spec in the message exactly. Return the chosen "
                        "theme slug and the finished principle entry as markdown."),
                messages=[{"role": "user", "content": content}],
                output_format=Draft,
            )
        except anthropic.APIError as e:
            print(f"  ✗ {tid}: API error — {e}")
            continue

        draft = resp.parsed_output
        if draft is None:
            print(f"  ✗ {tid}: model did not return a valid draft (refusal or parse fail)")
            continue
        (S_DRAFTS / f"{tid}.md").write_text(
            f"<!-- proposed theme: references/{draft.theme_slug}.md -->\n\n"
            + draft.entry_markdown.strip() + "\n")
        print(f"  ✓ {tid}: draft -> staging/drafts/{tid}.md  (theme: {draft.theme_slug})")

    print(f"\nReview each staging/drafts/<id>.md, then paste approved entries into the "
          f"named references/<theme>.md (newest-first) and run refresh_meta.py.")


if __name__ == "__main__":
    main()
