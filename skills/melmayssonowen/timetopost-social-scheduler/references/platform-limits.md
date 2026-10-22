# Common platform limits and timing fallback

Treat these as starting points, not guarantees. Check `get_capabilities` and current platform requirements before scheduling.

| Platform | Common text limit | Common media note |
| --- | ---: | --- |
| X | 280 characters per post | Threads may contain up to 24 segments. |
| Instagram | 2200 characters | Hosted media required. |
| TikTok | 2200 characters | Hosted media and creator choices required. |
| Threads | 500 characters | Use a native-length version. |
| LinkedIn | 3000 characters | Prefer a concise professional version. |
| Bluesky | 300 characters | Confirm live capability. |
| Mastodon | 500 characters | Server configuration may differ. |
| Pinterest | 500 characters | One image and board ID; title up to 100 characters. |

Call `get_optimal_times` first. When it returns no historical recommendation, label suggestions as generic heuristics, for example weekday lunch or early evening in the audience's time zone. Ask which time zone to use. These are broad starting points, not account-specific data.
