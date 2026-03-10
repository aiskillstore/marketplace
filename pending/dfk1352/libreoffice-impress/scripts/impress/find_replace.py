"""Find and replace operations for Impress."""

from pathlib import Path

from impress.exceptions import DocumentNotFoundError
from uno_bridge import uno_context


def find_replace(
    path: str,
    find: str,
    replace: str,
    match_case: bool = False,
    whole_word: bool = False,
) -> int:
    """Find and replace text across all slides.

    Args:
        path: Path to the presentation file.
        find: Text to search for.
        replace: Replacement text.
        match_case: Whether to match case.
        whole_word: Whether to match whole words only.

    Returns:
        Number of replacements made.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            count = 0
            # Use slide-level search/replace (slides implement XSearchable)
            pages = doc.DrawPages
            for page_idx in range(pages.Count):
                slide = pages.getByIndex(page_idx)
                sd = slide.createSearchDescriptor()
                sd.SearchString = find
                sd.ReplaceString = replace
                sd.SearchCaseSensitive = match_case
                sd.SearchWords = whole_word
                count += slide.replaceAll(sd)

            if count > 0:
                doc.store()
            return count
        finally:
            doc.close(True)
