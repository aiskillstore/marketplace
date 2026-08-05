## Description: <br>
AIMPACT Crypto provides crypto morning and evening reports, 24-hour hot-news rankings, and curated crypto updates by fetching listed APIs, sorting content by AI score, and optionally sending reports through preconfigured message channels. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jamesmenews](https://clawhub.ai/user/jamesmenews) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and agents use this skill to generate on-demand or scheduled Chinese-language crypto news reports from the configured AIMPACT and MetaEra APIs. Operators can optionally send reports to already configured messaging channels after confirming manual report output. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Reports depend on the listed agent.me.news API sources and may reflect their source quality or availability. <br>
Mitigation: Install and use the skill only if the operator trusts those API sources, and test manual report generation before relying on scheduled reports. <br>
Risk: Optional message delivery can send reports outside the chat when message channels or scheduled tasks are configured. <br>
Mitigation: Do not configure message channels or cron/scheduled tasks unless outbound delivery is intended; confirm the destination channel before enabling scheduled delivery. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/jamesmenews/aimpact-crypto) <br>
- [MetaEra AI flash API](https://agent.me.news/skill/flash/list?page=1&size=20) <br>
- [AIMPACT Crypto news API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=crypto) <br>
- [sources.md](artifact/sources.md) <br>
- [format.md](artifact/format.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown-style Chinese crypto news report with source links and optional scheduling command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Reports are organized by crypto category, limited to the selected top items, and may be sent through preconfigured messaging channels.] <br>

## Skill Version(s): <br>
0.8.1 (source: SKILL.md frontmatter and server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
