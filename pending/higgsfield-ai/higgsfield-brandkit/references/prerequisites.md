# Local prerequisites

Brandkit runs in the user's local Claude Code, Codex, or compatible agent environment. Check only the tools required by the current stage. Never install system packages without permission.

## Capability matrix

| Stage | Required tools |
|---|---|
| State and HTML generation | Python 3 |
| Higgsfield generations | `higgsfield` CLI, authenticated workspace |
| HTML screenshots | Node.js, `npx`, Playwright Chromium |
| Exact 4:5 crop from a 3:4 social render | ImageMagick (`magick` or `convert`) |
| SVG logo export | `rsvg-convert`, ImageMagick (`magick` or `convert`) |
| PDF/PPTX inspection | LibreOffice (`soffice`), Poppler |
| Canonical Brandbook | `rsvg-convert`, ImageMagick, LibreOffice, Poppler `pdffonts`, Fontconfig `fc-cache`/`fc-match` |
| Custom noncanonical deck | Node.js + PptxGenJS, or Python + `python-pptx` |

FFmpeg and ffprobe are not used. Brandkit does not produce motion, audio, or video deliverables.

## Check

```bash
for tool in python3 higgsfield node npx rsvg-convert magick convert soffice pdftoppm pdfimages pdffonts fc-cache fc-match; do
  command -v "$tool" >/dev/null 2>&1 && printf '%-14s ok\n' "$tool" || printf '%-14s missing\n' "$tool"
done
```

Either `magick` or `convert` satisfies the ImageMagick requirement.

## macOS with Homebrew

Ask before running:

```bash
brew install imagemagick librsvg poppler fontconfig
brew install --cask libreoffice
npx --yes playwright@1.62.1 install chromium
```

The npm-installed Higgsfield CLI already implies Node.js is available. Playwright is needed only for PNG screenshots of editable HTML review boards. PptxGenJS or `python-pptx` is optional and used only when the user requests a custom deck rather than the canonical Brandbook.

## Ubuntu/Debian

Ask before running:

```bash
sudo apt-get update
sudo apt-get install -y imagemagick librsvg2-bin poppler-utils fontconfig libreoffice
npx --yes playwright@1.62.1 install --with-deps chromium
```

When `sudo` or package installation is unavailable, continue only with stages whose dependencies already exist. State clearly which export or review format cannot be produced.

## Higgsfield setup

```bash
higgsfield version
higgsfield account status
higgsfield workspace status
```

If the CLI is missing, ask permission before installing:

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
```

Authentication requires an interactive user login:

```bash
higgsfield auth login
```

Never ask the user to paste an access token into chat.

## Network requirements

The workflow may access:

- Higgsfield API and result CDN
- Google Fonts CSS/font files when `google:<family>` is selected
- The fixed canonical Brandbook PPTX template
- User-supplied public brand URLs

If network policy blocks one source, stop that dependent stage and report the exact host or resource. Do not silently substitute different fonts, templates, or logos.
