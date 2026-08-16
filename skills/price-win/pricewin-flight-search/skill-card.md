## Description: <br>
Search live flight fares for a route and date across Agoda, Trip.com, and Traveloka — one-way or round-trip, in any cabin class. The skill is guidance only: it instructs an agent how to drive the `pricewin` MCP server's asynchronous flight search, poll for progressive results, and present ranked fares with airline, times, stops, duration, and the provider's own booking link. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[cotghw](https://clawhub.ai/user/cotghw) <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Travel-planning agents use this skill to find flights between two airports for a departure date and optional return date, then present the cheapest options per leg with correct currency, passenger-count semantics, and booking links that were returned by the tools. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill performs no network access itself, but it directs an agent to call the `pricewin` MCP server, which crawls third-party travel sites on the user's behalf. <br>
Mitigation: Install only alongside a `pricewin` MCP server you control or trust; without that server the skill is inert. <br>
Risk: The bundled `install.sh` edits agent configuration files (Claude Code, Cursor, Windsurf, Gemini CLI, VS Code, Codex) to register the hosted MCP endpoint, and it runs with the permissions of whoever invokes it. <br>
Mitigation: It is optional and never runs on its own — `skills add` only copies files. Preview it with `bash install.sh --dry-run`, point it elsewhere with `--url` or `PRICEWIN_MCP_URL`, and note that it writes a `.bak` before modifying any file, refuses to rewrite configs it cannot parse, and adds no credentials because the endpoint is anonymous. <br>
Risk: Search parameters (airport codes, dates, passenger count, cabin) leave the local environment as part of normal operation. <br>
Mitigation: Pass only the route and trip details needed for the search; do not include personal information in free-text fields such as `queryText`. <br>
Risk: Fares come from live public travel sites and may be partial or stale while a crawl is still running, when a provider is blocked or rate-limited, or when a cached result is replayed; the polling contract surfaces `searching` and `cached` for exactly this reason. <br>
Mitigation: Present output as point-in-time comparison data and re-confirm the fare on the provider's page before the user commits. <br>
Risk: `price` is the total for all passengers, which is easy to misreport as a per-person figure, and airport codes resolved from a city name may be the wrong airport. <br>
Mitigation: Follow the currency and passenger-total rules in SKILL.md exactly, and ask the user which airport is meant whenever a city has more than one. <br>
Risk: Fares are converted to USD from the service's VND display currency; if the live FX rate is unavailable the value stays in VND, so a consumer that assumes USD would misreport the amount. <br>
Mitigation: Read the returned `currency` field and label the figure with it instead of assuming a currency. <br>
Risk: Booking links are provider deep links, and a malformed or invented link could send a user to the wrong flight. <br>
Mitigation: Use `bookingUrl` verbatim, never append or construct parameters, and treat the `https://www.price.win/` fallback as "no deep link available" rather than a bookable link. <br>

## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/cotghw/skills/pricewin-flight-search) <br>
- [Project homepage](https://github.com/Price-Win/pricewin-skills-hub) <br>
- [reference.md](artifact/reference.md) <br>

## Skill Output: <br>
**Output Type(s):** [markdown, guidance] <br>
**Output Format:** [Markdown flight listings with airline, flight number, times, duration, stops, party-total fare, and provider booking links] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Fares are presented in USD as returned and represent the total for all passengers. Coverage may be partial while a crawl is still in progress or when a provider returns nothing. Outbound and return legs are independent one-way searches.] <br>

## Skill Version(s): <br>
1.1.0 (source: SKILL.md frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
