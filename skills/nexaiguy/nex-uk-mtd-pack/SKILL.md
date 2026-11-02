---
name: nex-uk-mtd-pack
description: 'Automate UK MTD for Income Tax compliance, applicability checks, and quarterly deadline scheduling for sole traders. Use when: Calculate qualifying income across multiple trade and property sources; Identify the specific mandate year based on 2024-2027 tax year thresholds; Generate quarterly submission calendars for standard or calendar tax periods.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-uk-mtd-pack
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex UK MTD Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-uk-mtd-pack). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

UK sole traders and landlords face a massive shift as Self Assessment is replaced by Making Tax Digital (MTD). Calculating qualifying income across multiple sources, managing quarterly deadlines, and navigating the new penalty points system is complex and high-stakes.

## What it does

- Determines mandation status and start years (2026, 2027, or 2028) based on gross income thresholds.
- Generates personalized onboarding plans including software selection criteria and sign-up timelines.
- Produces income-specific digital record checklists for trades and property businesses.
- Builds quarterly update calendars with specific submission deadlines and cumulative reporting rules.
- Drafts plain-English briefings on the 4-point penalty system and the 2026/27 soft landing period.

## Why this beats prompting it yourself

General LLMs often confuse MTD for VAT with MTD for Income Tax or miss the specific "qualifying income" definition (gross vs. profit). This skill uses a hardcoded applicability decision tree and the latest HMRC timetable to ensure accuracy on thresholds, joint property rules, and transition years.

## Use cases

- Assess if a client with mixed rental and trade income must join MTD by April 2026.
- Create a digital record-keeping checklist for a landlord moving away from paper receipts.
- Generate a deadline schedule for a sole trader to avoid accruing penalty points.
- Explain the final declaration process to a taxpayer used to traditional Self Assessment.

## Known limitations

Does not cover partnerships, limited companies, or trusts. Foreign property income involving non-domicile status requires separate professional advice.

## Example

**Request**

I have £45,000 from my consultancy and £10,000 in rental income. When do I need to start MTD, and what happens if I miss a quarterly update?

**Result**

Based on your £55,000 total qualifying income, you are mandated for MTD from 6 April 2026.

Your first quarterly update is due 7 August 2026. Under the new penalty system, each late update earns 1 point. At 4 points, you receive a £200 fine. However, a soft landing applies for 2026/27.

## Questions

### How does the nex-uk-mtd-pack help me prepare for the upcoming MTD for Income Tax changes?

This skill automates the transition to HMRC's new regime by calculating mandation dates based on gross income, generating quarterly submission calendars, and creating digital record-keeping checklists tailored to sole traders and landlords.

### Why should I use this skill instead of just asking a standard AI agent about UK tax rules?

Unlike general AI which often confuses MTD for VAT with Income Tax rules, this skill uses a specialized decision tree to correctly distinguish between gross income and profit, ensuring you receive accurate advice on thresholds and joint property rules.

### Are there any specific business structures that this skill does not support?

The pack is designed for sole traders and landlords with rental or trade income; however, it does not currently support limited companies, partnerships, trusts, or complex foreign property income scenarios.

### Which AI agents is this skill compatible with and how do I install it?

The skill is built to be compatible with most major LLM-based agents that support custom skill integration; you simply import the package into your agent's environment to begin running the compliance workflows.

### What exactly is included in the nex-uk-mtd-pack purchase?

Your purchase includes the full logic for MTD applicability checks, the quarterly update scheduling engine, record-keeping checklist templates, and plain-English briefing drafts for the new penalty system.

### How are updates handled if HMRC changes the MTD deadlines or income thresholds?

Tax regulations are subject to change, so this skill is updated periodically to reflect the latest HMRC timetables and threshold adjustments, ensuring your compliance advice remains current through the 2026-2028 rollout.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
