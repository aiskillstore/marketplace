# Backend, edge and data checks

Inventory per endpoint: host, path, method, auth, body shape, fields the app decodes, cached or not. Group by host (each can sit behind a different CDN zone).

## Read-only checks
```bash
curl -4 -sS -i --max-time 20 [-X METHOD] URL [-H "Content-Type: application/json" -d '{...}'] | grep -iE "^HTTP|cf-mitigated|content-type|server|cache|age"
```
- Status and content type are what the app expects (JSON, not an HTML challenge or error page).
- `cf-mitigated: challenge` / "Just a moment..." = Cloudflare managed challenge; apps cannot solve it. Exempt the API paths.
- Cache headers: per-user API responses must not be cached publicly.
- Run from the regions that matter (US for Apple review, every market). Confirm with `curl -s https://ipinfo.io/country`.
- Shape: fields the app needs that are null/missing; hard-coded ids/names vs server lists.
- Public auth routes with a stale bearer token (headless CMS: Authenticated vs Public role permissions).

## Ground-truth oracle (every list/filter/search bug)
Send the exact parameters the app sends for the reporter's state, and the variants of the impact map, and print only what the screen shows:
```python
# oracle.py - run with: python3 -I oracle.py
import json, urllib.request
URL = "https://example.com/api/events/search"    # the app's endpoint
CASES = {                                         # one entry per impact map row
    "reported (as the app sends it)": {"venue_ids": [], "category_ids": [7]},
    "intended":                       {"venue_ids": [0], "category_ids": [7]},
    "linked venue only":              {"venue_ids": [312]},
}
for name, body in CASES.items():
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    items = d.get("items", d)
    print(name, "count", d.get("count", len(items)), [i.get("title") for i in items[:6]])
```
The screen must equal the oracle for each row. If the reported screen equals a different row (e.g. "no venue filter"), you have found what the app really sends.

## Combination sweep (feeds and multi-filter screens)
When a screen queries with several user preferences at once (venue x category, category x region), request every combination a user can hold and count results. List the combinations that return nothing: each is a user population that sees an empty or error screen. Save the table to the work folder.

## Catalog sweep (data integrity)
For every option list the app shows (brands, venues, categories, tags):
- Every option has a real, unique id (no 0, -1, null, duplicates).
- Every option returns at least one item when used alone; list those that return none.
- Every content item is linked to at least one option where it should be (count orphans).
- Detail pages and option URLs answer 200 (no 404/redirect loops).
- Names match what the app hard-codes or normalises (case, accents, zero-width characters).
Report bad data as a backend finding with the owner, the exact items and the fix (e.g. "publish the 3 venue pages and link their events"). Paginate through the full list once, save it to the work folder, and answer later questions from that file instead of new requests.

## Authenticated writes
Only with a test account and the user's explicit OK. Never print tokens. Pattern: log in (token in a variable) -> read -> write a known value exactly like the app -> read and compare -> restore. Prefer handing the user a script that reads the password with `read -s` and prints only statuses and field values.

## Server-side causes to rule out
CDN/WAF geo rules, bot protection, rate limits too low for carrier NAT; role permissions per action; email delivery (SMTP sender verification); mixed hosts (auth, content, media, likes); server timezone; payload limits; CMS content not linked or not published.
