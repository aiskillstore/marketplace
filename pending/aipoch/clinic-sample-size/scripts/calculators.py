import math
from typing import Dict, Any, Union

class DiagnosticCalculator:
    """Calculates sample size for clinical diagnostic studies."""
    
    @staticmethod
    def calculate_sens_spec(se, sp, error, prev, dropout):
        alpha = 0.05
        z_alpha = 1.96
        
        # Case group sample size (based on Sensitivity)
        n_case_req = (z_alpha**2 * se * (1 - se)) / (error**2)
        n_total_case_based = n_case_req / prev
        
        # Control group sample size (based on Specificity)
        n_control_req = (z_alpha**2 * sp * (1 - sp)) / (error**2)
        n_total_control_based = n_control_req / (1 - prev)
        
        # Total sample size
        total_n_raw = max(n_total_case_based, n_total_control_based)
        total_n = math.ceil(total_n_raw)
        
        # Adjust for dropout
        final_n = math.ceil(total_n / (1 - dropout))
        
        n_case_final = math.ceil(final_n * prev)
        n_control_final = math.ceil(final_n * (1 - prev))
    
        return {
            "mode": "Sensitivity/Specificity",
            "mode_cn": "Sensitivity/specificity estimates",
            "inputs": {"Se": se, "Sp": sp, "Error": error, "Prevalence": prev, "Dropout": dropout},
            "results": {
                "required_cases_for_se": math.ceil(n_case_req),
                "required_controls_for_sp": math.ceil(n_control_req),
                "total_sample_size_raw": total_n,
                "final_sample_size_with_dropout": final_n,
                "estimated_cases": n_case_final,
                "estimated_controls": n_control_final
            },
            "description": f"To estimate the sensitivity ({se}) and specificity ({sp})，The error tolerance is {error}，in prevalence {prev} and shedding rate {dropout} under the conditions，Total needed {final_n} subjects。"
        }

    @staticmethod
    def calculate_auc(auc, margin_error, dropout):
        def norm_ppf(p):
            # Approximation of norm_ppf
            if p <= 0 or p >= 1: raise ValueError("p must be strictly between 0 and 1")
            return EfficacyCalculator.norm_ppf(p)

        z_score = norm_ppf(auc)
        a = z_score * math.sqrt(2)
        exp_term = math.exp(-a**2 / 2)
        term1 = 0.0099 * exp_term
        term2 = 6 * a**2 + 16
        v_auc = term1 * term2
        
        z_alpha = 1.96
        
        n_per_group = ((z_alpha**2) * v_auc) / (margin_error**2)
        n_per_group = math.ceil(n_per_group)
        total_n = n_per_group * 2
        final_n = math.ceil(total_n / (1 - dropout))
        
        return {
            "mode": "AUC",
            "mode_cn": "AUC (area under the ROC curve) estimation",
            "inputs": {"AUC": auc, "MarginError": margin_error, "Dropout": dropout},
            "results": {
                "n_per_group": n_per_group,
                "total_n_raw": total_n,
                "final_sample_size_with_dropout": final_n
            },
            "description": f"expected AUC for {auc}，The error tolerance is {margin_error}，English {dropout}，Total needed {final_n} subjects (Hypothetical cases and controls 1:1)。"
        }

    @staticmethod
    def calculate_kappa(pe, k1, dropout):
        alpha = 0.05
        z_alpha = 1.96
        beta = 0.2
        z_beta = 0.84162
        
        po = k1 * (1 - pe) + pe
        
        numerator = ((z_alpha + z_beta)**2) * (1 - pe)
        denominator = ((po - pe)**2) * (1 - po)
        
        if denominator == 0:
            return {"error": "The denominator is zero, please check the parameter settings."}
            
        sample_size = math.ceil(numerator / denominator)
        final_n = math.ceil(sample_size / (1 - dropout))
        
        return {
            "mode": "Kappa Consistency",
            "mode_cn": "Kappa consistency test",
            "inputs": {"Pe": pe, "MinKappa": k1, "Dropout": dropout},
            "results": {
                "Po": po,
                "sample_size_raw": sample_size,
                "final_sample_size_with_dropout": final_n
            },
            "description": f"In order to detect the lowest Kappa value {k1} (expected agreement rate Pe {pe})，English {dropout}，need {final_n} subjects。"
        }

    @staticmethod
    def calculate_epv(factors, prevalence, dropout):
        events_per_variable = 10
        required_events = factors * events_per_variable
        
        n_needed = required_events / prevalence
        final_n = math.ceil(n_needed / (1 - dropout))
        
        return {
            "mode": "Diagnostic Model (EPV)",
            "mode_cn": "Diagnostic prediction model (EPV method)",
            "inputs": {"Factors": factors, "Prevalence": prevalence, "Dropout": dropout},
            "results": {
                "required_events": required_events,
                "total_n_raw": math.ceil(n_needed),
                "final_sample_size_with_dropout": final_n
            },
            "description": f"Build contains {factors} diagnostic model，follow 10 EPV in principle，in prevalence {prevalence} and shedding rate {dropout} Down，need {final_n} subjects。"
        }

class EfficacyCalculator:
    """Calculates sample size for clinical efficacy studies."""

    @staticmethod
    def norm_ppf(p: float) -> float:
        if p <= 0 or p >= 1: raise ValueError("p must be in (0,1)")
        sign = -1 if p < 0.5 else 1
        p = min(p, 1 - p)
        t = math.sqrt(-2.0 * math.log(p))
        numerator = ((0.010328 * t + 0.802853) * t + 2.515517)
        denominator = (((0.001308 * t + 0.189269) * t + 1.432788) * t + 1.0)
        z = t - numerator / denominator
        return sign * z

    @staticmethod
    def calculate_two_arm_general(MeanT=0, MeanC=0, St=0, Sc=0, Pt=0, Pc=0, margin=0, Dropout=0) -> Dict[str, Any]:
        if margin == 0:
            alpha, beta, Z_alpha = 0.05, 0.2, 1.95996
            test_desc = "Difference test (two-sided)"
        else:
            alpha, beta, Z_alpha = 0.025, 0.2, 1.95996
            test_desc = "Non-inferiority test (one-sided)"
        
        Z_beta = 0.84162
        is_continuous = (MeanT != 0 or MeanC != 0 or St != 0 or Sc != 0)

        if is_continuous:
            delta = MeanT - MeanC
            if St == 0 and Sc == 0: sigma = 1.0
            elif St == 0: sigma = Sc
            elif Sc == 0: sigma = St
            else: sigma = math.sqrt((St**2 + Sc**2) / 2)
            
            denominator = delta**2 if margin == 0 else (delta - margin)**2
            if denominator == 0: return {"error": "The difference between the effect size and the boundary value is 0 and cannot be calculated."}

            n_per_group = math.ceil(2 * ((Z_alpha + Z_beta)**2 * sigma**2) / denominator)
            total_n = 2 * n_per_group
            true_n = math.ceil(total_n / (1 - Dropout))
            
            return {
                "type": "Continuous", 
                "mode_cn": "Comparison of continuous variables between arms",
                "test": test_desc,
                "results": {"n_per_group": n_per_group, "total_n": total_n, "true_n": true_n},
                "description": f"conduct{test_desc}，English {Dropout}，Each group needs {math.ceil(true_n/2)} example，total {true_n} example。"
            }
        else:
            p_bar = (Pt + Pc) / 2
            std_null = math.sqrt(2 * p_bar * (1 - p_bar))
            std_alt = math.sqrt(Pt * (1 - Pt) + Pc * (1 - Pc))
            delta_p = Pt - Pc
            
            denominator = delta_p**2 if margin == 0 else (delta_p - margin)**2
            if denominator == 0: return {"error": "The difference between the effect size and the boundary value is 0 and cannot be calculated."}

            numerator = (Z_alpha * std_null + Z_beta * std_alt)**2
            n_per_group = math.ceil(numerator / denominator)
            total_n = 2 * n_per_group
            true_n = math.ceil(total_n / (1 - Dropout))

            return {
                "type": "Categorical",
                "mode_cn": "Comparison of categorical variables in both arms",
                "test": test_desc,
                "results": {"n_per_group": n_per_group, "total_n": total_n, "true_n": true_n},
                "description": f"conduct{test_desc}，English {Dropout}，Each group needs {math.ceil(true_n/2)} example，total {true_n} example。"
            }

    @staticmethod
    def calculate_single_arm_ci(n=0, x=0, s=0, N=0, P=0, Dropout=0, alpha=0.05) -> Dict[str, Any]:
        # Implementation of single arm CI
        if n > 0 and s > 0: # Continuous
            true_n = math.ceil(n / (1 - Dropout))
            z_value = 1.96 # Simplified for large sample or use t-dist if needed
            margin_of_error = z_value * (s / math.sqrt(n))
            return {
                "type": "Continuous CI",
                "mode_cn": "One-arm continuous variable (confidence interval)",
                "results": {"lower": x - margin_of_error, "upper": x + margin_of_error, "true_n": true_n},
                "description": f"Calculates the mean of a single-arm continuous variable 95% confidence interval，English {Dropout}，The total sample size required is {true_n}。"
            }
        else: # Categorical
            true_n = math.ceil(N / (1 - Dropout))
            z_value = 1.96
            se = math.sqrt((P * (1 - P)) / N) if N > 0 else 0
            margin_of_error = z_value * se
            return {
                "type": "Categorical CI",
                "mode_cn": "One-arm categorical variable (confidence interval)",
                "results": {"lower": max(0, P - margin_of_error), "upper": min(1, P + margin_of_error), "true_n": true_n},
                "description": f"Calculate the rate of a single-arm categorical variable 95% confidence interval，English {Dropout}，The total sample size required is {true_n}。"
            }

    @staticmethod
    def _calculate_survival_common(accrual_time, total_time, groupC_surv, groupT_surv, Dropout, is_single_arm=False):
        if groupC_surv <= 1.0 and groupT_surv <= 1.0: # Survival Rate
            follow_up = total_time - accrual_time
            if follow_up <= 0: return {'error': 'Follow-up time must be greater than 0'}
            lambda_C = -math.log(groupC_surv) / follow_up
            lambda_T = -math.log(groupT_surv) / follow_up
        else: # Median
            lambda_C = math.log(2) / groupC_surv
            lambda_T = math.log(2) / groupT_surv
        
        hr = lambda_T / lambda_C
        
        def prob_event(accrual, total, lam):
            if accrual == 0 or lam * accrual == 0: return 1 - math.exp(-lam * total)
            return 1 - (math.exp(-lam * (total - accrual)) - math.exp(-lam * total)) / (lam * accrual)

        p_event_C = prob_event(accrual_time, total_time, lambda_C)
        p_event_T = prob_event(accrual_time, total_time, lambda_T)
        
        z_alpha, z_beta = 1.95996, 0.84162
        theta = math.log(hr)
        if theta == 0: return {'error': 'HR is 1 and cannot be calculated'}
        
        total_events = ((z_alpha + z_beta) / theta) ** 2 * 4
        overall_prob = (p_event_C + p_event_T) / 2
        total_sample = math.ceil(total_events / overall_prob)
        
        if is_single_arm: total_sample = math.ceil(total_sample / 4)
        
        true_n = math.ceil(total_sample / (1 - Dropout))
        mode_str = "One-arm survival analysis (historical control)" if is_single_arm else "Two-arm survival analysis (Log-rank)"
        
        return {
            "type": "Survival", 
            "mode_cn": mode_str,
            "is_single_arm": is_single_arm,
            "results": {"total_events": total_events, "total_sample": total_sample, "true_n": true_n, "HR": hr},
            "description": f"conduct{mode_str}，English {Dropout}，need to happen {math.ceil(total_events)} events，The total sample size required {true_n} example。"
        }

    @staticmethod
    def calculate_survival_two_arm(accrual_time, total_time, groupC_survival, groupT_survival, Dropout):
        return EfficacyCalculator._calculate_survival_common(accrual_time, total_time, groupC_survival, groupT_survival, Dropout, False)

    @staticmethod
    def calculate_survival_single_arm(accrual_time, total_time, historical_survival, group_survival, Dropout):
        return EfficacyCalculator._calculate_survival_common(accrual_time, total_time, historical_survival, group_survival, Dropout, True)

class EtiologyCalculator:
    """Calculates sample size for etiology studies."""
    
    @staticmethod
    def calculate_categorical(x, Pt, Pc, Dropout, alpha=0.05, power=0.8):
        Z_alpha = 1.96 if alpha == 0.05 else 1.95996
        Z_beta = 0.84162
        
        p_bar = (Pt + Pc) / 2
        std_null = math.sqrt(2 * p_bar * (1 - p_bar))
        std_alt = math.sqrt(Pt * (1 - Pt) + Pc * (1 - Pc))
        delta_p = abs(Pt - Pc)
        
        if delta_p == 0: return {"error": "The rates of the two groups are equal and cannot be calculated"}
        
        n_per_group = math.ceil(((Z_alpha * std_null + Z_beta * std_alt)**2) / delta_p**2)
        
        if x == 1:
            total_n = n_per_group * 2
            true_n = math.ceil(total_n / (1 - Dropout))
        else:
            x_fixed = 4 # From original logic
            total_n = math.ceil(n_per_group * x_fixed)
            true_n = math.ceil(total_n / (1 - Dropout))
            
        return {
            "mode": "Categorical",
            "mode_cn": "Categorical variables (case-control/cohort)",
            "results": {"n_per_group_base": n_per_group, "total_n": total_n, "true_n": true_n},
            "description": f"Compare rates in exposed and unexposed groups，English {Dropout}，The total sample size required {true_n} example。"
        }

    @staticmethod
    def calculate_survival(T0, T1, Mc, Mt, Dropout, x):
        if Mc <= 0 or Mt <= 0: return {"error": "Median survival time must be greater than 0"}
        lambda_C = math.log(2) / Mc
        lambda_T = math.log(2) / Mt
        
        def calc_prob(accrual, total, lam):
            if accrual == 0 or lam * accrual == 0: return 1 - math.exp(-lam * total)
            num = math.exp(-lam * (total - accrual)) - math.exp(-lam * total)
            return 1 - num / (lam * accrual)

        p_C = calc_prob(T0, T1, lambda_C)
        p_T = calc_prob(T0, T1, lambda_T)
        prob_avg = (p_C + p_T) / 2
        
        Z_alpha, Z_beta = 1.95996, 0.84162
        hr = lambda_C / lambda_T
        if hr == 1: return {"error": "HR is 1"}
        
        total_events = ((Z_alpha + Z_beta) / math.log(hr))**2 * 4
        sample_size = math.ceil(total_events / prob_avg)
        
        factor = 1 if x == 1 else 4
        total_sample = math.ceil(sample_size * factor)
        true_n = math.ceil(total_sample / (1 - Dropout))
        
        return {
            "mode": "Survival",
            "mode_cn": "Survival analysis (Log-rank)",
            "results": {"total_events": total_events, "total_sample": total_sample, "true_n": true_n},
            "description": f"Survival analysis comparison，English {Dropout}，The total sample size required {true_n} example。"
        }

class PrognosisCalculator:
    """Calculates sample size for prognosis studies."""
    
    @staticmethod
    def calculate_epv(P, training_rate, testing_rate, variables_number, Dropout):
        events = variables_number * 10
        if P <= 0: return {"error": "The event rate P must be greater than 0"}
        training_n = events / P
        total_n = math.ceil(training_n / training_rate)
        final_n = math.ceil(total_n / (1 - Dropout))
        
        return {
            "mode": "EPV",
            "mode_cn": "Prognosis prediction model (EPV method)",
            "results": {"events_needed": events, "total_n": total_n, "final_n": final_n},
            "description": f"build {variables_number} variable prognostic model (10 EPV)，event rate {P}，English {Dropout}，The total sample size required {final_n} example。"
        }

    @staticmethod
    def calculate_log_rank(Hr, overall_prob, T0, T1, Dropout, ratio):
        if Hr <= 0 or overall_prob <= 0: return {"error": "Invalid input"}
        z_alpha, z_beta = 1.95996, 0.84162
        theta = math.log(Hr)
        if theta == 0: return {"error": "HR is 1"}
        
        total_events = ((z_alpha + z_beta) / theta) ** 2
        total_sample_size = math.ceil(total_events / overall_prob)
        if ratio > 0: total_sample_size = math.ceil(total_sample_size / ratio) 
        
        true_n = math.ceil(total_sample_size / (1 - Dropout))
        return {
            "mode": "Log-rank",
            "mode_cn": "Prognostic survival analysis (Log-rank)",
            "results": {"total_events": total_events, "total_sample": total_sample_size, "true_n": true_n},
            "description": f"English，HR={Hr}，English {Dropout}，The total sample size required {true_n} example。"
        }

    @staticmethod
    def calculate_chi_square(P1, P2, Dropout, ratio):
        alpha, beta, Z_alpha, Z_beta = 0.05, 0.2, 1.95996, 0.84162
        p_bar = (P1 + P2) / 2
        std_null = math.sqrt(2 * p_bar * (1 - p_bar))
        std_alt = math.sqrt(P1 * (1 - P1) + P2 * (1 - P2))
        delta = abs(P1 - P2)
        if delta == 0: return {"error": "P1=P2"}
        
        n_per = math.ceil(((Z_alpha * std_null + Z_beta * std_alt)**2) / delta**2)
        total = 2 * n_per
        if ratio > 0: total = math.ceil(total / ratio)
        true_n = math.ceil(total / (1 - Dropout))
        
        return {
            "mode": "Chi-square",
            "mode_cn": "Prognostic factor analysis (chi-square test)",
            "results": {"n_per_group_base": n_per, "total": total, "true_n": true_n},
            "description": f"Compare the prognosis rates of the two groups ({P1} vs {P2})，English {Dropout}，The total sample size required {true_n} example。"
        }

    @staticmethod
    def calculate_t_test(mean1, mean2, S1, S2, Dropout, ratio):
        alpha, beta, Z_alpha, Z_beta = 0.05, 0.2, 1.95996, 0.84162
        delta = abs(mean1 - mean2)
        if delta == 0: return {"error": "Means are equal"}
        
        if S1 == 0 and S2 == 0: sigma = 1
        elif S1 == 0: sigma = S2
        elif S2 == 0: sigma = S1
        else: sigma = math.sqrt((S1**2 + S2**2) / 2)
        
        n_per = math.ceil(2 * ((Z_alpha + Z_beta)**2 * sigma**2) / delta**2)
        total = 2 * n_per
        if ratio > 0: total = math.ceil(total / ratio)
        true_n = math.ceil(total / (1 - Dropout))
        
        return {
            "mode": "T-test",
            "mode_cn": "Prognostic factor analysis (T test)",
            "results": {"n_per_group_base": n_per, "total": total, "true_n": true_n},
            "description": f"Compare the mean values ​​of prognostic indicators between the two groups ({mean1} vs {mean2})，English {Dropout}，The total sample size required {true_n} example。"
        }
