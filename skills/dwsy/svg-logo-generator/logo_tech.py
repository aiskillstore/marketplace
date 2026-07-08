#!/usr/bin/env python3
"""
Folder-Site Logo - Tech Modern Line Style
科技现代简线条风格
"""

import textwrap


def generate_tech_logo():
    """科技感线条风格 logo"""

    width, height = 512, 512

    # 科技蓝配色
    primary = "#0A84FF"
    secondary = "#64D2FF"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{primary};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{secondary};stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- 外层圆环 (细线) -->
  <circle cx="256" cy="256" r="230" fill="none" stroke="url(#g)" stroke-width="4" />

  <!-- 内部装饰点 -->
  <circle cx="256" cy="100" r="6" fill="{primary}" />
  <circle cx="412" cy="256" r="6" fill="{primary}" />
  <circle cx="256" cy="412" r="6" fill="{primary}" />
  <circle cx="100" cy="256" r="6" fill="{primary}" />

  <!-- 文件夹主体 (简线条) -->
  <g fill="none" stroke="url(#g)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
    <!-- 主框 -->
    <path d="M 140 180 L 220 180 L 250 210 L 372 210 L 372 370 L 140 370 Z" />
    <!-- 标签折角 -->
    <path d="M 140 180 L 200 180 L 230 210" />
    <!-- 内部文件线 -->
    <line x1="190" y1="260" x2="322" y2="260" stroke-width="6" />
    <line x1="190" y1="310" x2="270" y2="310" stroke-width="6" />
  </g>

  <!-- 科技感装饰: 右上角连接线 -->
  <g fill="none" stroke="url(#g)" stroke-width="3" stroke-linecap="round">
    <line x1="372" y1="210" x2="420" y2="162" />
    <circle cx="420" cy="162" r="4" fill="{primary}" stroke="none" />
  </g>
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Tech logo generated: {output}")
    return output


def generate_tech_v2():
    """科技感线条风格 v2 - 更极简"""

    width, height = 512, 512

    primary = "#007AFF"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 细圆环 -->
  <circle cx="256" cy="256" r="240" fill="none" stroke="{primary}" stroke-width="3" opacity="0.4" />

  <!-- 文件夹线条 -->
  <g fill="none" stroke="{primary}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round">
    <!-- 主轮廓 -->
    <path d="M 128 176 L 208 176 L 240 208 L 384 208 L 384 368 L 128 368 Z" />
    <!-- 内部线 -->
    <line x1="184" y1="256" x2="336" y2="256" />
    <line x1="184" y1="304" x2="272" y2="304" />
  </g>

  <!-- 装饰点 -->
  <circle cx="384" cy="208" r="8" fill="{primary}" />
  <circle cx="256" cy="112" r="5" fill="{primary}" opacity="0.5" />
  <circle cx="432" cy="256" r="5" fill="{primary}" opacity="0.5" />
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Tech logo v2 generated: {output}")
    return output


def generate_tech_v3():
    """科技感线条风格 v3 - 带斜切角"""

    width, height = 512, 512

    primary = "#5856D6"

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <!-- 外框 (带斜角) -->
  <path
    d="M 100 100 L 380 100 L 440 160 L 440 440 L 100 440 Z"
    fill="none"
    stroke="{primary}"
    stroke-width="4"
    stroke-linejoin="round"
    opacity="0.3"
  />

  <!-- 文件夹 (科技线条) -->
  <g fill="none" stroke="{primary}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">
    <!-- 主体 -->
    <path d="M 144 192 L 224 192 L 256 224 L 368 224 L 368 352 L 144 352 Z" />
    <!-- 内部文档线 -->
    <line x1="200" y1="264" x2="312" y2="264" />
    <line x1="200" y1="304" x2="272" y2="304" />
  </g>

  <!-- 科技装饰: 角落连接 -->
  <g stroke="{primary}" stroke-width="3">
    <line x1="440" y1="100" x2="440" y2="160" />
    <line x1="100" y1="100" x2="380" y2="100" />
    <line x1="440" y1="440" x2="368" y2="352" />
  </g>

  <!-- 装饰点 -->
  <circle cx="368" cy="224" r="6" fill="{primary}" />
  <circle cx="100" cy="100" r="5" fill="{primary}" opacity="0.5" />
  <circle cx="440" cy="100" r="5" fill="{primary}" opacity="0.5" />
</svg>'''

    output = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Tech logo v3 generated: {output}")
    return output


if __name__ == "__main__":
    # 使用 v2 版本 (最极简)
    generate_tech_v2()
