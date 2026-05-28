import sys
import subprocess
import argparse
import os

def check_environment():
    """Checks if essential dependencies are importable."""
    required_packages = ['torch', 'torch_geometric', 'rdkit', 'esm', 'networkx', 'scipy']
    missing = []
    
    print("Checking DiffDock environment...")
    for pkg in required_packages:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"  [FAIL] {pkg}")
            
    if missing:
        print(f"\nError: Missing dependencies: {', '.join(missing)}")
        print("Please ensure you are in the correct Conda environment or Docker container.")
        sys.exit(1)
    else:
        print("\nEnvironment looks good!")

if __name__ == "__main__":
    check_environment()
