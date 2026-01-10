# Tool Discovery Reference

Authoritative recommendations for common tasks. Use these instead of manual implementations.

## File Formats

### Documents
| Format | Python | CLI | Notes |
|--------|--------|-----|-------|
| **PDF** | `PyMuPDF`, `pdfplumber` | `pdftotext` | PyMuPDF for complex, pdfplumber for tables |
| **Word (.docx)** | `python-docx` | `pandoc` | |
| **Excel (.xlsx)** | `openpyxl`, `pandas` | | openpyxl for formatting, pandas for data |
| **CSV** | `pandas`, `csv` | `csvkit` | pandas for analysis, csv for streaming |
| **JSON** | `json`, `orjson` | `jq` | orjson 10x faster than json |
| **YAML** | `PyYAML`, `ruamel.yaml` | `yq` | ruamel preserves comments |
| **TOML** | `tomllib` (3.11+), `toml` | `yq` | |
| **XML** | `lxml`, `xml.etree` | `xmlstarlet` | lxml for speed |
| **Markdown** | `markdown`, `mistune` | `pandoc` | |

### Images
| Task | Python | CLI | Notes |
|------|--------|-----|-------|
| **Read/Write** | `Pillow (PIL)` | `imagemagick` | |
| **Computer Vision** | `opencv-python` | | |
| **OCR** | `pytesseract`, `paddleocr` | `tesseract` | paddleocr more accurate |
| **Metadata** | `exifread`, `Pillow` | `exiftool` | |
| **QR Codes** | `qrcode`, `pyzbar` | `zbarimg` | |

### Audio/Video
| Task | Python | CLI | Notes |
|------|--------|-----|-------|
| **Audio I/O** | `pydub`, `soundfile` | `ffmpeg` | |
| **Audio Analysis** | `librosa` | | Feature extraction, spectrograms |
| **Speech-to-Text** | `whisper`, `vosk` | | whisper most accurate |
| **Video** | `moviepy`, `opencv` | `ffmpeg` | |
| **Transcoding** | `ffmpeg-python` | `ffmpeg` | |

### Archives
| Format | Python | CLI |
|--------|--------|-----|
| **ZIP** | `zipfile` | `unzip` |
| **TAR/GZ** | `tarfile` | `tar` |
| **7z** | `py7zr` | `7z` |
| **RAR** | `rarfile` | `unrar` |

## Data Processing

### Structured Data
| Task | Python | CLI |
|------|--------|-----|
| **DataFrames** | `pandas`, `polars` | | polars 10x faster |
| **SQL Queries** | `sqlalchemy`, `sqlite3` | `sqlite3` |
| **GraphQL** | `gql`, `sgqlc` | |
| **Protobuf** | `protobuf` | `protoc` |

### Text Processing
| Task | Python | CLI |
|------|--------|-----|
| **Regex** | `re` | `rg`, `grep` |
| **Find/Replace** | `re.sub()` | `sd`, `sed` |
| **Diff** | `difflib` | `delta`, `difft` |
| **Fuzzy Match** | `fuzzywuzzy`, `rapidfuzz` | `fzf` |
| **NLP** | `spacy`, `nltk` | |
| **Tokenization** | `tiktoken` | | OpenAI tokenizer |

### Web/Network
| Task | Python | CLI |
|------|--------|-----|
| **HTTP Requests** | `httpx`, `requests` | `curl`, `http` |
| **Web Scraping** | `beautifulsoup4`, `selectolax` | `firecrawl` |
| **HTML Parsing** | `lxml`, `html5lib` | |
| **URL Parsing** | `urllib.parse`, `furl` | |
| **WebSockets** | `websockets`, `socketio` | `websocat` |
| **DNS** | `dnspython` | `dig` |

## Domain-Specific

### Scientific Computing
| Domain | Python |
|--------|--------|
| **Arrays/Math** | `numpy` |
| **Scientific** | `scipy` |
| **Statistics** | `statsmodels`, `scipy.stats` |
| **Symbolic Math** | `sympy` |
| **Plotting** | `matplotlib`, `plotly` |
| **Geospatial** | `geopandas`, `shapely` |

### Machine Learning
| Task | Python |
|------|--------|
| **General ML** | `scikit-learn` |
| **Deep Learning** | `pytorch`, `tensorflow` |
| **NLP Models** | `transformers` (HuggingFace) |
| **Computer Vision** | `torchvision`, `timm` |
| **Embeddings** | `sentence-transformers` |
| **LLM Inference** | `llama-cpp-python`, `vllm` |

### Cryptography
| Task | Python |
|------|--------|
| **Hashing** | `hashlib` |
| **Encryption** | `cryptography` |
| **JWT** | `pyjwt` |
| **Passwords** | `bcrypt`, `argon2-cffi` |
| **Secrets** | `secrets` (stdlib) |

### Games/Puzzles
| Domain | Python |
|--------|--------|
| **Chess** | `python-chess` |
| **Sudoku** | `py-sudoku` |
| **Graph Problems** | `networkx` |
| **Optimization** | `ortools`, `pulp` |

### Bioinformatics
| Task | Python |
|------|--------|
| **Sequences** | `biopython` |
| **Genomics** | `pysam`, `pyvcf` |
| **Protein** | `biotite` |

## CLI Tools (Modern Replacements)

| Instead of | Use | Why |
|------------|-----|-----|
| `find` | `fd` | 5x faster, simpler syntax |
| `grep` | `rg` (ripgrep) | 10x faster, respects .gitignore |
| `ls` | `eza` | Git status, icons, tree view |
| `cat` | `bat` | Syntax highlighting |
| `du` | `dust` | Visual tree sorted by size |
| `man` | `tldr` | Practical examples only |
| `sed` | `sd` | Simpler syntax |
| `diff` | `delta`, `difft` | Syntax highlighting, AST-aware |
| `top` | `btm` | Better graphs |
| `ps` | `procs` | Enhanced process view |

## Verification Commands

Before using a tool, verify it's available:

```bash
# Python packages
pip list | grep <package>
python -c "import <package>; print(<package>.__version__)"

# CLI tools
which <tool>
<tool> --version

# Install if missing
pip install <package>
# or
uv pip install <package>  # 10-100x faster
```

## Decision Tree

```
Need to process X?
├── Is X a standard file format?
│   └── Check "File Formats" section
├── Is X a data transformation?
│   └── Check "Data Processing" section
├── Is X domain-specific?
│   └── Check "Domain-Specific" section
└── Is X a CLI operation?
    └── Check "CLI Tools" section
```
