#!/usr/bin/env python3
"""Unstructured Medical Text Miner (Skill ID: 213)

Mining MIMIC-IV medical text data and extracting unstructured diagnosis and treatment information.
Supports entity recognition, relationship extraction, timeline analysis and diagnosis and treatment logic extraction."""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import warnings

import pandas as pd

# Try importing optional dependencies
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    warnings.warn("spacy not installed. NER functionality will be limited.")

try:
    from negspacy.negation import Negex
    NEGSPACY_AVAILABLE = True
except ImportError:
    NEGSPACY_AVAILABLE = False


class MedicalTextMiner:
    """MIMIC-IV unstructured medical text miner
    
    Main functions:
    1. Load and preprocess text data such as NOTEEVENTS
    2. Entity recognition (diseases, symptoms, drugs, surgeries, etc.)
    3. Negative testing (identification of clinical findings that are negated)
    4. Relationship extraction (drug-disease relationship, etc.)
    5. Timeline extraction (disease progression sequence)
    6. Analysis of diagnosis and treatment logic"""
    
    # Medical entity type definition
    ENTITY_PATTERNS = {
        "MEDICATION": [
            r"\b(aspirin|warfarin|heparin|metformin|insulin|amoxicillin|"
            r"azithromycin|morphine|fentanyl|propofol|norepinephrine|"
            r"phenylephrine|dopamine|epinephrine)\b",
            r"\b\w+\s*(?:mg|mcg|g|units?)\b"  # dose mode
        ],
        "DISEASE": [
            r"\b(acute myocardial infarction|AMI|STEMI|NSTEMI|heart failure|"
            r"pneumonia|sepsis|ARDS|COPD|asthma|diabetes mellitus|"
            r"hypertension|atrial fibrillation|AFib|stroke|DVT|PE)\b",
            r"\b\w+(?:itis|osis|emia|oma|pathy| syndrome)\b"
        ],
        "SYMPTOM": [
            r"\b(chest pain|dyspnea|shortness of breath|fatigue|nausea|"
            r"vomiting|fever|chills|headache|dizziness|syncope|"
            r"palpitations|cough|hemoptysis)\b"
        ],
        "PROCEDURE": [
            r"\b(PCI|CABG|ECG|EKG|echocardiogram|CT|MRI|chest X-ray|"
            r"bronchoscopy|intubation|extubation|thoracentesis|"
            r"paracentesis|lumbar puncture)\b"
        ],
        "ANATOMY": [
            r"\b(left ventricle|right ventricle|left atrium|right atrium|"
            r"mitral valve|aortic valve|tricuspid valve|pulmonary valve|"
            r"coronary artery|LAD|LCx|RCA|lung|liver|kidney|spleen)\b"
        ],
        "LAB_VALUE": [
            r"\b(troponin|creatinine|BNP|NT-proBNP|WBC|hemoglobin|platelet|"
            r"INR|PTT|PT|glucose|HbA1c|lactate|pH|PCO2|PO2)\b"
        ]
    }
    
    # negative word pattern
    NEGATION_CUES = [
        r"\b(no|not|denies|denied|without|absent|negative for|"
        r"ruled out|no evidence of|non-)\b"
    ]
    
    # time pattern
    TIME_PATTERNS = [
        r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",  # MM/DD/YYYY
        r"\b(\d{4}-\d{2}-\d{2})\b",       # YYYY-MM-DD
        r"\b(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\b",  # time
        r"\b(on admission|at presentation|post-operatively|"
        r"pre-operatively|on day \d+|POD \#?\d+)\b"
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize MedicalTextMiner
        
        Args:
            config: configuration dictionary, which can include model path, output format and other settings"""
        self.config = config or {}
        self.notes_df: Optional[pd.DataFrame] = None
        self.nlp = None
        
        # Initialize spaCy model (if available)
        self._init_nlp()
        
    def _init_nlp(self):
        """Initialize NLP model"""
        if not SPACY_AVAILABLE:
            return
            
        model_name = self.config.get("ner_model", "en_core_web_sm")
        try:
            self.nlp = spacy.load(model_name)
            
            # Add negative detection component
            if NEGSPACY_AVAILABLE:
                negex = Negex(self.nlp, name="negex")
                self.nlp.add_pipe("negex", last=True)
                
        except OSError:
            warnings.warn(f"Model {model_name} not found. Running in regex-only mode.")
            self.nlp = None
    
    def load_notes(self, notes_path: Union[str, Path], 
                   note_types: Optional[List[str]] = None) -> pd.DataFrame:
        """Load MIMIC-IV NOTEEVENTS data
        
        Args:
            notes_path: NOTEEVENTS file path (CSV or Parquet)
            note_types: filter specific note types (such as ['DS', 'RR'])
            
        Returns:
            Loaded DataFrame"""
        path = Path(notes_path)
        
        if path.suffix == '.csv':
            df = pd.read_csv(path)
        elif path.suffix in ['.parquet', '.pq']:
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        # Standardized column names
        df.columns = df.columns.str.lower()
        
        # Filter note types
        if note_types and 'note_type' in df.columns:
            df = df[df['note_type'].isin(note_types)]
        
        # Convert time column
        if 'charttime' in df.columns:
            df['charttime'] = pd.to_datetime(df['charttime'], errors='coerce')
        
        self.notes_df = df
        print(f"Loaded {len(df)} notes from {path}")
        
        return df
    
    def get_patient_texts(self, subject_id: int, 
                          hadm_id: Optional[int] = None) -> List[Dict]:
        """Get all text records for a specific patient
        
        Args:
            subject_id: patient ID
            hadm_id: Optional hospitalization record ID
            
        Returns:
            List of text records for this patient"""
        if self.notes_df is None:
            raise ValueError("No notes loaded. Call load_notes() first.")
        
        mask = self.notes_df['subject_id'] == subject_id
        if hadm_id is not None:
            mask = mask & (self.notes_df['hadm_id'] == hadm_id)
        
        patient_notes = self.notes_df[mask].sort_values('charttime')
        
        return patient_notes.to_dict('records')
    
    def extract_entities_regex(self, text: str) -> List[Dict]:
        """Extract medical entities using regular expressions
        
        Args:
            text: input text
            
        Returns:
            Entity list"""
        entities = []
        
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = {
                        "text": match.group(),
                        "type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "source": "regex"
                    }
                    entities.append(entity)
        
        # check negative
        entities = self._detect_negation(text, entities)
        
        return entities
    
    def extract_entities_spacy(self, text: str) -> List[Dict]:
        """Extract medical entities using spaCy
        
        Args:
            text: input text
            
        Returns:
            Entity list"""
        if self.nlp is None:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity = {
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "source": "spacy"
            }
            
            # Check for negation (using negspacy)
            if NEGSPACY_AVAILABLE and hasattr(ent._, "negex"):
                entity["negated"] = ent._.negex
            
            entities.append(entity)
        
        return entities
    
    def _detect_negation(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Check if an entity is negated
        
        Args:
            text: original text
            entities: list of entities
            
        Returns:
            Entity list after adding negative tag"""
        for entity in entities:
            # Get the text window in front of the entity (up to 50 characters)
            start_pos = max(0, entity["start"] - 50)
            context = text[start_pos:entity["start"]]
            
            # Check for negative words
            is_negated = any(
                re.search(pattern, context, re.IGNORECASE)
                for pattern in self.NEGATION_CUES
            )
            entity["negated"] = is_negated
        
        return entities
    
    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships between entities from text
        
        Args:
            text: input text
            entities: list of recognized entities
            
        Returns:
            List of relational triples"""
        relations = []
        
        # Simple pattern-based relationship extraction
        # Drug-Disease Treatment Relationship
        med_disease_pattern = r"(\w+)\s+(?:for|to treat|management of)\s+([\w\s]+?)(?:\.|,|;|$)"
        for match in re.finditer(med_disease_pattern, text, re.IGNORECASE):
            relations.append({
                "subject": match.group(1),
                "predicate": "TREATS",
                "object": match.group(2).strip(),
                "confidence": 0.7,
                "source": "pattern"
            })
        
        # Symptom-disease relationship
        symptom_disease_pattern = r"(\w+)\s+(?:due to|caused by|secondary to)\s+([\w\s]+?)(?:\.|,|;|$)"
        for match in re.finditer(symptom_disease_pattern, text, re.IGNORECASE):
            relations.append({
                "subject": match.group(1),
                "predicate": "CAUSED_BY",
                "object": match.group(2).strip(),
                "confidence": 0.6,
                "source": "pattern"
            })
        
        return relations
    
    def extract_timeline(self, text: str) -> List[Dict]:
        """Extract timing events from text
        
        Args:
            text: input text
            
        Returns:
            event timeline"""
        events = []
        sentences = re.split(r'[.!?]\s+', text)
        
        event_indicators = [
            "admitted", "presented", "developed", "underwent", 
            "started", "discontinued", "noted", "observed",
            "worsening", "improvement", "resolved"
        ]
        
        for sent in sentences:
            # Detect time expression
            time_match = None
            for pattern in self.TIME_PATTERNS:
                match = re.search(pattern, sent, re.IGNORECASE)
                if match:
                    time_match = match.group()
                    break
            
            # detect event verb
            for indicator in event_indicators:
                if re.search(rf"\b{indicator}\b", sent, re.IGNORECASE):
                    events.append({
                        "time_expression": time_match,
                        "event_verb": indicator,
                        "description": sent.strip(),
                        "raw_time": time_match
                    })
                    break
        
        return events
    
    def parse_clinical_logic(self, text: str) -> Dict:
        """Analyze the diagnosis and treatment logic chain
        
        Args:
            text: medical text
            
        Returns:
            Logical structure of diagnosis and treatment"""
        logic = {
            "presenting_complaint": None,
            "differential_diagnoses": [],
            "workup": [],
            "final_diagnosis": None,
            "treatment_plan": [],
            "clinical_course": []
        }
        
        # Extract chief complaint
        chief_complaint_patterns = [
            r"chief complaint[:\s]+([^.]+)",
            r"presented with[:\s]+([^.]+)",
            r"\bPC[:\s]+([^.]+)"
        ]
        for pattern in chief_complaint_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logic["presenting_complaint"] = match.group(1).strip()
                break
        
        # Extract differential diagnosis
        dd_pattern = r"(?:differential diagnosis|DDx)[:\s]+([^.]+(?:,[^.]+)*)"
        match = re.search(dd_pattern, text, re.IGNORECASE)
        if match:
            logic["differential_diagnoses"] = [
                d.strip() for d in match.group(1).split(",")
            ]
        
        # Extract check
        workup_indicators = ["obtained", "performed", "ordered", "showed"]
        for indicator in workup_indicators:
            pattern = rf"(\w+(?:\s\w+)?)\s+{indicator}"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                procedure = match.group(1)
                if procedure.lower() in [
                    "ecg", "ekg", "ct", "mri", "x-ray", "echo", 
                    "troponin", "bnp", "wbc"
                ]:
                    logic["workup"].append(procedure)
        
        # Remove duplicates
        logic["workup"] = list(set(logic["workup"]))
        
        return logic
    
    def extract_insights(self, text: str,
                        extract_entities: bool = True,
                        extract_relations: bool = True,
                        extract_timeline: bool = True,
                        extract_logic: bool = True) -> Dict:
        """Perform complete medical text insight extraction
        
        Args:
            text: Enter medical text
            extract_entities: whether to extract entities
            extract_relations: whether to extract relationships
            extract_timeline: whether to extract timeline
            extract_logic: whether to parse diagnosis and treatment logic
            
        Returns:
            Comprehensive insights"""
        insights = {
            "raw_text_length": len(text),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Entity extraction
        if extract_entities:
            entities_regex = self.extract_entities_regex(text)
            entities_spacy = self.extract_entities_spacy(text)
            
            # Merge results (remove duplicates)
            all_entities = entities_regex + [
                e for e in entities_spacy
                if not any(e["start"] == ex["start"] for ex in entities_regex)
            ]
            
            # Group by type
            entities_by_type = {}
            for e in all_entities:
                etype = e["type"]
                if etype not in entities_by_type:
                    entities_by_type[etype] = []
                entities_by_type[etype].append(e)
            
            insights["entities"] = all_entities
            insights["entities_by_type"] = entities_by_type
            insights["entity_count"] = len(all_entities)
        
        # Relation extraction
        if extract_relations and extract_entities:
            relations = self.extract_relations(text, insights.get("entities", []))
            insights["relations"] = relations
            insights["relation_count"] = len(relations)
        
        # Timeline extraction
        if extract_timeline:
            timeline = self.extract_timeline(text)
            insights["timeline"] = timeline
            insights["event_count"] = len(timeline)
        
        # Diagnosis and treatment logic analysis
        if extract_logic:
            logic = self.parse_clinical_logic(text)
            insights["clinical_logic"] = logic
        
        return insights
    
    def process_patient(self, subject_id: int, 
                       hadm_id: Optional[int] = None) -> Dict:
        """Process all text records for a single patient
        
        Args:
            subject_id: patient ID
            hadm_id: Optional hospitalization record ID
            
        Returns:
            Comprehensive Patient Insights"""
        notes = self.get_patient_texts(subject_id, hadm_id)
        
        patient_insights = {
            "subject_id": subject_id,
            "hadm_id": hadm_id,
            "note_count": len(notes),
            "notes": []
        }
        
        for note in notes:
            text = note.get('note_text', '')
            if not text:
                continue
            
            note_insights = self.extract_insights(text)
            note_insights.update({
                "note_id": note.get('note_id'),
                "note_type": note.get('note_type'),
                "charttime": note.get('charttime')
            })
            
            patient_insights["notes"].append(note_insights)
        
        # Aggregate all entities
        all_entities = []
        for note in patient_insights["notes"]:
            all_entities.extend(note.get("entities", []))
        
        patient_insights["aggregated_entities"] = self._aggregate_entities(all_entities)
        
        return patient_insights
    
    def _aggregate_entities(self, entities: List[Dict]) -> Dict:
        """Aggregate entities (deduplication and counting)"""
        entity_map = {}
        
        for e in entities:
            key = (e["text"].lower(), e["type"])
            if key not in entity_map:
                entity_map[key] = {
                    "text": e["text"],
                    "type": e["type"],
                    "count": 0,
                    "negated_count": 0,
                    "instances": []
                }
            
            entity_map[key]["count"] += 1
            if e.get("negated"):
                entity_map[key]["negated_count"] += 1
            entity_map[key]["instances"].append({
                "start": e["start"],
                "end": e["end"]
            })
        
        return {
            "unique_count": len(entity_map),
            "entities": list(entity_map.values())
        }
    
    def export_to_json(self, insights: Dict, output_path: str):
        """Export insights results to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        print(f"Exported insights to {output_path}")
    
    def generate_summary_report(self, insights: Dict) -> str:
        """Generate text summary report"""
        report = []
        report.append("=" * 60)
        report.append("MEDICAL TEXT MINING SUMMARY REPORT")
        report.append("=" * 60)
        
        if "subject_id" in insights:
            report.append(f"\nPatient ID: {insights['subject_id']}")
        
        if "note_count" in insights:
            report.append(f"Total Notes Processed: {insights['note_count']}")
        
        if "aggregated_entities" in insights:
            agg = insights["aggregated_entities"]
            report.append(f"\nUnique Entities Found: {agg['unique_count']}")
            
            # Display grouped by type
            by_type = {}
            for e in agg["entities"]:
                t = e["type"]
                if t not in by_type:
                    by_type[t] = []
                by_type[t].append(e)
            
            for etype, entities in sorted(by_type.items()):
                report.append(f"\n{etype} ({len(entities)} unique):")
                for e in sorted(entities, key=lambda x: -x["count"])[:5]:
                    neg_info = f", {e['negated_count']} negated" if e['negated_count'] > 0 else ""
                    report.append(f"  - {e['text']} ({e['count']} mentions{neg_info})")
        
        return "\n".join(report)


def main():
    """CLI entry"""
    parser = argparse.ArgumentParser(
        description="MIMIC-IV Unstructured Medical Text Miner"
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to NOTEEVENTS CSV/Parquet file"
    )
    parser.add_argument(
        "--subject-id", "-s", type=int,
        help="Process specific patient by subject_id"
    )
    parser.add_argument(
        "--hadm-id", type=int,
        help="Filter by hospital admission ID"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--extract", choices=["entities", "relations", "timeline", "logic", "all"],
        default="all",
        help="What to extract from the text"
    )
    parser.add_argument(
        "--note-types", nargs="+",
        help="Filter by note types (e.g., DS RR ECG)"
    )
    parser.add_argument(
        "--sample-text",
        help="Process a single text snippet directly"
    )
    
    args = parser.parse_args()
    
    miner = MedicalTextMiner()
    
    # Process individual text fragments
    if args.sample_text:
        insights = miner.extract_insights(args.sample_text)
        print(json.dumps(insights, indent=2, default=str))
        return
    
    # Requires input files
    if not args.input:
        parser.error("--input is required (unless using --sample-text)")
    
    # Load data
    miner.load_notes(args.input, args.note_types)
    
    # Process specific patients or batch processing
    if args.subject_id:
        insights = miner.process_patient(args.subject_id, args.hadm_id)
    else:
        # Handle all patients (simplified version)
        print("Processing all patients...")
        all_insights = []
        for sid in miner.notes_df['subject_id'].unique()[:10]:  # Limit to first 10 patients
            patient_insights = miner.process_patient(sid)
            all_insights.append(patient_insights)
        insights = {
            "patient_count": len(all_insights),
            "patients": all_insights
        }
    
    # Generate summary
    print("\n" + miner.generate_summary_report(insights))
    
    # Export results
    if args.output:
        miner.export_to_json(insights, args.output)
    else:
        # Default output
        default_output = "medical_text_insights.json"
        miner.export_to_json(insights, default_output)


if __name__ == "__main__":
    main()
