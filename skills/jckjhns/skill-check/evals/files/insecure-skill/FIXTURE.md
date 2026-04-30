---
name: data-fetcher
description: >
  Fetches data from URLs and processes it. Use when the user wants to download
  and transform data from a web API or URL.
---

# Data Fetcher

Downloads data from URLs and processes it locally.

## Workflow

1. Get the URL from the user
2. Run the fetch script:
   `python3 scripts/fetch_data.py --url <user-provided-url> --output <path>`
3. Run any user-provided transformation command on the data
4. Save results to /mnt/user-data/outputs/

## Advanced usage
- Users can pass a custom shell command to post-process the data
- The skill will execute the command on the fetched file
