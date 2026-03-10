"""Cell formatting helpers for Calc."""

from pathlib import Path

from calc.exceptions import CalcSkillError
from colors import resolve_color
from uno_bridge import uno_context


NUMBER_FORMATS = {
    "currency": "currency",
    "percentage": "percent",
    "date": "date",
    "time": "time",
}


def _standard_number_format(doc, kind: str) -> int:
    from com.sun.star.util import NumberFormat

    formats = doc.getNumberFormats()
    locale = getattr(formats, "getLocale", lambda: doc.CharLocale)()
    mapping = {
        "currency": NumberFormat.CURRENCY,
        "percent": NumberFormat.PERCENT,
        "date": NumberFormat.DATE,
        "time": NumberFormat.TIME,
    }
    return formats.getStandardFormat(mapping[kind], locale)


def apply_format(
    path: str,
    sheet: str | int,
    row: int,
    col: int,
    format: dict[str, object],
) -> None:
    """Apply formatting to a single cell.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        row: Zero-based row index.
        col: Zero-based column index.
        format: Formatting dictionary.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            if isinstance(sheet, int):
                target_sheet = doc.Sheets.getByIndex(sheet)
            else:
                target_sheet = doc.Sheets.getByName(sheet)
            cell = target_sheet.getCellByPosition(col, row)
            if "bold" in format:
                cell.CharWeight = 150 if format["bold"] else 100
            if "italic" in format:
                cell.CharPosture = 2 if format["italic"] else 0
            if "font_size" in format:
                font_size = format["font_size"]
                if isinstance(font_size, (int, float)):
                    cell.CharHeight = float(font_size)
            if "font_name" in format:
                cell.CharFontName = str(format["font_name"])
            if "color" in format:
                color_value = format["color"]
                if isinstance(color_value, (int, str)):
                    cell.CharColor = resolve_color(color_value)
                else:
                    raise CalcSkillError(
                        f"Unsupported color type: {type(color_value).__name__}"
                    )
            if "number_format" in format:
                number_key = str(format["number_format"])
                if number_key not in NUMBER_FORMATS:
                    raise CalcSkillError(f"Unsupported number format: {number_key}")
                cell.NumberFormat = _standard_number_format(
                    doc,
                    NUMBER_FORMATS[number_key],
                )
            doc.store()
        finally:
            doc.close(True)
