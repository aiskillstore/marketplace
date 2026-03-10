"""Chart helpers for Calc."""

from pathlib import Path

from calc.exceptions import ChartError
from uno_bridge import uno_context


CHART_TYPES = {
    "bar": "com.sun.star.chart.BarDiagram",
    "line": "com.sun.star.chart.LineDiagram",
    "pie": "com.sun.star.chart.PieDiagram",
    "scatter": "com.sun.star.chart.XYDiagram",
}


def _rectangle_from_anchor(
    sheet,
    anchor: tuple[int, int],
    size: tuple[int, int],
):
    import uno

    cell = sheet.getCellByPosition(anchor[1], anchor[0])
    pos = cell.Position
    rect = uno.createUnoStruct("com.sun.star.awt.Rectangle")
    rect.X = pos.X
    rect.Y = pos.Y
    rect.Width = int(size[0])
    rect.Height = int(size[1])
    return rect


def create_chart(
    path: str,
    sheet: str | int,
    data_range: tuple[int, int, int, int],
    chart_type: str,
    anchor: tuple[int, int],
    size: tuple[int, int],
    title: str | None = None,
) -> None:
    """Create a chart from a data range.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        data_range: (start_row, start_col, end_row, end_col).
        chart_type: Chart type key ("bar", "line", "pie", "scatter").
        anchor: (row, col) zero-based cell that pins the chart top-left.
        size: (width_px, height_px) pixel dimensions of the chart.
        title: Optional chart title.
    """
    if chart_type not in CHART_TYPES:
        raise ChartError(f"Unsupported chart type: {chart_type}")
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
            charts = target_sheet.Charts
            name = f"Chart{charts.getCount()}"
            range_addr = target_sheet.getCellRangeByPosition(
                data_range[1],
                data_range[0],
                data_range[3],
                data_range[2],
            ).getRangeAddress()
            rect = _rectangle_from_anchor(target_sheet, anchor, size)
            charts.addNewByName(
                name,
                rect,
                (range_addr,),
                True,
                True,
            )
            chart = charts.getByName(name).EmbeddedObject
            diagram = chart.createInstance(CHART_TYPES[chart_type])
            chart.setDiagram(diagram)
            try:
                chart.setDataRange((range_addr,))
            except Exception:
                pass
            if title:
                chart.HasMainTitle = True
                chart.Title.String = title
            doc.store()
        finally:
            doc.close(True)
