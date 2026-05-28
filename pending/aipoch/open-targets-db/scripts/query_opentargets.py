import requests
import argparse
import json
import sys

def query_opentargets(entity_id, query_type):
    """
    Query Open Targets Platform API.
    """
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"
    
    # Normalize EFO ID format (replace colon with underscore if needed)
    if query_type == "disease" and ":" in entity_id:
        entity_id = entity_id.replace(":", "_")
    
    # Construct query based on type
    if query_type == "target":
        query = """query targetQuery($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    approvedSymbol
    approvedName
    associatedDiseases {
      rows {
        disease { 
          id
          name 
        }
        score
        datatypeScores {
          componentId
          score
        }
      }
    }
  }
}"""
        variables = {"ensemblId": entity_id}
    elif query_type == "disease":
        # Enhanced disease query with more details
        query = """query diseaseQuery($efoId: String!) {
  disease(efoId: $efoId) {
    name
    description
    associatedTargets {
      count
      rows {
        target { 
          id
          approvedSymbol
          approvedName
        }
        score
      }
    }
  }
}"""
        variables = {"efoId": entity_id}
    elif query_type == "search":
        # Search for diseases or targets
        query = """{
  search(queryString: "%s") {
    hits {
      id
      name
    }
  }
}""" % entity_id
        variables = {}
    else:
        # Generic or raw query could be supported here
        print(f"Error: Unsupported query type '{query_type}'")
        sys.exit(1)

    try:
        r = requests.post(base_url, json={"query": query, "variables": variables})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error querying Open Targets: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Open Targets Platform")
    parser.add_argument("--id", required=True, help="Ensembl ID, EFO ID, or search term")
    parser.add_argument("--type", required=True, choices=["target", "disease", "search"], help="Query type")
    
    args = parser.parse_args()
    
    result = query_opentargets(args.id, args.type)
    print(json.dumps(result, indent=2))
