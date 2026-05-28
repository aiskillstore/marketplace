#!/usr/bin/env python3
"""IACUC Protocol Drafter (ID: 105)

Write an application for Animal Experimentation Ethics (IACUC), focusing on the argumentation part of the 3Rs principles.

3Rs principle:
- Replacement: Use non-animal methods to replace live animal testing
- Reduction: using the minimum number of animals to achieve effective results
- Refinement: Reduce animal pain and stress"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional


class IACUCProtocolDrafter:
    """IACUC application drafter"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate_input()
    
    def validate_input(self) -> None:
        """Verify input data integrity"""
        required_fields = ["title", "principal_investigator", "species", "number_of_animals"]
        missing = [f for f in required_fields if f not in self.data]
        if missing:
            raise ValueError(f"Missing required field: {', '.join(missing)}")
    
    def generate_protocol(self) -> str:
        """Generate a complete IACUC application"""
        sections = [
            self._generate_header(),
            self._generate_project_summary(),
            self._generate_three_rs_section(),
            self._generate_animal_procedures(),
            self._generate_veterinary_care(),
            self._generate_humane_endpoints(),
            self._generate_references(),
        ]
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate header section"""
        institution = self.data.get("institution", "[Organization name]")
        return f"""================================================================================
                    IACUC English
================================================================================

Organization name: {institution}
Application date: {datetime.now().strftime('%Y year %m month %d day')}

================================================================================
"""
    
    def _generate_project_summary(self) -> str:
        """Generate project summary"""
        title = self.data.get("title", "[experiment title]")
        pi = self.data.get("principal_investigator", "[researcher]")
        species = self.data.get("species", "[species]")
        num_animals = self.data.get("number_of_animals", 0)
        pain_category = self.data.get("pain_category", "B")
        procedure = self.data.get("procedure_description", "[Program description]")
        
        return f"""one、Project basic information

1.1 Experiment title
    {title}

1.2 Principal Investigator (Principal Investigator)
    {pi}

1.3 Laboratory animal information
    - Species: {species}
    - quantity: {num_animals} Only
    - USDA pain categories (USDA Pain Category): {pain_category}

1.4 Overview of Experimental Procedures
    {procedure}
"""
    
    def _generate_three_rs_section(self) -> str:
        """Generate 3Rs principle argumentation part - core content"""
        justification = self.data.get("justification", {})
        
        replacement = justification.get("replacement", {})
        reduction = justification.get("reduction", {})
        refinement = justification.get("refinement", {})
        
        return f"""two、3Rs principled argument (Three Rs Justification)

2.1 substitution principle (Replacement)

2.1.1 Alternatives considered
    {self._format_list(replacement.get("alternatives_considered", ["none"]))}

2.1.2 Reasons why live animals must be used
    {replacement.get("why_animals_needed", "[Please explain in detail why non-animal methods cannot meet experimental needs]")}

    scientific basis:
    - This study requires observation of complete physiological system responses，Not possible with cell culture or computer simulations
    - Research involving the interactions of multiple organ systems，Requires complete organism model
    - Relevant alternative method literature has been reviewed，Confirm that there is currently no suitable alternative

2.1.3 Proof of literature search
    A systematic literature search was conducted，The search strategy is as follows:
    - database: PubMed, Web of Science, 3Rs Alternativesdatabase
    - keywords: Alternative method、In vitro experiments、{self.data.get('species', '')} Model
    - Search results: No complete replacement for live animals has been found

--------------------------------------------------------------------------------

2.2 reduction principle (Reduction)

2.2.1 Sample size calculation
    {reduction.get("sample_size_calculation", "[Calculation of minimum sample size based on statistical methods]")}

    Specific calculation:
    - Statistical test type: [double samplettest/ANOVAwait]
    - effect size (Effect Size): [numerical value]
    - significance level (α): 0.05
    - Test effectiveness (Power, 1-β): 0.80
    - consider10-15%The final number of animals is determined after the shedding rate

2.2.2 Strategies to reduce animal populations
    {reduction.get("minimization_strategies", "[Describe how to minimize animal use]")}

    Implementation measures:
    - Using a paired experimental design，Reduce the impact of individual differences
    - Use a repeated measures design，Improve statistical performance
    - Optimize experimental process，Reduce experiment failure rate
    - Share control group data with existing study data（if feasible）

--------------------------------------------------------------------------------

2.3 Optimization principles (Refinement)

2.3.1 pain management
    {refinement.get("pain_management", "[Details on pain and stress management measures]")}

    Specific measures:
    - anesthesia plan: [Drug name、dose、Route of administration]
    - analgesic regimen: [Before surgery、intraoperatively、Postoperative analgesia plan]
    - Anesthesia depth monitoring: [Monitoring indicators and methods]
    - Postoperative care: [Insulation、Rehydration、Antibiotic use etc.]

2.3.2 Feeding environment optimization
    {refinement.get("housing_enrichment", "[Describe environmental enrichment measures]")}

    Environmental optimization:
    - English: Cage size and type that meet the natural behavioral needs of the species
    - Enrichment: Provide nest materials、Toy、Social opportunities etc.
    - Feeding conditions: temperature、humidity、Photoperiod adapted to species needs
    - Stocking density: Make sure there is enough space，English

2.3.3 Humane endpoint setting
    {refinement.get("humane_endpoints", "[Clear Humane Endpoints]")}

    humane endpoint criteria:
    - Weight loss beyond baseline weight20%
    - Unable to eat or drink more than24Hour
    - English
    - Unable to stand or extremely weak
    - severe infection symptoms
    - Any condition that causes ongoing pain or suffering

    implement: Immediate euthanasia when any endpoint is reached
"""
    
    def _generate_animal_procedures(self) -> str:
        """Generate animal experiment procedure descriptions"""
        return f"""three、Animal experiment procedures

3.1 animal origin
    - supplier: [AAALACcertified supplier]
    - animal class: [SPF/Ordinary level]
    - health certificate: Request a recent health test report

3.2 animal preparation
    - adaptive feeding: At least7Days of adaptation period
    - Marking method: [ear tag/chip/Dyeing etc.，Choose the least invasive method]
    - Group: random group，Reduce bias

3.3 Detailed description of experimental procedures
    {self.data.get("procedure_description", "[Detailed experimental steps]")}

3.4 euthanasia methods
    - method: [CO2English/Overdose of anesthesia/Cervical dislocation, etc.]
    - in accordance with: AVMAEuthanasia Guide
    - confirm: Follow-up operations can only be carried out after death is confirmed.
"""
    
    def _generate_veterinary_care(self) -> str:
        """Generate veterinary care plan"""
        return """4. Veterinary Care and Monitoring

4.1 Daily monitoring
    - Monitoring frequency: [daily/weekly times]
    - Monitoring indicators: weight, food and water intake, behavioral observations, clinical signs
    - Recording method: standardized record form

4.2 Emergency treatment
    - Emergency contact: [24-hour contact for veterinarian/research staff]
    - Emergency medicines: [equipped with commonly used first aid medicines]
    - Processing process: Discover problems→Notify veterinarian→Assess→Process→Record

4.3 Postoperative care (if applicable)
    - Recovery room: warm, quiet, monitored
    - Frequency of care: [Check every hour/every two hours]
    - Nursing records: body temperature, heart rate, respiration, pain score"""
    
    def _generate_humane_endpoints(self) -> str:
        """Generate detailed humane endpoint descriptions"""
        return """5. Detailed description of humanitarian endpoints

5.1 The Importance of Humane Endpoints
    Setting clear humane endpoints is the core embodiment of the Refinement principle to ensure that scientific goals are achieved
    Strike a balance with animal welfare and avoid unnecessary animal suffering.

5.2 Specific endpoint indicators

    Major Endpoints:
    - Weight loss >20% (no recovery for 3 consecutive days)
    - Continued inability to eat or drink for >24 hours
    - Severe dyspnea, cyanosis
    - Abnormal body temperature (<36°C or >40°C) lasting more than 4 hours
    - Unable to move independently or extremely weak

    Minor Endpoints:
    - Obvious pain behavior (hunched back, huddled, inactive)
    - Self-destructive behavior
    - Unusual aggressive behavior or social withdrawal
    - Surgical site infection that does not improve
    - Tumor volume exceeds preset limit

5.3 Endpoint execution
    - Discovery Indicator: Any human discovery is immediately notified to researchers and veterinarians
    - Assessment confirmation: joint assessment by veterinarians and researchers
    - Execution time: Euthanasia will be carried out within 1 hour after confirmation
    - Recording requirements: Detailed records of discovery time, indicators, and processing procedures

5.4 Exceptions
    If the scientific endpoint conflicts with the humane endpoint, IACUC approval must be obtained in advance and set:
    - Demonstration of scientific necessity
    - Minimal pain prolongation plan
    - Additional monitoring measures
    - Enhanced veterinary supervision"""
    
    def _generate_references(self) -> str:
        """Generate reference list"""
        return """6. References and Basis

6.1 Regulations and Guidance
    - Guide for the Care and Use of Laboratory Animals (8th Edition)
    - AVMA Guidelines for the Euthanasia of Animals
    - Regulations of the People's Republic of China on the Administration of Laboratory Animals
    - USDA Animal Welfare Act and Regulations

6.2 3Rs resources
    - NC3Rs (National Center for the Replacement, Refinement and Reduction of Animals in Research)
    - ALTBIB: Alternatives to Animal Testing (NIH)
    - FRAME (Fund for the Replacement of Animals in Medical Experiments)
    - 3Rs Center Utrecht Life Sciences

6.3 Related literature
    - Russell WMS, Burch RL. The Principles of Humane Experimental Technique (1959)
    - [Add relevant scientific literature based on actual experiments]

================================================================================
                              Declaration and signature
================================================================================

I confirm:
1. Have completely read and understood all contents of this application
2. Have the necessary qualifications and experience to perform this experiment
3. Will strictly comply with all conditions and requirements of IACUC approval
4. Ensure that all personnel involved receive appropriate animal experimentation training
5. If there are any changes to the experimental protocol, an amendment application will be submitted in a timely manner

Principal Investigator's Signature: ____________________________ Date: ______________

Signature of Laboratory Director: ____________________________ Date: ______________

================================================================================"""
    
    @staticmethod
    def _format_list(items: list) -> str:
        """Format list as string"""
        if not items:
            return "none"
        return "\n    ".join(f"- {item}" for item in items)


def create_sample_input() -> Dict[str, Any]:
    """Create sample input data"""
    return {
        "title": "Evaluation of the efficacy and safety of new anti-tumor drugs in tumor-bearing mouse models",
        "principal_investigator": "Professor Zhang",
        "institution": "XX University School of Medicine",
        "species": "Mice (Mus musculus)",
        "number_of_animals": 60,
        "pain_category": "E",
        "procedure_description": "Establish a subcutaneous transplanted tumor model, administer drugs to observe the tumor growth inhibition, and collect blood regularly to detect biochemical indicators.",
        "justification": {
            "replacement": {
                "alternatives_considered": ["In vitro tumor cell culture", "Organoid model", "Computer pharmacokinetic simulation"],
                "why_animals_needed": "Anti-tumor drugs need to evaluate complete in vivo pharmacodynamics, pharmacokinetics and systemic toxicity. In vitro models cannot simulate the complex tumor microenvironment and immune system interactions."
            },
            "reduction": {
                "sample_size_calculation": "Based on the pre-experimental data, the effect size is 0.8, α=0.05, Power=0.8. Use G*Power software to calculate that each group needs 16 animals. Considering the 20% dropout rate, the final group is 20 animals, with a total of 3 groups of 60 animals.",
                "minimization_strategies": "A repeated measures design was used, with each animal serving as its own control; comparison with historical control data to reduce the number of animals in the control group"
            },
            "refinement": {
                "pain_management": "Limit the tumor size to less than 1.5cm in diameter; euthanasia immediately if ulcers occur or affect mobility; local anesthesia is used for blood collection; the minimum effective dose of anesthetic is used",
                "housing_enrichment": "Provide nesting materials and chew toys; group housing to meet social needs; constant temperature and humidity feeding environment; 12-hour circadian rhythm",
                "humane_endpoints": "Weight loss >20%, tumor diameter >1.5cm or ulcers, inability to eat and drink independently, severe cachexia"
            }
        }
    }


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description="IACUC Protocol Drafter - Animal Experimentation Ethics Application Drafting Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  %(prog)s --input protocol.json --output protocol.txt
  %(prog)s --sample > sample_input.json
  cat protocol.json | %(prog)s > output.txt"""
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Enter JSON file path"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (defaults to standard output)"
    )
    
    parser.add_argument(
        "--sample", "-s",
        action="store_true",
        help="Generate sample input JSON file"
    )
    
    args = parser.parse_args()
    
    # Generate example
    if args.sample:
        sample = create_sample_input()
        print(json.dumps(sample, ensure_ascii=False, indent=2))
        return
    
    # Read input
    try:
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Read from standard input
            input_text = sys.stdin.read()
            if not input_text.strip():
                parser.print_help()
                sys.exit(1)
            data = json.loads(input_text)
    except json.JSONDecodeError as e:
        print(f"mistake: JSONParsing failed - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"mistake: Input file not found '{args.input}'", file=sys.stderr)
        sys.exit(1)
    
    # generate agreement
    try:
        drafter = IACUCProtocolDrafter(data)
        protocol = drafter.generate_protocol()
    except ValueError as e:
        print(f"mistake: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"mistake: An error occurred while generating the agreement - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(protocol)
        print(f"English: {args.output}", file=sys.stderr)
    else:
        print(protocol)


if __name__ == "__main__":
    main()
