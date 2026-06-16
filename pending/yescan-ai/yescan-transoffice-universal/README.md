# yescan-transoffice-universal

**English** | [简体中文](README.zh-CN.md)

Convert images, screenshots, and scans into editable Office documents (Word / Excel / PDF), powered by [Quark Scan King](https://scan.quark.cn/business).

## What it does

Send a single image (URL / local path / base64) to the Quark Scan King API and receive a converted Word, Excel, or PDF file saved to the system temp directory. Designed for AI agents (Claude / Codex / Claude Code / Coze / etc.) to invoke as a skill.

| Scene | Use case |
|---|---|
| `image-to-excel` | Tables, financial reports, sales sheets |
| `image-to-word` | Meeting notes, contracts, articles |
| `image-to-pdf` | Handwritten notes, mixed layouts, visual archives |

## Quick start

1. Get an API key from `https://scan.quark.cn/business` (Developer Console → API Key)
2. Save it locally:
   ```bash
   echo 'SCAN_WEBSERVICE_KEY=<your_api_key>' > ~/.yescan_env
   chmod 600 ~/.yescan_env
   ```
3. Install the skill into your agent runtime (see your agent's skill installation docs)
4. Ask the agent: *"Convert this screenshot to Excel: /path/to/image.png"*

## Repository layout

```
yescan-transoffice-universal/
├── SKILL.md                 # Agent-facing skill definition (intent dispatcher)
├── README.md                # English documentation
├── README.zh-CN.md          # 中文说明
├── LICENSE                  # MIT
├── SECURITY.md              # Security disclosure & data flow
├── scripts/
│   ├── scan.py              # Entry point
│   └── common/              # Scan King API client, file saver, validators, etc.
├── references/
│   ├── privacy.md           # Data flow, key configuration, rotation
│   ├── implementation.md    # Client-side script behavior, response fields
│   └── troubleshooting.md   # Error codes, common issues
└── examples/
    ├── excel-example.md
    ├── word-example.md
    └── pdf-example.md
```

## Requirements

- Python 3.9+
- `SCAN_WEBSERVICE_KEY` environment variable (or `~/.yescan_env`)
- Network access to `scan-business.quark.cn`
- Image input ≤ 5 MB, format in jpg/jpeg/png/gif/bmp/webp/tiff/wbmp

## Security

This skill sends user-provided images to a third-party API. Read [SECURITY.md](SECURITY.md) and [references/privacy.md](references/privacy.md) before processing sensitive data.

## License

[MIT](LICENSE)

## Author

[yescan-ai](https://github.com/yescan-ai)
