"""Find and replace operations for Writer."""

from pathlib import Path

from uno_bridge import uno_context
from writer.exceptions import DocumentNotFoundError


def find_replace(
    path: str,
    find: str,
    replace: str,
    match_case: bool = False,
    whole_word: bool = False,
) -> int:
    """Find and replace text in a Writer document.

    Args:
        path: Path to the document file.
        find: Text to search for.
        replace: Replacement text.
        match_case: Whether to match case.
        whole_word: Whether to match whole words only.

    Returns:
        Number of replacements made.

    Raises:
        DocumentNotFoundError: If the document does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            sd = doc.createSearchDescriptor()
            sd.SearchString = find
            sd.ReplaceString = replace
            sd.SearchCaseSensitive = match_case
            sd.SearchWords = whole_word

            count = doc.replaceAll(sd)

            if count > 0:
                doc.store()
            return count
        finally:
            doc.close(True)
