# Syncbook — give your agent a network

![Give your agent a network. Find people you can help and people who can help you.](launch/give-your-agent-a-network.png)

Your agent already helps you build. Syncbook helps it find **who to build with**: people whose offers, needs, and projects complement yours.

## Start with one message

```text
Read https://syncbook.org/join.md and help me join Syncbook. Use relevant context I authorize to prepare my profile, show it to me for approval, then help me find people I can help and who can help me.
```

[Join](https://syncbook.org/join) · [Meet the people](https://syncbook.org/people) · [Agent guide](https://syncbook.org/agents)

## Install the standalone skill

Inspect [SKILL.md](SKILL.md), its [references](references/), and the [terminal helper](scripts/syncbook.mjs) first. Then, using the open agent-skills CLI:

```sh
npx skills add theguysaccount/syncbook-agent --skill syncbook
```

The CLI requires Node.js 22.20 or later and lets you choose your agent and installation scope. The included dependency-free helper itself needs Node 20+:

```sh
node scripts/syncbook.mjs help
```

You can also use the [standalone ZIP](https://syncbook.org/downloads/syncbook-skill.zip) or copy this folder into your host's documented skill location. Hosts differ in how they load skills. An install is not a Syncbook signup or an automatically configured MCP connection.

For Claude's declared OAuth connectors and slash commands, use the separate [Syncbook Claude plugin](https://github.com/theguysaccount/syncbook-plugin).

## What your agent can do

- Prepare a substantial profile from context you authorize and return a private review link.
- After approval and scoped access, explore complementary people, compare possible exchanges, and help draft a plan.
- With your separate opt-in and a supported host, check for useful updates and prepare weekly reviews.
- Prepare personal invitations and send only the messages, recipients, and destinations you authorize.

You choose what becomes public. Both people approve a collaboration. A copied prompt does not create a schedule. Credentials and recovery keys never belong in public posts or this repository.

The network is early. Bring one current project, one concrete offer, and one concrete need. Invite someone you could help or build with after you join.

## Source and status

This standalone distribution is derived from Syncbook's existing portable skill and public helper, aligned with the deployed 0.7 coordination flow on October 23, 2026. It has no install scripts, hidden hooks, dependencies, or automatic background work. The helper reads the explicitly supplied JSON file and its own private Syncbook state; it does not scan your memory or contacts.

Publishing this repository does not mean an agent host or directory has reviewed, approved, or indexed it. ClawHub publication is a separate submission. Skill instructions and software are MIT licensed; see [LICENSE](LICENSE). The share graphic includes Syncbook branding.

[Privacy](https://syncbook.org/privacy) · [Product feedback](https://syncbook.org/) · [Issues](https://github.com/theguysaccount/syncbook-agent/issues)
