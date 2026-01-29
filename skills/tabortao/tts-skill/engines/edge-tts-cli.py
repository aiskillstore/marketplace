#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge-TTS CLI Engine
对接VoiceCraft在线TTS服务，支持多种微软语音
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path
import configparser
import re

def detect_language(text: str) -> str:
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    english_pattern = re.compile(r'[a-zA-Z]')
    chinese_count = len(chinese_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    return 'zh' if chinese_count > english_count else 'en'


def t(lang: str, zh: str, en: str) -> str:
    return zh if lang == 'zh' else en

class EdgeTTSClient:
    def __init__(self, config_file=None):
        self.config = configparser.ConfigParser()

        if config_file and os.path.exists(config_file):
            self.config.read(config_file, encoding='utf-8')
        else:
            # 默认配置
            self.config['DEFAULT'] = {
                'api_url': 'https://tts.wangwangit.com/v1/audio/speech',
                'voice': 'zh-CN-XiaoxiaoNeural',
                'speed': '1.0',
                'pitch': '0',
                'style': 'general'
            }

        self.api_url = self.config.get('DEFAULT', 'api_url')
        self.default_voice = self.config.get('DEFAULT', 'voice')
        self.default_speed = float(self.config.get('DEFAULT', 'speed'))
        self.default_pitch = self.config.get('DEFAULT', 'pitch')
        self.default_style = self.config.get('DEFAULT', 'style')

        # 支持的语音列表
        self.supported_voices = {
            # 女声
            'xiaoxiao': 'zh-CN-XiaoxiaoNeural',      # 晓晓 (温柔)
            'xiaoyi': 'zh-CN-XiaoyiNeural',          # 晓伊 (甜美)
            'xiaochen': 'zh-CN-XiaochenNeural',      # 晓辰 (知性)
            'xiaohan': 'zh-CN-XiaohanNeural',        # 晓涵 (优雅)
            'xiaomeng': 'zh-CN-XiaomengNeural',      # 晓梦 (梦幻)
            'xiaomo': 'zh-CN-XiaomoNeural',          # 晓墨 (文艺)
            'xiaoqiu': 'zh-CN-XiaoqiuNeural',        # 晓秋 (成熟)
            'xiaorui': 'zh-CN-XiaoruiNeural',        # 晓睿 (智慧)
            'xiaoshuang': 'zh-CN-XiaoshuangNeural',  # 晓双 (活泼)
            'xiaoxuan': 'zh-CN-XiaoxuanNeural',      # 晓萱 (清新)
            'xiaoyan': 'zh-CN-XiaoyanNeural',        # 晓颜 (柔美)
            'xiaoyou': 'zh-CN-XiaoyouNeural',        # 晓悠 (悠扬)
            'xiaozhen': 'zh-CN-XiaozhenNeural',      # 晓甄 (端庄)

            # 男声
            'yunxi': 'zh-CN-YunxiNeural',            # 云希 (清朗)
            'yunyang': 'zh-CN-YunyangNeural',        # 云扬 (阳光)
            'yunjian': 'zh-CN-YunjianNeural',        # 云健 (稳重)
            'yunfeng': 'zh-CN-YunfengNeural',        # 云枫 (磁性)
            'yunhao': 'zh-CN-YunhaoNeural',          # 云皓 (豪迈)
            'yunxia': 'zh-CN-YunxiaNeural',          # 云夏 (热情)
            'yunye': 'zh-CN-YunyeNeural',            # 云野 (野性)
            'yunze': 'zh-CN-YunzeNeural',            # 云泽 (深沉)
        }

        # 支持的语音风格
        self.supported_styles = [
            'general',           # 通用风格
            'assistant',         # 智能助手
            'chat',             # 聊天对话
            'customerservice',   # 客服专业
            'newscast',         # 新闻播报
            'affectionate',     # 亲切温暖
            'calm',             # 平静舒缓
            'cheerful',         # 愉快欢乐
            'gentle',           # 温和柔美
            'lyrical',          # 抒情诗意
            'serious',          # 严肃正式
        ]

    def find_voice_by_keyword(self, keyword):
        """根据关键词查找匹配的语音"""
        keyword = keyword.lower()

        # 精确匹配
        if keyword in self.supported_voices:
            return self.supported_voices[keyword]

        # 模糊匹配
        for voice_key, voice_id in self.supported_voices.items():
            if keyword in voice_key or voice_key in keyword:
                return voice_id

        # 如果没有匹配，返回默认语音
        return self.default_voice

    def generate_speech(self, text, voice=None, speed=None, pitch=None, style=None, output_path=None):
        """生成语音"""
        def sanitize_filename_part(value: str) -> str:
            if not value:
                return "tts"
            value = value.strip().replace("\n", " ").replace("\r", " ")
            value = re.sub(r"\s+", "_", value)
            value = re.sub(r'[<>:"/\\\\|?*]', "", value)
            value = value.strip(" ._")
            return value or "tts"

        lang = detect_language(text)

        # 处理参数
        if voice:
            selected_voice = self.find_voice_by_keyword(voice)
        else:
            selected_voice = self.default_voice

        selected_speed = speed or self.default_speed
        selected_pitch = pitch or self.default_pitch
        selected_style = style or self.default_style

        # 准备请求数据
        payload = {
            'input': text,
            'voice': selected_voice,
            'speed': selected_speed,
            'pitch': selected_pitch,
            'style': selected_style
        }

        try:
            print(t(lang, f"使用语音: {selected_voice}", f"Voice: {selected_voice}"))
            print(t(lang, f"文本内容: {text[:50]}{'...' if len(text) > 50 else ''}", f"Text: {text[:50]}{'...' if len(text) > 50 else ''}"))
            print(t(lang, f"参数: 语速={selected_speed}, 音调={selected_pitch}, 风格={selected_style}", f"Params: speed={selected_speed}, pitch={selected_pitch}, style={selected_style}"))

            # 发送请求
            response = requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                stream=True
            )

            if response.status_code == 200:
                # 设置输出路径
                if not output_path:
                    # 生成默认文件名：日期+文本前6个字
                    import time
                    date_str = time.strftime("%Y%m%d_%H%M%S")
                    prefix = text[:6] if len(text) >= 6 else text
                    prefix = sanitize_filename_part(prefix)
                    filename = f"{date_str}_{prefix}.mp3"

                    # 默认输出到上级目录的output文件夹
                    output_dir = Path(__file__).parent.parent / 'output'
                    output_dir.mkdir(exist_ok=True)
                    output_path = output_dir / filename
                else:
                    # 确保输出目录存在
                    output_path = Path(output_path)
                    output_path.parent.mkdir(exist_ok=True, parents=True)

                # 保存音频文件
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                return True, str(output_path)
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                return False, t(lang, f"API请求失败 ({response.status_code}): {error_msg}", f"API request failed ({response.status_code}): {error_msg}")

        except requests.exceptions.RequestException as e:
            return False, t(lang, f"网络请求错误: {str(e)}", f"Network error: {str(e)}")
        except Exception as e:
            return False, t(lang, f"生成失败: {str(e)}", f"Generation failed: {str(e)}")

    def list_voices(self):
        """列出所有支持的语音"""
        print("支持的语音列表:")
        print("\n女声:")
        female_voices = {k: v for k, v in self.supported_voices.items() if 'xia' in k}
        for key, voice_id in female_voices.items():
            name = voice_id.split('-')[-1].replace('Neural', '')
            print(f"  {key} -> {voice_id} ({name})")

        print("\n男声:")
        male_voices = {k: v for k, v in self.supported_voices.items() if 'yun' in k}
        for key, voice_id in male_voices.items():
            name = voice_id.split('-')[-1].replace('Neural', '')
            print(f"  {key} -> {voice_id} ({name})")

        print(f"\n默认语音: {self.default_voice}")

    def list_styles(self):
        """列出支持的语音风格"""
        print("支持的语音风格:")
        for style in self.supported_styles:
            print(f"  - {style}")

def main():
    parser = argparse.ArgumentParser(description='Edge-TTS CLI - VoiceCraft在线TTS服务')
    parser.add_argument('text', nargs='?', help='要转换为语音的文本内容')
    parser.add_argument('--voice', '-v', help='语音选择 (如: xiaoxiao, yunxi)')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--text-file', '-f', help='从文本文件读取内容')
    parser.add_argument('--speed', '-s', type=float, help='语速 (0.5-2.0)')
    parser.add_argument('--pitch', '-p', help='音调 (-50 到 50)')
    parser.add_argument('--style', help='语音风格')
    parser.add_argument('--list-voices', action='store_true', help='列出可用的语音')
    parser.add_argument('--list-styles', action='store_true', help='列出可用的语音风格')
    parser.add_argument('--config', help='配置文件路径')

    args = parser.parse_args()

    # 初始化客户端
    client = EdgeTTSClient(args.config)

    if args.list_voices:
        client.list_voices()
        return

    if args.list_styles:
        client.list_styles()
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
        speed=args.speed,
        pitch=args.pitch,
        style=args.style,
        output_path=args.output
    )

    if success:
        print(t(lang, f"语音生成成功: {result}", f"Success: {result}"))
    else:
        print(t(lang, f"生成失败: {result}", f"Failed: {result}"))

if __name__ == '__main__':
    main()
