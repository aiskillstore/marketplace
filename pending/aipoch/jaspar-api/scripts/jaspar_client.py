import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://jaspar.elixir.no/api/v1/"

def make_request(endpoint, params=None):
    url = BASE_URL + endpoint.strip("/") + "/"
    if params:
        # Filter out None values
        valid_params = {k: v for k, v in params.items() if v is not None}
        if valid_params:
            query_string = urllib.parse.urlencode(valid_params)
            url += "?" + query_string
    
    try:
        # User-Agent is good practice
        req = urllib.request.Request(url, headers={"User-Agent": "JASPAR-Skill-Client/1.0"})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                return {"error": f"HTTP {response.status}", "url": url}
    except urllib.error.HTTPError as e:
        return {"error": str(e), "code": e.code, "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}

def list_matrix(args):
    params = {
        "search": args.search,
        "order": args.order,
        "collection": args.collection,
        "name": args.name,
        "tax_group": args.tax_group,
        "tax_id": args.tax_id,
        "tf_class": args.tf_class,
        "tf_family": args.tf_family,
        "data_type": args.data_type,
        "version": args.version,
        "release": args.release,
        "page": args.page,
        "page_size": args.page_size
    }
    return make_request("matrix", params)

def read_matrix(args):
    return make_request(f"matrix/{args.matrix_id}")

def infer_profile(args):
    return make_request(f"infer/{args.sequence}")

def list_collections(args):
    return make_request("collections", {"search": args.search, "order": args.order, "release": args.release})

def read_collection(args):
    return make_request(f"collections/{args.collection}", {"search": args.search, "order": args.order, "version": args.version, "release": args.release})

def list_species(args):
    return make_request("species", {"search": args.search, "order": args.order, "release": args.release, "page": args.page, "page_size": args.page_size})

def read_species(args):
    return make_request(f"species/{args.tax_id}", {"search": args.search, "order": args.order, "version": args.version, "release": args.release})

def main():
    parser = argparse.ArgumentParser(description="JASPAR API Client")
    subparsers = parser.add_subparsers(dest="command")

    # Matrix List
    p_matrix_list = subparsers.add_parser("matrix_list")
    p_matrix_list.add_argument("--search")
    p_matrix_list.add_argument("--order")
    p_matrix_list.add_argument("--collection")
    p_matrix_list.add_argument("--name")
    p_matrix_list.add_argument("--tax_group")
    p_matrix_list.add_argument("--tax_id")
    p_matrix_list.add_argument("--tf_class")
    p_matrix_list.add_argument("--tf_family")
    p_matrix_list.add_argument("--data_type")
    p_matrix_list.add_argument("--version")
    p_matrix_list.add_argument("--release")
    p_matrix_list.add_argument("--page")
    p_matrix_list.add_argument("--page_size")

    # Matrix Read
    p_matrix_read = subparsers.add_parser("matrix_read")
    p_matrix_read.add_argument("matrix_id")

    # Infer
    p_infer = subparsers.add_parser("infer")
    p_infer.add_argument("sequence")

    # Collections
    p_col_list = subparsers.add_parser("collections_list")
    p_col_list.add_argument("--search")
    p_col_list.add_argument("--order")
    p_col_list.add_argument("--release")

    p_col_read = subparsers.add_parser("collections_read")
    p_col_read.add_argument("collection")
    p_col_read.add_argument("--search")
    p_col_read.add_argument("--order")
    p_col_read.add_argument("--version")
    p_col_read.add_argument("--release")
    
    # Species
    p_species_list = subparsers.add_parser("species_list")
    p_species_list.add_argument("--search")
    p_species_list.add_argument("--order")
    p_species_list.add_argument("--release")
    p_species_list.add_argument("--page")
    p_species_list.add_argument("--page_size")
    
    p_species_read = subparsers.add_parser("species_read")
    p_species_read.add_argument("tax_id")
    p_species_read.add_argument("--search")
    p_species_read.add_argument("--order")
    p_species_read.add_argument("--version")
    p_species_read.add_argument("--release")

    args = parser.parse_args()

    if args.command == "matrix_list":
        print(json.dumps(list_matrix(args), indent=2))
    elif args.command == "matrix_read":
        print(json.dumps(read_matrix(args), indent=2))
    elif args.command == "infer":
        print(json.dumps(infer_profile(args), indent=2))
    elif args.command == "collections_list":
        print(json.dumps(list_collections(args), indent=2))
    elif args.command == "collections_read":
        print(json.dumps(read_collection(args), indent=2))
    elif args.command == "species_list":
        print(json.dumps(list_species(args), indent=2))
    elif args.command == "species_read":
        print(json.dumps(read_species(args), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
