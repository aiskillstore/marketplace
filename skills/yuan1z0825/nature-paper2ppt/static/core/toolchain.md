# Toolchain policy and fast path

## Toolchain policy

Use a cross-platform Python-first stack unless the user explicitly asks for something else:

- PyMuPDF for metadata, text extraction, page rendering, and page-level crops,
- Pillow for figure crops, contact sheets, and lightweight preview images,
- python-pptx for slide authoring and PPTX-safe editing,
- zipfile plus a reopen pass through python-pptx for package validation.

This stack must work on macOS, Linux, and Windows. Use `pathlib` paths, project-local output directories, and Office-safe fonts or theme fonts. Do not hardcode OS font paths or platform-specific file locations. If Python packages are missing, create a local virtual environment and install the minimum packages only when policy permits; do not install broad document suites just to finish a normal deck.

Treat LibreOffice/soffice as optional, only when it is already available and a real rendered preview is worth the cost. Avoid Keynote, PowerPoint desktop automation, AppleScript, Preview, Finder, `open`, and any OS-specific font or path dependency in helper scripts. If a preview can be made from extracted slide objects or assets, prefer that over re-rendering the whole deck.

Ask or document the tradeoff before doing expensive extras such as full supplementary-material processing, high-resolution recreation of many figures, full slide-by-slide rendered QA, or very long decks.

## Default fast path

For a normal selectable-text paper PDF, run the shortest complete path:

1. Extract metadata, abstract, headings, figure legends, and table captions with PyMuPDF.
2. Identify the paper type, argument, and candidate figures before rendering high-resolution pages.
3. Render low-resolution contact sheets only when figure locations are unclear.
4. Render high-resolution images only for selected figure/table pages and crop only assets that will appear in the deck.
5. Build the PPTX directly with python-pptx, using native tables/charts when values are explicit and figure crops when the original visual carries the evidence.
6. Run the self-review and revision loop: inspect crop quality, slide density, layout bounds, source labels, notes, and figure readability; fix high- and medium-severity issues before final validation.
7. Verify by reopening the PPTX and inspecting package structure; render slide previews only if a reliable cross-platform headless renderer is already available.

OCR, full supplementary extraction, all-page high-resolution rendering, all-slide rendered QA, and long script files are opt-in or justified exceptions, not defaults.
