from typing import Dict, Any, List
from datetime import datetime

class ProtocolTemplateGenerator:
    """
    Unified Protocol Prompt Generator (Agentic Version)
    Generates structured prompts and logic guides for LLM Agents to write clinical study protocols.
    """
    
    def generate_protocol(self, study_info: Dict[str, Any]) -> str:
        study_type = study_info.get('study_type', 'efficacy')
        
        # Build the protocol structure with LLM instructions
        sections = []
        
        # Metadata for LLM context
        sections.append(self._get_llm_system_instruction(study_info))
        
        # 1. Title Page & Synopsis
        sections.append(self._get_title_page_prompt(study_info))
        sections.append(self._get_synopsis_prompt(study_info))
        
        # 2. Introduction
        sections.append(self._get_introduction_prompt(study_info))
        
        # 3. Objectives
        sections.append(self._get_objectives_prompt(study_info))
        
        # 4. Study Design
        sections.append(self._get_design_prompt(study_info))
        
        # 5. Population
        sections.append(self._get_population_prompt(study_info))
        
        # 6. Interventions/Exposure
        sections.append(self._get_interventions_prompt(study_info))
        
        # 7. Procedures
        sections.append(self._get_procedures_prompt(study_info))
        
        # 8. Outcomes
        sections.append(self._get_outcomes_prompt(study_info))
        
        # 9. Statistics (with pre-calculated values)
        sections.append(self._get_statistics_prompt(study_info))
        
        # 10. Admin Sections
        sections.append(self._get_admin_sections_prompt(study_info))
        
        return "\n\n".join(sections)

    def _get_llm_system_instruction(self, info):
        return f"""<!-- LLM SYSTEM INSTRUCTION:
You are an expert Clinical Research Associate (CRA) and Medical Writer.
Your task is to write a comprehensive clinical study protocol based on the following parameters.
Use professional medical terminology, clear logic, and standard ICH-GCP structure.

KEY PARAMETERS:
- Study Type: {info.get('study_type')}
- P (Population): {info.get('picos', {}).get('P')}
- I (Intervention/Index): {info.get('picos', {}).get('I')}
- C (Comparator/Control): {info.get('picos', {}).get('C')}
- O (Outcome): {info.get('picos', {}).get('O')}
- Study Design: {info.get('design_type')}
-->
"""

    def _get_title_page_prompt(self, info):
        return f"""# Clinical Study Protocol

> **[LLM Instruction]**: Generate a Title Page.
> *   **Title**: Create a professional title incorporating the study design, intervention, population, and primary outcome.
> *   **IDs**: Use placeholder 'DRAFT-001' for Protocol ID.
> *   **Date**: Use current date.
> *   **Personnel**: Create placeholders for PI and Institution.
"""

    def _get_synopsis_prompt(self, info):
        return f"""## Synopsis

> **[LLM Instruction]**: Generate a structured Synopsis table.
> *   **Fields**: Title, Phase (if applicable), Design, Population, Sample Size ({info.get('sample_size', {}).get('total_adjusted')} estimated), Duration, Intervention, Primary Outcome.
> *   **Tone**: Concise and factual.
"""

    def _get_introduction_prompt(self, info):
        p = info.get('picos', {}).get('P')
        i = info.get('picos', {}).get('I')
        st = info.get('study_type')
        
        prompt = f"""## 1. Introduction

> **[LLM Instruction]**: Write a 3-4 paragraph introduction.
> 1.  **Disease Burden**: Describe the epidemiology and clinical burden of **{p}**. Cite general knowledge about prevalence/morbidity.
> 2.  **Unmet Need**: """
        
        if st == 'diagnostic':
            prompt += f"Discuss limitations of current diagnostic methods for **{p}** (e.g., invasiveness, low sensitivity)."
        elif st == 'etiology':
            prompt += f"Discuss gaps in understanding risk factors for **{p}**."
        else:
            prompt += f"Discuss limitations of current standard of care for **{p}** (e.g., side effects, lack of efficacy)."
            
        prompt += f"""
> 3.  **Rationale**: Introduce **{i}**. Explain its mechanism/principle and why it is expected to improve outcomes/diagnosis compared to current standards.
> 4.  **Risk/Benefit**: Briefly summarize the potential benefits (e.g., better cure rate, earlier diagnosis) vs. risks, concluding that the trial is ethical.
"""
        return prompt

    def _get_objectives_prompt(self, info):
        return f"""## 2. Objectives

> **[LLM Instruction]**: Define clear Primary, Secondary, and Exploratory objectives.
> *   **Primary**: Focus on **{info.get('picos', {}).get('O')}**. Use verbs like "To evaluate", "To determine".
> *   **Secondary**: Include safety, tolerability, and secondary efficacy endpoints.
> *   **Exploratory**: Include biomarker analysis or subgroup effects if relevant.
"""

    def _get_design_prompt(self, info):
        st = info.get('study_type')
        design = info.get('design_type')
        
        prompt = f"""## 3. Study Design

> **[LLM Instruction]**: Describe the **{design}** design in detail.
> *   **Overview**: Describe the study flow (Screening -> Enrollment -> Intervention -> Follow-up).
"""
        if st == 'efficacy':
            prompt += "> *   **Randomization**: Describe how subjects will be randomized (e.g., 1:1 ratio, IWRS).\n"
            prompt += "> *   **Blinding**: Describe blinding procedures (Double-blind/Single-blind) to minimize bias."
        elif st == 'diagnostic':
            prompt += "> *   **Blinding**: Emphasize that index test readers must be blinded to gold standard results, and vice versa."
        
        return prompt

    def _get_population_prompt(self, info):
        return f"""## 4. Study Population

> **[LLM Instruction]**: Define the eligibility criteria for **{info.get('picos', {}).get('P')}**.
> *   **Sample Size**: State that approximately {info.get('sample_size', {}).get('total_adjusted')} subjects will be enrolled.
> *   **Inclusion Criteria**: List 4-5 key criteria (Informed consent, Age, Confirmed diagnosis, Severity baseline).
> *   **Exclusion Criteria**: List 4-5 key criteria (Contraindications, Comorbidities, Pregnancy, Recent trial participation).
> *   **Withdrawal**: List standard withdrawal criteria (Consent withdrawal, AE, Protocol violation).
"""

    def _get_interventions_prompt(self, info):
        st = info.get('study_type')
        i = info.get('picos', {}).get('I')
        c = info.get('picos', {}).get('C')
        
        header = "Interventions" if st == 'efficacy' else "Assessments"
        
        prompt = f"""## 5. {header}

> **[LLM Instruction]**: Detail the study interventions/tests.
"""
        if st == 'efficacy':
            prompt += f"> *   **Investigational Product**: **{i}**. Describe dosage, route, frequency.\n"
            prompt += f"> *   **Comparator**: **{c}**. Describe matching placebo or standard care.\n"
            prompt += "> *   **Compliance**: How compliance will be monitored (e.g., pill counts)."
        elif st == 'diagnostic':
            prompt += f"> *   **Index Test**: **{i}**. Describe the procedure, equipment, and cut-off definition.\n"
            prompt += f"> *   **Reference Standard**: **{c}**. Describe the gold standard confirmation method."
        else:
            prompt += f"> *   **Exposure Assessment**: How **{i}** will be measured/recorded."
            
        return prompt

    def _get_procedures_prompt(self, info):
        return f"""## 6. Study Procedures

> **[LLM Instruction]**: Outline the Schedule of Activities.
> *   **Visits**: Define key visits (Screening, Baseline, Treatment Visits, End of Study).
> *   **Assessments**: List what happens at each visit (Vitals, Labs, AE check, Efficacy assessment).
"""

    def _get_outcomes_prompt(self, info):
        return f"""## 7. Outcomes

> **[LLM Instruction]**: Define the endpoints clearly.
> *   **Primary Endpoint**: Specific definition of **{info.get('picos', {}).get('O')}** and timepoint of measurement.
> *   **Secondary Endpoints**: List 2-3 relevant secondary outcomes (e.g., QoL, Response Rate).
> *   **Safety Endpoints**: Adverse Events (AEs), SAEs, Lab abnormalities.
"""

    def _get_statistics_prompt(self, info):
        ss = info.get('sample_size', {})
        return f"""## 8. Statistical Analysis

> **[LLM Instruction]**: Describe the statistical plan.
> *   **Sample Size Calculation**:
>     *   Alpha: {ss.get('alpha')}
>     *   Power: {ss.get('power')}
>     *   Dropout rate: {ss.get('dropout_rate')}
>     *   **Calculated N**: {ss.get('total_adjusted')}
> *   **Analysis Sets**: Define ITT/FAS (Full Analysis Set), PP (Per Protocol), and Safety sets.
> *   **Methods**: Describe appropriate tests for the primary outcome (e.g., T-test/ANCOVA for continuous, Chi-square for rates).
"""

    def _get_admin_sections_prompt(self, info):
        return f"""## 9. Administrative & Ethics

> **[LLM Instruction]**: Write standard administrative sections.
> *   **Data Management**: eCRF usage, data validation.
> *   **Ethics**: Declaration of Helsinki, IRB/IEC approval, Informed Consent process.
> *   **Quality Control**: Monitoring plan, SOP adherence.
> *   **Publication**: Policy for publishing results (ICMJE guidelines).
"""

class ProtocolFormatter:
    def format_protocol(self, text):
        return text

    def generate_summary(self, info):
        return f"# Summary\nTitle: {info.get('title')}\nDesign: {info.get('study_type')}"
