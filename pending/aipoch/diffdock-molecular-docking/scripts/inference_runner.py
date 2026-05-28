import argparse
import subprocess
import os
import sys

def run_inference(protein_path, ligand_smiles, out_dir, config="default_inference_args.yaml"):
    """
    Wrapper for the main DiffDock inference module.
    Constructs the command line arguments and executes the model.
    """
    
    # Ensure output directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    # Construct the command
    # Assuming 'python -m inference' is the standard entry point as per docs
    cmd = [
        sys.executable, "-m", "inference",
        "--config", config,
        "--protein_path", protein_path,
        "--ligand", ligand_smiles,
        "--out_dir", out_dir
    ]
    
    print(f"Running DiffDock Inference...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Check if 'inference' module exists/is runnable implies running in the root of DiffDock repo usually
        # For this skill, we assume the user is in the DiffDock root or has it in PYTHONPATH
        subprocess.run(cmd, check=True)
        print(f"\nSuccess! Results saved to {out_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\nError during inference: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\nError: Could not execute python. Please check your path.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DiffDock Inference")
    parser.add_argument("--protein", required=True, help="Path to protein PDB file")
    parser.add_argument("--ligand", required=True, help="Ligand SMILES string")
    parser.add_argument("--out_dir", default="results/", help="Output directory")
    parser.add_argument("--config", default="default_inference_args.yaml", help="Path to config yaml")
    
    args = parser.parse_args()
    
    run_inference(args.protein, args.ligand, args.out_dir, args.config)
