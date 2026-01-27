#!/usr/bin/env python3
"""
将Markdown格式的测试用例转换为Xmind可导入的格式

使用方法：
    python convert_to_xmind.py input.md -o output.md

输出的Markdown采用缩进层级结构，可直接导入Xmind
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict


class XmindMarkdownConverter:
    """Xmind Markdown转换器"""
    
    def __init__(self, markdown_content: str):
        self.content = markdown_content
        self.outline = []
        
    def convert(self) -> str:
        """转换为Xmind可导入的Markdown格式"""
        lines = self.content.split('\n')
        xmind_lines = []
        current_indent = 0
        
        for line in lines:
            # 识别标题层级
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                content = line.lstrip('#').strip()
                
                # 跳过文档封面标题
                if level == 1 and any(keyword in content for keyword in ['测试用例集', '测试点清单']):
                    xmind_lines.append(f"# {content}")
                    continue
                
                # 转换为缩进格式
                indent = '\t' * (level - 2) if level > 1 else ''
                xmind_lines.append(f"{indent}- {content}")
                
            # 识别列表项
            elif re.match(r'^[-*+]\s+\[[ x]\]', line.strip()):
                # 任务列表
                content = re.sub(r'^[-*+]\s+\[[ x]\]\s+', '', line.strip())
                indent = '\t' * (current_indent + 1)
                xmind_lines.append(f"{indent}- {content}")
                
            elif re.match(r'^[-*+]\s+', line.strip()):
                # 普通列表
                content = re.sub(r'^[-*+]\s+', '', line.strip())
                indent = '\t' * (current_indent + 1)
                xmind_lines.append(f"{indent}- {content}")
            
            # 识别表格
            elif '|' in line and not line.strip().startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]  # 移除空元素
                
                if parts and '用例编号' not in line and '需求ID' not in line:
                    # 表格数据行转换为列表
                    for part in parts:
                        if part and part != '-':
                            indent = '\t' * (current_indent + 1)
                            xmind_lines.append(f"{indent}- {part}")
        
        return '\n'.join(xmind_lines)
    
    def convert_structured(self) -> str:
        """
        转换为结构化的Xmind格式（适合完整用例）
        
        结构：
        - 游戏测试用例集
            - 模块1
                - 功能1.1
                    - 用例编号
                        - 前置条件
                        - 操作步骤
                        - 预期结果
        """
        xmind_lines = ['# 游戏测试用例集\n']
        
        # 解析模块结构
        current_module = None
        current_function = None
        
        lines = self.content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 模块级别 (### 模块X：XXX)
            if re.match(r'^###\s+模块\d+[:：]', line):
                module_name = re.sub(r'^###\s+模块\d+[:：]\s*', '', line)
                xmind_lines.append(f"- {module_name}")
                current_module = module_name
                i += 1
                continue
            
            # 功能级别 (#### 功能X.X：XXX)
            elif re.match(r'^####\s+功能[\d.]+[:：]', line):
                function_name = re.sub(r'^####\s+功能[\d.]+[:：]\s*', '', line)
                xmind_lines.append(f"\t- {function_name}")
                current_function = function_name
                i += 1
                continue
            
            # 用例级别 (##### 用例 XXX-XXX-X：XXX)
            elif re.match(r'^#####\s+用例\s+[A-Z]+-\d{3}-[NBE][:：]', line):
                case_match = re.match(r'^#####\s+用例\s+([A-Z]+-\d{3}-[NBE])[:：](.+)', line)
                if case_match:
                    case_id = case_match.group(1)
                    case_title = case_match.group(2).strip()
                    xmind_lines.append(f"\t\t- {case_id}：{case_title}")
                    
                    # 解析用例内容
                    i += 1
                    case_content = self._parse_case_content(lines, i)
                    for content_line in case_content:
                        xmind_lines.append(f"\t\t\t{content_line}")
                    i += len(case_content)
                    continue
            
            i += 1
        
        return '\n'.join(xmind_lines)
    
    def _parse_case_content(self, lines: List[str], start_idx: int) -> List[str]:
        """解析用例内容"""
        content_lines = []
        i = start_idx
        current_section = None
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 遇到下一个用例或功能，停止
            if re.match(r'^#{3,5}\s+', line):
                break
            
            # 识别章节
            if re.match(r'\*\*(.+?)\*\*[:：]', line):
                section_match = re.match(r'\*\*(.+?)\*\*[:：]', line)
                current_section = section_match.group(1)
                content_lines.append(f"- {current_section}")
                i += 1
                continue
            
            # 列表项
            if re.match(r'^[-*+]\s+', line):
                item = re.sub(r'^[-*+]\s+\[[ x]\]\s+', '', line)
                item = re.sub(r'^[-*+]\s+', '', item)
                if item:
                    content_lines.append(f"\t- {item}")
            
            # 表格行
            elif '|' in line and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p and p != '-']
                for part in parts:
                    if not any(keyword in part for keyword in ['步骤', '操作', '测试数据', '异常情况']):
                        content_lines.append(f"\t- {part}")
            
            i += 1
        
        return content_lines
    
    def convert_quick_testpoints(self) -> str:
        """
        转换快速测试点格式
        
        结构：
        - 游戏测试点清单
            - 模块1
                - 功能点1
                    - 核心测试点
                        - 测试点1
                        - 测试点2
                    - 边界测试点
                    - 异常测试点
        """
        xmind_lines = ['# 游戏测试点清单\n']
        
        lines = self.content.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # 模块 (## 模块：XXX)
            if re.match(r'^##\s+模块[:：]', stripped):
                module = re.sub(r'^##\s+模块[:：]\s*', '', stripped)
                xmind_lines.append(f"- {module}")
                
            # 功能点 (### 功能点：XXX)
            elif re.match(r'^###\s+功能点[:：]', stripped):
                function = re.sub(r'^###\s+功能点[:：]\s*', '', stripped)
                xmind_lines.append(f"\t- {function}")
                
            # 测试点类型 (#### 🟢 核心测试点)
            elif re.match(r'^####\s+[🟢🟡🔴⚡🔒📱🎨]', stripped):
                type_name = re.sub(r'^####\s+[🟢🟡🔴⚡🔒📱🎨]\s*', '', stripped)
                type_name = re.sub(r'（.+?）', '', type_name)  # 移除括号说明
                xmind_lines.append(f"\t\t- {type_name}")
                
            # 测试点列表项
            elif re.match(r'^[-*+]\s+\[[ x]\]', stripped):
                testpoint = re.sub(r'^[-*+]\s+\[[ x]\]\s+', '', stripped)
                xmind_lines.append(f"\t\t\t- {testpoint}")
                
            # 待确认项 (## ❓ 待确认项)
            elif re.match(r'^##\s+❓\s*待确认项', stripped):
                xmind_lines.append(f"- 待确认项")
                
            # 待确认问题 (### 问题X：XXX)
            elif re.match(r'^###\s+问题\d+[:：]', stripped):
                question = re.sub(r'^###\s+问题\d+[:：]\s*', '', stripped)
                xmind_lines.append(f"\t- {question}")
        
        return '\n'.join(xmind_lines)


def detect_format_type(content: str) -> str:
    """检测Markdown格式类型"""
    if '测试点清单' in content or '核心测试点' in content:
        return 'quick'
    elif '用例编号' in content and '前置条件' in content:
        return 'full'
    else:
        return 'auto'


def convert_to_xmind_markdown(input_file: Path, output_file: Path, format_type: str = 'auto'):
    """转换为Xmind可导入的Markdown"""
    print(f"读取文件: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 自动检测格式
    if format_type == 'auto':
        format_type = detect_format_type(content)
        print(f"检测到格式类型: {format_type}")
    
    print("转换为Xmind格式...")
    converter = XmindMarkdownConverter(content)
    
    if format_type == 'quick':
        xmind_content = converter.convert_quick_testpoints()
    elif format_type == 'full':
        xmind_content = converter.convert_structured()
    else:
        xmind_content = converter.convert()
    
    print(f"写入文件: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xmind_content)
    
    print(f"✅ 转换完成! 输出文件: {output_file}")
    print(f"\n使用说明:")
    print(f"1. 打开Xmind软件")
    print(f"2. 选择 文件 > 导入 > Markdown")
    print(f"3. 选择生成的文件: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='将Markdown测试用例转换为Xmind可导入格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
格式类型:
    auto  - 自动检测（默认）
    full  - 完整用例格式
    quick - 快速测试点格式

示例:
    python convert_to_xmind.py test_cases.md
    python convert_to_xmind.py test_cases.md -o xmind_import.md
    python convert_to_xmind.py test_cases.md -t quick
        """
    )
    
    parser.add_argument('input', type=str, help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', type=str, help='输出文件路径（默认：原文件名_xmind.md）')
    parser.add_argument('-t', '--type', choices=['auto', 'full', 'quick'], 
                       default='auto', help='格式类型（默认：auto）')
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    
    if not input_file.exists():
        print(f"❌ 错误: 文件不存在 - {input_file}")
        return
    
    # 确定输出文件名
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = input_file.parent / f"{input_file.stem}_xmind.md"
    
    convert_to_xmind_markdown(input_file, output_file, args.type)


if __name__ == '__main__':
    main()
