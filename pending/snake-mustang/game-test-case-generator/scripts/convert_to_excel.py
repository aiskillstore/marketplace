#!/usr/bin/env python3
"""
将Markdown格式的测试用例转换为Excel格式

使用方法：
    python convert_to_excel.py input.md -o output.xlsx

依赖：
    pip install pandas openpyxl
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict
import pandas as pd


class TestCaseParser:
    """测试用例解析器"""
    
    def __init__(self, markdown_content: str):
        self.content = markdown_content
        self.test_cases = []
        
    def parse(self) -> List[Dict]:
        """解析Markdown内容为测试用例列表"""
        # 分割用例块（根据用例编号识别）
        pattern = r'#{2,5}\s+用例\s+([A-Z]+-\d{3}-[NBE])[:：](.+?)(?=#{2,5}\s+用例\s+[A-Z]+-\d{3}-[NBE]|$)'
        matches = re.finditer(pattern, self.content, re.DOTALL)
        
        for match in matches:
            case_id = match.group(1).strip()
            case_content = match.group(2).strip()
            
            test_case = self._parse_single_case(case_id, case_content)
            if test_case:
                self.test_cases.append(test_case)
        
        return self.test_cases
    
    def _parse_single_case(self, case_id: str, content: str) -> Dict:
        """解析单个测试用例"""
        case_data = {
            '用例编号': case_id,
            '用例标题': '',
            '所属模块': self._extract_module(case_id),
            '测试类型': '',
            '优先级': '',
            '前置条件': '',
            '操作步骤': '',
            '预期结果': '',
            '异常分支': '',
            '备注': ''
        }
        
        # 提取标题（第一行非标题内容）
        lines = content.split('\n')
        case_data['用例标题'] = lines[0].strip() if lines else ''
        
        # 提取测试类型
        type_match = re.search(r'\*\*测试类型\*\*[:：]\s*(.+)', content)
        if type_match:
            case_data['测试类型'] = type_match.group(1).strip()
        
        # 提取优先级
        priority_match = re.search(r'\*\*优先级\*\*[:：]\s*(.+)', content)
        if priority_match:
            case_data['优先级'] = priority_match.group(1).strip()
        
        # 提取前置条件
        precondition = self._extract_section(content, r'\*\*前置条件\*\*[:：]', r'\*\*操作步骤\*\*[:：]')
        case_data['前置条件'] = self._clean_bullets(precondition)
        
        # 提取操作步骤
        steps = self._extract_section(content, r'\*\*操作步骤\*\*[:：]', r'\*\*预期结果\*\*[:：]')
        case_data['操作步骤'] = self._clean_steps(steps)
        
        # 提取预期结果
        expected = self._extract_section(content, r'\*\*预期结果\*\*[:：]', r'\*\*异常分支\*\*[:：]')
        case_data['预期结果'] = self._clean_bullets(expected)
        
        # 提取异常分支
        exception = self._extract_section(content, r'\*\*异常分支\*\*[:：]', r'\*\*备注\*\*[:：]')
        case_data['异常分支'] = self._clean_bullets(exception)
        
        return case_data
    
    def _extract_module(self, case_id: str) -> str:
        """从用例编号提取模块名"""
        module_map = {
            'LOG': '账号系统',
            'REG': '账号系统',
            'COMBAT': '战斗系统',
            'SHOP': '商城系统',
            'BAG': '背包系统',
            'TASK': '任务系统',
            'SOCIAL': '社交系统',
            'PERF': '性能测试',
            'COMP': '兼容性测试',
        }
        prefix = case_id.split('-')[0]
        return module_map.get(prefix, '其他')
    
    def _extract_section(self, content: str, start_pattern: str, end_pattern: str = None) -> str:
        """提取内容段落"""
        if end_pattern:
            pattern = f'{start_pattern}(.+?)(?={end_pattern}|$)'
        else:
            pattern = f'{start_pattern}(.+?)$'
        
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ''
    
    def _clean_bullets(self, text: str) -> str:
        """清理列表项，转换为纯文本"""
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            # 移除列表标记
            line = re.sub(r'^[-*+]\s+\[[ x]\]\s+', '', line)
            line = re.sub(r'^[-*+]\s+', '', line)
            line = re.sub(r'^\d+\.\s+', '', line)
            line = re.sub(r'^✅\s+', '', line)
            if line:
                cleaned.append(line)
        return '\n'.join(cleaned)
    
    def _clean_steps(self, text: str) -> str:
        """清理操作步骤，保留序号"""
        lines = text.split('\n')
        cleaned = []
        step_num = 1
        
        for line in lines:
            line = line.strip()
            # 跳过表格分隔线和表头
            if '|' in line and ('步骤' in line or '---' in line):
                continue
            
            # 处理表格行
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    step_desc = parts[2]
                    test_data = parts[3] if len(parts) > 3 else ''
                    if step_desc and step_desc != '操作描述':
                        if test_data and test_data != '-':
                            cleaned.append(f"{step_num}. {step_desc}（测试数据：{test_data}）")
                        else:
                            cleaned.append(f"{step_num}. {step_desc}")
                        step_num += 1
            elif line and not line.startswith('#'):
                cleaned.append(f"{step_num}. {line}")
                step_num += 1
        
        return '\n'.join(cleaned)


def convert_markdown_to_excel(markdown_file: Path, output_file: Path):
    """转换Markdown测试用例为Excel"""
    print(f"读取文件: {markdown_file}")
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("解析测试用例...")
    parser = TestCaseParser(content)
    test_cases = parser.parse()
    
    if not test_cases:
        print("⚠️  未找到测试用例，请检查Markdown格式")
        return
    
    print(f"找到 {len(test_cases)} 个测试用例")
    
    # 转换为DataFrame
    df = pd.DataFrame(test_cases)
    
    # 调整列顺序
    columns = ['用例编号', '用例标题', '所属模块', '测试类型', '优先级', 
               '前置条件', '操作步骤', '预期结果', '异常分支', '备注']
    df = df[columns]
    
    # 写入Excel
    print(f"写入Excel: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='测试用例', index=False)
        
        # 设置列宽
        worksheet = writer.sheets['测试用例']
        worksheet.column_dimensions['A'].width = 15  # 用例编号
        worksheet.column_dimensions['B'].width = 30  # 用例标题
        worksheet.column_dimensions['C'].width = 12  # 所属模块
        worksheet.column_dimensions['D'].width = 12  # 测试类型
        worksheet.column_dimensions['E'].width = 8   # 优先级
        worksheet.column_dimensions['F'].width = 40  # 前置条件
        worksheet.column_dimensions['G'].width = 50  # 操作步骤
        worksheet.column_dimensions['H'].width = 40  # 预期结果
        worksheet.column_dimensions['I'].width = 30  # 异常分支
        worksheet.column_dimensions['J'].width = 20  # 备注
    
    print(f"✅ 转换完成! 输出文件: {output_file}")
    print(f"   共导出 {len(test_cases)} 个测试用例")


def main():
    parser = argparse.ArgumentParser(
        description='将Markdown格式的测试用例转换为Excel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python convert_to_excel.py test_cases.md -o output.xlsx
    python convert_to_excel.py test_cases.md
        """
    )
    
    parser.add_argument('input', type=str, help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', type=str, help='输出的Excel文件路径（默认：同名.xlsx）')
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    
    if not input_file.exists():
        print(f"❌ 错误: 文件不存在 - {input_file}")
        return
    
    # 确定输出文件名
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = input_file.with_suffix('.xlsx')
    
    # 检查依赖
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("❌ 缺少依赖包，请先安装:")
        print("   pip install pandas openpyxl")
        return
    
    convert_markdown_to_excel(input_file, output_file)


if __name__ == '__main__':
    main()
