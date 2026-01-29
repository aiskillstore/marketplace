#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-TTS CLI Engine
对接千问TTS模型，支持音色克隆和语音生成
"""

import os
import sys
import argparse
import subprocess
import json
import time
import threading
from pathlib import Path
import re
import configparser
from typing import Optional

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def detect_language(text):
    """检测文本语言，智能选择参考音频路径"""
    # 检测中文字符
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    # 检测英文字符
    english_pattern = re.compile(r'[a-zA-Z]')

    chinese_count = len(chinese_pattern.findall(text))
    english_count = len(english_pattern.findall(text))

    if chinese_count > english_count:
        return 'zh'
    else:
        return 'en'

def t(lang: str, zh: str, en: str) -> str:
    return zh if lang == 'zh' else en

def load_qwen3_config(config_file: Optional[str] = None) -> dict:
    config = configparser.ConfigParser()

    engines_dir = Path(__file__).resolve().parent
    config_paths = [
        config_file,
        str(engines_dir / 'qwen3-tts.config'),
        str(engines_dir.parent / 'qwen3-tts.config'),
        './qwen3-tts.config',
    ]

    for path in config_paths:
        if path and os.path.exists(path):
            config.read(path, encoding='utf-8')
            break

    section = config['Qwen3-TTS'] if 'Qwen3-TTS' in config else config['DEFAULT']

    model_dir_raw = section.get('model_dir', './Qwen3-TTS-12Hz-0.6B-Base')
    assets_dir_raw = section.get('assets_dir', '../assets')

    model_dir_path = Path(model_dir_raw)
    if not model_dir_path.is_absolute():
        model_dir_path = (engines_dir / model_dir_path).resolve()

    assets_dir_path = Path(assets_dir_raw)
    if not assets_dir_path.is_absolute():
        assets_dir_path = (engines_dir / assets_dir_path).resolve()

    return {
        'model_dir': str(model_dir_path),
        'assets_dir': str(assets_dir_path),
        'default_voice': section.get('default_voice', '赵信'),
        'output_format': section.get('output_format', 'wav'),
    }


def find_voice_reference(voice_keyword, assets_dir: Path):
    """根据关键词在assets目录中查找匹配的参考音频"""
    if not assets_dir.exists():
        return None, None

    # 支持的音频格式
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac']

    # 搜索匹配的音频文件
    for audio_file in assets_dir.iterdir():
        if audio_file.suffix.lower() in audio_extensions:
            # 检查文件名是否包含关键词
            if voice_keyword.lower() in audio_file.stem.lower():
                # 查找对应的文本文件
                text_file = audio_file.with_suffix('.txt')
                if text_file.exists():
                    return str(audio_file), str(text_file)

    # 如果没有找到匹配的，返回默认的赵信音色
    default_text = assets_dir / '赵信.txt'
    if default_text.exists():
        for ext in audio_extensions:
            default_audio = assets_dir / f'赵信{ext}'
            if default_audio.exists():
                return str(default_audio), str(default_text)

    # 如果连默认文件都不存在，返回第一个找到的音频文件
    for audio_file in assets_dir.iterdir():
        if audio_file.suffix.lower() in audio_extensions:
            text_file = audio_file.with_suffix('.txt')
            if text_file.exists():
                return str(audio_file), str(text_file)

    return None, None

def check_qwen3_environment():
    """检查Qwen3-TTS环境是否已配置"""
    try:
        # 检查是否在qwen3-tts虚拟环境中
        result = subprocess.run(['micromamba', 'run', '-n', 'qwen3-tts', 'python', '-c', 'import qwen_tts'],
                              capture_output=True, text=True)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_qwen3_environment(lang: str = 'zh'):
    """安装Qwen3-TTS环境"""
    print(t(lang, "正在配置Qwen3-TTS环境...", "Setting up Qwen3-TTS environment..."))

    try:
        # 1. 检查Python
        python_check = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if python_check.returncode != 0:
            print(t(lang, "❌ Python未安装，请先安装Python 3.12或更高版本", "❌ Python is not installed. Please install Python 3.12+ first."))
            return False

        # 2. 检查Micromamba
        try:
            subprocess.run(['micromamba', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(t(lang, "正在安装Micromamba...", "Installing micromamba..."))
            if os.name == 'nt':  # Windows
                ps_command = "Invoke-Expression ((Invoke-WebRequest -Uri https://micro.mamba.pm/install.ps1 -UseBasicParsing).Content)"
                subprocess.run(['powershell', '-Command', ps_command], check=True)
            else:  # Linux/Mac
                subprocess.run(['curl', '-Ls', 'https://micro.mamba.pm/install.sh'],
                             stdout=subprocess.PIPE, check=True)

        # 3. 创建虚拟环境
        print(t(lang, "正在创建qwen3-tts虚拟环境...", "Creating micromamba env: qwen3-tts ..."))
        subprocess.run(['micromamba', 'create', '-n', 'qwen3-tts', 'python=3.12', '-y'], check=True)

        # 4. 安装Qwen-TTS包
        print(t(lang, "正在安装Qwen3-TTS核心包...", "Installing qwen-tts ..."))
        subprocess.run(['micromamba', 'run', '-n', 'qwen3-tts', 'pip', 'install', '-U', 'qwen-tts'], check=True)

        # 5. 安装modelscope
        print(t(lang, "正在安装modelscope...", "Installing modelscope ..."))
        subprocess.run(['micromamba', 'run', '-n', 'qwen3-tts', 'pip', 'install', '-U', 'modelscope'], check=True)

        print(t(lang, "✅ Qwen3-TTS环境配置完成！", "✅ Qwen3-TTS environment is ready."))
        return True

    except subprocess.CalledProcessError as e:
        print(t(lang, f"❌ 环境配置失败: {e}", f"❌ Environment setup failed: {e}"))
        return False

def generate_speech_qwen3(reference_audio, reference_text, text, output_path, model_dir: str, lang: str):
    """使用Qwen3-TTS生成语音"""
    try:
        # 创建临时Python脚本文件
        engines_dir = Path(__file__).resolve().parent
        temp_script = engines_dir / 'temp_qwen3_generate.py'

        script_content = '''import sys
import os
import torch
import time
import threading
from pathlib import Path

# 添加当前目录到路径
sys.path.append(".")

# 设置UTF-8编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

lang = ''' + repr(lang) + '''

def t(zh: str, en: str) -> str:
    return zh if lang == 'zh' else en

try:
    # 导入必要的库
    print(t("📥 加载必要的库...", "📥 Loading required libraries..."))
    from qwen_tts import Qwen3TTSModel
    from modelscope import snapshot_download
    import torchaudio
    import numpy as np
    from tqdm import tqdm
    import soundfile as sf

    # 记录开始时间
    start_time = time.time()
    generation_start = time.time()

    print(t("⏰ 开始时间: ", "⏰ Start time: ") + time.strftime('%Y-%m-%d %H:%M:%S'))
    print(t("📝 输入文本: ", "📝 Input text: ") + ''' + text + ''' + " (" + str(len(''' + repr(text) + ''')) + t(" 字)", " chars)"))
    print(t("🎵 参考音频: ", "🎵 Reference audio: ") + os.path.basename(''' + repr(reference_audio) + ''') + "...")

    # 下载模型（如果未下载）
    print("\\n" + t("📥 下载/加载 Qwen3-TTS 模型...", "📥 Loading Qwen3-TTS model..."))
    configured_model_dir = Path(''' + repr(model_dir) + ''')
    if not configured_model_dir.is_absolute():
        configured_model_dir = (Path(__file__).resolve().parent / configured_model_dir).resolve()

    if configured_model_dir.exists():
        try:
            any_file = any(configured_model_dir.rglob('*'))
        except Exception:
            any_file = False

        if any_file:
            print(t("✅ 检测到本地模型目录，跳过下载: ", "✅ Local model directory detected, skipping download: ") + str(configured_model_dir))
            model_dir = str(configured_model_dir)
        else:
            print(t("⚠️  本地模型目录为空，将尝试下载: ", "⚠️  Local model directory is empty, will try to download: ") + str(configured_model_dir))
            model_dir = snapshot_download('Qwen/Qwen3-TTS-12Hz-0.6B-Base', local_dir=str(configured_model_dir))
    else:
        try:
            model_dir = snapshot_download('Qwen/Qwen3-TTS-12Hz-0.6B-Base', local_dir=str(configured_model_dir))
        except Exception as e:
            print(t("模型下载警告: ", "Model download warning: ") + str(e))
            model_dir = str(configured_model_dir)

    # 初始化模型
    print(t("🔧 初始化模型...", "🔧 Initializing model..."))
    tts = Qwen3TTSModel.from_pretrained(model_dir)

    # 读取参考文本
    print(t("📖 读取参考文本...", "📖 Reading reference transcript..."))
    ref_text_path = ''' + repr(reference_text) + '''
    with open(ref_text_path, 'r', encoding='utf-8') as f:
        ref_text = f.read().strip()

    # 进度跟踪变量
    progress_status = {'progress': 0, 'stop_progress': False}

    # 创建进度条和预计完成时间显示
    print("\\n" + t("🎵 正在生成语音...", "🎵 Generating audio..."))
    progress_bar = tqdm(
        total=100,
        desc=t("语音生成进度", "Generation progress"),
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_noinv_fmt}]",
        ncols=80
    )

    def update_progress():
        """更新进度条的后台线程"""
        while not progress_status['stop_progress'] and progress_status['progress'] < 100:
            elapsed = time.time() - generation_start
            # 基于文本长度估算进度（假设每字需要一定时间）
            estimated_total_time = ''' + str(len(text)) + ''' * 0.5  # 假设每字0.5秒
            progress_status['progress'] = min(99, int((elapsed / estimated_total_time) * 100))

            progress_text = t("语音生成进度", "Generation progress") + " (" + str(progress_status['progress']) + "%)"
            progress_bar.set_description(progress_text)

            progress_bar.update(max(0, progress_status['progress'] - progress_bar.n))
            time.sleep(0.5)

        # 完成时更新到100%
        if progress_status['progress'] < 100:
            progress_bar.update(100 - progress_bar.n)
        progress_bar.close()

    # 启动进度条线程
    progress_thread = threading.Thread(target=update_progress)
    progress_thread.start()

    # 生成语音
    ref_audio_path = ''' + repr(reference_audio) + '''
    result = tts.generate_voice_clone(
        text=''' + repr(text) + ''',
        ref_audio=ref_audio_path,
        ref_text=ref_text,
        x_vector_only_mode=False
    )

    # 处理不同的返回格式
    if isinstance(result, tuple) and len(result) == 2:
        wavs, sample_rate = result
    else:
        # 如果只返回音频数据，使用默认采样率
        wavs = result
        sample_rate = 22050  # 默认采样率

    # 停止进度条
    progress_status['stop_progress'] = True
    progress_thread.join()

    # 记录生成结束时间
    generation_end = time.time()
    generation_time = generation_end - generation_start

    # 保存结果
    output_path = ''' + repr(output_path) + '''
    sf.write(str(output_path), wavs[0], sample_rate)

    # 计算统计信息
    total_time = time.time() - start_time
    text_length = ''' + str(len(text)) + '''
    time_per_char = generation_time / text_length if text_length > 0 else 0

    # 输出结果
    print("\\n" + t("✅ 语音生成成功!", "✅ Generation succeeded!"))
    print(t("📁 输出文件: ", "📁 Output file: ") + str(output_path))
    print(t("🎵 采样率: ", "🎵 Sample rate: ") + str(sample_rate) + " Hz")
    print(t("⏱️  音频长度: ", "⏱️  Audio duration: ") + str(len(wavs[0]) / sample_rate) + t(" 秒", " seconds"))

    print("\\n" + t("📊 性能统计:", "📊 Stats:"))
    print(t("   总用时: ", "   Total time: ") + str(total_time/60) + t(" 分钟 (", " min (") + str(total_time) + t(" 秒)", " s)"))
    print(t("   生成用时: ", "   Generation time: ") + str(generation_time/60) + t(" 分钟 (", " min (") + str(generation_time) + t(" 秒)", " s)"))
    print(t("   文本长度: ", "   Text length: ") + str(text_length) + t(" 字", " chars"))
    print(t("   平均每字用时: ", "   Avg time per char: ") + str(time_per_char) + t(" 秒", " s"))

except Exception as e:
    # 确保进度条被正确关闭
    if 'progress_status' in locals():
        progress_status['stop_progress'] = True
        if 'progress_thread' in locals():
            progress_thread.join()
        if 'progress_bar' in locals():
            progress_bar.close()

    print("\\n" + t("❌ 错误: ", "❌ Error: ") + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

        # 写入临时文件
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 执行Python脚本
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        env['PYTHONUNBUFFERED'] = '1'

        cmd = ['micromamba', 'run', '-n', 'qwen3-tts', 'python', str(temp_script)]
        result = subprocess.run(cmd, env=env, cwd=str(engines_dir))
        return_code = result.returncode

        # 清理临时文件
        try:
            os.remove(temp_script)
        except:
            pass

        if return_code == 0:
            return True, output_path
        else:
            return False, t(lang, f"生成失败 (exit={return_code})", f"Generation failed (exit={return_code})")

    except Exception as e:
        return False, t(lang, f"执行错误: {str(e)}", f"Execution error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Qwen3-TTS CLI - 千问TTS语音生成工具')
    parser.add_argument('text', nargs='?', help='要转换为语音的文本内容')
    parser.add_argument('--voice', '-v', help='音色关键词（默认使用配置文件的 default_voice）')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--text-file', '-f', help='从文本文件读取内容')
    parser.add_argument('--install', action='store_true', help='安装Qwen3-TTS环境')
    parser.add_argument('--list-voices', action='store_true', help='列出可用的音色')
    parser.add_argument('--config', help='配置文件路径（默认读取 engines/qwen3-tts.config）')
    parser.add_argument('--model-dir', help='模型目录路径（优先级高于配置文件）')

    args = parser.parse_args()
    config = load_qwen3_config(args.config)
    model_dir = args.model_dir or config['model_dir']
    assets_dir = Path(config['assets_dir'])
    voice_keyword = args.voice or config['default_voice']

    if args.install:
        install_qwen3_environment()
        return

    if args.list_voices:
        print("可用的音色:")
        if not assets_dir.exists():
            return

        audio_extensions = {'.mp3', '.wav', '.m4a', '.flac'}
        stems = set()
        for audio_file in assets_dir.iterdir():
            if audio_file.suffix.lower() in audio_extensions:
                stems.add(audio_file.stem)

        for stem in sorted(stems):
            print(f"  - {stem}")
        return

    # 获取文本内容
    text = ""
    if args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    elif args.text:
        text = args.text
    else:
        print("ERROR: 请提供文本内容或文本文件")
        parser.print_help()
        return

    if not text:
        print("ERROR: 文本内容不能为空")
        return

    lang = detect_language(text)

    # 检测语言并查找音色
    reference_audio, reference_text = find_voice_reference(voice_keyword, assets_dir)

    if not reference_audio or not reference_text:
        print(t(lang, f"ERROR: 找不到匹配的音色文件: {voice_keyword}", f"ERROR: Cannot find matching voice files: {voice_keyword}"))
        return

    print(t(lang, f"使用音色: {Path(reference_audio).stem}", f"Voice: {Path(reference_audio).stem}"))
    print(t(lang, f"文本内容: {text[:50]}{'...' if len(text) > 50 else ''}", f"Text: {text[:50]}{'...' if len(text) > 50 else ''}"))

    # 设置输出路径
    if not args.output:
        # 生成默认文件名：日期+文本前6个字
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = text[:6] if len(text) >= 6 else text
        prefix = "".join(c for c in prefix if c.isalnum() or c in "_-")
        filename = f"{timestamp}_{prefix}.wav"

        # 默认输出到上级目录的output文件夹
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename
    else:
        output_path = args.output

    # 检查环境
    if not check_qwen3_environment():
        print(t(lang, "WARNING: Qwen3-TTS环境未配置，正在安装...", "WARNING: Qwen3-TTS environment is not set up. Installing..."))
        if not install_qwen3_environment(lang=lang):
            print(t(lang, "ERROR: 环境配置失败，请手动配置", "ERROR: Environment setup failed. Please install manually."))
            return

    # 生成语音
    success, result = generate_speech_qwen3(reference_audio, reference_text, text, output_path, model_dir=model_dir, lang=lang)

    if success:
        print(t(lang, f"SUCCESS: 语音生成成功: {result}", f"SUCCESS: Generated: {result}"))
    else:
        # Handle Unicode characters in error message
        try:
            print(t(lang, f"ERROR: 生成失败: {result}", f"ERROR: Failed: {result}"))
        except UnicodeEncodeError:
            # Fallback: encode with error handling
            safe_result = result.encode('gbk', errors='replace').decode('gbk')
            print(t(lang, f"ERROR: 生成失败: {safe_result}", f"ERROR: Failed: {safe_result}"))

if __name__ == '__main__':
    main()
