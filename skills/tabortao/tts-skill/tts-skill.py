#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS-Skill 主入口
多引擎文本转语音技能的统一接口
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import time
import re

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def detect_language(text: str) -> str:
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    english_pattern = re.compile(r'[a-zA-Z]')
    chinese_count = len(chinese_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    return 'zh' if chinese_count > english_count else 'en'


def t(lang: str, zh: str, en: str) -> str:
    return zh if lang == 'zh' else en

class TTSSkill:
    def __init__(self):
        self.engines_dir = Path(__file__).parent / 'engines'
        self.assets_dir = Path(__file__).parent / 'assets'
        self.output_dir = Path(__file__).parent / 'output'
        self.supported_engines = {
            'qwen3-tts': 'qwen3-tts-cli.py',
            'edge-tts': 'edge-tts-cli.py',
            'openai-tts': 'openai-tts-cli.py'
        }

        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)

    def generate_output_filename(self, text, extension='wav'):
        """生成输出文件名：日期+文本前6个字"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 获取输入文本的前6个字
        prefix = text[:6] if len(text) >= 6 else text
        prefix = prefix.strip().replace("\n", " ").replace("\r", " ")
        prefix = "_".join(prefix.split())
        invalid_chars = '<>:"/\\|?*'
        prefix = "".join(c for c in prefix if c not in invalid_chars)
        prefix = prefix.strip(" ._") or "tts"

        return f"{timestamp}_{prefix}.{extension}"

    def show_help(self):
        """显示帮助信息"""
        help_text = """
TTS-Skill - 多引擎文本转语音技能

基本语法:
    /tts-skill [引擎] [文本内容] --voice [音色关键词] [其他参数]

引擎选择:
    qwen3-tts  - 本地音色克隆 (Qwen3-TTS)
    edge-tts   - 在线多语音 (VoiceCraft)
    openai-tts - 商业级质量 (OpenAI TTS)

使用示例:
    /tts-skill qwen3-tts "胜利在呼唤" --voice 赵信
    /tts-skill edge-tts "你好世界" --voice xiaoxiao
    /tts-skill openai-tts "Hello World" --voice alloy
    /tts-skill qwen3-tts --text-file "input/text.txt" --voice 寒冰射手

命令行示例 (Windows):
    python tts-skill.py qwen3-tts --text-file "F:\\Code\\MySkills\\tts-skill\\input\\text.txt" --voice 寒冰射手

常用音色:
    赵信, 寒冰射手, Lei, 布里茨 (本地音色)
    xiaoxiao, yunxi, xiaoyi, yunyang (在线语音)
    alloy, echo, nova, fable (OpenAI语音)

工具命令:
    --list-engines     列出所有引擎
    --list-voices      列出所有音色
    --install          安装Qwen3-TTS环境
    --help             显示此帮助信息

详细文档: 查看 SKILL.md 文件
"""
        print(help_text)

    def list_engines(self):
        """列出所有支持的引擎"""
        print("支持的TTS引擎:")
        for engine, filename in self.supported_engines.items():
            engine_path = self.engines_dir / filename
            status = "可用" if engine_path.exists() else "缺失"
            print(f"  {engine} -> {filename} {status}")

    def list_voices(self):
        """列出所有可用的音色"""
        print("可用音色列表:")

        # 列出assets目录下的音色
        print("\n本地音色 (Qwen3-TTS):")
        if self.assets_dir.exists():
            for audio_file in self.assets_dir.rglob('*.mp3'):
                relative_path = audio_file.relative_to(self.assets_dir)
                print(f"  - {audio_file.stem} ({relative_path})")

            for audio_file in self.assets_dir.rglob('*.wav'):
                if not audio_file.name.endswith('.mp3'):
                    relative_path = audio_file.relative_to(self.assets_dir)
                    print(f"  - {audio_file.stem} ({relative_path})")
        else:
            print("  assets目录不存在")

        # 列出在线音色
        print("\n在线音色 (VoiceCraft):")
        online_voices = {
            'xiaoxiao': '晓晓 (温柔女声)',
            'xiaoyi': '晓伊 (甜美女声)',
            'xiaochen': '晓辰 (知性女声)',
            'yunxi': '云希 (清朗男声)',
            'yunyang': '云扬 (阳光男声)',
            'yunjian': '云健 (稳重男声)'
        }
        for voice, description in online_voices.items():
            print(f"  - {voice} -> {description}")

        # 列出OpenAI音色
        print("\nOpenAI音色:")
        openai_voices = {
            'alloy': '中性平衡',
            'echo': '深沉磁性',
            'fable': '轻快活泼',
            'onyx': '严肃有力',
            'nova': '温暖女性',
            'shimmer': '清晰悦耳'
        }
        for voice, description in openai_voices.items():
            print(f"  - {voice} -> {description}")

    def run_engine(self, engine, args, lang='zh'):
        """运行指定的TTS引擎"""
        if engine not in self.supported_engines:
            print(t(lang, f"ERROR: 不支持的引擎: {engine}", f"ERROR: Unsupported engine: {engine}"))
            print(t(lang, "可用引擎:", "Available engines:"), ", ".join(self.supported_engines.keys()))
            return False

        engine_script = self.engines_dir / self.supported_engines[engine]
        if not engine_script.exists():
            print(t(lang, f"ERROR: 引擎脚本不存在: {engine_script}", f"ERROR: Engine script not found: {engine_script}"))
            return False

        try:
            # 构建命令
            cmd = [sys.executable, str(engine_script)] + args

            print(t(lang, f"启动 {engine} 引擎...", f"Starting engine: {engine} ..."))
            result = subprocess.run(cmd, cwd=str(self.engines_dir),
                                  encoding='utf-8', errors='replace',
                                  env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})

            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(t(lang, f"ERROR: 引擎执行失败: {e}", f"ERROR: Engine execution failed: {e}"))
            return False
        except Exception as e:
            print(t(lang, f"ERROR: 执行错误: {e}", f"ERROR: Execution error: {e}"))
            return False

    def install_qwen3_environment(self):
        """安装Qwen3-TTS环境"""
        qwen_script = self.engines_dir / 'qwen3-tts-cli.py'
        if not qwen_script.exists():
            print("ERROR: Qwen3-TTS脚本不存在")
            return False

        try:
            cmd = [sys.executable, str(qwen_script), '--install']
            result = subprocess.run(cmd, cwd=str(self.engines_dir))
            return result.returncode == 0
        except Exception as e:
            print(f"ERROR: 安装失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='TTS-Skill - 多引擎文本转语音技能', add_help=False)
    parser.add_argument('engine', nargs='?', help='TTS引擎 (qwen3-tts, edge-tts, openai-tts)')
    parser.add_argument('text', nargs='*', help='要转换的文本内容')
    parser.add_argument('--text-file', '-f', help='从文本文件读取内容')
    parser.add_argument('--voice', '-v', help='音色选择')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--list-engines', action='store_true', help='列出所有引擎')
    parser.add_argument('--list-voices', action='store_true', help='列出所有音色')
    parser.add_argument('--install', action='store_true', help='安装Qwen3-TTS环境')
    parser.add_argument('--help', '-h', action='store_true', help='显示帮助信息')

    # 捕获所有参数传递给引擎
    args, unknown = parser.parse_known_args()

    skill = TTSSkill()

    # 处理帮助命令
    if args.help or (not args.engine and len(sys.argv) == 1):
        skill.show_help()
        return

    # 处理工具命令
    if args.list_engines:
        skill.list_engines()
        return

    if args.list_voices:
        skill.list_voices()
        return

    if args.install:
        print("INFO: 正在安装Qwen3-TTS环境...")
        if skill.install_qwen3_environment():
            print("SUCCESS: 安装成功！")
        else:
            print("ERROR: 安装失败")
        return

    # 处理引擎调用
    if not args.engine:
        print("ERROR: 请指定TTS引擎")
        print("可用引擎:", ", ".join(skill.supported_engines.keys()))
        print("\n使用 --help 查看帮助信息")
        return

    input_text = None
    if args.text_file:
        text_path = Path(args.text_file).expanduser()
        if not text_path.is_absolute():
            text_path = (Path.cwd() / text_path).resolve()

        if not text_path.exists():
            print("ERROR: 找不到输入文本文件")
            print(f"  传入路径: {args.text_file}")
            print(f"  解析路径: {text_path}")
            print('示例: python tts-skill.py qwen3-tts --text-file "F:\\Code\\MySkills\\tts-skill\\input\\text.txt" --voice 寒冰射手')
            return

        try:
            input_text = text_path.read_text(encoding='utf-8-sig').strip()
        except UnicodeDecodeError:
            input_text = text_path.read_text(encoding='gbk', errors='replace').strip()
    elif args.text:
        input_text = ' '.join(args.text).strip()

    lang = detect_language(input_text) if input_text else 'zh'

    # 构建引擎参数
    engine_args = []

    # 添加文本内容
    if input_text:
        engine_args.append(input_text)

        # 如果没有指定输出文件，生成默认文件名
        if not args.output:
            default_filename = skill.generate_output_filename(input_text)
            default_output_path = skill.output_dir / default_filename
            engine_args.extend(['--output', str(default_output_path)])
            print(t(lang, f"📁 默认输出路径: {default_output_path}", f"📁 Default output path: {default_output_path}"))
        else:
            engine_args.extend(['--output', args.output])
    else:
        # 如果没有文本但有输出参数，直接传递
        if args.output:
            engine_args.extend(['--output', args.output])

    # 添加其他参数
    if args.voice:
        engine_args.extend(['--voice', args.voice])

    # 添加未知参数
    engine_args.extend(unknown)

    # 运行引擎
    start_time = time.perf_counter()
    success = skill.run_engine(args.engine, engine_args, lang=lang)
    total_seconds = time.perf_counter() - start_time

    if args.engine == 'qwen3-tts' and input_text:
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', input_text))
        total_chars = len(input_text)
        basis = chinese_chars if chinese_chars > 0 else total_chars
        basis_label = t(lang, "汉字", "Chinese characters") if chinese_chars > 0 else t(lang, "字符", "characters")
        per_unit = (total_seconds / basis) if basis > 0 else 0.0
        print(t(lang, "\n📊 运行统计:", "\n📊 Stats:"))
        print(t(lang, f"   总用时: {total_seconds:.2f} 秒", f"   Total time: {total_seconds:.2f} s"))
        if chinese_chars > 0:
            print(t(lang, f"   汉字数: {chinese_chars}", f"   Chinese chars: {chinese_chars}"))
        print(t(lang, f"   字符数: {total_chars}", f"   Total chars: {total_chars}"))
        print(t(lang, f"   平均每{basis_label}耗时: {per_unit:.3f} 秒", f"   Avg per {basis_label}: {per_unit:.3f} s"))

    if success:
        print(t(lang, f"\n✅ {args.engine} 引擎执行成功！", f"\n✅ Engine succeeded: {args.engine}"))
        print(t(lang, f"📂 输出目录: {skill.output_dir}", f"📂 Output dir: {skill.output_dir}"))
    else:
        print(t(lang, f"❌ {args.engine} 引擎执行失败", f"❌ Engine failed: {args.engine}"))
        sys.exit(1)

if __name__ == '__main__':
    main()
