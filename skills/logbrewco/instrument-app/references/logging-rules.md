# Logging rules

These rules apply to any logging or error tracking tool. They make events
easy to search, group, and compare between releases, and they keep private
data out.

## Write structured events

- Write the message as a fixed operation and its result:
  `payment capture failed`, `report generated`. Put changing values in
  fields, not in the message. A fixed message groups well and is easy to
  search.
- Use the same field names everywhere: `order_id`, `route`, `status_code`,
  `duration_ms`. Do not use `orderId` in one place and `order` in another.
- Log IDs, not objects. Do not log a whole request, response, user record,
  or database row.
- Use 4 severity levels and keep their meaning fixed:
  - `info`: a normal event that you want to count or find.
  - `warning`: an unusual state that the code handled.
  - `error`: an operation failed and a user or job saw the failure.
  - `critical`: the service cannot do its main work.

## Keep secrets and personal data out

- Never log passwords, tokens, API keys, session cookies, authorization
  headers, card numbers, or private keys.
- Do not log email addresses, names, phone numbers, addresses, or IP
  addresses unless the team decided to collect them and has a reason.
  Use an opaque user ID instead.
- Do not log query strings or request bodies; they often contain the
  values above. Log the route template, such as `/orders/{id}`, not the
  concrete path.
- Exception messages can contain user input. Keep that in mind before you
  turn on message capture.

## Send 1 event for each failure

- Capture an error once, at the place that handles it. Do not log it and
  also re-throw it to a handler that captures it again.
- Do not log the same failure in a loop. Log the first one and a count.
- A retry that succeeds is a `warning` at most. Report the final failure as
  the `error`.
- Keep 1 sender for each signal. Two SDKs that capture the same exception
  create duplicate issues.

## Tag every event with its release

- Set the service, the environment, and the release once, in the client
  setup, so that every event carries them.
- The release names 1 build: `checkout-api@1.4.0`, `web@b7f4d91`, or a
  commit SHA. Do not use `latest`, `prod`, a branch name, or an empty value.
- Use fixed environment names: `production`, `staging`, `preview`, `local`.
- Set the release from the deployment pipeline, not by hand. Then a
  comparison between 2 releases shows what the new code changed.

## Make traces connect

- Start or continue 1 trace for each incoming request. Pass the W3C
  `traceparent` header to the services that you call.
- Logs and errors inside a request must carry its trace ID. Then 1 failing
  request shows its logs, spans, and error together.
- Name spans with the route template and the operation, such as
  `GET /orders/{id}` or `db.query orders`.

## Flush before exit

Short-lived processes (scripts, jobs, serverless functions, CLIs) must
flush or shut down the client before they exit. Otherwise the last events
are lost.
