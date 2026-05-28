import argparse
import urllib.request
import urllib.parse
import urllib.error
import sys
import json
import time
import socket

def query_ctd(input_type, input_terms, report, output_format):
    """
    Query the CTD Batch Query API with retry logic and structured error handling.
    """
    base_url = "https://ctdbase.org/tools/batchQuery.go"
    
    # inputTerms should be pipe-separated
    terms_str = "|".join(input_terms)
    
    params = {
        "inputType": input_type,
        "inputTerms": terms_str,
        "report": report,
        "format": output_format
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    max_retries = 3
    retry_delay = 2 # seconds
    timeout = 30 # seconds
    
    for attempt in range(max_retries):
        try:
            # User-Agent is often required by some APIs to avoid 403
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8')
                
                # Verify JSON integrity if requested
                if output_format == 'json':
                    if not content.strip():
                        raise ValueError("Empty response received")
                    try:
                        json.loads(content)
                    except json.JSONDecodeError:
                        # Sometimes APIs return HTML error pages instead of JSON
                        raise ValueError("Received invalid JSON response (possibly HTML error page)")
                
                print(content)
                return # Success

        except (urllib.error.URLError, socket.timeout, ValueError, ConnectionError) as e:
            # Retry on network-related errors
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            
            # Final attempt failed
            error_msg = str(e)
            if hasattr(e, 'reason'):
                error_msg = str(e.reason)
            
            if output_format == 'json':
                error_response = {
                    "status": "error",
                    "message": f"Unable to connect toCTDdatabase (ctdbase.org) or network timeout: {error_msg}",
                    "suggestion": "The network connection may be unstable, please check the network or try again later. If you have other CTD data files available, you can use the local file for analysis.",
                    "request": params
                }
                print(json.dumps(error_response, ensure_ascii=False))
            else:
                print(f"Network Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
            
        except urllib.error.HTTPError as e:
            # Retry on Server Errors (5xx)
            if e.code >= 500 and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue

            if output_format == 'json':
                error_response = {
                    "status": "error",
                    "message": f"CTD API return HTTP {e.code}: {e.reason}",
                    "suggestion": "Please check whether the input parameters are correct, or the CTD server is temporarily unavailable.",
                    "request": params
                }
                print(json.dumps(error_response, ensure_ascii=False))
            else:
                 print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            sys.exit(1)

        except Exception as e:
            if output_format == 'json':
                error_response = {
                    "status": "error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "request": params
                }
                print(json.dumps(error_response, ensure_ascii=False))
            else:
                print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query CTD Batch API")
    parser.add_argument("--inputType", required=True, help="chem, disease, gene, go, pathway, phenotype, reference")
    parser.add_argument("--inputTerms", required=True, nargs='+', help="List of query terms (space separated)")
    parser.add_argument("--report", required=True, help="Report type (e.g., genes_curated, diseases_curated)")
    parser.add_argument("--format", default="json", choices=["json", "xml", "tsv", "csv"], help="Output format")
    
    args = parser.parse_args()
    
    query_ctd(args.inputType, args.inputTerms, args.report, args.format)
