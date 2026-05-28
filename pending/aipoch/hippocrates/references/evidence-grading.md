# Evidence Appraisal Methodology Reference

Read this file when performing detailed evidence quality assessment or GRADE appraisal.

---

## 1. Evidence Hierarchy

From strongest to weakest:

1. **Systematic reviews & meta-analyses** (Cochrane reviews, well-conducted SRs)
2. **Randomized controlled trials** — especially large, multicenter, double-blind RCTs
3. **Cohort studies** (prospective > retrospective)
4. **Case-control studies**
5. **Case series / case reports**
6. **Expert opinion / consensus statements**
7. **In vitro / animal studies** (cannot be directly extrapolated to clinical practice)

Caveat: The pyramid is a heuristic. A well-designed cohort study may provide more reliable evidence than a small, high-bias RCT. Always evaluate study quality, not just study type.

---

## 2. GRADE Framework

### Starting level

- RCTs start at "High"
- Observational studies start at "Low"

### Downgrade factors (each can reduce by 1-2 levels)

| Factor | Key considerations |
|--------|--------------------|
| Risk of bias | Randomization, blinding, attrition, ITT analysis |
| Inconsistency | Heterogeneity in direction/magnitude across studies (I² > 50% warrants concern) |
| Indirectness | Do study populations/interventions/comparators/outcomes match the clinical question? |
| Imprecision | Sample size, event count, CI crossing the clinical decision threshold |
| Publication bias | Funnel plot asymmetry, small-study effects |

### Upgrade factors (observational studies only)

| Factor | Condition |
|--------|-----------|
| Large effect | RR > 2 or < 0.5 (no plausible confounding) → upgrade 1; RR > 5 or < 0.2 → upgrade 2 |
| Dose-response | Clear dose-response gradient present |
| Residual confounding direction | Plausible residual confounding would reduce the observed effect |

### Final quality levels

| Level | Meaning |
|-------|---------|
| ⊕⊕⊕⊕ High | Very confident the true effect is close to the estimate |
| ⊕⊕⊕◯ Moderate | True effect likely close to estimate, but may differ substantially |
| ⊕⊕◯◯ Low | Limited confidence — true effect may differ significantly |
| ⊕◯◯◯ Very low | Very little confidence in the estimate |

---

## 3. Key Statistical Measures — Teaching Guide

When analyzing study data, here's how to explain each measure (calibrate to student level):

### Treatment effect measures

- **RR (Relative Risk)**: < 1 means intervention group had lower risk. Tells you *proportional* reduction. Teach: "RR is the ratio — it tells you how much less likely something is, not how much less often."
- **ARR (Absolute Risk Reduction)**: More intuitive than RR — reflects the actual magnitude of clinical benefit. Teach: "A 50% relative reduction sounds impressive, but if baseline risk is 2%, the ARR is just 1%. That context matters."
- **NNT (Number Needed to Treat)**: How many people need treatment for one additional person to benefit. Lower = more impactful. Teach: "NNT is the most honest number in medicine — it tells you what the treatment actually delivers at population scale."
- **NNH (Number Needed to Harm)**: How many treated before one additional adverse event occurs.
- **OR (Odds Ratio)**: Approximates RR when event rate is low; overestimates effect at higher rates.

### Interpretation principles

- RR alone can mislead (low baseline risk → impressive RR but tiny ARR)
- Always present both relative and absolute measures
- NNT is the best teaching tool for explaining benefit to non-specialists
- Confidence intervals carry more clinical meaning than p-values — focus on whether CI crosses the null

---

## 4. Study Quality Quick-Check

When a student cites or asks about a specific study, rapidly assess:

- Does the study design match its claimed conclusions?
- Was the sample size adequate?
- Pre-registration status?
- Conflict of interest disclosures
- Peer-review status of the journal
- Replication — have subsequent studies confirmed the findings?
- Contradictory high-quality evidence?

Use this as a teaching opportunity: walk the student through the checklist so they learn to do it themselves.

---

## 5. Major Guideline Sources

**International**: WHO guidelines, Cochrane Library
**United States**: AHA/ACC (cardiovascular), NCCN (oncology), ADA (diabetes), IDSA (infectious disease), USPSTF (preventive medicine)
**Europe**: ESC (cardiovascular), ESMO (oncology), EASL (hepatology), ERS (respiratory)
**China**: Chinese Medical Association subspecialty guidelines, National Health Commission protocols
**Japan**: Japanese medical society guidelines (各学会ガイドライン)

When discussing guideline recommendations, note that different regions may diverge due to population differences, healthcare system constraints, or available evidence. Calibrate to the student's likely context.
