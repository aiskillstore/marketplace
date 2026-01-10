"""
代码片段解析器 - Code Parser

功能：
1. 从 Markdown 中提取代码块
2. 识别编程语言
3. 分析代码功能（函数名、参数等）
4. 生成代码元数据

版本: 2.0
"""

import re
from typing import List, Dict, Optional
from pathlib import Path


class CodeParser:
    """代码片段解析器"""

    def extract_code_blocks(self, content: str) -> List[Dict]:
        """
        从 Markdown 内容中提取代码块

        Args:
            content: Markdown 内容

        Returns:
            代码块列表，每个包含 {language, code, line_start}
        """
        # 匹配代码块: ```language\ncode\n```
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)

        code_blocks = []
        for match in matches:
            language = match.group(1) or 'text'
            code = match.group(2)

            code_blocks.append({
                'language': language.lower(),
                'code': code,
                'line_start': content[:match.start()].count('\n')
            })

        return code_blocks

    def analyze_code(self, code: str, language: str) -> Dict:
        """
        分析代码片段（简单实现，生产环境可用 LLM）

        Args:
            code: 代码内容
            language: 编程语言

        Returns:
            代码分析结果
        """
        analysis = {
            'language': language,
            'function_name': None,
            'parameters': [],
            'purpose': None,
            'complexity': 'simple',
            'dependencies': []
        }

        # Python 函数识别
        if language == 'python':
            func_match = re.search(r'def\s+(\w+)\s*\((.*?)\)', code)
            if func_match:
                analysis['function_name'] = func_match.group(1)
                params = func_match.group(2)
                if params:
                    analysis['parameters'] = [
                        p.strip().split(':')[0].split('=')[0].strip()
                        for p in params.split(',') if p.strip()
                    ]

            # 导入识别
            imports = re.findall(r'(?:from|import)\s+([\w.]+)', code)
            analysis['dependencies'] = list(set(imports))

        # JavaScript/TypeScript 函数识别
        elif language in ['javascript', 'typescript', 'js', 'ts']:
            # function foo() 或 const foo = () =>
            func_match = re.search(r'(?:function|const|let)\s+(\w+)', code)
            if func_match:
                analysis['function_name'] = func_match.group(1)

            # import 识别
            imports = re.findall(r'import.*from\s+[\'"](.+?)[\'"]', code)
            analysis['dependencies'] = list(set(imports))

        # 复杂度简单判断
        lines = code.split('\n')
        if len(lines) > 30:
            analysis['complexity'] = 'complex'
        elif len(lines) > 10:
            analysis['complexity'] = 'medium'

        return analysis


# 代码功能分析提示词（供 LLM 使用）
CODE_ANALYSIS_PROMPT = """
分析以下{language}代码片段：

```{language}
{code}
```

请提供：
1. 主要功能（一句话）
2. 函数/类名称
3. 参数列表
4. 使用场景
5. 复杂度评估（simple/medium/complex）

返回JSON格式。
"""
