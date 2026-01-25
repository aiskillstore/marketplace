# 🎬 Media Downloader

> Smart media downloader - Automatically search and download images/video clips based on your description, with auto-trimming support.

[🇨🇳 中文文档](./README_CN.md)

---

## 🚀 What Can I Do?

| You say... | I will... |
|------------|-----------|
| "Download some cute cat pictures" | Search and download 5 cat images |
| "Find a 15-second ocean wave video" | Download a 15s ocean wave clip |
| "Get me a 30-second cooking video" | Download a trimmed cooking clip |
| "Download this YouTube video from 1:30 to 2:00" | Download and auto-trim the specified segment |

---

## ✨ Features

- 🖼️ **Image Download** - Search HD images from professional stock libraries
- 🎬 **Video Clips** - Get free commercial-use video footage
- 📺 **YouTube Download** - Download and trim support
- ✂️ **Smart Trimming** - Auto-crop to your desired length
- 🌍 **Bilingual** - Supports both Chinese and English commands

---

## ⚡ One-Line Install

In Claude Code, just say:

> **"Help me install https://github.com/yizhiyanhua-ai/media-downloader.git and all its dependencies"**

Claude will automatically:
- Download the skill to the correct location
- Install yt-dlp, ffmpeg and other dependencies
- Check installation status

Just click "Allow" when Claude asks for permission!

---

## 🔑 Configure API Key (Required for Image Downloads)

> 💡 **Note**: If you only need to download YouTube videos, you can skip this step!

Image downloads require a free API Key (like a "membership card" for stock photo sites):

1. Go to **https://www.pexels.com**, click **Join** to register (Google/Apple quick signup supported)
2. After signup, visit **https://www.pexels.com/api/**, click **Your API Key**
3. Copy the key, then tell Claude: **"Help me save my Pexels API Key to environment variables"**

When done, tell Claude **"Check the status of media-downloader"** to confirm everything is working.

---

## 📋 More API Keys (Optional)

> 💡 **Why do I need API Keys?**
>
> Think of an API Key as a "membership card" for stock photo websites. With it, you can search and download HD images and videos.
>
> **Good news**: Registration is completely free, and all assets are free for commercial use!

The quick install above only configured Pexels. If you want more image sources, you can register for these:

### 🟢 Pixabay (More Assets)

1. Go to **https://pixabay.com**
2. Click **Join** in the top right corner
3. After signup, visit **https://pixabay.com/api/docs/**
4. Your API Key will be displayed right on the page (in the green box)
5. Tell Claude: **"Help me save my Pixabay API Key to environment variables"**, then paste your key

### 🔵 Unsplash (More Artistic Images)

1. Go to **https://unsplash.com/developers**
2. Click **Register as a developer**
3. Create an Application (just give it any name)
4. Find and copy the **Access Key**
5. Tell Claude: **"Help me save my Unsplash API Key to environment variables"**

### 🔧 Having Issues?

Tell Claude: **"Check the status of media-downloader"**

Claude will tell you which tools are installed and which API Keys are configured. Just fix what's missing!

---

## 💬 Usage Examples

> ⚠️ **Important**: Before using, tell Claude **"Check the status of media-downloader"** to make sure all dependencies are installed!

### Download Images

```
"Download 5 starry sky images"
"Download 10 coffee shop photos"
"Find some landscape images suitable for wallpapers"
```

### Download Videos

> 💡 **Recommended**: If you need to download videos, **use YouTube first**! YouTube has rich content, high quality, and doesn't require an extra API Key.

```
"Download this video: https://youtube.com/watch?v=xxx"
"Download minute 2 to minute 3 of this YouTube video"
"Only download the audio from this video"
```

If you need short video clips from stock libraries:

```
"Download a city night video, under 30 seconds"
"Find me a 15-second ocean wave video"
"Find some natural scenery videos suitable for backgrounds"
```

---

## 📁 Download Location

By default, all files are saved to:

```
~/.claude/skills/media-downloader/downloads/
```

### Custom Download Directory

You can specify a custom download location using the `-o` or `--output` option:

```bash
# Download images to a specific folder
media_cli.py image "cats" -o ~/Pictures/cats

# Download videos to Desktop
media_cli.py video "sunset" -o ~/Desktop

# Download YouTube video to current directory
media_cli.py youtube "URL" -o .
```

Or simply tell me where you want the files:

```
"Download 5 cat images to my Desktop"
"Save the video to ~/Videos/project"
```

---

## ❓ FAQ

### Q: Why are there no image search results?
A: Please confirm API Key is configured. Run `status` command to check configuration status.

### Q: YouTube video download failed?
A: YouTube download doesn't need an API Key, but requires yt-dlp. Run `pip install yt-dlp` to install.

### Q: Video trimming doesn't work?
A: ffmpeg is required. macOS users run `brew install ffmpeg`.

### Q: Can these images/videos be used commercially?
A: Assets from Pexels, Pixabay, and Unsplash can all be used commercially for free, no attribution required (though attribution is appreciated).

---

## 🛠️ CLI Reference

For advanced users using command line directly:

```bash
# Check configuration status
media_cli.py status

# Download images
media_cli.py image "keywords" -n count -o output_dir

# Download stock videos
media_cli.py video "keywords" -d max_duration -n count

# Download YouTube video
media_cli.py youtube "URL" --start start_seconds --end end_seconds

# Search media (no download)
media_cli.py search "keywords" --type image/video/all

# Trim local video
media_cli.py trim input_file --start start --end end
```

---

## 📦 Supported Sources

| Source | Type | Features |
|--------|------|----------|
| Pexels | Images + Videos | High quality, frequently updated |
| Pixabay | Images + Videos | Large quantity, diverse categories |
| Unsplash | Images | Artistic, great for wallpapers |
| YouTube | Videos | Rich content, trimming support |

---

## 📄 License

MIT License

---

🎬 **Start using! Just tell me what images or videos you want!**
