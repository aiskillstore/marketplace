# nx-matting — 图片与视频抠图 Skill

基于 BiRefNet GGUF 模型的本地抠图技能，支持图片和视频背景移除，输出透明 PNG、MOV 或 WebM。

## 特点

- 本地推理，无需 Python / PyTorch / CUDA
- 支持图片（JPG/PNG/BMP/WebP）和视频（MP4/MOV/WebM）
- Lite 模型约 88.6 MB，Full 模型约 440 MB
- Windows x64 原生 C++ 推理

## 安装

### skills.sh

```bash
npx skills add xiaowu89/skill-matting --skill nx-matting
```

### GitHub 手动安装

```bash
git clone https://github.com/xiaowu89/skill-matting.git /tmp/sm
cp -r /tmp/sm/plugins/nx-matting/skills/nx-matting ~/.claude/skills/
rm -rf /tmp/sm
```

## 快速使用

```powershell
# 图片抠图
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/matting.ps1" image `
  -InputPath "C:\photos\portrait.jpg"

# 视频抠图
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/matting.ps1" video `
  -InputPath "C:\videos\dance.mp4"
```

## 依赖

- Windows x64
- PowerShell
- 首次使用联网下载模型和运行时（魔搭）
