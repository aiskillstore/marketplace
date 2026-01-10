"""
Excel Generator
Wraps openpyxl/pandas to create .xlsx files.
"""

import os
import pandas as pd
from typing import List, Dict
from app.core.config import REPORTS_DIR

class ExcelGenerator:
    def __init__(self, output_dir: str = str(REPORTS_DIR)):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_excel(self, data: List[Dict[str, str]], filename: str) -> str:
        """
        Generates an Excel file from a list of dictionaries.
        """
        try:
            # Ensure filename ends with .xlsx
            if not filename.endswith(".xlsx"):
                filename += ".xlsx"
                
            if not data or not isinstance(data, list):
                raise ValueError("Empty excel data")
            has_row = any(isinstance(row, dict) and len(row) > 0 for row in data)
            if not has_row:
                raise ValueError("Empty excel rows")

            output_path = os.path.join(self.output_dir, filename)
            
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
            
            return output_path
        except Exception as e:
            print(f"Error generating Excel: {e}")
            return ""

excel_generator = ExcelGenerator()
