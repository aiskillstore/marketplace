---
name: find-the-original-image
description: >-
  Reverse image search across Yandex, Google Lens, Bing Visual Search, TinEye and Baidu to
  find where a picture came from and who published it first. Use when reverse image searching,
  identifying a photo, face, logo, product, uniform or building, tracing a profile picture or
  avatar, finding the oldest copy of an image, checking whether a photo is stock or a repost,
  or reverse-searching a video by keyframes. Applies to romance and investment scam
  investigation, fake-profile and synthetic-identity detection, disinformation and media
  verification, counterfeit and brand-infringement work, and insurance claim review. Reference
  at useosint.com/skills/find-the-original-image.

---

# Find the original image

The goal is almost never "find a match". It is **find the earliest publication
and read its page**. A match tells you the image exists elsewhere; the earliest
page tells you the photographer, the date, the caption, and the names — which is
what you actually pivot on.

The beginner mistake: uploading the full frame to one engine, getting nothing,
and concluding the image is unindexed. Cropping to one distinctive object and
re-searching finds things full-frame search cannot.

## Pick your engine by what you are holding

| You have | Start with | Why |
|---|---|---|
| A face | Yandex | Its index is built around facial similarity, so it returns different people who look alike *and* the same person in other photographs. No other general engine does this. |
| A face, and Yandex fails | A dedicated face engine (see below) | Only after you have cleared the legal and consent questions. |
| A street scene outside North America / Western Europe | Yandex | Deeply indexed Russian, Central Asian, Eastern European, Turkish and Chinese web content that Google under-crawls. |
| A product, book cover, artwork, plant, animal | Google Lens | Object and entity recognition, tied to Shopping and Knowledge Graph. |
| Text inside the image | Google Lens | It OCRs the frame and lets you search the extracted string. Often the text is the answer and the image search is irrelevant. |
| A landmark or a well-known building | Google Lens | Landmark classification is its strongest single feature. |
| A specific region of a cluttered photo | Bing Visual Search | Draw a box on the uploaded image and it re-searches only that region — the fastest crop-and-retry loop of any engine. |
| A press photo, meme, or anything you suspect is old | TinEye | The only major engine that sorts by oldest and that reliably surfaces *modified* copies. |
| Chinese-language or China-hosted content | Baidu image search | Coverage the others simply do not have. |

Run at least three. They disagree constantly, and that disagreement is
information: TinEye finding an exact copy from years back while Lens finds only
recent reposts is the signature of recycled media.

### What each engine is actually doing

**Yandex** matches on visual similarity with a strong face component. Its results
page groups "sites containing this image" separately from "similar images" —
only the first group is evidence. It tolerates crops, rotation and heavy
recompression better than the others.

**Google Lens** has moved away from whole-image duplicate matching toward "what
is this, and what can I sell you". For provenance work use the option that lists
pages containing the image rather than the visual-match carousel, and expect it
to return visually similar but unrelated photos as if they were matches.

**Bing Visual Search** sits between the two. Its region-select tool is the reason
to use it: no download, crop, re-upload cycle.

**TinEye** is crawl-based and comparatively small — plenty of images return zero
results, and absence from TinEye proves nothing. What it does that nothing else
does: exact and near-duplicate matching with the ability to sort by oldest, and
detection of copies that have been cropped, colour-shifted or watermarked, which
it will show you side by side against your input.

## Method

1. **Fix the input.** Get the highest-resolution copy you can — the file itself,
   not a screenshot of it. Screenshots add a resize and a recompression that cost
   you matches. Strip nothing yet; run `secrets-in-file-metadata` on the original
   before you start editing copies.
2. **Full frame, all engines.** Cheap, sometimes instant.
3. **Crop and re-search.** This is the highest-yield step in the whole skill. A
   full frame's fingerprint is dominated by the background; crop tightly to the
   face, the sign, the logo, the vehicle, the tattoo, the building corner, and
   search each crop separately. Reposts get cropped and re-framed, so the crop
   often matches when the frame does not.
4. **Flip horizontally.** Mirroring is a routine way to dodge automated matching
   and a routine artifact of screen-recording and video reposting. Flip and
   re-run the same engines.
5. **Preprocess and retry** on low-quality inputs — upscale, denoise, correct
   levels. See [reference/preprocessing.md](reference/preprocessing.md).
6. **For video**, extract keyframes and search them as stills. Search a frame
   from the start, the middle and the end, plus any frame containing a sign or a
   face. A keyframe hit is usually what breaks a video case.
7. **Sort for oldest.** On TinEye, sort by oldest. Then treat that date as a
   ceiling, not an answer, and go to step 8.
8. **Read the match pages.** Open them. Harvest: photographer credit, agency,
   caption, named people, on-page date, filename in the image URL (often
   `2019-04-city-event-03.jpg`), and any surrounding article text. This is where
   the selectors are.

## Establishing first publication, not just a match

An earliest-known-copy date is a claim about your search coverage, not about the
world. To harden it:

- Check the match page's own date against `read-deleted-pages` — the archive's
  first capture of the URL bounds when the page really existed, and the page's
  displayed date can be back- or forward-dated by its CMS.
- Use date-restricted search operators via `google-like-a-spy` to look for
  earlier text mentions of the same event or caption.
- Look for the same image at a larger resolution. The largest version is usually
  closest to the source; a wire agency's copy will be bigger than a Twitter
  repost of it. TinEye's biggest-image sort is useful here.
- Check the obvious stock libraries. A photo credited to three different news
  events in three countries is stock, and the "original" is a licensing page.
- Watermarks and agency slugs in the frame beat any index. Crop the watermark and
  search that alone.

## Face-specific engines and when not to use them

PimEyes and FaceCheck.ID crawl the open web for faces and match on biometric
similarity. They find people that no general engine will. They also carry real
exposure:

- A facial template is **biometric data** under GDPR Article 9 — a special
  category needing an explicit lawful basis, not just a legitimate interest.
  Illinois BIPA and Texas CUBI create private rights of action and statutory
  damages for collecting biometric identifiers without written consent.
- PimEyes' own terms position it as a tool to search for **your own** face and
  offer an opt-out. Running a third party's face through it is against those
  terms regardless of your intent.
- Search4Faces indexes faces from Russian social platforms and is the practical
  option when a subject's footprint is VK or Odnoklassniki.

Use face search when you have a documented authorization or a legitimate
protective purpose — verifying a counterparty in a fraud case, identity
verification with the subject's consent, missing-persons work, or checking your
own exposure. Do not use it to identify a stranger from a photo, to attach a name
to a face in a protest crowd, or to locate a private individual. Note in the case
file that you ran it and why. And treat a face-engine hit as **unconfirmed** on
its own — look-alike false positives are common and the engine gives you no
reasoning to audit.

## Where this goes wrong

- **Similar is not same.** Every engine mixes "pages with this image" and
  "images that look like this" into one visual grid. Only the first is evidence.
  Confirm a candidate by opening it and comparing pixel-level detail — a hand
  position, a fold in cloth, a reflection.
- **Absence is the default, not a finding.** Non-indexed, freshly published,
  login-walled, and app-only images return nothing. "No results across four
  engines" means the image is not in those indexes, which is weak evidence for
  originality and no evidence at all of authenticity.
- **Stock photography poisons attribution.** A "CEO" headshot that appears on
  forty unrelated sites is a stock model, and the entity using it is probably
  fake — that itself is a finding, and a good one.
- **AI-generated images have no origin to find.** Zero matches plus generative
  tells is a distinct outcome; hand it to `is-this-photo-real` rather than
  concluding the photo is an unpublished original.
- **Engines rewrite history.** Results are not reproducible: indexes drop pages,
  results reorder, and the hit you found last week may be gone. Screenshot the
  results page and archive the match URL the moment you find it.
- **Crops mislead in the other direction.** A crop of grass or sky returns
  thousands of confident, meaningless matches. Crop to what is *unusual*, not
  merely present.
- **You may be leaking.** Uploading a client's image to a commercial engine
  discloses it to that vendor and may deanonymise your interest. For sensitive
  material, search a crop that omits identifying detail — or don't search. See
  `investigate-without-getting-made`.

## Confidence grading

- **Confirmed original source** — you have a page that pre-dates every other copy
  found, hosted by a plausible originator (the photographer, the agency, the
  subject's own account), with an on-page date corroborated by an independent
  archive capture, and no larger or earlier version exists.
- **Probable** — earliest copy is consistent across engines and the host is
  plausible, but the date rests only on the page's own claim, or the archive has
  no capture from that period.
- **Match only** — you can show the image appeared at a given URL by a given
  date. Say exactly that. Do not upgrade it to "the original".
- **Unconfirmed** — visual similarity without pixel-level verification, or a
  face-engine hit, or a single engine's result you could not reproduce.

## Worked example

An account posts a photo captioned "police raid this morning, [city]".

Full frame in Lens: nothing but generic riot-police stock. Yandex: a dozen
similar police photos, none matching. TinEye: no results — which I note as
uninformative, since TinEye's index is small.

Crop to the shoulder patch and re-search in Bing using region select. It reads as
a municipal force from a different country than the caption claims.

Crop the shop sign in the background, OCR it in Lens, and search the business
name as text. Two hits, both a street in that other country. Dead end on the
image search itself — but the *text* pivot lands it.

Back to Yandex with the storefront crop: a news gallery from three years earlier,
same street, same shop awning, same barrier arrangement. Photographer credited.
Archive shows a capture of that gallery page two days after its stated date,
which corroborates it.

Conclusion: **confirmed** that this image was published years before the claimed
event, in another country. Recontextualised, not fabricated. Hand the location to
`geolocate-from-pixels` and the photographer credit to `find-anyone`.

## Pivots

| What you got | Send to |
|---|---|
| Location, street scene, storefront | `geolocate-from-pixels` |
| Named people, photographer credit | `find-anyone` |
| Publishing site or agency domain | `who-owns-this-domain` |
| Match page that is gone or altered | `read-deleted-pages` |
| Caption text, business name, filename slug | `google-like-a-spy` |
| Suspected manipulation or generation | `is-this-photo-real` |
| Posting account, avatar reused elsewhere | `hunt-a-handle`, `pattern-of-life-from-socials` |
| Full photo/video geolocation case | `where-was-this-taken` |

Engine-by-engine selection detail:
[reference/engine-matrix.md](reference/engine-matrix.md).
