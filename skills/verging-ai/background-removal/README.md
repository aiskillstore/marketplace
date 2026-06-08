# background-removal - AI Background Removal

Remove image backgrounds with AI. Returns transparent PNG. Supports local files and remote URLs.

## Install

```bash
npx skills add verging-ai/agent-skills --skill background-removal
```

## Setup

1. Visit [verging.ai](https://verging.ai)
2. Login → Click avatar (top right) → API Keys
3. Create a key, then set it:

```bash
export VERGING_API_KEY="vrg_sk_your_key_here"
```

## Requirements

- `curl`

## Usage

```bash
# Remove background from a local image
/background-removal -i ./photo.jpg

# Remove background from a URL
/background-removal -i "https://example.com/photo.png" --download

# Specify output path
/background-removal -i ./photo.jpg -o ./result.png
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --image | -i | Image file or URL | Required |
| --download | -d | Auto-download result | false |
| --output | -o | Output path | Current dir |

## Supported Formats

- JPG / JPEG
- PNG
- WebP
- Max file size: 10MB

## Credits

1 credit per image (fixed cost).

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
