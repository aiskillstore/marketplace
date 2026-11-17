# Production telemetry

## Production telemetry
When available (ask for access or exports): Crashlytics/Sentry/Xcode Organizer/Play Console vitals.
- Top crashes and ANRs by users affected, by version and OS; map each to code (symbolicated, see `references/autopsy.md`).
- Error spikes after a release: compare versions.
- Backend logs/APM for 4xx/5xx by endpoint and app version around the reported time.
Production issues become findings with real user impact numbers.
