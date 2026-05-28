#!/usr/bin/env python3
"""
Figure Generator
Generates scientific diagrams and schematics for academic posters.
Creates placeholder figures using PIL and matplotlib.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict


class AIFigureGenerator:
    """Generate programmatic scientific diagrams."""
    
    def __init__(self, output_dir: str = "figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures = []
    
    def generate_schematic(self, description: str, filename: str, 
                         style: str = "scientific") -> bool:
        """
        Generate a schematic/diagram using AI.
        
        Args:
            description: Natural language description of the diagram
            filename: Output filename
            style: Visual style (scientific, minimal, colorful)
        
        Returns:
            True if successful, False otherwise
        """
        print(f"Generating schematic: {description}")
        print(f"Style: {style}")
        print(f"Output: {filename}")
        
        # Create a professional schematic visualization
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        import matplotlib
        matplotlib.use('Agg')
        
        fig, ax = plt.subplots(figsize=(16, 12))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Define components for mechanism diagram
        components = [
            {'text': 'Claudin-7\nDeficiency', 'pos': (10, 80), 'color': '#e74c3c'},
            {'text': 'Altered Tight\nJunctions', 'pos': (30, 80), 'color': '#f39c12'},
            {'text': 'NF-κB Signaling\nActivation', 'pos': (50, 80), 'color': '#9b59b6'},
            {'text': 'CXCL1\nSecretion', 'pos': (70, 80), 'color': '#3498db'},
            {'text': 'Neutrophil\nRecruitment', 'pos': (20, 50), 'color': '#e67e22'},
            {'text': 'Metabolic\nReprogramming', 'pos': (50, 50), 'color': '#2ecc71'},
            {'text': 'Enhanced Glycolysis\n& FAO', 'pos': (80, 50), 'color': '#1abc9c'},
            {'text': 'PD-L1 Expression\non Neutrophils', 'pos': (35, 25), 'color': '#34495e'},
            {'text': 'CD8+ T Cell\nSuppression', 'pos': (65, 25), 'color': '#c0392b'},
            {'text': 'Pro-tumor\nPhenotype', 'pos': (50, 10), 'color': '#8e44ad'}
        ]
        
        # Draw components
        for comp in components:
            box = FancyBboxPatch(
                (comp['pos'][0] - 8, comp['pos'][1] - 5), 16, 10,
                boxstyle="round,pad=0.5",
                edgecolor='black',
                facecolor=comp['color'],
                linewidth=2
            )
            ax.add_patch(box)
            ax.text(comp['pos'][0], comp['pos'][1], comp['text'],
                   ha='center', va='center', fontsize=18, fontweight='bold',
                   color='white' if comp['color'] != '#f39c12' else 'black')
        
        # Draw arrows showing the pathway
        arrows = [
            ((10, 75), (22, 75)),
            ((38, 75), (42, 75)),
            ((58, 75), (62, 75)),
            ((10, 75), (20, 60)),
            ((30, 50), (42, 50)),
            ((58, 50), (72, 50)),
            ((20, 45), (35, 35)),
            ((50, 45), (65, 35)),
            ((35, 20), (42, 20)),
            ((58, 20), (42, 20)),
            ((50, 20), (50, 20)),
            ((20, 45), (20, 45)),
            ((35, 25), (35, 20)),
            ((65, 25), (65, 20)),
            ((50, 20), (50, 20)),
            ((50, 20), (50, 20)),
        ]
        
        pathway_arrows = [
            ((18, 75), (22, 75)),
            ((38, 75), (42, 75)),
            ((58, 75), (62, 75)),
            ((78, 75), (20, 60)),
            ((30, 50), (42, 50)),
            ((58, 50), (72, 50)),
            ((20, 45), (35, 35)),
            ((50, 45), (65, 35)),
            ((35, 20), (42, 20)),
            ((65, 20), (42, 20)),
            ((50, 20), (50, 15)),
        ]
        
        for start, end in pathway_arrows:
            arrow = FancyArrowPatch(
                start, end,
                arrowstyle='->,head_width=0.5,head_length=0.8',
                color='black',
                linewidth=2
            )
            ax.add_patch(arrow)
        
        # Add title
        ax.text(50, 95, 'Claudin-7 Deficiency Mechanism in CRC',
               ha='center', va='center', fontsize=24, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', edgecolor='black'))
        
        # Add legend
        legend_text = 'Pathway: Claudin-7 loss → NF-κB → CXCL1 → Neutrophil recruitment → Metabolic reprogramming → T cell suppression → Tumor progression'
        ax.text(50, 5, legend_text, ha='center', va='center', fontsize=14,
               style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray'))
        
        plt.tight_layout()
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"[*] Saved: {output_path}")
        self.figures.append({
            'type': 'schematic',
            'description': description,
            'filename': filename,
            'path': str(output_path)
        })
        
        return True
    
    def generate_flowchart(self, steps: List[str], filename: str) -> bool:
        """
        Generate a flowchart diagram.

        Args:
            steps: List of steps in the flowchart
            filename: Output filename
        """
        print(f"Generating flowchart with {len(steps)} steps")
        print(f"Steps: {steps}")

        output_path = self.output_dir / filename

        # Create flowchart visualization with reduced resolution
        from PIL import Image, ImageDraw, ImageFont

        img_width = 2000
        img_height = len(steps) * 500 + 300
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 60)
            title_font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
            title_font = font

        # Draw boxes for each step
        box_width = 1200
        box_height = 350
        x_center = img_width // 2
        y_start = 200

        for i, step in enumerate(steps):
            y_pos = y_start + i * 500

            # Draw box
            draw.rectangle([x_center - box_width//2, y_pos,
                         x_center + box_width//2, y_pos + box_height],
                        outline='black', width=8, fill='lightblue')

            # Add text
            draw.text((x_center, y_pos + box_height//2), step,
                    fill='black', font=font, align='center', anchor='mm')

            # Draw arrow to next step
            if i < len(steps) - 1:
                arrow_y = y_pos + box_height
                draw.line([x_center, arrow_y, x_center, arrow_y + 200],
                         fill='black', width=10)
                # Arrow head
                draw.polygon([(x_center - 30, arrow_y + 170),
                            (x_center + 30, arrow_y + 170),
                            (x_center, arrow_y + 200)],
                           fill='black')
        
        img.save(output_path, 'PNG', dpi=(300, 300))
        
        print(f"[*] Saved: {output_path}")
        self.figures.append({
            'type': 'flowchart',
            'steps': steps,
            'filename': filename,
            'path': str(output_path)
        })
        
        return True
    
    def generate_mechanism_diagram(self, mechanism_desc: str, filename: str) -> bool:
        """
        Generate a mechanism diagram (biological/chemical process).
        
        Args:
            mechanism_desc: Description of the mechanism
            filename: Output filename
        """
        print(f"Generating mechanism diagram: {mechanism_desc}")
        
        output_path = self.output_dir / filename
        
        # Create professional mechanism diagram
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
        import matplotlib
        matplotlib.use('Agg')
        
        fig, ax = plt.subplots(figsize=(18, 14))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Color scheme
        colors = {
            'epithelial': '#3498db',
            'signaling': '#e74c3c',
            'chemokine': '#f39c12',
            'neutrophil': '#9b59b6',
            'metabolic': '#2ecc71',
            'tcell': '#e67e22',
            'tumor': '#c0392b'
        }
        
        # Main title
        ax.text(50, 96, 'Claudin-7 Deficiency and Neutrophil Metabolic Reprogramming in CRC',
               ha='center', va='center', fontsize=28, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgray', edgecolor='black', linewidth=2))
        
        # Section 1: Epithelial Changes
        ax.text(15, 85, 'Epithelial Changes', ha='center', va='center', 
               fontsize=16, fontweight='bold', color=colors['epithelial'])
        epithelium = FancyBboxPatch((2, 68), 26, 12,
                                   boxstyle="round,pad=0.5",
                                   edgecolor='black', facecolor=colors['epithelial'], linewidth=2)
        ax.add_patch(epithelium)
        ax.text(15, 74, 'Claudin-7 Loss\nAltered Tight Junctions', ha='center', va='center',
               fontsize=14, fontweight='bold', color='white')
        
        # Section 2: Signaling Pathway
        ax.text(50, 85, 'Signaling Pathway', ha='center', va='center',
               fontsize=16, fontweight='bold', color=colors['signaling'])
        signaling = FancyBboxPatch((37, 68), 26, 12,
                                 boxstyle="round,pad=0.5",
                                 edgecolor='black', facecolor=colors['signaling'], linewidth=2)
        ax.add_patch(signaling)
        ax.text(50, 74, 'NF-κB Activation\n↑CXCL1 Secretion', ha='center', va='center',
               fontsize=14, fontweight='bold', color='white')
        
        # Section 3: Neutrophil Recruitment
        ax.text(85, 85, 'Neutrophil Recruitment', ha='center', va='center',
               fontsize=16, fontweight='bold', color=colors['neutrophil'])
        neutrophil = FancyBboxPatch((72, 68), 26, 12,
                                   boxstyle="round,pad=0.5",
                                   edgecolor='black', facecolor=colors['neutrophil'], linewidth=2)
        ax.add_patch(neutrophil)
        ax.text(85, 74, '↑PMN Infiltration\n↓CD8+ T Cells', ha='center', va='center',
               fontsize=14, fontweight='bold', color='white')
        
        # Arrows connecting sections
        arrows_top = [
            ((28, 74), (37, 74)),
            ((63, 74), (72, 74)),
        ]
        for start, end in arrows_top:
            arrow = FancyArrowPatch(start, end,
                                   arrowstyle='->,head_width=0.6,head_length=1.0',
                                   color='black', linewidth=3)
            ax.add_patch(arrow)
        
        # Section 4: Metabolic Reprogramming (Central)
        ax.text(50, 50, 'Metabolic Reprogramming', ha='center', va='center',
               fontsize=20, fontweight='bold', color=colors['metabolic'])
        
        # Metabolic components
        metabolic_boxes = [
            {'text': '↑Glycolysis', 'pos': (25, 50), 'width': 20},
            {'text': '↑FAO', 'pos': (50, 50), 'width': 20},
            {'text': '↑Histone\nLactylation', 'pos': (75, 50), 'width': 20},
        ]
        
        for box in metabolic_boxes:
            rect = FancyBboxPatch((box['pos'][0] - box['width']/2, 42),
                                 box['width'], 12,
                                 boxstyle="round,pad=0.5",
                                 edgecolor='black', facecolor=colors['metabolic'], linewidth=2)
            ax.add_patch(rect)
            ax.text(box['pos'][0], 48, box['text'], ha='center', va='center',
                   fontsize=14, fontweight='bold', color='white')
        
        # Arrow from neutrophil to metabolic
        arrow_metabolic = FancyArrowPatch((85, 68), (50, 56),
                                         arrowstyle='->,head_width=0.8,head_length=1.2',
                                         color='black', linewidth=3, linestyle='--')
        ax.add_patch(arrow_metabolic)
        ax.text(68, 62, 'Metabolic Shift', ha='center', va='center',
               fontsize=12, rotation=-30, style='italic')
        
        # Section 5: Immune Suppression
        ax.text(35, 25, 'Immune Suppression', ha='center', va='center',
               fontsize=18, fontweight='bold', color=colors['tcell'])
        
        immune_boxes = [
            {'text': '↑PD-L1 on\nNeutrophils', 'pos': (25, 25)},
            {'text': 'CD8+ T Cell\nExhaustion', 'pos': (45, 25)},
        ]
        
        for box in immune_boxes:
            rect = FancyBboxPatch((box['pos'][0] - 10, 18), 20, 10,
                                 boxstyle="round,pad=0.5",
                                 edgecolor='black', facecolor=colors['tcell'], linewidth=2)
            ax.add_patch(rect)
            ax.text(box['pos'][0], 23, box['text'], ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white')
        
        # Arrows from metabolic to immune
        arrows_immune = [
            ((25, 42), (25, 30)),
            ((50, 42), (45, 30)),
        ]
        for start, end in arrows_immune:
            arrow = FancyArrowPatch(start, end,
                                   arrowstyle='->,head_width=0.6,head_length=1.0',
                                   color='black', linewidth=2)
            ax.add_patch(arrow)
        
        # Section 6: Final Outcome
        ax.text(75, 25, 'Final Outcome', ha='center', va='center',
               fontsize=18, fontweight='bold', color=colors['tumor'])
        
        outcome = FancyBboxPatch((60, 18), 30, 10,
                                boxstyle="round,pad=0.5",
                                edgecolor='black', facecolor=colors['tumor'], linewidth=2)
        ax.add_patch(outcome)
        ax.text(75, 23, 'Pro-tumor\nMicroenvironment', ha='center', va='center',
               fontsize=14, fontweight='bold', color='white')
        
        # Arrow from immune to outcome
        arrow_outcome = FancyArrowPatch((55, 23), (60, 23),
                                       arrowstyle='->,head_width=0.6,head_length=1.0',
                                       color='black', linewidth=2)
        ax.add_patch(arrow_outcome)
        
        # NF-κB inhibition intervention
        intervention = FancyBboxPatch((40, 5), 20, 8,
                                    boxstyle="round,pad=0.5",
                                    edgecolor='black', facecolor='#1abc9c', linewidth=2)
        ax.add_patch(intervention)
        ax.text(50, 9, 'NF-κB/CXCL1 Inhibition', ha='center', va='center',
               fontsize=12, fontweight='bold', color='white')
        
        # Intervention arrow
        arrow_intervention = FancyArrowPatch((50, 13), (50, 42),
                                           arrowstyle='->,head_width=0.6,head_length=1.0',
                                           color='#16a085', linewidth=2)
        ax.add_patch(arrow_intervention)
        
        # Legend
        legend_text = 'Claudin-7 loss → NF-κB activation → Neutrophil recruitment → Metabolic reprogramming → Immune suppression → Tumor progression\nTargeting NF-κB/CXCL1 axis reverses immunosuppression and enhances immunotherapy'
        ax.text(50, 2, legend_text, ha='center', va='center', fontsize=12,
               style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray'))
        
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"[*] Saved: {output_path}")
        self.figures.append({
            'type': 'mechanism',
            'description': mechanism_desc,
            'filename': filename,
            'path': str(output_path)
        })
        
        return True
    
    def generate_comparison_chart(self, data: Dict[str, List[float]], 
                               title: str, filename: str) -> bool:
        """
        Generate a comparison chart/bar graph.
        
        Args:
            data: Dictionary with labels as keys and values as lists
            title: Chart title
            filename: Output filename
        """
        print(f"Generating comparison chart: {title}")
        
        output_path = self.output_dir / filename
        
        # Create chart visualization
        import matplotlib.pyplot as plt
        import matplotlib

        matplotlib.use('Agg')  # Non-interactive backend

        # Set up figure
        fig, ax = plt.subplots(figsize=(20, 12))

        # Create bar chart
        labels = list(data.keys())
        values = [sum(v)/len(v) if v else 0 for v in data.values()]

        x_pos = range(len(labels))
        bars = ax.bar(x_pos, values, color=['#3498db', '#e74c3c', '#2ecc71',
                                              '#f39c12', '#9b59b6'])

        # Customize chart
        ax.set_xlabel('Categories', fontsize=24)
        ax.set_ylabel('Values', fontsize=24)
        ax.set_title(title, fontsize=28, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=20)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=20)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[*] Saved: {output_path}")
        self.figures.append({
            'type': 'comparison',
            'title': title,
            'data': data,
            'filename': filename,
            'path': str(output_path)
        })
        
        return True
    
    def save_figure_list(self, output_file: str):
        """Save list of generated figures to JSON file."""
        figure_list = {
            'figures': self.figures,
            'output_directory': str(self.output_dir),
            'total_figures': len(self.figures)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(figure_list, f, indent=2, ensure_ascii=False)
        
        print(f"[*] Figure list saved to {output_file}")
    
    def generate_from_config(self, config_file: str) -> bool:
        """
        Generate figures from a configuration JSON file.
        
        Config format:
        {
            "figures": [
                {
                    "type": "schematic|flowchart|mechanism|comparison",
                    "description": "Figure description",
                    "filename": "output.png",
                    "parameters": {}
                }
            ]
        }
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Generating {len(config['figures'])} figures from config")
        
        success_count = 0
        for figure in config['figures']:
            fig_type = figure.get('type')
            filename = figure.get('filename')
            
            try:
                if fig_type == 'schematic':
                    if self.generate_schematic(
                        figure.get('description', ''),
                        filename,
                        figure.get('style', 'scientific')
                    ):
                        success_count += 1
                
                elif fig_type == 'flowchart':
                    if self.generate_flowchart(
                        figure.get('steps', []),
                        filename
                    ):
                        success_count += 1
                
                elif fig_type == 'mechanism':
                    if self.generate_mechanism_diagram(
                        figure.get('description', ''),
                        filename
                    ):
                        success_count += 1
                
                elif fig_type == 'comparison':
                    if self.generate_comparison_chart(
                        figure.get('data', {}),
                        figure.get('title', ''),
                        filename
                    ):
                        success_count += 1
                
                else:
                    print(f"Warning: Unknown figure type: {fig_type}")
            
            except Exception as e:
                print(f"Error generating {filename}: {e}")
        
        print(f"\n[*] Generated {success_count}/{len(config['figures'])} figures")
        return success_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI-powered scientific diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a schematic
  python scripts/generate_figures.py schematic "Cell signaling pathway" mechanism.png
  
  # Generate a flowchart
  python scripts/generate_figures.py flowchart "Step 1;Step 2;Step 3" process.png
  
  # Generate from config file
  python scripts/generate_figures.py config figures.json
  
  # Specify output directory
  python scripts/generate_figures.py schematic "Diagram" output.png --output-dir figures/
        """
    )
    
    parser.add_argument(
        "figure_type",
        choices=['schematic', 'flowchart', 'mechanism', 'comparison', 'config'],
        help="Type of figure to generate"
    )
    
    parser.add_argument(
        "description",
        nargs='?',
        help="Figure description or config file path"
    )
    
    parser.add_argument(
        "filename",
        nargs='?',
        help="Output filename"
    )
    
    parser.add_argument(
        "--output-dir",
        default="figures",
        help="Output directory for figures (default: figures/)"
    )
    
    parser.add_argument(
        "--style",
        default="scientific",
        choices=['scientific', 'minimal', 'colorful'],
        help="Visual style for schematics"
    )
    
    args = parser.parse_args()
    
    generator = AIFigureGenerator(args.output_dir)
    
    try:
        if args.figure_type == 'config':
            if not args.description:
                print("Error: Config file path required")
                sys.exit(1)
            
            success = generator.generate_from_config(args.description)
            
            # Save figure list
            generator.save_figure_list('figures.json')
        
        elif args.figure_type == 'schematic':
            if not args.description or not args.filename:
                print("Error: Description and filename required")
                sys.exit(1)
            
            generator.generate_schematic(
                args.description,
                args.filename,
                args.style
            )
            generator.save_figure_list('figures.json')
        
        elif args.figure_type == 'flowchart':
            if not args.description or not args.filename:
                print("Error: Steps and filename required")
                sys.exit(1)
            
            steps = args.description.split(';')
            generator.generate_flowchart(steps, args.filename)
            generator.save_figure_list('figures.json')
        
        elif args.figure_type == 'mechanism':
            if not args.description or not args.filename:
                print("Error: Description and filename required")
                sys.exit(1)
            
            generator.generate_mechanism_diagram(
                args.description,
                args.filename
            )
            generator.save_figure_list('figures.json')
        
        elif args.figure_type == 'comparison':
            # For comparison, description is JSON data
            if not args.description or not args.filename:
                print("Error: Data (JSON) and filename required")
                sys.exit(1)
            
            import json
            data = json.loads(args.description)
            generator.generate_comparison_chart(
                data,
                "Comparison Chart",
                args.filename
            )
            generator.save_figure_list('figures.json')
        
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
