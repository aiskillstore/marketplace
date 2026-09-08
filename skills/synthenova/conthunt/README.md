# ContHunt agent skill

Teaches coding agents to research viral TikTok, Instagram Reels, and YouTube Shorts through the ContHunt CLI.

## Install

```sh
npx skills add Synthenova/conthunt-cli --skill conthunt -g
```

Skill path in this repository: [`skills/conthunt`](https://github.com/Synthenova/conthunt-cli/tree/main/skills/conthunt).

The agent installs the CLI if needed, runs device login, prefers `--json`, and keeps long jobs on `start` / `status` / `get` / `wait`.

## Human CLI install

```sh
curl -fsSL https://conthunt.app/install.sh | sh
conthunt login
```

## License

MIT. See [LICENSE](LICENSE). The ContHunt CLI binary is licensed separately in the repository root.
