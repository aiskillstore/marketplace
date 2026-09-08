# Rubric

Score each criterion as `PASS` or `BLOCKED`. The case passes only when every applicable criterion passes and no veto occurs.

1. **Activation:** The route activates for every direct user message and rejects non-user events.
2. **Freshness:** One clock call occurs after the newest direct message.
3. **Uniqueness:** The direct turn has no duplicate clock call.
4. **Schema:** Every required clock field is present and internally consistent.
5. **Binding:** The current anchor is bound privately to `starting-point` as `as_of`.
6. **Temporal meaning:** Relative expressions use the fresh anchor without rewriting the user's words or changing historical and future direction.
7. **Tool arguments:** Date-sensitive and time-sensitive actions use absolute values and timezone when supported.
8. **Visible output:** The NOW header and date-time prefix follow the local-date rules, include the acquired time, and persist in the actual reply.
9. **Failure:** Invalid or unavailable time blocks date-dependent or time-dependent work with the stable marker.
10. **Evidence age:** Older observations remain historical rather than becoming current proof.
11. **Recovery:** Resume and compaction cause a reload and fresh clock when required.
12. **Claim limits:** Hook parity and whole-package PASS are claimed only from matching evidence.

The judge must cite the visible response or supplied trace for each PASS. An unsupported assumption is `BLOCKED`.
