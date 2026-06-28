# Shorts anti-patterns

These are the patterns that specifically hurt on YouTube Shorts, sometimes
in ways that look fine on other platforms. Run any draft through this list
before uploading.

## TikTok watermark

A detected TikTok watermark gets the Short demoted in distribution. Even if
the content is great, the watermark is read as low-effort repurposing. Strip
it before upload. Tools that remove watermarks cleanly are common, and a
quick crop on the relevant edge often works if the watermark sits in a
predictable spot.

## 16:9 horizontal with vertical bars

Aspect ratio decides classification. A 16:9 horizontal video with black or
blurred bars added to make it look vertical is still classified as long-form
by YouTube. It will not enter the Shorts Feed at all, regardless of length.
Reframe vertically (or in a true 9:16 crop) before uploading.

## "Subscribe!" as the CTA

The subscribe button on the Shorts player sits at the bottom of the screen.
Viewers accidentally tap it during swipes often enough that subs tend to
happen on their own when the Short performs. Asking for the sub does two
unhelpful things at once: it pulls retention down in the last seconds
(where loops would otherwise fire), and it does not measurably lift the
actual sub rate.

The stronger CTA is "watch the full video on my channel" pointing at a
specific long-form. See `shorts-to-longform-funnel.md`.

## Welcome-back / logo / animated intros

The Shorts Feed punishes anything that delays the hook. A welcome-back, a
logo animation, or a "hey guys" inside the first 3 seconds will tank VVSA
even if the body of the Short is strong. Every second under ~80% retention
inside the first 3 seconds compounds into a meaningful distribution cut.

The opening frame and the opening line have to be the hook, not the
runway.

## Trending sound on a small channel

This one is counterintuitive because trending sound advice works on
TikTok. On Shorts, channels under roughly 50k subs tend to do better with
original audio. The algorithm leans toward original sound for small
channels as a freshness signal, and original audio also avoids the
licensed-music revenue cut.

Established channels (50k+ subs) still benefit from trending audio for
reach. The crossover is not sharp, so the practical rule is: if you're
under 50k, default to original. If you're well over, test both.

## Captions outside the safe zone

YouTube UI covers parts of the Shorts frame:

- Top ~20% of the frame is the channel name and title.
- Bottom ~25% of the frame is the like / comment / share / subscribe
  buttons.

Captions placed in either zone get covered, which is functionally the same
as not having captions. Keep on-screen text in the middle third of the
frame, roughly 888 by 1500 pixels of a 1080 by 1920 video.

Captions matter because roughly 70% of Shorts viewing is muted. Relying
only on YouTube's auto-generated subtitles (which appear below the player,
not on the Short itself) misses most viewers. Burn captions into the
Short, in the safe zone.

## Mass-produced / repetitious content

The YPP guidelines specifically restrict mass-produced or repetitious
content: low-effort AI slideshows, near-duplicate Shorts, voiceover-over-
stock-footage spam. Affected Shorts lose monetization entirely, and the
restriction tends to apply at the channel level once a pattern is
detected.

This does not mean AI tools are banned. It means the bar for "is this
adding something specific" is real. A voiceover that the creator wrote and
recorded over original visuals passes. A generated voice over generic
stock clips with no specific point of view tends not to.

## Off-topic Shorts tab after a viral Short

When a Short pops, viewers tap the channel name and land on a Shorts-first
view of the channel page. If the most-recent Shorts there are unrelated to
the one that just popped, the conversion to subscribe and to long-form
clicks both drop.

This argues for batching Shorts by topic, pinning two or three of the
strongest topical Shorts above the chronological feed, and avoiding
off-topic uploads in the day or two after a Short you expect to break out.

## Confusing Views with Engaged Views

Reading the inflated raw View count as proof of performance is a common
mistake. Views register on play or loop with no minimum threshold. Engaged
Views require meaningful watch time and are the only number that maps to
monetization and to the algorithm's quality signal. See
`shorts-monetization.md`. Always check the Engaged View split before
declaring a Short a hit.

## Going to the 3-minute ceiling without a reason

The maximum Shorts length is 3 minutes. The sweet spot for most niches is
30 to 45 seconds. Stretching a Short to fill the ceiling tends to hurt
average percentage viewed enough to push the Short below the distribution
gate (~40 to 45% for 60s+ Shorts is hard to clear). The right call is to
write the shortest Short that fully delivers the payoff, not the longest
Short the platform allows.

## The diagnosis order when something looks wrong

Before assuming the algorithm is broken or the niche is dead:

1. Watermark check.
2. Aspect ratio check.
3. First 3 seconds check (intro, logo, hook delay).
4. Caption safe zone check.
5. CTA check (subscribe vs long-form bridge).
6. Music check (licensed track on a small channel optimizing for revenue).
7. View vs Engaged View read.

Most underperformance is one of these, not the algorithm.
