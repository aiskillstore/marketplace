import argparse
import requests
import sys
import urllib.parse

BASE_URL = "https://rnasysu.com/encori/api/"

def make_request(endpoint, params):
    """
    Make a GET request to the ENCORI API.
    """
    url = f"{BASE_URL}{endpoint}/"
    try:
        # Filter out None values
        valid_params = {k: v for k, v in params.items() if v is not None}
        
        # Construct query string manually to ensure correct formatting if needed, 
        # but requests.get handles it well usually. 
        # Note: The doc uses 'all' for downloading all data. 
        
        response = requests.get(url, params=valid_params)
        response.raise_for_status()
        
        # The API returns text data (often TSV/CSV-like)
        print(response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing ENCORI API: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_miRNATarget(args):
    params = {
        'assembly': args.assembly,
        'geneType': args.geneType,
        'miRNA': args.miRNA,
        'clipExpNum': args.clipExpNum,
        'degraExpNum': args.degraExpNum,
        'pancancerNum': args.pancancerNum,
        'programNum': args.programNum,
        'program': args.program,
        'target': args.target,
        'cellType': args.cellType
    }
    make_request('miRNATarget', params)

def cmd_degradomeRNA(args):
    params = {
        'assembly': args.assembly,
        'geneType': args.geneType,
        'miRNA': args.miRNA,
        'degraExpNum': args.degraExpNum,
        'target': args.target,
        'cellType': args.cellType
    }
    make_request('degradomeRNA', params)

def cmd_RNARNA(args):
    params = {
        'assembly': args.assembly,
        'geneType': args.geneType,
        'RNA': args.RNA,
        'interNum': args.interNum,
        'expNum': args.expNum,
        'cellType': args.cellType
    }
    make_request('RNARNA', params)

def cmd_ceRNA(args):
    params = {
        'assembly': args.assembly,
        'geneType': args.geneType,
        'ceRNA': args.ceRNA,
        'miRNAnum': args.miRNAnum,
        'family': args.family,
        'pval': args.pval,
        'fdr': args.fdr,
        'pancancerNum': args.pancancerNum
    }
    make_request('ceRNA', params)

def cmd_RBPTarget(args):
    params = {
        'assembly': args.assembly,
        'geneType': args.geneType,
        'RBP': args.RBP,
        'clipExpNum': args.clipExpNum,
        'pancancerNum': args.pancancerNum,
        'target': args.target,
        'cellType': args.cellType
    }
    make_request('RBPTarget', params)

def cmd_RBPDisease(args):
    params = {
        'assembly': args.assembly,
        'RBP': args.RBP,
        'tissue': args.tissue,
        'target': args.target
    }
    if args.disease:
        params['disease'] = args.disease
    make_request('RBPDisease', params)

def cmd_RBPMotifScan(args):
    params = {
        'assembly': args.assembly,
        'length': args.length,
        'motif': args.motif,
        'rankLimit': args.rankLimit
    }
    make_request('RBPMotifScan', params)

def cmd_bindingSite(args):
    params = {
        'assembly': args.assembly,
        'datasetID': args.datasetID
    }
    make_request('bindingSite', params)

def main():
    parser = argparse.ArgumentParser(description="ENCORI API Client")
    subparsers = parser.add_subparsers(dest='endpoint', help='API Endpoint')
    subparsers.required = True

    # Common args helper
    def add_common(p):
        p.add_argument('--assembly', default='hg38', help='Genome version (e.g., hg38, mm10)')
        p.add_argument('--geneType', default='mRNA', help='Main gene type (e.g., mRNA, lncRNA)')
        p.add_argument('--cellType', default='all', help='Cell type (e.g., HeLa, all)')

    # 1. miRNATarget
    p_mirna = subparsers.add_parser('miRNATarget', help='Get MiRNA Target Data')
    add_common(p_mirna)
    p_mirna.add_argument('--miRNA', default='all', help='MicroRNA name')
    p_mirna.add_argument('--target', default='all', help='Target gene name')
    p_mirna.add_argument('--clipExpNum', type=int, default=5, help='Min supporting CLIP-seq experiments')
    p_mirna.add_argument('--degraExpNum', type=int, default=0, help='Min supporting degradome-seq experiments')
    p_mirna.add_argument('--pancancerNum', type=int, default=0, help='Min number of Cancer types')
    p_mirna.add_argument('--programNum', type=int, default=1, help='Min number of target-predicting programs')
    p_mirna.add_argument('--program', default='None', help='Target-predicting programs')
    p_mirna.set_defaults(func=cmd_miRNATarget)

    # 2. degradomeRNA
    p_degra = subparsers.add_parser('degradomeRNA', help='Get Data for MiRNAs Cleavage Events')
    add_common(p_degra)
    p_degra.add_argument('--miRNA', default='all', help='MicroRNA name')
    p_degra.add_argument('--target', default='all', help='Target gene name')
    p_degra.add_argument('--degraExpNum', type=int, default=1, help='Min supporting degradome-seq experiments')
    p_degra.set_defaults(func=cmd_degradomeRNA)

    # 3. RNARNA
    p_rna = subparsers.add_parser('RNARNA', help='Get NcRNA-RNA Interaction Network')
    add_common(p_rna)
    p_rna.add_argument('--RNA', default='all', help='RNA name')
    p_rna.add_argument('--interNum', type=int, default=1, help='Min number of RNA-RNA interactions')
    p_rna.add_argument('--expNum', type=int, default=1, help='Min number of experiments')
    p_rna.set_defaults(func=cmd_RNARNA)

    # 4. ceRNA
    p_cerna = subparsers.add_parser('ceRNA', help='Get CeRNA Networks')
    p_cerna.add_argument('--assembly', default='hg38', help='Genome version')
    p_cerna.add_argument('--geneType', default='mRNA', help='Main gene type')
    p_cerna.add_argument('--ceRNA', default='all', help='CeRNA gene name')
    p_cerna.add_argument('--miRNAnum', type=int, default=1, help='Min number of miRNAs')
    p_cerna.add_argument('--family', default='all', help='miRNA family name or ID')
    p_cerna.add_argument('--pval', type=float, default=0.01, help='Max p-value')
    p_cerna.add_argument('--fdr', type=float, default=0.01, help='Max FDR')
    p_cerna.add_argument('--pancancerNum', type=int, default=0, help='Min number of Cancer types')
    p_cerna.set_defaults(func=cmd_ceRNA)

    # 5. RBPTarget
    p_rbp = subparsers.add_parser('RBPTarget', help='Get RBP Target Data')
    add_common(p_rbp)
    p_rbp.add_argument('--RBP', default='all', help='Protein name')
    p_rbp.add_argument('--target', default='all', help='Target gene name')
    p_rbp.add_argument('--clipExpNum', type=int, default=5, help='Min supporting CLIP-seq experiments')
    p_rbp.add_argument('--pancancerNum', type=int, default=0, help='Min number of Cancer types')
    p_rbp.set_defaults(func=cmd_RBPTarget)

    # 6. RBPDisease
    p_dis = subparsers.add_parser('RBPDisease', help='Get RBP and Somatic Gene Mutations Data')
    p_dis.add_argument('--assembly', default='hg38', help='Genome version')
    p_dis.add_argument('--RBP', default='all', help='Protein name')
    p_dis.add_argument('--tissue', required=True, help='Tissue name')
    p_dis.add_argument('--target', default='all', help='Target gene name')
    p_dis.add_argument('--disease', help='Disease name')
    p_dis.set_defaults(func=cmd_RBPDisease)

    # 7. RBPMotifScan
    p_motif = subparsers.add_parser('RBPMotifScan', help='Filter binding motifs of RBPs')
    p_motif.add_argument('--assembly', default='hg38', help='Genome version')
    p_motif.add_argument('--length', default='short', help='Motif length (short|long)')
    p_motif.add_argument('--motif', required=True, help='Motif pattern')
    p_motif.add_argument('--rankLimit', type=int, default=10, help='Rank limit')
    p_motif.set_defaults(func=cmd_RBPMotifScan)

    # 8. bindingSite
    p_bind = subparsers.add_parser('bindingSite', help='Get binding sites of CLIP-seq')
    p_bind.add_argument('--assembly', default='hg38', help='Genome version')
    p_bind.add_argument('--datasetID', required=True, help='Unique dataset ID')
    p_bind.set_defaults(func=cmd_bindingSite)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
