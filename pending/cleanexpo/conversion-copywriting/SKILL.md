---
name: conversion-copywriting
description: Generate conversion-optimized page copy using VOC research, competitor insights, and proven structures. Use when creating or revising landing pages, service pages, or marketing content.
allowed-tools: Read, Write, Edit
---

# Conversion Copywriting Skill

## Purpose
Generate copy that converts visitors into customers by speaking their language with verified claims.

## CRITICAL PRINCIPLES (Non-Negotiable)

### 1. UNIQUE - No Plagiarism
Every piece of content must be original. The verification system checks for:
- Common marketing phrases used verbatim
- Template-like language
- Generic claims without specifics
**Requirement:** 95%+ uniqueness score

### 2. VERIFIABLE - 100% Backed Claims
Every claim must be traceable to:
- Business Consistency Master (NAP, licenses, credentials)
- VOC Research (customer quotes)
- Public records (ABN, awards)
**Requirement:** Zero unverifiable credential claims

### 3. AUTHENTIC - Real Customer Voice
All "customer language" must come from:
- Actual VOC research quotes
- Real testimonials with permission
- Documented support interactions

## Section Structure (Proven)

### Homepage
```
1. Hero - Grab attention with customer-centric headline
2. Problem - Address their pain using VOC language
3. Value Props - 3-4 key benefits (specific, not vague)
4. Proof - Testimonials, stats, case studies
5. Process - How it works in 3-5 steps
6. FAQ - Common questions (from real customer data)
7. CTA - Final push to action
```

### Services Page
```
1. Hero - What we do best
2. Services Overview - Brief list
3. Service Details - Deep dive each service
4. Process - How we work together
5. Pricing Teaser - Starting from / Get a quote
6. Proof - Relevant testimonials
7. CTA - Get started
```

### About Page
```
1. Hero - Who we are in one sentence
2. Story - Origin story, why we started
3. Team - Key people with photos
4. Values - 3-5 core values
5. Credentials - Licenses, certifications, awards
6. CTA - Connect with us
```

## Tone & Voice Guidelines

### Conversational (Default)
Write like you're talking to a friend who needs help.
- Use "you" and "we"
- Short sentences
- Active voice
- Questions okay

### Professional
For B2B, legal, medical, finance.
- More formal language
- Industry terminology (explained)
- Data-driven claims

### Friendly
For consumer services.
- Warm and approachable
- Empathetic language
- Personal touches

## BANNED Phrases (Never Use)
```
leverage, synergy, optimize, utilize, cutting-edge,
state-of-the-art, best-in-class, world-class,
game-changer, disruptive, innovative, paradigm shift,
holistic, seamless, robust, scalable, empower,
thought leader, bleeding edge, next-generation
```

## Jargon Replacements
```
leverage → use
utilize → use
optimize → improve
facilitate → help
implement → use
comprehensive → complete
innovative → new
seamless → smooth
robust → strong
scalable → grows with you
```

## Verification Process

### Before Publishing
1. Extract all claims from copy
2. Cross-reference with Consistency Master
3. Verify statistics have sources
4. Check credential claims against licenses
5. Confirm customer quotes are from VOC

### Verification Report
Every piece of copy includes:
- Uniqueness score (must be 95%+)
- Verified claims count
- Unverified claims (must be 0 critical)
- Warnings (acceptable if addressed)

## When to Use
- Creating new landing pages
- Rewriting existing pages
- Generating email copy
- Creating ad copy
- Writing proposals

## Integration Points
- `src/lib/copywriting/conversion-copywriting-engine.ts` - Main engine
- `generated_page_copy` table - Storage
- `page_copy_templates` table - Templates
- VOC Research Skill - Quote source
- Competitor Analysis Skill - Insights source
- Business Consistency Skill - Claim verification

## Output Format
```json
{
  "page_type": "homepage",
  "meta_title": "50-60 chars",
  "meta_description": "150-160 chars",
  "sections": [...],
  "verification": {
    "uniqueness_score": 97,
    "verified_claims": 12,
    "unverified_claims": 0,
    "passed": true
  }
}
```
