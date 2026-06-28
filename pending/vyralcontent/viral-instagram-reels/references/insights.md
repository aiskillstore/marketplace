# Reels Insights

The Insights dashboard for a single Reel is the only honest feedback loop on
the platform. View count alone tells you almost nothing. The post-watch
behaviour metrics tell you what actually happened: who shared, who skipped,
who watched and forgot, who watched and followed.

The job of this reference is to teach you which metrics map to which levers,
so a flop or a hit can be read for what it actually was.

## The metrics that matter

The Reels Insights dashboard is organised by tabs (Overview, Engagement,
Audience). The metrics below are the ones worth acting on. Other numbers
in the dashboard (impressions, profile visits, etc.) are downstream signals
that mostly track the ones below.

### Skip rate

The percentage of viewers who scrolled away before a meaningful watch
threshold (typically the first three seconds). This is the cleanest read on
your hook.

- **High skip rate, low total views**: the hook failed the three-second
  cliff. The seed test never expanded. Rewrite the opening three seconds.
- **High skip rate, high total views**: rare. Usually a Reel that benefited
  from a strong audio trend or a topic spike. The hook still needs work for
  the next Reel.
- **Low skip rate**: the hook held. Whatever else underperformed, the
  opening did its job. Look downstream for the failure.

Your baseline depends on your account and your niche, so compare against
your own prior Reels, not against an absolute number.

### Share rate (and sends per reach)

The percentage of viewers who sent the Reel in a DM. The single most
important number for cold growth.

- **Above your baseline**: the payoff is shareable and the named-persona
  CTA worked. This is the metric that buys non-follower reach. Reels with
  above-baseline share rate tend to keep compounding for days.
- **Below your baseline**: the Reel didn't earn the favour. Either the
  payoff isn't useful to a specific person, or the CTA was generic, or
  both. See `sends-playbook.md` for the rewrite.
- **High views but low share rate**: classic "viral but flat" Reel. The
  audio or topic spiked the reach, but the Reel didn't earn the share that
  would have made the reach sustained.

### Retention curve and average watch time

A graph of where viewers dropped off, plus the average percentage watched.
Reading the curve is more useful than reading any single number.

- **Cliff in the first three seconds**: hook problem. (Match this against
  skip rate; they tell the same story two ways.)
- **Cliff at 5 to 10 seconds**: hook held but the body didn't deliver on
  the promise fast enough. Front-load more of the payoff.
- **Gradual flatline in the middle**: no escalation. The Reel opened well
  and then bled out. Add a re-hook in the middle or compress the section.
- **Spike at the end (rewatches)**: the loop landed. Lean into this format.
- **Cliff right before the payoff**: viewers gave up before getting the
  value. Either the body is too long, or the build-up reads as filler.

A Reel with strong retention can outperform a shorter Reel with weak
retention because total seconds watched matters. Don't shorten reflexively
if the retention curve is healthy.

### Followers from this post

The number of new followers Instagram attributes to viewing this specific
Reel. The most actionable single addition to Insights.

- **High views, near-zero follows**: the Reel got reach but didn't make the
  topic legible. Viewers watched and scrolled. The fix is in the topic
  signal: on-screen text, caption keyword, profile bio (does it match the
  Reel's topic?).
- **Moderate views, healthy follows**: the Reel did the job a Reel is meant
  to do. The topic was clear, the value was clear, the profile sold the
  follow.
- **Followers from this post versus your average**: the relative number
  matters more than the absolute. A Reel that drove three times your usual
  follow rate is a format to repeat.

A "viral" Reel that brings no followers is not actually growth. Use this
metric to separate views from real growth.

### Save rate

The percentage of viewers who saved the Reel. Weighted below sends, but
still a real signal of useful content (especially for tutorials, lists,
recipes, and reference material).

- **High save rate**: viewers want to come back to it. Common on educational
  or product-list Reels. Pairs well with named-list payoffs (see
  `sends-playbook.md`).
- **Low save rate on educational Reels**: the content wasn't actually
  useful enough to keep, or the payoff was unmemorable. Compress the
  takeaway into something nameable.

### Likes per reach

The like rate from non-followers. Mostly a connected-reach signal (it
helps you get re-shown to existing followers in main feed), not a cold-
reach signal. Don't optimise heavily for it. Sends and watch time matter
more for new audience.

### Comments

Comments matter mostly for connected reach and for community signal. A Reel
with a healthy comment thread keeps surfacing back to your followers in
main feed. The thread itself can also be the reason a viewer sends or
follows. But a Reel can be a hit on cold reach with very few comments if
the topic doesn't naturally invite discussion.

### Post-watch behaviour

A grouped read of what viewers did after the Reel: visited the profile,
followed, scrolled past, or kept watching another of your Reels (auto-play
into your next Reel). The auto-play continuation is particularly useful:
a high "watched your next Reel" rate means your account's topical
consistency is paying off.

## Reading a Reel as a whole

Most Reels fail for one of four reasons. The Insights dashboard tells you
which one.

1. **Hook failed.** Skip rate is high. Retention cliff in the first three
   seconds. Few views, regardless of everything else. The fix is in the
   opening. (See `reels-hook.md`.)
2. **Body failed.** Hook held but retention bleeds out in the middle. The
   fix is in escalation, pacing, and the re-hook.
3. **Topic failed.** Healthy reach and watch time but zero follows and low
   sends. The Reel was watchable but didn't make the topic legible enough
   to act on. The fix is in on-screen text and caption keyword.
4. **CTA failed.** Watch time and saves are fine, sends are low. The
   payoff is good, but the Reel didn't earn the favour of a share. The fix
   is a named-persona send-prompt. (See `sends-playbook.md`.)

A Reel can fail for more than one reason. Read the metrics in order and
fix the earliest failure first. Fixing the CTA on a Reel with a broken
hook does nothing.

## What not to read

- **Total view count.** Without a denominator (reach) and the share /
  follow context, view count is vanity. A Reel with 100K views and zero
  follows is a worse outcome than a Reel with 10K views and 200 follows
  for an account that's trying to grow.
- **Likes alone.** Likes are the cheapest action and the weakest distribution
  signal on Reels.
- **Day-one numbers as a verdict.** Reels can keep distributing for days
  or weeks if the share signal stays healthy. Don't write off a Reel on
  the 24-hour read alone unless the hook clearly failed.

## Working with the rest of the skill

Use `assets/insights-readout.md` to capture the numbers in a structured
form, then use the failure-mode list above to decide what to fix. For
diagnosing a specific underperforming Reel, walk `diagnose-flop.md`.
