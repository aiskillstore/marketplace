# Troubleshooting

Work down this list in order. It moves from cheapest check to most expensive, so you never burn a payment on a problem that a `curl` would have found.

## Order of diagnosis

1. `GET /api/health` — is the service up at all?
2. `GET /nodes.json` — is the exit you chose `disabled: false` and `healthy`?
3. `POST /api/token/validate` — is the token live?
4. Direct request without the proxy — is the target reachable at all?
5. Only then: retry through the proxy, and only then consider buying again.

## Symptom table

| Symptom                                        | Likely cause                                                        | Fix                                                          |
| ---------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------ |
| `Could not resolve proxy`                      | typo in hostname, or exit host does not exist                        | re-read `hostname` from `/nodes.json`                        |
| `Connection refused` on 3128                   | that exit does not offer the HTTP variant                            | use 1080, or one of `us-central1`/`eu-central1`/`asia-central2` |
| `CONNECT tunnel failed, response 407`          | no credentials sent — expected on the 3128 variant                   | pass the token as both username and password                 |
| `HTTP/1.1 407 Proxy Authentication Required`   | client reached the proxy but sent no/blank credentials               | check the token is not empty or truncated                    |
| SOCKS5 auth rejected / connection closed early | token wrong, expired, or already rotated                             | `validate`, then `status`, then `recover`                    |
| `401 invalid_token` on status                  | token unknown or expired                                             | check plan expiry; recover if the payment settled            |
| `400 invalid_request` on status                | sent `Authorization` instead of `{"token": ...}` body                | use the JSON body                                            |
| 402 again after `PAYMENT-SIGNATURE`            | amount, asset, `payTo`, or network changed since the quote           | re-read the fresh challenge; never reuse a cached one        |
| 402 with `maxTimeoutSeconds` elapsed           | authorization signed too long ago (default 300s)                     | sign and submit immediately                                  |
| `404 package_not_found`                        | package id not in the public catalog                                 | use an id from `/catalog.json`                               |
| `502` on access                                | payment settled, provisioning failed                                 | **do not repay**; use `recover` with the tx hash             |
| `403 ownership_not_proven` on recover          | signed with a different wallet than the one that paid                | re-sign with the paying wallet                               |
| `400 stale_recovery`                           | `issued_at` older than 10 minutes                                    | regenerate the message with a fresh timestamp                |
| Target sees the wrong country                  | connected to the wrong exit                                          | pick the exit whose `label` matches the region you need      |
| Target logs your local DNS resolver            | used `socks5://` instead of `socks5h://`                             | switch scheme so DNS resolves at the exit                    |
| Works in curl, fails in browser                | browser cannot do SOCKS5 auth                                        | use the HTTP CONNECT variant on 3128                         |
| Throughput collapses mid-job                   | fair-use data cap reached                                            | check usage via `status`; buy a larger plan                  |
| Second agent fails while first works           | single packages allow 1 active session                               | consolidate, or move to `multi_agent`                        |

## Retry policy

- **Provisioning `502`** — never retry the purchase. Money already moved. Recover instead.
- **`recovery_unavailable` (502)** — safe to retry later, with backoff.
- **Network timeouts through the proxy** — one retry against a *different* exit before concluding the target is down.
- **402** — never retry blindly. Parse the new challenge and re-sign.

## When to stop and ask the user

- Any error that suggests money was taken but access was not granted.
- Any request to buy a second package for the same job.
- Anything where the user's target site is explicitly banning automated access — a proxy changes your IP, not the legality or the terms of service you agreed to.

## Support

Telegram: `https://t.me/x402socks`. Include the `x-request-id` header from the failing response, plus the settlement tx hash if payment is involved. Never paste a live token.
