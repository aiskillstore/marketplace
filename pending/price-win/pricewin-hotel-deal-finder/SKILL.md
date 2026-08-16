---
name: pricewin-hotel-deal-finder
description: "Find the cheapest hotel deal by comparing live prices across Booking.com, Agoda, Google Hotels, and OpenTravel for any city worldwide and any travel dates — one command returns ranked best-value, cheapest, and quality picks with direct booking links, all normalized to USD. Use whenever someone asks for hotel prices, hotel deals, the cheapest room or rate, best hotel rates, a hotel price comparison, or which OTA is cheaper — e.g. 'is Booking or Agoda cheaper for Tokyo', 'find me a hotel in Bangkok under $100', 'compare hotel prices for 12–15 Aug', 'cheapest hotel near Shinjuku'."
version: 1.1.3
author: PriceWin
platforms: [linux, macos, windows]
tags: [hotel-price-comparison, compare-hotel-prices, cheapest-hotel, cheapest-hotels, hotel-deals, booking-vs-agoda, best-hotel-rates, best-rates, hotel-search, hotel-booking, price-comparison, booking-com, agoda, google-hotels, opentravel, ota, hotel, hotels, travel, travel-deals, trip-planning, accommodation, deals]
metadata:
  openclaw:
    requires:
      bins: [node, npx]
    envVars:
      - name: OPENTRAVEL_API_BASE_URL
        required: false
        description: Override the OpenTravel API host (default https://api.opentravel.one).
    emoji: "🏨"
    homepage: https://github.com/Price-Win/pricewin-skills-hub
---

# PriceWin Hotel Deal Finder

> **Compare live hotel prices across Booking.com, Agoda, Google Hotels & OpenTravel in one command** — and get back ranked best-value, cheapest, and quality picks with direct booking links.

Stop opening five OTA tabs to find the real cheapest rate. Ask your agent *"find me a hotel in Tokyo for 12–15 Aug, 2 guests"* and this skill returns a clean, ranked comparison in ~30–60 seconds (cached cities).

**Invoke this skill for questions like:**
- "What's the cheapest hotel in `<city>` for `<dates>`?"
- "Is Booking.com or Agoda cheaper for this hotel?"
- "Compare hotel prices for `<city>`, `<N>` guests."
- "Find me a hotel under $`<X>`/night in `<city>`."
- "Best-value place to stay near `<landmark>` on `<dates>`?"

Each returns the same one-command answer below — no clarifying round-trip needed.

**What you get from one command:**
- 🥇 Best value · 🥈 Cheapest · 🥉 Quality — picked side-by-side
- Real per-night prices from up to **4 sources**, normalized to **USD**
- **Clickable booking links** straight to the cheapest OTA for each hotel
- Works for **any city worldwide** — including bot-hardened ones (Shanghai, Hangzhou, Bangkok…) via a stealth Patchright daemon
- No API keys, no MCP server — `node`/`npx` is all you need

**Sample result:**

```
🏨 Tokyo • Aug 12–15 • 3 nights • 2 guests
━━━━━━━━━━━━━━━━━━━━
🥇 BEST VALUE
Shinjuku Granbell Hotel
  ✅ agoda      💰 $118/night
     booking    💰 $131/night
     → Save $13 vs Booking
🥈 CHEAPEST
APA Hotel Shinjuku
  ✅ google     💰 $94/night
📊 18 hotels | agoda, booking, google, opentravel • prices in USD
```

**Install:**
```bash
npx skills add https://github.com/Price-Win/pricewin-skills-hub --skill pricewin-hotel-deal-finder
```

---

## How to use this skill

**One command does the whole job — you normally won't need to ask clarifying questions first. Infer the parameters (below) and run it:**

```bash
cd {baseDir} && node bin/search.js "<city>" <checkInYYYY-MM-DD> <checkOutYYYY-MM-DD> <adults> en-us
```

`{baseDir}` is this skill's install directory (auto-resolved by the runtime). If your runtime does not substitute it, `cd` into the folder that contains this `SKILL.md` (the one with `bin/search.js`). Avoid hardcoding a `~/.hermes/...` or `~/.openclaw/...` path — it differs per platform.

Example:
```bash
cd {baseDir} && node bin/search.js "Hangzhou" 2026-06-10 2026-06-13 2 en-us
```

The script handles everything automatically: daemon launch, Agoda cache lookup, Google + Booking inline search, OpenTravel API lookup (all cities), discovery for new cities, and formatted tier-card output. Run it and send the output to the user.

**Infer the parameters instead of asking** (ask only if the city or dates are genuinely ambiguous):
- **Year:** use the current year from today's date unless the user states otherwise. If the requested day/month has already passed this year, assume next year. (Get today's date with `date +%Y-%m-%d` if unsure.)
- **"10-13/6"** → `<year>-06-10 <year>-06-13` — fill `<year>` from the rule above
- **"2 guests" / "2 people"** → `2` adults
- **Locale:** language/region code passed to the OTAs (controls site language + region). Default `en-us`. Prices are in USD (Google Hotels is requested with `gl=us&curr=USD`); other sources follow the locale you pass.

One `search.js` run is the whole workflow — no Python, curl, or ad-hoc scraping is needed on top of it.

---

## Operating rules — how to get reliable results

**RULE 0 — Drive the browser only through `search.js` (via your terminal/shell tool). The native browser tools don't work here.** This skill relies on a stealth Patchright daemon. The runtime's native tools — `browser_navigate` / `browser_open`, `browser_click`, `browser_type` / `browser_fill`, `browser_snapshot`, `browser_close`, any other `browser_*`, and subagent delegation (`delegate_task` / `spawn_agent`) — will fail on this task, so don't reach for them:

- Those native tools spawn a vanilla Chromium with no stealth, so Booking.com and Agoda detect the bot within seconds; the requests hang until the runtime kills them ("Command timed out after 30/60 seconds"). That burns 5+ minutes and returns nothing. The Patchright daemon that `search.js` launches survives bot-detection.
- Delegated subagents start with empty history and no skill context, so they fall back to Python/curl scraping that gets bot-blocked immediately. Run the skill in the current agent.

The one path that works:
```
cd {baseDir} && node bin/search.js ...
```

**RULE 1 — Let `search.js` do the scraping; don't scrape an OTA yourself.** Avoid calling `browse.js` directly, doing `goto`/`click`/`type` in the browser, building Agoda/Booking/Google URLs by hand, calling the OpenTravel API separately, or launching the daemon yourself. `search.js` already drives the stealth daemon through a careful flow that survives bot-detection — it handles Agoda discovery internally for EVERY city (including Chinese cities like Shanghai, Hangzhou, etc.). Manually navigating an OTA is the #1 cause of failure: it trips Agoda/Booking anti-bot ("detect automation", "redirect to homepage", "problem completing your search") and gets the IP blocked. Run `search.js` once and send its output. If a source looks "missing", see RULE 4 rather than fetching it by hand.

**RULE 2 — First-time city discovery takes 2–4 minutes.** If `search.js` output contains `"discovering"` or `"launching"` messages, tell the user: "First time searching this city — discovering selectors, this takes about 2–4 minutes..." and wait for the result rather than retrying or aborting.

**RULE 3 — Send the output exactly.** `search.js` outputs formatted tier cards ready to send. Copy the output directly into your response. Do not reformat, summarize, or abbreviate it.

**RULE 3a — Preserve the markdown hyperlinks.** Every hotel name in the output is already wrapped as `[Hotel Name](https://booking-url...)` — a clickable hyperlink. Keep it intact: don't split the URL onto a separate `🔗 https://...` line, don't replace `[Hotel Name](url)` with plain text, keep OTA names lowercase ("google", not "Google"), and keep section titles as-is ("📋 More good deals"). The output is Telegram-MarkdownV2-ready; sending it verbatim gives the user clickable hotel names with hidden URLs (clean UI).

**RULE 3b — Hyperlink hotel names in your own commentary too.** If you add a suggestion or commentary section after the output, wrap every hotel name you mention as `[Hotel Name](url)` using the same URL the script printed for that hotel, rather than plain text.

**RULE 4 — Partial results are normal — send them as-is rather than fixing by hand.** A source can be absent from a run (e.g. Agoda blocked this run, or OpenTravel has no inventory for the city). That's fine — send the tier cards with whatever sources are present; the footer (`📊 N hotels | <sources> • prices in USD`) lists exactly what was found. Fetching the missing source via the browser or a direct URL tends to trip anti-bot and make things worse, so avoid it. If `search.js` errors out entirely, tell the user what failed in one line and show any partial output it printed above the error. For more coverage, the one reliable retry is running the same `search.js` command again (anti-bot is often transient).

---

## Output Format Reference

`search.js` prints tier cards in this format — you send this directly to the user:

The hotel name is a Markdown link to its cheapest OTA. Price rows carry NO
links and the OTA key is shown lowercase (`agoda`/`booking`/`google`/`opentravel`).
There are no star ratings or area lines — the script does not have that data.

```
🏨 <city> • <d1>–<d2> • <N> nights • <adults> guests
━━━━━━━━━━━━━━━━━━━━

🥇 BEST VALUE
[<Hotel Name>](<cheapest_link>)
  ✅ agoda      💰 <price>/night
     booking    💰 <price>/night
     opentravel 💰 <price>/night
     → Save <diff> vs Booking

🥈 CHEAPEST
[<Hotel Name>](<cheapest_link>)
  ✅ google     💰 <price>/night
     agoda      💰 <price>/night

🥉 QUALITY
[<Hotel Name>](<cheapest_link>)
  ✅ booking    💰 <price>/night
     agoda      💰 <price>/night

📋 More good deals
  — Agoda —
  • [<Hotel>](<agoda_link>) — agoda: <price> | booking: <price>
  — Booking —
  • [<Hotel>](<booking_link>) — booking: <price>
  — Google —
  • [<Hotel>](<google_link>) — google: <price>
  — OpenTravel —
  • [<Hotel>](<opentravel_link>) — opentravel: <price>

💡 Tip: <best Hotel Name>
   [Book on <OTA>](<link>) — <price>/night

📊 <N> hotels | <sources with data> • prices in USD
```

All prices are shown in USD. Agoda, Google and OpenTravel geo-lock to VND by IP and are converted via a live FX rate; Booking returns USD natively. Only sources that actually returned data are listed in the footer.

---

## Limitations

- First search per city pays the Agoda discovery cost (2–4 minutes). Google and Booking are inline (no discovery); OpenTravel is a direct API call.
- Subsequent searches reuse the Agoda cache and complete in ~30–60 seconds.

## Security & data handling

Runs locally, needs no API keys, and collects no personal data — the only data
sent out is the search query (city, dates, guests). Scraped hotel text is treated
as untrusted: `sanitizeText()` in `bin/search.js` strips control/zero-width/bidi
and markdown-control characters before any of it reaches model output, and booking
links are restricted to `http(s)`.

The local browser daemon is **loopback-only, token-authenticated** (a per-run
token in a `0600` state file), rejects non-loopback `Host` headers against DNS
rebinding, and keeps the **Chromium sandbox enabled** — `--no-sandbox` is used
only where it cannot work (root on Linux, or explicit `PRICEWIN_NO_SANDBOX=1`).

Full disclosure of commands run, downloads, and network egress is in
[`SECURITY.md`](./SECURITY.md).
