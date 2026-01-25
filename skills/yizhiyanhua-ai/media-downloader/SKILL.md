---
name: media-downloader
description: |
  智能媒体下载器。根据用户描述自动搜索和下载图片、视频片段，支持视频自动剪辑。
  Smart media downloader. Automatically search and download images/video clips based on user description, with auto-trimming support.
  触发方式 Triggers: "下载图片", "找视频", "download media", "download images", "find video", "/media"
---

# 🎬 Media Downloader / 智能媒体下载器

只需告诉我你想要什么，我就会帮你找到并下载相关的图片和视频！

Just tell me what you want, and I'll find and download relevant images and videos for you!

---

## 🚀 我能帮你做什么？/ What Can I Do?

| 你说... / You say... | 我会... / I will... |
|---------------------|---------------------|
| "下载一些可爱的猫咪图片" | 搜索并下载 5 张猫咪图片 |
| "Download sunset photos" | Search and download sunset images |
| "找一段海浪的视频，15秒左右" | 下载一段 15 秒的海浪视频 |
| "Get me a 30-second cooking video" | Download a trimmed cooking clip |
| "下载这个 YouTube 视频的 1:30-2:00" | 下载并自动剪辑指定片段 |

---

## ✨ 功能特点 / Features

- 🖼️ **图片下载** - 从专业图库搜索高清图片
- 🎬 **视频素材** - 获取免费商用视频片段
- 📺 **YouTube 下载** - 支持下载和剪辑
- ✂️ **智能剪辑** - 自动裁剪到你需要的长度
- 🌍 **中英双语** - 支持中文和英文指令

---

## 📋 首次使用设置 / First-Time Setup

### 第一步：检查基础工具 / Step 1: Check Basic Tools

在终端运行以下命令检查状态：

```bash
python ~/.claude/skills/media-downloader/media_cli.py status
```

如果显示 yt-dlp 或 ffmpeg 未安装，请运行：

```bash
# 安装 Python 依赖
pip install requests yt-dlp

# 安装视频处理工具 (macOS)
brew install ffmpeg
```

### 第二步：获取免费 API 密钥 / Step 2: Get Free API Keys

> 💡 **为什么需要 API 密钥？**
>
> 图片和视频素材来自 Pexels、Pixabay 等专业图库网站。这些网站提供免费的高质量素材，但需要注册账号获取一个"通行证"（API Key）才能使用他们的搜索服务。
>
> **好消息是**：注册完全免费，而且这些素材可以免费商用！

#### 🟠 获取 Pexels API Key（推荐，最简单）

1. 打开 https://www.pexels.com
2. 点击右上角 **Join** 注册账号（可用 Google/Apple 账号快速注册）
3. 注册后，访问 https://www.pexels.com/api/
4. 点击 **Your API Key** 按钮
5. 填写简单信息后，复制显示的 API Key

#### 🟢 获取 Pixabay API Key

1. 打开 https://pixabay.com
2. 点击右上角 **Join** 注册账号
3. 注册后，访问 https://pixabay.com/api/docs/
4. 页面中会显示你的 API Key（绿色框内）

#### 🔵 获取 Unsplash API Key（可选）

1. 打开 https://unsplash.com/developers
2. 点击 **Register as a developer**
3. 创建一个 Application
4. 在应用详情页找到 **Access Key**

### 第三步：保存 API 密钥 / Step 3: Save Your Keys

将获取到的密钥添加到你的终端配置文件中。

**macOS / Linux 用户**，编辑 `~/.zshrc` 或 `~/.bashrc`：

```bash
# Media Downloader API Keys
export PEXELS_API_KEY="你的Pexels密钥"
export PIXABAY_API_KEY="你的Pixabay密钥"
export UNSPLASH_ACCESS_KEY="你的Unsplash密钥"  # 可选
```

保存后运行 `source ~/.zshrc` 使配置生效。

### 第四步：验证设置 / Step 4: Verify Setup

```bash
python ~/.claude/skills/media-downloader/media_cli.py status
```

看到绿色 ✅ 就说明配置成功了！

---

## 💬 使用示例 / Examples

### 下载图片 / Download Images

```
"帮我下载 5 张星空的图片"
"Download 10 coffee shop photos"
"找一些适合做壁纸的风景图"
```

### 下载视频素材 / Download Video Clips

```
"下载一段城市夜景的视频，30秒以内"
"Find me a 15-second ocean wave video"
"找一些适合做背景的自然风光视频"
```

### YouTube 下载与剪辑 / YouTube Download & Trim

```
"下载这个视频：https://youtube.com/watch?v=xxx"
"下载这个 YouTube 视频的第 2 分钟到第 3 分钟"
"只下载这个视频的音频"
```

---

## 📁 下载位置 / Download Location

所有文件默认保存在：

```
~/.claude/skills/media-downloader/downloads/
```

---

## ❓ 常见问题 / FAQ

### Q: 为什么搜索图片没有结果？
A: 请确认已配置 API Key。运行 `status` 命令检查配置状态。

### Q: YouTube 视频下载失败？
A: YouTube 下载不需要 API Key，但需要安装 yt-dlp。运行 `pip install yt-dlp` 安装。

### Q: 视频剪辑功能不工作？
A: 需要安装 ffmpeg。macOS 用户运行 `brew install ffmpeg`。

### Q: 这些图片/视频可以商用吗？
A: Pexels、Pixabay、Unsplash 的素材都可以免费商用，无需署名（但署名是一种礼貌）。

---

## 🛠️ CLI 命令参考 / CLI Reference

供高级用户直接使用命令行：

```bash
# 检查配置状态
media_cli.py status

# 下载图片
media_cli.py image "关键词" -n 数量 -o 输出目录

# 下载视频素材
media_cli.py video "关键词" -d 最大时长 -n 数量

# 下载 YouTube 视频
media_cli.py youtube "URL" --start 开始秒数 --end 结束秒数

# 搜索媒体（不下载）
media_cli.py search "关键词" --type image/video/all

# 剪辑本地视频
media_cli.py trim 输入文件 --start 开始 --end 结束
```

---

## 📦 支持的素材来源 / Supported Sources

| 来源 Source | 类型 Type | 特点 Features |
|-------------|-----------|---------------|
| Pexels | 图片 + 视频 | 高质量，更新快 |
| Pixabay | 图片 + 视频 | 数量多，种类全 |
| Unsplash | 图片 | 艺术感强，适合壁纸 |
| YouTube | 视频 | 内容丰富，支持剪辑 |

---

🎬 **开始使用吧！直接告诉我你想要什么图片或视频！**

🎬 **Start using! Just tell me what images or videos you want!**
