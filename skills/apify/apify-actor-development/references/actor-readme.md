# Actor README guidelines

The README is the Actor's landing page on Apify Store. It serves as SEO content, first impression, usage guide, and support resource. **Always generate a README.md when creating or deploying an Actor.**

## Required structure

Write in Markdown. Use H2 (`##`) for main sections (these form the table of contents) and H3 (`###`) for subsections. Do not use H1 — the Actor name is automatically used as H1.

### 1. What does [Actor name] do?

- 1-2 sentences explaining what the Actor does and doesn't do
- Include a link to the target website
- Mention keywords like "API" (e.g., "Instagram API alternative")
- Bold the most important terms

### 2. Why use [Actor name]? / Why scrape [target site]?

- Business use cases and benefits
- List main features and capabilities
- Highlight the Apify platform advantages: scheduling, API access, integrations, proxy rotation, and monitoring

### 3. What data can [Actor name] extract?

- Table showing main data fields the Actor outputs (field name, type, description)
- Don't list every field — focus on the most useful and understandable ones

### 4. How to scrape [target site]

- Numbered step-by-step tutorial (Google may pick these up as rich snippets)
- Include a link to blog tutorials if they exist

### 5. How much will it cost to scrape [target site]?

- Set pricing expectations based on the Actor's pricing model
- For pay-per-result: mention free tier limits and what larger plans offer
- For compute units: explain average data volume per dollar
- Cost-related questions rank well in Google search

### 6. Input

- Reference the input tab: "See the input tab for full configuration options"
- Explain any complex input fields or special formatting requirements
- Screenshot of the input schema is optional but helpful

### 7. Output

- Include: "You can download the dataset in various formats such as JSON, HTML, CSV, or Excel"
- Show a simplified JSON output example (2-3 items)
- If output is complex, show separate examples for different data types

### 8. Tips / Advanced options (if applicable)

- How to limit compute unit usage
- How to get more accurate results or improve speed

### 9. FAQ, Disclaimers, and Support

- Legal/scraping disclaimer (use this template and customize with the target site name):
  > Our Actors are ethical and do not extract any private user data, such as email addresses, gender, or location. They only extract what the user has chosen to share publicly. We therefore believe that our Actors, when used for ethical purposes by Apify users, are safe. However, you should be aware that your results could contain personal data. Personal data is protected by the GDPR in the European Union and by other regulations around the world. You should not scrape personal data unless you have a legitimate reason to do so. If you're unsure whether your reason is legitimate, consult your lawyers.
- Common troubleshooting tips
- Mention the Issues tab for feedback
- Link to API tab for programmatic access
- Use cases for the extracted data

## SEO best practices

- Include keywords naturally in H2/H3 headings (e.g., "How to scrape Instagram" not just "How to use")
- Target "People Also Ask" style questions as H3 headings
- Aim for at least 300 words total
- Embed a YouTube video URL if available (renders automatically as a player)
- Make images clickable with links

## Tone

- Match the README tone to the target audience skill level
- For no-code users: use plain language, avoid code blocks early on
- For developers: include technical details, code examples, and API references
- Be clear about what technical knowledge is needed to use the Actor

## Reference Actors

Before writing a README, review these top Actors on Apify Store for best practices on structure, tone, and content:

- [Instagram Scraper](https://apify.com/apify/instagram-scraper)
- [Google Maps Scraper](https://apify.com/compass/crawler-google-places)

## Key rules

- Always write the README as part of Actor development — do not skip this step
- The first 25% of the README is what most visitors read — put the most important info there
- Use emojis sparingly as bullet points to break up text
- Keep images compressed but good quality
- Use [Carbon](https://github.com/carbon-app/carbon) for code snippet screenshots if needed
