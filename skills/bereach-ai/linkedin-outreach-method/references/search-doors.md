# Search doors

Who is already in the account comes first; a search only fills a persona short of people. For that
persona the plan is the base; a card's other fields pick a second door.

## Existing contacts first (free)

1. The count, before the question round: `bereach_contacts` with `engaged: false`, `outreachStatus: "none"`,
   `lifecycleStage: "contact"`, `doNotContact: false`, `limit: 1`, and its `total`. Keep `engaged: false`: without it the call returns only people already touched, and
   nothing fails.
2. The split, after the answers, never a download of every row. The filters that exist: the four above,
   `hasProfileData: true`, `campaignId` (one list), `tag`, `sortBy` (`profileUpdatedAt_desc` first),
   `limit` up to 100, then the `nextPage` it answers with; there is no title, headline or place filter. A list whose people fit
   one persona is paged alone with its `campaignId`; otherwise pages of 100, each from the last page's `nextPage`. Each row goes to a card by its
   `headline`, `currentRole`, `company` and place against Found by and the place answered. Stop as soon as
   every persona has a few hundred (enough for the first weeks; close enough moves on), at most 10 pages (1,000 rows);
   the rest waits for a later batch, and the page counts only the rows read. A size or place the row does
   not show is not looked up: the row stays in. No profile data: the same count call with `hasProfileData:
   false`, its `total` is the amber `pas de profil : N`, never read one by one.
3. Before the invitations: the same call with `engaged: true` returns people touched in a way their status
   does not show yet: take their ids out, and anyone in `bereach_invitations` with `direction: "sent"`.
4. Per list: the list ids from each row's `campaigns`, then `bereach_contacts` with `campaignId`,
   `outreachStatus: "none"`, `limit: 1`, and read `total`.
5. On the Plan and personas yes (no search: as the page is shown): one `bereach_contact_update` per persona, up to 500 `contactIds`,
   `tags: { add: ["persona:<short-name>"] }`. A row already tagged is skipped, so a split resumes.

A persona short of people: the doors below.

## The doors

| Card field or ask | Door | Credits | Saves to the list |
|---|---|---|---|
| Found by (titles, seniority) inside the ICP: always first for a persona short of people | `bereach_plan_searches`, then `bereach_run_searches` | plan free; run about 11 per 25 people, capped at the plan's estimate | yes |
| Why now or Signal is a company event (a raise, a new executive) | `bereach_find_signals`: events first, read them, then resolve the chosen companies with the card's role | events 4 to 11; resolve about 11 to 20 per company, nothing when nobody comes back | yes, at resolve |
| Why now or Signal is a post on a topic | `bereach_find_posts` with `since`, `authorTitle`, `authorLocation`; then `bereach_collect_engagers` on the two or three best posts | posts 19 to 49 with a place (9 to 49 without), plus about 1 per 2 authors; engagers 1 per page of up to 100 | authors yes unless `save: "skip"`; engagers always |
| Proof that lands names past clients | `bereach_find_people` with `likeCompanies` (companies like them, never them) | 4 / 11 / 49 for up to 10 / 25 / 100, plus 1 per 2 profiles read | yes |
| Recently funded | `bereach_find_companies` with `filters.fundedWithinMonths`, then `bereach_find_people` with those companies and `perCompany` | companies 4 / 11 / 49 | companies no, people yes |
| Named accounts | `bereach_find_employees`, or `bereach_find_people` with the company and a role | 4 for a quick read, up to about 50 | yes |
| The list is built, a dated reason per person | `bereach_add_signals` (not a search) | it answers with its ceiling: information, run for the whole list without a yes | writes each person's reason on the row |

- Each door's people are one row on Plan and personas: persona, why them in plain words ("levée
  récente", "ont réagi à un post sur ..."), found, credits. Never a tool name.
- A signal lead is tagged `signal:<name>` and invited first; its event or post is its line.
- Hiring and job ads are a weak signal: say so before running one. Events are reasons, never a count.
