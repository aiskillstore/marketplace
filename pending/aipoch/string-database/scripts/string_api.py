
import requests
import pandas as pd
import io
import json
from typing import List, Union, Optional

class StringClient:
    """
    Client for interacting with the STRING Database API (v11+).
    Reference: https://string-db.org/help/api/
    """
    
    BASE_URL = "https://version-12-0.string-db.org/api"
    
    def __init__(self, caller_identity: str = "skill_user"):
        """
        Initialize the STRING client.
        
        Args:
            caller_identity (str): Identifier for the API request (politeness policy).
        """
        # print(f"DEBUG: Initializing StringClient with BASE_URL={self.BASE_URL}")
        self.caller_identity = caller_identity

    def _get_params(self, **kwargs):
        """Helper to inject caller_identity into params."""
        params = {"caller_identity": self.caller_identity}
        params.update(kwargs)
        return params

    def map_id(self, identifier: str, species: int = 9606, limit: int = 1) -> Optional[str]:
        """
        Map a single gene/protein name to a STRING ID.
        
        Args:
            identifier (str): The name to map (e.g., 'TP53').
            species (int): NCBI Taxon ID (default 9606 for Human).
            limit (int): Max number of matches to return.
            
        Returns:
            str: The STRING ID (e.g., '9606.ENSP00000269305') or None if not found.
        """
        endpoint = f"{self.BASE_URL}/json/get_string_ids"
        params = self._get_params(identifiers=identifier, species=species, limit=limit)
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return data[0]['stringId']
            return None
        except Exception as e:
            print(f"Error mapping ID {identifier}: {e}")
            return None

    def map_ids(self, identifiers: List[str], species: int = 9606) -> pd.DataFrame:
        """
        Map a list of identifiers.
        
        Returns:
            pd.DataFrame: Mapping results.
        """
        endpoint = f"{self.BASE_URL}/tsv/get_string_ids"
        params = self._get_params(identifiers="\r".join(identifiers), species=species)
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text), sep="\t")
        except Exception as e:
            print(f"Error mapping IDs: {e}")
            return pd.DataFrame()

    def get_network(self, identifiers: Union[str, List[str]], species: int = 9606, required_score: int = 400) -> pd.DataFrame:
        """
        Retrieve the interaction network for the given identifiers.
        
        Args:
            identifiers: Single ID string or list of IDs.
            species: NCBI Taxon ID.
            required_score: Confidence threshold (0-1000). 400 is medium confidence.
            
        Returns:
            pd.DataFrame: Interaction network data.
        """
        if isinstance(identifiers, str):
            identifiers = [identifiers]
            
        endpoint = f"{self.BASE_URL}/tsv/network"
        params = self._get_params(
            identifiers="\r".join(identifiers),
            species=species,
            required_score=required_score
        )
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text), sep="\t")
        except Exception as e:
            print(f"Error getting network: {e}")
            return pd.DataFrame()

    def get_enrichment(self, identifiers: List[str], species: int = 9606) -> pd.DataFrame:
        """
        Perform functional enrichment analysis (GO, KEGG, etc.).
        
        Args:
            identifiers: List of STRING IDs.
            species: NCBI Taxon ID.
            
        Returns:
            pd.DataFrame: Enrichment results.
        """
        endpoint = f"{self.BASE_URL}/tsv/enrichment"
        params = self._get_params(identifiers="\r".join(identifiers), species=species)
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text), sep="\t")
        except Exception as e:
            print(f"Error getting enrichment: {e}")
            return pd.DataFrame()

    def get_ppi_enrichment(self, identifiers: List[str], species: int = 9606, required_score: int = 400) -> pd.DataFrame:
        """
        Perform PPI enrichment analysis (test if network has more interactions than expected).
        
        Args:
            identifiers: List of STRING IDs.
            species: NCBI Taxon ID.
            required_score: Confidence threshold.
            
        Returns:
            pd.DataFrame: PPI enrichment statistics.
        """
        endpoint = f"{self.BASE_URL}/json/ppi_enrichment"
        params = self._get_params(
            identifiers="\r".join(identifiers), 
            species=species,
            required_score=required_score
        )
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            # The API returns JSON for PPI enrichment stats usually
            return pd.DataFrame(response.json())
        except Exception as e:
            print(f"Error getting PPI enrichment: {e}")
            return pd.DataFrame()

    def get_interaction_partners(self, identifiers: List[str], species: int = 9606, limit: Optional[int] = None, required_score: int = 400) -> pd.DataFrame:
        """
        Get all STRING interaction partners of the proteins.
        """
        endpoint = f"{self.BASE_URL}/tsv/interaction_partners"
        params = self._get_params(
            identifiers="\r".join(identifiers), 
            species=species,
            required_score=required_score
        )
        if limit:
            params['limit'] = limit
            
        try:
            # Try GET first as it might be more stable for this endpoint
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text), sep="\t")
        except Exception as e:
            print(f"Error getting interaction partners: {e}")
            return pd.DataFrame()

    def get_network_image(self, identifiers: List[str], output_file: str, species: int = 9606, 
                         network_type: str = "functional", add_color_nodes: int = 0,
                         hide_node_labels: int = 0) -> bool:
        """
        Retrieve and save the network image.
        """
        endpoint = f"{self.BASE_URL}/image/network"
        params = self._get_params(
            identifiers="\r".join(identifiers),
            species=species,
            network_type=network_type,
            add_color_nodes=add_color_nodes,
            hide_node_labels=hide_node_labels
        )
        
        # print(f"Debug: Requesting {endpoint} with params {params}")
        
        try:
            # Use GET for images to avoid potential POST body parsing issues
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Error getting network image: {e}")
            if 'response' in locals():
                print("Failed URL:", response.url)
            return False

    def get_functional_annotation(self, identifiers: List[str], species: int = 9606) -> pd.DataFrame:
        """
        Get functional annotation (GO, PFAM, etc.) for the proteins.
        """
        endpoint = f"{self.BASE_URL}/tsv/functional_annotation"
        params = self._get_params(identifiers="\r".join(identifiers), species=species)
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text), sep="\t")
        except Exception as e:
            print(f"Error getting functional annotation: {e}")
            return pd.DataFrame()

    def get_version(self) -> str:
        """Get current STRING version."""
        endpoint = f"{self.BASE_URL}/json/version"
        try:
            response = requests.get(endpoint) # Version is usually a GET
            response.raise_for_status()
            return response.json()[0]['string_version']
        except Exception:
            return "Unknown"

# Helper functions for simple functional usage
def string_map_ids(identifier, species=9606):
    client = StringClient()
    return client.map_id(identifier, species)

def string_network(identifiers, species=9606, required_score=400):
    client = StringClient()
    return client.get_network(identifiers, species, required_score)

def string_enrichment(identifiers, species=9606):
    client = StringClient()
    return client.get_enrichment(identifiers, species)
