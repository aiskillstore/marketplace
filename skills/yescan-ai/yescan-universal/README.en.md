# yescan

All-in-one image processing skill powered by Quark Scan. Supports 36 scenes across OCR, image enhancement, document conversion, and AIGC generation.

## Capabilities

| Category | Scenes | Typical Use Cases |
|---|---|---|
| OCR | 19 | ID card, invoice, table, handwriting, formula, etc. |
| Image Enhancement | 13 | Remove watermark / shadow / handwriting, crop & rectify, HD enhance, etc. |
| Document Conversion | 3 | Image to Word / Excel / PDF |
| AIGC Generation | 1 | ID photo generation |

## Quick Start

### 1. Install

```bash
pip3 install yescan
```

### 2. Configure API Key

```bash
yescan config set SCAN_WEBSERVICE_KEY <your_api_key>
```

> Apply for an API Key at the [Quark Scan Developer Console](https://scan.quark.cn/business).

### 3. Usage

```bash
# List all scenes
yescan --list-scenes

# OCR
yescan --scene idcard-ocr --path ./idcard.jpg

# Image enhancement
yescan --scene remove-watermark --path ./img.jpg

# Document conversion
yescan --scene image-to-excel --path ./table.jpg

# View scene parameters
yescan --list-scenes id-photo
```

## Design Philosophy

- **CLI-first**: CLI is self-describing — `--list-scenes` output includes intent descriptions and parameter details
- **Agent-native**: SKILL.md defines the PEV protocol (Plan → Execute → Verify) and constraints; Agent autonomously matches scenes
- **Dynamic discovery**: All scenes and parameters are queried via CLI at runtime, never hardcoded

## File Structure

```
yescan-universal/
├── SKILL.md                        ← Agent skill contract (PEV protocol + constraints)
├── references/
│   ├── privacy.md                  ← Privacy, data flow & key security
│   ├── troubleshooting.md          ← Error codes & troubleshooting
│   └── implementation.md           ← Implementation details: CLI behavior & response fields
├── SECURITY.md                     ← Security policy
├── README.md                       ← This document
└── README.en.md                    ← English README
```

## Links

- [Quark Scan Open Platform](https://scan.quark.cn/business)
- [SKILL.md](SKILL.md) — Agent skill contract
- [SECURITY.md](SECURITY.md) — Security policy
