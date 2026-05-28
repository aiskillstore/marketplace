# Experimental Design Patterns

## General Methods for Scientific Hypothesis Testing

This reference guide provides patterns and frameworks for designing experiments across scientific fields. Use these patterns to develop rigorous testing protocols for generated hypotheses.

**Note on Report Structure:** When generating hypothesis reports, mention only key experimental approaches (e.g., "in vivo knockout study" or "prospective cohort design") in the main hypothesis box. Include full experimental protocols, including detailed methods, controls, sample sizes, statistical approaches, feasibility assessments, and resource requirements, in **Appendix B: Detailed Experimental Design**.

## Design Selection Framework

Select experimental approaches based on the following dimensions:
- **Nature of Hypothesis:** Mechanistic, causal, correlational, descriptive
- **Study System:** In vitro, in vivo, in silico, observational
- **Feasibility:** Time, cost, ethics, technical capability
- **Required Evidence:** Proof of concept, causal demonstration, quantitative relationship

## Laboratory Experimental Design

### In Vitro Experiments

**Applicability:** Testing molecular, cellular, or biochemical mechanisms in controlled systems.

**Common Patterns:**

#### 1. Dose-Response Studies
- **Purpose:** To establish a quantitative relationship between input and effect.
- **Design:** Testing multiple concentrations/doses of an intervention.
- **Key Elements:**
  - Negative control (no treatment)
  - Positive control (treatment with known effect)
  - Multiple dose levels (typically 5-8 points)
  - Technical replicates (≥3 per condition)
  - Appropriate statistical analysis (curve fitting, IC50/EC50 determination)

**Application Example:**
"To test if compound X inhibits enzyme Y, measure enzyme activity at compound X concentrations of 0, 1, 10, 100, 1000 nM, with n=3 replicates per dose."

#### 2. Gain/Loss of Function Studies
- **Purpose:** To determine the causal role of a specific component.
- **Design:** Increasing (overexpression) or removing (knockout/knockdown) a component.
- **Key Elements:**
  - Wild-type control
  - Gain-of-function condition (overexpression, constitutive activation)
  - Loss-of-function condition (knockout, knockdown, inhibition)
  - Rescue experiment (restoring function to the loss-of-function state)
  - Measurement of downstream effects

**Application Example:**
"Test if protein X causes phenotype Y by: (1) knocking out X and observing loss of phenotype, (2) overexpressing X and observing enhanced phenotype, and (3) rescuing the knockout line by re-expressing X."

#### 3. Time-Course Studies
- **Purpose:** To understand temporal dynamics and the sequence of events.
- **Design:** Measuring outcomes at multiple time points.
- **Key Elements:**
  - Time 0 baseline
  - Early time points (to capture rapid changes)
  - Intermediate time points
  - Late time points (steady state)
  - Sufficient replicates at each time point

**Application Example:**
"Measure protein phosphorylation at 0, 5, 15, 30, 60, and 120 minutes post-stimulation to determine peak activation timing."

### In Vivo Experiments

**Applicability:** Testing hypotheses in whole organisms to assess systemic, physiological, or behavioral effects.

**Common Patterns:**

#### 4. Between-Subjects Designs
- **Purpose:** To compare different groups receiving different treatments.
- **Design:** Randomly assigning subjects to treatment groups.
- **Key Elements:**
  - Randomization
  - Appropriate sample size (power analysis)
  - Control groups (vehicle, sham, or standard treatment)
  - Blinding (single or double-blind)
  - Standardization of conditions across groups

**Application Example:**
"Randomly assign 20 mice to either a vehicle control or drug treatment group, measuring tumor size weekly for 8 weeks, with investigators blinded to the groupings."

#### 5. Within-Subjects Designs / Repeated Measures
- **Purpose:** Using each subject as its own control to reduce inter-individual variability.
- **Design:** Measuring the same subject under multiple conditions or time points.
- **Key Elements:**
  - Baseline measurement
  - Counterbalancing (if order effects are possible)
  - Washout periods (for sequential treatments)
  - Appropriate statistical methods for repeated measures

**Application Example:**
"Measure cognitive performance in the same cohort of participants at baseline, after a training intervention, and at a 3-month follow-up."

#### 6. Factorial Designs
- **Purpose:** To test multiple factors and their interactions simultaneously.
- **Design:** Crossing all levels of multiple independent variables.
- **Key Elements:**
  - Clear main effects and interactions
  - Sufficient power for interaction testing
  - Appropriate full or fractional factorial design

**Application Example:**
"A 2×2 design crossing genotype (wild-type vs. mutant) × treatment (vehicle vs. drug) to test if the drug effect depends on the genotype."

### Computational/Modeling Experiments

**Applicability:** Testing hypotheses about complex systems, making predictions, or when physical experiments are unfeasible.

#### 7. In Silico Simulations
- **Purpose:** To simulate complex systems and test theoretical predictions.
- **Design:** Implementing computational models and varying parameters.
- **Key Elements:**
  - Well-defined model with clear assumptions
  - Parameter sensitivity analysis
  - Validation against known data
  - Generation of predictions for experimental testing

**Application Example:**
"Build an agent-based model of disease spread, varying transmission rates and intervention timing, comparing predictions to empirical epidemiological data."

#### 8. Bioinformatics / Meta-Analysis
- **Purpose:** To test hypotheses using existing datasets.
- **Design:** Analyzing large-scale data or aggregating multiple studies.
- **Key Elements:**
  - Appropriate statistical corrections (multiple testing)
  - Validation in independent datasets
  - Control for confounding factors and batch effects
  - Clear inclusion/exclusion criteria

**Application Example:**
"Test if expression of gene X correlates with survival across 15 cancer datasets (total n>5000 patients) using Cox regression with clinical covariates."

## Observational Study Designs

### When Physical Manipulation is Impossible or Unethical

#### 9. Cross-Sectional Studies
- **Purpose:** To examine associations at a single point in time.
- **Design:** Measuring variables of interest in a population once.
- **Pros:** Fast, inexpensive, determines prevalence.
- **Cons:** Cannot determine temporal sequence or causality.
- **Key Elements:**
  - Representative sampling
  - Standardized measurements
  - Control for confounding variables
  - Appropriate statistical analysis

**Application Example:**
"Survey 1000 adults to test the association between dietary patterns and biomarker X, controlling for age, sex, BMI, and physical activity."

#### 10. Cohort Studies (Prospective/Longitudinal)
- **Purpose:** To establish temporal relationships and potential causal associations.
- **Design:** Following a group of people over time, measuring exposures and outcomes.
- **Pros:** Establishes temporal sequence, calculates incidence.
- **Cons:** Time-consuming, expensive, subject attrition.
- **Key Elements:**
  - Baseline exposure assessment
  - Regular follow-up
  - Minimization of loss to follow-up
  - Consideration of time-varying confounders

**Application Example:**
"Follow 5000 initially healthy individuals for 10 years to test if baseline vitamin D levels predict the incidence of cardiovascular disease."

#### 11. Case-Control Studies
- **Purpose:** To efficiently study rare outcomes by comparing cases and controls.
- **Design:** Identifying cases with the outcome, selecting matched controls, and comparing exposures.
- **Pros:** Efficient for rare diseases, relatively fast.
- **Cons:** Recall bias, selection bias, cannot calculate incidence.
- **Key Elements:**
  - Clear case definition
  - Appropriate control selection (matching or statistical adjustment)
  - Retrospective exposure assessment
  - Control for confounding factors

**Application Example:**
"Compare 200 patients with rare disease X to 400 matched controls without X to test if early-life exposure Y differs between groups."

## Clinical Trial Designs

#### 12. Randomized Controlled Trials (RCTs)
- **Purpose:** The gold standard for testing interventions in humans.
- **Design:** Randomly assigning participants to treatment or control groups.
- **Key Elements:**
  - Randomization (simple, block, or stratified)
  - Allocation concealment
  - Blinding (participant, provider, assessor)
  - Intention-to-treat (ITT) analysis
  - Pre-registered protocol and analysis plan

**Application Example:**
"A double-blind RCT: 300 patients randomly assigned to receive drug X or placebo for 12 weeks, measuring symptom improvement as the primary outcome."

#### 13. Crossover Trials
- **Purpose:** Each participant receives all treatments in sequence.
- **Design:** Participants cross over from one treatment to another with a washout period in between.
- **Pros:** Reduces inter-individual variability, requires fewer participants.
- **Cons:** Order effects, requires reversible disease state, longer duration.
- **Key Elements:**
  - Sufficient washout period
  - Randomized treatment order
  - Assessment of carryover effects

**Application Example:**
"A crossover trial: participants receive treatment A for 4 weeks, washout for 2 weeks, then receive treatment B for 4 weeks (order randomized)."

## Advanced Design Considerations

### Sample Size and Statistical Power

**Core Questions:**
- What effect size is meaningful to detect?
- Which statistical test will be used?
- What are the appropriate Alpha (significance level) and Beta (power)?
- What is the expected variability in measurements?

**General Guidelines:**
- Perform formal power analysis before the experiment.
- Pilot studies: minimum n≥10 per group.
- Definitive studies: target power ≥80%.
- Account for potential attrition in longitudinal studies.

### Controls

**Types of Controls:**
- **Negative Control:** No intervention (baseline).
- **Positive Control:** Intervention with known effect (validates system efficacy).
- **Vehicle Control:** Delivery medium without the active ingredient.
- **Sham Control:** Mimics the intervention without the active component (e.g., sham surgery).
- **Historical Control:** Previous data (weakest, avoid if possible).

### Blinding

**Levels:**
- **Open-label:** No blinding (acceptable for objective metrics).
- **Single-blind:** Participants are blinded (reduces placebo effect).
- **Double-blind:** Participants and experimenters are blinded (reduces assessment bias).
- **Triple-blind:** Participants, experimenters, and analysts are blinded (strongest evidence).

### Replication

**Technical Replicates:** Multiple measurements of the same sample.
- Reduces measurement error.
- Typically 2-3 replicates are sufficient.

**Biological Replicates:** Independent samples/subjects.
- Addresses biological variability.
- Essential for generalizing results.
- Minimum: n≥3; recommended n≥5-10 per group.

**Experimental Replication:** Repeating the entire experiment.
- Validates findings across time, equipment, and operators.
- The gold standard for confirming results.

### Confound Control

**Strategies:**
- **Randomization:** Distributes confounders evenly across groups.
- **Matching:** Pairs similar subjects across different conditions.
- **Blocking:** Groups by confounder, then randomizes within blocks.
- **Statistical Adjustment:** Measures confounders and adjusts for them in analysis.
- **Standardization:** Keeps experimental conditions constant across groups.

## Choosing the Right Design

**Decision Tree:**

1. **Can variables be manipulated?**
   - Yes → Experimental design (RCT, Lab experiment)
   - No → Observational design (Cohort, Case-control, Cross-sectional)

2. **What is the study system?**
   - Cells/Molecules → In vitro
   - Whole organisms → In vivo
   - Humans → Clinical trial or observational study
   - Complex systems → Computational modeling

3. **What is the primary goal?**
   - Mechanism → Gain/Loss of function, Dose-response
   - Causality → RCT, well-controlled cohort study
   - Association → Cross-sectional, Case-control
   - Prediction → Modeling, Machine learning
   - Temporal dynamics → Time-course, Longitudinal study

4. **What are the constraints?**
   - Limited time → Cross-sectional, In vitro
   - Limited budget → In silico, Observational
   - Ethical concerns → Observational, In vitro
   - Rare outcomes → Case-control, Meta-analysis

## Integrating Multiple Approaches

Robust hypothesis testing often combines multiple designs:

**Example: Testing if the microbiome affects cognitive function**
1. **Observational:** Cohort study showing association between microbiome composition and cognition.
2. **Animal Model:** Germ-free mice receiving microbiome transplants show cognitive changes.
3. **Mechanism:** In vitro studies showing microbial metabolites affect neuronal function.
4. **Clinical Trial:** RCT of a probiotic intervention to improve cognitive scores.
5. **Computational:** Model predicting which microbiome features influence cognition.

**Triangulation Approach:**
- Each design addresses different facets/limitations.
- Convergent evidence from multiple methods strengthens causal claims.
- Start with observational/in vitro and move toward definitive causal tests.

## Common Pitfalls

- Insufficient sample size (underpowered).
- Lack of appropriate controls.
- Failure to account for confounding variables.
- Use of inappropriate statistical tests.
- P-hacking or multiple testing without correction.
- Lack of blinding in subjective assessments.
- Failure to replicate experimental results.
- Failure to pre-register analysis plans (for clinical trials).

## Practical Application in Hypothesis Testing

When designing experiments to test a hypothesis:

1. **Match Design to Hypothesis Details:** Causal claims require experimental manipulation; association studies can use observational designs.
2. **Start Simple:** Use simple designs for pilots before increasing complexity.
3. **Plan Controls Carefully:** Controls validate the system and isolate specific effects.
4. **Consider Feasibility:** Balance ideal design with practical constraints.
5. **Plan Multiple Experiments:** Rarely does a single experiment definitively prove a hypothesis.
6. **Pre-specify Analysis:** Determine statistical tests before data collection.
7. **Build in Validation:** Independent replication, orthogonal methods, convergent evidence.