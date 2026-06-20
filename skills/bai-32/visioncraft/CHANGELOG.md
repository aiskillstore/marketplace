# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-06-19

### Added
- Initial public release of VisionCraft.
- Image generation via Agnes Image 2.1 Flash — text-to-image and image-to-image workflows.
- Video generation via Agnes Video V2.0 — text-to-video, image-to-video, multi-image, and keyframe animation.
- Asynchronous task creation and polling built into `gen_video.ps1` with automatic timeout recovery (surfaces `video_id` for manual re-query).
- Convenience shortcuts: `-Ratio` (image + video) and `-Seconds` (video) for ergonomic control without manual dimension / frame math.
- Full API reference, prompt guide, and parameter reference under [`references/`](references/).
- Copy-paste example command set under [`examples/`](examples/).
- Bilingual README (English + 中文).

### Defaults
- Images: `2048x2048`.
- Video: `1920x1080 @ 60fps, 241 frames` (~4s ultra-smooth).

[Unreleased]: https://github.com/BAI-32/visioncraft-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/BAI-32/visioncraft-skill/releases/tag/v1.0.0
