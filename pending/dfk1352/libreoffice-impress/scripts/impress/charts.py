"""Chart operations for Impress."""

import warnings
from pathlib import Path

from impress._util import _cm_to_hmm
from impress.exceptions import DocumentNotFoundError, ImpressSkillError
from uno_bridge import uno_context


CHART_TYPE_MAP = {
    "bar": "com.sun.star.chart.BarDiagram",
    "line": "com.sun.star.chart.LineDiagram",
    "pie": "com.sun.star.chart.PieDiagram",
    "scatter": "com.sun.star.chart.XYDiagram",
}

# CLSID for LibreOffice chart object
CHART_CLSID = "12DCAE26-281F-416F-a234-c3086127382e"


def add_chart(
    path: str,
    slide_index: int,
    chart_type: str,
    data: list[list],
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
    title: str | None = None,
) -> int:
    """Insert an embedded chart on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        chart_type: Chart type: bar, line, pie, scatter.
        data: 2D list of chart data. First row is headers.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.
        title: Optional chart title.

    Returns:
        Shape index of the new chart.

    Raises:
        ImpressSkillError: If chart_type is unknown.
    """
    if chart_type not in CHART_TYPE_MAP:
        raise ImpressSkillError(
            f"Unsupported chart type: {chart_type}. "
            f"Valid types: {list(CHART_TYPE_MAP.keys())}"
        )

    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        import uno  # type: ignore[import-not-found]

        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            slide = doc.DrawPages.getByIndex(slide_index)

            shape = doc.createInstance("com.sun.star.drawing.OLE2Shape")

            pos = uno.createUnoStruct("com.sun.star.awt.Point")
            pos.X = _cm_to_hmm(x_cm)
            pos.Y = _cm_to_hmm(y_cm)
            shape.Position = pos

            size = uno.createUnoStruct("com.sun.star.awt.Size")
            size.Width = _cm_to_hmm(width_cm)
            size.Height = _cm_to_hmm(height_cm)
            shape.Size = size

            # Set CLSID before adding to slide
            shape.CLSID = CHART_CLSID

            slide.add(shape)

            # Access the embedded chart via the OLE object's Component
            embed_obj = shape.EmbeddedObject
            chart_doc = embed_obj.Component if embed_obj is not None else None

            if chart_doc is not None:
                # Set chart type via old chart API
                diagram = chart_doc.createInstance(CHART_TYPE_MAP[chart_type])
                chart_doc.setDiagram(diagram)

                if data and len(data) > 1:
                    try:
                        _populate_chart_data(chart_doc, data, chart_type)
                    except Exception as exc:
                        warnings.warn(
                            f"chart data population failed: {exc}",
                            stacklevel=2,
                        )

                if title:
                    try:
                        chart_doc.HasMainTitle = True
                        chart_doc.Title.String = title
                    except Exception as exc:
                        warnings.warn(
                            f"chart title assignment failed: {exc}",
                            stacklevel=2,
                        )

            shape_index = slide.Count - 1
            doc.store()
            return shape_index
        finally:
            doc.close(True)


def _populate_chart_data(
    chart_doc: object,
    data: list[list],
    chart_type: str,
) -> None:
    """Populate chart with data using the internal data provider.

    Args:
        chart_doc: UNO chart document object.
        data: 2D list with headers in first row.
        chart_type: Chart type key.
    """
    try:
        chart_data = chart_doc.getData()  # type: ignore[attr-defined]
        if chart_data is None:
            return

        headers = data[0]
        rows = data[1:]

        categories = [str(row[0]) for row in rows]
        chart_data.setColumnDescriptions(tuple(categories))

        if len(headers) > 1:
            chart_data.setRowDescriptions(tuple(str(h) for h in headers[1:]))

        num_series = len(headers) - 1
        values = []
        for series_idx in range(num_series):
            series_values = []
            for row in rows:
                try:
                    series_values.append(float(row[series_idx + 1]))
                except (ValueError, IndexError):
                    series_values.append(0.0)
            values.append(tuple(series_values))

        if values:
            chart_data.setData(tuple(values))
    except Exception as exc:
        warnings.warn(f"chart data population failed: {exc}", stacklevel=2)
