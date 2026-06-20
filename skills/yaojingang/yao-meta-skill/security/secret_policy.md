# Secret Policy

Skills must not commit credentials, tokens, private keys, or customer secrets.

The v0 scanner blocks obvious high-risk patterns such as private key blocks, GitHub personal access tokens, Slack bot tokens, AWS access key ids, and OpenAI-style API keys.

Potential private paths or local-only references should be treated as warnings unless they expose credentials.
