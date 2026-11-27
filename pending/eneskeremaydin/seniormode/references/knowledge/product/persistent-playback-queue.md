---
id: "persistent-playback-queue"
title: "Persistent playback queue and resume behavior"
category: "product"
summary: "Keep shuffle and playback progress coherent across pauses, crashes and playlist edits."
aliases: ["resume playlist","persistent shuffle","playback queue","resume music","track cursor","müzikte kaldığı yerden devam etme","karışık çalma sırasını saklama","cihaz kapanınca aynı sıra"]
decisions: [{"when":"Users expect the current sequence to survive app restart","use":"Persist queue item identities and progress together, and define how deleted items are skipped.","tradeoff":"Snapshot state adds storage and requires a versioned format."},{"when":"Sessions are disposable or deliberately restart the order","use":"Persist minimal state and explicitly signal that resume starts a new sequence.","tradeoff":"Restart is cheap but can feel like lost progress."}]
checks: ["Restart after repeated IDs and verify the next distinct entry is preserved.","Remove the current track during a pause and verify the published resume rule."]
sources: [{"title":"Android Media3 playlists","url":"https://developer.android.com/media/media3/exoplayer/playlists"},{"title":"NIST dictionary entry on Fisher–Yates","url":"https://www.nist.gov/dads/HTML/fisherYatesShuffle.html"}]
related: ["music-shuffle"]
---

<!-- Generated record title. -->
# Persistent playback queue and resume behavior

## Scenario

An audiobook app mixes clips for a practice session. A phone restart should resume the expected next clip, even if the source library changed.

## Failure modes

Re-shuffling on every resume can replay and skip clips. Array indices can point at a different item after deletion. Identical track IDs can represent separate queue entries.

## Explain it simply

Save the session's ordered queue and current position, so resuming continues the same session.

## Architecture notes

Use distinct queue-entry identities even where two entries refer to the same track. Persist ordered entries and the next entry under one queue revision. A replayable seed needs an algorithm version and stable inputs as well. Exercise resume with a removed source track and repeated queue entries, and check that the cursor advances once.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Users expect the current sequence to survive app restart** Persist queue item identities and progress together, and define how deleted items are skipped. Snapshot state adds storage and requires a versioned format.
- **Sessions are disposable or deliberately restart the order** Persist minimal state and explicitly signal that resume starts a new sequence. Restart is cheap but can feel like lost progress.

## Verification

- Restart after repeated IDs and verify the next distinct entry is preserved.
- Remove the current track during a pause and verify the published resume rule.

## Sources

- [Android Media3 playlists](https://developer.android.com/media/media3/exoplayer/playlists)
- [NIST dictionary entry on Fisher–Yates](https://www.nist.gov/dads/HTML/fisherYatesShuffle.html)

## Related decisions

- [Shuffle semantics and perceived variety](music-shuffle.md)

<!-- End generated record details. -->
