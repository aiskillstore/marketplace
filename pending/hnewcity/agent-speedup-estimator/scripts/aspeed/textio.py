from __future__ import annotations

import io
from pathlib import Path
from typing import IO


class UnsupportedCompression(OSError):
    pass


def open_text(path: Path) -> IO[str]:
    """Open a transcript for line reading; transparently handles .zst files."""
    if not path.name.endswith(".zst"):
        return open(path, encoding="utf-8", errors="replace")
    try:
        from compression import zstd  # Python 3.14+

        return io.TextIOWrapper(zstd.ZstdFile(path), encoding="utf-8", errors="replace")
    except ImportError:
        pass
    try:
        import zstandard
    except ImportError:
        raise UnsupportedCompression(
            "compressed transcript needs Python 3.14+ or the 'zstandard' package (pip install zstandard)"
        ) from None
    reader = zstandard.ZstdDecompressor().stream_reader(open(path, "rb"))
    return io.TextIOWrapper(reader, encoding="utf-8", errors="replace")
