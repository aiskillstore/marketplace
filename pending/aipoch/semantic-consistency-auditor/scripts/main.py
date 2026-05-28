#!/usr/bin/env python3
"""Semantic Consistency Auditor
Semantic consistency assessment tool based on BERTScore and COMET
Used to evaluate the consistency of AI-generated medical records with expert gold standards

ID: 212
Author:OpenClaw
Date: 2026-02-06"""

import argparse
import json
import sys
import os
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

# Try importing optional dependencies
try:
    from bert_score import score as bert_score
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False
    print("Warning: bert_score is not installed and the BERTScore function is not available. Run: pip install bertscore")

try:
    from comet import download_model, load_from_checkpoint
    COMET_AVAILABLE = True
except ImportError:
    COMET_AVAILABLE = False
    print("Warning: comet-ml is not installed and the COMET function is not available. Run: pip install comet-ml")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class EvaluationResult:
    """Evaluation result data class"""
    case_id: Optional[str]
    ai_generated: str
    gold_standard: str
    bertscore_precision: float
    bertscore_recall: float
    bertscore_f1: float
    comet_score: float
    semantic_consistency: float
    passed: bool
    details: Dict


@dataclass
class SummaryResult:
    """Summary result data class"""
    total_cases: int
    passed_cases: int
    pass_rate: float
    avg_bertscore_f1: float
    avg_comet_score: float
    avg_consistency: float


class SemanticConsistencyAuditor:
    """Semantic consistency auditor
    
    Use the BERTScore and COMET algorithms to evaluate the semantic consistency between AI-generated text and the gold standard."""
    
    DEFAULT_CONFIG = {
        'bertscore': {
            'model': 'microsoft/deberta-xlarge-mnli',
            'lang': 'zh',
            'rescale_with_baseline': True,
            'device': 'auto'
        },
        'comet': {
            'model': 'Unbabel/wmt22-comet-da',
            'batch_size': 8,
            'device': 'auto'
        },
        'thresholds': {
            'bertscore_f1': 0.85,
            'comet_score': 0.75,
            'semantic_consistency': 0.80
        }
    }
    
    def __init__(
        self,
        bert_model: Optional[str] = None,
        comet_model: Optional[str] = None,
        lang: str = 'zh',
        device: str = 'auto',
        config_path: Optional[str] = None
    ):
        """Initialize the semantic consistency auditor
        
        Args:
            bert_model: model name used by BERTScore
            comet_model: model name used by COMET
            lang: language code ('zh', 'en', etc.)
            device: computing device ('auto', 'cpu', 'cuda')
            config_path: configuration file path"""
        self.config = self._load_config(config_path)
        self.lang = lang or self.config['bertscore']['lang']
        self.device = self._get_device(device)
        
        # BERTScore configuration
        self.bert_model = bert_model or self.config['bertscore']['model']
        self.bertscore_available = BERTSCORE_AVAILABLE
        
        # COMET configuration
        self.comet_model_name = comet_model or self.config['comet']['model']
        self.comet_model = None
        self.comet_available = COMET_AVAILABLE
        
        # threshold
        self.thresholds = self.config['thresholds']
        
        # Lazy loading model
        self._bertscore_initialized = False
        self._comet_initialized = False
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    try:
                        import yaml
                        return yaml.safe_load(f)
                    except ImportError:
                        pass
                return json.load(f)
        return self.DEFAULT_CONFIG
    
    def _get_device(self, device: str) -> str:
        """Determine computing device"""
        if device == 'auto':
            if TORCH_AVAILABLE and torch.cuda.is_available():
                return 'cuda'
            return 'cpu'
        return device
    
    def _init_bertscore(self):
        """Initialize BERTScore (load on demand)"""
        if self._bertscore_initialized:
            return
        if not self.bertscore_available:
            raise RuntimeError("BERTScore is not available, please install: pip install bertscore")
        self._bertscore_initialized = True
    
    def _init_comet(self):
        """Initialize COMET model (load on demand)"""
        if self._comet_initialized:
            return
        if not self.comet_available:
            raise RuntimeError("COMET is not available, please install: pip install comet-ml")
        
        try:
            # Download and load the COMET model
            model_path = download_model(self.comet_model_name)
            self.comet_model = load_from_checkpoint(model_path)
            self._comet_initialized = True
        except Exception as e:
            raise RuntimeError(f"COMETModel loading failed: {e}")
    
    def evaluate(
        self,
        ai_text: str,
        gold_text: str,
        case_id: Optional[str] = None
    ) -> Dict:
        """Assessing the semantic consistency of individual cases
        
        Args:
            ai_text: AI-generated medical record text
            gold_text: Expert gold standard text
            case_id: case ID (optional)
        
        Returns:
            A dictionary containing evaluation results"""
        if not ai_text or not gold_text:
            raise ValueError("E001: Input text cannot be empty")
        
        # Calculate BERTScore
        bertscore_result = self._compute_bertscore([ai_text], [gold_text])
        
        # Calculate COMET score
        comet_result = self._compute_comet([ai_text], [gold_text])
        
        # Compute synthetic semantic consistency
        semantic_consistency = self._compute_consistency(
            bertscore_result['f1'],
            comet_result['score']
        )
        
        # Determine whether it passes
        passed = self._check_passed(
            bertscore_result['f1'],
            comet_result['score'],
            semantic_consistency
        )
        
        # Analyze semantic differences
        details = self._analyze_semantic_details(ai_text, gold_text)
        
        result = EvaluationResult(
            case_id=case_id,
            ai_generated=ai_text,
            gold_standard=gold_text,
            bertscore_precision=bertscore_result['precision'],
            bertscore_recall=bertscore_result['recall'],
            bertscore_f1=bertscore_result['f1'],
            comet_score=comet_result['score'],
            semantic_consistency=semantic_consistency,
            passed=passed,
            details=details
        )
        
        return self._result_to_dict(result)
    
    def evaluate_batch(
        self,
        cases: List[Dict[str, str]],
        show_progress: bool = True
    ) -> List[Dict]:
        """Assess multiple cases in batches
        
        Args:
            cases: list of cases, each case contains 'ai', 'gold', optional 'case_id'
            show_progress: whether to show progress
        
        Returns:
            Evaluation results list"""
        results = []
        total = len(cases)
        
        for i, case in enumerate(cases):
            if show_progress:
                print(f"schedule: {i+1}/{total} ({(i+1)/total*100:.1f}%)", file=sys.stderr)
            
            try:
                result = self.evaluate(
                    ai_text=case['ai'],
                    gold_text=case['gold'],
                    case_id=case.get('case_id', f"CASE_{i+1:04d}")
                )
                results.append(result)
            except Exception as e:
                print(f"warn: cases {case.get('case_id', i)} Evaluation failed: {e}", file=sys.stderr)
                results.append({
                    'case_id': case.get('case_id', f"CASE_{i+1:04d}"),
                    'error': str(e),
                    'passed': False
                })
        
        return results
    
    def _compute_bertscore(
        self,
        candidates: List[str],
        references: List[str]
    ) -> Dict[str, float]:
        """Calculate BERTScore"""
        self._init_bertscore()
        
        try:
            P, R, F1 = bert_score(
                candidates,
                references,
                lang=self.lang,
                model_type=self.bert_model,
                device=self.device,
                rescale_with_baseline=self.config['bertscore']['rescale_with_baseline'],
                verbose=False
            )
            
            return {
                'precision': P[0].item(),
                'recall': R[0].item(),
                'f1': F1[0].item()
            }
        except Exception as e:
            print(f"BERTScoreCalculation warning: {e}", file=sys.stderr)
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    
    def _compute_comet(
        self,
        sources: List[str],
        translations: List[str]
    ) -> Dict[str, float]:
        """Calculate COMET score"""
        self._init_comet()
        
        try:
            # COMET requires source text, translation text and reference text
            # In the semantic consistency evaluation, we use gold as the reference and ai as the translation
            data = [{
                "src": sources[0],
                "mt": sources[0],  # AI generated text
                "ref": translations[0]  # gold standard
            }]
            
            seg_scores, sys_score = self.comet_model.predict(
                data,
                batch_size=self.config['comet']['batch_size']
            )
            
            return {
                'score': seg_scores[0] if seg_scores else sys_score,
                'system_score': sys_score
            }
        except Exception as e:
            print(f"COMETCalculation warning: {e}", file=sys.stderr)
            return {'score': 0.0, 'system_score': 0.0}
    
    def _compute_consistency(self, bertscore_f1: float, comet_score: float) -> float:
        """Calculate the overall semantic consistency score
        
        Combining BERTScore F1 and COMET scores using a weighted average"""
        # Weight of BERTScore and COMET (configurable)
        w_bert = 0.6
        w_comet = 0.4
        
        # COMET scores may need to be normalized (usually between -1 and 1)
        comet_normalized = (comet_score + 1) / 2 if comet_score < 0 else comet_score
        
        return w_bert * bertscore_f1 + w_comet * comet_normalized
    
    def _check_passed(
        self,
        bertscore_f1: float,
        comet_score: float,
        consistency: float
    ) -> bool:
        """Check if the evaluation passes"""
        return (
            bertscore_f1 >= self.thresholds['bertscore_f1'] and
            comet_score >= self.thresholds['comet_score'] and
            consistency >= self.thresholds['semantic_consistency']
        )
    
    def _analyze_semantic_details(
        self,
        ai_text: str,
        gold_text: str
    ) -> Dict:
        """Analyze differences in semantic details (simplified version)"""
        # More complex semantic analysis can be implemented here
        # For example: entity recognition, key concept extraction, etc.
        
        # Simple keyword matching example
        ai_words = set(ai_text.split())
        gold_words = set(gold_text.split())
        
        matched = ai_words & gold_words
        missed = gold_words - ai_words
        extra = ai_words - gold_words
        
        return {
            'semantic_gaps': list(missed)[:10],  # Up to 10 missing items
            'extra_content': list(extra)[:10],   # Up to 10 additional content
            'matched_concepts': list(matched)[:10],  # Up to 10 matches
            'match_ratio': len(matched) / len(gold_words) if gold_words else 0
        }
    
    def _result_to_dict(self, result: EvaluationResult) -> Dict:
        """Convert the result to dictionary format"""
        return {
            'case_id': result.case_id,
            'ai_generated': result.ai_generated,
            'gold_standard': result.gold_standard,
            'metrics': {
                'bertscore': {
                    'precision': round(result.bertscore_precision, 4),
                    'recall': round(result.bertscore_recall, 4),
                    'f1': round(result.bertscore_f1, 4)
                },
                'comet': {
                    'score': round(result.comet_score, 4)
                },
                'semantic_consistency': round(result.semantic_consistency, 4)
            },
            'passed': result.passed,
            'grade': self._get_grade(result.semantic_consistency),
            'details': result.details
        }
    
    def _get_grade(self, consistency: float) -> str:
        """Returns a grade based on consistency score"""
        if consistency >= 0.90:
            return "excellent"
        elif consistency >= 0.80:
            return "good"
        elif consistency >= 0.70:
            return "pass"
        elif consistency >= 0.60:
            return "To be improved"
        else:
            return "Unqualified"
    
    def compute_summary(self, results: List[Dict]) -> Dict:
        """Calculate summary statistics"""
        if not results:
            return {}
        
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'There is no valid evaluation result'}
        
        total = len(valid_results)
        passed = sum(1 for r in valid_results if r.get('passed', False))
        
        avg_bert_f1 = np.mean([r['metrics']['bertscore']['f1'] for r in valid_results])
        avg_comet = np.mean([r['metrics']['comet']['score'] for r in valid_results])
        avg_consistency = np.mean([r['metrics']['semantic_consistency'] for r in valid_results])
        
        summary = SummaryResult(
            total_cases=total,
            passed_cases=passed,
            pass_rate=round(passed / total, 4) if total > 0 else 0.0,
            avg_bertscore_f1=round(avg_bert_f1, 4),
            avg_comet_score=round(avg_comet, 4),
            avg_consistency=round(avg_consistency, 4)
        )
        
        return {
            'summary': asdict(summary),
            'thresholds': self.thresholds,
            'grade_distribution': self._compute_grade_distribution(valid_results)
        }
    
    def _compute_grade_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """Calculate rank distribution"""
        distribution = {"excellent": 0, "good": 0, "pass": 0, "To be improved": 0, "Unqualified": 0}
        for r in results:
            grade = r.get('grade', 'Unqualified')
            distribution[grade] = distribution.get(grade, 0) + 1
        return distribution


def load_batch_cases(file_path: str) -> List[Dict[str, str]]:
    """Load batch cases from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return [
            {
                'case_id': item.get('case_id', f"CASE_{i+1:04d}"),
                'ai': item.get('ai_generated', item.get('ai', '')),
                'gold': item.get('gold_standard', item.get('gold', ''))
            }
            for i, item in enumerate(data)
        ]
    elif isinstance(data, dict) and 'cases' in data:
        return [
            {
                'case_id': item.get('case_id', f"CASE_{i+1:04d}"),
                'ai': item.get('ai_generated', item.get('ai', '')),
                'gold': item.get('gold_standard', item.get('gold', ''))
            }
            for i, item in enumerate(data['cases'])
        ]
    else:
        raise ValueError("Input file format error, should be a list of cases or an object containing the 'cases' field")


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description='Semantic Consistency Auditor - Semantic consistency assessment based on BERTScore and COMET',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  # Single case assessment
  python main.py -a "AI generated medical records" -g "Expert gold standard"
  
  # Batch evaluation
  python main.py -i cases.json -o results.json
  
  # Use a specific model
  python main.py -a "..." -g "..." --bert-model "bert-base-chinese""""
    )
    
    # input parameters
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-a', '--ai-generated',
        help='AI-generated medical record text'
    )
    input_group.add_argument(
        '-i', '--input-file',
        help='JSON file path for batch evaluation'
    )
    
    parser.add_argument(
        '-g', '--gold-standard',
        help='Expert gold standard text (used with --ai-generated)'
    )
    parser.add_argument(
        '--case-id',
        help='Case ID (optional)'
    )
    
    # Model parameters
    parser.add_argument(
        '--bert-model',
        default='microsoft/deberta-xlarge-mnli',
        help='BERTScore model name (default: microsoft/deberta-xlarge-mnli)'
    )
    parser.add_argument(
        '--comet-model',
        default='Unbabel/wmt22-comet-da',
        help='COMET model name (default: Unbabel/wmt22-comet-da)'
    )
    parser.add_argument(
        '--lang', '-l',
        default='zh',
        help='Language code (default: zh)'
    )
    parser.add_argument(
        '--device',
        default='auto',
        choices=['auto', 'cpu', 'cuda'],
        help='Computing device (default: auto)'
    )
    
    # Threshold parameters
    parser.add_argument(
        '--threshold-bert',
        type=float,
        default=0.85,
        help='BERTScore F1 threshold (default: 0.85)'
    )
    parser.add_argument(
        '--threshold-comet',
        type=float,
        default=0.75,
        help='COMET score threshold (default: 0.75)'
    )
    parser.add_argument(
        '--threshold-consistency',
        type=float,
        default=0.80,
        help='Comprehensive consistency threshold (default: 0.80)'
    )
    
    # Output parameters
    parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['summary', 'detailed'],
        default='detailed',
        help='Output format (default: detailed)'
    )
    parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    
    args = parser.parse_args()
    
    # Validation parameters
    if args.ai_generated and not args.gold_standard:
        parser.error('--ai-generated needs to be used with --gold-standard')
    
    try:
        # Initialize the auditor
        auditor = SemanticConsistencyAuditor(
            bert_model=args.bert_model,
            comet_model=args.comet_model,
            lang=args.lang,
            device=args.device,
            config_path=args.config
        )
        
        # update threshold
        auditor.thresholds = {
            'bertscore_f1': args.threshold_bert,
            'comet_score': args.threshold_comet,
            'semantic_consistency': args.threshold_consistency
        }
        
        # Perform assessment
        if args.input_file:
            # Batch evaluation
            print(f"Loading case files: {args.input_file}")
            cases = load_batch_cases(args.input_file)
            print(f"Loaded {len(cases)} cases")
            
            print("Start evaluating...")
            results = auditor.evaluate_batch(cases)
            
            # Generate output
            if args.format == 'summary':
                output = auditor.compute_summary(results)
            else:
                summary = auditor.compute_summary(results)
                output = {
                    'cases': results,
                    'summary': summary.get('summary', {}),
                    'thresholds': summary.get('thresholds', {}),
                    'grade_distribution': summary.get('grade_distribution', {})
                }
        else:
            # single assessment
            result = auditor.evaluate(
                ai_text=args.ai_generated,
                gold_text=args.gold_standard,
                case_id=args.case_id
            )
            output = result
            
            # Print summary results to the console
            print(f"\nAssessment results:")
            print(f"  BERTScore F1: {result['metrics']['bertscore']['f1']:.4f}")
            print(f"  COMET Score: {result['metrics']['comet']['score']:.4f}")
            print(f"  semantic consistency: {result['metrics']['semantic_consistency']:.4f}")
            print(f"  grade: {result['grade']}")
            print(f"  pass: {'✓' if result['passed'] else '✗'}")
        
        # Save or export results
        output_json = json.dumps(output, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"\nResults have been saved to: {args.output}")
        else:
            print("Full results:")
            print(output_json)
    
    except FileNotFoundError as e:
        print(f"mistake: file not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"mistake: JSONParsing failed - {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"mistake: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"mistake: unexpected error - {e}", file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
