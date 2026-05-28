import argparse
import json
import sys
import os

# Prevent Python from generating __pycache__ files
sys.dont_write_bytecode = True

# Add current directory to path so modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from protocol_writer import ClinicResearchDesign

def main():
    parser = argparse.ArgumentParser(description="Clinic Research Design")
    
    # Common arguments
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--type', choices=['diagnostic', 'efficacy', 'etiology', 'prognosis'], help='Study Type')
    parser.add_argument('--P', help='Population')
    parser.add_argument('--I', help='Intervention/Index Test/Exposure/Factor')
    parser.add_argument('--C', help='Comparator/Control')
    parser.add_argument('--O', help='Outcome')
    parser.add_argument('--S', help='Study Design Description')
    parser.add_argument('--output_name', default='protocol', help='Output filename (without extension)')
    
    # Specific args (simplified for CLI, can be extended)
    parser.add_argument('--sensitivity', type=float, default=0.8)
    parser.add_argument('--specificity', type=float, default=0.8)
    parser.add_argument('--prevalence', type=float, default=0.5)
    
    args = parser.parse_args()
    
    inputs = {}
    
    if args.interactive:
        print(">>> Clinic Research Design Interactive Mode <<<")
        inputs['type'] = input("Study Type (diagnostic/efficacy/etiology/prognosis): ").strip()
        inputs['picos'] = {}
        inputs['picos']['P'] = input("Population (P): ").strip()
        inputs['picos']['I'] = input("Intervention/Exposure (I): ").strip()
        inputs['picos']['C'] = input("Comparator (C) [Optional]: ").strip()
        inputs['picos']['O'] = input("Outcome (O): ").strip()
        inputs['picos']['S'] = input("Study Design (S): ").strip()
        inputs['study_design'] = inputs['picos']['S']
    else:
        if not args.type or not args.P:
            parser.print_help()
            return
            
        inputs['type'] = args.type
        inputs['picos'] = {
            'P': args.P,
            'I': args.I,
            'C': args.C,
            'O': args.O,
            'S': args.S or "Standard Design"
        }
        inputs['study_design'] = inputs['picos']['S']
        # Pass through calculator args
        inputs['sensitivity'] = args.sensitivity
        inputs['specificity'] = args.specificity
        inputs['prevalence'] = args.prevalence

    writer = ClinicResearchDesign()
    result = writer.write_protocol(inputs)
    
    if result['success']:
        # Define fixed output directory
        # Fixed location: <skill_root>/output
        skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(skill_root, 'output')
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Construct output file path
        filename = f"{args.output_name}.md"
        output_path = os.path.join(output_dir, filename)
        
        # Write only the protocol markdown file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result['protocol'])
            
        print(f"Success! Protocol generated at: {output_path}")
        print(f"Sample Size Calculation Result: {result['data']['sample_size']}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
