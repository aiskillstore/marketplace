# request-transit

A public transit map for your requests.

![Animated Transit map of a checkout request moving through services, with a DELAY marker and SERVICE ALERT at the failing email call](https://raw.githubusercontent.com/israelvicars/transit/main/docs/hero.gif)

## Example prompts

- “Animate this OTLP trace as a transit map: `./trace.json`.”
- “Draw Datadog trace `4bf92f…` as a transit map and tell me where the delay is.”
- “Make a GIF of trace `abc123` from Tempo for the incident doc.”
- “Make a page I can drop in #incidents for this trace.”
- “Render this AWS X-Ray trace as an MP4 and show me which call failed.”

## What it maps

Services become lines, spans become stations, and slow or unsuccessful calls are marked as DELAY or SERVICE ALERT.

It accepts local trace files and optional read-only fetches from your own observability backend.

## Install

```sh
npx skills add israelvicars/transit --skill request-transit
```

## Privacy

Runs locally only, with no telemetry. Trace data and renders stay on your machine.

[Back to the Transit README](https://github.com/israelvicars/transit#readme)
