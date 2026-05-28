import os
import sys
from zeep import Client
import hashlib

# Configuration
WSDL_URL = "https://www.brenda-enzymes.org/soap/brenda_zeep.wsdl"
EMAIL = os.environ.get("BRENDA_EMAIL")
PASSWORD = os.environ.get("BRENDA_PASSWORD")

def get_client():
    if not EMAIL or not PASSWORD:
        print("Error: BRENDA_EMAIL and BRENDA_PASSWORD environment variables must be set.")
        sys.exit(1)
    
    password_hash = hashlib.sha256(PASSWORD.encode("utf-8")).hexdigest()
    client = Client(WSDL_URL)
    return client, password_hash

def parse_result(result_string):
    """
    Parses the BRENDA SOAP API result string.
    Format is typically: key1*value1#key2*value2...
    Returns a list of dictionaries.
    """
    if not result_string:
        return []
        
    parsed_data = []
    # Results are often lists of strings, or a single string
    if isinstance(result_string, list):
        items = result_string
    else:
        items = [result_string]
        
    for item in items:
        entry = {}
        # This is a simplified parser based on the description "organism*E. coli#value*..."
        # Actual format might be complex, but we follow the doc's implication.
        parts = item.split('#')
        for part in parts:
            if '*' in part:
                key, value = part.split('*', 1)
                entry[key] = value
        parsed_data.append(entry)
        
    return parsed_data

def get_km_values(ec_number, organism):
    client, password_hash = get_client()
    try:
        # The parameters string format is specific to BRENDA SOAP
        # Based on doc, we assume a method like getKmValue exists
        # In reality, BRENDA parameters are passed as string "ecNumber*1.1.1.1#organism*Homo sapiens..."
        # But let's follow the user doc's abstraction: get_km_values("1.1.1.1", organism="Homo sapiens")
        
        # Constructing query string for the SOAP call
        parameters = f"ecNumber*{ec_number}#organism*{organism}#password*{password_hash}#email*{EMAIL}"
        
        # Invoke SOAP method (example name based on doc)
        result = client.service.getKmValue(parameters)
        return parse_result(result)
    except Exception as e:
        print(f"Error querying BRENDA: {e}")
        return []

if __name__ == "__main__":
    # Example usage from CLI
    if len(sys.argv) < 3:
        print("Usage: python brenda_queries.py <ec_number> <organism>")
        sys.exit(1)
        
    ec = sys.argv[1]
    org = sys.argv[2]
    
    data = get_km_values(ec, org)
    print(f"Found {len(data)} entries for {ec} in {org}:")
    for entry in data:
        print(entry)
