"""Session-based editing API for Calc spreadsheets."""

# pyright: reportMissingImports=false, reportAttributeAccessIssue=false

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from calc.core import EXPORT_FILTERS
from calc.exceptions import CalcSessionError, DocumentNotFoundError, InvalidPayloadError
from calc.targets import (
    CalcTarget,
    CellFormatting,
    ChartSpec,
    CHART_TYPES,
    ValidationRule,
    format_validation_formula,
    normalize_validation_condition,
    normalize_validation_type,
    resolve_cell_target,
    resolve_chart_target,
    resolve_named_range_target,
    resolve_range_target,
    resolve_sheet_target,
    validate_chart_spec,
    validate_formatting,
    validate_validation_rule,
)
from colors import resolve_color
from calc.patch import PatchApplyMode
from session import BaseSession
from uno_bridge import uno_context

_BOLD_WEIGHT = 150
_NORMAL_WEIGHT = 100
_ITALIC_POSTURE = 2
_NORMAL_POSTURE = 0


class CalcSession(BaseSession):
    """Long-lived Calc editing session bound to one spreadsheet."""

    def __init__(self, path: str) -> None:
        super().__init__(closed_error_type=CalcSessionError)
        self._path = Path(path)
        if not self._path.exists():
            raise DocumentNotFoundError(f"Document not found: {path}")

        self._uno_manager: Any = None
        self._desktop: Any = None
        self._doc: Any = None
        self._open_document()

    @property
    def doc(self) -> Any:
        self._require_open()
        return self._doc

    def close(self, save: bool = True) -> None:
        self._require_open()
        try:
            if save:
                self._doc.store()
            self._doc.close(save)
        finally:
            try:
                self._uno_manager.__exit__(None, None, None)
            finally:
                self._closed = True
                self._doc = None
                self._desktop = None
                self._uno_manager = None

    def reset(self) -> None:
        self._require_open()
        self._doc.close(False)
        self._uno_manager.__exit__(None, None, None)
        self._open_document()

    def read_cell(self, target: CalcTarget) -> dict[str, object]:
        self._require_open()
        return _cell_result(resolve_cell_target(target, self.doc))

    def write_cell(
        self,
        target: CalcTarget,
        value: object,
        value_type: str = "auto",
    ) -> None:
        self._require_open()
        cell = resolve_cell_target(target, self.doc)
        normalized_type = value_type.strip().lower()
        if normalized_type == "formula":
            cell.Formula = str(value)
            return
        if normalized_type == "text":
            cell.String = "" if value is None else str(value)
            return
        if normalized_type in {"date", "number"}:
            cell.Value = (
                float(cast(int | float | str, value)) if value is not None else 0.0
            )
            return
        if normalized_type != "auto":
            raise InvalidPayloadError(f"Unsupported value_type: {value_type}")
        if isinstance(value, bool):
            cell.String = str(value)
        elif isinstance(value, (int, float)):
            cell.Value = float(value)
        elif value is None:
            cell.String = ""
        else:
            cell.String = str(value)

    def read_range(self, target: CalcTarget) -> list[list[dict[str, object]]]:
        self._require_open()
        cell_range = resolve_range_target(target, self.doc)
        address = cell_range.getRangeAddress()
        rows: list[list[dict[str, object]]] = []
        for row in range(address.StartRow, address.EndRow + 1):
            row_values: list[dict[str, object]] = []
            for col in range(address.StartColumn, address.EndColumn + 1):
                row_values.append(
                    _cell_result(
                        cell_range.getCellByPosition(
                            col - address.StartColumn, row - address.StartRow
                        )
                    )
                )
            rows.append(row_values)
        return rows

    def write_range(self, target: CalcTarget, data: list[list[object]]) -> None:
        self._require_open()
        cell_range = resolve_range_target(target, self.doc)
        address = cell_range.getRangeAddress()
        expected_rows = address.EndRow - address.StartRow + 1
        expected_cols = address.EndColumn - address.StartColumn + 1
        if len(data) != expected_rows:
            raise InvalidPayloadError(
                f"Range expects {expected_rows} rows but received {len(data)}"
            )
        for row_index, row_values in enumerate(data):
            if len(row_values) != expected_cols:
                raise InvalidPayloadError(
                    f"Range row {row_index} expects {expected_cols} values but received {len(row_values)}"
                )
            for col_index, value in enumerate(row_values):
                cell = cell_range.getCellByPosition(col_index, row_index)
                if isinstance(value, bool):
                    cell.String = str(value)
                elif isinstance(value, (int, float)):
                    cell.Value = float(value)
                elif value is None:
                    cell.String = ""
                else:
                    cell.String = str(value)

    def format_range(self, target: CalcTarget, formatting: CellFormatting) -> None:
        self._require_open()
        validate_formatting(formatting)
        if target.kind == "cell":
            resolved = resolve_cell_target(target, self.doc)
        else:
            resolved = resolve_range_target(target, self.doc)
        _apply_formatting(self.doc, resolved, formatting)

    def list_sheets(self) -> list[dict[str, object]]:
        self._require_open()
        sheets = []
        for index in range(self.doc.Sheets.getCount()):
            sheet = self.doc.Sheets.getByIndex(index)
            sheets.append(
                {"name": sheet.Name, "index": index, "visible": bool(sheet.IsVisible)}
            )
        return sheets

    def add_sheet(self, name: str, index: int | None = None) -> None:
        self._require_open()
        if not name.strip():
            raise InvalidPayloadError("Sheet name cannot be empty")
        insert_index = self.doc.Sheets.getCount() if index is None else index
        self.doc.Sheets.insertNewByName(name, insert_index)

    def rename_sheet(self, target: CalcTarget, new_name: str) -> None:
        self._require_open()
        if not new_name.strip():
            raise InvalidPayloadError("new_name cannot be empty")
        sheet = resolve_sheet_target(target, self.doc)
        sheet.Name = new_name

    def delete_sheet(self, target: CalcTarget) -> None:
        self._require_open()
        sheet = resolve_sheet_target(target, self.doc)
        self.doc.Sheets.removeByName(sheet.Name)

    def define_named_range(self, name: str, target: CalcTarget) -> None:
        self._require_open()
        if not name.strip():
            raise InvalidPayloadError("Named range name cannot be empty")
        cell_range = resolve_range_target(target, self.doc)
        base_address = cell_range.getCellByPosition(0, 0).getCellAddress()
        if self.doc.NamedRanges.hasByName(name):
            self.doc.NamedRanges.removeByName(name)
        self.doc.NamedRanges.addNewByName(
            name, cell_range.AbsoluteName, base_address, 0
        )

    def get_named_range(self, target: CalcTarget) -> dict[str, object]:
        self._require_open()
        named_range = resolve_named_range_target(target, self.doc)
        return {"name": target.name, "formula": named_range.Content}

    def delete_named_range(self, target: CalcTarget) -> None:
        self._require_open()
        named_range = resolve_named_range_target(target, self.doc)
        self.doc.NamedRanges.removeByName(named_range.Name)

    def set_validation(self, target: CalcTarget, rule: ValidationRule) -> None:
        self._require_open()
        validate_validation_rule(rule)
        cell_range = resolve_range_target(target, self.doc)

        import uno

        validation = cell_range.Validation
        validation.Type = normalize_validation_type(rule.type, uno)
        validation.setOperator(normalize_validation_condition(rule.condition, uno))
        validation.setFormula1(format_validation_formula(rule.value1))
        validation.setFormula2(format_validation_formula(rule.value2))
        validation.ShowErrorMessage = rule.show_error
        validation.ErrorMessage = rule.error_message
        validation.ShowInputMessage = rule.show_input
        validation.InputTitle = rule.input_title
        validation.InputMessage = rule.input_message
        validation.IgnoreBlankCells = rule.ignore_blank
        validation.ErrorAlertStyle = int(rule.error_style)
        validation.setSourcePosition(
            cell_range.getCellByPosition(0, 0).getCellAddress()
        )
        cell_range.Validation = validation

    def clear_validation(self, target: CalcTarget) -> None:
        self._require_open()
        cell_range = resolve_range_target(target, self.doc)
        validation = cell_range.Validation
        validation.Type = 0
        validation.setFormula1("")
        validation.setFormula2("")
        validation.ShowErrorMessage = False
        validation.ErrorMessage = ""
        validation.ShowInputMessage = False
        validation.InputTitle = ""
        validation.InputMessage = ""
        validation.IgnoreBlankCells = True
        validation.ErrorAlertStyle = 0
        cell_range.Validation = validation

    def create_chart(self, target: CalcTarget, spec: ChartSpec) -> None:
        self._require_open()
        validate_chart_spec(spec)
        sheet = resolve_sheet_target(target, self.doc)
        data_range = resolve_range_target(spec.data_range, self.doc)
        charts = sheet.Charts
        base_name = spec.title or "Chart"
        chart_name = base_name
        suffix = 1
        while charts.hasByName(chart_name):
            suffix += 1
            chart_name = f"{base_name}{suffix}"
        rectangle = _rectangle_from_anchor(
            sheet,
            (spec.anchor_row, spec.anchor_col),
            (spec.width, spec.height),
        )
        range_address = data_range.getRangeAddress()
        charts.addNewByName(chart_name, rectangle, (range_address,), True, True)
        chart = charts.getByName(chart_name).EmbeddedObject
        chart.setDiagram(chart.createInstance(CHART_TYPES[spec.chart_type]))
        try:
            chart.setDataRange((range_address,))
        except Exception:
            pass
        if spec.title:
            chart.HasMainTitle = True
            chart.Title.String = spec.title

    def update_chart(self, target: CalcTarget, spec: ChartSpec) -> None:
        self._require_open()
        validate_chart_spec(spec)
        table_chart = resolve_chart_target(target, self.doc)
        data_range = resolve_range_target(spec.data_range, self.doc)
        sheet = resolve_sheet_target(
            CalcTarget(
                kind="sheet",
                sheet=spec.data_range.sheet,
                sheet_index=spec.data_range.sheet_index,
            ),
            self.doc,
        )
        rectangle = _rectangle_from_anchor(
            sheet,
            (spec.anchor_row, spec.anchor_col),
            (spec.width, spec.height),
        )
        shape = _find_chart_shape(sheet, table_chart.Name)
        shape.Position = _point_from_rectangle(rectangle)
        shape.Size = _size_from_rectangle(rectangle)
        range_address = data_range.getRangeAddress()
        try:
            table_chart.setRanges((range_address,))
        except Exception as exc:
            raise InvalidPayloadError(
                f"Failed to update chart data range: {exc}"
            ) from exc
        embedded = shape.Model
        embedded.setDiagram(embedded.createInstance(CHART_TYPES[spec.chart_type]))
        if spec.title is not None:
            embedded.HasMainTitle = True
            embedded.Title.String = spec.title

    def delete_chart(self, target: CalcTarget) -> None:
        self._require_open()
        table_chart = resolve_chart_target(target, self.doc)
        sheet = resolve_sheet_target(
            CalcTarget(
                kind="sheet", sheet=target.sheet, sheet_index=target.sheet_index
            ),
            self.doc,
        )
        sheet.Charts.removeByName(table_chart.Name)

    def recalculate(self) -> None:
        self._require_open()
        self.doc.calculate()

    def export(self, output_path: str, format: str) -> None:
        self._require_open()
        if format not in EXPORT_FILTERS:
            raise InvalidPayloadError(f"Unsupported export format: {format}")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        import uno

        filter_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        filter_prop.Name = "FilterName"
        filter_prop.Value = EXPORT_FILTERS[format]
        self.doc.storeToURL(output.resolve().as_uri(), (filter_prop,))

    def patch(self, patch_text: str, mode: PatchApplyMode = "atomic"):
        self._require_open()
        from calc.patch import apply_operations

        return apply_operations(self, patch_text, mode)

    def _open_document(self) -> None:
        self._uno_manager = uno_context()
        self._desktop = self._uno_manager.__enter__()
        try:
            self._doc = self._desktop.loadComponentFromURL(
                self._path.resolve().as_uri(),
                "_blank",
                0,
                (),
            )
        except Exception as exc:
            self._uno_manager.__exit__(type(exc), exc, exc.__traceback__)
            self._uno_manager = None
            self._desktop = None
            raise CalcSessionError(
                f"Failed to open Calc document: {self._path}"
            ) from exc


def open_calc_session(path: str) -> CalcSession:
    """Open a Calc editing session for an existing spreadsheet."""
    return CalcSession(path)


FORMULA_ERRORS = {"#DIV/0!", "#REF!", "#VALUE!", "#NAME?", "#N/A"}


def _cell_result(cell: Any) -> dict[str, object]:
    formula = cell.Formula
    if formula and formula.startswith("="):
        value = cell.Value
        raw = cell.String if cell.String in FORMULA_ERRORS else value
        error = cell.String if cell.String in FORMULA_ERRORS else None
        return {
            "value": None if error else value,
            "formula": formula,
            "error": error,
            "type": "formula",
            "raw": raw,
        }
    if cell.Type.value == "TEXT" or cell.Type.value == 2:
        return {
            "value": cell.String,
            "formula": None,
            "error": None,
            "type": "text",
            "raw": cell.String,
        }
    return {
        "value": cell.Value,
        "formula": None,
        "error": None,
        "type": "number",
        "raw": cell.Value,
    }


def _apply_formatting(doc: Any, target: Any, formatting: CellFormatting) -> None:
    if formatting.bold is not None:
        target.CharWeight = _BOLD_WEIGHT if formatting.bold else _NORMAL_WEIGHT
    if formatting.italic is not None:
        target.CharPosture = _ITALIC_POSTURE if formatting.italic else _NORMAL_POSTURE
    if formatting.font_name is not None:
        target.CharFontName = formatting.font_name
    if formatting.font_size is not None:
        target.CharHeight = float(formatting.font_size)
    if formatting.color is not None:
        target.CharColor = resolve_color(formatting.color)
    if formatting.number_format is not None:
        target.NumberFormat = _standard_number_format(doc, formatting.number_format)


def _standard_number_format(doc: Any, kind: str) -> int:
    from com.sun.star.util import NumberFormat

    formats = doc.getNumberFormats()
    locale = getattr(formats, "getLocale", lambda: doc.CharLocale)()
    mapping = {
        "currency": NumberFormat.CURRENCY,
        "percentage": NumberFormat.PERCENT,
        "date": NumberFormat.DATE,
        "time": NumberFormat.TIME,
    }
    return formats.getStandardFormat(mapping[kind], locale)


def _rectangle_from_anchor(
    sheet: Any,
    anchor: tuple[int, int],
    size: tuple[int, int],
) -> Any:
    import uno

    cell = sheet.getCellByPosition(anchor[1], anchor[0])
    pos = cell.Position
    rect = uno.createUnoStruct("com.sun.star.awt.Rectangle")
    rect.X = pos.X
    rect.Y = pos.Y
    rect.Width = int(size[0])
    rect.Height = int(size[1])
    return rect


def _find_chart_shape(sheet: Any, chart_name: str) -> Any:
    draw_page = sheet.DrawPage
    for index in range(draw_page.getCount()):
        shape = draw_page.getByIndex(index)
        if str(getattr(shape, "PersistName", "")) == chart_name:
            return shape
    raise InvalidPayloadError(f'Chart shape not found: "{chart_name}"')


def _point_from_rectangle(rectangle: Any) -> Any:
    import uno

    point = uno.createUnoStruct("com.sun.star.awt.Point")
    point.X = rectangle.X
    point.Y = rectangle.Y
    return point


def _size_from_rectangle(rectangle: Any) -> Any:
    import uno

    size = uno.createUnoStruct("com.sun.star.awt.Size")
    size.Width = rectangle.Width
    size.Height = rectangle.Height
    return size
