#!/usr/bin/env python3
"""
EPUB Chapter Extractor
Extracts all chapters from an EPUB file into separate markdown files.

Usage:
    python extract_chapters.py /path/to/book.epub [output_dir]

If output_dir is not specified, creates a folder named after the EPUB.
"""

import os
import sys
import re
from typing import List, Tuple, Any

# Required: pip install ebooklib beautifulsoup4 html2text
from ebooklib import epub
from bs4 import BeautifulSoup, Comment
import html2text


def get_toc(book: Any) -> List[Tuple[str, str, int]]:
    """
    Extract table of contents with hierarchy level.
    Returns list of (title, href, level) tuples.
    """
    toc_entries = []

    for item in book.toc:
        if isinstance(item, tuple):
            # item format: (chapter element, list of subchapters)
            chapter = item[0]
            toc_entries.append((chapter.title, chapter.href, 1))
            # Add subchapters
            for sub_item in item[1]:
                if isinstance(sub_item, tuple):
                    toc_entries.append((sub_item[0].title, sub_item[0].href, 2))
                else:
                    toc_entries.append((sub_item.title, sub_item.href, 2))
        else:
            # Single level TOC item
            toc_entries.append((item.title, item.href, 1))

    return toc_entries


def clean_html(html_str: str) -> str:
    """
    Clean HTML content - remove scripts, styles, images, comments, empty tags.
    """
    soup = BeautifulSoup(html_str, 'html.parser')

    # Remove unnecessary tags
    for tag in soup(['script', 'style', 'img', 'svg', 'iframe', 'video', 'nav']):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove empty tags
    for tag in soup.find_all():
        if not tag.get_text(strip=True) and not tag.find('img') and not tag.name == 'br':
            tag.decompose()

    return str(soup)


def convert_html_to_markdown(html_str: str) -> str:
    """Convert HTML to Markdown."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # Don't wrap lines
    return h.handle(html_str)


def heading_level(tag_name: str) -> int:
    """Get numeric heading level from tag name (h1=1, h2=2, etc.)"""
    if tag_name and tag_name.startswith('h') and tag_name[1:].isdigit():
        return int(tag_name[1:])
    return 7  # treat as lowest priority


def extract_chapter_html(book: Any, anchor_href: str, toc_entries: List[Tuple[str, str, int]]) -> str:
    """
    Extract chapter HTML content with proper boundary handling for subchapters.
    """
    href, anchor = anchor_href.split('#') if '#' in anchor_href else (anchor_href, None)

    # Find current chapter in TOC
    current_idx = None
    current_level = None
    for i, (title, toc_href, level) in enumerate(toc_entries):
        if toc_href == anchor_href or (anchor_href in toc_href and '#' in anchor_href):
            current_idx = i
            current_level = level
            break

    if current_idx is None:
        raise ValueError(f"Chapter {anchor_href} not found in TOC")

    # Get the chapter file content
    item = book.get_item_with_href(href)
    if item is None:
        raise ValueError(f"Chapter file not found: {href}")

    soup = BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')
    elems = []

    if anchor:
        # Start from specific anchor
        start_elem = soup.find(id=anchor)
        if not start_elem:
            raise ValueError(f"Anchor {anchor} not found in {href}")

        start_level = heading_level(start_elem.name)
        for elem in start_elem.next_elements:
            if elem is start_elem:
                elems.append(str(elem))
                continue
            if hasattr(elem, 'name') and elem.name and elem.name.startswith('h') and elem.name[1:].isdigit():
                if heading_level(elem.name) <= start_level:
                    break
            elems.append(str(elem))
    else:
        # No anchor - extract from first heading or body
        chapter_elem = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if chapter_elem:
            start_level = heading_level(chapter_elem.name)
            for elem in chapter_elem.next_elements:
                if elem is chapter_elem:
                    elems.append(str(elem))
                    continue
                if hasattr(elem, 'name') and elem.name and elem.name.startswith('h') and elem.name[1:].isdigit():
                    if heading_level(elem.name) <= start_level:
                        break
                elems.append(str(elem))
        else:
            body_elem = soup.find('body')
            elems = [str(body_elem)] if body_elem else [str(soup)]

    html = '\n'.join(elems)
    return clean_html(html)


def sanitize_filename(title: str, max_length: int = 50) -> str:
    """Convert chapter title to safe filename."""
    # Replace problematic characters
    safe = re.sub(r'[/:*?"<>|\\]', '', title)
    # Replace spaces and multiple underscores
    safe = re.sub(r'\s+', '_', safe)
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores
    safe = safe.strip('_')
    # Truncate
    if len(safe) > max_length:
        safe = safe[:max_length].rstrip('_')
    # Lowercase
    return safe.lower()


def extract_all_chapters(epub_path: str, output_dir: str) -> List[str]:
    """
    Extract all chapters from EPUB to separate markdown files.

    Args:
        epub_path: Path to the EPUB file
        output_dir: Directory to save extracted chapters

    Returns:
        List of created file paths
    """
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    # Read EPUB
    print(f"Reading: {epub_path}")
    book = epub.read_epub(epub_path)

    # Get TOC
    toc_entries = get_toc(book)
    if not toc_entries:
        raise ValueError("EPUB has no table of contents")

    print(f"Found {len(toc_entries)} chapters")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    created_files = []
    errors = []

    for idx, (title, href, level) in enumerate(toc_entries, 1):
        safe_title = sanitize_filename(title)
        filename = f"{idx:02d}_{safe_title}.md"
        filepath = os.path.join(output_dir, filename)

        try:
            # Extract chapter HTML
            html = extract_chapter_html(book, href, toc_entries)

            # Convert to markdown
            markdown = convert_html_to_markdown(html)

            # Add title header
            content = f"# {title}\n\n{markdown}"

            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            created_files.append(filepath)
            print(f"  [{idx:02d}/{len(toc_entries)}] {filename}")

        except Exception as e:
            errors.append((title, str(e)))
            print(f"  [{idx:02d}/{len(toc_entries)}] ERROR: {title} - {e}")

    # Summary
    print(f"\nExtracted {len(created_files)}/{len(toc_entries)} chapters to: {output_dir}")

    if errors:
        print(f"\nFailed chapters ({len(errors)}):")
        for title, error in errors:
            print(f"  - {title}: {error}")

    return created_files


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_chapters.py <epub_path> [output_dir]")
        print("\nExtracts all chapters from an EPUB into separate markdown files.")
        sys.exit(1)

    epub_path = os.path.abspath(sys.argv[1])

    if len(sys.argv) >= 3:
        output_dir = os.path.abspath(sys.argv[2])
    else:
        # Default: create folder named after the EPUB
        base_name = os.path.splitext(os.path.basename(epub_path))[0]
        output_dir = os.path.join(os.path.dirname(epub_path), base_name)

    try:
        extract_all_chapters(epub_path, output_dir)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
