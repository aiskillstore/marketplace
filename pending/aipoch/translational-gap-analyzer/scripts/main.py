#!/usr/bin/env python3
"""Translational Gap Analyzer (ID: 209)
Assessing the translational gap between basic research models and human disease"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class DimensionScore:
    """Ratings and concerns for each dimension"""
    score: float  # 0-10, the higher the value, the greater the gap.
    concerns: List[str]
    details: Dict[str, any]


@dataclass
class GapAnalysisReport:
    """Conversion Gap Analysis Report"""
    model: str
    disease: str
    overall_gap_score: float
    risk_level: str
    dimensions: Dict[str, DimensionScore]
    clinical_failure_predictors: List[str]
    recommendations: List[str]


# Knowledge Base: Model-Disease Gap Data
TRANSLATIONAL_KNOWLEDGE = {
    "mouse": {
        "anatomy": {
            "brain_structure": 7.5,
            "organ_size_ratio": 6.0,
            "vascular_pattern": 7.0,
            "immune_organs": 5.5
        },
        "physiology": {
            "lifespan": 9.0,
            "heart_rate": 8.0,
            "body_temperature": 7.5,
            "reproductive_cycle": 8.5
        },
        "metabolism": {
            "drug_clearance": 8.0,
            "cytochrome_p450": 7.5,
            "glucose_metabolism": 6.5,
            "lipid_metabolism": 6.0
        },
        "immune": {
            "innate_immunity": 6.0,
            "adaptive_immunity": 5.5,
            "cytokine_profile": 7.0,
            "microglia_function": 8.5
        },
        "genetics": {
            "gene_conservation": 4.0,
            "regulatory_elements": 7.0,
            "chromosome_structure": 6.5,
            "splice_variants": 7.5
        },
        "behavior": {
            "cognitive_assessment": 8.0,
            "social_behavior": 7.5,
            "motor_function": 5.0,
            "pain_perception": 7.0
        }
    },
    "rat": {
        "anatomy": {
            "brain_structure": 6.5,
            "organ_size_ratio": 5.5,
            "vascular_pattern": 6.0,
            "immune_organs": 5.0
        },
        "physiology": {
            "lifespan": 8.5,
            "heart_rate": 7.5,
            "body_temperature": 7.0,
            "reproductive_cycle": 7.5
        },
        "metabolism": {
            "drug_clearance": 7.5,
            "cytochrome_p450": 7.0,
            "glucose_metabolism": 6.0,
            "lipid_metabolism": 5.5
        },
        "immune": {
            "innate_immunity": 5.5,
            "adaptive_immunity": 5.0,
            "cytokine_profile": 6.5,
            "microglia_function": 7.5
        },
        "genetics": {
            "gene_conservation": 4.5,
            "regulatory_elements": 6.5,
            "chromosome_structure": 6.0,
            "splice_variants": 7.0
        },
        "behavior": {
            "cognitive_assessment": 7.0,
            "social_behavior": 6.5,
            "motor_function": 4.5,
            "pain_perception": 6.5
        }
    },
    "zebrafish": {
        "anatomy": {
            "brain_structure": 8.5,
            "organ_structure": 8.0,
            "vascular_pattern": 7.0,
            "immune_organs": 8.5
        },
        "physiology": {
            "water_vs_air": 9.0,
            "temperature_regulation": 9.0,
            "reproduction": 8.5,
            "regeneration": 7.0
        },
        "metabolism": {
            "drug_metabolism": 8.5,
            "energy_metabolism": 7.5,
            "xenobiotic_metabolism": 8.0
        },
        "immune": {
            "adaptive_immunity": 9.0,
            "innate_immunity": 7.0,
            "inflammation": 7.5
        },
        "genetics": {
            "gene_duplication": 8.5,
            "conservation": 6.0,
            "regeneration_genes": 6.5
        },
        "behavior": {
            "cognitive_assessment": 8.5,
            "social_behavior": 8.0,
            "learning": 8.0
        }
    },
    "cell_line": {
        "anatomy": {
            "tissue_architecture": 9.5,
            "cell_interactions": 9.0,
            "extracellular_matrix": 8.5,
            "3d_structure": 9.0
        },
        "physiology": {
            "systemic_regulation": 10.0,
            "homeostasis": 9.5,
            "stress_response": 7.0
        },
        "metabolism": {
            "culture_medium_effects": 8.5,
            "oxygen_levels": 8.0,
            "nutrient_availability": 7.5
        },
        "immune": {
            "immune_interactions": 9.5,
            "inflammation_context": 9.0
        },
        "genetics": {
            "genetic_drift": 8.0,
            "passage_effects": 8.5,
            "mutation_accumulation": 8.0
        }
    },
    "organoid": {
        "anatomy": {
            "maturation": 7.5,
            "vascularization": 9.0,
            "size_limitations": 8.5,
            "cell_diversity": 6.5
        },
        "physiology": {
            "systemic_integration": 9.5,
            "maturity_level": 7.5,
            "functionality": 7.0
        },
        "metabolism": {
            "nutrient_diffusion": 8.0,
            "waste_removal": 8.5,
            "metabolic_activity": 6.5
        },
        "immune": {
            "immune_component": 8.5,
            "inflammation_modeling": 7.5
        },
        "genetics": {
            "genetic_stability": 6.0,
            "patient_variability": 5.5
        }
    },
    "primate": {
        "anatomy": {
            "brain_structure": 2.5,
            "organ_structure": 3.0,
            "vascular_pattern": 3.5,
            "immune_organs": 3.0
        },
        "physiology": {
            "lifespan": 4.5,
            "reproductive_cycle": 5.0,
            "metabolic_rate": 4.0,
            "body_temperature": 3.0
        },
        "metabolism": {
            "drug_metabolism": 4.5,
            "cytochrome_p450": 4.0,
            "glucose_metabolism": 3.5,
            "lipid_metabolism": 3.5
        },
        "immune": {
            "innate_immunity": 3.5,
            "adaptive_immunity": 3.0,
            "cytokine_profile": 4.0,
            "microglia_function": 3.5
        },
        "genetics": {
            "gene_similarity": 2.5,
            "regulatory_elements": 4.0,
            "chromosome_structure": 3.0
        },
        "behavior": {
            "cognitive_assessment": 4.0,
            "social_behavior": 3.5,
            "emotional_response": 4.5
        }
    }
}


# disease-specific risk factors
DISEASE_SPECIFIC_FACTORS = {
    "alzheimer": {
        "mouse": {
            "pathology_differences": ["Lack of natural tau pathology", "Different Aβ deposition patterns", "Differences in neurodegeneration rates"],
            "genetic_risks": ["APOE4 model limited", "TREM2 functional differences"],
            "immune_factors": ["Microglial reactivity differs", "Differences in neuroinflammation patterns"],
            "drug_targets": ["The amyloid hypothesis has failed many times", "Tau pathology is difficult to replicate"]
        },
        "rat": {
            "pathology_differences": ["tau pathology limited", "Aβ clearance differences"],
            "genetic_risks": ["There are fewer APOE models"],
            "behavioral_differences": ["Limitations of cognitive assessment methods"]
        }
    },
    "parkinson": {
        "mouse": {
            "pathology_differences": ["Lack of natural Lewy bodies", "Dopamine system differences"],
            "genetic_risks": ["LRRK2 mutations have different effects", "Limitations of SNCA overexpression model"],
            "drug_targets": ["Dopamine replacement therapy model is effective but clinically variable"]
        },
        "rat": {
            "toxin_models": ["MPTP model is very different from sporadic PD", "6-OHDA model limitations"],
            "genetic_models": ["Genetic modeling progress is slow"]
        }
    },
    "cancer": {
        "mouse": {
            "immune_factors": ["Differences in the immune system affect the effectiveness of immunotherapy", "Different tumor microenvironments"],
            "metabolic_factors": ["Drug metabolism varies significantly", "Dose conversion is difficult"],
            "genetic_risks": ["Driver mutations are conserved but contextually diverse"]
        },
        "cell_line": {
            "model_limitations": ["lack of microenvironment", "2D vs 3D differences", "cell line evolution"]
        }
    },
    "diabetes": {
        "mouse": {
            "metabolic_factors": ["Differences in insulin resistance mechanisms", "Different fat distribution"],
            "immune_factors": ["Type 1 diabetes autoimmune differences", "Limitations of NOD mice"],
            "drug_targets": ["GLP-1 analogues have been relatively successful", "SGLT2 inhibitor differences"]
        },
        "rat": {
            "metabolic_factors": ["Differences between Zucker diabetic obese rats and human T2D"]
        }
    },
    "autoimmune": {
        "mouse": {
            "immune_factors": ["Differences in immune tolerance mechanisms", "MHC systems are fundamentally different"],
            "drug_targets": ["TNF inhibitors are relatively successful", "B cell targeting differences"],
            "pathology_differences": ["Differences between disease-induced models and spontaneous diseases"]
        }
    },
    "cardiovascular": {
        "mouse": {
            "anatomical_differences": ["Different distribution of coronary arteries", "Differences in myocardial regeneration ability"],
            "physiological_differences": ["Extremely fast heart rate", "Differences in EKG Interpretation"],
            "drug_targets": ["Statins are effective", "Differences in anticoagulant drug metabolism"]
        },
        "rat": {
            "advantages": ["Cardiovascular surgery models are more mature"],
            "differences": ["Still significantly different from clinical"]
        }
    }
}


def normalize_disease_name(disease: str) -> str:
    """standardized disease names"""
    disease_lower = disease.lower().replace("'", "").replace(" ", "_")
    disease_mapping = {
        "alzheimer": "alzheimer",
        "alzheimers": "alzheimer",
        "alzheimers_disease": "alzheimer",
        "parkinson": "parkinson",
        "parkinsons": "parkinson",
        "parkinsons_disease": "parkinson",
        "cancer": "cancer",
        "tumor": "cancer",
        "diabetes": "diabetes",
        "autoimmune": "autoimmune",
        "cardiovascular": "cardiovascular",
        "heart_disease": "cardiovascular"
    }
    return disease_mapping.get(disease_lower, disease_lower)


def get_disease_specific_risks(model: str, disease: str) -> List[str]:
    """Get disease-specific risks"""
    normalized_disease = normalize_disease_name(disease)
    risks = []
    
    if normalized_disease in DISEASE_SPECIFIC_FACTORS:
        disease_data = DISEASE_SPECIFIC_FACTORS[normalized_disease]
        if model in disease_data:
            model_data = disease_data[model]
            for category, items in model_data.items():
                if isinstance(items, list):
                    risks.extend(items)
    
    return risks


def calculate_dimension_score(model: str, dimension: str, focus_areas: List[str]) -> DimensionScore:
    """Calculate the score for a specific dimension"""
    if model not in TRANSLATIONAL_KNOWLEDGE:
        return DimensionScore(score=5.0, concerns=["Unknown model type"], details={})
    
    model_data = TRANSLATIONAL_KNOWLEDGE[model]
    
    if dimension not in model_data:
        return DimensionScore(score=5.0, concerns=["The dimension data is not available"], details={})
    
    dim_data = model_data[dimension]
    scores = list(dim_data.values())
    avg_score = sum(scores) / len(scores) if scores else 5.0
    
    # Identify key concerns
    concerns = []
    for key, value in dim_data.items():
        if value >= 7.0:
            concerns.append(f"{key}: significant difference (score: {value})")
        elif value >= 5.0:
            concerns.append(f"{key}: medium difference (score: {value})")
    
    # If this dimension is the focus, list more detailed concerns
    if dimension in focus_areas:
        concerns = [f"{k}: {v}" for k, v in dim_data.items() if v >= 5.0]
    
    return DimensionScore(
        score=round(avg_score, 1),
        concerns=concerns[:5],  # limited quantity
        details=dim_data
    )


def determine_risk_level(overall_score: float) -> str:
    """Determine risk level"""
    if overall_score >= 8.0:
        return RiskLevel.CRITICAL.value
    elif overall_score >= 6.5:
        return RiskLevel.HIGH.value
    elif overall_score >= 4.0:
        return RiskLevel.MEDIUM.value
    else:
        return RiskLevel.LOW.value


def generate_failure_predictors(model: str, disease: str, dimensions: Dict[str, DimensionScore]) -> List[str]:
    """Generate clinical trial failure predictors"""
    predictors = []
    
    # Identify risks based on dimension scores
    high_gap_dims = [dim for dim, score in dimensions.items() if score.score >= 7.0]
    
    if "immune" in high_gap_dims:
        predictors.append("Research on immune-related mechanisms may be at risk of translation failure")
    if "metabolism" in high_gap_dims:
        predictors.append("Pharmacokinetic differences may lead to inappropriate clinical dosing")
    if "anatomy" in high_gap_dims and model in ["mouse", "rat"]:
        predictors.append("Differences in organ structure may affect drug distribution")
    if "behavior" in high_gap_dims and "alzheimer" in disease.lower():
        predictors.append("Interspecies differences in cognitive assessment methods may mask true efficacy")
    if "genetics" in high_gap_dims:
        predictors.append("Differences in gene regulatory networks may affect target effectiveness")
    
    # Add disease-specific risks
    disease_risks = get_disease_specific_risks(model, disease)
    predictors.extend(disease_risks[:3])  # Up to 3
    
    return predictors if predictors else ["No specific high-risk factors have been identified, but careful assessment is still required"]


def generate_recommendations(model: str, disease: str, dimensions: Dict[str, DimensionScore]) -> List[str]:
    """Generate improvement suggestions"""
    recommendations = []
    
    # Recommendations based on model type
    if model == "mouse":
        if dimensions.get("immune", DimensionScore(0, [], {})).score >= 7.0:
            recommendations.append("Consider using mouse models of humanized immune systems")
        if dimensions.get("metabolism", DimensionScore(0, [], {})).score >= 7.0:
            recommendations.append("In vitro human hepatocyte validation of drug metabolism")
        if dimensions.get("behavior", DimensionScore(0, [], {})).score >= 7.0:
            recommendations.append("Increase behavioral validation in non-human primates")
        recommendations.append("Consider using genetically humanized mice to increase translational relevance")
    
    elif model == "rat":
        recommendations.append("Utilizing Better Behavioral Characteristics of Rats for Cognitive Assessment")
        if dimensions.get("metabolism", DimensionScore(0, [], {})).score >= 6.0:
            recommendations.append("Performing metabolic studies in humanized liver microsomes")
    
    elif model == "zebrafish":
        recommendations.append("Mainly used for high-throughput screening and developmental toxicity testing")
        recommendations.append("Positive results need to be verified in mammalian models")
        recommendations.append("Focus on cardiovascular and neurodevelopmental toxicity assessment")
    
    elif model == "cell_line":
        recommendations.append("Improving physiological relevance using 3D culture or organoid models")
        recommendations.append("Combined with co-culture system to simulate tumor microenvironment")
        recommendations.append("Regularly verify cell line identity and genetic stability")
    
    elif model == "organoid":
        recommendations.append("Focus on organoid maturity and functional assessment")
        recommendations.append("Consider vascularization techniques to improve nutrient supply")
        recommendations.append("Combined with single-cell sequencing to verify cellular heterogeneity")
    
    elif model == "primate":
        recommendations.append("Used as final preclinical validation model")
        recommendations.append("Strictly follow the 3R principles and design experiments rationally")
    
    # Disease-specific recommendations
    normalized_disease = normalize_disease_name(disease)
    if normalized_disease == "alzheimer":
        recommendations.append("Focus on pathological mechanisms beyond Aβ and tau")
        recommendations.append("Pay attention to neuroimmune and microglia research")
    elif normalized_disease == "cancer":
        recommendations.append("Pay attention to tumor microenvironment and immunotherapy evaluation")
        recommendations.append("Consider patient-derived xenograft models (PDX)")
    elif normalized_disease == "autoimmune":
        recommendations.append("Focus on human-specific immune targets")
        recommendations.append("Consider using humanized immune system models")
    
    return recommendations


def analyze_gap(model: str, disease: str, focus_areas: List[str] = None) -> GapAnalysisReport:
    """Perform a conversion gap analysis"""
    if focus_areas is None:
        focus_areas = []
    
    dimensions_to_analyze = focus_areas if focus_areas else [
        "anatomy", "physiology", "metabolism", "immune", "genetics", "behavior"
    ]
    
    dimensions = {}
    total_score = 0
    
    for dim in dimensions_to_analyze:
        dim_score = calculate_dimension_score(model, dim, focus_areas)
        dimensions[dim] = dim_score
        total_score += dim_score.score
    
    overall_score = total_score / len(dimensions) if dimensions else 5.0
    risk_level = determine_risk_level(overall_score)
    
    failure_predictors = generate_failure_predictors(model, disease, dimensions)
    recommendations = generate_recommendations(model, disease, dimensions)
    
    # Convert to serializable format
    serializable_dimensions = {}
    for dim, score in dimensions.items():
        serializable_dimensions[dim] = {
            "score": score.score,
            "concerns": score.concerns,
            "details": score.details
        }
    
    return GapAnalysisReport(
        model=model,
        disease=disease,
        overall_gap_score=round(overall_score, 1),
        risk_level=risk_level,
        dimensions=serializable_dimensions,
        clinical_failure_predictors=failure_predictors,
        recommendations=recommendations
    )


def format_report(report: GapAnalysisReport, output_format: str = "json") -> str:
    """Format report output"""
    if output_format == "json":
        return json.dumps(asdict(report), indent=2, ensure_ascii=False)
    
    elif output_format == "markdown":
        md = f"""# Conversion Gap Analysis Report

## Basic information
- **Model**: {report.model}
- **disease**: {report.disease}
- **overall gap score**: {report.overall_gap_score}/10
- **risk level**: {report.risk_level}

## Assessment in various dimensions
"""
        for dim, data in report.dimensions.items():
            md += f"\n### {dim.capitalize()}\n"
            md += f"- **score**: {data['score']}\n"
            if data['concerns']:
                md += "- **Points of concern**:"
                for concern in data['concerns']:
                    md += f"  - {concern}\n"
        
        md += "## Predictors of clinical trial failure"
        for predictor in report.clinical_failure_predictors:
            md += f"- ⚠️ {predictor}\n"
        
        md += "## Improvement suggestions"
        for rec in report.recommendations:
            md += f"- 💡 {rec}\n"
        
        return md
    
    else:  # table format
        lines = []
        lines.append("=" * 70)
        lines.append(f"Conversion Gap Analysis Report - {report.model} vs {report.disease}")
        lines.append("=" * 70)
        lines.append(f"Overall rating: {report.overall_gap_score}/10 | risk level: {report.risk_level}")
        lines.append("-" * 70)
        lines.append(f"{'Dimensions':<15} {'score':<10} {'main focus'}")
        lines.append("-" * 70)
        
        for dim, data in report.dimensions.items():
            concerns = "; ".join(data['concerns'][:2]) if data['concerns'] else "none"
            lines.append(f"{dim.capitalize():<15} {data['score']:<10} {concerns}")
        
        lines.append("-" * 70)
        lines.append("[Risk warning of clinical trial failure]")
        for i, predictor in enumerate(report.clinical_failure_predictors[:3], 1):
            lines.append(f"  {i}. {predictor}")
        
        lines.append("[Improvement suggestions]")
        for i, rec in enumerate(report.recommendations[:4], 1):
            lines.append(f"  {i}. {rec}")
        
        return "\n".join(lines)


def compare_models(models: List[str], disease: str, focus_areas: List[str] = None) -> str:
    """Compare multiple models"""
    reports = []
    for model in models:
        report = analyze_gap(model, disease, focus_areas)
        reports.append(report)
    
    # Sorting: The lower the score, the better (the smaller the gap)
    reports.sort(key=lambda x: x.overall_gap_score)
    
    output = ["=" * 80]
    output.append(f"Multi-model comparative analysis: {disease}")
    output.append("=" * 80)
    output.append(f"{'Model':<15} {'gap score':<12} {'risk level':<12} {'Recommended sorting'}")
    output.append("-" * 80)
    
    for i, report in enumerate(reports, 1):
        output.append(f"{report.model:<15} {report.overall_gap_score:<12} {report.risk_level:<12} #{i}")
    
    output.append("\n" + "=" * 80)
    output.append("Detailed analysis")
    output.append("=" * 80)
    
    for report in reports:
        output.append(f"\n[{report.model.upper()}]")
        output.append(f"risk level: {report.risk_level} | key questions: {', '.join(report.clinical_failure_predictors[:2])}")
        output.append(f"Main recommendations: {report.recommendations[0] if report.recommendations else 'N/A'}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Translational Gap Analyzer - Assessing the translational gap between basic research models and human disease",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python main.py --model mouse --disease "Alzheimer's" --full
  python main.py --model mouse --disease "Alzheimer's" --quick
  python main.py --models mouse,rat,primate --disease cancer --compare
  python main.py --model mouse --disease diabetes --focus metabolism,immune"""
    )
    
    parser.add_argument("--model", type=str, help="Model type (mouse, rat, zebrafish, cell_line, organoid, primate)")
    parser.add_argument("--models", type=str, help="Multi-model comparison mode, comma separated")
    parser.add_argument("--disease", type=str, required=True, help="Disease name")
    parser.add_argument("--focus", type=str, help="Areas of concern, separated by commas (anatomy, physiology, metabolism, immune, genetics, behavior)")
    parser.add_argument("--full", action="store_true", help="Generate full assessment report")
    parser.add_argument("--quick", action="store_true", help="Rapid risk assessment mode")
    parser.add_argument("--compare", action="store_true", help="Multi-model comparison mode")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--format", type=str, choices=["json", "markdown", "table"], default="table", help="Output format")
    
    args = parser.parse_args()
    
    # Analyze areas of concern
    focus_areas = []
    if args.focus:
        focus_areas = [f.strip() for f in args.focus.split(",")]
    
    # Multi-model comparison mode
    if args.compare or args.models:
        if not args.models:
            print("Error: Comparison models require --models argument", file=sys.stderr)
            sys.exit(1)
        
        models = [m.strip() for m in args.models.split(",")]
        result = compare_models(models, args.disease, focus_areas)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Comparison report saved to: {args.output}")
        else:
            print(result)
        return
    
    # Single model analysis mode
    if not args.model:
        print("Error: Single-model analysis requires --model argument", file=sys.stderr)
        sys.exit(1)
    
    # Perform analysis
    report = analyze_gap(args.model, args.disease, focus_areas)
    
    # Determine output format
    output_format = args.format
    if args.full:
        output_format = "markdown"
    elif args.quick:
        output_format = "table"
    
    result = format_report(report, output_format)
    
    # Output results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Report saved to: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
