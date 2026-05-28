import pubchempy as pcp
import requests
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def resolve_cid(query_value, query_type):
    """Resolve a query to a PubChem CID."""
    try:
        if query_type == 'cid':
            return int(query_value)
        
        compounds = pcp.get_compounds(query_value, query_type)
        if compounds:
            return compounds[0].cid
        return None
    except Exception as e:
        logger.error(f"Error resolving CID: {e}")
        return None

def get_properties(query_value, query_type='name', properties=None):
    """
    Retrieve properties for a compound.
    Default properties: MolecularWeight, XLogP, TPSA, IsomericSMILES, IUPACName
    """
    if properties is None:
        properties = ['MolecularWeight', 'XLogP', 'TPSA', 'IsomericSMILES', 'IUPACName']
    
    try:
        compounds = pcp.get_compounds(query_value, query_type)
        if not compounds:
            return {"error": "Compound not found"}
        
        compound = compounds[0]
        
        # Extract properties safely
        data = {
            "cid": compound.cid,
            "molecular_weight": getattr(compound, 'molecular_weight', None),
            "xlogp": getattr(compound, 'xlogp', None),
            "tpsa": getattr(compound, 'tpsa', None),
            "isomeric_smiles": getattr(compound, 'isomeric_smiles', None),
            "iupac_name": getattr(compound, 'iupac_name', None)
        }
        return data
    except Exception as e:
        logger.error(f"Error getting properties: {e}")
        return {"error": str(e)}

def structure_search(query_value, search_type='similarity', threshold=90, max_records=10):
    """
    Perform structure search using PubChemPy.
    search_type: 'similarity', 'substructure', etc.
    query_value: typically a SMILES string or CID.
    """
    try:
        # Note: For similarity search via pcp, query_value is usually a SMILES or CID.
        # Ensure we use namespace='smiles' if query is a SMILES string.
        namespace = 'smiles'
        if isinstance(query_value, int) or (isinstance(query_value, str) and query_value.isdigit()):
            namespace = 'cid'
        
        results = pcp.get_compounds(query_value, namespace=namespace, searchtype=search_type, listkey_count=max_records, threshold=threshold)
        
        output = []
        for comp in results[:max_records]:
            output.append({
                "cid": comp.cid,
                "smiles": getattr(comp, 'isomeric_smiles', None)
            })
        return output
    except Exception as e:
        logger.error(f"Structure search failed: {e}")
        return {"error": str(e)}

def get_bioactivity(cid):
    """
    Fetch bioactivity summary for a CID via PUG-REST.
    """
    try:
        # Ensure cid is an integer string
        cid = str(cid)
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/JSON"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
        elif response.status_code == 404:
            return {"error": "No bioactivity data found"}
        else:
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        logger.error(f"Bioactivity fetch failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Test script
    print("Testing get_properties for Aspirin...")
    print(get_properties("Aspirin"))
