# AI Quiz Creator

Create personalized friendship quizzes with an AI assistant and share them through **[Block You Test Me](https://blockyoutestme.fun/)**.

The assistant collects your real preferences, prepares the answer key, and can create a hosted 10-question quiz. Your friends guess your choices and receive a score out of 10. You keep a separate private Friend Score Page to review results.

## Links

- **Website:** https://blockyoutestme.fun/
- **Documentation:** https://blockyoutestme.fun/how-to-play/
- **Publisher/about:** https://blockyoutestme.fun/about/
- **Contact:** patrickwu1992@gmail.com
- **Updates:** https://blockyoutestme.fun/updates/
- **Source repository:** https://github.com/ligoudancodeer/ai-quiz-creator
- **Maintainer:** https://github.com/ligoudancodeer
- [Agent instructions](SKILL.md)
- [Example conversations](examples/conversations.md)

## Features

- AI-guided collection of ten personal choices.
- Locally validated answer keys; no network request in draft mode.
- Optional hosted quiz creation without an account or API key.
- Public friend invitation and separate private scoreboard.
- Website-generated sharing cards and scores from 0 to 10.
- 25 website display languages, including English, Vietnamese, Hindi, Bengali, Turkish and Arabic.

The website currently uses **10 preset friendship questions**. This package does not promise custom-topic quizzes, educational exams or personality assessments. The AI workflow is supplied by your assistant; the website itself is a browser quiz game.

## Install

Using the Skills CLI:

```text
npx skills add ligoudancodeer/ai-quiz-creator
```

For an assistant supporting Agent Skills, place this folder in its documented skills directory. For Codex, the conventional user directory is `~/.codex/skills/ai-quiz-creator/`; other assistants have their own installation paths. Restart or reload skills as required by your assistant.

This package is plain Markdown, JSON and an optional dependency-free Node.js helper. The browser workflow can be used without the helper. Script mode requires Node.js 18+ and HTTPS access to the website.

## Try it

Ask your assistant:

> Help me make a friendship quiz on Block You Test Me. Ask for my real choices, then give me a link I can share with friends.

Or preview the included fictional sample locally:

```text
node scripts/create-quiz.mjs --input examples/draft.json
```

For your own real choices, replace the sample nickname and answer indices, then create a hosted quiz only when you intend to transmit them:

```text
node scripts/create-quiz.mjs --input /absolute/path/to/your-quiz.json --publish
```

Each answer is a zero-based index from 0 to 3, corresponding to the order in [questions.json](references/questions.json). `lang` defaults to `en`.

After publishing, save the private management URL securely. Do not commit the output or paste it into a public issue. Only the public `quizUrl` belongs in an invitation. The helper does not write either URL to disk.

## Privacy and limits

Draft mode stays on your device. Publish mode sends the nickname and ten selected answer indices to Block You Test Me for hosting. Refer to the [website privacy policy](https://blockyoutestme.fun/privacy) for storage, visibility and deletion details. The skill needs no passwords, social-media access or private contact lists. Sending invitations is a separate user action.

If access is blocked, use the [website manually](https://blockyoutestme.fun/) rather than repeatedly creating quizzes. Successful publication is verified by the API response; link availability still depends on website access.

## Development

```text
node tests/test-helper.mjs
```

Tests run offline against a mock transport. No test requests create production quizzes. The question snapshot was checked against the site source on October 13, 2026; live API access from the author's environment was blocked by an edge 403, so successful live script publication is not claimed.

## License

[MIT](LICENSE) applies to this skill package. It does not grant rights to the website's music, unrelated site assets or third-party trademarks. Website use remains subject to its [terms](https://blockyoutestme.fun/terms).
