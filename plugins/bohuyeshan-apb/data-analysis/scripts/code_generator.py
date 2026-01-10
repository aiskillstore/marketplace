from typing import Dict, Any
from openai import AsyncOpenAI
import os

class CodeGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def _get_client(self) -> AsyncOpenAI:
        role_config = self.config.get("researcher") or {} # Re-use researcher config
        api_key = role_config.get("api_key") or os.getenv("OPENAI_API_KEY")
        base_url = role_config.get("base_url") or os.getenv("OPENAI_BASE_URL")
        
        if not api_key:
            from app.core.config import settings
            api_key = settings.OPENAI_API_KEY
            base_url = settings.OPENAI_BASE_URL

        return AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate_analysis_code(self, data_context: str, requirement: str) -> str:
        """Generates Python code to analyze data and create a chart."""
        client = self._get_client()
        sys_prompt = """You are a Python Data Analysis Expert.
Your task is to write a complete, runnable Python script that analyzes the provided data and generates a visualization.
- Use `pandas` for data manipulation.
- Assume a helper function `set_style()` is available to set the professional theme. CALL IT FIRST.
- The script must save the plot to a file named 'chart_output.png'.
- Output ONLY the python code block (```python ... ```).
"""
        user_prompt = f"""Data Context:
{data_context}

Requirement:
{requirement}
"""
        response = await client.chat.completions.create(
            model="gpt-4o", # Prefer stronger model for code
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response.choices[0].message.content
        # Extract code block
        if "```python" in content:
            content = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
             content = content.split("```")[1].split("```")[0].strip()
        return content
