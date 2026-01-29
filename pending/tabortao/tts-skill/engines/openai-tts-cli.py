#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI-TTS CLI Engine
对接OpenAI TTS API，支持高质量语音生成
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path
import configparser
import time
import re

def detect_language(text: str) -> str:
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    english_pattern = re.compile(r'[a-zA-Z]')
    chinese_count = len(chinese_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    return 'zh' if chinese_count > english_count else 'en'


def t(lang: str, zh: str, en: str) -> str:
    return zh if lang == 'zh' else en

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

class OpenAITTSClient:
    def __init__(self, config_file=None):
        self.config = configparser.ConfigParser()

        # 查找配置文件
        config_paths = [
            config_file,
            './openai-tts.config',
            str(Path(__file__).parent / 'openai-tts.config'),
            str(Path(__file__).parent.parent / 'openai-tts.config')
        ]

        config_loaded = False
        for path in config_paths:
            if path and os.path.exists(path):
                self.config.read(path, encoding='utf-8')
                config_loaded = True
                break

        if not config_loaded:
            # 默认配置
            self.config['OpenAI'] = {
                'api_key': '',
                'base_url': 'https://api.openai.com/v1',
                'voice': 'alloy',
                'model': 'tts-1',
                'speed': '1.0',
                'output_format': 'mp3'
            }

        # 从配置文件读取设置
        try:
            openai_config = self.config['OpenAI']
        except KeyError:
            openai_config = self.config['DEFAULT'] if 'DEFAULT' in self.config else {}

        self.api_key = openai_config.get('api_key', '')
        base_url = openai_config.get('base_url', 'https://api.openai.com/v1')
        self.api_url = f"{base_url.rstrip('/')}/audio/speech"
        self.default_voice = openai_config.get('voice', 'alloy')
        self.default_model = openai_config.get('model', 'tts-1')
        self.default_speed = float(openai_config.get('speed', '1.0'))
        self.output_format = openai_config.get('output_format', 'mp3')

        # 支持的语音
        self.supported_voices = {
            'alloy': {'zh': '中性平衡的声音', 'en': 'Neutral and balanced'},
            'echo': {'zh': '深沉有磁性的声音', 'en': 'Deep and resonant'},
            'fable': {'zh': '轻快活泼的声音', 'en': 'Light and lively'},
            'onyx': {'zh': '严肃有力的声音', 'en': 'Serious and powerful'},
            'nova': {'zh': '温暖女性的声音', 'en': 'Warm and feminine'},
            'shimmer': {'zh': '清晰悦耳的声音', 'en': 'Clear and bright'}
        }

        # 支持的模型
        self.supported_models = {
            'tts-1': {'zh': '标准质量 (快速)', 'en': 'Standard quality (fast)'},
            'tts-1-hd': {'zh': '高质量 (较慢)', 'en': 'High quality (slower)'}
        }

    def generate_speech(self, text, voice=None, model=None, speed=None, output_path=None):
        """生成语音"""
        def sanitize_filename_part(value: str) -> str:
            if not value:
                return "tts"
            value = value.strip().replace("\n", " ").replace("\r", " ")
            value = "_".join(value.split())
            invalid_chars = '<>:"/\\|?*'
            value = "".join(c for c in value if c not in invalid_chars)
            value = value.strip(" ._") or "tts"
            return value

        lang = detect_language(text)

        if not self.api_key:
            return False, t(lang, "❌ 未配置OpenAI API密钥，请在配置文件中设置api_key", "❌ OpenAI API key is not configured. Set api_key in the config file.")

        # 处理参数
        selected_voice = voice or self.default_voice
        selected_model = model or self.default_model
        selected_speed = speed or self.default_speed

        # 验证参数
        if selected_voice not in self.supported_voices:
            return False, t(lang, f"❌ 不支持的语音: {selected_voice}", f"❌ Unsupported voice: {selected_voice}")

        if selected_model not in self.supported_models:
            return False, t(lang, f"❌ 不支持的模型: {selected_model}", f"❌ Unsupported model: {selected_model}")

        if not 0.25 <= selected_speed <= 4.0:
            return False, t(lang, f"❌ 语速超出范围 (0.25-4.0): {selected_speed}", f"❌ Speed out of range (0.25-4.0): {selected_speed}")

        # 准备请求数据
        payload = {
            'model': selected_model,
            'input': text,
            'voice': selected_voice,
            'speed': selected_speed,
            'response_format': 'mp3'
        }

        try:
            voice_desc = self.supported_voices[selected_voice]['zh'] if lang == 'zh' else self.supported_voices[selected_voice]['en']
            model_desc = self.supported_models[selected_model]['zh'] if lang == 'zh' else self.supported_models[selected_model]['en']
            print(t(lang, f"🎙️ 使用语音: {selected_voice} ({voice_desc})", f"🎙️ Voice: {selected_voice} ({voice_desc})"))
            print(t(lang, f"🤖 模型: {selected_model} ({model_desc})", f"🤖 Model: {selected_model} ({model_desc})"))
            print(t(lang, f"📝 文本内容: {text[:50]}{'...' if len(text) > 50 else ''}", f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}"))
            print(t(lang, f"⚡ 语速: {selected_speed}", f"⚡ Speed: {selected_speed}"))

            # 发送请求
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                # 设置输出路径
                if not output_path:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    prefix = sanitize_filename_part(text[:6] if len(text) >= 6 else text)
                    filename = f"{timestamp}_{prefix}.mp3"
                    output_dir = Path(__file__).parent.parent / 'output'
                    output_dir.mkdir(exist_ok=True)
                    output_path = str(output_dir / filename)

                # 保存音频文件
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                return True, output_path
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                return False, t(lang, f"API请求失败 ({response.status_code}): {error_msg}", f"API request failed ({response.status_code}): {error_msg}")

        except requests.exceptions.RequestException as e:
            return False, t(lang, f"网络请求错误: {str(e)}", f"Network error: {str(e)}")
        except Exception as e:
            return False, t(lang, f"生成失败: {str(e)}", f"Generation failed: {str(e)}")

    def list_voices(self):
        """列出所有支持的语音"""
        print("🎙️ 支持的OpenAI TTS语音:")
        for voice, description in self.supported_voices.items():
            print(f"  {voice} -> {description['zh']}")
        print(f"\n默认语音: {self.default_voice}")

    def list_models(self):
        """列出支持的模型"""
        print("🤖 支持的TTS模型:")
        for model, description in self.supported_models.items():
            print(f"  {model} -> {description['zh']}")
        print(f"\n默认模型: {self.default_model}")

def main():
    parser = argparse.ArgumentParser(description='OpenAI-TTS CLI - OpenAI TTS服务')
    parser.add_argument('text', nargs='?', help='要转换为语音的文本内容')
    parser.add_argument('--voice', '-v', help='语音选择 (alloy, echo, fable, onyx, nova, shimmer)')
    parser.add_argument('--model', '-m', help='TTS模型 (tts-1, tts-1-hd)')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--text-file', '-f', help='从文本文件读取内容')
    parser.add_argument('--speed', '-s', type=float, help='语速 (0.25-4.0)')
    parser.add_argument('--list-voices', action='store_true', help='列出可用的语音')
    parser.add_argument('--list-models', action='store_true', help='列出可用的模型')
    parser.add_argument('--config', help='配置文件路径')

    args = parser.parse_args()

    # 初始化客户端
    client = OpenAITTSClient(args.config)

    if args.list_voices:
        client.list_voices()
        return

    if args.list_models:
        client.list_models()
        return

    # 获取文本内容
    text = ""
    if args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    elif args.text:
        text = args.text
    else:
        print("❌ 请提供文本内容或文本文件")
        parser.print_help()
        return

    if not text:
        print("❌ 文本内容不能为空")
        return

    lang = detect_language(text)

    # 生成语音
    success, result = client.generate_speech(
        text=text,
        voice=args.voice,
        model=args.model,
        speed=args.speed,
        output_path=args.output
    )

    if success:
        print(t(lang, f"✅ 语音生成成功: {result}", f"✅ Success: {result}"))
    else:
        print(t(lang, f"❌ {result}", f"❌ {result}"))

if __name__ == '__main__':
    main()
