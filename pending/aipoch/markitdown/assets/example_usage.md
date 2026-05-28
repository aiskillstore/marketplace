# MarkItDown Usage Examples

This document provides practical examples of using MarkItDown in various scenarios.

## Basic Examples

### 1. Simple File Conversion

```python
from markitdown import MarkItDown

md = MarkItDown()

# Convert PDF
result = md.convert("research_paper.pdf")
print(result.text_content)

# Convert Word document
result = md.convert("manuscript.docx")
print(result.text_content)

# Convert PowerPoint
result = md.convert("presentation.pptx")
print(result.text_content)
```

### 2. Saving to a File

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")

with open("output.md", "w", encoding="utf-8") as f:
    f.write(result.text_content)
```

### 3. Converting from a Stream

```python
from markitdown import MarkItDown

md = MarkItDown()

with open("document.pdf", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")
    print(result.text_content)
```

## Scientific Workflows

### Converting Research Papers

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()

# Convert all papers in the directory
papers_dir = Path("research_papers/")
output_dir = Path("markdown_papers/")
output_dir.mkdir(exist_ok=True)

for paper in papers_dir.glob("*.pdf"):
    result = md.convert(str(paper))
    
    # Save using the original filename
    output_file = output_dir / f"{paper.stem}.md"
    output_file.write_text(result.text_content)
    
    print(f"Converted: {paper.name}")
```

### Extracting Tables from Excel

```python
from markitdown import MarkItDown

md = MarkItDown()

# Convert Excel to Markdown tables
result = md.convert("experimental_data.xlsx")

# Result contains tables in Markdown format
print(result.text_content)

# Save for further processing
with open("data_tables.md", "w") as f:
    f.write(result.text_content)
```

### Processing Presentation Slides

```python
from markitdown import MarkItDown
from openai import OpenAI

# Use AI to generate image descriptions
client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-sonnet-4.5",
    llm_prompt="Describe this scientific slide, focusing on data and key findings"
)

result = md.convert("conference_talk.pptx")

# Save and add metadata
output = f"""# Conference Talk

{result.text_content}
"""

with open("talk_notes.md", "w") as f:
    f.write(output)
```

## AI-Enhanced Conversion

### Detailed Image Descriptions

```python
from markitdown import MarkItDown
from openai import OpenAI

# Initialize OpenRouter client
client = OpenAI(
    api_key="your-openrouter-api-key",
    base_url="https://openrouter.ai/api/v1"
)

# Scientific chart analysis
scientific_prompt = """
Analyze this scientific chart. Describe:
- Visualization type (chart, microscopy image, schematic, etc.)
- Key data points and trends
- Axes, labels, and legends
- Scientific significance
Please stay professional and precise.
"""

md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-sonnet-4.5",  # Recommended for scientific visual analysis
    llm_prompt=scientific_prompt
)

# Convert paper with figures
result = md.convert("paper_with_figures.pdf")
print(result.text_content)
```

### Using Different Prompts for Different Files

```python
from markitdown import MarkItDown
from openai import OpenAI

# Initialize OpenRouter client
client = OpenAI(
    api_key="your-openrouter-api-key",
    base_url="https://openrouter.ai/api/v1"
)

# Scientific papers - use Claude for technical analysis
scientific_md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-sonnet-4.5",
    llm_prompt="Describe scientific charts with professional precision"
)

# Presentations - use GPT-4o for visual understanding
presentation_md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-sonnet-4.5",
    llm_prompt="Summarize slide content and key visual elements"
)

# Use the appropriate instance for each file
paper_result = scientific_md.convert("research.pdf")
slides_result = presentation_md.convert("talk.pptx")
```

## Batch Processing

### Processing Multiple Files

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()

files_to_convert = [
    "paper1.pdf",
    "data.xlsx",
    "presentation.pptx",
    "notes.docx"
]

for file in files_to_convert:
    try:
        result = md.convert(file)
        output = Path(file).stem + ".md"
        
        with open(output, "w") as f:
            f.write(result.text_content)
        
        print(f"✓ {file} -> {output}")
    except Exception as e:
        print(f"✗ Error converting {file}: {e}")
```

### Parallel Processing

```python
from markitdown import MarkItDown
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def convert_file(filepath):
    md = MarkItDown()
    result = md.convert(filepath)
    
    output = Path(filepath).stem + ".md"
    with open(output, "w") as f:
        f.write(result.text_content)
    
    return filepath, output

files = list(Path("documents/").glob("*.pdf"))

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(convert_file, [str(f) for f in files])
    
    for input_file, output_file in results:
        print(f"Converted: {input_file} -> {output_file}")
```

## Integration Examples

### Literature Review Pipeline

```python
from markitdown import MarkItDown
from pathlib import Path
import json

md = MarkItDown()

# Convert papers and create metadata
papers_dir = Path("literature/")
output_dir = Path("literature_markdown/")
output_dir.mkdir(exist_ok=True)

catalog = []

for paper in papers_dir.glob("*.pdf"):
    result = md.convert(str(paper))
    
    # Save Markdown
    md_file = output_dir / f"{paper.stem}.md"
    md_file.write_text(result.text_content)
    
    # Store metadata
    catalog.append({
        "title": result.title or paper.stem,
        "source": paper.name,
        "markdown": str(md_file),
        "word_count": len(result.text_content.split())
    })

# Save catalog
with open(output_dir / "catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)
```

### Data Extraction Pipeline

```python
from markitdown import MarkItDown
import re

md = MarkItDown()

# Convert Excel data to Markdown
result = md.convert("experimental_results.xlsx")

# Extract tables (Markdown tables start with |)
tables = []
current_table = []
in_table = False

for line in result.text_content.split('\n'):
    if line.strip().startswith('|'):
        in_table = True
        current_table.append(line)
    elif in_table:
        if current_table:
            tables.append('\n'.join(current_table))
            current_table = []
        in_table = False

# Process each table
for i, table in enumerate(tables):
    print(f"Table {i+1}:")
    print(table)
    print("\n" + "="*50 + "\n")
```

### YouTube Transcript Analysis

```python
from markitdown import MarkItDown

md = MarkItDown()

# Get transcript
video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
result = md.convert(video_url)

# Save transcript
with open("lecture_transcript.md", "w") as f:
    f.write(f"# Lecture Transcript\n\n")
    f.write(f"**Source**: {video_url}\n\n")
    f.write(result.text_content)
```

## Error Handling

### Robust Conversion

```python
from markitdown import MarkItDown
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

md = MarkItDown()

def safe_convert(filepath):
    """File conversion with error handling."""
    try:
        result = md.convert(filepath)
        output = Path(filepath).stem + ".md"
        
        with open(output, "w") as f:
            f.write(result.text_content)
        
        logger.info(f"Successfully converted {filepath}")
        return True
    
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return False
    
    except ValueError as e:
        logger.error(f"Invalid file format for {filepath}: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error converting {filepath}: {e}")
        return False

# Usage example
files = ["paper.pdf", "data.xlsx", "slides.pptx"]
results = [safe_convert(f) for f in files]

print(f"Successfully converted {sum(results)}/{len(files)} files")
```

## Advanced Use Cases

### Custom Metadata Extraction

```python
from markitdown import MarkItDown
import re
from datetime import datetime

md = MarkItDown()

def convert_with_metadata(filepath):
    result = md.convert(filepath)
    
    # Extract metadata from content
    metadata = {
        "file": filepath,
        "title": result.title,
        "converted_at": datetime.now().isoformat(),
        "word_count": len(result.text_content.split()),
        "char_count": len(result.text_content)
    }
    
    # Try to find author
    author_match = re.search(r'(?:Author|By):\s*(.+?)(?:\n|$)', result.text_content)
    if author_match:
        metadata["author"] = author_match.group(1).strip()
    
    # Create formatted output
    output = f"""---
title: {metadata['title']}
author: {metadata.get('author', 'Unknown')}
source: {metadata['file']}
converted: {metadata['converted_at']}
words: {metadata['word_count']}
---

{result.text_content}
"""
    
    return output, metadata

# Usage example
content, meta = convert_with_metadata("paper.pdf")
print(meta)
```

### Format-Specific Processing

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()

def process_by_format(filepath):
    path = Path(filepath)
    result = md.convert(filepath)
    
    if path.suffix == '.pdf':
        # Add PDF-specific metadata
        output = f"# PDF Document: {path.stem}\n\n"
        output += result.text_content
    
    elif path.suffix == '.xlsx':
        # Add table count
        table_count = result.text_content.count('|---')
        output = f"# Excel Data: {path.stem}\n\n"
        output += f"**Tables**: {table_count}\n\n"
        output += result.text_content
    
    elif path.suffix == '.pptx':
        # Add slide count
        slide_count = result.text_content.count('## Slide')
        output = f"# Presentation: {path.stem}\n\n"
        output += f"**Slides**: {slide_count}\n\n"
        output += result.text_content
    
    else:
        output = result.text_content
    
    return output

# Usage example
content = process_by_format("presentation.pptx")
print(content)
```