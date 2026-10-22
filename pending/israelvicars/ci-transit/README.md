# ci-transit

A transit map for your CI runs.

![Animated Transit map of a GitHub Actions run: each job is a line, its steps are stations, and a DELAY and SERVICE ALERT appear on the failing Run unit tests step](https://raw.githubusercontent.com/israelvicars/transit/main/docs/ci.gif)

## Example prompts

- “Show my last failed GitHub Actions run as a transit map.”
- “Render run `1234567890` in `owner/repo` as an MP4.”
- “Make a GIF of the latest CI run on `main` for the PR description.”
- “Share my last failed run in Slack.”
- “Map `./run.json` and tell me which step failed and which ones were slow.”

## What it maps

Jobs become lines and steps become stations. Slow steps receive DELAY markers, while unsuccessful or cancelled work receives SERVICE ALERT markers.

Use a saved run JSON for a fully local workflow, or let the optional fetch command read through your local `gh` CLI.

## Install

```sh
npx skills add israelvicars/transit --skill ci-transit
```

## Privacy

Runs locally only, with no telemetry. Run data and renders stay on your machine.

[Back to the Transit README](https://github.com/israelvicars/transit#readme)
