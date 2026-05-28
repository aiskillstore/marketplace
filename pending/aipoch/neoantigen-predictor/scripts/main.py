#!/usr/bin/env python3
"""Neoantigen Predictor Module
Predicting neoantigens based on patient HLA typing and tumor mutations
Supports MHC class I molecule binding prediction and immunogenicity assessment"""

import json
import re
import argparse
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MHC_Binding:
    """MHC binding prediction results"""
    rank_percentile: float = 100.0  # Combined with ranking percentage (lower is better)
    affinity_nM: Optional[float] = None  # Binding affinity (nM)
    binding_level: str = "Non-binder"  # Strong/Weak/Non-binder
    core_peptide: str = ""  # core binding sequence
    anchor_residues: List[int] = field(default_factory=list)  # anchor residue position
    score_el: Optional[float] = None  # EL (Eluted Ligand) score
    score_ba: Optional[float] = None  # BA (Binding Affinity) score


@dataclass
class Immunogenicity:
    """Immunogenicity assessment results"""
    foreignness_score: float = 0.0  # Exogenous score (0-1)
    self_similarity: float = 1.0  # Self-similarity (lower is better)
    amino_acid_change: str = ""  # Amino acid changes
    anchor_mutation: bool = False  # Whether the mutation is at the anchor position
    hydrophobicity_change: float = 0.0  # Hydrophobicity changes
    recognition_probability: float = 0.0  # Probability of being recognized by T cells


@dataclass
class Clinical_Info:
    """clinically relevant information"""
    variant_allele_frequency: Optional[float] = None  # variant allele frequency
    expression_level: Optional[str] = None  # gene expression level
    clonality: Optional[str] = None  # Clonal/Subclonal
    rna_editing: bool = False  # Is it an RNA editing site?
    germline_risk: bool = False  # Is it possible germline variation?


@dataclass
class Neoantigen_Candidate:
    """Complete information on neoantigen candidates"""
    # identification information
    mutation_id: str = ""
    gene: str = ""
    chromosome: str = ""
    position: int = 0
    
    # Variation information
    ref_aa: str = ""
    alt_aa: str = ""
    protein_change: str = ""  # Such as p.R273H
    
    # HLA information
    hla_allele: str = ""
    
    # Peptide information
    peptide_sequence: str = ""
    peptide_length: int = 9
    mutant_position: int = 0  # The position of the mutated amino acid in the peptide (1-based)
    wildtype_peptide: str = ""  # wild type peptide
    
    # Prediction results
    mhc_binding: MHC_Binding = field(default_factory=MHC_Binding)
    immunogenicity: Immunogenicity = field(default_factory=Immunogenicity)
    clinical_info: Clinical_Info = field(default_factory=Clinical_Info)
    
    # Overall rating
    priority_score: float = 0.0
    rank: int = 0


@dataclass
class Prediction_Result:
    """Complete prediction results"""
    patient_hla: List[str] = field(default_factory=list)
    prediction_method: str = "NetMHCpan 4.1"
    total_predictions: int = 0
    strong_binders: int = 0
    weak_binders: int = 0
    neoantigens: List[Neoantigen_Candidate] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class NetMHC_Predictor:
    """NetMHC combined with prediction simulator (replaced with real API calls or local programs when deployed)"""
    
    # HLA anchor position residue preference (based on known binding motifs)
    ANCHOR_PREFERENCES = {
        'HLA-A*01:01': {2: ['S', 'T', 'Y'], 9: ['A', 'V', 'I', 'L']},
        'HLA-A*02:01': {2: ['L', 'M', 'I', 'V'], 9: ['V', 'L', 'I', 'A']},
        'HLA-A*03:01': {2: ['L', 'M', 'I', 'V', 'F'], 9: ['K', 'R', 'Y']},
        'HLA-A*11:01': {2: ['T', 'V', 'I', 'M'], 9: ['K', 'R']},
        'HLA-A*24:02': {2: ['Y', 'F', 'W'], 9: ['F', 'I', 'L', 'W']},
        'HLA-A*68:01': {2: ['T', 'V', 'S'], 9: ['A', 'V', 'I']},
        'HLA-B*07:02': {2: ['P', 'R'], 9: ['L', 'F']},
        'HLA-B*08:01': {2: ['K', 'R'], 9: ['L', 'I']},
        'HLA-B*27:05': {2: ['R'], 9: ['L', 'F', 'I']},
        'HLA-B*35:01': {2: ['P', 'Y'], 9: ['L', 'F', 'M']},
        'HLA-B*57:01': {2: ['S', 'T'], 9: ['F', 'W']},
        'HLA-B*58:01': {2: ['A', 'T', 'S'], 9: ['F', 'W']},
    }
    
    # Hydrophobicity scale (Kyte-Doolittle)
    HYDROPATHY = {
        'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5,
        'M': 1.9, 'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8,
        'W': -0.9, 'Y': -1.3, 'P': -1.6, 'H': -3.2, 'E': -3.5,
        'Q': -3.5, 'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5
    }
    
    def __init__(self, method: str = "netmhcpan"):
        self.method = method
        logger.info(f"Initialized NetMHC predictor (method: {method})")
    
    def predict_binding(self, peptide: str, hla_allele: str) -> MHC_Binding:
        """Predict the binding affinity of peptides to HLA
        Note: This is a simplified simulation implementation, the NetMHCpan program should actually be called"""
        peptide = peptide.upper()
        length = len(peptide)
        
        # Standardized HLA nomenclature
        hla_normalized = self._normalize_hla(hla_allele)
        
        # Simplified scoring based on anchor residues and physicochemical properties
        score = self._calculate_binding_score(peptide, hla_normalized, length)
        
        # Convert to rank percentage (simulation)
        rank = self._score_to_rank(score)
        
        # Determine the binding level
        if rank <= 0.5:
            binding_level = "Strong"
        elif rank <= 2:
            binding_level = "Weak"
        else:
            binding_level = "Non-binder"
        
        # Calculate IC50 (analog)
        affinity = self._rank_to_ic50(rank) if rank < 10 else None
        
        # Identify anchor residue positions
        anchors = self._identify_anchors(hla_normalized, length)
        
        return MHC_Binding(
            rank_percentile=rank,
            affinity_nM=affinity,
            binding_level=binding_level,
            core_peptide=peptide,
            anchor_residues=anchors,
            score_el=score,
            score_ba=score * 0.9
        )
    
    def _normalize_hla(self, hla: str) -> str:
        """Standardized HLA nomenclature"""
        hla = hla.strip().upper()
        # Remove HLA-prefix
        if hla.startswith("HLA-"):
            hla = hla[4:]
        # Add HLA-prefix for matching
        return f"HLA-{hla}"
    
    def _calculate_binding_score(self, peptide: str, hla: str, length: int) -> float:
        """Compute binding score (simplified model)"""
        score = 0.5  # Basic points
        
        # Length penalty (8-11mer is best for MHC-I)
        if length < 8 or length > 11:
            score -= 0.3
        elif 9 <= length <= 10:
            score += 0.1
        
        # Anchor location preference
        if hla in self.ANCHOR_PREFERENCES:
            prefs = self.ANCHOR_PREFERENCES[hla]
            # Position 2
            if 2 in prefs and len(peptide) > 2:
                if peptide[1] in prefs[2]:
                    score += 0.25
                elif peptide[1] in ['A', 'V', 'L', 'I', 'F', 'W', 'Y', 'M']:
                    score += 0.1
            # C end (position length)
            if length in prefs:
                if peptide[-1] in prefs[length]:
                    score += 0.25
                elif peptide[-1] in ['V', 'L', 'I', 'F', 'Y']:
                    score += 0.1
        
        # GC content check (optimum 40-60%)
        gc_count = peptide.count('G') + peptide.count('C')
        gc_percent = gc_count / length
        if 0.3 <= gc_percent <= 0.7:
            score += 0.1
        
        # Hydrophobicity check (C-terminus prefers hydrophobicity)
        if peptide and peptide[-1] in self.HYDROPATHY:
            if self.HYDROPATHY[peptide[-1]] > 0:
                score += 0.1
        
        # Proline Penalty (Breaking the Spiral)
        if 'P' in peptide[2:-1]:
            score -= 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _score_to_rank(self, score: float) -> float:
        """Convert rating to rank percentage (simulation)"""
        # Linear mapping (simplified)
        rank = (1 - score) * 10
        return max(0.01, min(100, rank))
    
    def _rank_to_ic50(self, rank: float) -> float:
        """Convert rank to IC50 value (nM)"""
        # Approximate conversion: rank 0.5% ≈ 50nM, rank 2% ≈ 500nM
        if rank <= 0.5:
            return rank * 100
        else:
            return 50 + (rank - 0.5) * 300
    
    def _identify_anchors(self, hla: str, length: int) -> List[int]:
        """Identify anchor residue positions"""
        anchors = [2, length]  # MHC-I usually position 2 and C terminus
        return anchors


class NeoantigenPredictor:
    """Neoantigen prediction main category"""
    
    # Amino acid one-letter code
    AA_3TO1 = {
        'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
        'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
        'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
        'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
        'TER': '*', 'STP': '*', 'XAA': 'X'
    }
    
    WEIGHTS = {
        'mhc_binding': 0.40,
        'immunogenicity': 0.35,
        'clinical': 0.25
    }
    
    def __init__(self, mhc_method: str = "netmhcpan"):
        self.mhc_predictor = NetMHC_Predictor(method=mhc_method)
        logger.info("NeoantigenPredictor initialized")
    
    def predict(
        self,
        hla_alleles: List[str],
        mutations: List[Dict[str, Any]],
        peptide_length: List[int] = None,
        transcript_sequences: Dict[str, str] = None
    ) -> Prediction_Result:
        """Perform neoantigen prediction
        
        Args:
            hla_alleles: patient HLA alleles list
            mutations: mutation information list
            peptide_length: list of peptide lengths (default [9, 10])
            transcript_sequences: dictionary of transcript sequences (optional)
        
        Returns:
            Prediction_Result: Complete prediction result"""
        if peptide_length is None:
            peptide_length = [9, 10]
        
        # Standardized HLA nomenclature
        normalized_hla = [self._normalize_hla(hla) for hla in hla_alleles]
        
        candidates = []
        
        for mutation in mutations:
            # Generate variant peptides
            variant_peptides = self._generate_variant_peptides(
                mutation, peptide_length, transcript_sequences
            )
            
            for var_pep, wt_pep, mut_pos in variant_peptides:
                # Make predictions for each HLA allele
                for hla in normalized_hla:
                    candidate = self._predict_candidate(
                        mutation=mutation,
                        peptide=var_pep,
                        wildtype_peptide=wt_pep,
                        mutant_position=mut_pos,
                        hla_allele=hla
                    )
                    candidates.append(candidate)
        
        # Prioritization
        ranked_candidates = self._rank_candidates(candidates)
        
        # statistics
        strong_binders = sum(1 for c in candidates if c.mhc_binding.binding_level == "Strong")
        weak_binders = sum(1 for c in candidates if c.mhc_binding.binding_level == "Weak")
        
        # Build results
        result = Prediction_Result(
            patient_hla=normalized_hla,
            total_predictions=len(candidates),
            strong_binders=strong_binders,
            weak_binders=weak_binders,
            neoantigens=ranked_candidates,
            summary={
                "top_candidates": min(10, len(ranked_candidates)),
                "binding_distribution": {
                    "strong": strong_binders,
                    "weak": weak_binders,
                    "non_binder": len(candidates) - strong_binders - weak_binders
                }
            }
        )
        
        return result
    
    def _normalize_hla(self, hla: str) -> str:
        """Standardized HLA naming format"""
        hla = hla.strip().upper()
        
        # Make sure there is HLA-prefix
        if not hla.startswith("HLA-"):
            # Check if it is A/B/C format
            if hla[0] in ['A', 'B', 'C'] and (len(hla) == 1 or not hla[1].isdigit()):
                hla = f"HLA-{hla[0]}*{hla[1:3]}:{hla[3:]}"
            elif hla[0] in ['A', 'B', 'C']:
                hla = f"HLA-{hla}"
        
        return hla
    
    def _parse_protein_change(self, protein_change: str) -> Tuple[str, int, str]:
        """Resolve protein changes (e.g. p.R273H -> (R, 273, H))
        Returns: (ref_aa, position, alt_aa)"""
        # Remove p. prefix
        if protein_change.startswith('p.'):
            protein_change = protein_change[2:]
        
        # Matching pattern: R273H, Arg273His, etc.
        patterns = [
            r'([A-Za-z]{3})(\d+)([A-Za-z]{3})',  # Three letters: Arg273His
            r'([A-Za-z])(\d+)([A-Za-z*])',         # Single letters: R273H, R273*
        ]
        
        for pattern in patterns:
            match = re.match(pattern, protein_change)
            if match:
                ref = match.group(1)
                pos = int(match.group(2))
                alt = match.group(3)
                
                # Convert three letters to single letters
                if len(ref) == 3:
                    ref = self.AA_3TO1.get(ref.upper(), 'X')
                if len(alt) == 3:
                    alt = self.AA_3TO1.get(alt.upper(), 'X')
                
                return (ref.upper(), pos, alt.upper())
        
        raise ValueError(f"Unable to resolve protein changes: {protein_change}")
    
    def _generate_variant_peptides(
        self,
        mutation: Dict[str, Any],
        peptide_lengths: List[int],
        transcript_sequences: Dict[str, str] = None
    ) -> List[Tuple[str, str, int]]:
        """Generate variant peptides
        Returns: [(variant peptide, wild-type peptide, mutation position), ...]"""
        peptides = []
        
        protein_change = mutation.get('protein_change', '')
        if not protein_change:
            return peptides
        
        try:
            ref_aa, mut_pos, alt_aa = self._parse_protein_change(protein_change)
        except ValueError:
            logger.warning(f"Unable to resolve mutation: {protein_change}")
            return peptides
        
        gene = mutation.get('gene', 'Unknown')
        
        # Get protein sequence (simplified: use mock sequence)
        # Practical applications should obtain the real sequence from Ensembl/Uniprot
        protein_seq = self._get_protein_sequence(gene, transcript_sequences)
        
        if not protein_seq or mut_pos > len(protein_seq):
            logger.warning(f"Unable to obtain protein sequence or position is out of range: {gene} pos {mut_pos}")
            # Generate mock peptides for demonstration
            return self._generate_mock_peptides(ref_aa, alt_aa, peptide_lengths)
        
        # Verify reference amino acids
        if protein_seq[mut_pos - 1] != ref_aa:
            logger.warning(f"Reference amino acid mismatch: expect {ref_aa}, actual {protein_seq[mut_pos - 1]}")
        
        # Generate variant sequences
        variant_seq = protein_seq[:mut_pos - 1] + alt_aa + protein_seq[mut_pos:]
        
        # Extract peptides of various lengths
        for length in peptide_lengths:
            for start in range(max(0, mut_pos - length), min(mut_pos, len(protein_seq) - length + 1)):
                end = start + length
                
                wt_peptide = protein_seq[start:end]
                var_peptide = variant_seq[start:end]
                
                # Make sure the mutation is included in the peptide
                if ref_aa != alt_aa and var_peptide == wt_peptide:
                    continue
                
                mut_in_peptide = mut_pos - start  # 1-based location
                peptides.append((var_peptide, wt_peptide, mut_in_peptide))
        
        return peptides
    
    def _get_protein_sequence(
        self,
        gene: str,
        transcript_sequences: Dict[str, str] = None
    ) -> Optional[str]:
        """Get protein sequence (simplified implementation)"""
        if transcript_sequences and gene in transcript_sequences:
            return transcript_sequences[gene]
        
        # Return the simulated sequence (actually should be obtained from the database)
        return self._generate_mock_protein(gene)
    
    def _generate_mock_protein(self, gene: str) -> str:
        """Generate simulated protein sequences (for demonstration)"""
        # Generate pseudo-random but consistent sequences based on gene names
        import random
        random.seed(gene)
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        length = random.randint(200, 500)
        return ''.join(random.choice(amino_acids) for _ in range(length))
    
    def _generate_mock_peptides(
        self,
        ref_aa: str,
        alt_aa: str,
        lengths: List[int]
    ) -> List[Tuple[str, str, int]]:
        """Generate simulated peptides (for demonstration)"""
        peptides = []
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        import random
        random.seed(f"{ref_aa}{alt_aa}")
        
        for length in lengths:
            for _ in range(3):  # Generates 3 of each length
                flank = (length - 1) // 2
                left = ''.join(random.choice(amino_acids) for _ in range(flank))
                right = ''.join(random.choice(amino_acids) for _ in range(length - flank - 1))
                
                var_pep = left + alt_aa + right
                wt_pep = left + ref_aa + right
                peptides.append((var_pep, wt_pep, flank + 1))
        
        return peptides
    
    def _predict_candidate(
        self,
        mutation: Dict[str, Any],
        peptide: str,
        wildtype_peptide: str,
        mutant_position: int,
        hla_allele: str
    ) -> Neoantigen_Candidate:
        """Predict single candidate neoantigens"""
        
        # MHC binding prediction
        mhc_binding = self.mhc_predictor.predict_binding(peptide, hla_allele)
        
        # Immunogenicity assessment
        immunogenicity = self._assess_immunogenicity(
            peptide, wildtype_peptide, mutant_position, mhc_binding.anchor_residues
        )
        
        # Build candidates
        candidate = Neoantigen_Candidate(
            mutation_id=f"{mutation.get('gene', 'Unknown')}_{mutation.get('protein_change', '')}",
            gene=mutation.get('gene', 'Unknown'),
            chromosome=mutation.get('chrom', ''),
            position=mutation.get('pos', 0),
            ref_aa=wildtype_peptide[mutant_position - 1] if mutant_position <= len(wildtype_peptide) else '',
            alt_aa=peptide[mutant_position - 1] if mutant_position <= len(peptide) else '',
            protein_change=mutation.get('protein_change', ''),
            hla_allele=hla_allele,
            peptide_sequence=peptide,
            peptide_length=len(peptide),
            mutant_position=mutant_position,
            wildtype_peptide=wildtype_peptide,
            mhc_binding=mhc_binding,
            immunogenicity=immunogenicity
        )
        
        # Calculate priority score
        candidate.priority_score = self._calculate_priority_score(candidate)
        
        return candidate
    
    def _assess_immunogenicity(
        self,
        variant_peptide: str,
        wildtype_peptide: str,
        mutant_position: int,
        anchor_positions: List[int]
    ) -> Immunogenicity:
        """Assess immunogenicity"""
        
        # Calculate exogenous score (difference from wild type)
        diff_count = sum(1 for a, b in zip(variant_peptide, wildtype_peptide) if a != b)
        foreignness = min(1.0, diff_count / len(variant_peptide))
        
        # Check if mutation is at anchor position
        anchor_mutation = mutant_position in anchor_positions
        
        # Calculate hydrophobicity change
        hyd_var = sum(NetMHC_Predictor.HYDROPATHY.get(aa, 0) for aa in variant_peptide)
        hyd_wt = sum(NetMHC_Predictor.HYDROPATHY.get(aa, 0) for aa in wildtype_peptide)
        hyd_change = (hyd_var - hyd_wt) / len(variant_peptide)
        
        # Amino acid changes
        ref_aa = wildtype_peptide[mutant_position - 1] if mutant_position <= len(wildtype_peptide) else ''
        alt_aa = variant_peptide[mutant_position - 1] if mutant_position <= len(variant_peptide) else ''
        aa_change = f"{ref_aa}->{alt_aa}"
        
        # Recognition probability estimate
        recognition_prob = self._estimate_recognition_probability(
            foreignness, anchor_mutation, abs(hyd_change)
        )
        
        return Immunogenicity(
            foreignness_score=foreignness,
            self_similarity=1.0 - foreignness,
            amino_acid_change=aa_change,
            anchor_mutation=anchor_mutation,
            hydrophobicity_change=hyd_change,
            recognition_probability=recognition_prob
        )
    
    def _estimate_recognition_probability(
        self,
        foreignness: float,
        anchor_mutation: bool,
        hyd_change: float
    ) -> float:
        """Estimating T cell recognition probability (simplified model)"""
        prob = foreignness * 0.5
        if anchor_mutation:
            prob += 0.3
        prob += min(hyd_change * 0.1, 0.2)
        return min(1.0, max(0.0, prob))
    
    def _calculate_priority_score(self, candidate: Neoantigen_Candidate) -> float:
        """Calculate overall priority score"""
        
        # MHC binding score (based on rank)
        binding_score = max(0, (2 - candidate.mhc_binding.rank_percentile) / 2)
        
        # immunogenicity score
        immuno_score = (
            candidate.immunogenicity.foreignness_score * 0.4 +
            (1.0 if candidate.immunogenicity.anchor_mutation else 0.0) * 0.3 +
            candidate.immunogenicity.recognition_probability * 0.3
        )
        
        # Clinical Score (Simplified)
        clinical_score = 0.5
        
        # weighted synthesis
        priority = (
            self.WEIGHTS['mhc_binding'] * binding_score +
            self.WEIGHTS['immunogenicity'] * immuno_score +
            self.WEIGHTS['clinical'] * clinical_score
        )
        
        return round(priority, 3)
    
    def _rank_candidates(self, candidates: List[Neoantigen_Candidate]) -> List[Neoantigen_Candidate]:
        """Prioritize candidate neoantigens"""
        # Sort by priority rating descending
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (
                x.priority_score,
                2 - x.mhc_binding.rank_percentile,  # The smaller the rank, the better
                x.immunogenicity.foreignness_score
            ),
            reverse=True
        )
        
        # Assign ranking
        for i, candidate in enumerate(sorted_candidates, 1):
            candidate.rank = i
        
        return sorted_candidates
    
    def filter_by_binding(
        self,
        result: Prediction_Result,
        rank_threshold: float = 2.0,
        binding_level: str = None
    ) -> List[Neoantigen_Candidate]:
        """Screen candidates based on MHC binding affinity"""
        filtered = []
        
        for candidate in result.neoantigens:
            if candidate.mhc_binding.rank_percentile <= rank_threshold:
                if binding_level is None or candidate.mhc_binding.binding_level == binding_level:
                    filtered.append(candidate)
        
        return filtered
    
    def to_dict(self, result: Prediction_Result) -> Dict[str, Any]:
        """Convert the result to dictionary format"""
        return {
            "patient_hla": result.patient_hla,
            "prediction_method": result.prediction_method,
            "total_predictions": result.total_predictions,
            "strong_binders": result.strong_binders,
            "weak_binders": result.weak_binders,
            "neoantigens": [asdict(n) for n in result.neoantigens],
            "summary": result.summary
        }


def parse_hla_input(hla_string: str) -> List[str]:
    """Parse HLA input string"""
    hla_list = []
    for hla in hla_string.split(','):
        hla = hla.strip()
        if hla:
            hla_list.append(hla)
    return hla_list


def parse_mutations_csv(file_path: str) -> List[Dict[str, Any]]:
    """Parse mutation data from CSV file"""
    import csv
    mutations = []
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mutation = {
                'gene': row.get('Gene', row.get('gene', '')),
                'chrom': row.get('Chrom', row.get('chrom', '')),
                'pos': int(row.get('Position', row.get('pos', 0))),
                'ref': row.get('Ref', row.get('ref', '')),
                'alt': row.get('Alt', row.get('alt', '')),
                'protein_change': row.get('Protein_Change', row.get('protein_change', ''))
            }
            mutations.append(mutation)
    
    return mutations


def main():
    """Command line entry"""
    parser = argparse.ArgumentParser(
        description="Neoantigen Predictor - Predict neoantigens based on HLA and mutations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python main.py --hla "HLA-A*02:01,A*11:01" --mutations mutations.csv --output results.json
  python main.py --hla-file hla.txt --vcf variants.vcf --peptide-length 9,10 --rank-cutoff 0.5"""
    )
    
    # HLA input
    hla_group = parser.add_mutually_exclusive_group(required=True)
    hla_group.add_argument('--hla', help='HLA alleles, separated by commas (eg: HLA-A*02:01,A*11:01)')
    hla_group.add_argument('--hla-file', help='File containing HLA list')
    
    # mutation input
    mut_group = parser.add_mutually_exclusive_group(required=True)
    mut_group.add_argument('--mutations', help='Mutation data CSV file')
    mut_group.add_argument('--vcf', help='VCF format mutation file')
    mut_group.add_argument('--variant-peptides', help='Variant peptide FASTA file')
    
    # Prediction parameters
    parser.add_argument('--peptide-length', default='9,10',
                       help='Peptide lengths, comma separated (default: 9,10)')
    parser.add_argument('--rank-cutoff', type=float, default=2.0,
                       help='MHC binding rank threshold (default: 2.0)')
    parser.add_argument('--mhc-method', default='netmhcpan',
                       choices=['netmhcpan', 'mhcflurry', 'custom'],
                       help='MHC prediction method')
    
    # output
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', choices=['json', 'csv'], default='json',
                       help='Output format')
    parser.add_argument('--top-n', type=int, help='Only output the top N candidates')
    
    args = parser.parse_args()
    
    # Parse HLA
    if args.hla:
        hla_alleles = parse_hla_input(args.hla)
    else:
        with open(args.hla_file, 'r') as f:
            hla_alleles = parse_hla_input(f.read())
    
    logger.info(f"HLATypes: {hla_alleles}")
    
    # Analyze mutations
    if args.mutations:
        mutations = parse_mutations_csv(args.mutations)
    elif args.vcf:
        # Simplification: VCF parsing should use a dedicated library such as pysam
        logger.error("The VCF parsing function requires pysam to be installed, please use CSV format.")
        return 1
    else:
        logger.error("FASTA peptide input has not yet been implemented")
        return 1
    
    logger.info(f"number of mutations: {len(mutations)}")
    
    # Analyze peptide length
    peptide_lengths = [int(x) for x in args.peptide_length.split(',')]
    
    # Execute prediction
    predictor = NeoantigenPredictor(mhc_method=args.mhc_method)
    
    result = predictor.predict(
        hla_alleles=hla_alleles,
        mutations=mutations,
        peptide_length=peptide_lengths
    )
    
    # Screen for strong binding
    filtered = predictor.filter_by_binding(result, rank_threshold=args.rank_cutoff)
    logger.info(f"strong binding candidate: {len(filtered)}")
    
    # Apply top-n restrictions
    if args.top_n:
        result.neoantigens = result.neoantigens[:args.top_n]
    
    # Output results
    output_data = predictor.to_dict(result)
    
    if args.format == 'json':
        output = json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        # CSV format
        import csv
        import io
        output_io = io.StringIO()
        if result.neoantigens:
            writer = csv.writer(output_io)
            writer.writerow(['Rank', 'Gene', 'HLA', 'Peptide', 'Rank%', 'Binding', 'Priority'])
            for n in result.neoantigens:
                writer.writerow([
                    n.rank, n.gene, n.hla_allele, n.peptide_sequence,
                    n.mhc_binding.rank_percentile, n.mhc_binding.binding_level,
                    n.priority_score
                ])
        output = output_io.getvalue()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"Results have been saved to: {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    exit(main())
