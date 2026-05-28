import argparse
import json
import sys
import os
from datetime import datetime
sys.dont_write_bytecode = True

from calculators import DiagnosticCalculator, EfficacyCalculator, EtiologyCalculator, PrognosisCalculator

# Chinese mapping table
PARAM_MAP = {
    # Diagnostic
    "Se": "Sensitivity (Se)",
    "Sp": "Specificity (Sp)",
    "Error": "error tolerance",
    "Prevalence": "Prevalence",
    "Dropout": "shedding rate",
    "AUC": "Area under the curve (AUC)",
    "MarginError": "error tolerance",
    "Pe": "Expected agreement rate (Pe)",
    "MinKappa": "Minimum Kappa value",
    "Factors": "Number of predictors",
    "required_cases_for_se": "Number of cases required based on sensitivity",
    "required_controls_for_sp": "Number of controls required based on specificity",
    "total_sample_size_raw": "Original total sample size (excluding dropouts)",
    "final_sample_size_with_dropout": "Final total sample size (including dropouts)",
    "estimated_cases": "Estimated case group size",
    "estimated_controls": "Estimated number of people in the control group",
    
    # Efficacy & General
    "MeanT": "Experimental group mean",
    "MeanC": "control group mean",
    "St": "Experimental group standard deviation",
    "Sc": "Standard deviation of control group",
    "Pt": "Experimental group rate",
    "Pc": "control group rate",
    "P1": "Group 1 rate",
    "P2": "Group 2 rate",
    "margin": "Margin",
    "n_per_group": "Sample size per group",
    "total_n": "Total sample size (excluding dropouts)",
    "true_n": "Final total sample size (including dropouts)",
    "true_n_per_group": "Final sample size for each group",
    "lower": "confidence interval lower bound",
    "upper": "upper confidence interval",
    
    # Survival
    "accrual_time": "Enrollment time",
    "total_time": "total research time",
    "follow_up_time": "Follow-up time",
    "groupC_survival": "control group survival index",
    "groupT_survival": "Survival index of experimental group",
    "historical_survival": "historical control survival index",
    "group_survival": "Expected survival index of experimental group",
    "total_events": "total number of events required",
    "total_sample": "Total sample size (excluding dropouts)",
    "HR": "Hazard Ratio (HR)",
    "Mc": "Median survival time of control group",
    "Mt": "Median survival time of experimental group",
    "T0": "Enrollment time",
    "T1": "total research time",
    "Hr": "Hazard Ratio (HR)",
    "overall_prob": "total event probability",
    
    # Etiology
    "n_per_group_base": "Basic sample size for each group",
    "pt": "exposure group rate",
    "pc": "Non-exposed group rate",
    
    # Prognosis
    "events_needed": "number of events required",
    "variables_number": "Number of variables",
    "P": "incident rate",
    "training_rate": "Training set proportion",
    "testing_rate": "Test set proportion",
    "final_n": "Final total sample size (including dropouts)",
    
    # Common
    "alpha": "Significance level (α)",
    "beta": "Type II error (β)",
    "power": "Power",
    "ratio": "Proportion between groups",
    "test": "Inspection type"
}

def generate_markdown(data):
    lines = []
    lines.append(f"# Clinical study sample size calculation report")
    lines.append(f"**Generation time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if "error" in data:
        lines.append(f"## mistake\n> {data['error']}")
        return "\n".join(lines)

    # 1. Basic Info
    lines.append("## 1. Basic information")
    mode_cn = data.get('mode_cn') or data.get('mode') or data.get('type') or 'unknown'
    lines.append(f"- **Research Type**: {mode_cn}")
    
    study_name = data.get('study_name')
    if study_name:
        lines.append(f"- **Research name**: {study_name}")
        
    outcome = data.get('outcome')
    if outcome:
        lines.append(f"- **Outcome indicators**: {outcome}")
        
    lines.append("")
    
    # 2. Parameters
    params = data.get('inputs') or data.get('parameters') or data.get('params')
    inferred_keys = data.get('inferred_params', [])
    
    if not params:
        # Collect root keys that are not results or special keys
        special_keys = ['results', 'error', 'mode', 'mode_cn', 'type', 'method', 'description', 'is_single_arm', 'study_name', 'outcome', 'inferred_params']
        params = {k: v for k, v in data.items() if k not in special_keys}
    
    if params:
        lines.append("## 2. Input parameters")
        lines.append("| Parameter | Value | Description | Source |")
        lines.append("|---|---|---|---|")
        for k, v in params.items():
            cn_name = PARAM_MAP.get(k, k)
            # If the value is a floating point number, keep 4 decimal places
            val_str = f"{v:.4f}" if isinstance(v, float) else str(v)
            source = "Intelligent inference" if k in inferred_keys else "user input"
            lines.append(f"| {k} | {val_str} | {cn_name} | {source} |")
        lines.append("")
        
    # 3. Results
    results = data.get('results')
    if results:
        lines.append("## 3. Calculation results")
        lines.append("| Indicator | Value | Description |")
        lines.append("|---|---|---|")
        for k, v in results.items():
            cn_name = PARAM_MAP.get(k, k)
            val_str = f"{v:.4f}" if isinstance(v, float) else str(v)
            lines.append(f"| {k} | {val_str} | {cn_name} |")
        lines.append("")
        
    # 4. Conclusion
    desc = data.get('description')
    if desc:
        lines.append("## 4. Conclusion")
        lines.append(f"> {desc}\n")
        
    return "\n".join(lines)

def save_report(result, output_dir="output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = result.get('mode') or result.get('type') or 'result'
    mode = mode.replace(" ", "_").replace("/", "_").lower()
    filename = f"{mode}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    content = generate_markdown(result)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    return filepath

def infer_parameters(args, mode):
    """Intelligent parameter inference logic
    Returns: (processed parameter dictionary, inferred parameter list)"""
    params = {}
    inferred = []
    
    # Universal default
    default_dropout = 0.1
    default_alpha = 0.05
    default_power = 0.8
    
    # Helper functions: get or infer
    def get_or_infer(key, default_val):
        val = getattr(args, key, None)
        if val is not None:
            params[key] = val
        else:
            params[key] = default_val
            inferred.append(key)
        return params[key]

    if args.study_type == "diagnostic":
        if mode == "sens_spec":
            get_or_infer("se", 0.85)
            get_or_infer("sp", 0.90)
            get_or_infer("error", 0.05)
            get_or_infer("prev", 0.5) # Hypothetical case-control study, half and half
            get_or_infer("dropout", default_dropout)
            
        elif mode == "auc":
            get_or_infer("auc", 0.80)
            get_or_infer("error", 0.05)
            get_or_infer("dropout", default_dropout)
            
        elif mode == "kappa":
            get_or_infer("pe", 0.5)
            get_or_infer("k1", 0.7)
            get_or_infer("dropout", default_dropout)
            
        elif mode == "model":
            get_or_infer("factors", 5)
            get_or_infer("prev", 0.1) # Prevalence of common diseases
            get_or_infer("dropout", default_dropout)

    elif args.study_type == "etiology":
        if mode == "categorical":
            # Assume that the incidence rate in the non-exposed group is 0.1, RR=2.0 -> 0.2 in the exposed group
            get_or_infer("pc", 0.1)
            get_or_infer("pt", 0.2)
            get_or_infer("dropout", default_dropout)
            get_or_infer("x", 1)
            
        elif mode == "survival":
            get_or_infer("t0", 12)
            get_or_infer("t1", 24)
            # It is assumed that the median survival of the control group is 12 months and that of the experimental group is extended to 18 months (HR=0.67)
            get_or_infer("mc", 12)
            get_or_infer("mt", 18) 
            get_or_infer("dropout", default_dropout)
            get_or_infer("x", 1)

    elif args.study_type == "prognosis":
        if mode == "epv":
            get_or_infer("P", 0.1)
            get_or_infer("variables_number", 5)
            get_or_infer("training_rate", 0.7)
            get_or_infer("testing_rate", 0.3)
            get_or_infer("dropout", default_dropout)
            
        elif mode == "logrank":
            get_or_infer("Hr", 2.0) # Double the risk
            get_or_infer("overall_prob", 0.3)
            get_or_infer("T0", 12)
            get_or_infer("T1", 36)
            get_or_infer("dropout", default_dropout)
            get_or_infer("ratio", 1.0)
            
        elif mode == "chisquare":
            # P1=0.1, P2=0.2
            get_or_infer("P1", 0.1)
            get_or_infer("P2", 0.2)
            get_or_infer("dropout", default_dropout)
            get_or_infer("ratio", 1.0)
            
        elif mode == "ttest":
            # Cohen's d = 0.5 (medium effect size), SD=1
            get_or_infer("mean1", 0)
            get_or_infer("mean2", 0.5)
            get_or_infer("S1", 1)
            get_or_infer("S2", 1)
            get_or_infer("dropout", default_dropout)
            get_or_infer("ratio", 1.0)

    return params, inferred

def main():
    parser = argparse.ArgumentParser(description="Clinic Sample Size Calculator")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to save the Markdown report")
    
    # Added common parameters
    parser.add_argument("--study_name", type=str, help="Research name")
    parser.add_argument("--outcome", type=str, help="Main outcome measure/study endpoint")
    
    subparsers = parser.add_subparsers(dest="study_type", help="Type of clinical study", required=True)

    # ==========================================
    # 1. Diagnostic Study
    # ==========================================
    diag_parser = subparsers.add_parser("diagnostic", help="Diagnostic Study")
    diag_subs = diag_parser.add_subparsers(dest="mode", required=True)
    
    # Sens/Spec
    p_sens = diag_subs.add_parser("sens_spec")
    p_sens.add_argument("--se", type=float, required=False)
    p_sens.add_argument("--sp", type=float, required=False)
    p_sens.add_argument("--error", type=float, required=False)
    p_sens.add_argument("--prev", type=float, required=False)
    p_sens.add_argument("--dropout", type=float, default=0.1)

    # AUC
    p_auc = diag_subs.add_parser("auc")
    p_auc.add_argument("--auc", type=float, required=False)
    p_auc.add_argument("--error", type=float, required=False)
    p_auc.add_argument("--dropout", type=float, default=0.1)

    # Kappa
    p_kappa = diag_subs.add_parser("kappa")
    p_kappa.add_argument("--pe", type=float, required=False)
    p_kappa.add_argument("--k1", type=float, required=False)
    p_kappa.add_argument("--dropout", type=float, default=0.1)

    # EPV
    p_epv = diag_subs.add_parser("model")
    p_epv.add_argument("--factors", type=int, required=False)
    p_epv.add_argument("--prev", type=float, required=False)
    p_epv.add_argument("--dropout", type=float, default=0.1)

    # ==========================================
    # 2. Efficacy Study
    # ==========================================
    eff_parser = subparsers.add_parser("efficacy", help="Efficacy Study (JSON input)")
    eff_parser.add_argument("--input", type=str, help="JSON input string")
    eff_parser.add_argument("--file", type=str, help="JSON config file path")

    # ==========================================
    # 3. Etiology Study
    # ==========================================
    etio_parser = subparsers.add_parser("etiology", help="Etiology Study")
    etio_parser.add_argument("--mode", choices=["categorical", "survival"], required=True)
    etio_parser.add_argument("--pt", type=float)
    etio_parser.add_argument("--pc", type=float)
    etio_parser.add_argument("--t0", type=float)
    etio_parser.add_argument("--t1", type=float)
    etio_parser.add_argument("--mc", type=float)
    etio_parser.add_argument("--mt", type=float)
    etio_parser.add_argument("--dropout", type=float, default=0.2)
    etio_parser.add_argument("--x", type=int, default=1)

    # ==========================================
    # 4. Prognosis Study
    # ==========================================
    prog_parser = subparsers.add_parser("prognosis", help="Prognosis Study")
    prog_subs = prog_parser.add_subparsers(dest="mode", required=True)
    
    # EPV
    p_prog_epv = prog_subs.add_parser("epv")
    p_prog_epv.add_argument("--P", type=float, required=False)
    p_prog_epv.add_argument("--training_rate", type=float, default=0.7)
    p_prog_epv.add_argument("--testing_rate", type=float, default=0.3)
    p_prog_epv.add_argument("--variables_number", type=int, required=False)
    p_prog_epv.add_argument("--dropout", type=float, default=0.1)

    # Log-rank
    p_prog_log = prog_subs.add_parser("logrank")
    p_prog_log.add_argument("--Hr", type=float, required=False)
    p_prog_log.add_argument("--overall_prob", type=float, required=False)
    p_prog_log.add_argument("--T0", type=float, required=False)
    p_prog_log.add_argument("--T1", type=float, required=False)
    p_prog_log.add_argument("--dropout", type=float, default=0.1)
    p_prog_log.add_argument("--ratio", type=float, default=1.0)

    # Chi-square
    p_prog_chi = prog_subs.add_parser("chisquare")
    p_prog_chi.add_argument("--P1", type=float, required=False)
    p_prog_chi.add_argument("--P2", type=float, required=False)
    p_prog_chi.add_argument("--dropout", type=float, default=0.1)
    p_prog_chi.add_argument("--ratio", type=float, default=1.0)

    # T-test
    p_prog_ttest = prog_subs.add_parser("ttest")
    p_prog_ttest.add_argument("--mean1", type=float, required=False)
    p_prog_ttest.add_argument("--mean2", type=float, required=False)
    p_prog_ttest.add_argument("--S1", type=float, required=False)
    p_prog_ttest.add_argument("--S2", type=float, required=False)
    p_prog_ttest.add_argument("--dropout", type=float, default=0.1)
    p_prog_ttest.add_argument("--ratio", type=float, default=1.0)

    args = parser.parse_args()
    result = {}
    
    # Initialize inference records
    inferred_params = []

    try:
        # Diagnostic Execution
        if args.study_type == "diagnostic":
            params, inferred_params = infer_parameters(args, args.mode)
            
            if args.mode == "sens_spec":
                result = DiagnosticCalculator.calculate_sens_spec(params["se"], params["sp"], params["error"], params["prev"], params["dropout"])
            elif args.mode == "auc":
                result = DiagnosticCalculator.calculate_auc(params["auc"], params["error"], params["dropout"])
            elif args.mode == "kappa":
                result = DiagnosticCalculator.calculate_kappa(params["pe"], params["k1"], params["dropout"])
            elif args.mode == "model":
                result = DiagnosticCalculator.calculate_epv(params["factors"], params["prev"], params["dropout"])

        # Efficacy Execution
        elif args.study_type == "efficacy":
            data = {}
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f: data = json.load(f)
            elif args.input:
                data = json.loads(args.input)
            
            # Efficacy requires special handling because its parameters are in JSON
            if not data:
                # If there is no input, try to build default JSON
                # Default: Two-arm general research
                data = {
                    "study_type": "general",
                    "design": "two",
                    "params": {}
                }
                inferred_params.append("study_type")
                inferred_params.append("design")
            
            study_type = data.get('study_type')
            design = data.get('design')
            params = data.get('params', {})
            
            # Intelligent inference of Efficacy parameters
            if study_type == 'general':
                if design == 'two':
                    # Check if key parameters are missing
                    if 'MeanT' not in params and 'Pt' not in params:
                        # Default inference is continuous variable, medium effect size
                        params.setdefault('MeanT', 0.5)
                        params.setdefault('MeanC', 0)
                        params.setdefault('St', 1)
                        params.setdefault('Sc', 1)
                        inferred_params.extend(['MeanT', 'MeanC', 'St', 'Sc'])
                    
                    params.setdefault('margin', 0)
                    params.setdefault('Dropout', 0.1)
                    params.setdefault('Pt', 0)
                    params.setdefault('Pc', 0)
                    
                    result = EfficacyCalculator.calculate_two_arm_general(
                        MeanT=params['MeanT'], MeanC=params['MeanC'],
                        St=params['St'], Sc=params['Sc'],
                        Pt=params['Pt'], Pc=params['Pc'],
                        margin=params['margin'], Dropout=params['Dropout']
                    )
                elif design == 'single':
                    if 'n' not in params and 'N' not in params:
                        params.setdefault('n', 30) # Default small sample
                        params.setdefault('x', 0)
                        params.setdefault('s', 1)
                        inferred_params.extend(['n', 'x', 's'])
                    
                    params.setdefault('N', 0)
                    params.setdefault('P', 0)
                    params.setdefault('Dropout', 0.1)
                    
                    result = EfficacyCalculator.calculate_single_arm_ci(
                        n=params['n'], x=params['x'], s=params['s'],
                        N=params['N'], P=params['P'],
                        Dropout=params['Dropout']
                    )
            elif study_type == 'survival':
                params.setdefault('accrual_time', 12)
                params.setdefault('total_time', 24)
                params.setdefault('Dropout', 0.1)
                
                if design == 'two':
                    if 'groupC_survival' not in params:
                        params['groupC_survival'] = 12 # Median
                        params['groupT_survival'] = 18 # Median
                        inferred_params.extend(['groupC_survival', 'groupT_survival'])
                        
                    result = EfficacyCalculator.calculate_survival_two_arm(
                        accrual_time=params['accrual_time'], total_time=params['total_time'],
                        groupC_survival=params['groupC_survival'], groupT_survival=params.get('groupT_survival'),
                        Dropout=params['Dropout']
                    )
                elif design == 'single':
                    if 'historical_survival' not in params:
                        params['historical_survival'] = 12
                        params['group_survival'] = 18
                        inferred_params.extend(['historical_survival', 'group_survival'])
                        
                    result = EfficacyCalculator.calculate_survival_single_arm(
                        accrual_time=params['accrual_time'], total_time=params['total_time'],
                        historical_survival=params['historical_survival'], group_survival=params.get('group_survival'),
                        Dropout=params['Dropout']
                    )
            
            # Efficacy needs to supplement study_name from args
            if not args.study_name and 'study_name' in data: args.study_name = data['study_name']
            if not args.outcome and 'outcome' in data: args.outcome = data['outcome']

        # Etiology Execution
        elif args.study_type == "etiology":
            params, inferred_params = infer_parameters(args, args.mode)
            
            if args.mode == "categorical":
                result = EtiologyCalculator.calculate_categorical(params["x"], params["pt"], params["pc"], params["dropout"])
            elif args.mode == "survival":
                result = EtiologyCalculator.calculate_survival(params["t0"], params["t1"], params["mc"], params["mt"], params["dropout"], params["x"])

        # Prognosis Execution
        elif args.study_type == "prognosis":
            params, inferred_params = infer_parameters(args, args.mode)
            
            if args.mode == "epv":
                result = PrognosisCalculator.calculate_epv(params["P"], params["training_rate"], params["testing_rate"], params["variables_number"], params["dropout"])
            elif args.mode == "logrank":
                result = PrognosisCalculator.calculate_log_rank(params["Hr"], params["overall_prob"], params["T0"], params["T1"], params["dropout"], params["ratio"])
            elif args.mode == "chisquare":
                result = PrognosisCalculator.calculate_chi_square(params["P1"], params["P2"], params["dropout"], params["ratio"])
            elif args.mode == "ttest":
                result = PrognosisCalculator.calculate_t_test(params["mean1"], params["mean2"], params["S1"], params["S2"], params["dropout"], params["ratio"])

    except Exception as e:
        result = {"error": str(e)}

    # Inject metadata
    if args.study_name:
        result['study_name'] = args.study_name
    if args.outcome:
        result['outcome'] = args.outcome
    
    # Inject inferred params info
    if inferred_params:
        result['inferred_params'] = inferred_params

    # Save Report
    saved_path = save_report(result, args.output_dir)
    
    print(json.dumps({
        "status": "success" if "error" not in result else "error",
        "report_path": os.path.abspath(saved_path),
        "data": result
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
