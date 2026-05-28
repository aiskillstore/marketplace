#!/usr/bin/env python3
"""Microbiome Diversity Reporter
=============================
Analyze Alpha and Beta diversity indicators in 16S rRNA sequencing results

Author:OpenClaw
Version: 1.0.0"""

import argparse
import sys
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy import stats

# Try importing optional dependencies
try:
    import skbio
    from skbio.diversity import alpha_diversity, beta_diversity
    from skbio.stats.ordination import pcoa
    SKBIO_AVAILABLE = True
except ImportError:
    SKBIO_AVAILABLE = False
    warnings.warn("scikit-bio not available, using fallback implementations")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class AlphaDiversityCalculator:
    """Alpha Diversity Calculator"""
    
    METRICS = ['shannon', 'simpson', 'chao1', 'observed_otus', 'pielou']
    
    def __init__(self):
        self.results = {}
    
    def calculate(self, otu_table: pd.DataFrame, metric: str = 'shannon') -> Dict[str, float]:
        """Calculate Alpha Diversity
        
        Parameters:
        ----------
        otu_table : pd.DataFrame
            OTU table (samples x OTUs)
        metric : str
            Diversity indicator name
            
        Returns:
        --------
        Dict[str, float]
            Diversity index for each sample"""
        if metric not in self.METRICS:
            raise ValueError(f"Unsupported metric: {metric}. Use one of {self.METRICS}")
        
        results = {}
        for sample in otu_table.index:
            counts = otu_table.loc[sample].values
            results[sample] = self._calculate_metric(counts, metric)
        
        self.results[metric] = results
        return results
    
    def _calculate_metric(self, counts: np.ndarray, metric: str) -> float:
        """Calculate a single metric"""
        # Remove zero values
        counts = counts[counts > 0]
        total = counts.sum()
        
        if total == 0:
            return 0.0
        
        proportions = counts / total
        
        if metric == 'shannon':
            # Shannon index: -sum(p_i * ln(p_i))
            return -np.sum(proportions * np.log(proportions))
        
        elif metric == 'simpson':
            # Simpson index: 1 - sum(p_i^2)
            return 1 - np.sum(proportions ** 2)
        
        elif metric == 'chao1':
            # Chao1 estimate
            f1 = np.sum(counts == 1)  # singletons
            f2 = np.sum(counts == 2)  # doubletons
            s_obs = len(counts)
            if f2 == 0:
                return s_obs + f1 * (f1 - 1) / 2
            return s_obs + f1 ** 2 / (2 * f2)
        
        elif metric == 'observed_otus':
            # Number of OTUs observed
            return len(counts)
        
        elif metric == 'pielou':
            # Pielou uniformity index: H' / ln(S)
            shannon = -np.sum(proportions * np.log(proportions))
            s_obs = len(counts)
            if s_obs <= 1:
                return 0.0
            return shannon / np.log(s_obs)
        
        return 0.0
    
    def calculate_all(self, otu_table: pd.DataFrame) -> pd.DataFrame:
        """Calculate all alpha diversity metrics"""
        all_results = {}
        for metric in self.METRICS:
            all_results[metric] = self.calculate(otu_table, metric)
        return pd.DataFrame(all_results)
    
    def rarefaction_curve(self, otu_table: pd.DataFrame, 
                          step: int = 100,
                          iterations: int = 10) -> pd.DataFrame:
        """Generate sparse curve data
        
        Parameters:
        ----------
        otu_table : pd.DataFrame
            OTU table
        step : int
            Sampling step size
        iterations : int
            Number of iterations for each point
            
        Returns:
        --------
        pd.DataFrame
            sparse curve data"""
        curves = []
        max_depth = int(otu_table.sum(axis=1).min())
        depths = range(step, max_depth + 1, step)
        
        for sample in otu_table.index:
            counts = otu_table.loc[sample].values
            sample_curve = {'sample': sample, 'depths': [], 'richness': []}
            
            for depth in depths:
                richness_values = []
                for _ in range(iterations):
                    # random subsampling
                    subsampled = self._subsample(counts, depth)
                    richness = np.sum(subsampled > 0)
                    richness_values.append(richness)
                
                sample_curve['depths'].append(depth)
                sample_curve['richness'].append(np.mean(richness_values))
            
            curves.append(sample_curve)
        
        return pd.DataFrame(curves)
    
    def _subsample(self, counts: np.ndarray, depth: int) -> np.ndarray:
        """Subsample counts"""
        # Create a repeating list
        expanded = np.repeat(np.arange(len(counts)), counts.astype(int))
        # random sampling
        if len(expanded) <= depth:
            return counts
        sampled = np.random.choice(expanded, size=depth, replace=False)
        # Recalculate count
        result = np.zeros_like(counts)
        for idx in sampled:
            result[idx] += 1
        return result


class BetaDiversityCalculator:
    """Beta Diversity Calculator"""
    
    METRICS = ['braycurtis', 'jaccard', 'unweighted_unifrac', 'weighted_unifrac']
    
    def __init__(self):
        self.distance_matrix = None
        self.metric = None
    
    def calculate(self, otu_table: pd.DataFrame, metric: str = 'braycurtis') -> pd.DataFrame:
        """Calculate Beta diversity distance matrix
        
        Parameters:
        ----------
        otu_table : pd.DataFrame
            OTU table (samples x OTUs)
        metric : str
            distance measurement method
            
        Returns:
        --------
        pd.DataFrame
            distance matrix"""
        self.metric = metric
        
        if metric == 'braycurtis':
            distances = pdist(otu_table.values, metric='braycurtis')
            self.distance_matrix = pd.DataFrame(
                squareform(distances),
                index=otu_table.index,
                columns=otu_table.index
            )
        
        elif metric == 'jaccard':
            # Jaccard distance (based on presence/absence)
            binary_table = (otu_table > 0).astype(int)
            distances = pdist(binary_table.values, metric='jaccard')
            self.distance_matrix = pd.DataFrame(
                squareform(distances),
                index=otu_table.index,
                columns=otu_table.index
            )
        
        else:
            raise ValueError(f"Metric '{metric}' not implemented in fallback mode")
        
        return self.distance_matrix
    
    def pcoa(self, n_components: int = 3) -> Dict:
        """Principal Coordinate Analysis (PCoA)
        
        Parameters:
        ----------
        n_components : int
            number of dimensions retained
            
        Returns:
        --------
        Dict
            PCoA results"""
        if self.distance_matrix is None:
            raise ValueError("Must calculate distance matrix first")
        
        # PCoA using scikit-bio (if available)
        if SKBIO_AVAILABLE:
            dm = skbio.DistanceMatrix(self.distance_matrix.values, ids=self.distance_matrix.index)
            pcoa_result = skbio.stats.ordination.pcoa(dm, number_of_dimensions=n_components)
            
            return {
                'samples': pd.DataFrame(
                    pcoa_result.samples.values[:, :n_components],
                    index=self.distance_matrix.index,
                    columns=[f'PC{i+1}' for i in range(n_components)]
                ),
                'variance_explained': pcoa_result.proportion_explained.values[:n_components],
                'eigenvalues': pcoa_result.eigvals.values[:n_components]
            }
        
        # Fallback: Using classic multidimensional scaling (MDS)
        dist_matrix = self.distance_matrix.values
        n = dist_matrix.shape[0]
        
        # dual centralization
        J = np.eye(n) - np.ones((n, n)) / n
        B = -0.5 * J @ (dist_matrix ** 2) @ J
        
        # Eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(B)
        
        # Sort and select top n_components
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx][:n_components]
        eigenvectors = eigenvectors[:, idx][:, :n_components]
        
        # Calculate coordinates
        coords = eigenvectors * np.sqrt(np.maximum(eigenvalues, 0))
        
        # Calculate the proportion of variance explained
        total_variance = np.sum(np.maximum(eigenvalues, 0))
        variance_explained = eigenvalues / total_variance if total_variance > 0 else np.zeros(n_components)
        
        return {
            'samples': pd.DataFrame(
                coords,
                index=self.distance_matrix.index,
                columns=[f'PC{i+1}' for i in range(n_components)]
            ),
            'variance_explained': variance_explained,
            'eigenvalues': eigenvalues
        }
    
    def permanova(self, metadata: pd.DataFrame, grouping_column: str) -> Dict:
        """PERMANOVA statistical test
        
        Parameters:
        ----------
        metadata: pd.DataFrame
            metadata table
        grouping_column : str
            Grouping column name
            
        Returns:
        --------
        Dict
            PERMANOVA results"""
        if self.distance_matrix is None:
            raise ValueError("Must calculate distance matrix first")
        
        # Simple implementation (based on scipy)
        groups = metadata[grouping_column].loc[self.distance_matrix.index].values
        unique_groups = np.unique(groups)
        
        if len(unique_groups) < 2:
            return {'error': 'Need at least 2 groups for PERMANOVA'}
        
        # Calculate distances between and within groups
        distances = self.distance_matrix.values
        n = len(groups)
        
        # group index
        group_indices = {g: np.where(groups == g)[0] for g in unique_groups}
        
        # Calculate the average distance within a group (a simplified version of the pseudo-F statistic)
        within_sum = 0
        between_sum = 0
        
        total_mean = distances.mean()
        
        for g in unique_groups:
            idx = group_indices[g]
            group_distances = distances[np.ix_(idx, idx)]
            group_mean = group_distances.mean()
            within_sum += len(idx) * group_mean
        
        # simplified statistics
        between_sum = total_mean * (n ** 2) - within_sum
        
        return {
            'test': 'PERMANOVA (approximation)',
            'grouping_variable': grouping_column,
            'num_groups': len(unique_groups),
            'group_sizes': {g: len(group_indices[g]) for g in unique_groups},
            'pseudo_f': between_sum / within_sum if within_sum > 0 else float('inf')
        }


class DiversityReporter:
    """Diversity Report Generator"""
    
    def __init__(self, otu_table: pd.DataFrame, metadata: Optional[pd.DataFrame] = None):
        self.otu_table = otu_table
        self.metadata = metadata
        self.alpha_calc = AlphaDiversityCalculator()
        self.beta_calc = BetaDiversityCalculator()
        self.results = {}
    
    def analyze_alpha(self, metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """Analyzing Alpha Diversity"""
        if metrics is None:
            metrics = ['shannon', 'simpson', 'observed_otus']
        
        results = {}
        for metric in metrics:
            results[metric] = self.alpha_calc.calculate(self.otu_table, metric)
        
        df = pd.DataFrame(results)
        self.results['alpha'] = df
        return df
    
    def analyze_beta(self, metric: str = 'braycurtis') -> Dict:
        """Analyze Beta Diversity"""
        # Calculate distance matrix
        dist_matrix = self.beta_calc.calculate(self.otu_table, metric)
        
        # PCoA
        pcoa_result = self.beta_calc.pcoa()
        
        result = {
            'distance_matrix': dist_matrix,
            'pcoa': pcoa_result
        }
        
        # If metadata is available, perform PERMANOVA
        if self.metadata is not None:
            for col in self.metadata.columns:
                if col != 'SampleID':
                    permanova_result = self.beta_calc.permanova(self.metadata, col)
                    result[f'permanova_{col}'] = permanova_result
        
        self.results['beta'] = result
        return result
    
    def generate_report(self, output_format: str = 'json') -> Union[str, Dict]:
        """Generate report"""
        report = {
            'summary': {
                'num_samples': len(self.otu_table),
                'num_otus': len(self.otu_table.columns),
                'total_reads': int(self.otu_table.sum().sum()),
                'reads_per_sample': {
                    'mean': float(self.otu_table.sum(axis=1).mean()),
                    'std': float(self.otu_table.sum(axis=1).std()),
                    'min': float(self.otu_table.sum(axis=1).min()),
                    'max': float(self.otu_table.sum(axis=1).max())
                }
            }
        }
        
        # Add alpha diversity results
        if 'alpha' in self.results:
            alpha_df = self.results['alpha']
            report['alpha_diversity'] = {
                metric: {
                    'values': alpha_df[metric].to_dict(),
                    'statistics': {
                        'mean': float(alpha_df[metric].mean()),
                        'std': float(alpha_df[metric].std()),
                        'min': float(alpha_df[metric].min()),
                        'max': float(alpha_df[metric].max())
                    }
                }
                for metric in alpha_df.columns
            }
        
        # Add beta diversity results
        if 'beta' in self.results:
            beta_result = self.results['beta']
            report['beta_diversity'] = {
                'metric': self.beta_calc.metric,
                'pcoa': {
                    'variance_explained': beta_result['pcoa']['variance_explained'].tolist(),
                    'samples': beta_result['pcoa']['samples'].to_dict('index')
                }
            }
            
            # Add PERMANOVA results
            for key, value in beta_result.items():
                if key.startswith('permanova_'):
                    report['beta_diversity'][key] = value
        
        if output_format == 'json':
            return json.dumps(report, indent=2)
        return report
    
    def generate_html_report(self, output_path: str):
        """Generate HTML report"""
        report_data = self.generate_report(output_format='dict')
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Microbiome Diversity Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary-box {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-name {{
            font-weight: bold;
            color: #3498db;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        .metric-value {{
            font-size: 1.5em;
            color: #2c3e50;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <h1>🔬 Microbiome Diversity Analysis Report</h1>
    
    <div class="summary-box">
        <h2>📊 Sample summary</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-name">sample size</div>
                <div class="metric-value">{report_data['summary']['num_samples']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">OTUquantity</div>
                <div class="metric-value">{report_data['summary']['num_otus']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">totalReadsnumber</div>
                <div class="metric-value">{report_data['summary']['total_reads']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">averageReads/sample</div>
                <div class="metric-value">{report_data['summary']['reads_per_sample']['mean']:.0f}</div>
            </div>
        </div>
    </div>
"""
        
        # Add Alpha diversity section
        if 'alpha_diversity' in report_data:
            html_content += """<div class="summary-box">
        <h2>📈 Alpha diversity analysis</h2>
        <p>Alpha diversity measures the microbial diversity within a single sample. </p>
        <table>
            <tr>
                <th>Indicators</th>
                <th>Average</th>
                <th>Standard deviation</th>
                <th>Minimum value</th>
                <th>Maximum value</th>
            </tr>"""
            for metric, data in report_data['alpha_diversity'].items():
                stats = data['statistics']
                html_content += f"""
            <tr>
                <td><strong>{metric.upper()}</strong></td>
                <td>{stats['mean']:.3f}</td>
                <td>{stats['std']:.3f}</td>
                <td>{stats['min']:.3f}</td>
                <td>{stats['max']:.3f}</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""
        
        # Add Beta diversity section
        if 'beta_diversity' in report_data:
            pcoa = report_data['beta_diversity']['pcoa']
            html_content += f"""
    <div class="summary-box">
        <h2>🌐 Betadiversity analysis</h2>
        <p>BetaDiversity measures the differences in microbial composition between samples。use {report_data['beta_diversity']['metric']} distance。</p>
        
        <div class="highlight">
            <strong>PCoAVariance explained:</strong><br>
            PC1: {pcoa['variance_explained'][0]*100:.1f}%<br>
            PC2: {pcoa['variance_explained'][1]*100:.1f}%<br>
            PC3: {pcoa['variance_explained'][2]*100:.1f}%
        </div>
        
        <h3>Sample coordinates (forward3principal component)</h3>
        <table>
            <tr>
                <th>sample</th>
                <th>PC1</th>
                <th>PC2</th>
                <th>PC3</th>
            </tr>
"""
            for sample, coords in pcoa['samples'].items():
                html_content += f"""
            <tr>
                <td>{sample}</td>
                <td>{coords['PC1']:.3f}</td>
                <td>{coords['PC2']:.3f}</td>
                <td>{coords['PC3']:.3f}</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""
        
        html_content += """<div class="summary-box">
        <h2>ℹ️ Indicator explanation</h2>
        <ul>
            <li><strong>Shannon Index:</strong> Considering species richness and evenness, the higher the value, the better the diversity</li>
            <li><strong>Simpson Index:</strong> Measures the probability that two randomly selected individuals belong to different species</li>
            <li><strong>Observed OTUs:</strong> Actual number of observed OTUs</li>
            <li><strong>Chao1:</strong> Non-parametric method for estimating total species number</li>
            <li><strong>Bray-Curtis:</strong> A measure of compositional differences that considers species abundance</li>
            <li><strong>Jaccard:</strong> Binary distance based on species presence/absence</li>
        </ul>
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #7f8c8d;">
        <p>Generated by Microbiome Diversity Reporter v1.0.0</p>
    </footer>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path


def load_otu_table(path: str) -> pd.DataFrame:
    """Load OTU table"""
    df = pd.read_csv(path, sep='\t', index_col=0, comment='#')
    # Transpose so that samples are rows and OTUs are columns
    if df.shape[0] > df.shape[1]:
        df = df.T
    return df


def load_metadata(path: str) -> pd.DataFrame:
    """Load metadata"""
    df = pd.read_csv(path, sep='\t')
    if 'SampleID' in df.columns:
        df.set_index('SampleID', inplace=True)
    return df


def main():
    parser = argparse.ArgumentParser(
        description='Microbiome Diversity Analysis Tool - Analyze 16S rRNA Sequencing Data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  #Alpha Diversity Analysis
  python main.py --input otu_table.tsv --alpha --output alpha_report.html
  
  # Beta diversity analysis (requires metadata)
  python main.py --input otu_table.tsv --beta --metadata metadata.tsv --output beta_report.html
  
  # Complete analysis
  python main.py --input otu_table.tsv --full --metadata metadata.tsv --output full_report.html"""
    )
    
    parser.add_argument('--input', '-i', required=True,
                        help='OTU/ASV table path (TSV format)')
    parser.add_argument('--metadata', '-m',
                        help='Sample metadata path (TSV format)')
    parser.add_argument('--metric', choices=['shannon', 'simpson', 'chao1', 'observed_otus'],
                        default='shannon',
                        help='Alpha diversity metric (default: shannon)')
    parser.add_argument('--alpha', action='store_true',
                        help='Analyze alpha diversity only')
    parser.add_argument('--beta', action='store_true',
                        help='Analyze only beta diversity')
    parser.add_argument('--full', action='store_true',
                        help='Full analysis (Alpha + Beta)')
    parser.add_argument('--output', '-o',
                        help='Output file path (default output to stdout)')
    parser.add_argument('--format', choices=['html', 'json', 'markdown'],
                        default='html',
                        help='Output format (default: html)')
    
    args = parser.parse_args()
    
    # Determine analysis mode
    if not any([args.alpha, args.beta, args.full]):
        args.full = True  # Default full analysis
    
    # Load data
    try:
        otu_table = load_otu_table(args.input)
        print(f"loadOTUsheet: {otu_table.shape[0]} sample x {otu_table.shape[1]} OTUs", file=sys.stderr)
    except Exception as e:
        print(f"mistake: Unable to loadOTUsheet - {e}", file=sys.stderr)
        sys.exit(1)
    
    metadata = None
    if args.metadata:
        try:
            metadata = load_metadata(args.metadata)
            print(f"Load metadata: {metadata.shape[0]} sample x {metadata.shape[1]} property", file=sys.stderr)
        except Exception as e:
            print(f"warn: Unable to load metadata - {e}", file=sys.stderr)
    
    # Create analyzer
    reporter = DiversityReporter(otu_table, metadata)
    
    # Perform analysis
    if args.alpha or args.full:
        print("Calculate Alpha Diversity...", file=sys.stderr)
        reporter.analyze_alpha()
    
    if args.beta or args.full:
        print("Calculating Beta Diversity...", file=sys.stderr)
        if metadata is None:
            print("Warning: Beta analysis requires metadata for group comparisons", file=sys.stderr)
        reporter.analyze_beta()
    
    # Generate report
    if args.output:
        if args.format == 'html':
            output_path = reporter.generate_html_report(args.output)
            print(f"Report generated: {output_path}")
        elif args.format == 'json':
            report = reporter.generate_report(output_format='json')
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"JSONReport generated: {args.output}")
        else:
            report = reporter.generate_report(output_format='dict')
            # Markdown output
            md_content = f"""# Microbiome Diversity Analysis Report

## Sample summary

- **sample size**: {report['summary']['num_samples']}
- **OTUquantity**: {report['summary']['num_otus']}
- **totalReadsnumber**: {report['summary']['total_reads']:,}
- **averageReads/sample**: {report['summary']['reads_per_sample']['mean']:.0f}

## AlphaDiversity

"""
            if 'alpha_diversity' in report:
                md_content += "| Indicators | Mean | Standard Deviation |"
                md_content += "|------|--------|--------|\n"
                for metric, data in report['alpha_diversity'].items():
                    stats = data['statistics']
                    md_content += f"| {metric} | {stats['mean']:.3f} | {stats['std']:.3f} |\n"
            
            with open(args.output, 'w') as f:
                f.write(md_content)
            print(f"MarkdownReport generated: {args.output}")
    else:
        # Output to stdout
        report = reporter.generate_report(output_format='json')
        print(report)


if __name__ == '__main__':
    main()
