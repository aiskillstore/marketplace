#!/usr/bin/env python3
"""
代码统计器 - 分析代码库统计信息，包括行数、函数、类、注释率等
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any
import argparse


class CodeStats:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.stats: Dict[str, Any] = {
            'files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'by_extension': {}
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        file_stats = {
            'lines': 0,
            'code': 0,
            'comments': 0,
            'blank': 0,
            'functions': 0,
            'classes': 0,
            'imports': 0
        }

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()

            in_block_comment = False

            for line in lines:
                file_stats['lines'] += 1
                stripped = line.strip()

                # 空行
                if not stripped:
                    file_stats['blank'] += 1
                    continue

                # 块注释检测
                if '/*' in stripped and not in_block_comment:
                    in_block_comment = True
                    file_stats['comments'] += 1
                    continue

                if in_block_comment:
                    file_stats['comments'] += 1
                    if '*/' in stripped:
                        in_block_comment = False
                    continue

                # 行注释
                if stripped.startswith('#') or stripped.startswith('//'):
                    file_stats['comments'] += 1
                    continue

                if '#' in stripped and not stripped.startswith('"') and not stripped.startswith("'"):
                    file_stats['comments'] += 1
                    file_stats['code'] += 1
                    continue

                # 代码行
                file_stats['code'] += 1

                # 函数/类检测
                if 'def ' in line and 'class ' not in line:
                    file_stats['functions'] += 1
                elif 'class ' in line:
                    file_stats['classes'] += 1
                elif 'import ' in line or 'from ' in line:
                    file_stats['imports'] += 1

            return file_stats

        except Exception as e:
            print(f"⚠️  警告: 无法读取文件 {file_path}: {e}", file=sys.stderr)
            return file_stats

    def analyze_directory(self, directory: Path):
        """递归分析目录"""
        ignore_patterns = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules',
            'venv', 'env', '.venv', 'dist', 'build', '*.egg-info'
        }

        for item in directory.iterdir():
            # 忽略模式
            if any(pattern in str(item) for pattern in ignore_patterns):
                continue

            if item.is_dir():
                self.analyze_directory(item)
            elif item.is_file():
                # 支持的文件类型
                supported_ext = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.sh'}
                ext = item.suffix.lower()

                if ext in supported_ext:
                    file_stats = self.analyze_file(item)

                    # 更新全局统计
                    self.stats['files'] += 1
                    self.stats['total_lines'] += file_stats['lines']
                    self.stats['code_lines'] += file_stats['code']
                    self.stats['comment_lines'] += file_stats['comments']
                    self.stats['blank_lines'] += file_stats['blank']
                    self.stats['functions'] += file_stats['functions']
                    self.stats['classes'] += file_stats['classes']
                    self.stats['imports'] += file_stats['imports']

                    # 按扩展名分组
                    if ext not in self.stats['by_extension']:
                        self.stats['by_extension'][ext] = {
                            'files': 0,
                            'lines': 0,
                            'code': 0,
                            'comments': 0,
                            'blank': 0,
                            'functions': 0,
                            'classes': 0,
                            'imports': 0
                        }

                    ext_stats = self.stats['by_extension'][ext]
                    ext_stats['files'] += 1
                    ext_stats['lines'] += file_stats['lines']
                    ext_stats['code'] += file_stats['code']
                    ext_stats['comments'] += file_stats['comments']
                    ext_stats['blank'] += file_stats['blank']
                    ext_stats['functions'] += file_stats['functions']
                    ext_stats['classes'] += file_stats['classes']
                    ext_stats['imports'] += file_stats['imports']

    def calculate_complexity_score(self) -> float:
        """计算代码复杂度分数"""
        if self.stats['files'] == 0:
            return 0.0

        # 基于以下几个因素：
        # 1. 平均文件大小
        avg_file_size = self.stats['total_lines'] / self.stats['files']
        size_score = min(avg_file_size / 500, 1.0)  # 超过500行/文件扣分

        # 2. 注释率
        comment_ratio = self.stats['comment_lines'] / max(self.stats['total_lines'], 1)
        comment_score = 1.0 if comment_ratio > 0.1 else 0.5  # 注释率过低扣分

        # 3. 函数密度
        func_density = self.stats['functions'] / max(self.stats['files'], 1)
        func_score = min(func_density / 20, 1.0)  # 函数过多扣分

        # 综合评分（0-100）
        complexity = (size_score + comment_score + func_score) / 3 * 100
        return min(complexity, 100.0)

    def print_report(self):
        """打印分析报告"""
        print("📊 代码统计报告")
        print("=" * 60)
        print(f"项目路径: {self.project_path}")
        print("=" * 60)
        print()

        if self.stats['files'] == 0:
            print("⚠️  未找到支持的代码文件")
            return

        # 总体统计
        print("📁 总体统计:")
        print("-" * 60)
        print(f"文件总数: {self.stats['files']:,}")
        print(f"总行数: {self.stats['total_lines']:,}")
        print(f"代码行数: {self.stats['code_lines']:,} ({self.stats['code_lines']/self.stats['total_lines']*100:.1f}%)")
        print(f"注释行数: {self.stats['comment_lines']:,} ({self.stats['comment_lines']/self.stats['total_lines']*100:.1f}%)")
        print(f"空行行数: {self.stats['blank_lines']:,} ({self.stats['blank_lines']/self.stats['total_lines']*100:.1f}%)")
        print()
        print(f"函数总数: {self.stats['functions']:,}")
        print(f"类总数: {self.stats['classes']:,}")
        print(f"导入语句: {self.stats['imports']:,}")
        print()

        # 复杂度评分
        complexity = self.calculate_complexity_score()
        if complexity < 50:
            complexity_color = "\033[92m"  # 绿色
            complexity_level = "低"
        elif complexity < 75:
            complexity_color = "\033[93m"  # 黄色
            complexity_level = "中等"
        else:
            complexity_color = "\033[91m"  # 红色
            complexity_level = "高"

        print(f"代码复杂度: {complexity_color}{complexity:.1f} ({complexity_level})\033[0m")
        print()

        # 按文件类型统计
        if self.stats['by_extension']:
            print("📂 按文件类型统计:")
            print("-" * 60)
            print(f"{'类型':<10} {'文件数':>10} {'总行数':>12} {'代码行':>12} {'注释':>10} {'函数':>10} {'类':>8}")
            print("-" * 60)

            for ext, stats in sorted(self.stats['by_extension'].items()):
                print(f"{ext:<10} {stats['files']:>10,} {stats['lines']:>12,} {stats['code']:>12,} "
                      f"{stats['comments']:>10,} {stats['functions']:>10,} {stats['classes']:>8,}")

            print()

        # 健康评分
        health_score = 0
        health_issues = []

        # 注释率健康度
        comment_ratio = self.stats['comment_lines'] / max(self.stats['total_lines'], 1)
        if comment_ratio >= 0.1:
            health_score += 25
        else:
            health_issues.append(f"注释率偏低 ({comment_ratio*100:.1f}%，建议>10%)")

        # 文件大小健康度
        avg_file_size = self.stats['total_lines'] / self.stats['files']
        if avg_file_size <= 300:
            health_score += 25
        elif avg_file_size <= 500:
            health_score += 15
        else:
            health_issues.append(f"平均文件大小偏大 ({avg_file_size:.0f}行，建议<300)")

        # 空白行健康度
        blank_ratio = self.stats['blank_lines'] / max(self.stats['total_lines'], 1)
        if 0.05 <= blank_ratio <= 0.2:
            health_score += 25
        else:
            health_issues.append(f"空白行比例异常 ({blank_ratio*100:.1f}%)")

        # 函数分布健康度
        avg_funcs_per_file = self.stats['functions'] / self.stats['files']
        if avg_funcs_per_file <= 15:
            health_score += 25
        else:
            health_issues.append(f"平均函数数偏高 ({avg_funcs_per_file:.1f}个/文件)")

        print("🏥 代码健康度:")
        print("-" * 60)
        print(f"健康评分: {health_score}/100")

        if health_issues:
            print()
            print("⚠️  发现的问题:")
            for issue in health_issues:
                print(f"  - {issue}")
        else:
            print("✅ 代码健康状况良好")

        print()

        # 建议
        print("💡 建议:")
        print("-" * 60)

        if comment_ratio < 0.1:
            print("  - 增加代码注释，提高可维护性")

        if avg_file_size > 500:
            print("  - 考虑拆分大文件，遵循单一职责原则")

        if len(self.stats['by_extension']) > 5:
            print("  - 项目包含多种语言，注意依赖管理")
        elif len(self.stats['by_extension']) == 1:
            print("  - 单一语言项目，结构清晰")

        if self.stats['classes'] > 0:
            avg_methods_per_class = self.stats['functions'] / max(self.stats['classes'], 1)
            if avg_methods_per_class > 20:
                print("  - 类的职责可能过重，考虑拆分类")

        if health_score >= 80:
            print("  - ✅ 代码质量良好，继续保持")

        print()
        print("=" * 60)
        print("代码统计完成")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='代码统计器 - 分析代码库统计信息',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 code-stats.py .                    # 分析当前目录
  python3 code-stats.py /path/to/project     # 分析指定项目
  python3 code-stats.py . --json             # JSON格式输出
  python3 code-stats.py . --output report.md # 保存报告
        """
    )

    parser.add_argument(
        'project_path',
        nargs='?',
        default='.',
        help='项目路径（默认：当前目录）'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON格式输出'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出报告到文件'
    )

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"❌ 错误: 路径不存在: {args.project_path}")
        sys.exit(1)

    analyzer = CodeStats(args.project_path)
    analyzer.analyze_directory(Path(args.project_path))

    if args.json:
        import json
        print(json.dumps(analyzer.stats, indent=2))
    elif args.output:
        # 重定向输出到文件
        with open(args.output, 'w', encoding='utf-8') as f:
            old_stdout = sys.stdout
            sys.stdout = f
            try:
                analyzer.print_report()
            finally:
                sys.stdout = old_stdout
        print(f"✅ 报告已保存: {args.output}")
    else:
        analyzer.print_report()

    sys.exit(0)


if __name__ == '__main__':
    main()
