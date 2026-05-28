import argparse
import pandas as pd
from arboreto.algo import grnboost2, genie3

def main():
    parser = argparse.ArgumentParser(description='Infer Gene Regulatory Networks using Arboreto.')
    parser.add_argument('--input', type=str, required=True, help='Path to input expression matrix (TSV/CSV). Genes as columns.')
    parser.add_argument('--output', type=str, required=True, help='Path to output network file.')
    parser.add_argument('--algo', type=str, choices=['grnboost2', 'genie3'], default='grnboost2', help='Inference algorithm.')
    parser.add_argument('--separator', type=str, default='\t', help='Separator for input file (default: tab).')
    
    args = parser.parse_args()
    
    print(f"Loading data from {args.input}...")
    # Load expression data
    try:
        expression_matrix = pd.read_csv(args.input, sep=args.separator)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Running inference using {args.algo}...")
    
    try:
        if args.algo == 'grnboost2':
            network = grnboost2(expression_data=expression_matrix)
        else:
            network = genie3(expression_data=expression_matrix)
    except Exception as e:
        print(f"Error during inference: {e}")
        return

    print(f"Saving network to {args.output}...")
    # Save
    network.to_csv(args.output, sep='\t', index=False, header=False)
    print("Done.")

if __name__ == '__main__':
    main()
