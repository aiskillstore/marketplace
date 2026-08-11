#!/usr/bin/env python3
"""Render a Brandkit PPTX to PDF locally with exact-font verification.

The Brandkit builder owns the PPTX structure. This script registers the approved
fonts, invokes LibreOffice, and checks the embedded PDF fonts with Poppler.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import unicodedata
from xml.sax.saxutils import escape


COMMAND_TIMEOUT_SECONDS = 90


def family_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(character.lower() for character in normalized if character.isalnum())


def run(label: str, command: list[str], environment: dict[str, str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=True,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"{label} timed out") from error
    except subprocess.CalledProcessError as error:
        detail = (error.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"{label} failed{suffix}") from error
    return completed.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--pptx", required=True, type=Path)
    parser.add_argument("--fonts-dir", required=True, type=Path)
    parser.add_argument("--families-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    work_dir: Path = args.work_dir.resolve()
    pptx: Path = args.pptx.resolve()
    fonts_dir: Path = args.fonts_dir.resolve()
    families_path: Path = args.families_json.resolve()
    output: Path = args.output.resolve()
    profile_dir = work_dir / "libreoffice-profile"
    font_cache = work_dir / "font-cache"
    font_config = work_dir / "fonts.conf"

    profile_dir.mkdir(parents=True, exist_ok=True)
    font_cache.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    families = json.loads(families_path.read_text(encoding="utf-8"))
    if not isinstance(families, list) or not families or not all(
        isinstance(family, str) and family.strip() for family in families
    ):
        raise RuntimeError("Brandbook PDF conversion requires approved font families")

    font_config.write_text(
        '<?xml version="1.0"?>\n'
        '<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n'
        "<fontconfig>\n"
        "  <include ignore_missing=\"yes\">/etc/fonts/fonts.conf</include>\n"
        f"  <dir>{escape(str(fonts_dir))}</dir>\n"
        f"  <cachedir>{escape(str(font_cache))}</cachedir>\n"
        "</fontconfig>\n",
        encoding="utf-8",
    )
    environment = {
        **os.environ,
        "FONTCONFIG_FILE": str(font_config),
        "FONTCONFIG_PATH": str(work_dir),
    }

    run("Brandbook font cache", ["fc-cache", "-f", str(fonts_dir)], environment)
    for family in families:
        match = run(
            f"Brandbook font verification for '{family}'",
            ["fc-match", "--format=%{family}", family],
            environment,
        )
        if family_key(family) not in family_key(match):
            raise RuntimeError(
                f"Brandbook font '{family}' was substituted with '{match.strip()}'"
            )

    run(
        "LibreOffice Brandbook conversion",
        [
            "soffice",
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output.parent),
            str(pptx),
        ],
        environment,
    )
    converted = output.parent / f"{pptx.stem}.pdf"
    if converted != output:
        converted.replace(output)
    if not output.read_bytes().startswith(b"%PDF-"):
        raise RuntimeError("LibreOffice returned an invalid Brandbook PDF")

    embedded_fonts = run(
        "Brandbook PDF font inspection",
        ["pdffonts", str(output)],
        environment,
    )
    embedded_key = family_key(embedded_fonts)
    for family in families:
        if family_key(family) not in embedded_key:
            raise RuntimeError(f"Brandbook PDF did not embed font '{family}'")
    font_names = [
        line.split()[0]
        for line in embedded_fonts.splitlines()[2:]
        if line.strip()
    ]
    unexpected = [
        name
        for name in font_names
        if not any(family_key(family) in family_key(name) for family in families)
    ]
    if unexpected:
        raise RuntimeError(
            "Brandbook PDF contains unapproved fonts: " + ", ".join(unexpected)
        )

    print(
        json.dumps(
            {
                "families": families,
                "output": str(output),
                "status": "ok",
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
