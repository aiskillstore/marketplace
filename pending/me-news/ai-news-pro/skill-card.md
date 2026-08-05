## Description: <br>
AI News Pro generates AI morning and evening briefings, 24-hour hot news rankings, and curated AI news reports sorted by AI score. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jamesmenews](https://clawhub.ai/user/jamesmenews) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and developers use this skill to fetch structured AI news reports from configured ME News API endpoints. The skill can return the report directly or send it through an already configured messaging channel. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill fetches news from agent.me.news API endpoints. <br>
Mitigation: Confirm the user trusts those endpoints before installation and keep collection limited to the URLs listed in sources.md. <br>
Risk: Optional message delivery can send generated reports to configured channels. <br>
Mitigation: Enable the message tool only for intended channels and verify credentials outside the skill before automated delivery. <br>
Risk: AI-scored news summaries may omit context or prioritize items imperfectly. <br>
Mitigation: Review important reports and follow source links before making decisions based on the briefing. <br>


## Reference(s): <br>
- [AI News Pro ClawHub page](https://clawhub.ai/jamesmenews/ai-news-pro) <br>
- [Output format template](artifact/format.md) <br>
- [AI news source configuration](artifact/sources.md) <br>
- [MetaEra AI flash API](https://agent.me.news/skill/flash/list?page=1&size=20&category=ai) <br>
- [AI news API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=ai) <br>
- [OpenClaw news API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=openclaw) <br>
- [AI industry events API](https://agent.me.news/skill/aimpact/events) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance] <br>
**Output Format:** [Markdown news report with source links and optional cron or task scheduler command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Reports are grouped by AI category, usually capped at 10 to 12 items, and optional push delivery depends on a preconfigured message tool.] <br>

## Skill Version(s): <br>
0.9.1 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
