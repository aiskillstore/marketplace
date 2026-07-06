# yescan-ocr-universal

**English** | [简体中文](README.zh-CN.md)

Extract, recognize, and structure text from images — covering handwriting, tables, IDs, invoices, formulas, medical reports, pharmaceutical inspection reports, business licenses, product labels, image translation, and more across 19 scenes — powered by [Quark Scan King](https://scan.quark.cn/business).

## What it does

Send a single image (URL / local path / base64) to the Quark Scan King API and receive structured JSON recognition results. Designed for AI agents (Claude / Codex / Claude Code / Coze / etc.) to invoke as a skill.

| Scene | Description |
|---|---|
| `handwritten-ocr` | Handwritten Chinese/English recognition, cursive → high-accuracy text |
| `table-ocr` | Table recognition, restore row/column structure and cell content |
| `idcard-ocr` | ID card recognition, extract name, ID number, address, etc. |
| `social-security-card-ocr` | Social security card recognition, extract name, SSN, bank number, etc. |
| `travel-permit-ocr` | HK/Macau travel permit recognition, extract permit number, validity, etc. |
| `degree-certificate-ocr` | Degree certificate recognition, extract school, major, certificate number, etc. |
| `vat-invoice-ocr` | VAT invoice recognition, extract seller, amount, 30+ fields |
| `train-ticket-ocr` | Train ticket recognition, extract train number, fare, seat, etc. |
| `formula-ocr` | Math/chemistry formula recognition, output LaTeX |
| `question-ocr` | Exam question extraction, text only (no answers) |
| `driver-license-ocr` | Driver's license recognition, extract license number, name, class, etc. |
| `vehicle-license-ocr` | Vehicle license recognition, extract plate number, vehicle type, etc. |
| `commercial-invoice-ocr` | English commercial invoice recognition, extract buyer/seller, line items, etc. |
| `medical-report-ocr` | Medical report recognition, extract test items and results |
| `pharmaceutical-inspection-report` | Pharmaceutical inspection report recognition, extract drug name, results, etc. |
| `business-license-ocr` | Business license recognition, extract credit code, legal representative, etc. |
| `product-image-ocr` | Product image text recognition, extract brand, specs, ingredients, etc. |
| `pic-translate` | Image translation, generate translated image preserving layout |
| `general-ocr` | General text extraction (fallback scene) |

## Quick start

1. Get an API key from `https://scan.quark.cn/business` (Developer Console → API Key)
2. Configure your API key (choose one):
   - **Option A: Environment variable** (recommended)
     ```bash
     export SCAN_WEBSERVICE_KEY=<your_api_key>
     ```
   - **Option B: Config file**
     ```bash
     echo 'SCAN_WEBSERVICE_KEY=<your_api_key>' > ~/.yescan_env
     chmod 600 ~/.yescan_env
     ```
   > The environment variable takes priority; if not set, the key is loaded from `~/.yescan_env`.
3. Install the skill into your agent runtime (see your agent's skill installation docs)
4. Ask the agent: *"Recognize this invoice image: /path/to/invoice.png"*

## Repository layout

```
yescan-ocr-universal/
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
    ├── handwritten-ocr-example.md
    ├── table-ocr-example.md
    ├── idcard-ocr-example.md
    ├── social-security-card-ocr-example.md
    ├── travel-permit-ocr-example.md
    ├── degree-certificate-ocr-example.md
    ├── vat-invoice-ocr-example.md
    ├── train-ticket-ocr-example.md
    ├── formula-ocr-example.md
    ├── question-ocr-example.md
    ├── driver-license-ocr-example.md
    ├── vehicle-license-ocr-example.md
    ├── commercial-invoice-ocr-example.md
    ├── medical-report-ocr-example.md
    ├── pharmaceutical-inspection-report-example.md
    ├── business-license-ocr-example.md
    ├── product-image-ocr-example.md
    ├── pic-translate-example.md
    └── general-ocr-example.md
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
