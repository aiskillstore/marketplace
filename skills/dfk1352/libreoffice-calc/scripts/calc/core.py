"""Core document lifecycle operations for Calc."""

from pathlib import Path

from calc.exceptions import CalcSkillError, DocumentNotFoundError
from uno_bridge import uno_context


EXPORT_FILTERS = {
    "pdf": "calc_pdf_Export",
    "xlsx": "Calc MS Excel 2007 XML",
    "csv": "Text - txt - csv (StarCalc)",
}


def create_spreadsheet(path: str) -> None:
    """Create a new Calc spreadsheet at the specified path.

    Args:
        path: Output path for the new spreadsheet.
    """
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, ())
        try:
            file_url = output.resolve().as_uri()
            doc.storeAsURL(file_url, ())
        finally:
            doc.close(True)


def export_spreadsheet(path: str, output_path: str, format: str) -> None:
    """Export a spreadsheet to another format.

    Args:
        path: Path to the spreadsheet file.
        output_path: Destination file path.
        format: Export format key.

    Raises:
        CalcSkillError: If the export format is unsupported.
    """
    if format not in EXPORT_FILTERS:
        raise CalcSkillError(f"Unsupported export format: {format}")
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(),
            "_blank",
            0,
            (),
        )
        try:
            import uno

            filter_name = EXPORT_FILTERS[format]
            filter_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
            filter_prop.Name = "FilterName"
            filter_prop.Value = filter_name
            doc.storeToURL(output.resolve().as_uri(), (filter_prop,))
        finally:
            doc.close(True)
