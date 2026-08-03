# Reverse image engine selection matrix

## By engine

### Yandex Images

- **Entry:** `https://yandex.com/images/` — upload or paste an image URL.
- **Matching model:** learned visual similarity with a strong face component.
- **Best at:** faces; the same person in other photographs; street scenes and
  buildings in Russia, Central Asia, the Caucasus, Eastern Europe, Turkey, the
  Balkans, Iran and China; crops and rotations; screenshots of images.
- **Reading the results:** the page separates *sites where the image appears*
  from *similar images*. Only the first block is provenance evidence. Yandex also
  offers size variants of the matched image — use the largest to find the copy
  closest to source.
- **Weak at:** consumer products, English-language commerce, very recent posts.
- **Failure mode:** returns a confident wall of different people with the same
  haircut. It optimises for similarity, not identity.

### Google Lens

- **Entry:** `https://lens.google.com/` — also reachable from the camera icon in
  Google Images, and by right-clicking an image in Chrome.
- **Matching model:** object, entity, text and landmark recognition first;
  duplicate detection second.
- **Best at:** identifying *what a thing is* — species, model, artwork, plant,
  book, uniform type, aircraft type; landmarks; reading and searching text in the
  frame; anything with a retail listing.
- **Reading the results:** prefer the option that lists web pages containing the
  image over the visual-match carousel. The carousel routinely presents
  same-genre photographs as matches.
- **Weak at:** exact-duplicate provenance; ordering by date; non-Latin scripts in
  low-resource languages.
- **Failure mode:** answers a question you didn't ask. You want "where did this
  photo come from" and it tells you which sneaker it is.

### Bing Visual Search

- **Entry:** `https://www.bing.com/images` — camera icon; upload, paste URL, or
  drag.
- **Matching model:** visual similarity plus object detection.
- **Best at:** the region-select box. After you upload, drag a rectangle over any
  part of the image and it re-searches only that region — the fastest way to run
  the crop-and-retry loop without leaving the browser. Also picks up product and
  object matches Google misses.
- **Weak at:** date ordering; non-Western geography.
- **Failure mode:** heavy commercial bias; shopping results crowd out pages.

### TinEye

- **Entry:** `https://tineye.com/` — upload or URL. Browser extension available.
  A paid API exists for bulk work.
- **Matching model:** perceptual hashing over its own crawl. It is looking for
  *this image*, not for images like it.
- **Best at:** the sort orders. Oldest gives you the earliest copy in its index.
  Biggest image gives you the highest-resolution copy, which is usually nearest
  the source. Most-changed surfaces copies that have been cropped, recoloured,
  text-overlaid or watermarked, and it displays them aligned against your input so
  you can see exactly what changed — no other free engine does this.
- **Weak at:** coverage. The index is small relative to Google's or Yandex's, and
  faces are not supported at all.
- **Failure mode:** zero results, frequently, on perfectly ordinary images. Never
  read a TinEye null as evidence.

### Baidu image search

- **Entry:** `https://graph.baidu.com/` or the camera icon at
  `https://image.baidu.com/`.
- **Best at:** Chinese-language web content, Chinese e-commerce and social
  platforms, Chinese street scenes and signage.
- **Practical notes:** interface is Chinese-only; some functionality is
  region-gated. Worth the friction when a case has any China nexus.

### Face-specific engines

Read the consent and legality section of the parent skill before using any of
these. Facial templates are biometric data.

| Engine | Index | Notes |
|---|---|---|
| PimEyes | Open web, broad | Paid for URLs. Terms position it as self-search; offers an opt-out and removal requests. Strong recall, look-alike false positives common. |
| FaceCheck.ID | Open web, weighted toward news, court and social sources | Paid credits. Returns a similarity score — treat the score as a ranking, not a probability. |
| Search4Faces | VK, Odnoklassniki and related Russian platforms | The right tool when the subject's social footprint is Russian-language. |

None of these produce auditable reasoning. A hit is a lead requiring independent
corroboration — a second photo, a name, a shared associate.

## By input type

| Input | Order to run | Notes |
|---|---|---|
| Profile avatar | Yandex, then TinEye, then Lens | Reused avatars are a strong sockpuppet indicator. Also check for stock. |
| Passport/ID photo | Yandex, then face engines only if authorized | Legally sensitive. Consider not uploading at all. |
| Protest or conflict scene | Yandex, TinEye, Lens | Recycled footage is the norm. TinEye oldest sort matters most here. |
| Product for sale (scam check) | Lens, Bing, Baidu | Stolen listing photos are near-universal in marketplace fraud. |
| Logo or letterhead | Lens, Bing | Also OCR the text and search it as a string. |
| Screenshot of a tweet or chat | Lens for the OCR text, then search that text | Screenshots defeat image matching; the text does not. |
| Video frame | Yandex, Lens, TinEye per keyframe | Extract keyframes first; search three or more. |
| Artwork or illustration | TinEye, then Lens | TinEye's modified-copy detection is designed for exactly this. |
| Satellite or aerial image | None of the above reliably | Go to `geolocate-from-pixels` and match terrain directly. |

## Multi-engine tactics

- Browser extensions that fan a single right-click out to several engines
  (RevEye, "Search by Image") remove most of the tedium. They open one tab per
  engine with the same input.
- Search order matters for cost, not for results: run the free engines to
  exhaustion before spending credits on a face engine.
- Record, per engine, the query you ran (full frame, crop, flipped, upscaled) and
  the outcome including nulls. A null against a documented query is a defensible
  statement; "I searched and found nothing" is not.
- Archive every match URL immediately. Match pages disappear, and a screenshot
  without an archive capture is weak evidence.
