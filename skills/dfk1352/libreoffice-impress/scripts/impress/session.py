"""Session-based editing API for Impress presentations."""

# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

import warnings
from pathlib import Path
from collections.abc import Callable
from typing import Any, Literal, cast

from colors import resolve_color
from impress.exceptions import (
    DocumentNotFoundError,
    ImpressSessionError,
    ImpressSkillError,
    InvalidLayoutError,
    InvalidPayloadError,
    InvalidShapeError,
    MediaNotFoundError,
    TargetNoMatchError,
)
from impress.targets import (
    ImpressTarget,
    ListItem,
    ShapePlacement,
    TextFormatting,
    alignment_code,
    resolve_insertion_point,
    resolve_list_target,
    resolve_master_page_target,
    resolve_shape_target,
    resolve_slide_target,
    resolve_text_range,
    validate_formatting,
    validate_list_items,
    validate_placement,
)
from session import BaseSession
from uno_bridge import uno_context

_PARAGRAPH_BREAK = 0
_BOLD_WEIGHT = 150
_NORMAL_WEIGHT = 100
_ITALIC_POSTURE = 2
_NORMAL_POSTURE = 0
_SINGLE_UNDERLINE = 1
_NO_UNDERLINE = 0
_ORDERED_LIST_STYLE = "Numbering 123"
_UNORDERED_LIST_STYLE = "List 1"
_LAYOUT_MAP = {
    "BLANK": 20,
    "TITLE_SLIDE": 0,
    "TITLE_AND_CONTENT": 1,
    "TITLE_ONLY": 19,
    "TWO_CONTENT": 3,
    "CENTERED_TEXT": 2,
}
_SHAPE_TYPE_MAP = {
    "rectangle": "com.sun.star.drawing.RectangleShape",
    "ellipse": "com.sun.star.drawing.EllipseShape",
    "line": "com.sun.star.drawing.LineShape",
    "triangle": "com.sun.star.drawing.CustomShape",
    "arrow": "com.sun.star.drawing.CustomShape",
}
_EXPORT_FILTERS = {
    "pdf": "impress_pdf_Export",
    "pptx": "Impress MS PowerPoint 2007 XML",
}
_CHART_TYPE_MAP = {
    "bar": "com.sun.star.chart.BarDiagram",
    "line": "com.sun.star.chart.LineDiagram",
    "pie": "com.sun.star.chart.PieDiagram",
    "scatter": "com.sun.star.chart.XYDiagram",
}
_CHART_CLSID = "12DCAE26-281F-416F-a234-c3086127382e"
_TEXT_DELETE_KINDS = {"text", "notes"}
_SHAPE_DELETE_KINDS = {"shape", "image", "table", "chart", "media"}


class ImpressSession(BaseSession):
    """Long-lived Impress editing session bound to one presentation."""

    def __init__(self, path: str) -> None:
        super().__init__(closed_error_type=ImpressSessionError)
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

    def restore_snapshot(self, snapshot: bytes) -> None:
        self._require_open()
        self._doc.close(False)
        self._uno_manager.__exit__(None, None, None)
        self._path.write_bytes(snapshot)
        self._open_document()

    def get_slide_count(self) -> int:
        self._require_open()
        return int(self.doc.DrawPages.Count)

    def get_slide_inventory(self, target: ImpressTarget) -> dict[str, object]:
        self._require_open()
        slide = resolve_slide_target(target, self.doc)
        shapes = [
            _shape_summary(slide.getByIndex(index), index)
            for index in range(slide.Count)
        ]
        return {
            "slide_index": int(cast(int, target.slide_index)),
            "layout": int(slide.Layout),
            "shape_count": int(slide.Count),
            "shapes": shapes,
        }

    def add_slide(self, index: int | None = None, layout: str = "BLANK") -> None:
        self._require_open()
        if layout not in _LAYOUT_MAP:
            raise InvalidLayoutError(f"Unknown layout: {layout}")
        pages = self.doc.DrawPages
        insert_index = pages.Count if index is None else index
        if insert_index < 0 or insert_index > pages.Count:
            raise InvalidPayloadError(f"Slide index out of range: {insert_index}")
        pages.insertNewByIndex(insert_index)
        pages.getByIndex(insert_index).Layout = _LAYOUT_MAP[layout]

    def delete_slide(self, target: ImpressTarget) -> None:
        self._require_open()
        slide = resolve_slide_target(target, self.doc)
        self.doc.DrawPages.remove(slide)

    def move_slide(self, target: ImpressTarget, to_index: int) -> None:
        self._require_open()
        source_index = int(target.slide_index) if target.slide_index is not None else -1
        pages = self.doc.DrawPages
        count = pages.Count
        if source_index < 0 or source_index >= count:
            raise InvalidPayloadError(f"Slide index out of range: {source_index}")
        if to_index < 0 or to_index >= count:
            raise InvalidPayloadError(f"Slide index out of range: {to_index}")
        if source_index == to_index:
            return
        _copy_slide_to_position(self.doc, pages, source_index, to_index)

    def duplicate_slide(self, target: ImpressTarget) -> None:
        self._require_open()
        pages = self.doc.DrawPages
        source_index = int(target.slide_index) if target.slide_index is not None else -1
        if source_index < 0 or source_index >= pages.Count:
            raise InvalidPayloadError(f"Slide index out of range: {source_index}")
        self.doc.duplicate(pages.getByIndex(source_index))

    def read_text(self, target: ImpressTarget) -> str:
        self._require_open()
        return resolve_text_range(target, self.doc).getString()

    def insert_text(self, text: str, target: ImpressTarget | None = None) -> None:
        self._require_open()
        cursor = resolve_insertion_point(target, self.doc)
        _insert_string(cursor.getText(), cursor, text)

    def replace_text(self, target: ImpressTarget, new_text: str) -> None:
        self._require_open()
        resolve_text_range(target, self.doc).setString(new_text)

    def format_text(self, target: ImpressTarget, formatting: TextFormatting) -> None:
        self._require_open()
        validate_formatting(formatting)
        _apply_text_formatting(resolve_text_range(target, self.doc), formatting)

    def insert_list(
        self,
        items: list[ListItem],
        ordered: bool,
        target: ImpressTarget | None = None,
    ) -> None:
        self._require_open()
        validate_list_items(items)
        cursor = resolve_insertion_point(target, self.doc)
        _insert_list_at_cursor(cursor.getText(), cursor, items, ordered)
        self.doc.store()
        self.reset()

    def replace_list(
        self,
        target: ImpressTarget,
        items: list[ListItem],
        ordered: bool | None = None,
    ) -> None:
        self._require_open()
        validate_list_items(items)
        paragraphs = resolve_list_target(target, self.doc)
        ordered_value = _list_is_ordered(paragraphs) if ordered is None else ordered
        _rewrite_list_block(target, paragraphs, items, ordered_value, self.doc)
        self.doc.store()
        self.reset()

    def insert_text_box(
        self,
        slide: ImpressTarget,
        text: str,
        placement: ShapePlacement,
        name: str | None = None,
    ) -> None:
        self._require_open()
        validate_placement(placement)
        page = resolve_slide_target(slide, self.doc)
        shape = self.doc.createInstance("com.sun.star.drawing.TextShape")
        _set_shape_geometry(shape, placement)
        page.add(shape)
        shape.setString(text)
        if name is not None:
            _assign_shape_name(shape, name)

    def insert_shape(
        self,
        slide: ImpressTarget,
        shape_type: str,
        placement: ShapePlacement,
        fill_color: int | str | None = None,
        line_color: int | str | None = None,
        name: str | None = None,
    ) -> None:
        self._require_open()
        validate_placement(placement)
        if shape_type not in _SHAPE_TYPE_MAP:
            raise InvalidShapeError(f"Unknown shape type: {shape_type}")
        page = resolve_slide_target(slide, self.doc)
        shape = self.doc.createInstance(_SHAPE_TYPE_MAP[shape_type])
        _set_shape_geometry(shape, placement)
        page.add(shape)
        if shape_type == "triangle":
            _set_custom_shape_geometry(shape, "isosceles-triangle")
        elif shape_type == "arrow":
            _set_custom_shape_geometry(shape, "right-arrow")
        if fill_color is not None:
            shape.FillStyle = 1
            shape.FillColor = resolve_color(fill_color)
        if line_color is not None:
            shape.LineColor = resolve_color(line_color)
        if name is not None:
            _assign_shape_name(shape, name)

    def delete_item(self, target: ImpressTarget) -> None:
        self._require_open()
        if target.kind in _TEXT_DELETE_KINDS:
            resolve_text_range(target, self.doc).setString("")
            return
        if target.kind == "list":
            _rewrite_list_block(
                target, resolve_list_target(target, self.doc), [], False, self.doc
            )
            self.doc.store()
            self.reset()
            return
        if target.kind in _SHAPE_DELETE_KINDS:
            _delete_shape_like_target(self, target)
            return
        raise InvalidPayloadError(
            "delete_item requires a text, notes, list, shape, image, table, chart, or media target"
        )

    def insert_image(
        self,
        slide: ImpressTarget,
        image_path: str,
        placement: ShapePlacement,
        name: str | None = None,
    ) -> None:
        self._require_open()
        validate_placement(placement)
        image_file = Path(image_path)
        if not image_file.exists():
            raise MediaNotFoundError(f"Image not found: {image_path}")
        page = resolve_slide_target(slide, self.doc)
        _insert_image_shape(
            self.doc,
            page,
            image_file.resolve().as_uri(),
            placement,
            name=name,
        )

    def replace_image(
        self,
        target: ImpressTarget,
        image_path: str | None = None,
        placement: ShapePlacement | None = None,
    ) -> None:
        self._require_open()
        if image_path is None and placement is None:
            raise InvalidPayloadError(
                "replace_image requires image_path and/or placement"
            )
        _replace_url_backed_shape(
            self,
            target=target,
            asset_path=image_path,
            placement=placement,
            current_url_getter=_image_url_from_shape,
            shape_inserter=_insert_image_shape,
            missing_error_label="Image",
        )

    def insert_table(
        self,
        slide: ImpressTarget,
        rows: int,
        cols: int,
        placement: ShapePlacement,
        data: list[list[str]] | None = None,
        name: str | None = None,
    ) -> None:
        self._require_open()
        validate_placement(placement)
        if rows < 1 or cols < 1:
            raise InvalidPayloadError("rows and cols must be >= 1")
        page = resolve_slide_target(slide, self.doc)
        _insert_table_shape(
            self.doc,
            page,
            rows,
            cols,
            placement,
            data=data,
            name=name,
        )

    def update_table(self, target: ImpressTarget, data: list[list[str]]) -> None:
        self._require_open()
        model = _resolve_table_model(target, self.doc)
        if model is None:
            self.doc.store()
            self.reset()
            model = _resolve_table_model(target, self.doc)
        if model is None:
            raise InvalidPayloadError("Table model is unavailable after reopen")
        if len(data) != model.Rows.Count:
            raise InvalidPayloadError(
                f"Table expects {model.Rows.Count} rows but received {len(data)}"
            )
        for row_index, row in enumerate(data):
            if len(row) != model.Columns.Count:
                raise InvalidPayloadError(
                    f"Table row {row_index} expects {model.Columns.Count} values but received {len(row)}"
                )
        _write_table_data(model, data)
        self.doc.store()

    def insert_chart(
        self,
        slide: ImpressTarget,
        chart_type: str,
        data: list[list[object]],
        placement: ShapePlacement,
        title: str | None = None,
        name: str | None = None,
    ) -> None:
        self._require_open()
        validate_placement(placement)
        if chart_type not in _CHART_TYPE_MAP:
            raise InvalidPayloadError(f"Unsupported chart type: {chart_type}")
        page = resolve_slide_target(slide, self.doc)
        _insert_chart_shape(
            self.doc,
            page,
            chart_type,
            data,
            placement,
            title=title,
            name=name,
        )

    def update_chart(
        self,
        target: ImpressTarget,
        chart_type: str | None = None,
        data: list[list[object]] | None = None,
        placement: ShapePlacement | None = None,
        title: str | None = None,
    ) -> None:
        self._require_open()
        if not any(value is not None for value in (chart_type, data, placement, title)):
            raise InvalidPayloadError(
                "update_chart requires chart_type, data, placement, or title"
            )
        shape = resolve_shape_target(target, self.doc)
        if placement is not None:
            validate_placement(placement)
            _set_shape_geometry(shape, placement)
        _update_chart_shape(shape, chart_type=chart_type, data=data, title=title)
        self.doc.store()
        self.reset()
        if (
            chart_type is not None
            or data is not None
            or title is not None
            or placement is not None
        ):
            shape = resolve_shape_target(target, self.doc)
            if placement is not None:
                _set_shape_geometry(shape, placement)
            _update_chart_shape(shape, chart_type=chart_type, data=data, title=title)
            self.doc.store()

    def insert_media(
        self,
        slide: ImpressTarget,
        media_path: str,
        placement: ShapePlacement,
        name: str | None = None,
    ) -> None:
        self._require_open()
        validate_placement(placement)
        media_file = Path(media_path)
        if not media_file.exists():
            raise MediaNotFoundError(f"Media not found: {media_path}")
        page = resolve_slide_target(slide, self.doc)
        _insert_media_shape(
            self.doc,
            page,
            media_file.resolve().as_uri(),
            placement,
            name=name,
        )

    def replace_media(
        self,
        target: ImpressTarget,
        media_path: str | None = None,
        placement: ShapePlacement | None = None,
    ) -> None:
        self._require_open()
        if media_path is None and placement is None:
            raise InvalidPayloadError(
                "replace_media requires media_path and/or placement"
            )
        _replace_url_backed_shape(
            self,
            target=target,
            asset_path=media_path,
            placement=placement,
            current_url_getter=_media_url_from_shape,
            shape_inserter=_insert_media_shape,
            missing_error_label="Media",
        )

    def set_notes(self, target: ImpressTarget, text: str) -> None:
        self._require_open()
        resolve_text_range(target, self.doc).setString(text)

    def get_notes(self, target: ImpressTarget) -> str:
        self._require_open()
        return resolve_text_range(target, self.doc).getString()

    def list_master_pages(self) -> list[str]:
        self._require_open()
        masters = self.doc.MasterPages
        return [str(masters.getByIndex(index).Name) for index in range(masters.Count)]

    def apply_master_page(
        self, target: ImpressTarget, master_target: ImpressTarget
    ) -> None:
        self._require_open()
        master_page = resolve_master_page_target(master_target, self.doc)
        slide = resolve_slide_target(target, self.doc)
        slide.MasterPage = master_page

    def set_master_background(self, target: ImpressTarget, color: int | str) -> None:
        self._require_open()
        master_page = resolve_master_page_target(target, self.doc)
        background = self.doc.createInstance("com.sun.star.drawing.Background")
        background.FillStyle = 1
        background.FillColor = resolve_color(color)
        master_page.Background = background

    def import_master_page(self, template_path: str) -> str:
        self._require_open()
        template_file = Path(template_path)
        if not template_file.exists():
            raise DocumentNotFoundError(f"Template not found: {template_path}")
        template_doc = self._desktop.loadComponentFromURL(
            template_file.resolve().as_uri(),
            "_blank",
            0,
            (),
        )
        try:
            imported_name = str(template_doc.MasterPages.getByIndex(0).Name)
        finally:
            template_doc.close(True)
        masters = self.doc.MasterPages
        for index in range(masters.Count):
            if str(masters.getByIndex(index).Name) == imported_name:
                return imported_name
        new_master = masters.insertNewByIndex(masters.Count)
        new_master.Name = imported_name
        return imported_name

    def export(self, output_path: str, format: str) -> None:
        self._require_open()
        if format not in _EXPORT_FILTERS:
            raise ImpressSkillError(f"Unsupported export format: {format}")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        import uno  # type: ignore[import-not-found]

        filter_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        filter_prop.Name = "FilterName"
        filter_prop.Value = _EXPORT_FILTERS[format]
        self.doc.storeToURL(output.resolve().as_uri(), (filter_prop,))

    def patch(
        self,
        patch_text: str,
        mode: Literal["atomic", "best_effort"] = "atomic",
    ):
        self._require_open()
        from impress.patch import apply_operations

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
            raise ImpressSkillError(
                f"Failed to open Impress document: {self._path}"
            ) from exc


def open_impress_session(path: str) -> ImpressSession:
    """Open an Impress editing session for an existing presentation."""
    return ImpressSession(path)


def _shape_summary(shape: Any, index: int) -> dict[str, object]:
    text = ""
    try:
        if bool(shape.supportsService("com.sun.star.drawing.Text")):
            text = str(shape.getString())
    except Exception:
        text = ""
    return {
        "index": index,
        "name": _shape_name(shape),
        "type": str(getattr(shape, "ShapeType", "")),
        "text": text,
        "x_cm": int(getattr(shape.Position, "X", 0)) / 1000.0,
        "y_cm": int(getattr(shape.Position, "Y", 0)) / 1000.0,
        "width_cm": int(getattr(shape.Size, "Width", 0)) / 1000.0,
        "height_cm": int(getattr(shape.Size, "Height", 0)) / 1000.0,
    }


def _insert_string(text_obj: Any, cursor: Any, text: str) -> None:
    parts = text.split("\n")
    for index, part in enumerate(parts):
        if index > 0:
            text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)
        if part:
            text_obj.insertString(cursor, part, False)


def _apply_text_formatting(text_range: Any, formatting: TextFormatting) -> None:
    if formatting.bold is not None:
        text_range.CharWeight = _BOLD_WEIGHT if formatting.bold else _NORMAL_WEIGHT
    if formatting.italic is not None:
        text_range.CharPosture = (
            _ITALIC_POSTURE if formatting.italic else _NORMAL_POSTURE
        )
    if formatting.underline is not None:
        text_range.CharUnderline = (
            _SINGLE_UNDERLINE if formatting.underline else _NO_UNDERLINE
        )
    if formatting.font_name is not None:
        text_range.CharFontName = formatting.font_name
    if formatting.font_size is not None:
        text_range.CharHeight = float(formatting.font_size)
    if formatting.color is not None:
        text_range.CharColor = resolve_color(formatting.color)
    if formatting.align is not None:
        text_range.ParaAdjust = alignment_code(formatting.align)


def _insert_list_at_cursor(
    text_obj: Any, cursor: Any, items: list[ListItem], ordered: bool
) -> None:
    if _cursor_has_text_before(cursor):
        text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)
    for index, item in enumerate(items):
        start = cursor.getStart()
        text_obj.insertString(
            cursor,
            item.text,
            False,
        )
        paragraph_cursor = text_obj.createTextCursorByRange(start)
        paragraph_cursor.gotoRange(cursor.getEnd(), True)
        _apply_list_style(paragraph_cursor, int(item.level), ordered)
        if index < len(items) - 1:
            text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)


def _cursor_has_text_before(cursor: Any) -> bool:
    probe = cursor.getText().createTextCursorByRange(cursor.getStart())
    probe.gotoStart(True)
    return bool(probe.getString())


def _list_is_ordered(paragraphs: list[Any]) -> bool:
    if not paragraphs:
        return False
    paragraph_cursor = _paragraph_cursor(paragraphs[0])
    rules = getattr(paragraph_cursor, "NumberingRules", None)
    if rules is None:
        return False
    level = int(getattr(paragraph_cursor, "NumberingLevel", 0))
    try:
        properties = rules.getByIndex(level)
    except Exception:
        properties = rules.getByIndex(0)
    for property_value in properties:
        if getattr(property_value, "Name", None) == "NumberingType":
            try:
                return int(property_value.Value) == 4
            except Exception:
                return False
    return False


def _apply_list_style(paragraph_cursor: Any, level: int, ordered: bool) -> None:
    style_name = _ORDERED_LIST_STYLE if ordered else _UNORDERED_LIST_STYLE
    try:
        paragraph_cursor.NumberingStyleName = style_name
    except Exception:
        pass
    paragraph_cursor.NumberingLevel = int(level)
    try:
        paragraph_cursor.NumberingIsNumber = ordered
    except Exception:
        pass


def _rewrite_list_block(
    target: ImpressTarget,
    paragraphs: list[Any],
    items: list[ListItem],
    ordered: bool,
    doc: Any,
) -> None:
    shape = resolve_shape_target(target, doc)
    text_obj = shape.getText()
    all_paragraphs = _enumerate_paragraphs(text_obj)
    group_positions = {
        _cursor_index(text_obj, paragraph.getStart()) for paragraph in paragraphs
    }
    group_indices = [
        index
        for index, paragraph in enumerate(all_paragraphs)
        if _cursor_index(text_obj, paragraph.getStart()) in group_positions
    ]
    if not group_indices:
        raise InvalidPayloadError("List block could not be rewritten")

    first_index = min(group_indices)
    last_index = max(group_indices)
    prefix = [paragraph.getString() for paragraph in all_paragraphs[:first_index]]
    suffix = [paragraph.getString() for paragraph in all_paragraphs[last_index + 1 :]]
    replacement = [item.text for item in items]
    rebuilt = prefix + replacement + suffix
    shape.setString("\n".join(rebuilt))

    if not items:
        return

    rewritten_paragraphs = _enumerate_paragraphs(shape.getText())
    start_index = len(prefix)
    for offset, item in enumerate(items):
        paragraph_cursor = _paragraph_cursor(rewritten_paragraphs[start_index + offset])
        _apply_list_style(paragraph_cursor, int(item.level), ordered)


def _write_table_data(model: Any, data: list[list[str]]) -> None:
    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            model.getCellByPosition(col_index, row_index).setString(str(value))


def _resolve_table_model(target: ImpressTarget, doc: Any) -> Any | None:
    shape = resolve_shape_target(target, doc)
    model = getattr(shape, "Model", None)
    if model is not None:
        return model
    if target.shape_name is None:
        return None
    slide = resolve_slide_target(target, doc)
    normalized_target = "_".join(target.shape_name.split()).lower()
    for index in range(slide.Count):
        candidate = slide.getByIndex(index)
        candidate_name = _shape_name(candidate)
        if "_".join(candidate_name.split()).lower() != normalized_target:
            continue
        candidate_model = getattr(candidate, "Model", None)
        if candidate_model is not None:
            return candidate_model
    return None


def _set_table_column_widths(model: Any, total_width: int, cols: int) -> None:
    if cols <= 0:
        return
    base_width = max(total_width // cols, 1)
    remainder = max(total_width - (base_width * cols), 0)
    for index in range(cols):
        width = base_width + (remainder if index == cols - 1 else 0)
        try:
            model.Columns.getByIndex(index).Width = width
        except Exception:
            return


def _insert_image_shape(
    doc: Any,
    page: Any,
    image_url: str,
    placement: ShapePlacement,
    *,
    name: str | None,
) -> Any:
    shape = doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
    _set_shape_geometry(shape, placement)
    page.add(shape)
    shape.GraphicURL = image_url
    try:
        shape.Description = image_url
    except Exception:
        pass
    if name is not None:
        _assign_shape_name(shape, name)
    return shape


def _insert_table_shape(
    doc: Any,
    page: Any,
    rows: int,
    cols: int,
    placement: ShapePlacement,
    *,
    data: list[list[str]] | None,
    name: str | None,
) -> Any:
    shape = doc.createInstance("com.sun.star.drawing.TableShape")
    _set_shape_geometry(shape, placement)
    page.add(shape)
    model = shape.Model
    if rows > 1:
        model.Rows.insertByIndex(1, rows - 1)
    if cols > 1:
        model.Columns.insertByIndex(1, cols - 1)
    _set_table_column_widths(model, int(placement.width_cm * 1000), cols)
    if data is not None:
        _write_table_data(model, data)
    if name is not None:
        _assign_shape_name(shape, name)
    return shape


def _insert_chart_shape(
    doc: Any,
    page: Any,
    chart_type: str,
    data: list[list[object]],
    placement: ShapePlacement,
    *,
    title: str | None,
    name: str | None,
) -> Any:
    shape = doc.createInstance("com.sun.star.drawing.OLE2Shape")
    _set_shape_geometry(shape, placement)
    shape.CLSID = _CHART_CLSID
    page.add(shape)
    if name is not None:
        _assign_shape_name(shape, name)
    _update_chart_shape(shape, chart_type=chart_type, data=data, title=title)
    return shape


def _insert_media_shape(
    doc: Any,
    page: Any,
    media_url: str,
    placement: ShapePlacement,
    *,
    name: str | None,
) -> Any:
    try:
        shape = doc.createInstance("com.sun.star.presentation.MediaShape")
    except Exception as exc:
        warnings.warn(f"media shape creation fallback triggered: {exc}", stacklevel=2)
        shape = doc.createInstance("com.sun.star.drawing.PluginShape")
    _set_shape_geometry(shape, placement)
    page.add(shape)
    _set_media_url(shape, media_url)
    if name is not None:
        _assign_shape_name(shape, name)
    return shape


def _update_chart_shape(
    shape: Any,
    *,
    chart_type: str | None,
    data: list[list[object]] | None,
    title: str | None,
) -> None:
    embedded_object = getattr(shape, "EmbeddedObject", None)
    chart_doc = embedded_object.Component if embedded_object is not None else None
    if chart_doc is None:
        return
    if chart_type is not None:
        if chart_type not in _CHART_TYPE_MAP:
            raise InvalidPayloadError(f"Unsupported chart type: {chart_type}")
        chart_doc.setDiagram(chart_doc.createInstance(_CHART_TYPE_MAP[chart_type]))
    if data:
        try:
            chart_data = chart_doc.getData()
            if chart_data is not None and len(data) > 1:
                _populate_chart_data(chart_doc, chart_data, data, chart_type)
        except Exception as exc:
            warnings.warn(f"chart data population failed: {exc}", stacklevel=2)
    if title is not None:
        try:
            chart_doc.HasMainTitle = True
            chart_doc.Title.String = title
        except Exception as exc:
            warnings.warn(f"chart title assignment failed: {exc}", stacklevel=2)


def _set_media_url(shape: Any, media_url: str) -> None:
    try:
        shape.MediaURL = media_url
        return
    except Exception:
        pass
    try:
        shape.PluginURL = media_url
        return
    except Exception as exc:
        raise InvalidPayloadError(f"Failed to assign media URL: {exc}") from exc


def _populate_chart_data(
    chart_doc: Any,
    chart_data: Any,
    data: list[list[object]],
    chart_type: str | None,
) -> None:
    headers = data[0]
    rows = data[1:]
    if not rows:
        return

    if chart_type == "line":
        chart_data.setColumnDescriptions(tuple(str(row[0]) for row in rows))
        chart_data.setRowDescriptions(
            (str(headers[1]) if len(headers) > 1 else "Value",)
        )
        chart_data.setData(
            (
                tuple(
                    float(cast(float | int | str, row[1])) if len(row) > 1 else 0.0
                    for row in rows
                ),
            )
        )
        try:
            diagram = chart_doc.getDiagram()
            diagram.DataRowSource = _chart_row_source("ROWS")
            diagram.SymbolType = 0
        except Exception:
            pass
        return

    chart_data.setColumnDescriptions(tuple(str(row[0]) for row in rows))
    if len(headers) > 1:
        chart_data.setRowDescriptions(tuple(str(value) for value in headers[1:]))
    values = []
    for series_index in range(max(len(headers) - 1, 0)):
        series_values = []
        for row in rows:
            try:
                series_values.append(
                    float(cast(float | int | str, row[series_index + 1]))
                )
            except (TypeError, ValueError, IndexError):
                series_values.append(0.0)
        values.append(tuple(series_values))
    if values:
        chart_data.setData(tuple(values))
    try:
        diagram = chart_doc.getDiagram()
        diagram.DataRowSource = _chart_row_source("COLUMNS")
    except Exception:
        pass


def _chart_row_source(value: Literal["ROWS", "COLUMNS"]) -> Any:
    import uno  # type: ignore[import-not-found]

    return uno.Enum("com.sun.star.chart.ChartDataRowSource", value)


def _placement_from_shape(shape: Any) -> ShapePlacement:
    return ShapePlacement(
        x_cm=int(shape.Position.X) / 1000.0,
        y_cm=int(shape.Position.Y) / 1000.0,
        width_cm=int(shape.Size.Width) / 1000.0,
        height_cm=int(shape.Size.Height) / 1000.0,
    )


def _replace_url_backed_shape(
    session: ImpressSession,
    *,
    target: ImpressTarget,
    asset_path: str | None,
    placement: ShapePlacement | None,
    current_url_getter: Callable[[Any], str],
    shape_inserter: Callable[..., Any],
    missing_error_label: str,
) -> None:
    shape = resolve_shape_target(target, session.doc)
    shape_name = _shape_name(shape) or target.shape_name
    current_placement = _placement_from_shape(shape)
    next_url = current_url_getter(shape) if asset_path is None else ""
    if asset_path is not None:
        asset_file = Path(asset_path)
        if not asset_file.exists():
            raise MediaNotFoundError(f"{missing_error_label} not found: {asset_path}")
        next_url = asset_file.resolve().as_uri()
    next_placement = current_placement if placement is None else placement
    validate_placement(next_placement)
    slide = resolve_slide_target(target, session.doc)
    normalized_name = "_".join(shape_name.split()).lower() if shape_name else None
    if normalized_name:
        _remove_named_shapes(slide, normalized_name)
    else:
        _remove_shape_from_slide(slide, shape)
    session.doc.store()
    session.reset()
    slide = resolve_slide_target(target, session.doc)
    new_shape = shape_inserter(
        session.doc,
        slide,
        next_url,
        next_placement,
        name=shape_name or None,
    )
    _set_shape_geometry(new_shape, next_placement)
    session.doc.store()


def _image_url_from_shape(shape: Any) -> str:
    description = getattr(shape, "Description", "")
    if description:
        return str(description)
    for attribute in ("GraphicStreamURL",):
        value = getattr(shape, attribute, "")
        if value:
            return str(value)
    graphic = getattr(shape, "Graphic", None)
    if graphic is not None:
        for attribute in ("OriginURL", "URL"):
            value = getattr(graphic, attribute, "")
            if value:
                return str(value)
    raise InvalidPayloadError("Image shape does not expose a persisted source URL")


def _remove_shape_from_slide(slide: Any, shape: Any) -> None:
    removed = False
    for index in range(slide.Count - 1, -1, -1):
        candidate = slide.getByIndex(index)
        if candidate == shape:
            slide.remove(candidate)
            removed = True
            break
    if not removed:
        slide.remove(shape)


def _remove_named_shapes(slide: Any, normalized_name: str) -> bool:
    removed_any = False
    for index in range(slide.Count - 1, -1, -1):
        candidate = slide.getByIndex(index)
        candidate_name = _shape_name(candidate)
        if "_".join(candidate_name.split()).lower() != normalized_name:
            continue
        slide.remove(candidate)
        removed_any = True
    return removed_any


def _delete_shape_like_target(session: ImpressSession, target: ImpressTarget) -> None:
    slide = resolve_slide_target(target, session.doc)
    normalized_name = (
        "_".join(cast(str, target.shape_name).split()).lower()
        if target.shape_name is not None
        else None
    )
    if normalized_name is None:
        _remove_shape_from_slide(slide, resolve_shape_target(target, session.doc))
        session.doc.store()
        session.reset()
        return

    removed_once = False
    while True:
        removed_any = False
        for index in range(slide.Count - 1, -1, -1):
            candidate = slide.getByIndex(index)
            candidate_name = _shape_name(candidate)
            if "_".join(candidate_name.split()).lower() != normalized_name:
                continue
            slide.remove(candidate)
            removed_any = True
            removed_once = True
        session.doc.store()
        session.reset()
        slide = resolve_slide_target(target, session.doc)
        if not removed_any:
            break
    if not removed_once:
        raise TargetNoMatchError(f'Shape not found: "{target.shape_name}"')


def _copy_slide_to_position(doc: Any, pages: Any, src_idx: int, dst_idx: int) -> None:
    source = pages.getByIndex(src_idx)
    layout = source.Layout
    master = source.MasterPage
    if dst_idx < src_idx:
        insert_at = dst_idx
        actual_src = src_idx + 1
    else:
        insert_at = dst_idx + 1
        actual_src = src_idx
    pages.insertNewByIndex(insert_at)
    target = pages.getByIndex(insert_at)
    target.Layout = layout
    target.MasterPage = master

    source = pages.getByIndex(actual_src)
    object_names = _slide_object_names(source)
    _copy_slide_contents(doc, source, target)
    _restore_slide_object_names(target, object_names)
    pages.remove(source)


def _slide_object_names(slide: Any) -> list[str]:
    names: list[str] = []
    for index in range(slide.Count):
        shape = slide.getByIndex(index)
        if _is_placeholder_shape(shape):
            continue
        names.append(_shape_name(shape))
    return names


def _restore_slide_object_names(slide: Any, expected_names: list[str]) -> None:
    object_index = 0
    for index in range(slide.Count):
        shape = slide.getByIndex(index)
        if _is_placeholder_shape(shape):
            continue
        if object_index >= len(expected_names):
            return
        expected_name = expected_names[object_index]
        if expected_name:
            _assign_shape_name(shape, expected_name)
        object_index += 1


def _copy_slide_contents(doc: Any, source: Any, target: Any) -> None:
    for index in range(source.Count):
        src_shape = source.getByIndex(index)
        if _is_placeholder_shape(src_shape):
            continue
        _copy_shape_to_slide(doc, target, src_shape)


def _copy_shape_to_slide(doc: Any, target: Any, src_shape: Any) -> None:
    shape_type = str(getattr(src_shape, "ShapeType", ""))
    placement = _placement_from_shape(src_shape)
    name = _shape_name(src_shape) or None
    if shape_type == "com.sun.star.drawing.GraphicObjectShape":
        _insert_image_shape(
            doc,
            target,
            _image_url_from_shape(src_shape),
            placement,
            name=name,
        )
        return
    if shape_type == "com.sun.star.drawing.TableShape":
        rows, cols, data = _table_payload_from_shape(src_shape)
        _insert_table_shape(
            doc,
            target,
            rows,
            cols,
            placement,
            data=data,
            name=name,
        )
        return
    if shape_type == "com.sun.star.drawing.OLE2Shape":
        _insert_chart_shape(
            doc,
            target,
            _chart_type_from_shape(src_shape),
            _chart_data_from_shape(src_shape),
            placement,
            title=_chart_title_from_shape(src_shape),
            name=name,
        )
        return
    if shape_type in {
        "com.sun.star.presentation.MediaShape",
        "com.sun.star.drawing.PluginShape",
    }:
        _insert_media_shape(
            doc,
            target,
            _media_url_from_shape(src_shape),
            placement,
            name=name,
        )
        return

    new_shape = doc.createInstance(shape_type)
    new_shape.Position = src_shape.Position
    new_shape.Size = src_shape.Size
    target.add(new_shape)
    if name is not None:
        _assign_shape_name(new_shape, name)
    for attribute in ("FillStyle", "FillColor", "LineColor"):
        try:
            setattr(new_shape, attribute, getattr(src_shape, attribute))
        except Exception:
            pass
    try:
        new_shape.CustomShapeGeometry = src_shape.CustomShapeGeometry
    except Exception:
        pass
    try:
        new_shape.setString(src_shape.getString())
    except Exception:
        pass


def _table_payload_from_shape(shape: Any) -> tuple[int, int, list[list[str]]]:
    model = getattr(shape, "Model", None)
    if model is None:
        raise InvalidPayloadError("Table model is unavailable for slide copy")
    rows = int(model.Rows.Count)
    cols = int(model.Columns.Count)
    data = [
        [str(model.getCellByPosition(col, row).getString()) for col in range(cols)]
        for row in range(rows)
    ]
    return rows, cols, data


def _chart_title_from_shape(shape: Any) -> str | None:
    embedded_object = getattr(shape, "EmbeddedObject", None)
    chart_doc = embedded_object.Component if embedded_object is not None else None
    if chart_doc is None:
        return None
    try:
        if getattr(chart_doc, "HasMainTitle", False):
            return str(chart_doc.Title.String)
    except Exception:
        return None
    return None


def _chart_type_from_shape(shape: Any) -> str:
    embedded_object = getattr(shape, "EmbeddedObject", None)
    chart_doc = embedded_object.Component if embedded_object is not None else None
    if chart_doc is None:
        return "bar"
    try:
        diagram = chart_doc.getDiagram()
        if diagram.supportsService("com.sun.star.chart.LineDiagram"):
            return "line"
        if diagram.supportsService("com.sun.star.chart.PieDiagram"):
            return "pie"
        if diagram.supportsService("com.sun.star.chart.XYDiagram"):
            return "scatter"
    except Exception:
        return "bar"
    return "bar"


def _chart_data_from_shape(shape: Any) -> list[list[object]]:
    title = _chart_title_from_shape(shape) or "Value"
    return [["Category", "Value"], [title, 1]]


def _media_url_from_shape(shape: Any) -> str:
    for attribute in ("MediaURL", "PluginURL", "Description"):
        value = getattr(shape, attribute, "")
        if value:
            return str(value)
    raise InvalidPayloadError("Media shape does not expose a persisted source URL")


def _set_shape_geometry(shape: Any, placement: ShapePlacement) -> None:
    import uno  # type: ignore[import-not-found]

    position = uno.createUnoStruct("com.sun.star.awt.Point")
    position.X = int(placement.x_cm * 1000)
    position.Y = int(placement.y_cm * 1000)
    shape.Position = position
    size = uno.createUnoStruct("com.sun.star.awt.Size")
    size.Width = int(placement.width_cm * 1000)
    size.Height = int(placement.height_cm * 1000)
    shape.Size = size


def _set_custom_shape_geometry(shape: Any, preset_type: str) -> None:
    import uno  # type: ignore[import-not-found]

    geom = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    geom.Name = "Type"
    geom.Value = "non-primitive"
    geom2 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    geom2.Name = "ViewBox"
    rect = uno.createUnoStruct("com.sun.star.awt.Rectangle")
    rect.X = 0
    rect.Y = 0
    rect.Width = 21600
    rect.Height = 21600
    geom2.Value = rect
    geom3 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    geom3.Name = "Coordinates"
    if preset_type == "isosceles-triangle":
        points = [(10800, 0), (21600, 21600), (0, 21600)]
    else:
        points = [
            (0, 5400),
            (16200, 5400),
            (16200, 0),
            (21600, 10800),
            (16200, 21600),
            (16200, 16200),
            (0, 16200),
        ]
    pairs = []
    for x_value, y_value in points:
        pair = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        pair.First.Value = x_value
        pair.First.Type = 0
        pair.Second.Value = y_value
        pair.Second.Type = 0
        pairs.append(pair)
    geom3.Value = tuple(pairs)
    shape.CustomShapeGeometry = (geom, geom2, geom3)


def _assign_shape_name(shape: Any, name: str) -> None:
    normalized = "_".join(name.split())
    candidates = [normalized]
    if name and normalized != name:
        candidates.append(name)
    for candidate in candidates:
        if hasattr(shape, "setName"):
            try:
                shape.setName(candidate)
                return
            except Exception:
                pass
        try:
            shape.Name = candidate
            return
        except Exception:
            pass


def _shape_name(shape: Any) -> str:
    if hasattr(shape, "getName"):
        try:
            return str(shape.getName())
        except Exception:
            pass
    return str(getattr(shape, "Name", ""))


def _is_placeholder_shape(shape: Any) -> bool:
    if not bool(getattr(shape, "IsPresentationObject", False)):
        return False
    shape_type = str(getattr(shape, "ShapeType", ""))
    return not shape_type.endswith("MediaShape")


def _paragraph_cursor(paragraph: Any) -> Any:
    text_obj = paragraph.getText()
    cursor = text_obj.createTextCursorByRange(paragraph.getStart())
    cursor.gotoRange(paragraph.getEnd(), True)
    return cursor


def _enumerate_paragraphs(text_obj: Any) -> list[Any]:
    enumeration = text_obj.createEnumeration()
    paragraphs: list[Any] = []
    while enumeration.hasMoreElements():
        paragraphs.append(enumeration.nextElement())
    return paragraphs


def _cursor_index(text_obj: Any, position: Any) -> int:
    cursor = text_obj.createTextCursor()
    cursor.gotoStart(False)
    cursor.gotoRange(position, True)
    return len(cursor.getString())
