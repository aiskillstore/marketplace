# Conference Formatting Requirements

Comprehensive formatting requirements and submission guidelines for major academic conferences across various disciplines.

**Last Updated**: 2024

---

## Machine Learning and Artificial Intelligence

### NeurIPS (Neural Information Processing Systems)

**Conference Type**: Top-tier machine learning conference  
**Frequency**: Annual (December)

**Formatting Requirements**:
- **Page Limit**:
  - Main Text: 8 pages (excluding references)
  - References: Unlimited
  - Appendix/Supplementary Material: Unlimited (optional, review at the discretion of reviewers)
- **Layout**: Double-column
- **Font**: Times or Times New Roman, 10pt for main text
- **Line Spacing**: Single-spaced
- **Margins**: 1 inch (2.54 cm) on all sides
- **Column Gap**: 0.25 inches (0.635 cm)
- **Paper Size**: US Letter (8.5 × 11 inches)
- **Anonymization**: Initial submission **must** be anonymous (double-blind review)
  - Remove author names and affiliations
  - Anonymize self-citations ("Author et al." → "Anonymous et al.")
  - Remove acknowledgments that reveal identity
- **Citations**: Numbered in square brackets [1], [2-4]
- **References**: Any consistent style (usually numbered citations)
- **Figures**:
  - High resolution (300+ dpi)
  - Colorblind-friendly color schemes recommended
  - Can span across both columns if necessary
- **Tables**: Clear and legible at publication size
- **Equations**: Should be numbered if referenced in the text
- **LaTeX Class File**: `neurips_2024.sty` (updated annually)
- **Supplementary Material**:
  - Providing code is strongly encouraged (GitHub or anonymous repository for review)
  - Extra experiments, proofs
  - Does not count toward the page limit

**LaTeX Template**: `assets/journals/neurips_article.tex`

**Submission Notes**:
- Use the official style file (updated annually)
- The first page must include the Paper ID (automatically generated during the submission process)
- Include a "broader impact" statement (requirements vary by year)
- Reproducibility checklist must be completed

**Official Website**: https://neurips.cc/

---

### ICML (International Conference on Machine Learning)

**Conference Type**: Top-tier machine learning conference  
**Frequency**: Annual (July)

**Formatting Requirements**:
- **Page Limit**:
  - Main Text: 8 pages (excluding references and appendix)
  - References: Unlimited
  - Appendix: Unlimited (optional)
- **Layout**: Double-column
- **Font**: Times, 10pt
- **Line Spacing**: Single-spaced
- **Margins**: 1 inch on all sides
- **Paper Size**: US Letter
- **Anonymization**: **Must** be anonymous (double-blind)
- **Citations**: Numbered or Author-Year (must be consistent)
- **Figures**: High resolution, colorblind-safe palettes recommended
- **LaTeX Class File**: `icml2024.sty` (updated annually)
- **Supplementary Material**: Strongly encouraged (code, data, appendix)

**LaTeX Template**: `assets/journals/icml_article.tex`

**Submission Notes**:
- Must use the official ICML style file
- Include reproducibility checklist
- Provide ethics statement where applicable

**Official Website**: https://icml.cc/

---

### ICLR (International Conference on Learning Representations)

**Conference Type**: Top-tier deep learning conference  
**Frequency**: Annual (April/May)

**Formatting Requirements**:
- **Page Limit**:
  - Main Text: 8 pages (excluding references, appendix, and ethics statement)
  - References: Unlimited
  - Appendix: Unlimited
- **Layout**: Double-column
- **Font**: Times, 10pt
- **Anonymization**: **Must** be anonymous (double-blind)
- **Citations**: Numbered [1] or Author-Year
- **LaTeX Class File**: `iclr2024_conference.sty`
- **Supplementary Material**: Code and data encouraged (anonymous GitHub)
- **Open Review**: Review comments and responses will be public after the decision is released

**LaTeX Template**: `assets/journals/iclr_article.tex`

**Unique Features**:
- Uses the OpenReview platform (transparent review process)
- Discussion between authors and reviewers is possible during the review period
- Camera-ready version can exceed 8 pages

**Official Website**: https://iclr.cc/

---

### CVPR (Computer Vision and Pattern Recognition)

**Conference Type**: Top-tier computer vision conference  
**Frequency**: Annual (June)

**Formatting Requirements**:
- **Page Limit**:
  - Main Text: 8 pages (including figures, excluding references)
  - References: Unlimited (separate section)
- **Layout**: Double-column
- **Font**: Times Roman, 10pt
- **Anonymization**: **Must** be anonymous (double-blind)
  - Blur faces in images if necessary
  - Anonymize datasets that might reveal identity
- **Paper Size**: US Letter
- **Citations**: Numbered [1]
- **Figures**: High resolution, can be in color
- **LaTeX Template**: Official CVPR template (updated annually)
- **Supplementary Material**:
  - Video demonstrations encouraged
  - Extra results, code
  - All supplementary files limited to 100 MB

**LaTeX Template**: `assets/journals/cvpr_article.tex`

**Official Website**: https://cvpr.thecvf.com/

---

### AAAI (Association for the Advancement of Artificial Intelligence)

**Conference Type**: Major AI conference  
**Frequency**: Annual (February)

**Formatting Requirements**:
- **Page Limit**:
  - Technical Papers: 7 pages (excluding references)
  - References: Unlimited
- **Layout**: Double-column
- **Font**: Times Roman, 10pt
- **Anonymization**: **Must** be anonymous (double-blind)
- **Paper Size**: US Letter
- **Citations**: Multiple styles accepted (must remain consistent)
- **LaTeX Template**: Official AAAI style
- **Supplementary Material**: Optional appendix

**LaTeX Template**: `assets/journals/aaai_article.tex`

**Official Website**: https://aaai.org/conference/aaai/

---

### IJCAI (International Joint Conference on Artificial Intelligence)

**Conference Type**: Major AI conference  
**Frequency**: Annual

**Formatting Requirements**:
- **Page Limit**: 7 pages (excluding references)
- **Layout**: Double-column
- **Font**: Times, 10pt
- **Anonymization**: **Mandatory**
- **LaTeX Template**: Official IJCAI style

---

## Computer Science

### ACM CHI (Human-Computer Interaction)

**Conference Type**: Premier HCI conference  
**Frequency**: Annual (April/May)

**Formatting Requirements**:
- **Page Limit**:
  - Papers: 10 pages (excluding references)
  - Late-Breaking Work: 4 pages
- **Layout**: Single-column ACM format
- **Font**: Depends on ACM template
- **Anonymization**: **Mandatory** for the Papers track
- **LaTeX Class File**: `acmart` using the CHI conference format
- **Citations**: ACM style (numbered or Author-Year)
- **Figures**: High quality, accessibility must be considered
- **Accessibility**: Alt text for images is encouraged

**LaTeX Template**: `assets/journals/chi_article.tex`

**Official Website**: https://chi.acm.org/

---

### SIGKDD (Knowledge Discovery and Data Mining)

**Conference Type**: Top-tier data mining conference  
**Frequency**: Annual (August)

**Formatting Requirements**:
- **Page Limit**:
  - Research Track: 9 pages (excluding references)
  - Applied Data Science Track: 9 pages
- **Layout**: Double-column
- **LaTeX Class File**: `acmart` (sigconf format)
- **Font**: ACM template default
- **Anonymization**: **Must** be anonymous (double-blind)
- **Citations**: ACM numbered style
- **Supplementary Material**: Code and data submission encouraged

**LaTeX Template**: `assets/journals/kdd_article.tex`

**Official Website**: https://kdd.org/

---

### EMNLP (Empirical Methods in Natural Language Processing)

**Conference Type**: Top-tier NLP conference  
**Frequency**: Annual (November/December)

**Formatting Requirements**:
- **Page Limit**:
  - Long Papers: 8 pages (+ unlimited references and appendix)
  - Short Papers: 4 pages (+ unlimited references)
- **Layout**: Double-column
- **Font**: Times New Roman, 11pt
- **Anonymization**: **Must** be anonymous (double-blind)
  - Must not include author names or affiliations
  - Self-citations should be anonymized
- **Paper Size**: US Letter or A4
- **Citations**: ACL-like name style
- **LaTeX Template**: Official ACL/EMNLP style
- **Supplementary Material**: Unlimited appendix, code submission encouraged

**LaTeX Template**: `assets/journals/emnlp_article.tex`

**Official Website**: https://www.emnlp.org/

---

### ACL (Association for Computational Linguistics)

**Conference Type**: Premier NLP conference  
**Frequency**: Annual (July)

**Formatting Requirements**:
- **Page Limit**: Long papers 8 pages, short papers 4 pages, excluding references
- **Layout**: Double-column
- **Font**: Times, 11pt
- **Anonymization**: **Mandatory**
- **LaTeX Template**: Official ACL style (acl.sty)

**LaTeX Template**: `assets/journals/acl_article.tex`

---

### USENIX Security Symposium

**Conference Type**: Top-tier security conference  
**Frequency**: Annual (August)

**Formatting Requirements**:
- **Page Limit**:
  - Papers: No strict limit (usually 15-20 pages including everything)
  - Preference given to well-written, concise papers
- **Layout**: Double-column
- **Font**: Times, 10pt
- **Anonymization**: **Must** be anonymous (double-blind)
- **LaTeX Template**: Official USENIX template
- **Citations**: Numbered
- **Paper Size**: US Letter

**LaTeX Template**: `assets/journals/usenix_article.tex`

**Official Website**: https://www.usenix.org/conference/usenixsecurity

---

### SIGIR (Information Retrieval)

**Conference Type**: Top-tier information retrieval conference  
**Frequency**: Annual (July)

**Formatting Requirements**:
- **Page Limit**:
  - Long Papers: 10 pages (excluding references)
  - Short Papers: 4 pages (excluding references)
- **Layout**: Single-column ACM format
- **LaTeX Class File**: `acmart` (sigconf)
- **Anonymization**: **Mandatory**
- **Citations**: ACM style

**LaTeX Template**: `assets/journals/sigir_article.tex`

---

## Biology and Bioinformatics

### ISMB (Intelligent Systems for Molecular Biology)

**Conference Type**: Top-tier computational biology conference  
**Frequency**: Annual (July)

**Formatting Requirements**:
- **Publication**: Proceedings are published in the *Bioinformatics* journal
- **Page Limit**:
  - Usually 7-8 pages (including figures and references)
- **Layout**: Double-column
- **Font**: Times, 10pt
- **Citations**: Numbered (Oxford style similar to Bioinformatics journal)
- **LaTeX Template**: Oxford Bioinformatics template
- **Anonymization**: **Not required** (single-blind)
- **Figures**: High resolution, color accepted
- **Supplementary Material**: Extra data/methods encouraged

**LaTeX Template**: `assets/journals/ismb_article.tex`

**Official Website**: https://www.iscb.org/ismb

---

### RECOMB (Research in Computational Molecular Biology)

**Conference Type**: Top-tier computational biology conference  
**Frequency**: Annual (April/May)

**Formatting Requirements**:
- **Publication**: Proceedings are published as Springer LNCS (Lecture Notes in Computer Science)
- **Page Limit**:
  - Extended Abstracts: 12-15 pages (including references)
- **Layout**: Single-column
- **Font**: Based on Springer LNCS template
- **LaTeX Class File**: `llncs` (Springer)
- **Citations**: Numbered or Author-Year
- **Anonymization**: **Must** be anonymous (double-blind)
- **Supplementary Material**: Appendix can be submitted

**LaTeX Template**: `assets/journals/recomb_article.tex`

**Official Website**: https://www.recomb.org/

---

### PSB (Pacific Symposium on Biocomputing)

**Conference Type**: Biomedical informatics conference  
**Frequency**: Annual (January)

**Formatting Requirements**:
- **Page Limit**: 12 pages (including figures and references)
- **Layout**: Single-column
- **Font**: Times, 11pt
- **Margins**: 1 inch on all sides
- **Citations**: Numbered
- **Anonymization**: **Not required**
- **Figures**: Embedded in the main text
- **LaTeX Template**: Official PSB template

**LaTeX Template**: `assets/journals/psb_article.tex`

**Official Website**: https://psb.stanford.edu/

---

## Engineering

### IEEE International Conference on Robotics and Automation (ICRA)

**Formatting Requirements**:
- **Page Limit**: 8 pages (including figures and references)
- **Layout**: Double-column
- **Font**: Times, 10pt
- **LaTeX Class File**: IEEEtran
- **Citations**: IEEE style [1]
- **Anonymization**: **Mandatory** for initial submission
- **Video**: Optional video submission encouraged

**LaTeX Template**: `assets/journals/icra_article.tex`

---

### IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)

**Format**: Same as ICRA (IEEE Robotics template)

---

### International Conference on Computer-Aided Design (ICCAD)

**Formatting Requirements**:
- **Page Limit**: 8 pages
- **Layout**: Double-column
- **LaTeX Class File**: IEEE template
- **Citations**: IEEE style

---

### Design Automation Conference (DAC)

**Formatting Requirements**:
- **Page Limit**: 6 pages
- **Layout**: Double-column
- **Font**: Times, 10pt
- **LaTeX Class File**: ACM or IEEE template (check annual guidelines)

---

## Multidisciplinary

### AAAS Annual Meeting

**Conference Type**: General science conference  
**Format**: Varies by specific symposium (usually extended abstracts)

---

## Quick Reference Table

| Conference | Pages | Layout | Blind Review | Citation Style | Template |
|------------|-------|--------|-------|-----------|----------|
| **NeurIPS** | 8 + Ref | Double-column | Double-blind | [1] | `neurips_article.tex` |
| **ICML** | 8 + Ref | Double-column | Double-blind | [1] | `icml_article.tex` |
| **ICLR** | 8 + Ref | Double-column | Double-blind | [1] | `iclr_article.tex` |
| **CVPR** | 8 + Ref | Double-column | Double-blind | [1] | `cvpr_article.tex` |
| **AAAI** | 7 + Ref | Double-column | Double-blind | Various | `aaai_article.tex` |
| **CHI** | 10 + Ref | Single-column | Double-blind | ACM | `chi_article.tex` |
| **SIGKDD** | 9 + Ref | Double-column | Double-blind | ACM [1] | `kdd_article.tex` |
| **EMNLP** | 8 + Ref | Double-column | Double-blind | Name | `emnlp_article.tex` |
| **ISMB** | 7-8 pages | Double-column | Single-blind | [1] | `ismb_article.tex` |
| **RECOMB** | 12-15 pages | Single-column | Double-blind | Springer | `recomb_article.tex` |

---

## General Conference Submission Guidelines

### Anonymization Best Practices (Double-Blind Review)

**Remove**:
- Author names, affiliations, and emails from the title page
- Acknowledgments section
- Funding information that reveals identity
- Any "our previous research" citations that make identity obvious

**Anonymize**:
- Self-citations: Change "Smith et al. [5]" to "Anonymous et al. [5]" or "Prior work [5]"
- Institutional details: Change "our university" to "a large research university"
- Dataset names if they reveal identity

**Maintain Anonymity**:
- Code repositories (use anonymous GitHub for review)
- Supplementary materials
- Any URLs or links

### Supplementary Material

**Commonly Included Content**:
- Source code (GitHub repository, zip file)
- Extra experimental results
- Proofs and derivations
- Extended related work
- Dataset descriptions
- Video demonstrations
- Interactive demos

**Best Practices**:
- Keep supplementary material well-organized
- Clearly reference supplementary material in the main text
- Ensure supplementary material for double-blind review is anonymized
- Check file size limits (usually 50-100 MB)

### Camera-Ready Preparation

After acceptance:
1. **De-anonymize**: Add author names and affiliations
2. **Add Acknowledgments**: Funding, contributions
3. **Copyright**: Add conference copyright statement
4. **Formatting**: Follow specific camera-ready guidelines
5. **Page Limit**: May allow an extra 1-2 pages (check guidelines)
6. **PDF/A Compliance**: Some conferences require PDF/A format

### Accessibility Considerations

**Applicable to all conferences**:
- Use colorblind-safe color schemes
- Ensure sufficient contrast
- Provide alt text for figures (if supported)
- Use clear, legible fonts
- Avoid relying solely on color for differentiation

---

## Common Mistakes to Avoid

1. **Wrong Style File**: Using an outdated conference style file
2. **Violating Page Limits**: Figures causing the main text to exceed length
3. **Font Size Manipulation**: Shrinking fonts to fit more content
4. **Margin Adjustments**: Modifying margins to gain more space
5. **Anonymization Failure**: Accidentally revealing identity in double-blind review
6. **Missing References**: Failing to cite relevant prior work
7. **Low-Quality Figures**: Images that are blurry or illegible
8. **Inconsistent Formatting**: Different sections using different styles

---

## Obtaining Official Templates

**Where to find official templates**:
1. **Conference Website**: Check "Call for Papers" or "Author Instructions"
2. **GitHub**: Many conferences host templates on GitHub
3. **Overleaf**: Overleaf has many official templates available
4. **CTAN**: LaTeX class files are often in the CTAN repository

**Template Naming**:
- Conferences usually update templates annually
- Use the template for the corresponding year (e.g., `neurips_2024.sty`)
- Distinguish between "camera-ready" and "submission" versions

---

## Notes

1. **Annual Updates**: Conference requirements change; always check the CFP (Call for Papers) for the current year
2. **Deadline Types**: 
   - Abstract deadline (usually 1 week before the paper deadline)
   - Paper deadline (usually a hard deadline with no extensions)
   - Supplementary material deadline (may be a few days after the paper deadline)
3. **Time Zones**: Note the time zone for deadlines (usually AOE - Anywhere on Earth)
4. **Rebuttal**: Many conferences have an author rebuttal/response phase
5. **Dual Submission**: Check conference policies regarding parallel submissions
6. **Poster/Oral**: Presentation format is usually announced after acceptance

## Conference Tiers (Informal)

**Machine Learning**:
- **Tier 1**: NeurIPS, ICML, ICLR
- **Tier 2**: AAAI, IJCAI, UAI

**Computer Vision**:
- **Tier 1**: CVPR, ICCV, ECCV

**Natural Language Processing**:
- **Tier 1**: ACL, EMNLP, NAACL

**Bioinformatics**:
- **Tier 1**: RECOMB, ISMB
- **Tier 2**: PSB, WABI

(Tiers are informal and field-dependent; not official rankings)