---
id: "music-shuffle"
title: "Shuffle semantics and perceived variety"
category: "product"
summary: "Choose uniform shuffling or constrained variety according to the playback product contract."
aliases: ["shuffle","fisher yates","artist aware shuffle","karışık çalma","playlist shuffle","aynı müzisyeni art arda duymak","şarkıları karışık çalma","aynı sanatçı peş peşe","çalma listesi karıştırma","gerçek rastgelelik","müzik uygulamasına karışık çalma","add shuffle to music app"]
decisions: [{"when":"The product promises equal odds for each permutation","use":"Use Fisher–Yates with an unbiased bounded random integer at each step.","tradeoff":"Clusters are legitimate and tests should not reject them."},{"when":"The product prioritizes perceived variety","use":"Schedule by groups with an explicit repeat rule and a documented fallback for skew, using random tie breaks.","tradeoff":"Constrained schedules sacrifice permutation uniformity."}]
checks: ["Prove the output is a permutation of queue-entry IDs and leaves the input order intact, including two entries that refer to the same track.","For Fisher–Yates, exhaust all bounded draws for a three-entry queue and observe all six permutations exactly once.","Check an interleavable queue, a single artist, and an excess of one artist against the documented repeat limit.","When resume must preserve the order, restart between two tracks and verify the next queue-entry ID is unchanged.","If variety is promised across an edit, verify the next artist against the last played artist and preserve every unplayed entry."]
sources: [{"title":"NIST dictionary entry on Fisher–Yates","url":"https://www.nist.gov/dads/HTML/fisherYatesShuffle.html"},{"title":"ECMAScript Array.prototype.sort and consistent comparator requirements","url":"https://tc39.es/ecma262/#sec-array.prototype.sort"},{"title":"Spotify Engineering on perceived randomness","url":"https://engineering.atspotify.com/2025/11/shuffle-making-random-feel-more-human"}]
related: ["persistent-playback-queue","cryptographic-randomness","property-based-testing"]
---

<!-- Generated record title. -->
# Shuffle semantics and perceived variety

## Scenario

A fitness app has a six-entry offline playlist. One user expects every order to be equally likely. Another wants fewer runs of the same performer. Decide which behavior the control promises before choosing the algorithm. Keep the entire set of queue entries in the result, even if two entries refer to the same track.

## Failure modes

Random sort comparators can give different results for the same pair and do not meet the ordering contract of a sort. Sorting by a random key assigned once per entry is a different technique, with tie semantics and a sort cost to account for. Uniform draws can legitimately cluster. Forcing separation changes the output distribution, while silently discarding a repeated track changes the playlist. Rebuilding the queue on resume can replay or skip entries.

## Explain it simply

A fair draw can put similar tracks next to each other. A variety mode can spread those tracks out while keeping every track. The right option depends on whether equal chances or fewer repetitions matter to the listener.

## When not to use

Use a uniform shuffle for a statistical experiment or a control that promises equal odds per ordering. Artist-aware ordering serves a different preference and can exclude most permutations. If the user asks for only the next item or a recent-play cooldown, define that smaller behavior before building a full artist-aware queue. Specify separately what resuming and explicitly reshuffling do to playback progress.

## Implementation guidance

For a full uniform shuffle, copy the queue and iterate backward from its final index to index one. At each position i, choose j independently and uniformly from the inclusive range zero through i, then swap the two entries. With an unbiased bounded draw, the construction gives each permutation the same probability and takes linear time. Inject the bounded draw for repeatable tests. Choose a source appropriate to the product and use a bounded drawing API or rejection sampling when reduction would bias the range.

For an artist-aware mode, group entries by stable artist identity, randomize within each group, then choose a substantial remaining group different from the last one when possible. A common policy chooses the largest eligible group and uses a random draw to break ties. When only the last group remains, emit its remaining entries under the declared fallback. Preserve a unique identity per queue entry. State how collaborations or missing artist metadata are grouped so the rule uses stable inputs.

## Worked example

With two entries each from artists A, B and C, A A B B C C is a legitimate uniform result. A B C A B C is a valid variety result. A single fixed run can demonstrate the listener experience, while exhaustive bounded draws on three entries can verify the Fisher–Yates permutation mapping. The repository's six-track demonstration compares these goals with a random-comparator baseline using a repeatable seed. Its repeat counts illustrate one sample, not a statistical evaluation of sorting behavior.

Spotify Engineering describes a Fewer Repeats method that scores multiple random candidate orders by how recently tracks were heard, then picks the highest-scoring order. The artist-grouping rule here is a standalone design choice for products that want to reduce back-to-back artists. The published Spotify example supports the distinction between statistical randomness and listener perception.

## Architecture notes

Place order generation in a pure queue-building policy when separate service ownership or deployment is unnecessary. The playback controller should consume queue entries and advance one cursor. When resume must preserve a session, persist ordered entry IDs and progress together, or retain the seed, algorithm version and immutable source revision needed to reconstruct exactly that order. Apply playlist edits through a defined queue revision, with any rescheduling limited to the unplayed portion unless the listener starts a new shuffle. If the variety rule covers the transition across an edit, pass the last played artist into the new ordering policy. After playing A, the remaining entries A and B should start with B even though either order has zero repeats within the remaining queue alone.

## Edge cases

For n total entries with m from the dominant artist, n - m other entries create at most n - m + 1 gaps. Thus at least max(0, 2m - n - 1) dominant adjacent pairs are unavoidable. With four A entries and only B and C as separators, at least one A adjacency remains. Also cover empty and singleton queues, all entries from one artist, two queue entries pointing to one track, and metadata changes between shuffle and resume. For the all-one-artist case, preserve every entry and make the fallback explicit.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The product promises equal odds for each permutation** Use Fisher–Yates with an unbiased bounded random integer at each step. Clusters are legitimate and tests should not reject them.
- **The product prioritizes perceived variety** Schedule by groups with an explicit repeat rule and a documented fallback for skew, using random tie breaks. Constrained schedules sacrifice permutation uniformity.

## Verification

- Prove the output is a permutation of queue-entry IDs and leaves the input order intact, including two entries that refer to the same track.
- For Fisher–Yates, exhaust all bounded draws for a three-entry queue and observe all six permutations exactly once.
- Check an interleavable queue, a single artist, and an excess of one artist against the documented repeat limit.
- When resume must preserve the order, restart between two tracks and verify the next queue-entry ID is unchanged.
- If variety is promised across an edit, verify the next artist against the last played artist and preserve every unplayed entry.

## Sources

- [NIST dictionary entry on Fisher–Yates](https://www.nist.gov/dads/HTML/fisherYatesShuffle.html)
- [ECMAScript Array.prototype.sort and consistent comparator requirements](https://tc39.es/ecma262/#sec-array.prototype.sort)
- [Spotify Engineering on perceived randomness](https://engineering.atspotify.com/2025/11/shuffle-making-random-feel-more-human)

## Related decisions

- [Persistent playback queue and resume behavior](persistent-playback-queue.md)
- [Random sources for tokens and product choices](../security/cryptographic-randomness.md)
- [Property-based tests for invariants](../testing/property-based-testing.md)

<!-- End generated record details. -->
