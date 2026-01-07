#!/usr/bin/env python3
"""
Parse Markdown for X Articles publishing.

Extracts:
- Title (from first H1/H2 or first line)
- Cover image (first image)
- Content images with block index for precise positioning
- HTML content (images stripped)

Usage:
    python parse_markdown.py <markdown_file> [--output json|html]

Output (JSON):
{
    "title": "Article Title",
    "cover_image": "/path/to/cover.jpg",
    "content_images": [
        {"path": "/path/to/img.jpg", "block_index": 3, "after_text": "context..."},
        ...
    ],
    "html": "<p>Content...</p><h2>Section</h2>...",
    "total_blocks": 25
}

The block_index indicates which block element (0-indexed) the image should follow.
This allows precise positioning without relying on text matching.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def split_into_blocks(markdown: str) -> list[str]:
    """Split markdown into logical blocks (paragraphs, headers, quotes, code blocks, etc.)."""
    blocks = []
    current_block = []
    in_code_block = False
    code_block_lines = []

    lines = markdown.split('\n')

    for line in lines:
        stripped = line.strip()

        # Handle code block boundaries
        if stripped.startswith('```'):
            if in_code_block:
                # End of code block
                in_code_block = False
                if code_block_lines:
                    # Mark as code block with special prefix for later processing
                    # Use ___CODE_BLOCK_START___ and ___CODE_BLOCK_END___ to preserve content
                    blocks.append('___CODE_BLOCK_START___' + '\n'.join(code_block_lines) + '___CODE_BLOCK_END___')
                code_block_lines = []
            else:
                # Start of code block
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                in_code_block = True
            continue

        # If inside code block, collect ALL lines (including empty lines)
        if in_code_block:
            code_block_lines.append(line)
            continue

        # Empty line signals end of block
        if not stripped:
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            continue

        # Headers, blockquotes are their own blocks
        if stripped.startswith(('#', '>')):
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            blocks.append(stripped)
            continue

        # Image on its own line is its own block
        if re.match(r'^!\[.*\]\(.*\)$', stripped):
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            blocks.append(stripped)
            continue

        current_block.append(line)

    if current_block:
        blocks.append('\n'.join(current_block))

    # Handle unclosed code block
    if code_block_lines:
        blocks.append('___CODE_BLOCK_START___' + '\n'.join(code_block_lines) + '___CODE_BLOCK_END___')

    return blocks


def extract_images_with_block_index(markdown: str, base_path: Path) -> tuple[list[dict], str, int]:
    """Extract images with their block index position.

    Returns:
        (image_list, markdown_without_images, total_blocks)
    """
    blocks = split_into_blocks(markdown)
    images = []
    clean_blocks = []

    img_pattern = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)$')

    for i, block in enumerate(blocks):
        match = img_pattern.match(block.strip())
        if match:
            alt_text = match.group(1)
            img_path = match.group(2)

            # Resolve relative paths
            if not os.path.isabs(img_path):
                full_path = str(base_path / img_path)
            else:
                full_path = img_path

            # block_index is the index in clean_blocks (without images)
            # i.e., this image should be inserted after clean_blocks[block_index-1]
            block_index = len(clean_blocks)

            # Get context from previous block for reference
            after_text = ""
            if clean_blocks:
                prev_block = clean_blocks[-1].strip()
                # Get last line of previous block
                lines = [l for l in prev_block.split('\n') if l.strip()]
                after_text = lines[-1][:80] if lines else ""

            images.append({
                "path": full_path,
                "alt": alt_text,
                "block_index": block_index,
                "after_text": after_text  # Keep for reference/debugging
            })
        else:
            clean_blocks.append(block)

    clean_markdown = '\n\n'.join(clean_blocks)
    return images, clean_markdown, len(clean_blocks)


def extract_title(markdown: str) -> tuple[str, str]:
    """Extract title from first H1, H2, or first non-empty line.

    Returns:
        (title, markdown_without_title): Title string and markdown with H1 title removed.
        If title is from H1, it's removed from markdown to avoid duplication.
    """
    lines = markdown.strip().split('\n')
    title = "Untitled"
    title_line_idx = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # H1 - use as title and mark for removal
        if stripped.startswith('# '):
            title = stripped[2:].strip()
            title_line_idx = idx
            break
        # H2 - use as title but don't remove (it's a section header)
        if stripped.startswith('## '):
            title = stripped[3:].strip()
            break
        # First non-empty, non-image line
        if not stripped.startswith('!['):
            title = stripped[:100]
            break

    # Remove H1 title line from markdown to avoid duplication
    if title_line_idx is not None:
        lines.pop(title_line_idx)
        markdown = '\n'.join(lines)

    return title, markdown


def markdown_to_html(markdown: str) -> str:
    """Convert markdown to HTML for X Articles rich text paste."""
    html = markdown

    # Process code blocks first (marked with ___CODE_BLOCK_START___ and ___CODE_BLOCK_END___)
    # Convert to blockquote format since X Articles doesn't support <pre><code>
    def convert_code_block(match):
        code_content = match.group(1)
        lines = code_content.strip().split('\n')
        # Join non-empty lines with <br> for display
        formatted = '<br>'.join(line for line in lines if line.strip())
        return f'<blockquote>{formatted}</blockquote>'

    html = re.sub(r'___CODE_BLOCK_START___(.*?)___CODE_BLOCK_END___', convert_code_block, html, flags=re.DOTALL)

    # Headers (H2 only, H1 is title)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Blockquotes (regular markdown blockquotes, not code blocks)
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Unordered lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Ordered lists
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Wrap consecutive <li> in <ul>
    html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', html)

    # Paragraphs - split by double newlines
    parts = html.split('\n\n')
    processed_parts = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip if already a block element
        if part.startswith(('<h2>', '<h3>', '<blockquote>', '<ul>', '<ol>')):
            processed_parts.append(part)
        else:
            # Wrap in paragraph, convert single newlines to <br>
            part = part.replace('\n', '<br>')
            processed_parts.append(f'<p>{part}</p>')

    return ''.join(processed_parts)


def parse_markdown_file(filepath: str) -> dict:
    """Parse a markdown file and return structured data."""
    path = Path(filepath)
    base_path = path.parent

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title first (and remove H1 from markdown)
    title, content = extract_title(content)

    # Extract images with block indices
    images, clean_markdown, total_blocks = extract_images_with_block_index(content, base_path)

    # Convert to HTML
    html = markdown_to_html(clean_markdown)

    # Separate cover image from content images
    cover_image = images[0]["path"] if images else None
    content_images = images[1:] if len(images) > 1 else []

    # Adjust block_index for content images (subtract 1 since cover image is removed)
    # The first content image's block_index was calculated including cover image's position

    return {
        "title": title,
        "cover_image": cover_image,
        "content_images": content_images,
        "html": html,
        "total_blocks": total_blocks,
        "source_file": str(path.absolute())
    }


def main():
    parser = argparse.ArgumentParser(description='Parse Markdown for X Articles')
    parser.add_argument('file', help='Markdown file to parse')
    parser.add_argument('--output', choices=['json', 'html'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--html-only', action='store_true',
                       help='Output only HTML content')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = parse_markdown_file(args.file)

    if args.html_only:
        print(result['html'])
    elif args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result['html'])


if __name__ == '__main__':
    main()
