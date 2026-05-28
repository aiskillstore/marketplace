import argparse
import subprocess
import sys
import os

def annotate_vcf(input_vcf, output_vcf, clinvar_vcf=None):
    """
    Wrapper for bcftools annotate.
    Assumes bcftools is installed and clinvar.vcf.gz is available or provided.
    """
    if not clinvar_vcf:
        # Default path or environment variable could go here
        clinvar_vcf = "clinvar.vcf.gz"
    
    if not os.path.exists(input_vcf):
        print(f"Error: Input file {input_vcf} not found.", file=sys.stderr)
        sys.exit(1)

    cmd = [
        "bcftools", "annotate",
        "-a", clinvar_vcf,
        "-c", "ID,INFO",
        "-o", output_vcf,
        input_vcf
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        # In a real scenario, we might just print the command or run it if allowed.
        # For this skill, we simulate the execution or run it if bcftools exists.
        subprocess.run(cmd, check=True)
        print(f"Annotation complete: {output_vcf}")
    except FileNotFoundError:
        print("Error: bcftools not found in PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running bcftools: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate VCF with ClinVar")
    parser.add_argument("--input", required=True, help="Input VCF file")
    parser.add_argument("--output", required=True, help="Output VCF file")
    parser.add_argument("--clinvar", help="Path to ClinVar VCF reference")
    
    args = parser.parse_args()
    annotate_vcf(args.input, args.output, args.clinvar)
