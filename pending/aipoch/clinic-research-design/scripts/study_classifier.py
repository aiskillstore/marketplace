from enum import Enum
from typing import Dict, Any

class StudyType(Enum):
    DIAGNOSTIC = "diagnostic"
    EFFICACY = "efficacy"
    ETIOLOGY = "etiology"
    PROGNOSIS = "prognosis"
    UNKNOWN = "unknown"

class StudyClassifier:
    def classify(self, picos: Dict[str, str], user_type_hint: str = None) -> str:
        if user_type_hint and user_type_hint in [e.value for e in StudyType]:
            return user_type_hint
            
        # Heuristic classification
        objective = picos.get('O', '').lower()
        intervention = picos.get('I', '').lower()
        study_design = picos.get('S', '').lower()
        
        if "sensitivity" in objective or "specificity" in objective or "accuracy" in objective or "diagnostic" in study_design:
            return StudyType.DIAGNOSTIC.value
            
        if "prognosis" in study_design or "survival" in objective or "hazard" in objective:
            return StudyType.PROGNOSIS.value
            
        if "risk factor" in study_design or "cause" in objective or "association" in objective:
            return StudyType.ETIOLOGY.value
            
        # Default to efficacy/intervention if drugs/treatment mentioned
        return StudyType.EFFICACY.value
