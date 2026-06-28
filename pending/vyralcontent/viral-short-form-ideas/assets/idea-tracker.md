# Idea tracker

The minimum-viable pipeline. Five statuses, one expiry rule, no
gold-plating. If you find yourself adding fields, you're in
productivity-theater mode (see `references/anti-patterns.md`).

## The statuses

```
INBOX     -> raw capture, untouched
TRIAGE    -> evaluated against the filters; either promoted or killed
SCRIPTED  -> hook, payoff, format, length target written
FILMED    -> recorded but not yet posted
PUBLISHED -> shipped, with a performance grade after 7 days
```

## The five fields (don't add more)

```
- Idea (one line)
- Pillar
- Hook draft
- Status (Inbox / Triage / Scripted / Filmed / Published)
- Last touched (date)
```

Once it's Published, add one more field:

```
- 7-day grade (1 to 10) and one sentence on what worked or didn't
```

## The 90-day expiry rule

Any idea in Inbox or Triage that hasn't been touched in 90 days is
archived or killed. No exceptions, no "but I might come back to it."
If you'd come back to it, you would have by now. The backlog rotting
is worse than losing a few real ideas.

When you archive, write one sentence on why. Sometimes the why turns
out to be wrong six months later and the idea comes back as
inspiration for a different angle.

## The template

```
─────────────────────────────────────────────────────────────────────────────
IDEA              | PILLAR  | HOOK DRAFT         | STATUS    | LAST TOUCHED
─────────────────────────────────────────────────────────────────────────────
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
                  |         |                    |           |
─────────────────────────────────────────────────────────────────────────────
```

## Triage cadence

Run a triage session once a week, ~30 minutes. Goal: every Inbox item
either gets promoted to Triage (with a hook draft) or killed. Don't
let items sit in Inbox for weeks; that's how the wall starts.

In the triage session itself, use `references/idea-evaluation.md` as
the filter pass.

## Sanity rules

- An Inbox item with no hook draft is a topic, not an idea. Either
  draft a hook or kill it.
- A Scripted item that hasn't moved in 14 days is probably the wrong
  shoot. Either schedule the shoot or move it back to Triage.
- A Filmed item that hasn't shipped in 7 days is a calendar problem,
  not a content problem. Fix the calendar.
- The Published column is for learning, not for vanity. The 7-day
  grade and the one-sentence note are the most valuable rows in the
  whole tracker.

## What this tracker is not

It is not a swipe file. Swipe files hold inspiration from other
people's content. This tracker holds your own ideas in motion. Keep
them in separate places.

It is not a publishing calendar. Calendar tools handle the publish
schedule, the captions, and the platforms. This tracker handles the
upstream pipeline.

It is not a CRM, a goal tracker, or a habit log. If you're tempted to
add those, start a new doc for them. The point of this one is that it
stays small enough to actually use.
