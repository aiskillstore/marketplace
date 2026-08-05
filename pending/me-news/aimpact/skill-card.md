## Description: <br>
AIMPACT fetches AI news, morning and evening briefings, 24-hour hot-news rankings, and selected AI content from documented ME News API endpoints, then formats the results for agent users. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jamesmenews](https://clawhub.ai/user/jamesmenews) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and agent operators use this skill to retrieve concise AI news digests, 24-hour trend rankings, and category-organized reports. It can optionally send the generated report through a messaging channel that the host environment has already configured. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill fetches content from ME News API endpoints, so report quality and availability depend on those endpoints. <br>
Mitigation: Install and run it only if the ME News API endpoints listed in sources.md are trusted for the intended workflow. <br>
Risk: Optional scheduled push can send generated news reports outside the active agent session. <br>
Mitigation: Confirm the host environment's configured message channel and credentials before enabling scheduled push. <br>
Risk: The skill requires curl for primary API access and may fall back to web_fetch only when available. <br>
Mitigation: Verify curl is installed in the runtime environment and keep requests limited to the documented sources.md endpoints. <br>


## Reference(s): <br>
- [AIMPACT ClawHub page](https://clawhub.ai/jamesmenews/aimpact) <br>
- [MetaEra AI flash API](https://agent.me.news/skill/flash/list?page=1&size=20&category=ai) <br>
- [AIMPACT AI articles API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=ai) <br>
- [AIMPACT OpenClaw articles API](https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=openclaw) <br>
- [AIMPACT events API](https://agent.me.news/skill/aimpact/events) <br>
- [sources.md](artifact/sources.md) <br>
- [format.md](artifact/format.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown news digest with optional shell command examples for scheduling] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Reports are organized by AI-news category, sorted by available AI score, and limited to the current query window.] <br>

## Skill Version(s): <br>
0.8.1 (source: frontmatter and server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
