# Target types

Six kinds of third-party page tend to answer "which tool should I use?"
questions. For each: what it's good for, how entry usually works, what to
check, and what to avoid. Rules vary per target; always read the target's own
page before drafting.

## "Best X" roundups and listicles

Editorial articles: "best <category> tools in <year>", "<competitor>
alternatives", "top <category> for <segment>".

- **Why they matter:** they answer the exact buyer question in a ranked,
  quotable form, so they turn up for "best" questions often.
- **Entry:** a short pitch to the author or editor. Many are written by a
  vendor ranking its own product first; those rarely add a rival. Check who
  publishes it before pitching.
- **Check:** date and whether it's updated yearly; an author or contact
  route; whether listings are sponsored (a disclosure line, "featured" labels).
- **Avoid:** paying for a placement whose link passes ranking credit (Google
  treats paid links without `rel="sponsored"` or `nofollow` as link spam);
  pitching the same text to every author.

## Directories and marketplaces

Category directories (SaaS, AI tools, dev tools, local services), app and
plugin marketplaces, integration marketplaces, package registries, MCP and
agent-skill directories.

- **Why they matter:** structured pages with category, pricing and
  description; engines and buyers use them to build shortlists.
- **Entry:** a submit form, often with a review queue; some charge for faster
  review or featured placement; some crawl automatically from GitHub, a
  registry or a package manifest.
- **Check:** whether competitors are there; whether the category fits; review
  time; whether it requires an account, a badge on your site or a backlink in
  return; whether the listing page is indexed (search `site:<directory>
  <competitor>`).
- **Avoid:** directories that exist to sell links (thousands of unrelated
  entries, no traffic, badge-swap requirements), and bulk-submission services.

## Review sites

G2, Capterra, TrustRadius, app-store reviews, Google Business Profile,
Trustpilot, category-specific review sites.

- **Why they matter:** engines quote them for "is X good" and comparison
  questions, and a profile with no reviews says little.
- **Entry:** claim or create the vendor profile (often free), then ask real
  customers for honest reviews.
- **Check:** eligibility (some exclude consumer products or betas), whether the
  profile already exists unclaimed, and the site's own review-solicitation
  rules.
- **Avoid:** in the US, the FTC rule on reviews bans fake reviews and
  incentives conditioned on a positive (or negative) review, and requires
  reviews by officers, managers, employees and agents to clearly disclose the
  connection. Asking all customers for honest reviews is fine; FTC staff warn
  that asking only the happy ones can still mislead.

## GitHub awesome lists and curated repos

`awesome-<topic>` lists and curated catalogs for developer tools, AI agents,
skills, MCP servers and self-hosted software.

- **Why they matter:** developer-facing questions often surface these lists,
  and they're how many developers shortlist tools.
- **Entry:** a pull request (sometimes an issue form) adding one line in the
  list's format.
- **Check:** `CONTRIBUTING.md`, the PR template and recent merged PRs. Common
  gates: minimum stars or project age, open source only, "no SaaS" or "no
  paid-only tools", alphabetical order, description length, one entry per PR,
  no AI-generated PRs, reviewing other PRs first. Check whether the maintainer
  still merges (last merged PR date).
- **Avoid:** PRs that ignore the format, add a whole section for yourself, or
  rewrite other entries.

## Community threads

Reddit, Hacker News, Stack Exchange, Indie Hackers, Discord or Slack
communities with public archives, product forums.

- **Why they matter:** "what do people use for X?" threads get cited for
  recommendation questions and read by buyers deciding.
- **Entry:** a reply in an existing, relevant, still-open thread, from the
  user's own long-standing account, disclosing the connection.
- **Check:** the community's own rules on self-promotion (many ban it outright
  or allow it only in set threads); thread age (archived threads can't take
  replies); whether the question is one the product actually answers.
- **Avoid:** new or second accounts, posing as a customer, coordinated
  replies, asking anyone to upvote. Reddit's rules call for authentic
  participation and ban content manipulation and misleading impersonation;
  Hacker News asks users not to solicit votes or comments; US FTC guidance
  says employees and owners endorsing their own product must disclose the
  relationship.

## Comparison pages

Third-party "<A> vs <B>" pages and comparison tables on review sites,
directories and competitor sites.

- **Why they matter:** they answer the head-to-head questions buyers ask late
  in the decision.
- **Entry:** for neutral third-party comparisons, a request to add the
  business, or to correct its facts if it's already there (a
  `revnu-fix-ai-claims` job). Competitor-owned comparison pages won't add you;
  note what they say and leave them.
- **Your own comparison pages** are content work, not a listing. Out of scope
  here; note the gap for the user.

## Profiles that support everything above

A consistent set of official profiles (LinkedIn company page, Crunchbase,
GitHub org, Product Hunt, package registry pages) with the same name,
description and canonical URL. They're rarely the page an engine cites for a
"best" question, but listings, reviewers and engines use them to confirm who
the business is. Fix inconsistencies before submitting elsewhere.
