# RELEASE.md Template

This is the canonical template for `releases/{release-slug}/RELEASE.md` — the master release-management document. It travels with a release through every lifecycle stage: announcement, release week, sustain. Step 5 of the recoup-roster-add-artist chain scaffolds it per album returned by Spotify; the remaining fields fill in over time as distribution, marketing, and PR work happens.

**Don't delete unfilled sections.** Leave them as `⚠️ TBD` so a later turn knows what's still missing. Mark a section `N/A` only when it genuinely doesn't apply (e.g. "no physical production planned"). Tick `✅` once a field is confirmed.

## Sharing tags

Each section heading carries one tag indicating its sharing status:

- **`[INTERNAL]`** — scrub before any external sharing (campaign budgets, KPI targets, team contacts, internal flags).
- **`[SHAREABLE]`** — safe for DSPs, press, partners (project snapshot, narrative, audience stats, tour info).
- **`[OPS]`** — operations reference (release identifiers, distribution metadata).

## Status markers

- **`✅`** — confirmed.
- **`❌`** — required but missing — action needed.
- **`⚠️ TBD`** — to be determined; placeholder for unknown.
- **`N/A`** — does not apply to this release.

## Slug convention

Slug = `lowercase-kebab-case` of the project title plus a format suffix:

- **Album** → `releases/{title-slug}/` (no suffix — album is the default).
- **EP** → `releases/{title-slug}-ep/`.
- **Single** → `releases/{title-slug}-single/`.
- **Compilation** → `releases/{title-slug}-compilation/`.

Examples: `releases/after-hours/`, `releases/adhd-ep/`, `releases/blinding-lights-single/`.

## What Step 5 of create-artist fills in

**Filled from the Spotify album response (`GET /api/spotify/album?id=$ALBUM_ID`):**

- Section 1: Artist Name, Project Title, Release Date (Digital), Format (`album_type` + `total_tracks`).
- Section 2.1: Spotify URI (album-level `external_urls.spotify`).
- Section 2.2: per-track Title (from `tracks.items[].name`), Duration (formatted `mm:ss` from `duration_ms`), Explicit (from `tracks.items[].explicit`).
- Section 2.3: cross-reference local `songs/` to mark which `.mp3` files exist as `✅ Present` vs `❌ Missing`.
- Section 18: Cover Art URL (from `images[0].url`, typically 640px); Audio Assets (MP3) status from `songs/`.
- Document History: initial entry `RELEASE.md scaffolded from Spotify catalog`.

**Stays as `⚠️ TBD` until the user provides:**

- ISRCs (per track), UPC — not in the public Spotify response; come from the distributor.
- Writers, Producers, Features (per track) — artist-supplied.
- Primary Genre / Subgenre — Spotify returns artist-level genres, not album-level.
- Label, Distributor.
- All marketing, PR, budget, KPI, paid-ad sections — campaign-time concerns.
- Audience demographics — comes from Spotify For Artists, not the public API.
- Press contacts, team contacts, links hub URLs.

## Past releases

For releases already in the artist's catalog (most of what Spotify returns), the campaign / KPI / paid-ad sections (6, 7, 8.4, 16, 17) generally don't apply going forward. Leave them as `⚠️ TBD` at scaffold time and let a later turn explicitly mark them `N/A — past release` if confirmed. Don't pre-emptively mark them N/A.

---

Below is the full template. Copy it verbatim into `releases/{release-slug}/RELEASE.md`, fill placeholders as data becomes available, and update **Last Updated** + the **Document History** table on every save.

# RELEASE.md

**Last Updated:** {YYYY-MM-DD}

> **Sharing Tags:** `[INTERNAL]` scrub before external sharing · `[SHAREABLE]` safe for DSPs, press, partners · `[OPS]` operations reference

---

## Section 1: Project Snapshot [SHAREABLE]

| Field | Value |
|-------|-------|
| Artist Name | {Artist Name} |
| Project Title | {Project Title} |
| Release Date (Digital) | ⚠️ TBD |
| Release Date (Physical) | N/A |
| Announcement Date | ⚠️ TBD |
| Format | {Album / EP (N tracks) / Single} |
| Territory | ⚠️ TBD |
| Primary Genre | ⚠️ TBD |
| Subgenre(s) | ⚠️ TBD |
| Explicit / Clean | ⚠️ TBD — confirm per track |
| Label | ⚠️ TBD |
| Distributor | ⚠️ TBD |

---

## Section 2: Release Identifiers & Metadata [OPS]

### 2.1 Digital Identifiers

| Identifier | Value |
|------------|-------|
| UPC | ⚠️ TBD |
| Spotify URI | {Spotify album URL} |
| Apple Music ID | ⚠️ TBD |
| Amazon ASIN | ⚠️ TBD |
| YouTube Asset ID | ⚠️ TBD |

### 2.2 Track-Level Metadata

_Repeat the block below for every track in the release._

**Track 01:**
| Field | Value |
|-------|-------|
| Title | {Track 01 Title} |
| ISRC | ⚠️ TBD |
| Duration | {mm:ss from duration_ms} |
| Explicit? | {true / false from tracks.items[0].explicit} |
| Writers | ⚠️ TBD |
| Producers | ⚠️ TBD |
| Features | ⚠️ TBD |

### 2.3 Audio Asset Status [INTERNAL]

| Asset | Sandbox Path | Format | Status |
|-------|-------------|--------|--------|
| {track-slug}.mp3 | `songs/{track-slug}/{track-slug}.mp3` | MP3 | ⚠️ TBD |
| Master WAVs (24-bit/44.1kHz) | Not in sandbox | WAV | ❌ MISSING — required for distribution |
| Instrumentals / Stems | Not in sandbox | — | ❌ MISSING |
| Radio Edits | Not in sandbox | — | ❌ MISSING |

---

## Section 3: Narrative & Positioning [SHAREABLE]

### 3.1 The Pitch (Elevator Version)

_2-3 sentences capturing the essence of this release._

[WRITE PITCH HERE]

### 3.2 Extended Narrative

_The fuller story. Context, artist arc, meaning._

[WRITE NARRATIVE HERE]

### 3.3 Project Highlights / Tentpoles

- ⚠️ TBD

### 3.4 Mood & Keywords

| Category | Value |
|----------|-------|
| Mood Tags | ⚠️ TBD |
| Vibe Keywords | ⚠️ TBD |
| Activity/Use Case Tags | ⚠️ TBD |

### 3.5 Comparables

| Category | Value |
|----------|-------|
| For Fans Of (RIYL) | ⚠️ TBD |
| Sonic References | ⚠️ TBD |
| Competitive Positioning | ⚠️ TBD |

---

## Section 4: Artist Background [SHAREABLE]

### 4.1 Artist Bio (150-200 words)

[WRITE BIO HERE]

### 4.2 Sales & Streaming History

| Platform | Stats |
|----------|-------|
| Spotify | ⚠️ TBD |
| Apple Music | ⚠️ TBD |
| Amazon Music | ⚠️ TBD |
| Pandora | ⚠️ TBD |
| YouTube | ⚠️ TBD |

| Metric | Value |
|--------|-------|
| Certifications | ⚠️ TBD |
| Previous Editorial Support | ⚠️ TBD |
| Notable Collaborations | ⚠️ TBD |

### 4.3 Press & Media Highlights

| Publication | Headline | Date | Link |
|-------------|----------|------|------|
| ⚠️ TBD | — | — | — |

---

## Section 5: Audience & Market Data [SHAREABLE]

### 5.1 Current Audience Stats

| Platform | Handle / Value |
|----------|----------------|
| Spotify Monthly Listeners | ⚠️ TBD |
| Instagram | ⚠️ TBD |
| TikTok | ⚠️ TBD |
| Twitter/X | ⚠️ TBD |
| YouTube | ⚠️ TBD |
| Facebook | ⚠️ TBD |
| VAULT/SMS List | ⚠️ TBD |

### 5.2 Geographic Data

| Region | Top 5 |
|--------|-------|
| Top Streaming Cities (US) | ⚠️ TBD |
| Top Streaming Countries | ⚠️ TBD |

### 5.3 Demographics

| Age Range | Percentage |
|-----------|------------|
| 18-24 | ⚠️ TBD |
| 25-34 | ⚠️ TBD |
| 35+ | ⚠️ TBD |

| Gender | Percentage |
|--------|------------|
| Female | ⚠️ TBD |
| Male | ⚠️ TBD |

### 5.4 Core Fanbase Insights

_Who are they? What do they care about?_

[WRITE INSIGHTS HERE]

---

## Section 6: DSP & Streaming Strategy [SHAREABLE]

### 6.1 Spotify For Artists Pitch (500 char limit)

[WRITE PITCH HERE — submit 7 days before release date, no earlier]

### 6.2 Focus Track(s)

| Track | Title | Rationale |
|-------|-------|-----------|
| Primary Focus | ⚠️ TBD | — |
| Secondary Focus | ⚠️ TBD | — |

### 6.3 Editorial Playlist Targets

| Platform | Playlist | Priority | Rationale |
|----------|----------|----------|-----------|
| ⚠️ TBD | — | — | — |

### 6.4 Pre-Save Strategy

| Element | Value |
|---------|-------|
| Pre-Save Link | ❌ Not created |
| SmartURL | ❌ Not set |
| Fan Opt-In | ⚠️ TBD |
| Pre-Save Incentive | ⚠️ TBD |

---

## Section 7: Marketing Strategy [INTERNAL]

### 7.1 Campaign Goals

- ⚠️ TBD

### 7.2 Key KPIs

| Metric | Current | Target |
|--------|---------|--------|
| Spotify Streams (Week 1) | 0 | ⚠️ TBD |
| Spotify Follower Growth | 0 | ⚠️ TBD |
| Pre-Saves | 0 | ⚠️ TBD |
| Instagram Followers | ⚠️ TBD | ⚠️ TBD |
| TikTok Views | 0 | ⚠️ TBD |

### 7.3 Rollout Phases

**PHASE 1: TEASE & ANNOUNCE**
| Field | Value |
|-------|-------|
| Dates | ⚠️ TBD |
| Goal | ⚠️ TBD |
| Action Items | ⚠️ TBD |

**PHASE 2: RELEASE WEEK**
| Field | Value |
|-------|-------|
| Dates | ⚠️ TBD |
| Goal | ⚠️ TBD |
| Action Items | ⚠️ TBD |

**PHASE 3: SUSTAIN & WORK**
| Field | Value |
|-------|-------|
| Dates | ⚠️ TBD |
| Goal | ⚠️ TBD |
| Action Items | ⚠️ TBD |

---

## Section 8: Social & Digital Marketing [INTERNAL]

### 8.1 Organic Social Strategy

| Element | Value |
|---------|-------|
| Primary Platforms | ⚠️ TBD |
| Content Pillars | ⚠️ TBD |
| Posting Cadence | ⚠️ TBD |
| Key Hooks/Angles | ⚠️ TBD |

### 8.2 TikTok & UGC Strategy

| Element | Value |
|---------|-------|
| UGC Hook(s) | ⚠️ TBD |
| Trend/Sound Strategy | ⚠️ TBD |
| Prompt-Based Storytelling Ideas | ⚠️ TBD |

### 8.3 Influencer & Community Marketing

| Influencer/Creator | Platform | Followers | Status | Notes |
|--------------------|----------|-----------|--------|-------|
| ⚠️ TBD | — | — | Not initiated | — |

### 8.4 Paid Advertising

| Platform | Budget | Objective | Targeting | Dates |
|----------|--------|-----------|-----------|-------|
| TikTok | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| Meta | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| YouTube | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| Spotify Ad Studio | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |

**Total Campaign Budget:** ⚠️ TBD

---

## Section 9: PR & Media Relations [SHAREABLE]

### 9.1 Press Strategy

| Element | Value |
|---------|-------|
| Press Angle | ⚠️ TBD |
| Embargo Date | ⚠️ TBD |
| Exclusive Offer | ⚠️ TBD |

### 9.2 Press Targets

| Outlet | Contact | Priority | Status | Notes |
|--------|---------|----------|--------|-------|
| ⚠️ TBD | ⚠️ TBD | — | Not initiated | — |

### 9.3 Press Materials

| Material | Status / Link |
|----------|--------------|
| Press Release | ❌ Not written |
| EPK / One-Sheet | ❌ Not complete |
| Press Photos | ❌ MISSING |
| Album Artwork (Hi-Res) | ⚠️ TBD |

---

## Section 10: Visual & Creative Assets [SHAREABLE]

### 10.1 Visual Strategy

| Element | Value |
|---------|-------|
| Creative Concept | ⚠️ TBD |
| Aesthetic/Mood | ⚠️ TBD |

### 10.2 Asset Inventory

| Asset | Status |
|-------|--------|
| Album Artwork (3000×3000px, RGB) | ⚠️ TBD |
| Press Photos | ❌ MISSING |
| Music Video | ⚠️ TBD |
| Lyric Video | ⚠️ TBD |
| Visualizer | ⚠️ TBD |
| Spotify Canvas | ⚠️ TBD |
| Social Content Templates | ⚠️ TBD |

---

## Section 11: Physical Production [OPS / INTERNAL]

### 11.1 Physical Formats

| Format | Quantity | Color/Variant | Status |
|--------|----------|---------------|--------|
| Vinyl | ⚠️ TBD | — | ⚠️ TBD |
| CD | ⚠️ TBD | — | ⚠️ TBD |
| Cassette | ⚠️ TBD | — | ⚠️ TBD |

---

## Section 12: Merch [INTERNAL]

### 12.1 Merch Items

| Item | Variants | Qty | Cost | Retail | Status |
|------|----------|-----|------|--------|--------|
| ⚠️ TBD | — | — | — | — | — |

### 12.2 Merch Strategy

| Element | Value |
|---------|-------|
| Bundling with Release | ⚠️ TBD |
| Exclusive Items | ⚠️ TBD |
| Tour Merch Tie-In | ⚠️ TBD |

---

## Section 13: Experiential & OOH [INTERNAL]

⚠️ TBD

---

## Section 14: Touring & Live [SHAREABLE]

⚠️ TBD

---

## Section 15: Team Contacts [INTERNAL]

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Artist / Label | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| Management | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| Publicist | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| Booking Agent | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |
| Distributor | ⚠️ TBD | — | — |

---

## Section 16: Budget Overview [INTERNAL]

| Category | Allocated | Spent | Remaining |
|----------|-----------|-------|-----------|
| Paid Media | ⚠️ TBD | $0 | — |
| Influencer | ⚠️ TBD | $0 | — |
| PR/Press | ⚠️ TBD | $0 | — |
| Video Production | ⚠️ TBD | $0 | — |
| Physical Production | ⚠️ TBD | $0 | — |
| OOH/Experiential | ⚠️ TBD | $0 | — |
| Merch | ⚠️ TBD | $0 | — |
| Other | ⚠️ TBD | $0 | — |
| **TOTAL** | **⚠️ TBD** | **$0** | **—** |

---

## Section 17: Performance Tracking [INTERNAL]

### 17.1 Weekly KPI Tracking

_Activate once the release is live._

| Week | Spotify | Apple | TikTok | IG |
|------|---------|-------|--------|-----|
| Week 1 | — | — | — | — |
| Week 2 | — | — | — | — |
| Week 3 | — | — | — | — |
| Week 4 | — | — | — | — |

### 17.2 Key Wins & Learnings

| Category | Notes |
|----------|-------|
| Wins | — |
| Adjustments Made | — |
| Learnings for Future Releases | — |

---

## Section 18: Links & Resources Hub

| Resource | Link / Status |
|----------|--------------|
| Master Asset Folder | ⚠️ TBD |
| SmartURL | ❌ Not created |
| Pre-Save Link | ❌ Not created |
| EPK | ❌ Not complete |
| Press Photos | ❌ MISSING |
| Audio Assets (MP3) | ⚠️ TBD |
| Audio Assets (WAV masters) | ❌ MISSING |
| Cover Art URL | {images[0].url from Spotify, or ❌ MISSING} |
| Social Content Pack | ⚠️ TBD |

---

## Outstanding Deliverables [INTERNAL]

| Deliverable | Owner | Due Date | Status |
|-------------|-------|----------|--------|
| Set release date | ⚠️ TBD | ⚠️ ASAP — blocks everything | ⚠️ TBD |
| Select distributor | ⚠️ TBD | — | ❌ |
| Export master WAVs (24-bit/44.1kHz) | ⚠️ TBD | — | ❌ |
| Finalize album artwork (3000×3000px) | ⚠️ TBD | — | ❌ |
| Submit to distributor | ⚠️ TBD | — | ❌ |
| Create pre-save link | ⚠️ TBD | — | ❌ |
| Write Spotify for Artists pitch | ⚠️ TBD | — | ❌ |
| Confirm PR/press plan | ⚠️ TBD | — | ⚠️ |
| Register publishing with PRO | ⚠️ TBD | — | ⚠️ |

---

## Notes & Internal Flags [INTERNAL]

- _Append timestamped notes here as new information surfaces._

---

## Document History

| Date | Updated By | Changes |
|------|------------|---------|
| {YYYY-MM-DD} | Recoup Sandbox | Initial RELEASE.md scaffolded from Spotify catalog |

---

For questions, contact ⚠️ TBD.
