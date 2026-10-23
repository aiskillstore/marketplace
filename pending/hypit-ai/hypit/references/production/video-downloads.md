# Downloading a video from a link

Read this when a reference or source clip lives on a video page. `hypit download` saves the
video as a project file through yt-dlp. For a website's interface, scroll or interaction, use
[browser capture](browser-capture.md).

## Save the source video

```bash
hypit download "https://example.com/watch?v=VIDEO_ID" \
  --to references/ad/source.mp4
```

Replace the example URL with the actual video link. Quote it so URL punctuation stays part of the
argument. The destination is relative to the current directory; the CLI creates parent directories
and requires a new output path. `--json` reports the saved path, source URL, duration, dimensions,
frame rate and audio presence.

The command fetches one video, including its audio when available, even when the link also belongs
to a playlist. It prefers H.264 and a resolution near 1080p; the source's available formats determine
the result. Destinations can use `.mp4`, `.mkv`, `.webm` or `.mov`. Downloading retains source timing;
it is separate from preparing material for a production's frame clock.

## Prepare the downloader

Run `hypit download prepare` explicitly before the first download. It uses uv to prepare the
Distribution's locked downloader and JavaScript solver, then reports the executable path. Reuse that
environment for subsequent downloads. `download` never installs dependencies, updates tools or
acquires remote components; a missing environment reports the preparation command. `ffmpeg` merges separate picture and sound streams, and `ffprobe` reads the
saved file. [Local tools](../environment/local-tools.md#supply-host-executables-at-machine-scope)
covers these executables on macOS, Windows and Linux. The command runs directly, without a Runtime
Profile, model credential or Build.

Supported sites and access requirements depend on yt-dlp and the source site. A failed download
includes the downloader's error. When a site needs additional download options, the installed
`@hypit/yt-dlp/runtime/README.md` explains direct use of the packaged tool; the site's own download or
export can also supply the same local file.

## Continue from the saved file

Keep the source URL and local path in the reference notes. Use the file for
[reference understanding](../creation/reference-video.md): transcription, timed frames and grids all
refer to that same source clock. Reuse the saved file when returning to the reference.

When the downloaded clip becomes material in the new video, declare it as `media:Video` and follow
[media preparation](media.md). The composition then places the prepared material against the
target's events.
