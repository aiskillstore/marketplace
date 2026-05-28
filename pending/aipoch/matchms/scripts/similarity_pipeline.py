import sys
import argparse
from matchms.importing import load_from_mgf, load_from_msp
from matchms import calculate_scores
from matchms.similarity import CosineGreedy, ModifiedCosine

def main():
    parser = argparse.ArgumentParser(description="Matchms Similarity Pipeline")
    parser.add_argument("--input", required=True, help="Input spectra file (MGF/MSP)")
    parser.add_argument("--reference", help="Reference spectra file (MGF/MSP). If not provided, compares input against itself.")
    parser.add_argument("--metric", default="cosine_greedy", choices=["cosine_greedy", "modified_cosine"], help="Similarity metric")
    args = parser.parse_args()

    # Load spectra
    print(f"Loading spectra from {args.input}...")
    try:
        if args.input.lower().endswith(".mgf"):
            spectra = list(load_from_mgf(args.input))
        elif args.input.lower().endswith(".msp"):
            spectra = list(load_from_msp(args.input))
        else:
            print("Unsupported input format. Please use MGF or MSP.")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading input file: {e}")
        sys.exit(1)

    if args.reference:
        print(f"Loading reference spectra from {args.reference}...")
        try:
            if args.reference.lower().endswith(".mgf"):
                references = list(load_from_mgf(args.reference))
            elif args.reference.lower().endswith(".msp"):
                references = list(load_from_msp(args.reference))
            else:
                print("Unsupported reference format. Please use MGF or MSP.")
                sys.exit(1)
        except Exception as e:
            print(f"Error loading reference file: {e}")
            sys.exit(1)
    else:
        references = spectra

    # Select metric
    if args.metric == "cosine_greedy":
        similarity_metric = CosineGreedy()
    elif args.metric == "modified_cosine":
        similarity_metric = ModifiedCosine()
    
    print(f"Calculating scores using {args.metric}...")
    # Calculate scores
    scores = calculate_scores(references, spectra, similarity_metric)
    
    # Output results (simplified for demo)
    print(f"Calculated scores matrix shape: {scores.scores.shape}")
    print("Top scores (example):")
    # In a real skill, we might save this to a file or print top hits
    # Here we just print the shape to confirm it worked
    
if __name__ == "__main__":
    main()
