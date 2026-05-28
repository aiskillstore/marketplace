# File Format Support

This document provides detailed information on each file format supported by MarkItDown.

## Document Formats

### PDF (.pdf)

**Features**:
- Text extraction
- Table detection
- Metadata extraction
- OCR for scanned documents (requires dependencies)

**Dependencies**:
```bash
pip install 'markitdown[pdf]'
```

**Best for**:
- Scientific papers
- Reports
- Books
- Forms

**Limitations**:
- Complex layouts may not preserve formatting perfectly
- Scanned PDFs require OCR configuration
- Certain PDF features (annotations, forms) may not be converted

**Example**:
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("research_paper.pdf")
print(result.text_content)
```

**Enhanced with Azure Document Intelligence**:
```python
md = MarkItDown(docintel_endpoint="https://YOUR-ENDPOINT.cognitiveservices.azure.com/")
result = md.convert("complex_layout.pdf")
```

---

### Microsoft Word (.docx)

**Features**:
- Text extraction
- Table conversion
- Heading hierarchy
- List formatting
- Basic text formatting (bold, italics)

**Dependencies**:
```bash
pip install 'markitdown[docx]'
```

**Best for**:
- Research papers
- Reports
- Documentation
- Manuscripts

**Preserved Elements**:
- Headings (converted to Markdown headers)
- Tables (converted to Markdown tables)
- Lists (unordered and ordered)
- Basic formatting (bold, italics)
- Paragraphs

**Example**:
```python
result = md.convert("manuscript.docx")
```

---

### PowerPoint (.pptx)

**Features**:
- Slide content extraction
- Speaker notes
- Table extraction
- Image descriptions (with AI)

**Dependencies**:
```bash
pip install 'markitdown[pptx]'
```

**Best for**:
- Presentations
- Lecture slides
- Conference talks

**Output Format**:
```markdown
# Slide 1: Title

Content from slide 1...

**Notes**: Speaker notes appear here

---

# Slide 2: Next Topic

...
```

**With AI Image Descriptions**:
```python
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("presentation.pptx")
```

---

### Excel (.xlsx, .xls)

**Features**:
- Worksheet extraction
- Table formatting
- Data preservation
- Formula values (calculated values)

**Dependencies**:
```bash
pip install 'markitdown[xlsx]'  # Modern Excel
pip install 'markitdown[xls]'   # Legacy Excel
```

**Best for**:
- Data tables
- Research data
- Statistical results
- Experimental data

**Output Format**:
```markdown
# Sheet: Results

| Sample | Control | Treatment | P-value |
|--------|---------|-----------|---------|
| 1      | 10.2    | 12.5      | 0.023   |
| 2      | 9.8     | 11.9      | 0.031   |
```

**Example**:
```python
result = md.convert("experimental_data.xlsx")
```

---

## Image Formats

### Images (.jpg, .jpeg, .png, .gif, .webp)

**Features**:
- EXIF metadata extraction
- OCR text extraction
- AI-driven image descriptions

**Dependencies**:
```bash
pip install 'markitdown[all]'  # Includes image support
```

**Best for**:
- Scanned documents
- Charts and graphs
- Scientific diagrams
- Photos with text

**Output without AI**:
```markdown
![Image](image.jpg)

**EXIF Data**:
- Camera: Canon EOS 5D
- Date: 2024-01-15
- Resolution: 4000x3000
```

**Output with AI**:
```python
from openai import OpenAI

client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="Describe this scientific diagram in detail" # Detailed description of this scientific diagram
)
result = md.convert("graph.png")
```

**OCR for Text Extraction**:
Requires Tesseract OCR:
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
```

---

## Audio Formats

### Audio (.wav, .mp3)

**Features**:
- Metadata extraction
- Speech-to-text (transcription)
- Duration and technical info

**Dependencies**:
```bash
pip install 'markitdown[audio-transcription]'
```

**Best for**:
- Lecture recordings
- Interviews
- Podcasts
- Meeting recordings

**Output Format**:
```markdown
# Audio: interview.mp3

**Metadata**:
- Duration: 45:32
- Bitrate: 320kbps
- Sample Rate: 44100Hz

**Transcription**:
[Transcription text appears here...]
```

**Example**:
```python
result = md.convert("lecture.mp3")
```

---

## Web Formats

### HTML (.html, .htm)

**Features**:
- Clean HTML to Markdown conversion
- Link preservation
- Table conversion
- List formatting

**Best for**:
- Web pages
- Documentation
- Blog posts
- Online articles

**Output Format**: Clean Markdown preserving links and structure

**Example**:
```python
result = md.convert("webpage.html")
```

---

### YouTube URLs

**Features**:
- Fetch video transcriptions
- Extract video metadata
- Subtitle download

**Dependencies**:
```bash
pip install 'markitdown[youtube-transcription]'
```

**Best for**:
- Educational videos
- Lectures
- Talks
- Tutorials

**Example**:
```python
result = md.convert("https://www.youtube.com/watch?v=VIDEO_ID")
```

---

## Data Formats

### CSV (.csv)

**Features**:
- Automatic table conversion
- Delimiter detection
- Header preservation

**Output Format**: Markdown table

**Example**:
```python
result = md.convert("data.csv")
```

**Output**:
```markdown
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| Value1  | Value2  | Value3  |
```

---

### JSON (.json)

**Features**:
- Structured presentation
- Pretty formatting
- Nested data visualization

**Best for**:
- API responses
- Configuration files
- Data exports

**Example**:
```python
result = md.convert("data.json")
```

---

### XML (.xml)

**Features**:
- Structure preservation
- Attribute extraction
- Formatted output

**Best for**:
- Configuration files
- Data exchange
- Structured documents

**Example**:
```python
result = md.convert("config.xml")
```

---

## Archive Formats

### ZIP (.zip)

**Features**:
- Iterate through archive contents
- Convert files individually
- Maintain directory structure in output

**Best for**:
- Document collections
- Project archives
- Batch conversion

**Output Format**:
```markdown
# Archive: documents.zip

## File: document1.pdf
[Content from document1.pdf...]

---

## File: document2.docx
[Content from document2.docx...]
```

**Example**:
```python
result = md.convert("archive.zip")
```

---

## E-book Formats

### EPUB (.epub)

**Features**:
- Full text extraction
- Chapter structure
- Metadata extraction

**Best for**:
- E-books
- Digital publications
- Long-form content

**Output Format**: Markdown preserving chapter structure

**Example**:
```python
result = md.convert("book.epub")
```

---

## Other Formats

### Outlook Email (.msg)

**Features**:
- Email content extraction
- Attachment list
- Metadata (From, To, Subject, Date)

**Dependencies**:
```bash
pip install 'markitdown[outlook]'
```

**Best for**:
- Email archiving
- Communication records

**Example**:
```python
result = md.convert("message.msg")
```

---

## Format-Specific Recommendations

### PDF Best Practices

1. **Use Azure Document Intelligence for complex layouts**:
   ```python
   md = MarkItDown(docintel_endpoint="endpoint_url")
   ```

2. **Ensure OCR is configured for scanned PDFs**:
   ```bash
   brew install tesseract  # macOS
   ```

3. **Split very large PDFs** before conversion for better performance

### PowerPoint Best Practices

1. **Use AI for visual content**:
   ```python
   md = MarkItDown(llm_client=client, llm_model="gpt-4o")
   ```

2. **Check speaker notes** - they will be included in the output

3. **Complex animations are not captured** - static content only

### Excel Best Practices

1. **Large spreadsheets** may take time to convert

2. **Formulas are converted to their calculated values**

3. **Multiple worksheets** are all included in the output

4. **Charts will become text descriptions** (use AI for better descriptions)

### Image Best Practices

1. **Use AI for meaningful descriptions**:
   ```python
   md = MarkItDown(
       llm_client=client,
       llm_model="gpt-4o",
       llm_prompt="Describe this scientific figure in detail" # Detailed description of this scientific figure
   )
   ```

2. **Ensure OCR dependencies are installed** for text-heavy images

3. **High-resolution images** may require longer processing time

### Audio Best Practices

1. **Clear audio** produces better transcriptions

2. **Long recordings** can be time-consuming

3. **Consider splitting long audio files** to speed up processing

---

## Unsupported Formats

If you need to convert an unsupported format:

1. **Create a custom converter** (refer to `api_reference.md`)
2. **Look for plugins on GitHub** (#markitdown-plugin)
3. **Pre-convert to a supported format** (e.g., convert .rtf to .docx)

---

## Format Detection

MarkItDown automatically detects formats via:

1. **File extension** (preferred method)
2. **MIME type** (fallback)
3. **Magic Bytes** (fallback)

**Force specify format**:
```python
# Force a specific format
result = md.convert("file_without_extension", file_extension=".pdf")

# Using Streams
with open("file", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")
```