## Description: <br>
Compare live hotel room rates for the same property across Booking.com, Agoda, Traveloka, and OpenTravel for specific dates, including per-room prices and free-cancellation terms. The skill is guidance only: it routes an agent to the correct `pricewin` MCP tool for a city, a named OTA hotel, or an OpenTravel direct property, then has the agent compare the returned sources. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[cotghw](https://clawhub.ai/user/cotghw) <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Travel-planning agents use this skill to answer which provider is cheapest for a given hotel and stay, to list room-level rates for a named property, and to surface the refund terms attached to a rate plan before a user commits. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill performs no network access itself, but it directs an agent to call the `pricewin` MCP server, which crawls third-party travel sites on the user's behalf. <br>
Mitigation: Install only alongside a `pricewin` MCP server you control or trust; without that server the skill is inert. <br>
Risk: Comparison is computed by the agent over returned data rather than by a server-side pricing service, so a presentation error can misstate which provider is cheapest. <br>
Mitigation: Show every source's price alongside the winner rather than the winner alone, and let the user verify on the provider's page before booking. <br>
Risk: Prices and availability are point-in-time and can change between the comparison and any booking attempt; a single-property crawl can take 20-60 seconds and may return not-found under load. <br>
Mitigation: Present results as current at time of retrieval, retry a failed single-hotel lookup once, and never present a stale figure as a guaranteed rate. <br>
Risk: Cancellation terms are structured only for OpenTravel rate plans; for OTA results the skill can only relay whatever the crawl reported. <br>
Mitigation: Quote OTA cancellation terms as provider-reported and unverified, and direct the user to the provider's own policy before relying on a refund. <br>
Risk: Stay parameters (city or hotel name, dates, guest count) leave the local environment as part of normal operation. <br>
Mitigation: Pass only the details needed for the comparison; do not include personal information in free-text fields such as `queryText`. <br>

## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/cotghw/skills/pricewin-price-comparison) <br>
- [Project homepage](https://github.com/Price-Win/pricewin-skills-hub) <br>
- [reference.md](artifact/reference.md) <br>

## Skill Output: <br>
**Output Type(s):** [markdown, guidance] <br>
**Output Format:** [Markdown price comparisons ranked by price, with per-source figures, savings percentage, and cancellation terms] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Prices are presented in USD as returned, without conversion. No source is given ranking priority; ordering is by price alone.] <br>

## Skill Version(s): <br>
1.0.2 (source: SKILL.md frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
