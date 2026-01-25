#!/usr/bin/env python3
"""
Media Downloader - 智能媒体下载器
支持图片、视频搜索下载和自动剪辑
"""
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import quote_plus

# 尝试导入 requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# 配置
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(SKILL_DIR, 'downloads')
CACHE_DIR = os.path.join(SKILL_DIR, 'cache')

# 确保目录存在
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# API Keys (可以从环境变量获取)
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', '')
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY', '')


class ImageDownloader:
    """图片下载器"""

    def __init__(self):
        self.session = requests.Session() if REQUESTS_AVAILABLE else None

    def search_pexels(self, query: str, count: int = 5) -> List[Dict]:
        """从 Pexels 搜索图片"""
        if not PEXELS_API_KEY:
            return []

        url = f"https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page={count}"
        headers = {"Authorization": PEXELS_API_KEY}

        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "url": photo["src"]["large"],
                        "original": photo["src"]["original"],
                        "photographer": photo["photographer"],
                        "source": "pexels",
                        "id": photo["id"],
                    }
                    for photo in data.get("photos", [])
                ]
        except Exception as e:
            print(f"Pexels 搜索失败: {e}")
        return []

    def search_unsplash(self, query: str, count: int = 5) -> List[Dict]:
        """从 Unsplash 搜索图片"""
        if not UNSPLASH_ACCESS_KEY:
            return []

        url = f"https://api.unsplash.com/search/photos?query={quote_plus(query)}&per_page={count}"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "url": photo["urls"]["regular"],
                        "original": photo["urls"]["full"],
                        "photographer": photo["user"]["name"],
                        "source": "unsplash",
                        "id": photo["id"],
                    }
                    for photo in data.get("results", [])
                ]
        except Exception as e:
            print(f"Unsplash 搜索失败: {e}")
        return []

    def search_pixabay(self, query: str, count: int = 5) -> List[Dict]:
        """从 Pixabay 搜索图片"""
        if not PIXABAY_API_KEY:
            return []

        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={quote_plus(query)}&per_page={count}&image_type=photo"

        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "url": hit["largeImageURL"],
                        "original": hit["largeImageURL"],
                        "photographer": hit["user"],
                        "source": "pixabay",
                        "id": hit["id"],
                    }
                    for hit in data.get("hits", [])
                ]
        except Exception as e:
            print(f"Pixabay 搜索失败: {e}")
        return []

    def search_all(self, query: str, count: int = 5) -> List[Dict]:
        """从所有来源搜索图片"""
        results = []
        results.extend(self.search_pexels(query, count))
        results.extend(self.search_unsplash(query, count))
        results.extend(self.search_pixabay(query, count))
        return results[:count]

    def download(self, url: str, filename: str, output_dir: str = None) -> Optional[str]:
        """下载图片"""
        if not REQUESTS_AVAILABLE:
            print("❌ 需要安装 requests: pip install requests")
            return None

        output_dir = output_dir or DOWNLOADS_DIR
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        try:
            resp = self.session.get(url, timeout=30, stream=True)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filepath
        except Exception as e:
            print(f"下载失败: {e}")
        return None


class VideoDownloader:
    """视频下载器"""

    def __init__(self):
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        self.ytdlp_available = self._check_ytdlp()
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ytdlp(self) -> bool:
        """检查 yt-dlp 是否可用"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_ffmpeg(self) -> bool:
        """检查 ffmpeg 是否可用"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def search_pexels_videos(self, query: str, count: int = 5) -> List[Dict]:
        """从 Pexels 搜索视频"""
        if not PEXELS_API_KEY:
            return []

        url = f"https://api.pexels.com/videos/search?query={quote_plus(query)}&per_page={count}"
        headers = {"Authorization": PEXELS_API_KEY}

        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for video in data.get("videos", []):
                    # 获取最佳质量视频
                    files = video.get("video_files", [])
                    best = max(files, key=lambda x: x.get("width", 0)) if files else None
                    if best:
                        results.append({
                            "url": best["link"],
                            "duration": video.get("duration", 0),
                            "width": best.get("width", 0),
                            "height": best.get("height", 0),
                            "source": "pexels",
                            "id": video["id"],
                        })
                return results
        except Exception as e:
            print(f"Pexels Videos 搜索失败: {e}")
        return []

    def search_pixabay_videos(self, query: str, count: int = 5) -> List[Dict]:
        """从 Pixabay 搜索视频"""
        if not PIXABAY_API_KEY:
            return []

        url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={quote_plus(query)}&per_page={count}"

        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for hit in data.get("hits", []):
                    videos = hit.get("videos", {})
                    # 优先选择大尺寸
                    for quality in ["large", "medium", "small"]:
                        if quality in videos:
                            results.append({
                                "url": videos[quality]["url"],
                                "duration": hit.get("duration", 0),
                                "width": videos[quality].get("width", 0),
                                "height": videos[quality].get("height", 0),
                                "source": "pixabay",
                                "id": hit["id"],
                            })
                            break
                return results
        except Exception as e:
            print(f"Pixabay Videos 搜索失败: {e}")
        return []

    def search_youtube(self, query: str, count: int = 5) -> List[Dict]:
        """搜索 YouTube 视频 (使用 yt-dlp)"""
        if not self.ytdlp_available:
            return []

        try:
            cmd = [
                'yt-dlp',
                f'ytsearch{count}:{query}',
                '--dump-json',
                '--no-download',
                '--flat-playlist',
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                results = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            results.append({
                                "url": f"https://www.youtube.com/watch?v={data.get('id', '')}",
                                "title": data.get("title", ""),
                                "duration": data.get("duration", 0),
                                "channel": data.get("channel", ""),
                                "source": "youtube",
                                "id": data.get("id", ""),
                            })
                        except json.JSONDecodeError:
                            pass
                return results
        except Exception as e:
            print(f"YouTube 搜索失败: {e}")
        return []

    def download_video(self, url: str, filename: str, output_dir: str = None) -> Optional[str]:
        """下载视频文件"""
        if not REQUESTS_AVAILABLE:
            return None

        output_dir = output_dir or DOWNLOADS_DIR
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        try:
            resp = self.session.get(url, timeout=60, stream=True)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filepath
        except Exception as e:
            print(f"下载失败: {e}")
        return None

    def download_youtube(self, url: str, output_dir: str = None,
                         audio_only: bool = False) -> Optional[str]:
        """从 YouTube 下载视频"""
        if not self.ytdlp_available:
            print("❌ 需要安装 yt-dlp: pip install yt-dlp")
            return None

        output_dir = output_dir or DOWNLOADS_DIR
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_template = os.path.join(output_dir, f"yt_{timestamp}_%(title)s.%(ext)s")

        cmd = ['yt-dlp', '-o', output_template]

        if audio_only:
            cmd.extend(['--extract-audio', '--audio-format', 'mp3'])
        else:
            # 优先下载 mp4 格式，便于后续剪辑
            cmd.extend(['-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'])
            cmd.extend(['--merge-output-format', 'mp4'])

        cmd.append(url)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                # 找到下载的文件
                for f in os.listdir(output_dir):
                    if f.startswith(f"yt_{timestamp}_"):
                        return os.path.join(output_dir, f)
        except subprocess.TimeoutExpired:
            print("❌ 下载超时")
        except Exception as e:
            print(f"❌ 下载失败: {e}")
        return None


class VideoTrimmer:
    """视频剪辑器"""

    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_duration(self, filepath: str) -> float:
        """获取视频时长"""
        if not self.ffmpeg_available:
            return 0

        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 0

    def trim(self, input_path: str, output_path: str,
             start: float = 0, end: float = None, duration: float = None) -> bool:
        """剪辑视频"""
        if not self.ffmpeg_available:
            print("❌ 需要安装 ffmpeg: brew install ffmpeg")
            return False

        # 使用 -ss 在 -i 之前进行快速定位，然后在之后使用 -ss 0 精确定位
        cmd = ['ffmpeg', '-y']

        if start > 0:
            cmd.extend(['-ss', str(start)])

        cmd.extend(['-i', input_path])

        if end:
            # 计算实际需要的时长
            target_duration = end - start
            cmd.extend(['-t', str(target_duration)])
        elif duration:
            cmd.extend(['-t', str(duration)])

        # 使用重新编码以确保精确剪辑
        cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', output_path])

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ 剪辑失败: {e}")
        return False

    def auto_trim(self, input_path: str, output_path: str,
                  target_duration: float = 30) -> bool:
        """自动剪辑到目标时长 (从中间取)"""
        total_duration = self.get_duration(input_path)
        if total_duration <= target_duration:
            # 不需要剪辑
            import shutil
            shutil.copy(input_path, output_path)
            return True

        # 从中间取
        start = (total_duration - target_duration) / 2
        return self.trim(input_path, output_path, start=start, duration=target_duration)


# ═══════════════════════════════════════════════════════════
# CLI 命令
# ═══════════════════════════════════════════════════════════

def cmd_image(args):
    """下载图片"""
    if not REQUESTS_AVAILABLE:
        print("❌ 需要安装 requests: pip install requests")
        return 1

    downloader = ImageDownloader()

    print(f"🔍 搜索图片: {args.query}")
    results = downloader.search_all(args.query, args.count * 2)

    if not results:
        print("❌ 未找到图片。请检查 API Key 配置:")
        print("   export PEXELS_API_KEY=your_key")
        print("   export UNSPLASH_ACCESS_KEY=your_key")
        print("   export PIXABAY_API_KEY=your_key")
        return 1

    print(f"✅ 找到 {len(results)} 张图片，开始下载...")

    output_dir = args.output or DOWNLOADS_DIR
    downloaded = 0

    for i, img in enumerate(results[:args.count]):
        ext = img["url"].split(".")[-1].split("?")[0][:4]
        if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
            ext = "jpg"
        filename = f"{args.query.replace(' ', '_')}_{i+1}_{img['source']}.{ext}"

        print(f"  ⬇️ 下载 {i+1}/{args.count}: {filename}")
        path = downloader.download(img["url"], filename, output_dir)
        if path:
            downloaded += 1

    print()
    print(f"✅ 下载完成: {downloaded} 张图片")
    print(f"📁 保存位置: {output_dir}")
    return 0


def cmd_video(args):
    """下载视频"""
    if not REQUESTS_AVAILABLE:
        print("❌ 需要安装 requests: pip install requests")
        return 1

    downloader = VideoDownloader()
    trimmer = VideoTrimmer()

    print(f"🔍 搜索视频: {args.query}")

    # 搜索免费视频
    results = []
    results.extend(downloader.search_pexels_videos(args.query, args.count))
    results.extend(downloader.search_pixabay_videos(args.query, args.count))

    if not results:
        print("❌ 未找到视频。请检查 API Key 配置")
        return 1

    # 过滤时长
    if args.duration:
        results = [v for v in results if v.get("duration", 0) <= args.duration * 1.5]

    print(f"✅ 找到 {len(results)} 个视频")

    output_dir = args.output or DOWNLOADS_DIR
    downloaded = 0

    for i, video in enumerate(results[:args.count]):
        filename = f"{args.query.replace(' ', '_')}_{i+1}_{video['source']}.mp4"
        print(f"  ⬇️ 下载 {i+1}/{args.count}: {filename} ({video.get('duration', '?')}s)")

        path = downloader.download_video(video["url"], filename, output_dir)
        if path:
            # 检查是否需要剪辑
            if args.duration:
                duration = trimmer.get_duration(path)
                if duration > args.duration:
                    print(f"    ✂️ 剪辑到 {args.duration} 秒...")
                    trimmed_path = path.replace(".mp4", "_trimmed.mp4")
                    if trimmer.auto_trim(path, trimmed_path, args.duration):
                        os.remove(path)
                        os.rename(trimmed_path, path)
            downloaded += 1

    print()
    print(f"✅ 下载完成: {downloaded} 个视频")
    print(f"📁 保存位置: {output_dir}")
    return 0


def cmd_youtube(args):
    """从 YouTube 下载"""
    downloader = VideoDownloader()
    trimmer = VideoTrimmer()

    if not downloader.ytdlp_available:
        print("❌ 需要安装 yt-dlp: pip install yt-dlp")
        return 1

    print(f"⬇️ 下载 YouTube 视频: {args.url}")

    output_dir = args.output or DOWNLOADS_DIR
    path = downloader.download_youtube(args.url, output_dir, args.audio_only)

    if not path:
        print("❌ 下载失败")
        return 1

    print(f"✅ 下载完成: {os.path.basename(path)}")

    # 剪辑
    if args.start is not None or args.end is not None:
        if not trimmer.ffmpeg_available:
            print("⚠️ 需要 ffmpeg 进行剪辑: brew install ffmpeg")
        else:
            start = args.start or 0
            print(f"✂️ 剪辑: {start}s - {args.end}s")

            trimmed_path = path.rsplit(".", 1)[0] + "_trimmed." + path.rsplit(".", 1)[1]
            if trimmer.trim(path, trimmed_path, start=start, end=args.end):
                os.remove(path)
                os.rename(trimmed_path, path)
                print(f"✅ 剪辑完成")
            else:
                print("❌ 剪辑失败")

    print(f"📁 保存位置: {path}")
    return 0


def cmd_search(args):
    """搜索媒体"""
    if not REQUESTS_AVAILABLE:
        print("❌ 需要安装 requests")
        return 1

    print(f"🔍 搜索: {args.query}")
    print()

    if args.type in ["image", "all"]:
        img_dl = ImageDownloader()
        images = img_dl.search_all(args.query, args.count)
        if images:
            print(f"📷 图片 ({len(images)} 张):")
            for img in images[:5]:
                print(f"   • [{img['source']}] {img['photographer']}")
        print()

    if args.type in ["video", "all"]:
        vid_dl = VideoDownloader()
        videos = []
        videos.extend(vid_dl.search_pexels_videos(args.query, args.count))
        videos.extend(vid_dl.search_pixabay_videos(args.query, args.count))
        if videos:
            print(f"🎬 视频 ({len(videos)} 个):")
            for vid in videos[:5]:
                print(f"   • [{vid['source']}] {vid.get('duration', '?')}s - {vid.get('width', '?')}x{vid.get('height', '?')}")
        print()

        # YouTube
        yt_results = vid_dl.search_youtube(args.query, args.count)
        if yt_results:
            print(f"📺 YouTube ({len(yt_results)} 个):")
            for vid in yt_results[:5]:
                print(f"   • {vid['title'][:50]}...")
                print(f"     {vid['url']}")
        print()

    return 0


def cmd_trim(args):
    """剪辑视频"""
    trimmer = VideoTrimmer()

    if not trimmer.ffmpeg_available:
        print("❌ 需要安装 ffmpeg: brew install ffmpeg")
        return 1

    if not os.path.exists(args.input):
        print(f"❌ 文件不存在: {args.input}")
        return 1

    output = args.output or args.input.rsplit(".", 1)[0] + "_trimmed." + args.input.rsplit(".", 1)[1]

    print(f"✂️ 剪辑视频: {args.input}")

    if args.duration:
        success = trimmer.auto_trim(args.input, output, args.duration)
    else:
        success = trimmer.trim(args.input, output, start=args.start or 0, end=args.end)

    if success:
        duration = trimmer.get_duration(output)
        print(f"✅ 剪辑完成: {output} ({duration:.1f}s)")
        return 0
    else:
        print("❌ 剪辑失败")
        return 1


def cmd_status(args):
    """Check configuration status / 检查配置状态"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       Media Downloader - Status / 配置状态                ║")
    print("╠═══════════════════════════════════════════════════════════╣")

    # API Keys
    print("║  API Keys:                                                ║")
    pexels = "✅ Configured" if PEXELS_API_KEY else "❌ Not set"
    unsplash = "✅ Configured" if UNSPLASH_ACCESS_KEY else "❌ Not set"
    pixabay = "✅ Configured" if PIXABAY_API_KEY else "❌ Not set"
    print(f"║    Pexels:    {pexels:<42} ║")
    print(f"║    Unsplash:  {unsplash:<42} ║")
    print(f"║    Pixabay:   {pixabay:<42} ║")

    print("╠═══════════════════════════════════════════════════════════╣")

    # Tools
    print("║  Tools / 工具:                                            ║")
    import shutil
    ytdlp = "✅ Available" if shutil.which("yt-dlp") else "❌ Not found"
    ffmpeg = "✅ Available" if shutil.which("ffmpeg") else "❌ Not found"
    requests_status = "✅ Available" if REQUESTS_AVAILABLE else "❌ Not installed"
    print(f"║    yt-dlp:    {ytdlp:<42} ║")
    print(f"║    ffmpeg:    {ffmpeg:<42} ║")
    print(f"║    requests:  {requests_status:<42} ║")

    print("╠═══════════════════════════════════════════════════════════╣")

    # Features
    print("║  Features / 功能:                                         ║")
    img_ready = "✅" if (PEXELS_API_KEY or UNSPLASH_ACCESS_KEY or PIXABAY_API_KEY) else "❌"
    vid_ready = "✅" if (PEXELS_API_KEY or PIXABAY_API_KEY) else "❌"
    yt_ready = "✅" if shutil.which("yt-dlp") else "❌"
    trim_ready = "✅" if shutil.which("ffmpeg") else "❌"
    print(f"║    {img_ready} Image download / 图片下载                          ║")
    print(f"║    {vid_ready} Stock video download / 视频素材下载                 ║")
    print(f"║    {yt_ready} YouTube download / YouTube 下载                     ║")
    print(f"║    {trim_ready} Video trimming / 视频剪辑                          ║")

    print("╚═══════════════════════════════════════════════════════════╝")

    if not (PEXELS_API_KEY or UNSPLASH_ACCESS_KEY or PIXABAY_API_KEY):
        print()
        print("💡 Tip: Set API keys to enable image/video search:")
        print("   export PEXELS_API_KEY=your_key")
        print("   export UNSPLASH_ACCESS_KEY=your_key")
        print("   export PIXABAY_API_KEY=your_key")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Media Downloader - Smart media downloader / 智能媒体下载器"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands / 可用命令")

    # image command / 图片命令
    img_parser = subparsers.add_parser("image", help="Download images / 下载图片")
    img_parser.add_argument("query", help="Search keywords / 搜索关键词")
    img_parser.add_argument("--count", "-n", type=int, default=5, help="Number to download / 下载数量")
    img_parser.add_argument("--output", "-o", help="Output directory / 输出目录")

    # video command / 视频命令
    vid_parser = subparsers.add_parser("video", help="Download stock videos / 下载视频素材")
    vid_parser.add_argument("query", help="Search keywords / 搜索关键词")
    vid_parser.add_argument("--count", "-n", type=int, default=3, help="Number to download / 下载数量")
    vid_parser.add_argument("--duration", "-d", type=int, default=60, help="Max duration (seconds) / 最大时长(秒)")
    vid_parser.add_argument("--output", "-o", help="Output directory / 输出目录")

    # youtube command / YouTube 命令
    yt_parser = subparsers.add_parser("youtube", help="Download YouTube videos / 下载 YouTube 视频")
    yt_parser.add_argument("url", help="YouTube URL")
    yt_parser.add_argument("--start", "-s", type=float, help="Start time (seconds) / 开始时间(秒)")
    yt_parser.add_argument("--end", "-e", type=float, help="End time (seconds) / 结束时间(秒)")
    yt_parser.add_argument("--audio-only", "-a", action="store_true", help="Download audio only / 仅下载音频")
    yt_parser.add_argument("--output", "-o", help="Output directory / 输出目录")

    # search command / 搜索命令
    search_parser = subparsers.add_parser("search", help="Search media / 搜索媒体")
    search_parser.add_argument("query", help="Search keywords / 搜索关键词")
    search_parser.add_argument("--type", "-t", choices=["image", "video", "all"], default="all", help="Media type / 媒体类型")
    search_parser.add_argument("--count", "-n", type=int, default=5, help="Number of results / 结果数量")

    # trim command / 剪辑命令
    trim_parser = subparsers.add_parser("trim", help="Trim video / 剪辑视频")
    trim_parser.add_argument("input", help="Input video file / 输入视频文件")
    trim_parser.add_argument("--start", "-s", type=float, help="Start time (seconds) / 开始时间(秒)")
    trim_parser.add_argument("--end", "-e", type=float, help="End time (seconds) / 结束时间(秒)")
    trim_parser.add_argument("--duration", "-d", type=float, help="Target duration (seconds) / 目标时长(秒)")
    trim_parser.add_argument("--output", "-o", help="Output file / 输出文件")

    # status command / 状态命令
    subparsers.add_parser("status", help="Check configuration status / 检查配置状态")

    args = parser.parse_args()

    if args.command == "image":
        return cmd_image(args)
    elif args.command == "video":
        return cmd_video(args)
    elif args.command == "youtube":
        return cmd_youtube(args)
    elif args.command == "search":
        return cmd_search(args)
    elif args.command == "trim":
        return cmd_trim(args)
    elif args.command == "status":
        return cmd_status(args)
    else:
        parser.print_help()
        print()
        print("Examples / 示例:")
        print("  python media_cli.py status                    # Check config / 检查配置")
        print("  python media_cli.py image 'cute cats' -n 5    # Download images / 下载图片")
        print("  python media_cli.py video 'sunset' -d 30      # Download videos / 下载视频")
        print("  python media_cli.py youtube 'URL' -s 60 -e 90 # YouTube + trim / 下载剪辑")
        print("  python media_cli.py search 'nature' -t video  # Search / 搜索")
        print("  python media_cli.py trim video.mp4 -d 30      # Trim video / 剪辑视频")
        return 0


if __name__ == "__main__":
    sys.exit(main())
