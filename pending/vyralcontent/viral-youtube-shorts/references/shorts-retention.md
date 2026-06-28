# Shorts retention

Retention on Shorts is two things stacked: the swipe-or-stay decision in the
first 3 seconds (VVSA), and the percentage-viewed curve across the rest of
the video. Both have to clear their gate for the Short to widen. The
retention graph in YouTube Studio is the most useful artifact you have for
diagnosing where a Short is losing people.

## How to read the retention graph

In Studio under a Short's analytics you get a blue line over a gray band.

- The **blue line** is the percentage of viewers still watching at each
  second of this specific Short. It starts at 100% and falls.
- The **gray band** is the channel-typical range for Shorts of similar
  length. Above the band is good. Below it is the problem area.
- The graph is a curve, not the orange "key moments" markers that show on
  long-form videos. There are no spikes from rewinds. There are dips from
  swipes.

Three shapes show up over and over:

1. **Cliff in the first 3 seconds.** The line drops sharply right at the
   start, often from 100% to under 80% inside 3 seconds. Cause: weak opening
   frame, slow first line, logo or welcome-back, or a hook that does not
   match the title or thumbnail. Fix: rewrite the first 3 seconds entirely.
2. **Slow bleed through the middle.** The line falls steadily without a
   cliff. Cause: no escalation, no re-hook, the body is one flat note. Fix:
   add a turn or stakes raise around the 5 to 8 second mark.
3. **Late cliff before the payoff.** The line holds, then drops in the last
   third. Cause: the payoff is buried or never lands, viewers gave up before
   the resolution. Fix: move the payoff earlier or tighten the setup.

A flat line above the gray band across the whole Short is the goal. Most
strong Shorts also show a small bump at the end where loops bring viewers
back past 100%.

## Length benchmarks

These are the percentage-viewed gates where distribution tends to widen.
Missing them is the most common reason a Short stalls.

| Length      | Target avg percentage viewed |
| ----------- | ---------------------------- |
| Under 30s   | ~65%+                        |
| 30 to 60s   | ~50%+                        |
| 60s+        | ~40 to 45%+                  |

Sub-15s Shorts can struggle even at 100% retention because the absolute
watch time is too low to clear the bar. 30 to 45s is the sweet spot for
most niches: long enough to clear watch-time gates, short enough that
retention stays above the curve.

## Loops as free retention

Because Shorts auto-loop, percentage viewed can go past 100%. A re-watch
within roughly 2 seconds of the end is weighted as a partial new view, which
both lifts the watch-time signal and counts toward the loop-rate input.

How to design for loops:

- **Visual loop.** Make the last frame match the first. If the opening is a
  product on a counter and the close is the same product on the same
  counter, the loop feels intentional.
- **Audio loop.** End the voiceover on a beat that hands off cleanly to the
  opening line. Avoid trailing breaths or "thanks for watching."
- **Question loop.** Close on a line that makes the opening line hit
  differently. Viewers re-watch to verify they heard it right.
- **Cliff loop.** End on a tease ("the real reason it works is..."). The
  payoff is at the start of the loop, not the end of the original.

Loops cost almost nothing to add and tend to move both percentage viewed
and recommendation weight measurably.

## The first 3 seconds, specifically

The Shorts Feed punishes any delay in delivering the hook. A rule of thumb:
every second under ~80% retention inside the first 3 seconds compounds into
a meaningful distribution cut.

The opening has to do three things at once:

- Land on a visual that earns the next second. No logo, no animated intro,
  no welcome-back shot.
- Land the first spoken line inside the first ~1.5 seconds. If the line
  takes longer than 2 seconds to say, cut it down.
- Land an on-screen text hook on frame 1, in the safe zone (middle third
  of the screen). Roughly 70% of Shorts viewing is muted, so the on-screen
  text is doing real work, not just reinforcement.

See `viral-hooks` for hook archetypes. The YouTube-specific delivery
constraint is the 3-second window and the safe-zone caption.

## Diagnosing a flopping Short

Order of operations:

1. Pull VVSA from Studio (Analytics > Shorts Feed). This is the gate.
2. Pull the retention graph and find the shape (cliff in 3s / slow bleed /
   late cliff).
3. Map the shape to a cause from the section above.
4. Rewrite the specific beat the graph implicates. Do not rewrite the whole
   Short if only the opening is failing.
5. Re-upload as a new Short rather than as a re-edit of the same video. The
   algorithm grades from upload, not from edit history.

If VVSA is healthy but no long-form click happens, the diagnosis shifts from
retention to funnel. See `shorts-to-longform-funnel.md`.
