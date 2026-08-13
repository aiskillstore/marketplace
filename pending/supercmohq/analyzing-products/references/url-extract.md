# URL extraction — structured product data from an e-commerce page

Pull clean facts and product images from any product page (Amazon, Shopify, AliExpress, a brand
store). Loaded when the input is a URL.

## Step 1: Extract with `url_extraction`

Call `url_extraction` with the URL and a product-focused prompt. It returns a few KB of clean
structured JSON — fields plus product-image URLs — instead of a whole-page dump:

- **prompt** — ask for exactly what you need, e.g.: *"Pull the product's name, brand, price and
  currency, the chosen variant, the full write-up, and any spec or feature bullets — plus the URLs of
  the main product photos (hero shots and packaging). Leave out customer-review images, 'related
  products', site navigation, promo banners, colour-swatch thumbnails, sizing charts, and brand
  logos."*
- **schema** *(optional)* — pass a JSON schema when you want a strict, typed shape back.

## Step 2: Download the candidate images

Take at most the **first 10** candidate URLs (hero and main-gallery shots first) — never download or
filter more than 10, however many the extractor returns. Download each into `$SCRATCH` (set in the
snippet below) **with a browser User-Agent** — without one, some CDNs return a stub a few hundred bytes
long rather than the image, which then renders broken when generation fetches it:

```
SCRATCH="${SUPERCMO_SCRATCH_DIR:-${TMPDIR:-/tmp}/supercmo-work}"; mkdir -p "$SCRATCH"
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36" -o "$SCRATCH/product_N.jpg" "IMAGE_URL"
```

Verify each file is **>10KB** — anything smaller is a placeholder or a blocked URL; drop it. From here
on work from the downloaded files, not the URLs, so generation gets
the real bytes rather than a hotlink that may 403.

## Step 3: Filter the images with `image_analysis`

Call `image_analysis` on each downloaded image — **at most 10 calls total** — and keep only clean
product shots. Always route each image through `image_analysis`; don't rely on reading it yourself. This
filter is **mandatory**: one wrong-variant or face-carrying image corrupts the generation. For each
image, judge:

- **Type** — is the product the clear subject, or is it a lifestyle/review photo, a size chart, a logo,
  or a banner? Keep only a clean product shot.
- **Face** — drop any image showing a human face (hands holding the product are fine).
- **Variant** — drop any image whose colour/variant differs from the listing.

A prompt that gets all three at once: *"Is this a clean product-only photo of [product], or is it a
lifestyle/review shot, size chart, logo, or banner? Is any human face visible? What colour/variant is
shown?"* Keep up to 5 that pass.

## Step 4: Write the description

From the extracted fields, write a description of roughly two paragraphs — factual, not marketing copy:

Open with what it is and who makes it, cover the three to five points that would actually decide a
purchase, give the concrete specs, and close on who it's for.

Include the concrete specs — dimensions, weight, materials, compatibility. This is the text that
anchors the generation prompt and keeps the product described the same everywhere it's used.

## Hand off

Return the kept image file paths and the description.
