"""Session-based editing API for Writer documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from colors import resolve_color
from session import BaseSession
from uno_bridge import uno_context
from writer.core import EXPORT_FILTERS
from writer.exceptions import (
    DocumentNotFoundError,
    ImageNotFoundError,
    WriterSessionError,
    WriterSkillError,
)
from writer.patch import PatchApplyMode
from writer.targets import (
    ListItem,
    TextFormatting,
    WriterTarget,
    resolve_image_target,
    resolve_insertion_point,
    resolve_list_target,
    resolve_table_target,
    resolve_text_range,
    validate_formatting,
    validate_image_update,
    validate_list_items,
    validate_table_data,
)

_PARAGRAPH_BREAK = 0
_BOLD_WEIGHT = 150
_NORMAL_WEIGHT = 100
_ITALIC_POSTURE = 2
_NORMAL_POSTURE = 0
_SINGLE_UNDERLINE = 1
_NO_UNDERLINE = 0
_ALIGNMENT_MAP = {
    "left": 0,
    "right": 1,
    "center": 2,
    "justify": 3,
}
_ORDERED_LIST_STYLE = "Numbering 123"
_UNORDERED_LIST_STYLE = "List 1"


class WriterSession(BaseSession):
    """Long-lived Writer editing session bound to one document."""

    def __init__(self, path: str) -> None:
        super().__init__(closed_error_type=WriterSessionError)
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

    def read_text(self, target: WriterTarget | None = None) -> str:
        self._require_open()
        if target is None:
            return self.doc.Text.getString()
        return resolve_text_range(target, self.doc).getString()

    def insert_text(self, text: str, target: WriterTarget | None = None) -> None:
        self._require_open()
        cursor = resolve_insertion_point(target, self.doc)
        _insert_string(self.doc.Text, cursor, text)

    def replace_text(self, target: WriterTarget, new_text: str) -> None:
        self._require_open()
        match = resolve_text_range(target, self.doc)
        match.setString(new_text)

    def delete_text(self, target: WriterTarget) -> None:
        self._require_open()
        match = resolve_text_range(target, self.doc)
        match.setString("")

    def format_text(self, target: WriterTarget, formatting: TextFormatting) -> None:
        self._require_open()
        validate_formatting(formatting)
        text_range = resolve_text_range(target, self.doc)
        _apply_formatting(text_range, formatting)

    def insert_table(
        self,
        rows: int,
        cols: int,
        data: list[list[Any]] | None = None,
        name: str | None = None,
        target: WriterTarget | None = None,
    ) -> None:
        self._require_open()
        validate_table_data(rows, cols, data)

        table = self.doc.createInstance("com.sun.star.text.TextTable")
        table.initialize(rows, cols)

        cursor = resolve_insertion_point(target, self.doc)
        self.doc.Text.insertTextContent(cursor, table, False)
        if name is not None:
            _assign_content_name(table, name)

        if data is not None:
            _write_table_data(table, data)

    def update_table(self, target: WriterTarget, data: list[list[Any]]) -> None:
        self._require_open()
        table = resolve_table_target(target, self.doc)
        rows = table.Rows.Count
        cols = table.Columns.Count
        validate_table_data(rows, cols, data)
        _write_table_data(table, data)

    def delete_table(self, target: WriterTarget) -> None:
        self._require_open()
        table = resolve_table_target(target, self.doc)
        try:
            self.doc.Text.removeTextContent(table)
        except Exception:
            table.dispose()

    def insert_image(
        self,
        image_path: str,
        width: int | None = None,
        height: int | None = None,
        name: str | None = None,
        target: WriterTarget | None = None,
    ) -> None:
        self._require_open()
        image_file = Path(image_path)
        if not image_file.exists():
            raise ImageNotFoundError(f"Image not found: {image_path}")

        graphic = self.doc.createInstance("com.sun.star.text.GraphicObject")
        graphic.GraphicURL = image_file.resolve().as_uri()
        if width is not None or height is not None:
            _set_graphic_size(graphic, width, height)

        cursor = resolve_insertion_point(target, self.doc)
        self.doc.Text.insertTextContent(cursor, graphic, False)
        if name is not None:
            _assign_content_name(graphic, name)

    def update_image(
        self,
        target: WriterTarget,
        image_path: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        self._require_open()
        validate_image_update(image_path, width, height)

        graphic = resolve_image_target(target, self.doc)
        if image_path is not None:
            image_file = Path(image_path)
            if not image_file.exists():
                raise ImageNotFoundError(f"Image not found: {image_path}")
            graphic.GraphicURL = image_file.resolve().as_uri()
        if width is not None or height is not None:
            _set_graphic_size(graphic, width, height)

    def delete_image(self, target: WriterTarget) -> None:
        self._require_open()
        graphic = resolve_image_target(target, self.doc)
        try:
            self.doc.Text.removeTextContent(graphic)
        except Exception:
            graphic.dispose()

    def insert_list(
        self,
        items: list[ListItem],
        ordered: bool,
        target: WriterTarget | None = None,
    ) -> None:
        self._require_open()
        validate_list_items(items)
        cursor = resolve_insertion_point(target, self.doc)
        if target is not None and target.after is not None and target.before is None:
            cursor, following_list = _advance_cursor_past_following_list(cursor)
            if following_list:
                _apply_list_style_to_paragraphs(following_list, ordered)
        _insert_list_at_cursor(self.doc.Text, cursor, items, ordered)

    def replace_list(
        self,
        target: WriterTarget,
        items: list[ListItem],
        ordered: bool | None = None,
    ) -> None:
        self._require_open()
        validate_list_items(items)
        paragraphs = resolve_list_target(target, self.doc)
        ordered_value = ordered
        if ordered_value is None:
            ordered_value = _paragraphs_are_ordered(paragraphs)
        anchor = _delete_paragraph_block(self.doc, paragraphs)
        _insert_list_at_cursor(self.doc.Text, anchor, items, ordered_value)

    def delete_list(self, target: WriterTarget) -> None:
        self._require_open()
        paragraphs = resolve_list_target(target, self.doc)
        _delete_paragraph_block(self.doc, paragraphs)

    def patch(self, patch_text: str, mode: PatchApplyMode = "atomic"):
        self._require_open()
        from writer.patch import apply_operations

        return apply_operations(self, patch_text, mode)

    def export(self, output_path: str, format: str) -> None:
        """Export the current document state to another Writer-supported format."""
        self._require_open()
        if format not in EXPORT_FILTERS:
            raise WriterSkillError(f"Unsupported export format: {format}")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        import uno  # type: ignore[import-not-found]

        filter_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        filter_prop.Name = "FilterName"
        filter_prop.Value = EXPORT_FILTERS[format]
        self.doc.storeToURL(output.resolve().as_uri(), (filter_prop,))

    def reset(self) -> None:
        """Discard in-memory changes and reopen the backing document."""
        self._require_open()
        self._doc.close(False)
        self._uno_manager.__exit__(None, None, None)
        self._open_document()

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
            raise WriterSkillError(
                f"Failed to open Writer document: {self._path}"
            ) from exc


def open_writer_session(path: str) -> WriterSession:
    """Open a Writer editing session for an existing document."""
    return WriterSession(path)


def _insert_string(text_obj: Any, cursor: Any, text: str) -> None:
    if not _cursor_is_at_paragraph_boundary(cursor) and _cursor_has_text_before(cursor):
        text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)
    parts = text.split("\n")
    for index, part in enumerate(parts):
        if index > 0:
            text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)
        if part:
            text_obj.insertString(cursor, part, False)


def _apply_formatting(text_range: Any, formatting: TextFormatting) -> None:
    paragraph_cursor = _paragraph_cursor_for_range(text_range)

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
        text_range.CharHeight = formatting.font_size
    if formatting.color is not None:
        text_range.CharColor = resolve_color(formatting.color)
    if formatting.align is not None:
        paragraph_cursor.ParaAdjust = _ALIGNMENT_MAP[
            str(formatting.align).strip().lower()
        ]
    if formatting.line_spacing is not None:
        import uno  # type: ignore[import-not-found]

        line_spacing = uno.createUnoStruct("com.sun.star.style.LineSpacing")
        line_spacing.Mode = 0
        line_spacing.Height = int(formatting.line_spacing * 100)
        paragraph_cursor.ParaLineSpacing = line_spacing
    if formatting.spacing_before is not None:
        paragraph_cursor.ParaTopMargin = formatting.spacing_before
    if formatting.spacing_after is not None:
        paragraph_cursor.ParaBottomMargin = formatting.spacing_after


def _paragraph_cursor_for_range(text_range: Any) -> Any:
    text_obj = text_range.getText()
    paragraph_cursor = text_obj.createTextCursorByRange(text_range.Start)
    paragraph_cursor.gotoStartOfParagraph(False)
    paragraph_end = text_obj.createTextCursorByRange(text_range.End)
    paragraph_end.gotoEndOfParagraph(False)
    paragraph_cursor.gotoRange(paragraph_end.getEnd(), True)
    return paragraph_cursor


def _write_table_data(table: Any, data: list[list[Any]]) -> None:
    for row_index, row_data in enumerate(data):
        for col_index, cell_value in enumerate(row_data):
            table.getCellByName(_get_cell_name(row_index, col_index)).setString(
                str(cell_value)
            )


def _insert_list_at_cursor(
    text_obj: Any,
    cursor: Any,
    items: list[ListItem],
    ordered: bool,
) -> None:
    style_name = _ORDERED_LIST_STYLE if ordered else _UNORDERED_LIST_STYLE
    if not _cursor_is_at_paragraph_boundary(cursor) and _cursor_has_text_before(cursor):
        text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)
    for index, item in enumerate(items):
        start = cursor.getStart()
        text_obj.insertString(cursor, item.text, False)
        paragraph_cursor = text_obj.createTextCursorByRange(start)
        paragraph_cursor.gotoRange(cursor.getEnd(), True)
        paragraph_cursor.NumberingStyleName = style_name
        paragraph_cursor.NumberingLevel = item.level
        if index < len(items) - 1:
            text_obj.insertControlCharacter(cursor, _PARAGRAPH_BREAK, False)


def _advance_cursor_past_following_list(cursor: Any) -> tuple[Any, list[Any]]:
    text_obj = cursor.getText()
    enumeration = text_obj.createEnumeration()
    trailing_list: list[Any] = []
    cursor_start = cursor.getStart()
    while enumeration.hasMoreElements():
        paragraph = enumeration.nextElement()
        if not _range_is_after(text_obj, paragraph.getStart(), cursor_start):
            continue
        if not paragraph.getString() and not getattr(
            paragraph, "NumberingStyleName", ""
        ):
            continue
        if getattr(paragraph, "NumberingStyleName", ""):
            trailing_list.append(paragraph)
            continue
        break
    if not trailing_list:
        return cursor, []
    return text_obj.createTextCursorByRange(trailing_list[-1].getEnd()), trailing_list


def _cursor_has_text_before(cursor: Any) -> bool:
    probe = cursor.getText().createTextCursorByRange(cursor.getStart())
    probe.gotoStart(True)
    return bool(probe.getString())


def _cursor_is_at_paragraph_boundary(cursor: Any) -> bool:
    probe = cursor.getText().createTextCursorByRange(cursor.getStart())
    try:
        return probe.isStartOfParagraph()
    except Exception:
        return False


def _range_is_after(text_obj: Any, first: Any, second: Any) -> bool:
    return text_obj.compareRegionStarts(first, second) < 0


def _delete_paragraph_block(doc: Any, paragraphs: list[Any]) -> Any:
    text_obj = doc.Text
    cursor = text_obj.createTextCursorByRange(paragraphs[0].getStart())
    if len(paragraphs) == 1:
        paragraph = paragraphs[0]
        paragraph.setString("")
        paragraph.NumberingStyleName = ""
        paragraph.NumberingLevel = 0
        return cursor
    for paragraph in reversed(paragraphs):
        try:
            paragraph.dispose()
        except Exception:
            paragraph.setString("")
            paragraph.NumberingStyleName = ""
            paragraph.NumberingLevel = 0
    try:
        cursor.collapseToStart()
    except Exception:
        pass
    return cursor


def _paragraphs_are_ordered(paragraphs: list[Any]) -> bool:
    if not paragraphs:
        return False
    numbering_type = _paragraph_numbering_type(paragraphs[0])
    return numbering_type == 4


def _apply_list_style_to_paragraphs(paragraphs: list[Any], ordered: bool) -> None:
    style_name = _ORDERED_LIST_STYLE if ordered else _UNORDERED_LIST_STYLE
    for paragraph in paragraphs:
        paragraph.NumberingStyleName = style_name


def _paragraph_numbering_type(paragraph: Any) -> int | None:
    rules = getattr(paragraph, "NumberingRules", None)
    if rules is None:
        return None
    level = int(getattr(paragraph, "NumberingLevel", 0))
    try:
        properties = rules.getByIndex(level)
    except Exception:
        properties = rules.getByIndex(0)
    for property_value in properties:
        if getattr(property_value, "Name", None) == "NumberingType":
            try:
                return int(property_value.Value)
            except Exception:
                return None
    return None


def _get_cell_name(row: int, col: int) -> str:
    col_name = ""
    col_num = col + 1
    while col_num > 0:
        col_num -= 1
        col_name = chr(65 + (col_num % 26)) + col_name
        col_num //= 26
    return f"{col_name}{row + 1}"


def _set_graphic_size(graphic: Any, width: int | None, height: int | None) -> None:
    import uno  # type: ignore[import-not-found]

    current = graphic.Size
    size = uno.createUnoStruct("com.sun.star.awt.Size")
    size.Width = current.Width if width is None else width
    size.Height = current.Height if height is None else height
    graphic.setSize(size)


def _assign_content_name(content: Any, name: str) -> None:
    candidates = [name]
    normalized = "_".join(name.split())
    if normalized != name:
        candidates.append(normalized)

    for candidate in candidates:
        if hasattr(content, "setName"):
            try:
                content.setName(candidate)
                return
            except Exception:
                pass
        try:
            content.Name = candidate
            return
        except Exception:
            pass
