# Survival Curve Risk Table Generator

Automatically align and add "Number at risk" tables below Kaplan-Meier survival curves, consistent with Clinical Oncology Journal standards.
## Install
```bash
pip install -r requirements.txt
```

## Quick Start
### 1. Create sample data
```bash
python scripts/main.py --create-sample-data sample_data.csv
```

### 2. Generate risk table
```bash
python scripts/main.py \
    --input sample_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --style NEJM \
    --output risk_table.png
```

### 3. Generate combination chart (KM curve + risk table)
```bash
python scripts/main.py \
    --input sample_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --combine \
    --output combined_figure.png
```

## Command line parameters
|parameter|illustrate|Example|
|------|------|------|
| `--input` |Enter data file path| `data.csv` |
| `--time-col` |time column name| `time` |
| `--event-col` |Event column name (1=event, 0=censored)| `event` |
| `--group-col` |Grouping column name| `treatment` |
| `--output` |Output file path| `risk_table.png` |
| `--style` |Journal style (NEJM/Lancet/JCO)| `NEJM` |
| `--time-points` |Custom time point| `0,6,12,18,24,30` |
| `--combine` |Generate combination diagram| - |
| `--show-censored` |Show censored number of people| - |

## Input data format
CSV format example:
```csv
time,event,treatment
12.5,1,Experimental
18.3,0,Experimental
24.0,1,Control
...
```

## Python API

```python
from scripts.main import RiskTableGenerator

# initialization
generator = RiskTableGenerator(style="NEJM")

# Load data
generator.load_data_from_file(
    "data.csv",
    time_col="time",
    event_col="event",
    group_col="treatment"
)

# Generate risk table
generator.generate_risk_table("risk_table.png")

# Generate combination diagram
generator.generate_combined_plot(output_path="combined.png")
```

## Journal style
- **NEJM**: New England Journal of Medicine style- **Lancet**: The Lancet style- **JCO**: Journal of Clinical Oncology style
## License
MIT License
