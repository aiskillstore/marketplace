from typing import Dict, Any
from calculators.sample_size import calculate_sample_size
from templates.protocol_templates import ProtocolTemplateGenerator, ProtocolFormatter
from study_classifier import StudyClassifier

class ClinicResearchDesign:
    def __init__(self):
        self.classifier = StudyClassifier()
        self.generator = ProtocolTemplateGenerator()
        self.formatter = ProtocolFormatter()
    
    def write_protocol(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 1. Classify
            picos = inputs.get('picos', {})
            study_type = self.classifier.classify(picos, inputs.get('type'))
            
            # 2. Calculate Sample Size
            # Map inputs to calculator arguments based on type
            calc_args = self._map_calculator_args(study_type, inputs)
            sample_size_result = calculate_sample_size(study_type, **calc_args)
            
            # 3. Build Study Info
            study_info = {
                'study_type': study_type,
                'picos': picos,
                'design_type': inputs.get('study_design', 'Standard'),
                'sample_size': sample_size_result,
                'pi': inputs.get('principal_investigator'),
                'institution': inputs.get('institution')
            }
            
            # 4. Generate Protocol
            protocol_text = self.generator.generate_protocol(study_info)
            summary_text = self.formatter.generate_summary(study_info)
            
            return {
                'success': True,
                'protocol': protocol_text,
                'summary': summary_text,
                'data': study_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _map_calculator_args(self, study_type, inputs):
        args = inputs.copy()
        # Add any specific mapping logic here if needed
        return args
