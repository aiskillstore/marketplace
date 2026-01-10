#!/usr/bin/env python3
"""
依赖关系分析器
分析Python/JavaScript项目的依赖关系，生成可视化报告
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
import argparse

class DependencyAnalyzer:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.dependencies: Dict[str, Any] = {}
        self.issues: List[str] = []

    def analyze_python(self) -> Dict[str, Any]:
        """分析Python项目依赖"""
        try:
            if not (self.root / "requirements.txt").exists():
                return {}

            result = {
                "language": "python",
                "dependencies": [],
                "issues": []
            }

            # 读取requirements.txt
            req_file = self.root / "requirements.txt"
            lines = req_file.read_text().splitlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # 简单解析：django>=3.0, pandas==1.5.0
                    if "==" in line:
                        name, version = line.split("==", 1)
                        result["dependencies"].append({
                            "name": name,
                            "constraint": "==",
                            "version": version,
                            "type": "exact"
                        })
                    elif ">=" in line:
                        name, version = line.split(">=", 1)
                        result["dependencies"].append({
                            "name": name,
                            "constraint": ">=",
                            "version": version,
                            "type": "minimum"
                        })
                    else:
                        result["dependencies"].append({
                            "name": line,
                            "constraint": None,
                            "version": None,
                            "type": "any"
                        })

            # 检查常见安全问题
            for dep in result["dependencies"]:
                name = dep["name"].lower()
                if name in ["django", "flask"]:
                    result["issues"].append(f"⚠️  Web框架: {name}，建议检查是否为最新版本")
                if name == "requests":
                    result["issues"].append(f"ℹ️  HTTP库: {name}，考虑使用内置的httpx")

            return result

        except Exception as e:
            return {
                "language": "python",
                "error": str(e),
                "dependencies": []
            }

    def analyze_javascript(self) -> Dict[str, Any]:
        """分析JavaScript/Node.js项目依赖"""
        try:
            if not (self.root / "package.json").exists():
                return {}

            result = {
                "language": "javascript",
                "dependencies": [],
                "issues": []
            }

            # 读取package.json
            package_file = self.root / "package.json"
            package = json.loads(package_file.read_text())

            # 合并dependencies和devDependencies
            all_deps = {}
            all_deps.update(package.get("dependencies", {}))
            all_deps.update(package.get("devDependencies", {}))

            for name, version in all_deps.items():
                result["dependencies"].append({
                    "name": name,
                    "version": version,
                    "type": "exact" if version.startswith("^") or version.startswith("~") else "range"
                })

            # 检查常见安全问题
            for dep in result["dependencies"]:
                name = dep["name"].lower()
                if name == "lodash":
                    result["issues"].append(f"⚠️  lodash有已知漏洞，建议使用原生JS方法")
                if name == "express":
                    result["issues"].append(f"⚠️  Express: {name}，建议使用helmet增强安全")

            return result

        except Exception as e:
            return {
                "language": "javascript",
                "error": str(e),
                "dependencies": []
            }

    def visualize_report(self, results: Dict[str, Any]):
        """生成可视化报告"""
        print("# 📦 依赖关系分析报告")
        print("=" * 60)

        for lang, data in results.items():
            if not data or "error" in data:
                continue

            print(f"\n## {lang.upper()} 项目")
            print("-" * 60)

            deps = data.get("dependencies", [])
            print(f"\n依赖总数: {len(deps)}")

            if deps:
                print("\n### 依赖清单")
                print("| 包名 | 版本 | 类型 |")
                print("|------|------|------|")
                for dep in deps[:20]:  # 只显示前20个
                    name = dep.get("name", "unknown")
                    version = dep.get("version", "latest")
                    dep_type = dep.get("type", "unknown")
                    print(f"| {name} | {version} | {dep_type} |")

                if len(deps) > 20:
                    print(f"| ... | ... | ... |")
                    print(f"| <font color='gray'>共 {len(deps)} 个依赖</font> | | |")

            issues = data.get("issues", [])
            if issues:
                print("\n### ⚠️  发现的问题")
                for issue in issues:
                    print(f"- {issue}")
            else:
                print("\n### ✅ 未发现明显问题")

    def save_json(self, results: Dict[str, Any], output_path: Path):
        """保存JSON格式的详细报告"""
        output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"\n💾 JSON报告已保存: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="依赖关系分析器")
    parser.add_argument("project_dir", nargs="?", default=".", help="项目目录路径")
    parser.add_argument("-o", "--output", help="输出JSON报告到文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    project_path = Path(args.project_dir)
    if not project_path.exists():
        print(f"❌ 错误: 目录不存在: {project_path}")
        sys.exit(1)

    print("🔍 分析项目依赖关系...")
    print(f"项目路径: {project_path.absolute()}")
    print("=" * 60)

    analyzer = DependencyAnalyzer(project_path)

    # 分析Python
    python_results = analyzer.analyze_python()

    # 分析JavaScript
    js_results = analyzer.analyze_javascript()

    # 生成报告
    all_results = {
        "python": python_results,
        "javascript": js_results,
        "metadata": {
            "analyzed_at": "2025-11-14T10:00:00Z",
            "tool_version": "1.0.0",
            "analyzer": "CodeConscious"
        }
    }

    analyzer.visualize_report(all_results)

    # 保存JSON报告
    if args.output:
        output_path = Path(args.output)
        analyzer.save_json(all_results, output_path)
    else:
        # 默认保存到报告目录
        report_dir = project_path / "reports"
        report_dir.mkdir(exist_ok=True)
        analyzer.save_json(all_results, report_dir / "dependency-report.json")

    print("\n✅ 分析完成！")

if __name__ == "__main__":
    main()
