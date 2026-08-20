## Description: <br>
ME Featured Events discovers and subscribes to selected AI and Web3 events from ME News, with type and region filters plus optional recurring reminders. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ME News](https://me.news) <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Users browse upcoming AI and Web3 events, filter by region, initialize a local subscription, and receive daily or near-real-time reminders through messaging channels already configured in their agent platform. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Recurring reminders may send messages to an unintended channel or recipient. <br>
Mitigation: Show the filter, schedule, channel, and recipient and require explicit confirmation before creating automation. <br>
Risk: Failed or uncertain incremental delivery could cause duplicate or missed reminders. <br>
Mitigation: Keep the batch pending and advance the server cursor only after the delivery tool explicitly reports success. <br>

## Reference(s): <br>
- [ME News](https://me.news) <br>
- [Filter options API](https://api.me.news/skill/events/options) <br>
- [Upcoming events API](https://api.me.news/skill/events/upcoming) <br>
- [New events API](https://api.me.news/skill/events/changes) <br>

## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Guidance] <br>
**Output Format:** [Grouped event reminders with description excerpts, complete time ranges, locations, and source links] <br>
**Output Parameters:** [1D] <br>

## Skill Version(s): <br>
1.1.0 <br>

## Ethical Considerations: <br>
Users should verify event details at the source link and review automation recipients and schedules before enabling delivery. <br>
