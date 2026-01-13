---
name: create-svg-from-prompt
description: Generate an SVG of a user-requested image or scene
---

## Setup

if `autotrace` is not available in the environment, then install it with the following command:

```bash
sudo apt update
sudo apt install git build-essential intltool imagemagick libmagickcore-dev pstoedit libpstoedit-dev autopoint
git clone https://github.com/autotrace/autotrace.git
cd autotrace
./autogen.sh
LD_LIBRARY_PATH=/usr/local/lib ./configure --prefix=/usr
make
sudo make install
```

## Core Workflow

When the user prompts the model to generate an SVG of and image or scene:

### User wants an SVG of an image or scene

To generate an SVG of an image or scene use Google Gemini and autotrace:

```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" -H "x-goog-api-key: <GEMINI_API_KEY>" -H "Content-Type: application/json" -d '{ "contents": [{ "parts": [ {"text": "<IMAGE_PROMPT>"}]}]}' | grep -o '"data": "[^"]*"' | cut -d'"' -f4 | base64 --decode | autotrace -output-format svg -despeckle-level 10 -despeckle-tightness 2.0 -output-file <OUTPUT_FILE>.svg
```

**Arguments from prompt:**
- `<GEMINI_API_KEY>`: The Gemini API key gotten from the environment variable "GEMINI_API_KEY"
- `<IMAGE_PROMPT>`: The user's initial prompt modified to change phrases like "Generate an svg" to "Generate an image." Do not modify the rest of the prompt or add any extra instructions or descriptions. 
- `<OUTPUT_FILE>`: An 8-30 character filename based on the image the user wants

