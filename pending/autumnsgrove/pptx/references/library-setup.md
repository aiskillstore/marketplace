# Library Setup & Installation

## Primary Library: python-pptx

**Installation:**
```bash
pip install python-pptx
# or with uv
uv pip install python-pptx
```

**Import:**
```python
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
```

**Documentation:**
- Official Docs: https://python-pptx.readthedocs.io/
- GitHub: https://github.com/scanny/python-pptx

## Supporting Libraries

### Pillow (PIL): Image Processing

Install:
```bash
pip install Pillow
```

Usage:
```python
from PIL import Image
from io import BytesIO

# Resize image before adding to presentation
img = Image.open('large_photo.jpg')
img.thumbnail((1920, 1080))  # Resize to max 1920x1080

# Save to bytes
img_bytes = BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Add to slide
pic = slide.shapes.add_picture(img_bytes, Inches(1), Inches(1), height=Inches(5))
```

### pandas: Data Preparation

Install:
```bash
pip install pandas
```

Usage:
```python
import pandas as pd

# Load data for charts and tables
df = pd.read_csv('sales_data.csv')

# Use for chart data
chart_data = CategoryChartData()
chart_data.categories = df['Quarter'].tolist()
chart_data.add_series('Sales', df['Amount'].tolist())
```

### matplotlib: Chart Generation

Install:
```bash
pip install matplotlib
```

Usage (convert matplotlib charts to images):
```python
import matplotlib.pyplot as plt
from io import BytesIO

# Create matplotlib chart
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [10, 20, 15, 25])

# Save to bytes
img_bytes = BytesIO()
fig.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
img_bytes.seek(0)
plt.close()

# Add to presentation
slide.shapes.add_picture(img_bytes, Inches(1), Inches(2), width=Inches(8))
```

## Complete Installation Script

```bash
#!/bin/bash
# Install all dependencies for PowerPoint automation

pip install python-pptx
pip install Pillow
pip install pandas
pip install matplotlib

# Verify installations
python -c "import pptx; print(f'python-pptx {pptx.__version__}')"
python -c "import PIL; print(f'Pillow {PIL.__version__}')"
python -c "import pandas; print(f'pandas {pandas.__version__}')"
python -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')"

echo "✅ All dependencies installed successfully"
```

## Virtual Environment Setup

```bash
# Create virtual environment
python -m venv pptx_env

# Activate (Linux/Mac)
source pptx_env/bin/activate

# Activate (Windows)
pptx_env\Scripts\activate

# Install dependencies
pip install python-pptx Pillow pandas matplotlib

# Save dependencies
pip freeze > requirements.txt
```
