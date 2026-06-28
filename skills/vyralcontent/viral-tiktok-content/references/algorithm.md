# The TikTok algorithm

The For You Page is an interest graph, not a social graph. TikTok recommends
videos to a user based on a personalized prediction score, and the highest-
scoring videos surface on that user's feed. Follower count and past hits are
not direct ranking inputs. Every upload is re-tested on its own metadata,
sound, and early signals.

That single fact is why TikTok is harder to game than Instagram or YouTube,
and also why brand-new accounts can outperform established ones on the right
post. Plan content for the algorithm, not the audience you already have.

## The three named ranking categories

TikTok's own documentation groups the signals into three buckets. Optimize
across all three, not just the first.

1. **User interactions.** Likes, shares, comments, follows, completion,
   rewatches, saves, content the viewer creates. This is where retention and
   share-driven signals live, and the heaviest weights sit here.
2. **Video information.** Captions (first 100–150 characters do the heaviest
   lifting), sounds, hashtags, on-screen text, transcripts. This is how the
   algorithm understands what the video is about and who to test it on.
3. **Device and account settings.** Language, country, device type. Mostly
   used to filter the pool of candidate viewers, not to rank within it.

The implication for writing: every hook and every caption is doing double
duty. It has to grab a human in the first second, and it has to tell the
algorithm what kind of viewer to seed the video against.

## Test-then-expand distribution

New uploads do not get pushed to everyone at once. The pattern looks like
this:

1. **Seed cohort.** A small initial pool of viewers whose interests align
   with the video's metadata, sound, and early signals.
2. **Read the signals.** Completion rate, rewatches, saves, shares, comments,
   and follow-through (does the viewer click into the profile?) all feed the
   prediction score.
3. **Expand or park.** Strong signals push the video to progressively larger
   lookalike clusters. Weak signals park it.

TikTok has not published the exact seed sizes or the expansion thresholds.
The staircase shape is real, the specific numbers floating around in creator
guides are third-party estimates. Treat them as directional.

## Follower-first seeding

The seeding pool tends to include the creator's existing followers first
before pushing to lookalikes. This raises the bar on first-day engagement
velocity from people who already opted in: if your followers do not complete,
share, or save the video, the algorithm has fewer reasons to expand.

Practical consequence: a feed that trained itself on one kind of content
(say, GRWM clips) can quietly punish a creator who pivots format, because
the existing followers are not the right seed audience for the new thing.
If you change format, expect a few rough uploads while the algorithm reseeds.

## Stale uploads can re-enter testing

A dormant video can be re-tested months after upload if it picks up new
shares, related searches, or off-platform attention. Two consequences:

- **Do not delete underperformers.** A weak first-day video can light up
  later. Deleting forfeits that optionality.
- **A single share spike can revive a back-catalog video.** Worth pinning
  evergreen pieces and pushing them again on owned channels.

This delayed-virality mechanic is observed consistently across creator
analyses. TikTok has not published a name for it.

## What the algorithm rewards in practice

The signals that consistently correlate with expanded distribution:

- **Completion and watch time** outweigh likes. See `retention-math.md` for
  the benchmarks by length.
- **Saves and shares** outweigh likes too. Saves read as "future intent"
  (the viewer expects to need this again). Shares read as social proof and
  expand reach off-platform.
- **Rewatches and loops** are read as a direct quality signal. Designing
  the final frame to feel like the start of the video drives this.
- **Comments that drive replies** beat comments that sit alone. A thread
  reads as conversation; a list of one-liners does not.
- **Follow-through to profile** tells the algorithm the video bonded the
  viewer to the creator, not just the topic.

## What it does not reward (despite what people assume)

- **Like counts** in isolation. Likes are cheap and shallow.
- **Watch-time gimmicks** that pad seconds without earning them. Padding
  hurts completion rate, which matters more than raw seconds.
- **Hashtag stuffing.** 20+ broad hashtags is dead practice; 3–5 specific
  ones beats it. See `anti-patterns.md`.
- **Posting frequency for its own sake.** Repetitive low-effort posting is
  actively enforced against under "non-engaging content publishing" rules.

## The forked US algorithm

US TikTok now runs on retrained recommendation infrastructure under the US
entity, separate from the global model. The practical effect for creators:
global trends can surface more slowly in the US, domestic content can ride
faster, and cross-platform diversification (Reels, Shorts, owned channels)
is the standard hedge. Build for TikTok, but do not depend on it alone.

See also: `retention-math.md` for the completion benchmarks, `sounds.md`
for the metadata signal hidden in audio choice, `anti-patterns.md` for the
things that quietly demote.
