#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Term database management module
Provides Chinese-English comparison, abbreviation specifications and synonyms unification functions for professional terms"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class IssueSeverity(Enum):
    """problem severity"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(Enum):
    """Question Category"""

    TERMINOLOGY = "terminology"
    ABBREVIATION = "abbreviation"
    CONSISTENCY = "consistency"
    CAPITALIZATION = "capitalization"


@dataclass
class TerminologyIssue:
    """Terminology check issue record"""

    type: str
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    start: int = 0
    end: int = 0
    line: int = 1
    severity: IssueSeverity = IssueSeverity.WARNING
    term_data: Optional[Dict] = None


@dataclass
class Term:
    """Terminology data"""

    en: str
    zh: str
    abbrev: Optional[str] = None
    full_form: Optional[str] = None
    domain: str = "general"
    variants: List[str] = field(default_factory=list)
    related_terms: List[str] = field(default_factory=list)
    source: Optional[str] = None
    notes: Optional[str] = None


class TerminologyManager:
    """Termbase Manager"""

    def __init__(
        self,
        domain: str = "biology",
        custom_terminology_path: Optional[str] = None,
        strict: bool = False,
    ):
        self.domain = domain
        self.strict = strict
        self.terminology: Dict[str, Dict[str, Term]] = {}
        self.abbreviations: Dict[str, Dict[str, str]] = {}
        self.glossary_index: Dict[str, Set[str]] = {}

        self.base_path = Path(__file__).parent.parent
        self.terminology_path = self.base_path / "assets" / "terminology"
        self.rules_path = self.base_path / "assets" / "rules"

        self._load_default_terminology()
        self._load_domain_terminology(domain)

        if custom_terminology_path:
            self._load_custom_terminology(custom_terminology_path)

    def _load_default_terminology(self):
        """Load default termbase"""
        default_files = [
            "biology.json",
            "medicine.json",
            "chemistry.json",
            "physics.json",
        ]

        for filename in default_files:
            filepath = self.terminology_path / filename
            if filepath.exists():
                self._load_terminology_file(filepath)

    def _load_domain_terminology(self, domain: str):
        """Load the specified domain terminology database"""
        domain_file = self.terminology_path / f"{domain}.json"
        if domain_file.exists():
            self._load_terminology_file(domain_file)
        else:
            self._create_default_terminology(domain)

    def _load_terminology_file(self, filepath: Path):
        """Load terminology file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for category, terms in data.items():
                if category not in self.terminology:
                    self.terminology[category] = {}

                for term_key, term_data in terms.items():
                    term = Term(
                        en=term_data.get("en", ""),
                        zh=term_data.get("zh", ""),
                        abbrev=term_data.get("abbrev"),
                        full_form=term_data.get("full_form"),
                        domain=term_data.get("domain", self.domain),
                        variants=term_data.get("variants", []),
                        related_terms=term_data.get("related_terms", []),
                        source=term_data.get("source"),
                        notes=term_data.get("notes"),
                    )
                    self.terminology[category][term_key] = term

                    self._index_term(term)

        except Exception as e:
            print(f"warn: Unable to load terminology file {filepath}: {e}")

    def _index_term(self, term: Term):
        """Index terms"""
        self.glossary_index.setdefault(term.en.lower(), set()).add(term.en)
        if term.zh:
            self.glossary_index.setdefault(term.zh, set()).add(term.zh)
        if term.abbrev:
            self.glossary_index.setdefault(term.abbrev.lower(), set()).add(term.abbrev)
        for variant in term.variants:
            self.glossary_index.setdefault(variant.lower(), set()).add(variant)

    def _create_default_terminology(self, domain: str):
        """Create a default termbase"""
        if domain == "biology":
            default_terms = self._get_biology_terms()
        elif domain == "medicine":
            default_terms = self._get_medicine_terms()
        elif domain == "chemistry":
            default_terms = self._get_chemistry_terms()
        elif domain == "physics":
            default_terms = self._get_physics_terms()
        else:
            default_terms = {}

        for category, terms in default_terms.items():
            if category not in self.terminology:
                self.terminology[category] = {}

            for term_key, term_data in terms.items():
                self.terminology[category][term_key] = Term(**term_data)
                self._index_term(self.terminology[category][term_key])

    def _get_biology_terms(self) -> Dict:
        """Get biology default terms"""
        return {
            "molecular": {
                "dna": {
                    "en": "DNA",
                    "zh": "DNA",
                    "abbrev": "DNA",
                    "full_form": "deoxyribonucleic acid",
                    "domain": "biology",
                    "variants": ["Deoxyribonucleic acid", "deoxyribonucleic acid"],
                    "related_terms": ["RNA", "gene", "chromosome"],
                    "source": "IUPAC",
                },
                "rna": {
                    "en": "RNA",
                    "zh": "RNA",
                    "abbrev": "RNA",
                    "full_form": "ribonucleic acid",
                    "domain": "biology",
                    "variants": ["Ribonucleic acid", "ribonucleic acid"],
                    "related_terms": ["DNA", "mRNA", "transcription"],
                    "source": "IUPAC",
                },
                "mrna": {
                    "en": "mRNA",
                    "zh": "messenger RNA",
                    "abbrev": "mRNA",
                    "full_form": "messenger RNA",
                    "domain": "biology",
                    "variants": ["messenger RNA", "Messenger RNA"],
                    "related_terms": ["RNA", "translation", "protein"],
                    "source": "IUPAC",
                },
                "trna": {
                    "en": "tRNA",
                    "zh": "transfer RNA",
                    "abbrev": "tRNA",
                    "full_form": "transfer RNA",
                    "domain": "biology",
                    "variants": ["transfer RNA", "Transfer RNA"],
                    "related_terms": ["RNA", "amino acid", "translation"],
                    "source": "IUPAC",
                },
                "rrna": {
                    "en": "rRNA",
                    "zh": "Ribosomal RNA",
                    "abbrev": "rRNA",
                    "full_form": "ribosomal RNA",
                    "domain": "biology",
                    "variants": ["ribosomal RNA", "Ribosomal RNA"],
                    "related_terms": ["RNA", "ribosome", "translation"],
                    "source": "IUPAC",
                },
                "gene": {
                    "en": "gene",
                    "zh": "Gene",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Gene", "genes"],
                    "related_terms": ["DNA", "chromosome", "allele"],
                    "source": "IUPAC",
                },
                "protein": {
                    "en": "protein",
                    "zh": "protein",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Protein", "proteins"],
                    "related_terms": ["amino acid", "polypeptide", "enzyme"],
                    "source": "IUPAC",
                },
                "enzyme": {
                    "en": "enzyme",
                    "zh": "enzyme",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Enzyme", "enzymes"],
                    "related_terms": ["catalyst", "substrate", "reaction"],
                    "source": "IUPAC",
                },
                "amino_acid": {
                    "en": "amino acid",
                    "zh": "amino acids",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["aminoacid", "amino-acid"],
                    "related_terms": ["protein", "peptide", "nitrogen"],
                    "source": "IUPAC",
                },
                "nucleotide": {
                    "en": "nucleotide",
                    "zh": "Nucleotide",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Nucleotide", "nucleotides"],
                    "related_terms": ["DNA", "RNA", "nucleoside"],
                    "source": "IUPAC",
                },
            },
            "cellular": {
                "cell": {
                    "en": "cell",
                    "zh": "cell",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Cell", "cells"],
                    "related_terms": ["tissue", "organelle", "membrane"],
                    "source": "IUPAC",
                },
                "organelle": {
                    "en": "organelle",
                    "zh": "organelles",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Organelle", "organelles"],
                    "related_terms": ["cell", "mitochondria", "nucleus"],
                    "source": "IUPAC",
                },
                "mitochondria": {
                    "en": "mitochondrion",
                    "zh": "Mitochondria",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["mitochondria", "Mitochondria", "mitochondrion"],
                    "related_terms": ["cell", "ATP", "respiration"],
                    "source": "IUPAC",
                },
                "nucleus": {
                    "en": "nucleus",
                    "zh": "cell nucleus",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Nucleus", "nuclei"],
                    "related_terms": ["cell", "DNA", "chromosome"],
                    "source": "IUPAC",
                },
                "membrane": {
                    "en": "membrane",
                    "zh": "membrane",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Membrane", "membranes"],
                    "related_terms": ["cell", "lipid", "protein"],
                    "source": "IUPAC",
                },
                "cytoplasm": {
                    "en": "cytoplasm",
                    "zh": "cytoplasm",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Cytoplasm", "cytosol"],
                    "related_terms": ["cell", "organelle", "cytoskeleton"],
                    "source": "IUPAC",
                },
                "ribosome": {
                    "en": "ribosome",
                    "zh": "Ribosomes",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Ribosome", "ribosomes"],
                    "related_terms": ["RNA", "protein", "translation"],
                    "source": "IUPAC",
                },
                "chromosome": {
                    "en": "chromosome",
                    "zh": "chromosome",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Chromosome", "chromosomes"],
                    "related_terms": ["DNA", "gene", "nucleus"],
                    "source": "IUPAC",
                },
            },
            "genetics": {
                "genome": {
                    "en": "genome",
                    "zh": "genome",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Genome", "genomes"],
                    "related_terms": ["gene", "DNA", "chromosome"],
                    "source": "IUPAC",
                },
                "mutation": {
                    "en": "mutation",
                    "zh": "mutation",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Mutation", "mutations"],
                    "related_terms": ["gene", "DNA", "variation"],
                    "source": "IUPAC",
                },
                "allele": {
                    "en": "allele",
                    "zh": "allele",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Allele", "alleles"],
                    "related_terms": ["gene", "genotype", "phenotype"],
                    "source": "IUPAC",
                },
                "genotype": {
                    "en": "genotype",
                    "zh": "genotype",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Genotype", "genotypes"],
                    "related_terms": ["allele", "phenotype", "gene"],
                    "source": "IUPAC",
                },
                "phenotype": {
                    "en": "phenotype",
                    "zh": "Phenotype",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Phenotype", "phenotypes"],
                    "related_terms": ["genotype", "trait", "gene"],
                    "source": "IUPAC",
                },
                "transcription": {
                    "en": "transcription",
                    "zh": "Transcribe",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Transcription"],
                    "related_terms": ["RNA", "DNA", "gene expression"],
                    "source": "IUPAC",
                },
                "translation": {
                    "en": "translation",
                    "zh": "translate",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Translation"],
                    "related_terms": ["RNA", "protein", "ribosome"],
                    "source": "IUPAC",
                },
            },
            "ecology": {
                "ecosystem": {
                    "en": "ecosystem",
                    "zh": "ecosystem",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Ecosystem", "ecosystems"],
                    "related_terms": ["ecology", "habitat", "species"],
                    "source": "IUPAC",
                },
                "habitat": {
                    "en": "habitat",
                    "zh": "habitat",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Habitat", "habitats"],
                    "related_terms": ["ecosystem", "species", "environment"],
                    "source": "IUPAC",
                },
                "species": {
                    "en": "species",
                    "zh": "Species",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Species", "spp."],
                    "related_terms": ["population", "genus", "biodiversity"],
                    "source": "IUPAC",
                },
                "biodiversity": {
                    "en": "biodiversity",
                    "zh": "biodiversity",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "biology",
                    "variants": ["Biodiversity", "biological diversity"],
                    "related_terms": ["species", "ecosystem", "conservation"],
                    "source": "IUPAC",
                },
            },
        }

    def _get_medicine_terms(self) -> Dict:
        """Get medical default terms"""
        return {
            "anatomy": {
                "heart": {
                    "en": "heart",
                    "zh": "heart",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "medicine",
                    "variants": ["Heart", "cardiac"],
                    "related_terms": ["cardiovascular", "artery", "blood"],
                    "source": "IUPAC",
                },
                "liver": {
                    "en": "liver",
                    "zh": "liver",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "medicine",
                    "variants": ["Liver", "hepatic"],
                    "related_terms": ["hepatocyte", "bile", "detoxification"],
                    "source": "IUPAC",
                },
            },
            "pathology": {
                "disease": {
                    "en": "disease",
                    "zh": "disease",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "medicine",
                    "variants": ["Disease", "disorder", "condition"],
                    "related_terms": ["symptom", "diagnosis", "treatment"],
                    "source": "IUPAC",
                },
                "diagnosis": {
                    "en": "diagnosis",
                    "zh": "diagnosis",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "medicine",
                    "variants": ["Diagnosis", "diagnoses"],
                    "related_terms": ["symptom", "test", "prognosis"],
                    "source": "IUPAC",
                },
            },
            "pharmacology": {
                "drug": {
                    "en": "drug",
                    "zh": "drug",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "medicine",
                    "variants": ["Drug", "medication", "medicine"],
                    "related_terms": ["pharmacology", "treatment", "therapy"],
                    "source": "IUPAC",
                },
                "therapy": {
                    "en": "therapy",
                    "zh": "treat",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "medicine",
                    "variants": ["Therapy", "treatment"],
                    "related_terms": ["drug", "diagnosis", "prognosis"],
                    "source": "IUPAC",
                },
            },
        }

    def _get_chemistry_terms(self) -> Dict:
        """Get chemical default terms"""
        return {
            "organic": {
                "molecule": {
                    "en": "molecule",
                    "zh": "molecular",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "chemistry",
                    "variants": ["Molecule", "molecules"],
                    "related_terms": ["atom", "bond", "compound"],
                    "source": "IUPAC",
                },
                "compound": {
                    "en": "compound",
                    "zh": "compound",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "chemistry",
                    "variants": ["Compound", "compounds"],
                    "related_terms": ["molecule", "element", "reaction"],
                    "source": "IUPAC",
                },
                "reaction": {
                    "en": "reaction",
                    "zh": "reaction",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "chemistry",
                    "variants": ["Reaction", "reactions"],
                    "related_terms": ["compound", "catalyst", "equilibrium"],
                    "source": "IUPAC",
                },
            },
            "physical": {
                "atom": {
                    "en": "atom",
                    "zh": "atom",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "chemistry",
                    "variants": ["Atom", "atoms"],
                    "related_terms": ["element", "molecule", "nucleus"],
                    "source": "IUPAC",
                },
                "element": {
                    "en": "element",
                    "zh": "element",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "chemistry",
                    "variants": ["Element", "elements"],
                    "related_terms": ["atom", "periodic table", "compound"],
                    "source": "IUPAC",
                },
            },
        }

    def _get_physics_terms(self) -> Dict:
        """Get physics default term"""
        return {
            "mechanics": {
                "force": {
                    "en": "force",
                    "zh": "force",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "physics",
                    "variants": ["Force", "forces"],
                    "related_terms": ["mass", "acceleration", "motion"],
                    "source": "IUPAC",
                },
                "energy": {
                    "en": "energy",
                    "zh": "energy",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "physics",
                    "variants": ["Energy", "energies"],
                    "related_terms": ["work", "power", "thermodynamics"],
                    "source": "IUPAC",
                },
            },
            "quantum": {
                "quantum": {
                    "en": "quantum",
                    "zh": "quantum",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "physics",
                    "variants": ["Quantum", "quanta"],
                    "related_terms": ["particle", "wave", "mechanics"],
                    "source": "IUPAC",
                },
                "particle": {
                    "en": "particle",
                    "zh": "particle",
                    "abbrev": None,
                    "full_form": None,
                    "domain": "physics",
                    "variants": ["Particle", "particles"],
                    "related_terms": ["quantum", "wave", "physics"],
                    "source": "IUPAC",
                },
            },
        }

    def _load_custom_terminology(self, filepath: str):
        """Load a custom termbase"""
        path = Path(filepath)
        if path.exists():
            self._load_terminology_file(path)

    def check(self, text: str) -> List[TerminologyIssue]:
        """Perform a terminology check"""
        issues = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            self._check_term_consistency(line, line_num, text, issues)
            self._check_abbreviation_usage(line, line_num, text, issues)
            self._check_term_capitalization(line, line_num, issues)

        return issues

    def _check_term_consistency(
        self, line: str, line_num: int, full_text: str, issues: List[TerminologyIssue]
    ):
        """Check terminology consistency"""
        for category, terms in self.terminology.items():
            for term_key, term in terms.items():
                standard_en = term.en
                standard_zh = term.zh

                for variant in term.variants:
                    if variant.lower() != standard_en.lower():
                        pattern = re.compile(re.escape(variant), re.IGNORECASE)
                        for match in pattern.finditer(line):
                            issues.append(
                                TerminologyIssue(
                                    type="terminology",
                                    category=IssueCategory.CONSISTENCY,
                                    message=f"Use term variations: '{match.group()}'",
                                    suggestion=f"It is recommended to use standard terminology: '{standard_en}'",
                                    start=match.start(),
                                    end=match.end(),
                                    line=line_num,
                                    severity=IssueSeverity.INFO,
                                    term_data={
                                        "en": standard_en,
                                        "zh": standard_zh,
                                        "category": category,
                                    },
                                )
                            )

    def _check_abbreviation_usage(
        self, line: str, line_num: int, full_text: str, issues: List[TerminologyIssue]
    ):
        """Check abbreviation usage"""
        for category, terms in self.terminology.items():
            for term_key, term in terms.items():
                if term.abbrev:
                    pattern = re.compile(
                        r"\b" + re.escape(term.abbrev) + r"\b", re.IGNORECASE
                    )
                    for match in pattern.finditer(line):
                        is_first_occurrence = not any(
                            term.en in prev_line
                            for prev_line in full_text[: match.start()].split("\n")
                        )

                        if is_first_occurrence:
                            issues.append(
                                TerminologyIssue(
                                    type="abbreviation",
                                    category=IssueCategory.ABBREVIATION,
                                    message=f"first use of abbreviation: '{match.group()}'",
                                    suggestion=f"The full name should be given when it appears for the first time: '{term.full_form}' ({term.zh})",
                                    start=match.start(),
                                    end=match.end(),
                                    line=line_num,
                                    severity=IssueSeverity.WARNING,
                                    term_data={
                                        "en": term.en,
                                        "zh": term.zh,
                                        "abbrev": term.abbrev,
                                        "full_form": term.full_form,
                                    },
                                )
                            )

    def _check_term_capitalization(
        self, line: str, line_num: int, issues: List[TerminologyIssue]
    ):
        """Check term case"""
        for category, terms in self.terminology.items():
            for term_key, term in terms.items():
                if term.en and term.en[0].isupper() and len(term.en) > 1:
                    lowercase = term.en.lower()
                    pattern = re.compile(
                        r"\b" + re.escape(lowercase) + r"\b", re.IGNORECASE
                    )
                    for match in pattern.finditer(line):
                        if not match.group()[0].isupper():
                            issues.append(
                                TerminologyIssue(
                                    type="terminology",
                                    category=IssueCategory.CAPITALIZATION,
                                    message=f"the term '{match.group()}' not capitalized",
                                    suggestion=f"Proper nouns should be capitalized: '{term.en}'",
                                    start=match.start(),
                                    end=match.end(),
                                    line=line_num,
                                    severity=IssueSeverity.INFO
                                    if not self.strict
                                    else IssueSeverity.WARNING,
                                )
                            )

    def search_term(self, query: str) -> List[Term]:
        """Search terms"""
        results = []
        query_lower = query.lower()

        for category, terms in self.terminology.items():
            for term_key, term in terms.items():
                if (
                    query_lower in term.en.lower()
                    or query_lower in term.zh
                    or (term.abbrev and query_lower == term.abbrev.lower())
                ):
                    results.append(term)

        return results

    def get_translation(self, term: str) -> Optional[Dict]:
        """Get term translations"""
        for category, terms in self.terminology.items():
            for term_key, term_data in terms.items():
                if term.lower() == term_data.en.lower() or term == term_data.zh:
                    return {
                        "en": term_data.en,
                        "zh": term_data.zh,
                        "abbrev": term_data.abbrev,
                        "full_form": term_data.full_form,
                        "category": category,
                    }
        return None

    def add_term(self, category: str, term_key: str, term_data: Dict):
        """Add term"""
        if category not in self.terminology:
            self.terminology[category] = {}

        term = Term(**term_data)
        self.terminology[category][term_key] = term
        self._index_term(term)

    def export_terminology(self, filepath: str, category: Optional[str] = None):
        """Export termbase"""
        export_data = {}

        if category:
            if category in self.terminology:
                export_data[category] = {}
                for term_key, term in self.terminology[category].items():
                    export_data[category][term_key] = {
                        "en": term.en,
                        "zh": term.zh,
                        "abbrev": term.abbrev,
                        "full_form": term.full_form,
                        "domain": term.domain,
                        "variants": term.variants,
                        "related_terms": term.related_terms,
                        "source": term.source,
                        "notes": term.notes,
                    }
        else:
            for cat, terms in self.terminology.items():
                export_data[cat] = {}
                for term_key, term in terms.items():
                    export_data[cat][term_key] = {
                        "en": term.en,
                        "zh": term.zh,
                        "abbrev": term.abbrev,
                        "full_form": term.full_form,
                        "domain": term.domain,
                        "variants": term.variants,
                        "related_terms": term.related_terms,
                        "source": term.source,
                        "notes": term.notes,
                    }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def import_terminology(self, filepath: str):
        """Import termbase"""
        self._load_terminology_file(Path(filepath))
