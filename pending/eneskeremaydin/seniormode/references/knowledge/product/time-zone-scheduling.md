---
id: "time-zone-scheduling"
title: "Scheduling across time zones and DST"
category: "product"
summary: "Decide whether a schedule follows a local clock or a fixed elapsed interval and define ambiguous times."
aliases: ["daylight saving","recurring schedule","time zone","DST overlap","local wall time","saat dilimine göre tekrarlanan görev","yaz saati geçişi","yerel saatle zamanlama"]
decisions: [{"when":"The event recurs at a local wall time","use":"Store local schedule, IANA zone and explicit gap or overlap rules, then compute each occurrence.","tradeoff":"Timezone rule updates can change future occurrences."},{"when":"The task runs at a fixed elapsed time or known instant","use":"Store and compare an instant and render it in the viewer's preferred zone.","tradeoff":"The displayed wall time may shift when timezone rules change."}]
checks: ["Test spring gaps, fall overlaps and a zone with a non-hour offset.","Verify job retries cannot create two effects for one logical occurrence."]
sources: [{"title":"RFC 5545 calendar recurrence","url":"https://www.rfc-editor.org/rfc/rfc5545"},{"title":"IANA Time Zone Database","url":"https://www.iana.org/time-zones"}]
---

<!-- Generated record title. -->
# Scheduling across time zones and DST

## Scenario

A volunteer reminder repeats every Sunday at 09:00 in Berlin, while one-off reminders are delivered at a known instant worldwide.

## Failure modes

UTC alone loses intended wall-clock recurrence. Nonexistent and repeated local times can cause missed or duplicate reminders.

## Explain it simply

Save a recurring meeting's local time and named zone so it stays at the intended hour when clocks change.

## Implementation guidance

Store a recurring local time with its named zone and explicit gap and overlap policy. Persist a triggered occurrence with a fixed instant and stable identity. A weekly 09:00 appointment stays at 09:00 through DST even when its UTC time shifts. Test nonexistent spring time, repeated autumn time, and reruns of the same occurrence.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The event recurs at a local wall time** Store local schedule, IANA zone and explicit gap or overlap rules, then compute each occurrence. Timezone rule updates can change future occurrences.
- **The task runs at a fixed elapsed time or known instant** Store and compare an instant and render it in the viewer's preferred zone. The displayed wall time may shift when timezone rules change.

## Verification

- Test spring gaps, fall overlaps and a zone with a non-hour offset.
- Verify job retries cannot create two effects for one logical occurrence.

## Sources

- [RFC 5545 calendar recurrence](https://www.rfc-editor.org/rfc/rfc5545)
- [IANA Time Zone Database](https://www.iana.org/time-zones)

<!-- End generated record details. -->
