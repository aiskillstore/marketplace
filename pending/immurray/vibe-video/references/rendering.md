# 跨运行环境渲染

依赖：Python 3.9+、Node.js 20+、ffmpeg/ffprobe（含 libx264、AAC、loudnorm、h264_metadata）、中文字体。Python：numpy/scipy/Pillow；Node：@napi-rs/canvas。脚本不调用任何模型 API，由宿主负责模型和工具权限。

## 首次使用

把 SKILL_DIR 替换为当前技能的实际目录。示例为 POSIX shell；Windows 可使用 WSL，原生 Windows 尚未测试。

```bash
python3 "$SKILL_DIR/scripts/prepare.py" --topic '如果光速突然变慢' --project work/vibe-light --music '/path/music.m4a'
cd work/vibe-light
npm install
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python "$SKILL_DIR/scripts/doctor.py" --project .
```

只有缺依赖时才安装；可复用宿主已经提供的依赖。不要假设 Codex 缓存路径存在。离线环境提前准备依赖。缺中文字体时安装 Noto Sans CJK，或把 VIBE_FONT_PATH 指向有使用权的本地字体文件；包内不分发字体。doctor.py 不安装依赖，不会调用模型或访问网络。

## 配乐与新主题

首次设置技能目录 local-profile.json 或项目父目录 vibe-video.local.json，格式见 assets/local-profile.example.json。也可用 VIBE_MUSIC 或 prepare.py 的 --music。相对路径以配置文件所在目录为准；命令行相对路径以当前目录为准。音乐应由使用者自行提供并确认用途。

prepare.py 的 film.js 是二向箔代码案例，需重写新主题全部相关场景和动画。brief.json 的 beat_analysis_status 为 reference_verified 才表示复用了匹配音轨的分析；requires_analysis 或 music_not_configured 不代表已经卡点。

```bash
.venv/bin/python "$SKILL_DIR/scripts/analyze_music.py" --audio '/path/music.m4a' --start 0 --duration 60 --output work/music-analysis.json
node film.js preview
node film.js render 0 60 work/silent.mp4
.venv/bin/python "$SKILL_DIR/scripts/finish.py" --silent work/silent.mp4 --music '/path/music.m4a' --duration 60 --output '../../outputs/主题_2K30.mp4' --qa-dir work/qa
```

修改案例的场景、文字、图形、预览点、musicKnots 和总长。音轨分析时间相对于截取起点；混音的 --music-start 必须相同。候选 BPM 有二倍/半倍歧义，仍需看事件和试听。

finish.py 支持 --sfx，执行混音、响度控制、AAC 编码、H.264 BT.709 元数据、faststart；要求输入已按 BT.709 编码，标签不能替代色彩转换。默认拒绝覆盖成片。

qa/report.json 和 contact.jpg 为技术及视觉检查材料。须查看图片和关键运动帧。宿主只能读文本时，把视觉审片留给图像工具或人工，不得声称已完成视觉 QA。文件用当前宿主支持的附件/下载链接交付，不依赖 Codex 面板。
