---
name: analyzing-products
description: Normalizes a product into generation-ready facts — from an e-commerce URL (a clean description plus curated product images) or from a photo alone (category, how it's used, its moving/opening parts, and key visual details). Use when a product URL or photo needs turning into inputs for image/video generation, or when another skill needs product facts before generating. 
license: Apache-2.0
metadata:
  version: "0.1.0"
  category: creative
  summary: "Analyzes an e-commerce link or photo to map out your product's exact physical mechanics and extract clean reference images, building a highly accurate creative brief without any manual research or extraction."
---

# Product Analysis

Turn a product — an e-commerce **URL** or a bare **photo** — into clean, reusable facts for downstream
image/video generation: a tight description, curated product images, and how the product is physically
used. It's a building block: other skills call it at the input stage, before any generation.

## Workflow

### Step 1: Pick the mode and run it

| Input | Reference | What you produce |
| ----- | --------- | ---------------- |
| An e-commerce URL (Amazon, Shopify, AliExpress, any product page) | `references/url-extract.md` | A two-paragraph description + up to 5 downloaded, filtered product images |
| A product photo only (no URL, no description) | `references/photo-analysis.md` | Category + how it's used + moving/opening parts + key visual details |

Read **only** the matching reference and follow it end to end. If both a URL and a photo are given, run
the URL mode (richer) and keep the photo as one more reference image; if neither is given, there's
nothing to analyze — ask for one. Don't pause for confirmation — a URL (or photo) plus generation
intent means extract and proceed.

### Step 2: Hand off

Return the result to whoever called you, ready to drop into generation:

- **URL mode** → the description and the kept image files (local paths, usable as reference images).
- **Photo mode** → the category, how it's used, any moving or opening parts, and the key visual details.

Don't rank the product's market position — the calling skill decides that from packaging cues. Your
job is the objective facts.

## Edge cases

- **The URL can't be extracted** (no result, or the extractor isn't set up) → ask for a product photo
  instead and switch to photo mode.
- **Every image fails the filter** (faces, wrong variant, not a product shot) → keep the single
  cleanest, or hand off the description alone and say plainly that no clean image survived.
- **A supplied photo is too unclear to read** (blurry, cropped, ambiguous) → say what you can't
  determine and ask for a clearer shot rather than guessing the mechanic.
- **Neither a URL nor a photo** → ask for one; there is nothing to analyze.

## Reference

- `references/url-extract.md` — the URL pipeline: `url_extraction` → download the images → filter them
  with `image_analysis` → write the description.
- `references/photo-analysis.md` — the photo pipeline: category, how it's used, moving/opening parts,
  and the visual details to preserve.
