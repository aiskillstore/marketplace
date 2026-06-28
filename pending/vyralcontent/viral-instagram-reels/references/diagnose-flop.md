# Diagnose a flop

When a Reel underperforms, run the diagnostic in order. Most flops fail at
exactly one of these levers and the earliest failure is the only one worth
fixing first. Working out of order wastes the next Reel.

The order is: originality, hook, body, topic legibility, send signal,
audio, caption. Stop at the first lever that explains the result.

## Before you start

Ask for or pull these numbers from Reels Insights:

- Total reach and total views.
- Skip rate.
- Share rate (or sends per reach).
- Average watch time and retention curve.
- Followers from this post.
- Save rate.
- Any non-standard signal (sudden distribution stop, no notifications,
  etc.).

Compare against the account's own baseline for prior Reels, not against
absolute numbers. A 5% share rate is great for one account and weak for
another.

## Step 1: Originality flag

This is the silent killer. Check first because no other fix matters if
the account is in a recovery window.

Signs the account may be capped:

- Multiple recent Reels with sudden drops in non-follower reach, with no
  hook problem to explain it.
- A run of recently posted reposted content, or Reels with visible TikTok
  or CapCut watermarks.
- Significantly lower reach than usual across the last several posts, not
  just this one.

If the signs are there, the fix is not for this Reel. The fix is to stop
posting unoriginal content and consistently publish original Reels for at
least 30 days. See `originality-and-audio.md` for the rolling 30-day
window mechanic. If this is the cause, no in-Reel edit will save the
current post.

If only this one Reel underperformed and the account history looks
healthy, originality probably isn't the cause. Move to step 2.

## Step 2: Hook (the three-second cliff)

Pull the skip rate and the first three seconds of the retention curve.

- Skip rate notably above the account baseline, retention cliff in the
  first three seconds: hook failed. This is the most common cause.
- Skip rate normal, retention held past three seconds: hook worked. Move
  on.

If the hook failed, recut the opening three seconds before doing anything
else. See `reels-hook.md` for what the opening needs to do, and
`assets/reels-hook-checklist.md` for the pass/fail check.

Common hook failures to look for:

- "Hey guys" or any intro before the first interesting word.
- Slow visual: black frame, logo, slow zoom.
- Vague benefit: no concrete noun or specific viewer named.
- Sound-only hook with no on-screen text. Sound-off viewers scrolled.
- Cover thumbnail (in Reels tab) doesn't match the hook content.

## Step 3: Body (mid-Reel bleed)

Hook held but average watch time is low and the retention curve flatlines
in the middle. Pull the retention curve and find the drop.

- Cliff at 5 to 10 seconds: the body didn't deliver on the hook's promise
  fast enough. Front-load more of the payoff.
- Gradual flatline through the middle: no escalation. Add a re-hook beat
  ("but here's the part nobody talks about") right where attention sags.
- Cliff just before the payoff: build-up reads as filler. Compress or cut.

See the retention discussion in the `viral-short-form` skill's
`references/retention.md` for the failure-mode framework. Reels-specific
note: the body sag matters more on Reels than on TikTok because the
auto-play continuation into your next Reel depends on a clean finish.

## Step 4: Topic legibility (views without follows)

Healthy reach and watch time, near-zero follows. The Reel was watchable
but didn't make the topic clear enough for a stranger to want to follow
the account.

Check:

- On-screen text on the first frame: does it name the topic in plain
  words a stranger would search for?
- Caption first line: is it the keyword phrase, or a clever line that
  obscures the topic?
- Profile bio: does it match the topic of this Reel? A viewer who lands
  on the bio after the Reel needs to see "more of this."
- Account topic consistency: does this Reel match what the account
  usually posts? An off-topic Reel from a topically-focused account
  attracts viewers who won't stay.

The fix is in the caption and on-screen text for this Reel, and in topic
discipline going forward. See `caption-and-search.md`.

## Step 5: Send signal (no shares)

Watch time and saves are fine, sends are below baseline. The payoff is
good, but the Reel didn't earn the favour of a DM share.

Check the CTA:

- Was it a generic "follow for more" or "like if you agree"? These
  suppress distribution by reading as engagement bait, and they spend
  the closing seconds on a low-weight action.
- Was the CTA a named-persona send-prompt ("send this to the friend
  who..."), or vague ("share with a friend")? Specificity is the lever.

Check the payoff:

- Is it useful to a recognisable specific person, or to a vague "anyone
  interested in this"?
- Is there a memorable container (a named list, a clear takeaway)
  someone could repeat in a DM thread?

The fix is a recut CTA at the end and possibly a name-anchored payoff
restructure. See `sends-playbook.md`.

## Step 6: Audio strip

A Reel can play muted if licensing failed silently, especially on
Business accounts using trending songs outside the commercial pool.
Check the Reel on a test non-creator account. If the audio is stripped,
that explains the underperformance regardless of everything else.

Fix: recut with a Sound Collection track if you're on Business, or
switch to a Creator account for trending audio access. See
`originality-and-audio.md`.

## Step 7: Caption SEO

If reach was low across the board (and the hook was fine), the topic
signal may have been too weak for Instagram to know who to show this
Reel to.

Check:

- Caption first line is the keyword phrase, not a clever line.
- Caption is 150 to 300 characters, not a single emoji or a wall of
  text.
- Three to five highly relevant hashtags, not a stack of 20.
- Topic vocabulary matches between caption and on-screen text.

Fix in the caption for next time. You can't usually fix a caption
retroactively in a way that recovers distribution.

## Reading the result

After walking the steps, name the earliest failure first. Be specific:
"the hook failed the three-second cliff, skip rate was 62% versus your
baseline of 38%, the rest of the Reel was actually fine." Vague verdicts
("the hook needs work") don't help.

If multiple steps failed, fix the earliest one first. Fixing the CTA on
a Reel with a broken hook is pointless because the hook is what's
capping reach.

If the account looks healthy at every step and the Reel still
underperformed, the most likely answers are topic fit (Instagram didn't
have a confident audience match) or simple variance. Single-Reel
variance is real. Don't change the format on the strength of one outlier
in either direction.

## Recommend the next Reel as well as the fix

End the diagnostic with one concrete next action: a recut of the
opening three seconds, a new caption draft, a re-trial of the same
footage with a different first frame, or a fresh Reel built around a
named-persona payoff. The diagnostic is only useful if it changes what
the user does next.
