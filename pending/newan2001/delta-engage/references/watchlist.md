# Watchlist flywheel — emergent KOL / buyer discovery

The watchlist is **emergent, not required up front**. You never ask the user to seed it (though
they may in onboarding Stage 3). It grows itself from what proves worthy, run over run.

## Why it works this way

Two motions, in tension, both useful:
- **Explore** = topic/keyword search. Finds *new* accounts on pure relevance. Broad, cheaper to be
  wrong, this is how cold start works with zero seeds.
- **Exploit** = the watchlist. Cheap, high-precision monitoring of accounts that have *already*
  proven worthy. Narrow, high hit-rate.

Discovery (explore) feeds the watchlist; a healthy watchlist (exploit) frees search budget to keep
exploring. The flywheel: worthy authors recur → get promoted → become cheap reliable signal → you
spend the freed-up search effort finding the next ones.

## Cold start (no watchlist)

Run purely on ICP + `topics`. Topic/keyword search surfaces opportunities on relevance alone.
Day-one value with zero seed accounts. Every worthy author found is a promotion candidate for next
time.

## Promotion — quality-weighted recurrence, NOT volume

`scripts/watchlist_tally.py` reads `run_history` and the current run, and surfaces candidates. The
rule it encodes, and the rule you must honor when presenting:

- Promote an author who hits **N worthy posts within a window** (default: 2 worthy posts in the
  last ~4 runs / ~2 weeks), **or** a high **worthy-to-total ratio** (they show up a lot and are
  almost always worthy).
- **"Worthy"** = cleared both the relevance and engagement bars in a run (made the ranked set above
  threshold), *not* "posted a lot." A prolific poster who's rarely relevant must **not** get
  promoted — that's the failure mode this guards against.

## Confirm, never auto-add

The script only *nominates*. You present:

> "These accounts keep coming up in your worthy set — add to your watchlist?
>  • @author_a (reddit) — 3 worthy posts in the last 2 weeks
>  • @author_b (linkedin) — 2 worthy posts, 2/2 worthy
>  Add which?"

Only on the user's yes do you write them into `config.watchlist`. This is the same
draft→confirm→apply discipline as the ICP and the top-N set.

## Decay — keep the list from bloating

Accounts that stop being worthy age back out. `watchlist_tally.py` decrements / flags entries
whose `last_worthy_run` is older than the decay window (default ~6 runs / ~3 weeks). Surface
decayed entries as a gentle "these went quiet — drop them?" rather than silently removing, so the
user stays in control. The goal is a small, live list of currently-worthy voices.

## Two audiences

- **KOL voices** (large audience, brand value) **emerge** from recurrence — you rarely seed these;
  they surface because they keep producing worthy, well-engaged posts. Weighted up when
  `primary_goal == brand`.
- **ICP buyers** (direct relevance, reachable) can be **seeded deliberately**: from the ICP's
  titles + firmographics, use `Apollo:apollo_mixed_people_api_search` (fully-qualified) to find
  matching people, resolve LinkedIn URLs, and propose them as watchlist entries. Most relevant
  when `primary_goal == pipeline`. Always confirm before adding.
