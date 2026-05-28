# MarkItDown API Reference

## Core Classes

### MarkItDown

The main class used for converting files to Markdown.

```python
from markitdown import MarkItDown

md = MarkItDown(
    llm_client=None,
    llm_model=None,
    llm_prompt=None,
    docintel_endpoint=None,
    enable_plugins=False
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_client` | OpenAI Client | `None` | OpenAI-compatible client used for generating AI image descriptions |
| `llm_model` | str | `None` | Model name used for image descriptions (e.g., "anthropic/claude-opus-4.5") |
| `llm_prompt` | str | `None` | Custom prompt for image descriptions |
| `docintel_endpoint` | str | `None` | Azure Document Intelligence endpoint |
| `enable_plugins` | bool | `False` | Enable third-party plugins |

#### Methods

##### convert()

Converts a file to Markdown.

```python
result = md.convert(
    source,
    file_extension=None
)
```

**Parameters**:
- `source` (str): Path to the file to be converted
- `file_extension` (str, optional): Override file extension detection

**Returns**: `DocumentConverterResult` object

**Example**:
```python
result = md.convert("document.pdf")
print(result.text_content)
```

##### convert_stream()

Converts from a file-like binary stream.

```python
result = md.convert_stream(
    stream,
    file_extension
)
```

**Parameters**:
- `stream` (BinaryIO): Binary file-like object (e.g., a file opened in `"rb"` mode)
- `file_extension` (str): File extension used to determine the conversion method (e.g., ".pdf")

**Returns**: `DocumentConverterResult` object

**Example**:
```python
with open("document.pdf", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")
    print(result.text_content)
```

**Important**: Streams must be opened in binary mode (`"rb"`), not text mode.

## Result Object

### DocumentConverterResult

The result of a conversion operation.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `text_content` | str | Converted Markdown text |
| `title` | str | Document title (if available) |

#### Example

```python
result = md.convert("paper.pdf")

# Access content
content = result.text_content

# Access title (if available)
title = result.title
```

## Custom Converters

You can create custom document converters by implementing the `DocumentConverter` interface.

### DocumentConverter Interface

```python
from markitdown import DocumentConverter

class CustomConverter(DocumentConverter):
    def convert(self, stream, file_extension):
        """
        Convert a document from a binary stream.
        
        Parameters:
            stream (BinaryIO): Binary file-like object
            file_extension (str): File extension (e.g., ".custom")
            
        Returns:
            DocumentConverterResult: Conversion result
        """
        # Write your conversion logic here
        pass
```

### Registering Custom Converters

```python
from markitdown import MarkItDown, DocumentConverter, DocumentConverterResult

class MyCustomConverter(DocumentConverter):
    def convert(self, stream, file_extension):
        content = stream.read().decode('utf-8')
        markdown_text = f"# Custom Format\n\n{content}"
        return DocumentConverterResult(
            text_content=markdown_text,
            title="Custom Document"
        )

# Create MarkItDown instance
md = MarkItDown()

# Register custom converter for .custom files
md.register_converter(".custom", MyCustomConverter())

# Use it
result = md.convert("myfile.custom")
```

## Plugin System

### Finding Plugins

Search for the `#markitdown-plugin` tag on GitHub.

### Using Plugins

```python
from markitdown import MarkItDown

# Enable plugins
md = MarkItDown(enable_plugins=True)
result = md.convert("document.pdf")
```

### Creating Plugins

Plugins are Python packages that register converters with MarkItDown.

**Plugin structure**:
```
my-markitdown-plugin/
├── setup.py
├── my_plugin/
│   ├── __init__.py
│   └── converter.py
└── README.md
```

**setup.py**:
```python
from setuptools import setup

setup(
    name="markitdown-my-plugin",
    version="0.1.0",
    packages=["my_plugin"],
    entry_points={
        "markitdown.plugins": [
            "my_plugin = my_plugin.converter:MyConverter",
        ],
    },
)
```

**converter.py**:
```python
from markitdown import DocumentConverter, DocumentConverterResult

class MyConverter(DocumentConverter):
    def convert(self, stream, file_extension):
        # Your conversion logic
        content = stream.read()
        markdown = self.process(content)
        return DocumentConverterResult(
            text_content=markdown,
            title="My Document"
        )
    
    def process(self, content):
        # Process content
        return "# Converted Content\n\n..."
```

## AI-Enhanced Conversion

### Image Description with OpenRouter

```python
from markitdown import MarkItDown
from openai import OpenAI

# Initialize OpenRouter client (OpenAI-compatible API)
client = OpenAI(
    api_key="your-openrouter-api-key",
    base_url="https://openrouter.ai/api/v1"
)

# Create AI-enabled MarkItDown
md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-opus-4.5",  # Recommended for scientific vision analysis
    llm_prompt="Describe this image in detail for scientific documentation"
)

# Convert a file containing images
result = md.convert("presentation.pptx")
```

### Models Available via OpenRouter

Commonly used vision-capable models:
- `anthropic/claude-opus-4.5` - **Recommended for scientific vision analysis**
- `google/gemini-3-pro-preview` - Gemini Pro Vision

See https://openrouter.ai/models for the full list.

### Custom Prompts

```python
# For scientific charts
scientific_prompt = """
Analyze this scientific diagram or chart. Describe:
1. The type of visualization (graph, chart, diagram, etc.)
2. Key data points or trends
3. Labels and axes
4. Scientific significance
Be precise and technical.
"""

md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-opus-4.5",
    llm_prompt=scientific_prompt
)
```

## Azure Document Intelligence

### Setup

1. Create an Azure Document Intelligence resource
2. Get the endpoint URL
3. Set up authentication

### Usage

```python
from markitdown import MarkItDown

md = MarkItDown(
    docintel_endpoint="https://YOUR-RESOURCE.cognitiveservices.azure.com/"
)

result = md.convert("complex_document.pdf")
```

### Authentication

Set environment variables:
```bash
export AZURE_DOCUMENT_INTELLIGENCE_KEY="your-key"
```

Or pass credentials via code.

## Error Handling

```python
from markitdown import MarkItDown

md = MarkItDown()

try:
    result = md.convert("document.pdf")
    print(result.text_content)
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid file format: {e}")
except Exception as e:
    print(f"Conversion error: {e}")
```

## Performance Tips

### 1. Reuse MarkItDown Instance

```python
# Recommended: Create once, use multiple times
md = MarkItDown()

for file in files:
    result = md.convert(file)
    process(result)
```

### 2. Use Streaming for Large Files

```python
# For large files
with open("large_file.pdf", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")
```

### 3. Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

md = MarkItDown()

def convert_file(filepath):
    return md.convert(filepath)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(convert_file, file_list)
```

## Breaking Changes (v0.0.1 to v0.1.0)

1. **Dependencies**: Now organized into optional feature groups
   ```bash
   # Old version
   pip install markitdown
   
   # New version
   pip install 'markitdown[all]'
   ```

2. **convert_stream()**: Now requires a binary file-like object
   ```python
   # Old version (also accepted text)
   with open("file.pdf", "r") as f:  # Text mode
       result = md.convert_stream(f)
   
   # New version (binary only)
   with open("file.pdf", "rb") as f:  # Binary mode
       result = md.convert_stream(f, file_extension=".pdf")
   ```

3. **DocumentConverter Interface**: Changed to read from stream instead of file path
   - No temporary files created
   - More memory efficient
   - Plugins need to be updated

## Version Compatibility

- **Python**: Requires 3.10 or higher
- **Dependencies**: Check version constraints in `setup.py`
- **OpenAI**: Compatible with OpenAI Python SDK v1.0+

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key for image descriptions | `sk-or-v1-...` |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Azure DI authentication key | `key123...` |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure DI endpoint | `https://...` |