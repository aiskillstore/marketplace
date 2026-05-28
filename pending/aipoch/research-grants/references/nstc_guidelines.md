# Taiwan National Science and Technology Council (NSTC) Proposal Writing Guide

> ⚠️ **Important Disclaimer**: This guide is prepared based on public information and general academic writing principles. **Please ensure you refer to the official NSTC website and the specific Call for Proposals (CFP) for your application to obtain the most accurate and up-to-date requirements.** Requirements may vary by field, program type, and year.

## Overview

**Official Name**: National Science and Technology Council (NSTC)  
**Former Name**: Ministry of Science and Technology (MOST)  
**Official Website**: https://www.nstc.gov.tw/

**Mission**: To promote the development of science and technology in Taiwan through research funding, emphasizing scientific breakthroughs, industrial applications, and societal impact.

---

## CM03: Research Proposal Content

CM03 is the core technical document of the NSTC proposal. Its official title is "Contents of Grant Proposal".

### Official Formatting Requirements

According to official NSTC documents:

**Paper Size**: A4 (29.7 cm × 21 cm)

**Fonts**:
- Chinese: PMingLiU or BiauKai
- English: Times New Roman or Arial
- Font Size: Minimum 12pt

**Spacing**: Single spacing for English; no extra line spacing required for Chinese.

**Page Limits** (Varies by department and program type):
- **Humanities and Social Sciences**: Individual 1-year: 30 pages; Multi-year: 45 pages
- **Engineering and Technologies**: Individual 1-year: 20 pages; Multi-year: 25 pages
- **Natural Sciences**: Individual: 30 pages; Integrated: 45 pages
- **Life Sciences (Bio-medical)**: Individual: 25 pages
- **⚠️ Crucial**: Page limits include references, tables, and figures. Exceeding the limit may lead to immediate rejection.

**File Format**: Submission in PDF format is recommended.

---

## Required Content Sections

According to the official CM03 template, the proposal must include:

### 1. Abstract

**Requirements**:
- **Chinese Abstract**: Maximum 500 characters
- **English Abstract**: Maximum 500 words
- **Keywords**: 3-5 keywords in both Chinese and English

**Content**:
- Research background and problem statement
- Research objectives
- Key methodology and approach
- Expected outcomes and impact

### 2. Research Background and Objectives

**Essential Elements**:
- Problem statement and its significance
- Research originality and innovation
- Expected impact
- Literature review of relevant research (domestic and international)
- Important references and their critical evaluation
- **For Continued Projects**: Progress report of the previous year

### 3. Research Methods, Steps, and Timeline

**Essential Elements**:
- Research principles and methodology
- Justification for the chosen methods
- Innovative aspects of the research approach
- Anticipated problems and solutions
- Equipment and instrumentation requirements
- **For International Travel**: Explanation of necessity and expected benefits
- **Execution Timeline**: Itemized activities listed by year

### 4. Expected Outcomes

**Essential Elements**:
- Expected research tasks (by year)
- Talent cultivation plan
- Expected outputs:
  - Journal papers (specify target journals)
  - Conference papers
  - Patents
  - Technology transfers
  - Other deliverables

---

## FY 114 (2025) Application Requirements

According to official announcements:

**Application Method**: Entirely online via the "Academic Research Service Portal".

**Project Start Date**: Most projects begin on August 1, 2025 (Year 114).

**Academic Ethics Requirements**:
- First-time applicants and first-time participants must complete **at least 6 hours** of academic ethics education training within 3 years prior to submission.
- Supporting documentation must be provided.

**Thesis Disclosure**:
- If the proposal content involves a thesis from a student supervised by the Principal Investigator (PI), it must be explicitly disclosed or cited.
- Previously published work (including student theses) should not be concealed as new research content.

---

## Budget Categories

According to official guidelines:

**Personnel**:
- Postdoctoral researchers
- Research assistants
- Part-time personnel
- **Note**: PI salary is generally not allowed as a line item.

**Equipment**:
- Items with a unit price exceeding NT$10,000 and a service life of over 2 years.
- Items exceeding NT$200,000 may require price quotations.

**Consumables**:
- Lab supplies, reagents, software licenses, etc.

**Travel**:
- Domestic and international academic conferences.
- Research collaborations.

**Other**:
- Publication fees, data collection fees, outsourcing fees, etc.

---

## Review Criteria

**Note**: NSTC does not disclose specific scoring weights. The following are general evaluation dimensions based on academic practice:

1. **Innovation**: Originality of concepts and methods.
2. **Feasibility**: Rigor of methodology and availability of preliminary data.
3. **PI Capability**: Past performance and professional expertise.
4. **Value**: Academic contribution and social/industrial impact.

---

## Official Resources

**NSTC Official Website**: https://www.nstc.gov.tw/

**Application System**: Access via the "Academic Research Service Portal."

**Inquiry Hotlines**:
- Computer/System Issues: 0800-212-058 or (02)2737-7592
- Regulatory Inquiries: (02)2737-7440, 7568, 7847, 7980, 8010

**Important Tip**: Always download the latest application forms and guidelines from the "Research Project Section" on the NSTC website.

### LaTeX Templates

For scholars who prefer writing proposals in LaTeX, here are excellent community-contributed templates:

#### Official CTAN Package (Recommended)

**nstc-proposal** - A professional LaTeX class for NSTC proposals:
- **GitHub**: https://github.com/L-TChen/nstc-proposal
- **CTAN**: Installable via `tlmgr install nstc-proposal`
- **Support**: Supports both CM03 and CM302 (Reference format).
- **Features**:
  - Compatible with pdfLaTeX and XeTeX.
  - Bilingual support (Chinese/English).
  - Predefined section commands (`\ProposalBackground`, `\ProposalMethod`, `\ProposalPlan`, `\ProposalIntegration`).
  - Multiple font options (Standard, Libertine, Kai).
  - Typesetting compliant with NSTC requirements.

**Installation**:
```bash
# Via TeX package manager (easiest)
tlmgr install nstc-proposal

# Or manual installation from GitHub
git clone https://github.com/L-TChen/nstc-proposal.git
cd nstc-proposal
latex nstc-proposal.ins
```

**Basic Usage Example**:
```latex
\documentclass{nstc-cm03}
\usepackage{microtype}

\begin{document}
\ProposalBackground
% Enter content here

\ProposalMethod
% Enter content here

\ProposalPlan
% Enter content here

\nocite{*}
\bibliographystyle{plain}
\bibliography{references}
\end{document}
```

#### Other Templates

**Engineering Department Template**:
- GitHub: https://github.com/mcps5601/NSTC-proposal-LaTeX
- Specifically targets the CM03 format provided by the Department of Engineering.
- **Note**: Formatting requirements may vary slightly between departments.

**Overleaf Templates**:

1. **audachang's CM03 Template** (Recommended for Overleaf users):
   - GitHub: https://github.com/audachang/taiwan-nstc-cm03-template
   - Overleaf: Can be imported directly from GitHub.
   - **Features**:
     - Includes official CM03.doc for reference.
     - Uses XeCJK and BiauKai font support for Traditional Chinese.
     - Well-organized structure with separate files for sections (`background.tex`, `methods.tex`, `expected_outcomes.tex`).
     - **Important**: Must use XeLaTeX or LuaLaTeX compiler.
   - Developed based on Chen Wen-sheng's template.

2. **Other Overleaf Templates**:
- Search for "National Science Council Research Project Content: CM03" on Overleaf.   - Includes various community-contributed templates.

> ⚠️ **Important Tip**: These are community-contributed templates. Always verify that the formatting matches the latest official requirements for your specific field and program type. The `nstc-proposal` CTAN package is the most reliable choice due to regular maintenance.

---

## Practical Insights from Reviewers

> 📚 **Source**: This section is based on "Experience Sharing in Writing NSTC Proposals" by Prof. You-Ping Huang, President of National Penghu University of Science and Technology. These insights reflect the **reviewer's perspective**, particularly applicable to the Department of Engineering.

> ⚠️ **Important Note**: Scoring thresholds and specific criteria may vary by department (e.g., Humanities, Engineering, Natural Sciences, Life Sciences). Please check the requirements for your specific field.

### Understanding the Scoring System

Based on experience in the Engineering Department - Automation/Control field:

**Scoring Thresholds**:
- **92+ (Top 5%)**: Outstanding research level - eligible for the Outstanding Research Award.
- **88+ (Top 15%)**: Necessary threshold for applying for a second concurrent project.
- **81+ (Top 54-55%)**: **Passing Grade** - Projects scoring 81 and above are generally recommended for approval.
- **80 and below**: Not recommended for approval.

**Core Insight**: The gap between "Passing" (81) and "Excellent" (88+) often lies in the strength of preliminary data, clarity of innovation, and the persuasiveness of feasibility.

---

### Writing Strategies by Section

#### Abstract

**Reviewer Expectations**:
- Must immediately demonstrate **innovation** and **problem-solving strategies**.
- Should grab the reviewer's attention upon first reading.
- Clearly state how this project differs from existing work.

**Key Question**: Does the abstract make the reviewer want to read the rest of the proposal?

#### Research Background and Motivation

**Reviewer Focus**:
- **Clear Problem Definition**: Is the core problem well-defined?
- **Reasonable Design and Objectives**: Are the goals achievable and well-supported?
- **Logical Flow**: Does the background lead naturally to the research objectives?

**Common Weakness**: Vague problem descriptions that fail to identify the specific research gap you are filling.

#### Literature Review

**Quality over Quantity**:
- Select **highly relevant** literature rather than just listing a large number of papers.
- **Critical Synthesis**: Don't just list papers; analyze strengths, weaknesses, and gaps.
- **Timeliness**: Include publications from the **last 2-3 years** to show mastery of the current cutting edge.
- **Strategic Positioning**: Use the review to lead the reader to agree with your research goals.

**Reviewer Perspective**: A curated review of 20 papers with critical analysis is far superior to a list of 50 papers without synthesis.

#### Research Methods and Implementation

**Feasibility is Key**:
- **Avoid Over-idealization**: Projects that are too ambitious but lack risk mitigation strategies often fail.
- **Logical Progression**: Each step should follow naturally from the previous one.
- **Comparison with Existing Methods**: Clearly show how your method is different and why it is better.
- **Contingency Plans**: Anticipate potential problems and provide alternative solutions.

**Reviewer Red Flags**:
- Proposing highly difficult methods without demonstrating capability.
- Lack of logical connection between steps.
- Failure to discuss potential challenges.
- Novel methods lacking supporting preliminary data.

#### Expected Outcomes

**Specificity and Quantifiability**:
- ✅ **Good**: "Increase system efficiency by 15% compared to benchmark method X."
- ❌ **Bad**: "Improve system efficiency."

**Include Multi-dimensional Outputs**:
- **Academic Value**: Target journals and expected number of publications.
- **Economic Benefits**: Potential industrial applications.
- **Talent Cultivation**: Number and level of students to be trained.

---

### Budgeting Advice

**Link to the Research Plan**:
- Every budget item should directly support a specific research activity.
- Personnel costs should reflect actual time commitment.
- Equipment justifications should explain why existing facilities are insufficient.

**International Conference Travel**:
- Typical budget: NT$70,000 - 100,000.
- **Must Justify**: Explain your past record and contributions to international conferences.
- State how attending the conference benefits the research.

**Reviewer Checkpoint**: Does the budget match the proposed activities? Are there unexplained large expenditures?

---

### Career Strategy Advice

**Advice for New Faculty**:
1. **Must Apply**: New researchers have certain advantages - don't miss the opportunity.
2. **Build a Foundation**: Use Undergraduate Research Projects to accumulate preliminary data.
3. **Self-Assessment**: Use a reviewer's checklist to evaluate your own proposal before submission.

**Building Academic Visibility**:
- Join professional societies (e.g., IEEE, CAA).
- Serve as a reviewer for journals and conferences.
- Serve as an Associate Editor (AE) or editorial board member.
- **Importance**: Reviewers are more likely to recognize and trust researchers active in the academic community.

---

### Preparation and Mindset

**Timeline**:
- **Start Early**: A successful proposal requires multiple revisions.
- **Iterate, Iterate, Iterate**: Don't wait until the deadline to start writing.
- **Seek Feedback**: Ask colleagues to review your drafts.

**Handling Rejection**:
- **Learn from Feedback**: Study all reviewer comments carefully.
- **Revise and Resubmit**: Address criticisms in the next application.
- **Consider Alternatives**: If there are fundamental issues, consider a different program type or research area.

**Professional Presentation**:
- **Figures and Tables**: Must be clear, numbered, and properly labeled.
- **Formatting**: Professional typesetting shows attention to detail.
- **Proofreading**: Typos and formatting errors suggest a lack of diligence.

---

### Self-Assessment Checklist

Before submitting, ask yourself:

**Innovation**:
- [ ] Is my method truly novel, or just an incremental improvement?
- [ ] Have I clearly explained what is new compared to existing work?
- [ ] Do I have evidence (preliminary data) that my innovation is feasible?

**Feasibility**:
- [ ] Is my methodology description detailed and logically sound?
- [ ] Do I have the necessary expertise and resources?
- [ ] Have I addressed potential problems?
- [ ] Is my timeline realistic?

**Impact**:
- [ ] Are my expected outcomes specific and measurable?
- [ ] Have I explained both academic and practical value?
- [ ] Does my project align with national priorities or industrial needs?

**Presentation**:
- [ ] Are all figures and tables clear and correctly labeled?
- [ ] Is the writing clear and error-free?
- [ ] Does the budget align with the proposed activities?
- [ ] Have I included all required sections?

---

## Advanced Writing Strategies from Senior Reviewers

> 📚 **Source**: This section integrates insights from two comprehensive guides:
> 1. "How to Improve the Quality of Government S&T Development Proposals" by **Prof. Yao-Huang Kuo**.
> 2. "How to Improve the Quality of Government S&T Development Proposals" by **President Yao-Hui Wei** of Mackay Medical College.
>
> These guides are based on extensive experience reviewing government S&T projects, including NSTC and other ministerial programs.

### Closed-Loop Logic Framework

**Core Principle**: A high-quality proposal must demonstrate complete logical consistency from problem to performance.

**The Logic Loop**:
```
Identify Problem → Define Objectives → Formulate Strategy → 
Specific Measures → Execution Plan → Key Performance Indicators (KPIs)
```

**Key Requirement**: Every element must be tightly linked logically.

**Example of a Logical Break**:
- ❌ **Objective**: Improve industrial technology.
- ❌ **Strategy**: Provide student scholarships.
- **Problem**: The strategy does not directly support the objective.

**Example of a Logical Loop**:
- ✅ **Objective**: Improve industrial technology.
- ✅ **Strategy**: Develop advanced manufacturing processes.
- ✅ **Measures**: Establish testing facilities, train engineers.
- ✅ **KPI**: Achieve a 15% efficiency increase, train 20 engineers.

---

### SMART Principles for Project Planning

Before writing, ensure your project meets the **SMART** criteria:

| Criterion | Meaning | Application |
|-----------|---------|-------------|
| **S**pecific | Clear objectives | Define precise technical metrics (e.g., "Improve accuracy to 95%"). |
| **M**easurable | Quantifiable KPIs | Use numbers, percentages, or counts. |
| **A**chievable | Realistic scale | Match with available resources, personnel, equipment, and budget. |
| **R**ealistic | Scientifically grounded | Based on data and logical reasoning. |
| **T**imely | Clear schedule | Specific milestones with dates. |

---

### The Four Dimensions of Review Criteria

Reviewers evaluate proposals across four key dimensions:

#### 1. **Necessity**
- Does it align with national S&T policy?
- Is there an urgent need for this research?
- Why must this problem be solved **now**?
- Why is **your institution** the right choice for this task?

**Poor Proposal**: Generalities without urgency.  
**Strong Proposal**: Cites specific policy documents and demonstrates time-sensitive needs.

#### 2. **Feasibility**
- Can the goals be achieved within the proposed timeframe?
- Is the team qualified (past performance, expertise)?
- Is the methodology rigorous and well-supported?
- Is the management plan realistic?

**Red Flag**: Overly ambitious goals lacking preliminary data or risk mitigation.

#### 3. **Appropriateness**
- Does the budget match the scope of work?
- Is the personnel allocation reasonable?
- Are existing facilities being used effectively?
- Are high-cost items fully justified?

**Reviewer Question**: Why is this expensive equipment needed if similar facilities already exist?

#### 4. **Impact and Benefits**
- Beyond academic output, what are the societal impacts?
- What are the economic benefits or industrial applications?
- Impact on environment, health, or national security?
- What is the long-term sustainability?

**Core Insight**: Reviewers increasingly value **societal impact** over pure academic metrics.

---

### Key Performance Indicators (KPIs): Three Levels

Understanding the difference between inputs, outputs, and outcomes is vital:

| Level | Type | Example | Reviewer Value |
|-------|------|----------|----------------|
| **Input** | Resources invested | Personnel, budget, equipment | Basic requirement |
| **Output** | Direct products | Papers, patents, conferences | Minimum expectation |
| **Outcome** | Real-world impact | Industrial adoption, health improvement, policy change | **High Value** |

**Comparison Example**:
- ❌ **Weak KPI**: "Publish 3 papers" (Output only).
- ✅ **Strong KPI**: "Publish 3 papers in Q1 journals AND transfer technology to 2 companies, generating NT$5M in licensing revenue" (Output + Outcome).

**KPI Best Practices**:
- **Relevance**: Directly linked to project goals.
- **Convenience**: Easy to measure and verify.
- **Credibility**: Based on realistic projections.
- **Cost-effectiveness**: Achievable within the budget.

**Progressive Goals**: Show year-by-year progress rather than just the final target.
- Year 1: 30% completion.
- Year 2: 70% completion.
- Year 3: 100% completion + sustainability plan.

---

### Practical Analysis Tools

#### SWOT Analysis

Use SWOT to strategically position your proposal:

| Strengths | Weaknesses |
|-----------|------------|
| Your unique expertise | Resource limitations |
| Existing facilities | Lack of certain specific skills |
| Strong past performance | Time constraints |

| Opportunities | Threats |
|---------------|---------|
| Policy alignment | Competing teams |
| Industry partnerships | Rapid tech changes |
| Emerging trends | Budget cuts |

**Key**: Don't just list SWOT—**provide strategies** to address weaknesses and threats.

**Example**:
- **Weakness**: Lack of high-performance computing cluster.
- **Mitigation**: Collaboration with the National Center for High-performance Computing (NCHC).

#### Fishbone Diagram

Use a Fishbone diagram to show deep understanding of the problem:

```
                    Core Problem
                         ↑
        ┌───────┬────────┼────────┬───────┐
      Factor 1  Factor 2  Factor 3  Factor 4
        │         │         │         │
      Sub-cause Sub-cause Sub-cause Sub-cause
```

**Purpose**: Demonstrate to reviewers that you have analyzed root causes, not just surface symptoms.

#### Gantt Chart

For complex multi-year projects, use a Gantt chart to show:
- Task dependencies.
- Resource allocation over time.
- Milestones and deliverables.
- Risk management checkpoints.

**Professional Presentation**: Use visualization tools to demonstrate project management capability.

---

### Budgeting: Critical Details

#### Necessity and Reasonableness

**Every budget item must answer two questions**:
1. **Why is this necessary?** (Link to specific research activities).
2. **How was this calculated?** (Show detailed breakdown).

**Example - Equipment Justification**:
- ❌ **Weak**: "High-performance workstation: NT$150,000."
- ✅ **Strong**: "High-performance workstation (Intel Xeon 32-core, 128GB RAM, RTX 4090 GPU) for deep learning model training: NT$150,000. Existing lab PCs (8GB RAM) cannot handle the 50GB datasets required for Objective 2. Estimated training time reduction from 2 weeks to 2 days."

#### Budget Categories

**Core Rule**: Strictly distinguish between "Recurrent" and "Capital" expenditures.

**Recurrent**:
- Personnel costs.
- Travel.
- Consumables.
- Publication fees.

**Capital**:
- Equipment with unit price ≥ NT$10,000 and life ≥ 2 years.
- Items ≥ NT$200,000 may require price comparisons.

**Taboo**: Using S&T funds for general administrative work.

#### Outsourcing Fees

If including outsourcing:
- Define the specific scope of work.
- Explain why it cannot be done in-house.
- Describe the selection and supervision process.
- Provide a cost breakdown.

#### International Conference Travel

**Typical Range**: NT$70,000 - 100,000.

**Essential Justification**:
- Your past record of international conference presentations.
- Specific conference names and dates (if known).
- How attendance benefits the research (networking, collaboration, dissemination).
- Why the conference is significant for your field.

---

### Common Negative Reviewer Feedback to Avoid

Based on actual feedback from government project reviews:

#### 1. **Vague Objectives**
- ❌ "Promote the development of..."
- ❌ "Research on..."
- ✅ "Develop an algorithm that achieves 95% accuracy on benchmark X."

#### 2. **Redundancy and Overlap**
- **Problem**: Multiple agencies funding similar work.
- **Solution**: Clearly differentiate from existing projects; coordinate with other ministries before submission.

#### 3. **Lack of Continuity Explanation**
- **For Continued Projects**: Must explain the relationship between previous results and the new application.
- Show how you are building on past work (not repeating it).

#### 4. **Technology Push Without Market Pull**
- **Problem**: Developing technology without considering industrial needs or market readiness.
- **Solution**: Include industry letters of intent, market analysis, or user needs assessments.

#### 5. **Ignoring Negative Impacts**
- **Common Oversight**: Privacy concerns, environmental impact, ethical issues.
- **Solution**: Include risk assessment and mitigation strategies.

#### 6. **Excessive Administrative Overhead**
- **Problem**: Too many Project Management Offices (PMOs) or coordinators.
- **Solution**: Justify the administrative structure based on project complexity.

#### 7. **Missing Customer Definition**
- **Problem**: Who will use your research results?
- **Answer**: Clearly define your target users/beneficiaries.

---

### Writing for the Reviewer

**Remember**: You are writing for a busy reviewer, not for yourself.

**Best Practices**:
1. **Use Visual Aids**: Replace dense text with charts, tables, and flowcharts.
2. **Data-Driven**: Support arguments with specific numbers and citations.
3. **Objectively Correct**: Verify all data and calculations.
4. **Logical Flow**: Each section should lead naturally to the next.
5. **Professional Polish**: Clean layout, no typos, consistent terminology.

**Key Question**: After reading the abstract, does the reviewer **want** to keep reading?

---

### Policy Alignment

**Crucial**: Connect your research to national priorities.

**How to Show Alignment**:
- Cite specific government policy documents (e.g., "Six Core Strategic Industries").
- Reference National Development Plans.
- Show how your research addresses societal needs.
- Link to specific priorities of the department/ministry.

**Example**:
"This research directly supports Taiwan's '5+2 Innovative Industries Plan,' specifically in the bio-medical sector, by developing..."

---

### Exit Strategy - For Multi-year Projects

**Requirement**: Long-term projects must include a sustainability plan.

**Core Questions**:
- What happens when the funding ends?
- How will results be maintained or transferred?
- What are the success/failure criteria for early termination?

**Components**:
- Tech transfer plan.
- Industry partnership agreements.
- Follow-on funding strategy.
- Publication and dissemination plan.

---

### Evaluation Mechanisms

**For Public Service Projects**: Include feedback and evaluation systems.

**Components**:
- User satisfaction surveys.
- KPI tracking.
- Regular milestone reviews.
- Adjustment mechanisms based on feedback.

---

## Common Mistakes to Avoid

1. **Exceeding Page Limits** → Automatic rejection.
2. **Missing Required Sections** → Incomplete application.
3. **Incorrect Font or Formatting** → Non-compliance.
4. **Lack of Preliminary Data** (where applicable) → Lower competitiveness.
5. **Vague Methodology** → Leads to doubts about feasibility.
6. **Failure to Link to Taiwan Context** → Lower impact score.

---

## Final Checklist

Before submission, confirm:

- [ ] Checked field-specific requirements in the Call for Proposals.
- [ ] Verified page limits for your department and project type.
- [ ] Completed academic ethics training (if required).
- [ ] Prepared both Chinese and English abstracts.
- [ ] Included all required forms (CM01, CM02, CM03, etc.).
- [ ] Verified all formatting requirements.
- [ ] Proofread for errors.
- [ ] Submitted via the official online system before the deadline.

---

## Disclaimer

**This guide is for reference only.** Official requirements may change annually and vary by program. **Always refer to**:
1. The latest official NSTC Call for Proposals.
2. Specific application guidelines for your program.
3. Your institution's Office of Research and Development (ORD).
4. Senior colleagues in your field.

For the most authoritative information, visit: **https://www.nstc.gov.tw/**