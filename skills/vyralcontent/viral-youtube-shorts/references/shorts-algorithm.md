# Shorts algorithm

The Shorts Feed runs on its own ranking lane, separate from long-form
recommendations. A Short does not drag or lift the channel's long-form
performance, and a channel's subscriber count barely counts toward how far a
single Short goes. Each Short is judged on its own merits.

## What the Shorts Feed actually ranks on

The signals that move distribution, in roughly the order they matter:

1. **VVSA (Viewed vs Swiped Away).** The top-of-funnel gate. Under ~60% tends
   to flop. 70 to 90% tends to break out. 30/70 viewed/swiped means the Short
   is effectively dead. This replaces CTR-on-thumbnail as the entry signal.
2. **Average percentage viewed.** Inside the watch, how much of the Short the
   viewer actually consumes. Benchmarks where distribution tends to widen:
   ~65% for sub-30s Shorts, ~50% for 30 to 60s, ~40 to 45% for 60s+.
3. **Loop rate.** A re-watch within roughly 2 seconds of the end gets weighted
   as a partial new view. Because Shorts auto-loop, percentage viewed can
   exceed 100%, and over 100% is a strong positive signal.
4. **Shares.** Heavy weight on the Shorts Feed because they predict reach
   outside the algorithm.
5. **First-frame engagement.** What happens in the first 1 to 3 seconds is
   counted on its own, not just as part of overall retention.
6. **Likes and comments.** Weak correlation with distribution on Shorts.
   Useful as community signal, not as a lever to chase.

## Viewer satisfaction is a real input

YouTube also pipes post-view survey results into ranking. The framing the
platform uses is "satisfaction, not raw watch time." On Shorts this gets
enforced harder than on long-form because a swipe-away is a clean negative
signal. Designing a Short that scores high on watch time but feels like a
bait-and-switch tends to underperform what its raw numbers predict.

## How seeding works (and why subs barely help)

A new Short tends to start with a small initial test audience, roughly 50 to
500 viewers. About 70% of that initial pool is non-subscribers. So the first
read on a Short is mostly from people who do not know the channel. If the
opening 3 seconds hold them, the Short widens into the next ring. If not, the
test ends fast.

The practical consequence: do not rely on existing subscribers to "warm up" a
Short. Write the opening as if every viewer has never heard of the channel,
because most of them haven't.

## Why small channels can spike on a single Short

The framing the platform repeats is "we look at video and topic, not channel
or creator." That is the mechanism behind the small-channel spike: a strong
VVSA plus a high loop rate on a topical Short can outpace a much larger
channel's weaker Short on the same topic. The corollary is that you can post
ten Shorts, have nine die in the seeding window, and have one cross a million
views because that single video cleared the gates. This is normal. Treat each
upload as a swing, not a trend reading.

## Where Shorts can surface

A Short can appear in at least four places:

- The vertical **Shorts Feed** (the swipeable player). This is where the
  ranking signals above apply.
- The **Shorts shelf** on the home feed (a horizontal carousel). After the
  home feed redesign, roughly 80% of available home-feed slots are Shorts.
- The **Shorts tab** on the channel page. Viewers tapping the channel name
  from a Short tend to land here first.
- **Search**, with a dedicated Shorts filter. Title, description, spoken
  transcript, and on-screen text are all indexed for Shorts, which makes
  search a real long-tail distribution channel for evergreen topics.

See `shorts-search-and-shelf.md` for how to optimize for the shelf and search
specifically.

## What the algorithm does not reward

- Subscriber count, on a single-Short basis. A 50-subscriber channel and a
  500k-subscriber channel get roughly the same seeding pool on a new Short.
- Upload frequency, as a standalone signal. A high-VVSA Short once a week
  outperforms a daily stream of low-VVSA Shorts.
- Trending sounds, for small channels. Original audio tends to win for
  channels under roughly 50k subs. Bigger channels still benefit from
  trending audio.
- Cross-platform watermarks. Detected TikTok watermarks get demoted in
  distribution. See `shorts-anti-patterns.md`.

## How to use this for diagnosis

If a Short underperforms, the diagnosis order is:

1. Check VVSA first. If it is under 60%, the opening 3 seconds are the
   problem, not the body. Rewrite from the first frame.
2. If VVSA is healthy but average percentage viewed misses the length
   benchmark, the body is bleeding out. See `shorts-retention.md`.
3. If percentage viewed clears 100%, loops are firing. Reach is being limited
   by something else (shares, topic ceiling, anti-pattern). See
   `shorts-anti-patterns.md`.
4. If long-form clicks are zero on a Short that performed, the funnel is
   missing, not the video. See `shorts-to-longform-funnel.md`.

The right number to read first is always VVSA. Raw views are a vanity number
that can rise from inflated view counting, and likes barely move ranking.
