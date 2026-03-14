# DB Craft Marketplace Submission Checklist

## Purpose

Use this checklist as the final release gate before submitting DB Craft to a public skill marketplace.

## 1. Core Positioning

- [x] Product name confirmed as `DB Craft`
- [x] Public positioning is `design-to-SQL`, not direct live database execution
- [x] Marketplace description avoids implying automatic production deployment
- [x] Marketplace description explains that DB Craft opens a local visual schema tool

## 2. Core User Documentation

- [x] Marketplace description prepared
  - See `references/marketplace-copy.md`
- [x] Example prompts prepared
  - See `references/example-prompts.md`
- [x] Installation and prerequisites documented
  - See `references/install-prerequisites.md`
- [x] Data and security notes documented
  - See `references/data-security.md`
- [x] Usage and operating notes documented
  - See `references/usage.md`

## 3. Product Behavior To Double-Check Before Submission

- [x] Reuse an existing local service if already running
- [x] Start the local service automatically when it is not running
- [x] Tell the user whether the service was reused or newly started
- [x] Keep model changes reflected in the current `*.dbmodel.json` for the same workspace/project
- [x] Save/export SQL to the active local workspace
- [x] Keep the public marketplace behavior at `model + SQL + handoff`
- [x] Support fallback from AI Build to `Send to Codex`

## 4. Licensing And Ownership

- [x] MIT license added to the product root
  - See `D:\DBdesigner\LICENSE`
- [x] About dialog includes license and copyright notice
- [x] Help manual includes open-source license disclosure
- [x] README mentions MIT license

## 5. Marketplace Submission Assets

- [ ] Marketplace icon prepared
- [ ] At least 1 polished product screenshot prepared
- [ ] Ideally 3 screenshots prepared:
  - main modeling workspace
  - AI build or SQL import flow
  - SQL preview / handoff flow
- [ ] Short demo GIF or short demo video prepared
- [ ] Public support/contact channel confirmed

Asset planning reference:
- `references/icon-and-screenshot-checklist.md`

## 6. Technical Packaging Review

- [ ] Remove or generalize machine-specific absolute paths from the public-facing marketplace copy where possible
- [ ] Review whether `D:\DBdesigner` should stay as an implementation detail instead of user-facing marketing copy
- [ ] Review whether `http://127.0.0.1:3000` should appear only in install/runtime notes, not in high-level marketing text
- [ ] Verify the launcher and startup behavior on a clean Windows machine, not only the current development machine
- [ ] Verify behavior when `Node.js` is missing
- [ ] Verify behavior when port `3000` is occupied by a non-DB-Craft process

## 7. Data And Trust Review

- [x] Local-vs-cloud behavior is documented
- [x] AI-provider prompt transmission is disclosed
- [x] API key sensitivity is disclosed
- [x] Local handoff file behavior is disclosed
- [ ] Add a short public privacy/support statement if the marketplace expects one

## 8. Internationalization Review

- [x] Default language can start in English
- [x] Language choice persists across reopen
- [x] Help manual follows saved language
- [x] High-frequency dialogs and UI are localized
- [ ] Do one final pass for low-frequency edge-case messages in non-Chinese modes before submission

## 9. Sample And Demo Readiness

- [x] Sample model prepared
  - `D:\DBdesigner\samples\sample.dbmodel.json`
- [x] Sample SQL prepared
  - `D:\DBdesigner\samples\sample.sql`
- [ ] Add a visible `Open Sample Model` entry in the product if you want marketplace reviewers to discover the sample immediately

## 10. Recommended Final Submission Bundle

Before submission, make sure you have these ready in one place:

- `SKILL.md`
- `agents/openai.yaml`
- `references/marketplace-copy.md`
- `references/example-prompts.md`
- `references/install-prerequisites.md`
- `references/data-security.md`
- `references/icon-and-screenshot-checklist.md`
- product screenshots
- product icon
- short demo media

## 11. Current Bottom Line

Current status:
- `Documentation readiness`: strong
- `Product readiness`: strong
- `Marketplace asset readiness`: still incomplete
- `Biggest remaining blockers`: icon, screenshots, demo assets, and public-facing de-localization review

If you want the shortest path to submission, do these next:

1. Prepare icon + screenshots + one short demo
2. Review and reduce machine-specific wording in public-facing copy
3. Do one clean-machine Windows startup verification
