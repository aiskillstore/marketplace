# Troubleshooting Reference

Common issues and solutions for PDF extraction and LaTeX poster generation.

## PDF Extraction Issues

### Problem: Empty text extraction

**Symptoms:**
- `page.extract_text()` returns empty string
- No content extracted from PDF

**Causes:**
1. PDF is image-based (scanned document)
2. Text is embedded as fonts not recognized by pdfplumber
3. Corrupted PDF file

**Solutions:**

**Solution 1: Use OCR for scanned PDFs:**
```python
from pdf2image import convert_from_path
import pytesseract

images = convert_from_path('paper.pdf', dpi=300)
text = ""
for image in images:
    text += pytesseract.image_to_string(image)
```

**Solution 2: Try alternative extraction methods:**
```python
# Method 1: extract_text()
text = page.extract_text()

# Method 2: extract_words()
words = page.extract_words()
text = ' '.join([w['text'] for w in words])

# Method 3: Use pdfminer.six
from pdfminer.high_level import extract_text
text = extract_text("paper.pdf")

# Method 4: Use pypdf
from pypdf import PdfReader
reader = PdfReader("paper.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

**Solution 3: Check if PDF is searchable:**
```bash
# Using pdffonts to check for embedded fonts
pdffonts paper.pdf

# If no fonts, PDF is image-based - use OCR
```

### Problem: Tables not extracting correctly

**Symptoms:**
- `extract_tables()` returns None or empty list
- Tables are merged with surrounding text
- Cells are misaligned

**Causes:**
1. Complex table layouts
2. Tables with merged cells
3. Tables spanning multiple pages

**Solutions:**

**Solution 1: Adjust extraction tolerance:**
```python
import pdfplumber

with pdfplumber.open("paper.pdf") as pdf:
    for page in pdf.pages:
        # Try different tolerance values
        tables = page.extract_tables(
            table_settings={
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "min_words_vertical": 3,
                "min_words_horizontal": 3,
            }
        )
```

**Solution 2: Use explicit table detection:**
```python
with pdfplumber.open("paper.pdf") as pdf:
    for page in pdf.pages:
        # Find table boundaries
        tables = page.find_tables()
        for table in tables:
            # Extract specific table region
            table_region = page.crop(table.bbox)
            table_data = table_region.extract_table()
```

**Solution 3: Manually merge split tables:**
```python
def merge_tables_across_pages(pdf_path):
    """Merge tables that span multiple pages"""
    all_tables = []
    current_table = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                if current_table is None:
                    current_table = table
                else:
                    # Check if continuation (same number of columns)
                    if len(current_table[0]) == len(table[0]):
                        # Remove duplicate header if present
                        if current_table[0] == table[0]:
                            table.pop(0)
                        current_table.extend(table)
                    else:
                        all_tables.append(current_table)
                        current_table = table

    if current_table:
        all_tables.append(current_table)

    return all_tables
```

### Problem: Text extraction is garbled

**Symptoms:**
- Random characters in extracted text
- Wrong order of text
- Special characters not displaying

**Causes:**
1. Font encoding issues
2. Right-to-left text
3. Complex formatting

**Solutions:**

**Solution 1: Specify encoding:**
```python
import pdfplumber

with pdfplumber.open("paper.pdf", laparams={"all_texts": True}) as pdf:
    for page in pdf.pages:
        text = page.extract_text(x_tolerance=2, y_tolerance=2)
```

**Solution 2: Handle special characters:**
```python
import re

def clean_extracted_text(text):
    """Clean and normalize extracted text"""
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Fix common extraction errors
    text = text.replace('ﬃ', 'ffi')
    text = text.replace('ﬂ', 'fl')

    return text
```

### Problem: OCR produces poor results

**Symptoms:**
- Many misspellings
- Numbers not recognized
- Mixed languages not handled

**Causes:**
1. Poor image quality
2. Wrong page segmentation mode
3. Language not specified

**Solutions:**

**Solution 1: Preprocess images:**
```python
import cv2
import numpy as np
from PIL import Image

def preprocess_image(image):
    """Improve image quality for OCR"""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Apply threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary, h=10)

    # Sharpen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)

    return Image.fromarray(sharpened)

# Use in OCR
images = convert_from_path("scanned.pdf", dpi=300)
for image in images:
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
```

**Solution 2: Use correct page segmentation mode:**
```python
# Try different segmentation modes
modes = {
    'psm6': 'Assume a single uniform block of text',
    'psm3': 'Fully automatic page segmentation',
    'psm4': 'Assume a single column of text',
    'psm5': 'Assume a single uniform block of vertically aligned text'
}

for mode_name, description in modes.items():
    custom_config = f'--oem 3 --{mode_name}'
    text = pytesseract.image_to_string(image, config=custom_config)
    print(f"{description}: {text[:100]}")
```

**Solution 3: Specify language:**
```python
# For English
text = pytesseract.image_to_string(image, lang='eng')

# For multiple languages
text = pytesseract.image_to_string(image, lang='eng+chi_sim')  # English + Simplified Chinese

# For scientific text
text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
```

## LaTeX Poster Issues

### Problem: Wrong page size

**Symptoms:**
- Poster is too small or too large
- Margins are excessive
- Content doesn't fit page

**Diagnosis:**
```bash
# Check PDF dimensions
pdfinfo poster.pdf | grep "Page size"
```

**Expected sizes:**
- A0: 2384 x 3370 points (841 x 1189 mm)
- A1: 1684 x 2384 points (594 x 841 mm)
- 36×48": 2592 x 3456 points

**Solutions:**

**beamerposter:**
```latex
% Correct setup for A0 portrait
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}

% Remove default margins
\setbeamersize{text margin left=5mm, text margin right=5mm}

% Alternative: Use geometry
\usepackage[margin=10mm]{geometry}
```

**tikzposter:**
```latex
% Correct setup for A0 portrait
\documentclass[
  25pt,                      % Font scaling
  a0paper,                   % Paper size
  portrait,                  % Orientation
  margin=10mm,               % Outer margins
  innermargin=15mm           % Space inside blocks
]{tikzposter}
```

**baposter:**
```latex
% Correct setup for A0 portrait
\documentclass[a0paper,portrait,fontscale=0.285]{baposter}

\begin{poster}{
  grid=false,
  columns=3,
  colspacing=1.5em
}{...}{...}
```

### Problem: Fonts too small

**Symptoms:**
- Text unreadable from distance
- Title appears tiny

**Solutions:**

**Increase scaling:**

beamerposter:
```latex
% Try different scale values
\usepackage[size=a0,scale=1.4]{beamerposter}  % Default
\usepackage[size=a0,scale=1.6]{beamerposter}  % Larger
\usepackage[size=a0,scale=1.8]{beamerposter}  % Even larger
```

tikzposter:
```latex
% Increase font size
\documentclass[30pt,a0paper]{tikzposter}  % Was 25pt
```

baposter:
```latex
% Increase fontscale
\documentclass[a0paper,fontscale=0.32]{baposter}  % Was 0.285
```

**Manual font size adjustment:**
```latex
% beamerposter
\setbeamerfont{title}{size=\VeryHuge}
\setbeamerfont{block title}{size=\huge}
\setbeamerfont{normal text}{size=\Large}

% TikZ
\tikzset{font={\fontsize{36}{40}\selectfont}}

% baposter (in documentclass options)
\documentclass[a0paper,fontscale=0.32]{baposter}
```

### Problem: Compilation errors

**Common error messages:**

**Error: "File `beamerposter.sty` not found"**
```bash
# Install missing package
tlmgr install beamerposter
```

**Error: "Undefined control sequence"**
```latex
% Usually missing package
\usepackage{graphicx}  % For images
\usepackage{booktabs}  % For tables
\usepackage{tikz}      % For graphics
```

**Error: "Overfull \hbox"**
```latex
% Text too wide for column
\begin{column}{0.48\paperwidth}  % Wider column
\end{column}

% Or use sloppy mode
\sloppy
```

**Error: "Underfull \vbox"**
```latex
% Not enough content in column
\vfill  % Fill vertical space

% Or adjust spacing
\vspace{2cm}  % Add specific space
```

### Problem: Colors not displaying

**Symptoms:**
- Colors appear black and white
- Custom colors not working
- Theme colors not applying

**Solutions:**

**Check color package:**
```latex
\usepackage{xcolor}  % Make sure xcolor is loaded

% Define custom colors
\definecolor{myblue}{RGB}{0,102,204}
\definecolor{myred}{RGB}{204,0,0}
```

**Verify theme loading:**
```latex
% beamerposter
\usetheme{Madrid}
\usecolortheme{beaver}  % Make sure this comes after theme

% tikzposter
\usetheme{Rays}
\usecolorstyle{Denmark}  % Make sure this comes after theme
```

**Test color rendering:**
```latex
\begin{center}
  \colorbox{red}{Red text}
  \colorbox{blue}{Blue text}
  \textcolor{green}{Green text}
\end{center}
```

### Problem: Images not appearing

**Symptoms:**
- Blank space where image should be
- Compilation error: "File not found"
- Low resolution output

**Solutions:**

**Check file path:**
```latex
% Use absolute path
\includegraphics{/full/path/to/image.png}

% Or set graphics path
\graphicspath{{./images/}{./figures/}}
\includegraphics{image.png}
```

**Check image format:**
```latex
% Supported formats
\includegraphics{figure.png}   % PNG
\includegraphics{figure.jpg}   % JPEG
\includegraphics{figure.pdf}   % PDF (best quality)
\includegraphics{figure.eps}   % EPS
```

**Ensure sufficient resolution:**
```bash
# Check image resolution
file image.png

# Should be at least 300 DPI at final size
# For A0 poster: ~9930 pixels wide minimum
```

**Troubleshoot missing file:**
```latex
% Add draft option to see placeholders
\usepackage[demo]{graphicx}  % Creates placeholder boxes

% Remove demo option when ready
\usepackage{graphicx}
```

### Problem: Content extends beyond page

**Symptoms:**
- Text cut off at edges
- Figures partially visible
- Compilation warning about overfull box

**Solutions:**

**Check margins:**
```latex
% Reduce margins
\setbeamersize{text margin left=5mm, text margin right=5mm}

% Or use geometry
\usepackage[margin=5mm]{geometry}
```

**Adjust column widths:**
```latex
% Ensure total width equals paper width
% For 3 columns: 3 × 0.32 + 2 × 0.02 = 1.00

\begin{columns}
  \begin{column}{0.32\paperwidth}  % Column 1
  \end{column}
  \begin{column}{0.32\paperwidth}  % Column 2
  \end{column}
  \begin{column}{0.32\paperwidth}  % Column 3
  \end{column}
\end{columns}
```

**Debug page boundaries:**
```latex
\usepackage{eso-pic}
\AddToShipoutPictureBG{
  \AtPageLowerLeft{
    \put(0,0){
      \framebox(\LenToUnit{\paperwidth},\LenToUnit{\paperheight}){}
    }
  }
}
```

## Output Quality Issues

### Problem: Blurry output

**Symptoms:**
- Text appears fuzzy
- Images are pixelated
- Print quality poor

**Solutions:**

**Check PDF quality:**
```bash
# Check page size
pdfinfo poster.pdf | grep "Page size"

# Should match expected dimensions
```

**Increase image resolution:**
```python
# Use high-DPI images
images = convert_from_path('paper.pdf', dpi=600)

# Save as high-resolution PNG
image.save('figure.png', dpi=(600, 600))
```

**Use vector graphics:**
```latex
% PDF format preferred for diagrams
\includegraphics{diagram.pdf}

% Or SVG converted to PDF
```

**Compilation settings:**
```bash
# Use high-quality compilation
pdflatex -interaction=nonstopmode -halt-on-error poster.tex

# Or use LuaLaTeX for better font rendering
lualatex poster.tex
```

### Problem: Colors look wrong in print

**Symptoms:**
- Colors appear washed out
- RGB/CMYK mismatch
- Colors darker/lighter than expected

**Solutions:**

**Understand color spaces:**
- RGB: For digital display (screen)
- CMYK: For print (ink-based printers)

**Convert RGB to CMYK:**
```latex
% Use CMYK colors
\definecolor{cmykblue}{cmyk}{1,0.5,0,0}

% Or convert PDF after compilation
gs -sDEVICE=pdfwrite -dColorConversionStrategy=CMYK \
   -dProcessColorModel=DeviceCMYK \
   -dCompatibilityLevel=1.4 \
   -dNOPAUSE -dBATCH \
   -sOutputFile=poster_cmyk.pdf \
   poster_rgb.pdf
```

**Test colors:**
```latex
% Print color test page
\begin{center}
  \colorbox{red}{Red}
  \colorbox{green}{Green}
  \colorbox{blue}{Blue}
  \colorbox{yellow}{Yellow}
\end{center}
```

**Consult printer:**
- Request color profile
- Use printer's preferred color space
- Get test print before final run

### Problem: File size too large

**Symptoms:**
- File over 50MB
- Difficult to email or upload
- Slow to open

**Solutions:**

**Optimize images:**
```python
from PIL import Image

def optimize_image(input_path, output_path, quality=85):
    """Reduce image file size"""
    img = Image.open(input_path)

    # Reduce resolution if very high
    if img.width > 4000:  # More than needed for A0
        img = img.resize((img.width//2, img.height//2), Image.LANCZOS)

    # Save with compression
    img.save(output_path, optimize=True, quality=quality)

optimize_image('large_image.png', 'optimized_image.png')
```

**Compress PDF:**
```bash
# Ghostscript compression
gs -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/printer \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=poster_compressed.pdf \
   poster.pdf

# Different quality levels:
# /screen  (72 DPI)   - smallest
# /ebook   (150 DPI)  - medium
# /printer (300 DPI)  - high quality
# /prepress (300 DPI, color preserving) - best quality
```

**Remove unnecessary content:**
```latex
% Don't embed fonts that are system fonts
% Use subset fonts

% Remove unused packages
```

## Debugging Techniques

### Enable Verbose Output

```bash
# LaTeX compilation with verbose output
pdflatex -interaction=nonstopmode -halt-on-error poster.tex

# Check log file for warnings
grep -i "warning\|error" poster.log

# View specific warnings
grep "Overfull\|Underfull" poster.log
```

### Test Compilation Stages

```bash
# Stage 1: Check syntax
pdflatex -draftmode poster.tex

# Stage 2: Generate DVI
latex poster.tex

# Stage 3: Create PDF
dvipdf poster.dvi

# Stage 4: Full compilation with bibliography
pdflatex poster.tex
bibtex poster
pdflatex poster.tex
pdflatex poster.tex
```

### Isolate Issues

```latex
% Comment out sections to find problematic code
% \begin{block}{Section}
%   Content
% \end{block}

% Or use \iffalse ... \fi to skip blocks
\iffalse
  Problematic code here
\fi
```

### Use Test Document

```latex
% Minimal working example
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4]{beamerposter}

\begin{document}
\begin{frame}
  \begin{center}
    \Huge Test Poster
  \end{center}
\end{frame}
\end{document}
```

## Getting Help

### Check Documentation

```bash
# LaTeX package documentation
texdoc beamerposter
texdoc tikzposter
texdoc baposter

# Python package documentation
python -m pydoc pdfplumber
python -m pydoc pypdf
```

### Online Resources

- **TeX Stack Exchange**: https://tex.stackexchange.com/
- **LaTeX Community**: https://www.latex-community.org/
- **Overleaf Documentation**: https://www.overleaf.com/learn
- **GitHub Issues**: Check package repositories

### Minimal Working Example

When seeking help, provide:
1. Minimal code that reproduces the issue
2. Error messages (full, not truncated)
3. LaTeX log file
4. List of packages used
5. Document class and options

Example:
```latex
% MWE for issue
\documentclass[a0paper,fontscale=0.285]{baposter}
\usepackage{graphicx}

\begin{poster}{
  grid=false,
  columns=3
}{...}{
  \headerbox{Test}{name=test,column=0,row=0}{
    Minimal content
  }
}
\end{poster}
```
