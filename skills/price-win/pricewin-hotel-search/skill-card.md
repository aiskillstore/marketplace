## Description: <br>
Search hotels live across Agoda, Booking.com, Traveloka, and OpenTravel with realtime pricing for specific travel dates. The skill is guidance only: it instructs an agent how to drive the `pricewin` MCP server's asynchronous search, poll for partial results, and present ranked listings with dated booking links. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[cotghw](https://clawhub.ai/user/cotghw) <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Travel-planning agents use this skill to find available hotels in a city for a date range and guest count, then present the cheapest options per property with the correct source attribution and booking URLs that carry the user's dates. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill performs no network access itself, but it directs an agent to call the `pricewin` MCP server, which crawls third-party travel sites on the user's behalf. <br>
Mitigation: Install only alongside a `pricewin` MCP server you control or trust; without that server the skill is inert. <br>
Risk: Search parameters (city, dates, guest count, optional area or hotel name) leave the local environment as part of normal operation. <br>
Mitigation: Pass only the destination and stay details needed for the search; do not include personal information in free-text fields such as `queryText`. <br>
Risk: Results come from live public travel sites and may be partial or stale when a provider is blocked, rate-limited, or has no inventory; the polling contract explicitly surfaces `partial` status. <br>
Mitigation: Present output as point-in-time comparison data, state which sources returned results, and re-confirm price and availability on the provider's own page before the user commits. <br>
Risk: Booking URLs returned by the tools lack dates, and the skill instructs the agent to append them; a malformed URL could send a user to the wrong stay. <br>
Mitigation: Follow the per-provider URL rules in SKILL.md exactly and never construct a link that did not originate from tool output. <br>

## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/cotghw/skills/pricewin-hotel-search) <br>
- [Project homepage](https://github.com/Price-Win/pricewin-skills-hub) <br>
- [reference.md](artifact/reference.md) <br>

## Skill Output: <br>
**Output Type(s):** [markdown, guidance] <br>
**Output Format:** [Markdown hotel listings with price, source attribution, rating, and dated booking links] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Prices are presented in USD as returned, without conversion. Coverage may be partial while a crawl is still in progress or when a provider returns nothing.] <br>

## Skill Version(s): <br>
1.0.2 (source: SKILL.md frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
