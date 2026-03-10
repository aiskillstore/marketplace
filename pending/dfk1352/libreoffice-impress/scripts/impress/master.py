"""Master page operations for Impress."""

from pathlib import Path

from colors import resolve_color
from impress.exceptions import DocumentNotFoundError, MasterNotFoundError
from uno_bridge import uno_context


def list_master_pages(path: str) -> list[str]:
    """Return list of master page names in the presentation.

    Args:
        path: Path to the presentation file.

    Returns:
        List of master page name strings.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            masters = doc.MasterPages
            names = []
            for i in range(masters.Count):
                names.append(masters.getByIndex(i).Name)
            return names
        finally:
            doc.close(True)


def apply_master_page(path: str, master_name: str) -> None:
    """Apply a master page to all slides.

    Args:
        path: Path to the presentation file.
        master_name: Name of the master page.
    Raises:
        MasterNotFoundError: If master_name is not found.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            masters = doc.MasterPages
            target_master = None
            for i in range(masters.Count):
                m = masters.getByIndex(i)
                if m.Name == master_name:
                    target_master = m
                    break

            if target_master is None:
                available = [masters.getByIndex(i).Name for i in range(masters.Count)]
                raise MasterNotFoundError(
                    f"Master page '{master_name}' not found. Available: {available}"
                )

            pages = doc.DrawPages
            for i in range(pages.Count):
                slide = pages.getByIndex(i)
                slide.MasterPage = target_master

            doc.store()
        finally:
            doc.close(True)


def import_master_from_template(path: str, template_path: str) -> str:
    """Import the first master page from a template into the target.

    Args:
        path: Path to the target presentation.
        template_path: Path to the template presentation.

    Returns:
        Name of the imported master page.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    tmpl_path = Path(template_path)
    if not tmpl_path.exists():
        raise DocumentNotFoundError(f"Template not found: {template_path}")

    with uno_context() as desktop:
        tmpl_doc = desktop.loadComponentFromURL(
            tmpl_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            tmpl_master = tmpl_doc.MasterPages.getByIndex(0)
            imported_name = tmpl_master.Name
        finally:
            tmpl_doc.close(True)

        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            masters = doc.MasterPages

            for i in range(masters.Count):
                if masters.getByIndex(i).Name == imported_name:
                    return imported_name

            new_master = masters.insertNewByIndex(masters.Count)
            new_master.Name = imported_name

            doc.store()
            return imported_name
        finally:
            doc.close(True)


def set_master_background(
    path: str,
    master_name: str,
    color: int | str,
) -> None:
    """Set a solid background colour on a master page.

    Args:
        path: Path to the presentation file.
        master_name: Name of the master page.
        color: Background colour as 0xRRGGBB integer or name.

    Raises:
        MasterNotFoundError: If master_name is not found.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            masters = doc.MasterPages
            target_master = None
            for i in range(masters.Count):
                master = masters.getByIndex(i)
                if master.Name == master_name:
                    target_master = master
                    break

            if target_master is None:
                available = [masters.getByIndex(i).Name for i in range(masters.Count)]
                raise MasterNotFoundError(
                    f"Master page '{master_name}' not found. Available: {available}"
                )

            bg = doc.createInstance("com.sun.star.drawing.Background")
            bg.FillStyle = 1  # SOLID
            bg.FillColor = resolve_color(color)
            target_master.Background = bg

            doc.store()
        finally:
            doc.close(True)
