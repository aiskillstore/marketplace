# Browser Bridge

Use this reference when implementing an `aac run` login bridge for an agent-controlled browser.

## Security Model

`aac run --env-all` injects credentials into the child process environment. The values are not exported into the parent shell, but the child process can read them. If the child sends those values to browser automation, agent-controlled code handles them in memory. That is not transcript exposure, but it is not strictly agent-blind.

Safer options, in order:

1. Human types or approves the login manually.
2. A credential-blind helper types into the focused browser and never returns values to the agent.
3. A temporary local bridge passes credentials in memory to active browser automation, with no logging and immediate cleanup.

Use option 3 only when the user understands the in-memory trust boundary.

## Active Bridge Shape

Keep all browser work inside one active browser-control execution:

```js
// Pseudocode only. Do not paste real domains or credentials into source.
const email = tab.playwright.getByPlaceholder("Email address", { exact: true });
const password = tab.playwright.getByPlaceholder("Password", { exact: true });
const submit = tab.playwright.getByRole("button", { name: "Login", exact: true });

if (await email.count() !== 1 || await password.count() !== 1 || await submit.count() !== 1) {
  throw new Error("Unexpected login form shape");
}

// Start a one-use 127.0.0.1 server on a random port.
// Spawn:
//   aac run --domain example-app.test --env-all -- node -e '<helper>'
// The helper posts { u: AAC_USERNAME, p: AAC_PASSWORD } to the local server.
// The active browser-control execution fills and submits, then closes the server.
```

Never print the POST body, the environment, request headers, or the credential-bearing command internals.

## Helper Rules

- Bind the temporary server to `127.0.0.1`, not all interfaces.
- Use a random port.
- Accept one request, then close the server.
- Use `stdio: ["ignore", "pipe", "pipe"]` and sanitize logs before returning errors.
- Redact email-like strings, rendezvous-code-shaped strings, and ids in any error summary.
- Kill the child process and close the server on timeout.
- Return only status fields such as `submitted`, `aac-run-failed`, or `timed-out`.

## Approval Prompt

Before launching `aac run`, tell the user:

```text
Approve only if Agent Access shows domain: example-app.test.
```

Do not ask the user to paste the approval screen, token, password, or full CLI output.

## Verification

After submit, verify success from non-secret page state:

- URL changed away from the login page.
- Page title changed.
- A logout link or account greeting is visible.
- The expected next workflow step is visible.

If verification fails, inspect visible validation errors and CLI exit status only. Do not dump logs that may include credentials.
