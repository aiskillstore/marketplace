import xml.etree.ElementTree as ET
import sys
import os

def parse_drugbank(xml_path):
    """
    Parses the DrugBank XML file.
    """
    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}", file=sys.stderr)
        return

    print(f"Parsing {xml_path}...")
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Namespace handling would go here
        ns = '{http://www.drugbank.ca}'
        count = 0
        for drug in root.findall(f"{ns}drug"):
            count += 1
            # Extract basic info
            name = drug.find(f"{ns}name").text
            print(f"Found drug: {name}")
            if count >= 5: break # Demo limit
        print(f"Parsed initial entries successfully.")
    except Exception as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_drugbank(sys.argv[1])
    else:
        print("Usage: python parse_xml.py <path_to_xml>")
