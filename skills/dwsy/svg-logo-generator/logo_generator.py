#!/usr/bin/env python3
"""
Folder-Site Logo Generator
生成现代简约的几何 SVG logo
"""

import textwrap


def generate_folder_logo():
    """生成 folder-site 项目 logo"""

    # 配置
    width, height = 512, 512

    # 颜色方案 - 现代蓝绿渐变
    primary_color = "#3B82F6"      # 蓝色 - 技术/专业
    secondary_color = "#10B981"    # 绿色 - 文档/知识
    accent_color = "#F59E0B"       # 琥珀色 - 强调
    bg_dark = "#1E293B"            # 深色背景
    text_color = "#FFFFFF"         # 白色文字

    # SVG Header
    svg_header = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- 渐变定义 -->
    <linearGradient id="folderGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{secondary_color};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="pageGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:0.95" />
      <stop offset="100%" style="stop-color:#F1F5F9;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="4" dy="8" stdDeviation="12" flood-color="{bg_dark}" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- 背景 -->
  <rect width="{width}" height="{height}" fill="none" />
'''

    # 几何元素
    shapes = textwrap.dedent(f'''
    <!-- 主文件夹形状 - 使用 path 创建带折角的文件夹 -->
    <g filter="url(#shadow)">
      <!-- 文件夹底部 -->
      <path d="M 64 160 L 200 160 L 220 180 L 448 180 L 448 420 L 64 420 Z"
            fill="url(#folderGradient)" />
      <!-- 文件夹标签页 -->
      <path d="M 64 160 L 180 160 L 200 180 L 180 180 L 180 160 Z"
            fill="{primary_color}" />
      <!-- 文件夹前盖（稍浅） -->
      <path d="M 64 200 L 200 200 L 220 220 L 448 220 L 448 420 L 64 420 Z"
            fill="url(#folderGradient)" opacity="0.3" />
    </g>

    <!-- 页面/文档图标从文件夹中飞出 -->
    <g transform="translate(256, 280)" filter="url(#shadow)">
      <!-- 页面主体 -->
      <rect x="-80" y="-100" width="160" height="200" rx="8"
            fill="url(#pageGradient)" />
      <!-- 页面折角 -->
      <path d="M 80 -100 L 80 -60 L 60 -60 L 60 -100 Z"
            fill="{secondary_color}" opacity="0.8" />
      <!-- 页面内容线（模拟文字） -->
      <rect x="-60" y="-60" width="100" height="8" rx="4" fill="#CBD5E1" />
      <rect x="-60" y="-40" width="120" height="6" rx="3" fill="#E2E8F0" />
      <rect x="-60" y="-20" width="100" height="6" rx="3" fill="#E2E8F0" />
      <rect x="-60" y="0" width="110" height="6" rx="3" fill="#E2E8F0" />
      <rect x="-60" y="20" width="80" height="6" rx="3" fill="#E2E8F0" />
      <!-- 代码/文档图标 -->
      <circle cx="0" cy="70" r="24" fill="{accent_color}" opacity="0.9"/>
      <path d="M -8 62 L 0 70 L 8 62 M -8 70 L 0 78 L 8 70"
            stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- 网站/链接图标（右上角） -->
    <g transform="translate(380, 120)">
      <circle r="36" fill="{accent_color}" opacity="0.9"/>
      <path d="M -12 -8 L -4 -8 L -4 4 L -12 4 Z M 4 -8 L 12 -8 L 12 4 L 4 4 Z"
            fill="white" opacity="0.9"/>
      <path d="M -4 16 L 0 20 L 4 16"
            stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- 装饰性圆点 -->
    <circle cx="140" cy="130" r="8" fill="{accent_color}" opacity="0.8"/>
    <circle cx="100" cy="380" r="6" fill="white" opacity="0.3"/>
    <circle cx="420" cy="360" r="10" fill="{secondary_color}" opacity="0.4"/>
''')

    # 关闭 SVG
    svg_footer = "\n</svg>"

    # 组装完整 SVG
    svg_content = svg_header + shapes + svg_footer

    # 输出文件
    output_path = "/Users/dengwenyu/Dev/AI/folder-site/public/logo.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✅ Logo generated: {output_path}")
    print(f"\n📐 尺寸: {width}x{height}")
    print(f"🎨 主色调: {primary_color} (蓝色)")
    print(f"🌿 辅助色: {secondary_color} (绿色)")
    print(f"✨ 强调色: {accent_color} (琥珀色)")
    return output_path


if __name__ == "__main__":
    generate_folder_logo()
