import tempfile
import zipfile
from pathlib import Path

MAX_ZIP_SIZE = 20 * 1024 * 1024  # 20 MB
MAX_FILE_COUNT = 20


class PackageError(Exception):
    pass


def _validate_zip(zp: Path) -> None:
    if zp.stat().st_size > MAX_ZIP_SIZE:
        raise PackageError(f"ZIP file exceeds 20 MB limit")
    with zipfile.ZipFile(zp) as zf:
        if len(zf.namelist()) > MAX_FILE_COUNT:
            raise PackageError(f"ZIP contains more than {MAX_FILE_COUNT} files")


def _zip_paths(paths: list[Path], dest: Path) -> None:
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, p.name)


def package(inputs: list[str]) -> Path:
    paths = [Path(p) for p in inputs]

    for p in paths:
        if not p.exists():
            raise PackageError(f"Path not found: {p}")

    # Single .zip file — passthrough
    if len(paths) == 1 and paths[0].suffix == ".zip":
        _validate_zip(paths[0])
        return paths[0]

    # Single directory — zip its contents
    if len(paths) == 1 and paths[0].is_dir():
        files = [f for f in paths[0].rglob("*") if f.is_file()]
        if len(files) > MAX_FILE_COUNT:
            raise PackageError(f"Directory contains more than {MAX_FILE_COUNT} files")
        dest = Path(tempfile.mktemp(suffix=".zip"))
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f, f.relative_to(paths[0]))
        _validate_zip(dest)
        return dest

    # Multiple files — zip them together
    if len(paths) > MAX_FILE_COUNT:
        raise PackageError(f"Input exceeds {MAX_FILE_COUNT} files limit")
    dest = Path(tempfile.mktemp(suffix=".zip"))
    _zip_paths(paths, dest)
    _validate_zip(dest)
    return dest
