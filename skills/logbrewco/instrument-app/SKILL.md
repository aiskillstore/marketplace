---
name: instrument-app
description: Add error tracking, structured logs, and tracing to an app, then prove it works by reading a test event back. Use when someone asks to add error tracking, logging, monitoring, observability, or tracing, to set up LogBrew or install its SDK, or to check that events arrive. Detects the framework with logbrew setup --json, installs the matching SDK, sets service, environment, and release, sends one test event, and reads it back. Includes logging rules that help with any tool.
license: MIT
---

# Instrument an app

An accepted send is not proof. The task is done only when you read the test
event back from LogBrew with the right service, environment, and release.

## Rules

- Never print, paste, or commit a key. Never ask a person to paste a key
  into the chat. Keys go in files with owner-only permissions or in the
  app's secret configuration.
- Never use account access as SDK configuration. SDKs use a project ingest
  key. Browser and mobile code use a key of kind `browser`, never a server
  key or a read key.
- Keep 1 sender for each signal. If the app already sends errors or logs
  with another tool, ask the person before you add a second sender or
  remove the first.
- Follow [references/logging-rules.md](references/logging-rules.md) for
  every log and event that you add.

## Steps

### 1. Read the app

Find the runtime, framework, package manager, and entry point. Find the
existing logger and error handler. Find where the deployment sets its
version and environment.

### 2. Detect the framework

Run this from the project root. It changes no files.

```bash
logbrew setup --json
```

Read `detected` (manifest, runtime, package manager). When `install_plan`
is not `null`, use `install_plan.install_command`, check each item in
`install_plan.compatibility`, and read `install_plan.surfaces` for the key
kind that each surface needs. When `install_plan` is `null`, select the
package from [references/frameworks.md](references/frameworks.md).

If the CLI is not installed, install it with
`brew install LogBrewCo/tap/logbrew` or `npm install -g logbrew-cli@latest`,
or select the package from the manifest by hand.

### 3. Get a project and a key

```bash
logbrew status --json
```

If it reports no authentication, ask a person to run `logbrew login` once,
then continue. Then create a project, or a key for an existing project. The
CLI writes the key to a new owner-only file and never prints it.

```bash
install -d -m 700 "$HOME/.logbrew"
logbrew projects create "$APP_NAME" --runtime "$RUNTIME" --environment development --ingest-key-file "$HOME/.logbrew/$APP_NAME.ingest" --json
logbrew projects keys create "$PROJECT_ID" --kind server --label "$APP_NAME server" --ingest-key-file "$HOME/.logbrew/$APP_NAME.ingest" --json
```

Run only one of the 2 commands: `projects create` for a new project, or
`projects keys create` for an existing one. Read `project.id` from the
result. The destination file must not exist. If the result is unclear, run
the same command again; the CLI reuses its pending request.

### 4. Install the SDK and add the setup code

1. Run the install command from step 2.
2. Add the setup code from [references/frameworks.md](references/frameworks.md)
   for the framework. Create the client once, in the app's startup code.
3. Load the key from the environment, for example
   `LOGBREW_SERVER_API_KEY`. Do not write it in source files.
4. Set the service name, the environment, and the release. The framework
   reference shows where each SDK reads them, for example from
   `LOGBREW_SERVICE_NAME`, `LOGBREW_ENVIRONMENT`, and `LOGBREW_RELEASE`. Take
   the release from the deployment, such as `checkout-api@1.4.0` or a commit
   SHA. Do not use `latest`, a branch name, or an empty value.
5. Connect the existing logger to the SDK when the package supports it, so
   current logs flow without code changes at each call.

### 5. Send 1 test event

Send the event through the real code path. Request a route that the app
already has, or log 1 `info` message with a unique marker, such as
`setup check 2026-10-26T10:00:00Z`. Keep it at `info`; do not make a fake
error to find it more easily. To test error capture too, trigger 1 handled
test error.

The SDK or the app reports a `2xx` status. This shows only that LogBrew
accepted the request. Continue.

### 6. Read the event back

```bash
logbrew read logs --project "$PROJECT_ID" --search "$MARKER" --since 1h --json
logbrew read issues --project "$PROJECT_ID" --since 1h --json
```

With a project read key instead of account access, set `LOGBREW_TOKEN` to
the key and leave out `--project`. With the MCP server, use `logs.list.v1`
with `project_id`, `search`, and `since`.

Check that the event has the expected service, environment, and release.
If the list is empty:

1. Wait 10 seconds and read again, 3 times at most.
2. Compare the project, environment, release, and time range with the
   event that you sent.
3. Make sure that the app flushes or shuts down the SDK client before the
   process exits.
4. Read the SDK delivery error. `unauthenticated` means the ingest key is
   wrong; a new CLI login does not fix it.

Do not report success until the read-back shows the event.

### 7. Report

Tell the person:

- the packages installed and the files changed;
- the environment variables to set in each deployment
  (`LOGBREW_SERVER_API_KEY`, `LOGBREW_SERVICE_NAME`,
  `LOGBREW_ENVIRONMENT`, `LOGBREW_RELEASE`, or the names that the SDK uses);
- the read-back result: the command, the event time, service, environment,
  and release;
- what is not set up yet, such as source maps, browser capture, or
  deployment records.
