import math
from typing import Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class SampleSizeParams:
    """Sample size calculation parameters"""
    alpha: float = 0.05
    beta: float = 0.2
    dropout_rate: float = 0.2
    power: float = 0.8

class SampleSizeCalculator:
    """Unified Clinical Study Sample Size Calculator"""
    
    def __init__(self):
        self.z_values = {
            0.05: 1.96,   # alpha = 0.05 (two-sided)
            0.01: 2.58,   # alpha = 0.01 (two-sided)
            0.1: 1.645,   # alpha = 0.1 (two-sided)
        }
        self.z_beta = {
            0.2: 0.84,    # beta = 0.2, power = 0.8
            0.1: 1.28,    # beta = 0.1, power = 0.9
            0.05: 1.645,  # beta = 0.05, power = 0.95
        }
    
    def get_z_value(self, alpha: float, two_sided: bool = True) -> float:
        if two_sided:
            alpha = alpha / 2
        return self.z_values.get(alpha, 1.96)
    
    def get_z_beta(self, beta: float) -> float:
        return self.z_beta.get(beta, 0.84)
    
    def adjust_for_dropout(self, n: int, dropout_rate: float) -> int:
        return math.ceil(n / (1 - dropout_rate))

    # --- Diagnostic Studies ---
    def diagnostic_accuracy(self, sensitivity: float, specificity: float, 
                          prevalence: float, precision: float, params: SampleSizeParams) -> Dict[str, Any]:
        """
        Calculate sample size for diagnostic accuracy (Sensitivity/Specificity).
        Formula: N_diseased = Z^2 * Sn * (1-Sn) / d^2
                 N_total = N_diseased / Prevalence
        """
        z_alpha = self.get_z_value(params.alpha)
        
        # Calculate for Sensitivity
        n_sens = (z_alpha**2 * sensitivity * (1 - sensitivity)) / (precision**2)
        n_total_sens = n_sens / prevalence if prevalence > 0 else n_sens
        
        # Calculate for Specificity
        n_spec = (z_alpha**2 * specificity * (1 - specificity)) / (precision**2)
        n_total_spec = n_spec / (1 - prevalence) if prevalence < 1 else n_spec
        
        # Take the maximum required
        n_total_theoretical = max(n_total_sens, n_total_spec)
        n_total = math.ceil(n_total_theoretical)
        n_adjusted = self.adjust_for_dropout(n_total, params.dropout_rate)
        
        return {
            "theoretical": n_total,
            "adjusted": n_adjusted,
            "details": {
                "based_on_sensitivity": math.ceil(n_total_sens),
                "based_on_specificity": math.ceil(n_total_spec)
            }
        }

    # --- Cohort / Etiology Studies ---
    def cohort_two_arm(self, p1: float, p2: float, params: SampleSizeParams) -> Dict[str, int]:
        """Two-arm cohort (Exposed vs Unexposed)"""
        z_alpha = self.get_z_value(params.alpha)
        z_beta = self.get_z_beta(params.beta)
        
        p_pooled = (p1 + p2) / 2
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                  z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p1 - p2) ** 2 if p1 != p2 else 0.0001
        
        n_per_group = math.ceil(numerator / denominator)
        n_adjusted = self.adjust_for_dropout(n_per_group, params.dropout_rate)
        
        return {
            "theoretical_per_group": n_per_group,
            "adjusted_per_group": n_adjusted,
            "total_adjusted": n_adjusted * 2
        }

    # --- Intervention / Efficacy Studies ---
    def rct_two_arm_binary(self, p1: float, p2: float, params: SampleSizeParams) -> Dict[str, int]:
        """RCT Binary Outcome (Same as Cohort Two Arm)"""
        return self.cohort_two_arm(p1, p2, params)

    def rct_two_arm_continuous(self, mean_diff: float, sd: float, params: SampleSizeParams) -> Dict[str, int]:
        """RCT Continuous Outcome"""
        z_alpha = self.get_z_value(params.alpha)
        z_beta = self.get_z_beta(params.beta)
        
        n_per_group = math.ceil((2 * sd ** 2 * (z_alpha + z_beta) ** 2) / (mean_diff ** 2))
        n_adjusted = self.adjust_for_dropout(n_per_group, params.dropout_rate)
        
        return {
            "theoretical_per_group": n_per_group,
            "adjusted_per_group": n_adjusted,
            "total_adjusted": n_adjusted * 2
        }

    def single_arm_trial(self, p_expected: float, p_target: float, params: SampleSizeParams) -> Dict[str, int]:
        """Single Arm Trial"""
        z_alpha = self.get_z_value(params.alpha)
        denominator = (p_expected - p_target) ** 2 if p_expected != p_target else 0.0001
        n = math.ceil((z_alpha ** 2 * p_expected * (1 - p_expected)) / denominator)
        n_adjusted = self.adjust_for_dropout(n, params.dropout_rate)
        
        return {
            "theoretical": n,
            "adjusted": n_adjusted
        }

    # --- Prognosis Studies ---
    def prognosis_model(self, num_vars: int, event_rate: float, epv: int = 10, params: SampleSizeParams = None) -> Dict[str, int]:
        """Prognostic Model (EPV based)"""
        if params is None:
            params = SampleSizeParams()
            
        min_events = num_vars * epv
        n_total = math.ceil(min_events / event_rate) if event_rate > 0 else 0
        n_adjusted = self.adjust_for_dropout(n_total, params.dropout_rate)
        
        return {
            "theoretical": n_total,
            "adjusted": n_adjusted,
            "min_events": min_events
        }

def calculate_sample_size(study_type: str, **kwargs) -> Dict[str, Any]:
    """Unified entry point"""
    calculator = SampleSizeCalculator()
    params = SampleSizeParams(
        alpha=kwargs.get('alpha', 0.05),
        beta=kwargs.get('beta', 0.2),
        dropout_rate=kwargs.get('dropout_rate', 0.2)
    )
    
    try:
        if study_type == "diagnostic":
            return calculator.diagnostic_accuracy(
                sensitivity=kwargs.get('sensitivity', 0.8),
                specificity=kwargs.get('specificity', 0.8),
                prevalence=kwargs.get('prevalence', 0.5),
                precision=kwargs.get('precision', 0.05),
                params=params
            )
        
        elif study_type in ["efficacy", "intervention", "rct"]:
            design = kwargs.get('design_type', 'rct')
            outcome_type = kwargs.get('outcome_type', 'binary')
            
            if design == 'single_arm':
                return calculator.single_arm_trial(
                    p_expected=kwargs.get('p_expected', 0.7),
                    p_target=kwargs.get('p_target', 0.5),
                    params=params
                )
            elif outcome_type == 'continuous':
                return calculator.rct_two_arm_continuous(
                    mean_diff=kwargs.get('mean_diff', 1.0),
                    sd=kwargs.get('sd', 1.0),
                    params=params
                )
            else: # binary
                return calculator.rct_two_arm_binary(
                    p1=kwargs.get('p1', 0.6),
                    p2=kwargs.get('p2', 0.4),
                    params=params
                )
                
        elif study_type in ["etiology", "cohort"]:
            return calculator.cohort_two_arm(
                p1=kwargs.get('p1', 0.15),
                p2=kwargs.get('p2', 0.05),
                params=params
            )
            
        elif study_type == "prognosis":
            if kwargs.get('model_building', False):
                return calculator.prognosis_model(
                    num_vars=kwargs.get('num_vars', 5),
                    event_rate=kwargs.get('event_rate', 0.3),
                    params=params
                )
            else:
                # Treat prognostic factor study like a cohort study (High risk vs Low risk group)
                return calculator.cohort_two_arm(
                    p1=kwargs.get('p1', 0.4),
                    p2=kwargs.get('p2', 0.2),
                    params=params
                )
        
        else:
            return {"error": f"Unknown study type: {study_type}"}
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(calculate_sample_size("diagnostic", sensitivity=0.85, specificity=0.90, prevalence=0.3))
