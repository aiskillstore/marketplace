# Installation and Configuration

## System Requirements

### Hardware Requirements
- **GPU**: NVIDIA A6000 (48GB) minimum for video generation with talking-head
- **CPU**: Multi-core processor recommended for PDF processing and document conversion
- **RAM**: Minimum 16GB, 32GB recommended for large papers

### Software Requirements
- **Python**: 3.11 or higher
- **Conda**: Environment manager for dependency isolation
- **LibreOffice**: For document format conversion (e.g., PDF to PPTX)
- **Poppler utilities**: For PDF processing and manipulation

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/YuhangChen1/Paper2All.git
cd Paper2All
```

### 2. Create Conda Environment
```bash
conda create -n paper2all python=3.11
conda activate paper2all
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice poppler-utils
```

**macOS:**
```bash
brew install libreoffice poppler
```

**Windows:**
- Download and install LibreOffice from https://www.libreoffice.org/
- Download and install Poppler from https://github.com/oschwartz10612/poppler-windows

## API Configuration

Create a `.env` file in the project root directory with the following credentials:

### Required API Keys

**Option 1: OpenAI API**
```
OPENAI_API_KEY=your_openai_api_key_here
```

**Option 2: OpenRouter API** (Alternative to OpenAI)
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Optional API Keys

**Google Search API** (For automatic logo lookup)
```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

## Model Configuration

The system supports multiple LLM backends:

### Supported Models
- GPT-4 (Recommended for best quality)
- GPT-4.1 (Latest version)
- GPT-3.5-turbo (Faster, lower cost)
- Claude models via OpenRouter
- Other OpenRouter-supported models

### Model Selection

Specify models via `--model-choice` parameter or `--model_name_t` and `--model_name_v` parameters:
- Model choice 1: GPT-4 for all components
- Model choice 2: GPT-4.1 for all components
- Custom: Specify different models for text and visual processing respectively

## Verification

Test if installation was successful:

```bash
python pipeline_all.py --help
```

If successful, you will see a help menu with all available options.

## Troubleshooting

### Common Issues

**1. LibreOffice Not Found**
- Ensure LibreOffice is installed and added to system PATH
- Try running `libreoffice --version` to verify

**2. Poppler Utilities Not Found**
- Use `pdftoppm -v` to verify installation
- If needed, add Poppler's bin directory to PATH

**3. Video Generation GPU/CUDA Errors**
- Ensure NVIDIA drivers are updated to latest version
- Verify CUDA toolkit is installed
- Use `nvidia-smi` to check GPU memory

**4. API Key Errors**
- Verify `.env` file is in project root
- Check if API keys are valid and have sufficient balance
- Ensure no extra spaces or quotes around keys in `.env`

## Directory Structure

After installation, organize your workspace as follows:

```
Paper2All/
├── .env                  # API credentials
├── input/               # Place your paper files here
│   └── paper_name/      # Each paper in its own directory
│       └── main.tex     # LaTeX source or PDF
├── output/              # Generated output content
│   └── paper_name/
│       ├── website/     # Generated website files
│       ├── video/       # Generated video files
│       └── poster/      # Generated poster files
└── ...
```
