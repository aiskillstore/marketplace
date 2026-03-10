"""Find and replace operations for Calc."""

from pathlib import Path

from uno_bridge import uno_context


def find_replace(
    path: str,
    find: str,
    replace: str,
    match_case: bool = False,
    whole_word: bool = False,
    sheet: str | int | None = None,
) -> int:
    """Find and replace text in a Calc spreadsheet.

    Args:
        path: Path to the spreadsheet file.
        find: Text to search for.
        replace: Replacement text.
        match_case: Whether to match case.
        whole_word: Whether to match whole words only.
        sheet: Optional sheet name or index to scope the replacement.
            If None, replaces across all sheets.

    Returns:
        Number of replacements made.
    """
    file_path = Path(path)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            if sheet is not None:
                # Scope to a specific sheet
                sheets = doc.Sheets
                if isinstance(sheet, int):
                    target = sheets.getByIndex(sheet)
                else:
                    target = sheets.getByName(sheet)

                sd = target.createSearchDescriptor()
                sd.SearchString = find
                sd.ReplaceString = replace
                sd.SearchCaseSensitive = match_case
                sd.SearchWords = whole_word
                count = target.replaceAll(sd)
            else:
                # Replace across entire document
                count = 0
                sheets = doc.Sheets
                for i in range(sheets.Count):
                    target = sheets.getByIndex(i)
                    sd = target.createSearchDescriptor()
                    sd.SearchString = find
                    sd.ReplaceString = replace
                    sd.SearchCaseSensitive = match_case
                    sd.SearchWords = whole_word
                    count += target.replaceAll(sd)

            if count > 0:
                doc.store()
            return count
        finally:
            doc.close(True)
