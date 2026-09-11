from __future__ import annotations

import shutil
import subprocess
import uuid
import re
from pathlib import Path
from typing import Any

from pptx import Presentation


def _not_run(reason: str) -> dict[str, Any]:
    return {"status": "not_run", "reason": reason, "artifacts": []}


def _reset_renderer_directory(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)


_SLIDE_ARTIFACT_PATTERN = re.compile(
    r"(?:slide|page)[-_ ]*0*([1-9][0-9]*)\.png$", re.IGNORECASE
)


def _normalize_complete_artifacts(
    artifacts: list[Path], renderer_directory: Path, expected_slide_count: int
) -> list[Path] | None:
    """Require one local PNG for every slide and promote a canonical file name."""

    resolved_directory = renderer_directory.resolve()
    resolved_paths = [Path(path).resolve() for path in artifacts]
    if len(set(resolved_paths)) != len(resolved_paths):
        return None
    if not all(
        path.is_file() and path.is_relative_to(resolved_directory)
        for path in resolved_paths
    ):
        return None
    page_numbers: list[int] = []
    for path in resolved_paths:
        match = _SLIDE_ARTIFACT_PATTERN.fullmatch(path.name)
        if match is None:
            return None
        page_numbers.append(int(match.group(1)))
    if sorted(page_numbers) != list(range(1, expected_slide_count + 1)):
        return None
    normalized: list[Path] = []
    for page_number, path in sorted(zip(page_numbers, resolved_paths)):
        canonical = resolved_directory / f"slide-{page_number:02d}.png"
        if path != canonical:
            path.replace(canonical)
        normalized.append(canonical)
    return normalized


def _render_with_powerpoint_com(pptx_path: Path, output_dir: Path) -> list[Path] | None:
    """Render through desktop PowerPoint when the optional COM bridge is available."""

    try:
        import win32com.client  # type: ignore[import-not-found]
    except ImportError:
        return None

    application = presentation = None
    try:
        application = win32com.client.DispatchEx("PowerPoint.Application")
        application.Visible = 1
        presentation = application.Presentations.Open(
            str(pptx_path.resolve()), False, False, False
        )
        artifacts: list[Path] = []
        for index, slide in enumerate(presentation.Slides, start=1):
            artifact = output_dir / f"slide-{index:02d}.png"
            slide.Export(str(artifact), "PNG", 1600, 900)
            if artifact.is_file():
                artifacts.append(artifact)
        return artifacts or None
    except Exception:
        return None
    finally:
        if presentation is not None:
            try:
                presentation.Close()
            except Exception:
                pass
        if application is not None:
            try:
                application.Quit()
            except Exception:
                pass


def _render_with_soffice(pptx_path: Path, output_dir: Path) -> list[Path] | None:
    """Use LibreOffice headlessly only after the PowerPoint route is unavailable."""

    soffice = shutil.which("soffice") or shutil.which("soffice.exe")
    if not soffice:
        return None
    try:
        completed = subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(pptx_path),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=90,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    artifact = output_dir / f"{pptx_path.stem}.pdf"
    if completed.returncode != 0 or not artifact.is_file():
        return None
    pdftoppm = shutil.which("pdftoppm") or shutil.which("pdftoppm.exe")
    if not pdftoppm:
        # Keep the PDF as evidence of an attempted soffice conversion; the
        # caller will mark a multi-page deck incomplete rather than passing it.
        return [artifact]
    try:
        converted = subprocess.run(
            [pdftoppm, "-png", str(artifact), str(output_dir / "slide")],
            capture_output=True,
            text=True,
            check=False,
            timeout=90,
        )
    except (OSError, subprocess.SubprocessError):
        return [artifact]
    artifacts = sorted(output_dir.glob("slide-*.png"))
    return artifacts if converted.returncode == 0 and artifacts else [artifact]


def render_ppt_for_review(pptx_path: Path, output_dir: Path) -> dict[str, Any]:
    """Create render artifacts while reserving final visual approval for a human."""

    source = Path(pptx_path)
    if not source.is_file():
        return _not_run("pptx_not_found")
    try:
        expected_slide_count = len(Presentation(source).slides)
    except Exception:
        return _not_run("pptx_unreadable")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    run_directory = destination / f"render-{uuid.uuid4().hex}"
    run_directory.mkdir()
    incomplete_seen = False
    for renderer, render in (
        ("powerpoint_com", _render_with_powerpoint_com),
        ("soffice", _render_with_soffice),
    ):
        renderer_directory = run_directory / renderer
        _reset_renderer_directory(renderer_directory)
        try:
            artifacts = render(source, renderer_directory)
        except Exception:
            artifacts = None
        if artifacts:
            normalized_artifacts = _normalize_complete_artifacts(
                artifacts, renderer_directory, expected_slide_count
            )
            if normalized_artifacts is None:
                incomplete_seen = True
                _reset_renderer_directory(renderer_directory)
                continue
            return {
                "status": "rendered_pending_review",
                "renderer": renderer,
                "artifacts": [str(path) for path in normalized_artifacts],
            }
        _reset_renderer_directory(renderer_directory)
    shutil.rmtree(run_directory, ignore_errors=True)
    return _not_run("incomplete_render" if incomplete_seen else "no_supported_renderer")
