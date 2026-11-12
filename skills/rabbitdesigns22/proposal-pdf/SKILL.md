---
name: proposal-pdf
description: >-
  Load when the agent has to make a sales proposal, quote or offer as a PDF for a small-business client (agency services, ads management, websites, design, any monthly plan), especially when it must "convince", "look elegant", "feel friendly" or carry both the agency's logo and the client's name or logo. It covers: checking every price and fact against its source before writing, a 5-page structure that sells without pressure, copy rules (no promised results, one clear next step, the client's own words), elegant layout when the client has no logo, building the PDF from HTML, and a page-by-page check before delivery. Triggers on "make a proposal", "PDF proposal", "quote for the client", "propuesta en PDF", "cotización", "que convenza y caiga bien".
license: MIT
---

# Proposal PDF

A proposal is read on a phone, in a WhatsApp chat, by a busy owner. They decide in about 30 seconds whether it is for them. It has to look like it came from an expensive agency and still read like a friend explaining a good deal. A wrong price or a promise you can't keep costs more than a plain design.

## 1. Lock the facts before writing a word

Write down, one line each, with the source of each fact:
- **Client:** business name exactly as they write it, what they sell, city, phone, address, links. Take these from their own page or chat. Never from memory.
- **What they asked for, in their own words.** The proposal answers that first.
- **Every number:** price, what is included, free extras, what they pay to third parties (ad spend). Take each from the price list or the person who sets prices. If a number is missing, ask once. Never invent a number, a discount or a deadline.
- **Logo:** do they have one in good resolution? If not, see section 4.

If one fact can't be confirmed, leave it out rather than guessing.

## 2. Structure: 5 pages (4 to 6 is fine)

1. **Cover:** "Proposal for <Business>", the client's name or logo large, the agency's logo small, the date. Nothing else.
2. **What you get:** 3 short points about their business, not about the agency. Example: "People searching for sportswear in your city find you first", not "We are experts in Google Ads".
3. **What's included:** the service, step by step (3 to 5 steps, one line each). Free extras go in their own box marked "Included at no cost", each with one line saying why it helps.
4. **Investment:** when the service includes running ads or any ongoing management, add a short, warm block on what happens if the service stops. For example: "a campaign is never left alone; that weekly care is part of the service, so if you pause the service we also pause the campaign, so your budget isn't spent with nobody watching it. Your account stays yours, and we can restart it whenever you want." Write it as care, never as a threat or fine print. Then the investment itself: one clear table with the monthly fee, what is free, and what they pay directly to third parties (for example the ad budget, with a suggested starting amount). Include payment terms only if they are confirmed.
5. **Next step:** the start steps in order. Always include the step where the client gives access to their own accounts (for example: "you open your ad account with your email and card, and invite us as admins; we send you the steps"). Skip the closing call-to-action block when the proposal is sent inside a chat that is already open with the client.

Only offer what the service really includes. A channel that needs extra setup (a maps listing, a verified profile) stays out unless it is part of the deal. Don't mention another account or project of the client unless it has already started.

## 3. Copy rules

- Use the register the client uses (formal or informal), and keep it the same on every page.
- No promised results: no "more sales", "guaranteed", "first place on Google", "X clicks". Describe what you will do, not what the platform will deliver.
- Short sentences, plain words, no jargon (say "your ad shows up when someone searches..." instead of "search intent"). At most about 60 words per page outside the table.
- Free extras are framed as part of the deal ("it comes with..."), never as a desperate discount.
- At most one call to action, at the end (none when the proposal goes inside a chat already open with the client; see page 5). No "let me know if you have questions".
- Run a de-AI pass (no "elevate", "unlock", "seamless", em-dash chains, groups of three for the sake of it).

## 4. Design

- **Two logos, clear hierarchy:** the client is the hero (cover, header). The agency logo is small and consistent (cover corner and footer).
- **Client with no logo:** set their name as an elegant wordmark: one refined typeface (a high-contrast serif or a clean geometric sans), generous letter spacing, one color. Do not draw a fake logo, and do not use a logo you plan to make for them later.
- **Palette:** take it from the client's world (their page, products, photos). One neutral background (cream, off-white or deep charcoal), one text color, one accent. The agency's colors appear only in its logo and maybe in the final button.
- **Type:** at most 2 families. Big titles, 11-12 pt body, line height of about 1.4.
- **Space:** wide margins (about 18-22 mm), one idea per block, plenty of air. Prices go in a clean table or cards with the total impossible to miss.
- **Images:** only the client's real photos, or free commercial stock (Pexels, Unsplash, Pixabay) without visible brands or recognizable people presented as the client's customers. Record every source. With no good images, use typography and color; that looks better than a weak photo.
- **Format:** Letter or A4 portrait, so it opens well on a phone and prints well. Keep it under about 3 MB.

## 5. Build it

- Write it as one HTML file with print CSS (`@page { size: Letter; margin: 0 }`, one `<section>` per page with a fixed page height, `page-break-after: always`). Embed the fonts or load them from Google Fonts, and use local image files.
- Render to PDF with a headless browser (Playwright/Chromium `page.pdf({ printBackground: true })`) or the environment's PDF skill. Also export one PNG per page.

## 6. Check before delivering (every time)

1. Look at every page PNG at full size: nothing cut, overlapping or orphaned, no empty page, logos sharp.
2. Extract the PDF text (pdftotext or similar) and compare it with the fact list from section 1: every price, phone, name and address matches character for character.
3. Search the text for banned promises and for typos and accents in the client's language.
4. Make sure the PDF opens, its size is reasonable and the file name is clean (`Proposal <Business>.pdf`).
5. Report: the path, the PNGs of the pages, and the fact list with ✓ next to each fact. Say anything you could not check.

Never send it to the client yourself unless you were explicitly told to. Hand it to the person who owns the relationship.
