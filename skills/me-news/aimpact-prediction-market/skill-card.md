## Description: <br>
Monitors prediction-market API feeds and produces alerts for trending events, large trades, probability moves, and potential trading opportunities. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jamesmenews](https://clawhub.ai/user/jamesmenews) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and agents use this skill to monitor prediction-market feeds and generate formatted alerts for market-moving events, large trades, probability changes, and potential opportunities. It can also support scheduled checks and optional push notifications when the user's OpenClaw message channels are already configured. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Prediction-market alerts can be mistaken for financial advice. <br>
Mitigation: Treat generated alerts as informational and review them before making any trading decision. <br>
Risk: The skill depends on agent.me.news market data feeds. <br>
Mitigation: Confirm that the data source is trusted before installation and validate important alerts against primary market sources. <br>
Risk: Scheduled checks or push notifications may post more often or to more channels than intended. <br>
Mitigation: Review configured message channels and polling frequency before enabling scheduled monitoring. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/jamesmenews/aimpact-prediction-market) <br>
- [MetaEra Prediction API](https://agent.me.news/skill/flash/list?page=1&size=20&category=prediction) <br>
- [ME News Poly Events API](https://agent.me.news/skill/poly/events?page=1&size=20&active_only=true) <br>
- [Polymarket](https://polymarket.com) <br>
- [sources.md](artifact/sources.md) <br>
- [format.md](artifact/format.md) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance] <br>
**Output Format:** [Markdown alert text with optional shell command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Outputs are informational alerts and may be pushed only through already configured OpenClaw message channels.] <br>

## Skill Version(s): <br>
1.0.1 (source: server release metadata and SKILL.md frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
