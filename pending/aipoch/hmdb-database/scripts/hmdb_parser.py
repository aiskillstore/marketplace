import xml.etree.ElementTree as ET
import os

class HMDBParser:
    """
    Parses HMDB XML datasets to extract metabolite information.
    """
    
    def __init__(self, xml_file_path):
        """
        Initialize the parser with the path to the HMDB XML file.
        """
        self.xml_file_path = xml_file_path
        if not os.path.exists(xml_file_path):
            raise FileNotFoundError(f"HMDB XML file not found at: {xml_file_path}")

    def search(self, query, search_type="text"):
        """
        Search for metabolites by text (name) or ID.
        Returns a list of matching metabolite dictionaries.
        """
        results = []
        # Note: Parsing the full HMDB XML can be memory intensive.
        # This is a simplified iterative parser.
        context = ET.iterparse(self.xml_file_path, events=("end",))
        
        for event, elem in context:
            if elem.tag == "{http://www.hmdb.ca}metabolite":
                name_elem = elem.find("{http://www.hmdb.ca}name")
                id_elem = elem.find("{http://www.hmdb.ca}accession")
                
                name = name_elem.text if name_elem is not None else ""
                accession = id_elem.text if id_elem is not None else ""
                
                match = False
                if search_type == "text":
                    if query.lower() in name.lower():
                        match = True
                elif search_type == "id":
                    if query.lower() == accession.lower():
                        match = True
                
                if match:
                    results.append({
                        "name": name,
                        "accession": accession,
                        "description": self._get_text(elem, "description"),
                        "chemical_formula": self._get_text(elem, "chemical_formula"),
                        "average_molecular_weight": self._get_text(elem, "average_molecular_weight")
                    })
                    
                # Clear element to save memory
                elem.clear()
                
        return results

    def _get_text(self, parent, tag_name):
        """Helper to safely extract text from a child element."""
        found = parent.find(f"{{http://www.hmdb.ca}}{tag_name}")
        return found.text if found is not None else None

# Example Usage (Commented out)
# if __name__ == "__main__":
#     parser = HMDBParser("hmdb_metabolites.xml")
#     print(parser.search("Caffeine"))
