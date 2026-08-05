## Description: <br>
AIMPACT provides AI morning briefings, evening summaries, 24-hour hot news rankings, and selected AI content sorted by AI scoring, with optional scheduled delivery. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jamesmenews](https://clawhub.ai/user/jamesmenews) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and developers use this skill to fetch AIMPACT/ME News AI reports, including morning briefings, evening summaries, 24-hour trend rankings, and selected AI news. It can also prepare reports for delivery through user-configured messaging channels. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Scheduled reports may be sent externally through configured message channels. <br>
Mitigation: Review the selected message channel, credentials, recipients, and schedule before enabling push delivery. <br>
Risk: Reports depend on the disclosed AIMPACT/ME News API endpoints being reachable and current. <br>
Mitigation: Check returned source links and error summaries before relying on a generated report. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/jamesmenews/menews) <br>
- [Publisher profile](https://clawhub.ai/user/jamesmenews) <br>
- [MetaEra AI flash API](https://agent.me.news/skill/flash/list?page=1&size=20&category=ai) <br>
- [AIMPACT AI articles API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=ai) <br>
- [AIMPACT OpenClaw articles API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=openclaw) <br>
- [AIMPACT events API](https://agent.me.news/skill/aimpact/events) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Guidance] <br>
**Output Format:** [Markdown news report with categorized items, source links, and a concise trend comment] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Reports are limited to the configured AIMPACT/ME News sources and may be delivered through user-configured message channels.] <br>

## Skill Version(s): <br>
1.0.11 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
