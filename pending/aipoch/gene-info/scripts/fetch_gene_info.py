import os
import sys
import json
import time
import requests
import xml.etree.ElementTree as ET
import logging
import argparse
import re
import csv
import io
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# Logging setup - log to stderr so stdout is clean for JSON piping
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)
logger = logging.getLogger('gene_info_tool')

class NCBIClient:
    """Base client for NCBI E-utilities"""
    def __init__(self, email, api_key=None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.email = email
        self.api_key = api_key
        # Rate limits: 10 req/s with key, 3 req/s without key
        self.delay = 0.15 if api_key else 0.4

    def _get(self, endpoint, params, retries=3):
        url = f"{self.base_url}{endpoint}"
        if self.email:
            params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
        
        for i in range(retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    time.sleep(self.delay)
                    return response
                elif response.status_code == 429:
                    wait = (i + 1) * 2
                    logger.warning(f"Rate limit hit (429), waiting {wait}s")
                    time.sleep(wait)
                else:
                    logger.warning(f"Request failed: {response.status_code} {response.text}")
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Request error: {e}")
                time.sleep(1)
        return None

class PubMedSearch(NCBIClient):
    """Class for querying PubMed article counts and links"""
    
    def get_linked_article_count(self, gene_id, keyword=None):
        """
        Get article count using ELink (Gene -> PubMed).
        More accurate than text search.
        """
        if not gene_id:
            return 0
            
        params = {
            "dbfrom": "gene",
            "db": "pubmed",
            "id": gene_id,
            "cmd": "neighbor",
            "retmode": "json" # Try JSON first
        }
        
        if keyword:
            # ELink supports term filtering for the destination database
            params["term"] = keyword
            
        # Try JSON
        resp = self._get("elink.fcgi", params)
        if resp:
            try:
                data = resp.json()
                # Parse JSON structure for ELink
                # Structure: linksets -> [linkset] -> linksetdbs -> [linksetdb] -> links -> [id]
                linksets = data.get('linksets', [])
                count = 0
                for ls in linksets:
                    linksetdbs = ls.get('linksetdbs', [])
                    for lsdb in linksetdbs:
                        if lsdb.get('dbname') == 'pubmed':
                            count += len(lsdb.get('links', []))
                return count
            except:
                # Fallback to XML parsing if JSON fails or structure differs
                pass
                
        # Fallback to XML if JSON failed (retry without retmode or just parse the resp if it was XML)
        if resp and resp.text.strip().startswith('<'):
            try:
                root = ET.fromstring(resp.text)
                # Count Link/Id inside LinkSetDb where DbTo=pubmed
                count = 0
                for linkset in root.findall(".//LinkSetDb"):
                    if linkset.find("DbTo").text == "pubmed":
                        count += len(linkset.findall(".//Link/Id"))
                return count
            except Exception as e:
                logger.error(f"Error parsing ELink XML: {e}")
        
        return 0

    def search_gene_articles(self, gene_symbol, keyword=None):
        """
        Legacy text search.
        """
        query = f"{gene_symbol}"
        if keyword:
            query = f"{gene_symbol} AND {keyword}"
            
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "rettype": "count",
            "tool": "PubMedGeneSearch"
        }
        
        resp = self._get("esearch.fcgi", params)
        if resp:
            try:
                data = resp.json()
                return int(data.get('esearchresult', {}).get('count', 0))
            except:
                pass
        return 0

class NCBIGeneFetcher(NCBIClient):
    """Class for fetching gene details from NCBI Gene DB"""
    
    def resolve_gene_ids(self, gene_symbols, organism="human"):
        """
        Batch resolve symbols to IDs using OR query.
        Returns dict: {symbol: gene_id}
        """
        if not gene_symbols:
            return {}
            
        # Construct query: (Sym1[Sym] OR Sym2[Sym]) AND Organism[Orgn]
        # Note: This is an approximation. Some symbols might be ambiguous.
        # Ideally we process huge lists in chunks.
        chunk_size = 50
        mapping = {}
        
        for i in range(0, len(gene_symbols), chunk_size):
            chunk = gene_symbols[i:i+chunk_size]
            or_clause = " OR ".join([f"{s}[Gene Symbol]" for s in chunk])
            query = f"({or_clause}) AND {organism}[Organism]"
            
            params = {
                "db": "gene",
                "term": query,
                "retmode": "json",
                "retmax": len(chunk) * 2, # Allow for some duplicates/ambiguity
                "tool": "GeneIDResolver"
            }
            
            resp = self._get("esearch.fcgi", params)
            if resp:
                try:
                    data = resp.json()
                    id_list = data.get('esearchresult', {}).get('idlist', [])
                    if id_list:
                        # Now we have a bag of IDs. We need to know which ID is which Symbol.
                        # We must fetch summaries to map them back.
                        summaries = self.fetch_summaries_by_ids(id_list)
                        for gene_id, summary in summaries.items():
                            sym = summary.get('gene_symbol')
                            # Case-insensitive match against requested symbols
                            for req_sym in chunk:
                                if sym and req_sym.lower() == sym.lower():
                                    mapping[req_sym] = gene_id
                except Exception as e:
                    logger.error(f"Error resolving IDs: {e}")
                    
        return mapping

    def fetch_summaries_by_ids(self, gene_ids):
        """
        Batch fetch summaries for a list of Gene IDs.
        Returns dict: {gene_id: summary_dict}
        """
        if not gene_ids:
            return {}
            
        results = {}
        chunk_size = 50 # ESummary limit
        
        for i in range(0, len(gene_ids), chunk_size):
            chunk = gene_ids[i:i+chunk_size]
            ids_str = ",".join(chunk)
            
            params = {
                "db": "gene",
                "id": ids_str,
                "retmode": "json",
                "tool": "GeneSummaryFetcher"
            }
            
            resp = self._get("esummary.fcgi", params)
            if resp:
                try:
                    data = resp.json()
                    uids = data.get('result', {}).get('uids', [])
                    for uid in uids:
                        info = data['result'][uid]
                        results[uid] = {
                            "gene_id": uid,
                            "gene_symbol": info.get("name", ""),
                            "gene_description": info.get("description", ""),
                            "summary": info.get("summary", ""),
                            "chromosome": info.get("chromosome", ""),
                            "organism": info.get("organism", {}).get("scientificname", "")
                        }
                except Exception as e:
                    logger.error(f"Error parsing summaries: {e}")
                    
        return results

class EnsemblFetcher:
    """Class for interacting with Ensembl REST API"""
    
    def __init__(self):
        self.base_url = "https://rest.ensembl.org"
        self.headers = {"Content-Type": "application/json"}
    
    def _get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        retries = 3
        for i in range(retries):
            try:
                resp = requests.get(url, params=params, headers=self.headers, timeout=30)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 429:
                    time.sleep((i + 1) * 2)
                else:
                    # Ensembl often returns 400 for not found, which is fine
                    if resp.status_code != 400:
                        logger.warning(f"Ensembl error {resp.status_code}: {resp.text}")
                    return None
            except Exception as e:
                logger.error(f"Ensembl request error: {e}")
                time.sleep(1)
        return None

    def get_gene_data(self, gene_symbol, species="human", include_sequence=False, include_homology=False):
        """
        Fetch Ensembl data for a gene.
        """
        # 1. Lookup ID from Symbol
        lookup_endpoint = f"lookup/symbol/{species}/{gene_symbol}"
        data = self._get(lookup_endpoint, {"expand": 1})
        
        result = {
            "ensembl_id": None,
            "transcript_count": 0,
            "max_amino_acids": 0,
            "description": "Not found in Ensembl"
        }
        
        if not data:
            return result
            
        result["ensembl_id"] = data.get("id")
        result["description"] = data.get("description")
        
        transcripts = data.get("Transcript", [])
        result["transcript_count"] = len(transcripts)
        
        max_aa = 0
        for t in transcripts:
            length = t.get("Translation", {}).get("length", 0)
            if length > max_aa:
                max_aa = length
        result["max_amino_acids"] = max_aa
        
        # 2. Optional: Sequence (Genomic)
        if include_sequence and result["ensembl_id"]:
            seq_endpoint = f"sequence/id/{result['ensembl_id']}"
            seq_data = self._get(seq_endpoint, {"type": "genomic"})
            if seq_data:
                result["sequence"] = seq_data.get("seq", "")
                
        # 3. Optional: Homology
        if include_homology and result["ensembl_id"]:
            hom_endpoint = f"homology/id/{species}/{result['ensembl_id']}"
            hom_data = self._get(hom_endpoint, {"type": "orthologues"})
            if hom_data:
                homologies = hom_data.get("data", [])
                orthologs = []
                for h in homologies:
                    for hom in h.get("homologies", []):
                        orthologs.append({
                            "species": hom.get("target", {}).get("species"),
                            "symbol": hom.get("target", {}).get("display_id"),
                            "type": hom.get("type")
                        })
                result["orthologs"] = orthologs[:5] # Limit to 5 for brevity
                
        return result

def read_genes_from_file(file_path):
    """Read genes from file (CSV/Text)"""
    genes = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Try detecting CSV header
        lines = content.splitlines()
        # ... (simplified logic for brevity, relying on basic splitting for now as user provided robust input examples)
        tokens = re.split(r'[,\s;\n\t]+', content)
        genes = [t.strip() for t in tokens if t.strip()]
        
        # Filter out common header words if they got in
        blacklist = {'gene', 'symbol', 'name'}
        genes = [g for g in genes if g.lower() not in blacklist]
        
        return genes
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return []

def write_csv(results, output_file):
    """Write results to CSV"""
    if not results:
        return
    
    # Flatten complex fields for CSV
    flat_results = []
    for r in results:
        flat = r.copy()
        if 'orthologs' in flat:
            flat['orthologs'] = "; ".join([f"{o['species']}:{o['symbol']}" for o in flat['orthologs']])
        if 'sequence' in flat:
             flat['sequence'] = "Sequence_Truncated_For_CSV" # Too long
        flat_results.append(flat)

    keys = set()
    for r in flat_results:
        keys.update(r.keys())
    
    fieldnames = ['gene_symbol'] + [k for k in sorted(list(keys)) if k != 'gene_symbol']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_results)
    except Exception as e:
        logger.error(f"Error writing CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch gene information")
    parser.add_argument("genes", nargs='*', help="List of Gene symbols")
    parser.add_argument("--file", help="Path to file containing gene symbols")
    parser.add_argument("--keyword", help="PubMed keyword")
    parser.add_argument("--output", help="Output file (JSON/CSV)")
    parser.add_argument("--workers", type=int, default=3, help="Number of parallel workers")
    parser.add_argument("--api-key", help="NCBI API Key")
    parser.add_argument("--email", help="Email for NCBI (optional but recommended)")
    parser.add_argument("--include-sequence", action="store_true", help="Include genomic sequence from Ensembl")
    parser.add_argument("--include-homology", action="store_true", help="Include orthologs from Ensembl")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("NCBI_API_KEY")
    email = args.email or os.environ.get("NCBI_EMAIL")
    
    if not email:
        logger.warning("No email provided. Using default rate limits. Providing an email is recommended by NCBI.")
        # sys.exit(1) # Removed strict requirement
        
    genes_to_process = []
    if args.genes:
        genes_to_process.extend(args.genes)
    if args.file:
        genes_to_process.extend(read_genes_from_file(args.file))
        
    if not genes_to_process:
        logger.error("No genes specified.")
        sys.exit(1)
        
    # Remove duplicates
    genes_to_process = list(set(genes_to_process))
    logger.info(f"Processing {len(genes_to_process)} genes...")
    
    # Initialize Clients
    ncbi_gene = NCBIGeneFetcher(email, api_key)
    pubmed = PubMedSearch(email, api_key)
    ensembl = EnsemblFetcher()
    
    final_results = []
    
    # 1. Batch Resolve NCBI IDs and Fetch Summaries (Optimization)
    logger.info("Resolving Gene IDs and fetching summaries...")
    # Map Symbol -> GeneID
    symbol_map = ncbi_gene.resolve_gene_ids(genes_to_process)
    # Fetch Summaries for all IDs found
    all_ids = list(symbol_map.values())
    summaries_map = ncbi_gene.fetch_summaries_by_ids(all_ids)
    
    # 2. Parallel Processing for PubMed and Ensembl (Compute/Net heavy)
    logger.info("Fetching PubMed and Ensembl data...")
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Define worker task
        def process_single_gene(symbol):
            res = {"gene_symbol": symbol}
            
            # Merge NCBI Summary if available
            gene_id = symbol_map.get(symbol)
            if gene_id and gene_id in summaries_map:
                res.update(summaries_map[gene_id])
            else:
                res["error_ncbi"] = "Gene not found in NCBI"
                
            # Fetch PubMed
            try:
                # Prefer ELink if Gene ID is available
                if gene_id:
                     res["total_publications"] = pubmed.get_linked_article_count(gene_id)
                     if args.keyword:
                         res["keyword_publications"] = pubmed.get_linked_article_count(gene_id, args.keyword)
                         res["keyword"] = args.keyword
                else:
                    # Fallback to text search
                    res["total_publications"] = pubmed.search_gene_articles(symbol)
                    if args.keyword:
                        res["keyword_publications"] = pubmed.search_gene_articles(symbol, args.keyword)
                        res["keyword"] = args.keyword
            except Exception as e:
                res["error_pubmed"] = str(e)
                
            # Fetch Ensembl
            try:
                ensembl_data = ensembl.get_gene_data(
                    symbol, 
                    include_sequence=args.include_sequence,
                    include_homology=args.include_homology
                )
                res.update(ensembl_data)
            except Exception as e:
                res["error_ensembl"] = str(e)
                
            return res

        future_to_gene = {executor.submit(process_single_gene, g): g for g in genes_to_process}
        
        for future in concurrent.futures.as_completed(future_to_gene):
            gene = future_to_gene[future]
            try:
                data = future.result()
                final_results.append(data)
            except Exception as e:
                logger.error(f"Error processing {gene}: {e}")
                final_results.append({"gene_symbol": gene, "error": str(e)})

    # Output
    if args.output:
        if args.output.endswith('.csv'):
            write_csv(final_results, args.output)
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {args.output}")
    
    print(json.dumps(final_results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
