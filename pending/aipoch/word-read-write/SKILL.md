---
name: word-read-write
description: Create and read Microsoft Word (.docx) documents. Use this skill when you need to generate reports/letters/templates as .docx or extract readable text from existing .docx files.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Generate Word reports (e.g., weekly status, audit summaries) from structured data in Node.js.
- Produce standardized memos/letters/templates with consistent page size, margins, headings, and tables.
- Export documents that must render reliably across Microsoft Word and Google Docs (tables, shading, widths).
- Insert images, headers/footers, page numbers, page breaks, and a table of contents programmatically.
- Extract text from existing `.docx` files for indexing, review, or conversion to Markdown.

## Key Features

- Create `.docx` documents using the `docx` (docx-js) library.
- Explicit page setup (US Letter vs A4), margins, and landscape handling.
- Style control (default font, overriding built-in Heading styles for TOC compatibility).
- Proper list generation (bullets/numbering via numbering config, not Unicode characters).
- Robust table rendering rules (DXA widths, column widths + cell widths, shading, borders, padding).
- Images with required metadata and transformations.
- Page breaks, headers/footers, and page numbering.
- Table of contents generation based on Word heading levels.
- Read/extract `.docx` content via Pandoc conversion.

## Dependencies

- **Node.js**: >= 18
- **docx**: `^9.0.0`
- **pandoc**: `>= 2.0` (CLI tool for extracting/converting `.docx` content)

## Example Usage

### 1) Create a `.docx` (Node.js)

**Install**
```bash
npm i docx
```

**create-doc.js**
```javascript
const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  ImageRun,
  Header,
  Footer,
  AlignmentType,
  BorderStyle,
  WidthType,
  ShadingType,
  PageOrientation,
  PageNumber,
  PageBreak,
  TableOfContents,
  HeadingLevel,
  LevelFormat,
} = require("docx");

const US_LETTER = { width: 12240, height: 15840 }; // DXA (1440 = 1 inch)
const MARGINS_1IN = { top: 1440, right: 1440, bottom: 1440, left: 1440 };
const CONTENT_WIDTH = US_LETTER.width - MARGINS_1IN.left - MARGINS_1IN.right; // 9360

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 24 }, // 12pt
      },
    },
    paragraphStyles: [
      // Use exact IDs to override built-in Word heading styles
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 },
      },
    ],
  },

  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "numbers",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },

  sections: [
    {
      properties: {
        page: {
          size: {
            width: US_LETTER.width,
            height: US_LETTER.height,
            // For landscape: pass portrait dimensions and set orientation; docx swaps internally.
            // orientation: PageOrientation.LANDSCAPE,
          },
          margin: MARGINS_1IN,
        },
      },

      headers: {
        default: new Header({
          children: [new Paragraph({ children: [new TextRun("Sample Header")] })],
        }),
      },

      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              children: [
                new TextRun("Page "),
                new TextRun({ children: [PageNumber.CURRENT] }),
              ],
            }),
          ],
        }),
      },

      children: [
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("DOCX Creation Example")],
        }),

        new TableOfContents("Table of Contents", {
          hyperlink: true,
          headingStyleRange: "1-3",
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Lists")],
        }),

        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun("Bullet item")],
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun("Numbered item")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Table")],
        }),

        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [CONTENT_WIDTH / 2, CONTENT_WIDTH / 2],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders,
                  width: { size: CONTENT_WIDTH / 2, type: WidthType.DXA },
                  shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                  margins: { top: 80, bottom: 80, left: 120, right: 120 },
                  children: [new Paragraph("Left cell")],
                }),
                new TableCell({
                  borders,
                  width: { size: CONTENT_WIDTH / 2, type: WidthType.DXA },
                  shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
                  margins: { top: 80, bottom: 80, left: 120, right: 120 },
                  children: [new Paragraph("Right cell")],
                }),
              ],
            }),
          ],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Image")],
        }),

        new Paragraph({
          children: [
            new ImageRun({
              type: "png",
              data: fs.readFileSync("./image.png"),
              transformation: { width: 200, height: 150 },
              altText: { title: "Title", description: "Desc", name: "Name" },
            }),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("New Page Section")],
        }),

        // Do not use "\n" inside TextRun; create separate Paragraphs instead.
        new Paragraph({ children: [new TextRun("This is on a new page.")] }),
      ],
    },
  ],
});

(async () => {
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync("output.docx", buffer);
  console.log("Wrote output.docx");
})();
```

**Run**
```bash
node create-doc.js
```

### 2) Read/extract `.docx` text with Pandoc

```bash
pandoc document.docx -o output.md
```

## Implementation Details

- **DOCX structure**: `.docx` is a ZIP archive containing XML parts; libraries generate the required XML and package it.
- **Page sizing (DXA)**:
  - Word uses **DXA** units where **1440 DXA = 1 inch**.
  - docx-js defaults to **A4**; for US documents set **US Letter** explicitly: `12240 x 15840`.
  - With 1" margins, **content width** is `12240 - 1440 - 1440 = 9360 DXA`.
- **Landscape orientation**:
  - docx-js swaps width/height internally for landscape.
  - Provide portrait dimensions and set `orientation: PageOrientation.LANDSCAPE`.
- **Headings and TOC**:
  - TOC generation requires paragraphs using `HeadingLevel.*`.
  - To override built-in heading appearance, use exact style IDs: `"Heading1"`, `"Heading2"`, etc.
  - Include `outlineLevel` (H1 = 0, H2 = 1, ...), otherwise TOC may not pick up headings.
- **Paragraphs vs newlines**:
  - Do not embed `\n` in runs to simulate line breaks; create separate `Paragraph` elements.
- **Lists**:
  - Do not manually insert Unicode bullet characters as plain text.
  - Use `numbering.config` with `LevelFormat.BULLET` / `LevelFormat.DECIMAL`.
  - Numbering continuity depends on `reference`: same reference continues; different reference restarts.
- **Tables (critical rendering rules)**:
  - Always use `WidthType.DXA` (percent widths can break in Google Docs).
  - Set **table `width`** and **`columnWidths`**; the sum of `columnWidths` must equal table width.
  - Set **each cell `width`** to match its corresponding column width (required for consistent rendering).
  - Cell `margins` are internal padding and do not add to width; they reduce usable content area.
  - For shading, prefer `ShadingType.CLEAR` to avoid unexpected black backgrounds.
- **Images**:
  - `ImageRun` requires a valid `type` (e.g., `png`, `jpg`) and `altText` fields.
- **Page breaks**:
  - `PageBreak` must be inside a `Paragraph` (or use `pageBreakBefore: true`).