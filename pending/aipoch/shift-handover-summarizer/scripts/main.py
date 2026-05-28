#!/usr/bin/env python3
"""
Shift Handover Summarizer (ID: 168)
Generate shift handover summaries based on EMR updates, highlighting key events during the shift
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class EventPriority(Enum):
    """Event priority level"""
    HIGH = "high"       # High risk / urgent
    MEDIUM = "medium"   # Medium / needs attention
    LOW = "low"         # Low / routine


class RecordType(Enum):
    """Medical record type"""
    VITAL_SIGNS = "vital_signs"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    EVENT = "event"
    NOTE = "note"


@dataclass
class VitalSigns:
    """Vital signs data"""
    heart_rate: Optional[int] = None
    blood_pressure: Optional[str] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    spo2: Optional[int] = None
    timestamp: Optional[str] = None


@dataclass
class KeyEvent:
    """Key clinical event"""
    timestamp: str
    type: str
    description: str
    severity: EventPriority
    action_taken: Optional[str] = None


@dataclass
class PatientSummary:
    """Individual patient summary"""
    patient_id: str
    patient_name: str
    bed_number: str
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    priority: EventPriority = EventPriority.LOW
    key_events: List[KeyEvent] = field(default_factory=list)
    vitals_summary: Dict[str, Any] = field(default_factory=dict)
    medication_summary: List[Dict] = field(default_factory=list)
    procedure_summary: List[Dict] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)


@dataclass
class ShiftSummary:
    """Shift summary"""
    shift_period: Dict[str, str]
    generated_at: str
    total_patients: int
    critical_patients: int
    department: Optional[str] = None
    summary_text: str = ""
    patients: List[PatientSummary] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        # Convert enum values
        for patient in result.get('patients', []):
            if isinstance(patient.get('priority'), EventPriority):
                patient['priority'] = patient['priority'].value
            for event in patient.get('key_events', []):
                if isinstance(event.get('severity'), EventPriority):
                    event['severity'] = event['severity'].value
        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class ShiftHandoverSummarizer:
    """Shift handover summary generator"""

    # Default threshold configuration
    DEFAULT_THRESHOLDS = {
        "high_heart_rate": 120,
        "low_heart_rate": 50,
        "high_systolic_bp": 180,
        "low_systolic_bp": 90,
        "high_temperature": 38.5,
        "low_spo2": 90
    }

    # Key event keywords
    EVENT_KEYWORDS = {
        EventPriority.HIGH: ["resuscitation", "cardiac arrest", "respiratory distress", "major hemorrhage", "coma", "shock", "asphyxia"],
        EventPriority.MEDIUM: ["chest pain", "dizziness", "nausea", "fever", "blood pressure fluctuation", "vomiting", "palpitations"]
    }

    def __init__(
        self,
        shift_start: str,
        shift_end: str,
        department: Optional[str] = None,
        thresholds: Optional[Dict] = None,
        include_vitals: bool = True,
        include_medications: bool = True,
        include_procedures: bool = True,
        language: str = "zh-CN"
    ):
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.department = department
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.include_vitals = include_vitals
        self.include_medications = include_medications
        self.include_procedures = include_procedures
        self.language = language

    def generate_summary(self, patient_records: List[Dict]) -> ShiftSummary:
        """Generate shift handover summary"""
        patient_summaries = []
        critical_count = 0

        for record in patient_records:
            patient_summary = self._analyze_patient(record)
            patient_summaries.append(patient_summary)
            if patient_summary.priority == EventPriority.HIGH:
                critical_count += 1

        # Sort by priority
        patient_summaries.sort(key=lambda x: (
            0 if x.priority == EventPriority.HIGH else
            1 if x.priority == EventPriority.MEDIUM else 2
        ))

        # Generate statistics
        statistics = self._generate_statistics(patient_summaries)

        # Generate text summary
        summary_text = self._generate_summary_text(patient_summaries, statistics)

        return ShiftSummary(
            shift_period={
                "start": self.shift_start,
                "end": self.shift_end
            },
            generated_at=datetime.now().isoformat(),
            total_patients=len(patient_summaries),
            critical_patients=critical_count,
            department=self.department,
            summary_text=summary_text,
            patients=patient_summaries,
            statistics=statistics
        )

    def _analyze_patient(self, record: Dict) -> PatientSummary:
        """Analyze a single patient record"""
        patient_id = record.get("patient_id", "")
        patient_name = record.get("patient_name", "")
        bed_number = record.get("bed_number", "")
        
        summary = PatientSummary(
            patient_id=patient_id,
            patient_name=patient_name,
            bed_number=bed_number,
            age=record.get("age"),
            gender=record.get("gender"),
            diagnosis=record.get("diagnosis", "")
        )

        records = record.get("records", [])
        key_events = []
        max_priority = EventPriority.LOW

        for rec in records:
            event = self._analyze_record(rec)
            if event:
                key_events.append(event)
                if self._priority_value(event.severity) > self._priority_value(max_priority):
                    max_priority = event.severity

            # Collect summary information by type
            rec_type = rec.get("type", "")
            if rec_type == RecordType.VITAL_SIGNS.value and self.include_vitals:
                self._collect_vitals(summary, rec)
            elif rec_type == RecordType.MEDICATION.value and self.include_medications:
                self._collect_medication(summary, rec)
            elif rec_type == RecordType.PROCEDURE.value and self.include_procedures:
                self._collect_procedure(summary, rec)

        summary.key_events = key_events
        summary.priority = max_priority
        summary.pending_tasks = self._generate_pending_tasks(summary)

        return summary

    def _analyze_record(self, record: Dict) -> Optional[KeyEvent]:
        """Analyze a single record and extract key events"""
        rec_type = record.get("type", "")
        timestamp = record.get("timestamp", "")
        data = record.get("data", {})
        severity = record.get("severity", "")

        # Analyze by type
        if rec_type == RecordType.EVENT.value:
            return self._analyze_event_record(record)
        elif rec_type == RecordType.VITAL_SIGNS.value:
            return self._analyze_vitals_record(record)
        elif rec_type == RecordType.PROCEDURE.value:
            return self._analyze_procedure_record(record)
        elif rec_type == RecordType.MEDICATION.value:
            return self._analyze_medication_record(record)

        return None

    def _analyze_event_record(self, record: Dict) -> Optional[KeyEvent]:
        """Analyze event record"""
        data = record.get("data", {})
        description = data.get("description", "")
        severity_str = record.get("severity", "medium")
        
        severity = EventPriority(severity_str) if severity_str in ["high", "medium", "low"] else EventPriority.MEDIUM
        
        # Adjust priority based on keywords
        if any(kw in description for kw in self.EVENT_KEYWORDS[EventPriority.HIGH]):
            severity = EventPriority.HIGH

        return KeyEvent(
            timestamp=record.get("timestamp", ""),
            type="Event",
            description=description,
            severity=severity,
            action_taken=data.get("action_taken", "")
        )

    def _analyze_vitals_record(self, record: Dict) -> Optional[KeyEvent]:
        """Analyze vital signs record and detect abnormalities"""
        data = record.get("data", {})
        abnormalities = []
        severity = EventPriority.LOW

        # Check heart rate
        hr = data.get("heart_rate")
        if hr:
            if hr > self.thresholds["high_heart_rate"]:
                abnormalities.append(f"Tachycardia ({hr} bpm)")
                severity = EventPriority.MEDIUM
            elif hr < self.thresholds["low_heart_rate"]:
                abnormalities.append(f"Bradycardia ({hr} bpm)")
                severity = EventPriority.MEDIUM

        # Check blood pressure
        bp = data.get("blood_pressure")
        if bp:
            try:
                systolic = int(bp.split("/")[0])
                if systolic > self.thresholds["high_systolic_bp"]:
                    abnormalities.append(f"Hypertension ({bp})")
                    severity = EventPriority.MEDIUM
                elif systolic < self.thresholds["low_systolic_bp"]:
                    abnormalities.append(f"Hypotension ({bp})")
                    severity = EventPriority.MEDIUM
            except:
                pass

        # Check temperature
        temp = data.get("temperature")
        if temp and temp > self.thresholds["high_temperature"]:
            abnormalities.append(f"Fever ({temp}°C)")
            severity = EventPriority.MEDIUM

        # Check SpO2
        spo2 = data.get("spo2")
        if spo2 and spo2 < self.thresholds["low_spo2"]:
            abnormalities.append(f"Low SpO2 ({spo2}%)")
            severity = EventPriority.HIGH

        if abnormalities:
            return KeyEvent(
                timestamp=record.get("timestamp", ""),
                type="Abnormal Vital Signs",
                description="; ".join(abnormalities),
                severity=severity
            )
        return None

    def _analyze_procedure_record(self, record: Dict) -> Optional[KeyEvent]:
        """Analyze procedure/examination record"""
        data = record.get("data", {})
        procedure_name = data.get("procedure_name", "")
        result = data.get("result", "")

        # Check for abnormal result keywords
        if result and any(kw in result for kw in ["abnormal", "positive", "critical", "severe"]):
            return KeyEvent(
                timestamp=record.get("timestamp", ""),
                type="Abnormal Exam Result",
                description=f"{procedure_name}: {result}",
                severity=EventPriority.MEDIUM
            )
        return None

    def _analyze_medication_record(self, record: Dict) -> Optional[KeyEvent]:
        """Analyze medication record"""
        # Currently only logs medication info, not treated as a key event
        return None

    def _collect_vitals(self, summary: PatientSummary, record: Dict):
        """Collect vital signs information"""
        data = record.get("data", {})
        timestamp = record.get("timestamp", "")
        
        if "latest_vitals" not in summary.vitals_summary:
            summary.vitals_summary["latest_vitals"] = {}
            summary.vitals_summary["latest_timestamp"] = timestamp

        summary.vitals_summary["latest_vitals"].update(data)

    def _collect_medication(self, summary: PatientSummary, record: Dict):
        """Collect medication information"""
        data = record.get("data", {})
        summary.medication_summary.append({
            "timestamp": record.get("timestamp", ""),
            **data
        })

    def _collect_procedure(self, summary: PatientSummary, record: Dict):
        """Collect procedure information"""
        data = record.get("data", {})
        summary.procedure_summary.append({
            "timestamp": record.get("timestamp", ""),
            **data
        })

    def _generate_pending_tasks(self, summary: PatientSummary) -> List[str]:
        """Generate pending task suggestions"""
        tasks = []
        
        # Generate tasks based on key events
        for event in summary.key_events:
            if event.severity == EventPriority.HIGH:
                tasks.append(f"Continue monitoring: {event.description}")
        
        # Generate tasks based on vital signs
        vitals = summary.vitals_summary.get("latest_vitals", {})
        if vitals.get("spo2", 100) < self.thresholds["low_spo2"]:
            tasks.append("Intensify oxygen therapy monitoring")
        
        # Routine tasks
        if summary.diagnosis:
            tasks.append(f"Monitor symptoms related to {summary.diagnosis}")
        
        if not tasks:
            tasks.append("Routine monitoring")
        
        return tasks

    def _generate_statistics(self, summaries: List[PatientSummary]) -> Dict:
        """Generate statistics"""
        stats = {
            "new_admissions": 0,
            "transfers_out": 0,
            "resuscitations": 0,
            "surgeries": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0
        }

        for summary in summaries:
            if summary.priority == EventPriority.HIGH:
                stats["high_priority"] += 1
            elif summary.priority == EventPriority.MEDIUM:
                stats["medium_priority"] += 1
            else:
                stats["low_priority"] += 1

            # Count resuscitation events
            for event in summary.key_events:
                if "resuscitation" in event.description or "cardiac arrest" in event.description:
                    stats["resuscitations"] += 1

        return stats

    def _generate_summary_text(self, summaries: List[PatientSummary], stats: Dict) -> str:
        """Generate text-format summary"""
        lines = []
        
        # Title
        dept_str = f"[{self.department}] " if self.department else ""
        lines.append(f"{dept_str}Shift Handover Summary {self.shift_start[:10]} {self.shift_start[11:16]} - {self.shift_end[11:16]}")
        lines.append("")

        # Priority patients
        high_priority = [s for s in summaries if s.priority == EventPriority.HIGH]
        medium_priority = [s for s in summaries if s.priority == EventPriority.MEDIUM]
        low_priority = [s for s in summaries if s.priority == EventPriority.LOW]

        if high_priority:
            lines.append("[HIGH PRIORITY PATIENTS]")
            for s in high_priority:
                lines.extend(self._format_patient_summary(s, "[HIGH]"))
            lines.append("")

        if medium_priority:
            lines.append("[PATIENTS REQUIRING ATTENTION]")
            for s in medium_priority:
                lines.extend(self._format_patient_summary(s, "[MED]"))
            lines.append("")

        if low_priority:
            bed_numbers = [s.bed_number for s in low_priority]
            lines.append("[STABLE PATIENTS]")
            lines.append(f"Beds {', '.join(bed_numbers)}: Condition stable, routine treatment ongoing")
            lines.append("")

        # Statistics
        lines.append("[SHIFT OVERVIEW]")
        lines.append(f"- Total patients: {len(summaries)}")
        lines.append(f"- High priority: {stats['high_priority']}")
        lines.append(f"- Resuscitations: {stats['resuscitations']}")
        lines.append(f"- Surgeries: {stats['surgeries']}")

        return "\n".join(lines)

    def _format_patient_summary(self, summary: PatientSummary, icon: str) -> List[str]:
        """Format individual patient summary"""
        lines = []
        
        # Basic info
        info_parts = [f"Bed {summary.bed_number}", summary.patient_name]
        if summary.gender:
            info_parts.append(f"({summary.gender}")
            if summary.age:
                info_parts[-1] += f", {summary.age}y"
            info_parts[-1] += ")"
        if summary.diagnosis:
            info_parts.append(f"- {summary.diagnosis}")
        
        lines.append(f"{icon} {' '.join(info_parts)}")

        # Key events
        for event in summary.key_events:
            time_str = event.timestamp[11:16] if len(event.timestamp) > 16 else ""
            event_icon = "[!]" if event.severity == EventPriority.HIGH else "[*]"
            lines.append(f"   {event_icon} {time_str} {event.type}: {event.description}")
            if event.action_taken:
                lines.append(f"      -> Action: {event.action_taken}")

        # Vital signs summary
        if self.include_vitals and summary.vitals_summary.get("latest_vitals"):
            vitals = summary.vitals_summary["latest_vitals"]
            vital_strs = []
            if vitals.get("blood_pressure"):
                vital_strs.append(f"BP {vitals['blood_pressure']}")
            if vitals.get("heart_rate"):
                vital_strs.append(f"HR {vitals['heart_rate']}")
            if vitals.get("spo2"):
                vital_strs.append(f"SpO2 {vitals['spo2']}%")
            if vital_strs:
                lines.append(f"   Vitals: {', '.join(vital_strs)}")

        # Pending tasks
        if summary.pending_tasks:
            lines.append(f"   Pending: {'; '.join(summary.pending_tasks[:2])}")

        return lines

    @staticmethod
    def _priority_value(priority: EventPriority) -> int:
        """Get numeric priority value"""
        return {"high": 3, "medium": 2, "low": 1}.get(priority.value, 0)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Shift Handover Summarizer")
    parser.add_argument("--records", "-r", required=True, help="Patient records JSON file path")
    parser.add_argument("--shift-start", "-s", required=True, help="Shift start time (ISO 8601)")
    parser.add_argument("--shift-end", "-e", required=True, help="Shift end time (ISO 8601)")
    parser.add_argument("--department", "-d", help="Department name")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--no-vitals", action="store_true", help="Exclude vital signs")
    parser.add_argument("--no-medications", action="store_true", help="Exclude medication info")
    parser.add_argument("--no-procedures", action="store_true", help="Exclude procedure info")

    args = parser.parse_args()

    # Read patient records
    with open(args.records, "r", encoding="utf-8") as f:
        patient_records = json.load(f)

    # Create summarizer
    summarizer = ShiftHandoverSummarizer(
        shift_start=args.shift_start,
        shift_end=args.shift_end,
        department=args.department,
        include_vitals=not args.no_vitals,
        include_medications=not args.no_medications,
        include_procedures=not args.no_procedures
    )

    # Generate summary
    summary = summarizer.generate_summary(patient_records)

    # Output result
    output = {
        "success": True,
        "shift_summary": summary.to_dict()
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Summary saved to: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
