# Bait check

Fast pass/fail for a CTA, caption line, or pinned-comment trigger. Run
any closing line through this before shipping. If it fails on any of
the first six, rewrite. See `references/anti-patterns.md` for the
underlying logic.

## Fail conditions

- [ ] Asks for the **act** of engagement, not the **content**.
      ("Comment YES" vs "tell me what you'd do.")
- [ ] Contains a phrase named or shape-matched as bait: "like for part
      2", "comment YES", "tag a friend", "double-tap if", "share with
      [number] friends", "follow for more", "drop a heart if".
- [ ] Uses a number to demand engagement: "tag 3 friends", "share with
      5 people".
- [ ] Promises a payoff that requires the act of commenting/liking to
      get ("comment YES for the link").
- [ ] Stacks multiple asks: like + save + share + follow + comment.
- [ ] Bait-and-switch: caption promises a free thing, the link or DM
      delivers a sales page.
- [ ] Sits in the closing seconds with no value moment before it.

If any of the above is true, the CTA is bait-shaped. Rewrite.

## Pass conditions (a clean CTA usually has these)

- [ ] One ask, matched to the content type.
- [ ] Tied to a heavy action: send, save, or watch-to-end.
- [ ] Names a specific recipient (for sends) or a specific future
      moment (for saves).
- [ ] Rides a value beat, not the opening seconds.
- [ ] Reads like something a friend would say, not like a pop-up.

## Common rewrites (keep the intent, lose the bait)

| Bait | Rewrite |
|---|---|
| "Comment YES for the link" | Put the link in the pinned comment, say "link's in the pinned comment". |
| "Tag a friend who needs this" | "Send this to your friend who [specific situation]." |
| "Share with 5 friends" | "Send this to the one person who keeps asking you about [thing]." |
| "Like for part 2" | "I'm filming the part nobody talks about. It'll go up [when]." |
| "Follow for more skincare tips" | Cut it. Replace with a save or send. |
| "Comment below what you think" | "Tell me I'm wrong about [specific claim]." |
| "Drop a heart if you agree" | Cut it. |
| "Like, save, share, follow, comment" | Pick one. |

## When in doubt

If you can't tell whether a line is bait-shaped, ask: would a friend
of yours send this exact sentence in a DM with a straight face? If the
answer is no, the algorithm reads it the same way the friend would.
