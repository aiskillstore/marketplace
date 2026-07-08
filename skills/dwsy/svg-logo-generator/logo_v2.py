#!/usr/bin/env python3
"""
Folder-Site Logo Generator v2
极简现代风格
"""

import textwrap


def generate_simple_logo():
    """生成简洁现代的 logo"""

    width, height = 512, 512

    # 简洁的蓝紫色系
    primary = "#6366F1"      # Indigo
    secondary = "#8B5CF6"    # Violet
    dark = "#1E1B4B"         # Dark indigo
    white = "#FFFFFF"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{primary};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{secondary};stop-opacity:1" />
    </linearGradient>
    <filter id="s" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="{dark}" flood-opacity="0.25"/>
    </filter>
  </defs>

  <!-- 背景圆 -->
  <circle cx="256" cy="256" r="240" fill="url(#g)" filter="url(#s)" />

  <!-- 文件夹图标 -->
  <g fill="none" stroke="{white}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round">
    <!-- 文件夹主体 -->
    <path d="M 120 170 L 200 170 L 230 200 L 392 200 L 392 380 L 120 380 Z" />
    <!-- 标签 -->
    <path d="M 120 170 L 180 170 L 210 200" />
    <!-- 内部页面线 -->
    <path d="M 170 260 L 342 260" stroke-width="16" opacity="0.6" />
    <path d="M 170 300 L 310 300" stroke-width="16" opacity="0.6" />
    <path d="M 170 340 L 260 340" stroke-width="16" opacity="0.6" />
  </g>
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Logo v2 generated: {output}")
    return output


def generate_circle_logo():
    """极简圆形 logo"""

    width, height = 512, 512

    primary = "#3B82F6"
    white = "#FFFFFF"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 蓝色圆形背景 -->
  <circle cx="256" cy="256" r="240" fill="{primary}" />

  <!-- 白色文件夹图标 (简洁线条) -->
  <g fill="none" stroke="{white}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round">
    <!-- 主轮廓 -->
    <path d="M 130 180 L 210 180 L 240 210 L 382 210 L 382 360 L 130 360 Z" />
    <!-- 内部横线 -->
    <line x1="170" y1="260" x2="342" y2="260" />
    <line x1="170" y1="310" x2="280" y2="310" />
  </g>
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Circle logo generated: {output}")
    return output


def generate_fs_logo():
    """FS 字母组合 logo"""

    width, height = 512, 512

    primary = "#10B981"
    dark = "#064E3B"
    white = "#FFFFFF"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 绿色渐变背景 -->
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#34D399;stop-opacity:1" />
      <stop offset="100%" style="stop-color:{primary};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="64" fill="url(#g)" />

  <!-- F -->
  <text x="160" y="380" font-family="system-ui, sans-serif" font-size="280" font-weight="bold" fill="{white}">F</text>

  <!-- S -->
  <text x="270" y="380" font-family="system-ui, sans-serif" font-size="280" font-weight="bold" fill="{dark}" opacity="0.9">S</text>
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ FS letter logo generated: {output}")
    return output


def generate_minimal_folder():
    """极简文件夹 logo - 推荐版本"""

    width, height = 512, 512

    primary = "#0EA5E9"
    white = "#FFFFFF"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 简洁蓝色圆角矩形 -->
  <rect x="60" y="100" width="392" height="312" rx="40" fill="{primary}" />

  <!-- 文件夹标签 -->
  <path d="M 60 140 L 180 140 L 210 170 L 452 170 L 452 380 L 60 380 Z" fill="white" opacity="0.3" />

  <!-- 简洁线条装饰 -->
  <g stroke="{white}" stroke-width="20" stroke-linecap="round" opacity="0.9">
    <line x1="120" y1="240" x2="392" y2="240" />
    <line x1="120" y1="300" x2="300" y2="300" />
  </g>
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Minimal folder logo generated: {output}")
    return output


if __name__ == "__main__":
    # 使用极简版本
    generate_minimal_folder()
