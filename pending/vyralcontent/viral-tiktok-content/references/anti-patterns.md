# Anti-patterns

These are the things TikTok quietly punishes. None of them get a clear
"your video was demoted" notice; they just stall in the seed cohort and
never expand. Strip every one of them before publishing.

## TikTok watermark on Reels or Shorts

Cross-posting from TikTok with the watermark still on the clip is
explicitly demoted on both Reels and Shorts, with observed reach
reductions up to ~40% on both platforms. Both Instagram and YouTube run
watermark detection.

Fix: strip the watermark before cross-posting (use a clean export from
your editor or a watermark remover), or better, re-export the source
natively for each platform with appropriate aspect ratio and audio.

The right answer for serious multi-platform creators is usually to keep
one source project file and export three versions, not to cross-post the
TikTok with the watermark baked in.

## Generic "follow for more" / "like and share" CTAs

Pattern-matched as engagement bait under TikTok's Integrity and
Authenticity policy. Suppresses distribution. The platform also enforces
against "repetitive non-engaging content publishing."

Why generic CTAs fail:

- The algorithm reads them as soliciting fake signals, not earning real
  ones.
- Viewers tune them out, so the comments fill with nothing useful, which
  hurts the conversation signal.
- They take up the most valuable real estate (the final 2–3 seconds)
  with content that does not drive the metrics the algorithm weights.

What works instead, because it drives metrics the algorithm reads:

- **"Save this for next time you …"** Triggers the save signal.
- **"Send to a friend who …"** Triggers the share signal.
- **"Comment X if you want the rest."** Triggers comment-reply threads
  and gives you content for follow-up posts.
- **No CTA at all.** Loop the final frame and let the rewatch carry it.

## Low-effort AI content

The AI label itself is not penalized. The algorithm does not systematically
demote disclosed AI content. What gets enforced:

- **Unlabeled synthetic media showing realistic people, places, or events.**
  Required disclosure. Tens of thousands of videos removed, accounts banned.
- **Repetitive low-effort AI content.** Mass-produced variant content that
  reads as filler. Enforcement tightened under updated Community Guidelines.

If you use AI in a video that shows a realistic person, place, or event,
toggle the AI-generated disclosure in the upload flow. Embedded C2PA
metadata from DALL-E or Midjourney triggers auto-labels too; assume the
label will appear and post accordingly.

The label is not the problem. Slop is the problem.

## Hashtag stuffing

The "20 broad hashtags" approach is dead. Current guidance from accounts
tracking actual reach data:

- **3–5 highly relevant hashtags**, mixing one broader and a few specific.
- **Captions, on-screen text, and transcripts are the real search surface.**
  TikTok indexes spoken audio and on-screen text more aggressively than
  generic hashtags.
- **Avoid #fyp, #foryou, #viral as the strategy.** They do not target a
  cohort and they signal "I am trying to manipulate distribution."

A specific niche tag (e.g. `#minimalistskincare`) tells the algorithm
who to seed against. A broad tag (`#beauty`) tells it almost nothing.

## Delayed-hook intros

The single biggest hook killer.

- **Logo or intro animation in frame 1.** Burns 1–2 seconds.
- **"Hey guys, welcome back to my channel."** Channel-format signal that
  the FYP does not reward. Loses the second-3 cliff.
- **"Today I'm going to talk about why X matters."** A setup sentence
  that is not the hook.
- **A musical sting before the first spoken line.** Silent dead air feels
  broken to a viewer mid-scroll.

Fix: open on the payoff or the stake. Cut everything before the first
interesting word.

## Business account for a creator who wants trending sounds

Locks you out of the licensed music library (you only get the Commercial
Music Library, which lags real trends by days or weeks) and out of
Creator Rewards monetization.

If you have commercial intent but want reach from trending audio, use a
Creator account. Switch in Settings → Account. You do not lose followers
or analytics.

## Deleting low-performing videos

TikTok can re-test stale uploads if external interest reignites. Deleting
forfeits that delayed-virality optionality.

Fix: archive instead of delete. If a video is genuinely embarrassing,
archive it; the analytics stay, the URL goes private. If it just
underperformed, leave it up.

## Engagement-baiting comments from the same account

Reply-from-the-creator threads work when the replies add information,
clarify, or extend the conversation. They fail when:

- **The creator drops 10 one-word replies** for the comment count.
- **The replies are obvious bot patterns** (same phrasing on every video).
- **Pinned comments asking for engagement** ("comment if you want part 2"
  on every post).

Reply to the comments that move the thread. Pin the one comment that
adds the most context.

## Pad-stretching to 60 seconds for Creator Rewards

Cuts longer than the substance warrants underperform on completion rate.
A 60-second cut that needs to be 35 seconds loses on the ~50% completion
gate, and the Creator Rewards payout depends on the video performing,
not just clearing the length minimum.

If the story is 30 seconds, post the 30-second cut for reach. Do not
stretch.

## Cross-posting without re-shooting the hook

Reels and Shorts hooks are not interchangeable with TikTok hooks. Reels
viewers often watch muted (on-screen text carries the hook). Shorts
viewers come from YouTube search behavior (longer hook arc is tolerated).

Fix: when cross-posting, re-export with platform-appropriate hook
emphasis. At minimum, change the on-screen text overlay for muted
viewers on Reels.

See also: `algorithm.md` for the ranking signals these patterns hurt,
`sounds.md` for the Creator vs Business account decision,
`retention-math.md` for why hook-delay blows the 3-second cliff.
