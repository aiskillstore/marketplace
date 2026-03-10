"""Formula recalculation helpers for Calc."""

from pathlib import Path

from uno_bridge import uno_context


def recalculate(path: str) -> None:
    """Force formula recalculation for a spreadsheet.

    Args:
        path: Path to the spreadsheet file.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            doc.calculate()
            doc.store()
        finally:
            doc.close(True)
