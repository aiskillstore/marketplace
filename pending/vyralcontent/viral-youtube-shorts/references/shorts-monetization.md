# Shorts monetization

Shorts revenue works differently from long-form. The headline number you
see on the dashboard is not the number that pays. Understanding the
breakdown matters because a few choices (music, length, view definition)
move RPM by a multiple, not by a percentage.

## Views vs Engaged Views

There are two view counts on Shorts and only one of them pays.

- **View.** Registers the instant a Short starts playing or loops. No
  minimum watch threshold. This is the number that shows up on the player
  and in public counts. It is structurally inflated compared to the old
  view definition.
- **Engaged View.** Requires meaningful watch time. This is the only
  number that counts for YPP eligibility and for the algorithm's quality
  signal.

When someone says "my Short got a million views," that is almost always
the View count, not the Engaged View count. Engaged Views tend to land at
some fraction of the View number depending on retention. Reading the raw
View count as proof of performance is one of the most common mistakes.

In Studio, the Engaged Views split is visible in the Shorts Feed analytics
section. That is the number that maps to revenue.

## How the Creator Pool split actually works

Monthly Shorts Feed ad revenue goes into a single pool, then is split in a
specific order:

1. The pool is divided between a **music-licensing bucket** and a
   **Creator Pool**, weighted by how many tracks each Short used.
2. The Creator Pool is then allocated across creators proportional to each
   creator's share of total Engaged Views in that month.
3. Each creator receives **45% of their allocation**. YouTube keeps the
   other 55%.

The 45% is not paid out of the Short's individual ad revenue. It comes out
of your slice of the Creator Pool, after the music bucket has been peeled
off. This is why two creators with the same Engaged Views can have
materially different revenue: the music choices on their Shorts moved them
into different splits.

## Licensed music is the biggest avoidable cost

If a Short uses one licensed track, roughly half of that Short's slice goes
to the music-licensing bucket before your 45% applies. Two or more tracks
reduces it further. The reduction stacks: a Short with three licensed
tracks earns substantially less than the same Short with original audio,
holding everything else constant.

Original audio (voiceover, sound design you made, royalty-free music)
keeps the full slice in the Creator Pool. For monetization-focused Shorts,
original audio tends to RPM measurably higher than trending sound.

For small channels the choice gets sharper. Trending sounds give less
algorithmic lift on channels under roughly 50k subs, and they also cost
revenue. Original audio tends to win both ways. Larger channels still
benefit from trending audio for reach, and have to weigh that against the
revenue cut.

## A Shorts-only revenue trap to know about

A Short with an active Content ID claim that is over 60 seconds is blocked
globally and earns nothing. This rule applies only to Shorts. It is a real
trap for creators who repurpose long-form clips with licensed music: the
clip will upload, look fine, and earn zero. Check Content ID status before
treating the Short as monetized.

## RPM ranges to set expectations

Typical Shorts RPM after the split sits in the $0.03 to $0.10 per 1,000
views range, where "views" here refers to the Engaged View count, not the
inflated View count. The high end of that range is finance, tech, and US-
heavy audiences. The low end is broad entertainment.

Long-form RPM in the same niches sits at roughly $3 to $15. The 30 to 100x
gap is structural, not something a better Shorts strategy closes. The
Shorts revenue math only works if Shorts are feeding long-form watch time.
See `shorts-to-longform-funnel.md`.

## YPP eligibility via Shorts

The Shorts path to YouTube Partner Program eligibility:

- 1,000 subscribers, and
- 10 million valid public Shorts Engaged Views in the last 90 days.

The long-form alternative:

- 1,000 subscribers, and
- 4,000 long-form public watch hours in the last 12 months.

The Shorts path is faster for high-volume channels with strong retention.
The long-form path is faster for channels that already pull 10+ minute
watch sessions. Either path gets you into the Partner Program with the
same benefits.

Note that the 10M is **Engaged Views**, not raw Views. A channel sitting
at 12M raw Views can still miss eligibility if Engaged Views are 8M.

## When to optimize for monetization vs reach

Two cases where the right call is the opposite:

- **Monetization mode.** Original audio, longer Shorts (30 to 60s) to
  clear watch time, clear long-form bridge, accept slightly lower reach
  ceiling. Best for niches where Shorts are a funnel into a high-RPM long-
  form library (finance, tech, education).
- **Reach mode.** Trending sound if you're over the 50k threshold,
  shorter Shorts (15 to 30s) optimized purely for VVSA and loops, accept
  lower direct revenue. Best for brand-building, lead-gen, or selling an
  off-platform product where YouTube ad revenue is a rounding error.

Most creators end up running both modes on different Shorts. Mixing both
on the same Short tends to fail both goals.
