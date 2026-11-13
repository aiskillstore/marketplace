# Landing page checks, in detail

Load this while running steps 1 and 3. Platform facts carry a source in
[sources.md](sources.md), as of 2026-11-05. Everything else is judgement and
is written as such.

## Getting the page

Use the best tool the host has, in this order:

1. **A real browser** (the host's browser or screenshot tool, or Playwright
   if the project has it). Capture:
   - phone: 390x844 viewport, the first screen and a full-page capture;
   - desktop: 1440x900, the first screen.
   Click the main button once to see where it goes. Don't submit forms with
   real data; stop at the form.
2. **The repo source**, when the page lives here. Read the route, the
   components it renders, and any A/B, locale or feature-flag branches. The
   source shows copy a fetch may miss, but not what a visitor sees after
   CSS and scripts; say which you used.
3. **A plain fetch** (`curl -sL <url>` or the host's web fetch). Good for the
   copy, meta tags and links. If `<body>` is mostly an empty root element and
   scripts, the page renders client-side: don't report "no headline" or "no
   proof" from that fetch. Mark the first-screen and mobile checks "could not
   check" unless you have a browser or the source.

Never log in, bypass a bot check or submit a real form to audit a page.

## The promise check

- Put the traffic's words and the page's first words side by side in the
  output. The visitor should not have to translate between them.
- Paid search: the query and the ad. The page should answer the query's
  intent (comparing, pricing, "how to") rather than give a general pitch.
  Google Ads rates "landing page experience" as how relevant and useful the
  page is to people who click the ad; it feeds Quality Score, which Google
  calls a diagnostic, not an auction input.
- Paid social or a post: the hook in the creative. If the ad promised a
  specific thing (a free template, a price, a calculator), it should be on
  the first screen, not one click deeper.
- Organic search: the query that brings most visits to this page, from Google
  Search Console if the user can share it. Without it, mark the check
  "could not check" rather than guessing the query.
- Email or outbound: the line in the email that earned the click.

## First screen

- Headline: what it is or what it does for whom, in the buyer's words.
  "The platform for modern teams" fails; a competitor could use it unchanged.
- Subhead or supporting line: who it's for, or how it works, in one sentence.
- One primary action, visibly heavier than anything else. Navigation, a
  second "Book a demo" and a chat bubble all compete with it.
- On a phone, the headline and the primary button both show before the first
  scroll. A large hero image or video that pushes the button below the fold
  is a common finding.

## Proof

- Strong: named customers the visitor would recognise, quotes with a name,
  role and company (and a photo where the site has one), numbers with a time
  frame and a source, a real product screenshot or short demo, a public
  review score with the count.
- Weak: anonymous quotes, unattributed "trusted by thousands", stock photos
  of people, logos with no link to any story.
- Placement: next to the claim or button it supports, not collected in a
  block above the footer.
- Never write new proof. If a claim on the page looks unsupported, list it
  and ask the user for the source; an unsupported claim is a trust and
  sometimes a legal risk.

## Call to action

- The label says what happens next and, where true, what it costs ("Start
  free, no card").
- The button works: it goes to the promised next step, which loads, and the
  next step doesn't ask for more than the label implied.
- After each major section a visitor can act without scrolling back up.
- Price: if the visitor came from a price-sensitive promise and the price is
  hidden behind a call, that's a finding. For high-touch sales it may be
  deliberate; ask.

## Friction

List every obstacle between "I want this" and "done":

- form fields (count them; for each, is it needed now?), required phone
  numbers, card up front, forced account creation before any value;
- popups or cookie walls that cover the first screen on arrival;
- surprises: a price that differs from the ad, a waitlist where the ad said
  "start now";
- errors: dead links, a broken form, a console error that stops the button.

## Mobile

- Body text readable without zoom; no sideways scrolling.
- Tap targets at least 24x24 CSS px (WCAG 2.2 success criterion 2.5.8,
  level AA) and not crowded together.
- Sticky headers, chat widgets or cookie banners not covering the button.
- Form inputs use the right type (`type="email"`, `type="tel"`) so the
  phone shows the right keyboard, and autofill works.

## Speed

- Field data beats a lab score. PageSpeed Insights (https://pagespeed.web.dev)
  shows real-user Core Web Vitals when Chrome has enough data for the URL or
  origin. Google's "good" thresholds at the 75th percentile: LCP 2.5 s or
  less, INP 200 ms or less, CLS 0.1 or less.
- The API is
  `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url>&strategy=mobile`.
  Without a `key=` parameter it shares a public quota that is often used up;
  if it returns a quota error, use the web page or ask the user for a free
  API key. Don't report a speed finding you didn't measure.
- A lab score alone (no field data) is a hint, not a verdict. Say which it is.

## Tracking

- Click IDs: Google adds `gclid` with auto-tagging and says it must reach the
  final landing page for conversion tracking; Meta adds `fbclid`; Microsoft
  Advertising adds `msclkid`. Test with a fake value and follow redirects:

  ```sh
  curl -sIL -o /dev/null -w '%{url_effective}\n' "https://example.com/lp?gclid=TEST&fbclid=TEST&msclkid=TEST"
  ```

  If the final URL lost them, a redirect is dropping them. Some sites also
  return an error page for unknown query parameters; that is a finding too.
- Conversion event: whether the thank-you step fires the event can only be
  confirmed in a browser's network panel or the ad platform's diagnostics.
  Without access, put it under "could not check".

## Reading the user's numbers

- Conversion rate = conversions / visits for the same page, window and
  device. Compare phone and desktop separately when you can; a big gap points
  at the mobile checks.
- With a few hundred visits or a few dozen conversions in the window, a
  change of a couple of points is within normal week-to-week noise. Say so
  and rank by what the page shows rather than by the numbers.
- Published conversion "benchmarks" mix industries, traffic sources and
  definitions. Don't grade the page against one.
