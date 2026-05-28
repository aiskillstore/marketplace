#!/usr/bin/env python3
"""Disclosure Generator - Convert technical descriptions into structured disclosures"""

import argparse
import json
import sys
from datetime import datetime


TEMPLATE = """#Patent technology disclosure document

**Generation date**: {date}
**Status**: Draft (needs review by the inventor)

---

## 1. Invention name

{title}

## 2. Technical field

The invention relates to the technical field of {domain}, and specifically to {sub_domain}.

## 3. Background technology

### 3.1 Description of existing technology

{prior_art}

### 3.2 Defects in existing technology

The existing technology has the following problems:

{problems}

## 4. Contents of the invention

### 4.1 Technical issues to be solved

The technical problem to be solved by this invention is: {core_problem}

### 4.2 Technical Solution

In order to solve the above technical problems, the present invention adopts the following technical solutions:

{solution}

### 4.3 Beneficial effects

Adopting the technical solution of the present invention has the following beneficial effects:

{benefits}

## 5. Specific implementation methods

### 5.1 Embodiment 1

{implementation}

## 6. Picture description

It is recommended to draw the following drawings:

{figures}

## 7. Keywords

{keywords}

---

## Audit Checklist

- [ ] Whether the invention name accurately reflects the technical solution
- [ ] Is the background technology description complete?
- [ ] Whether the technical solution contains all key features
- [ ] Is the beneficial effect supported by data?
- [ ] Are the examples detailed enough?
- [ ] Can the attached drawing clearly illustrate the plan?

## Next step

1. The inventor reviews and adds technical details
2. Conduct a patent search to confirm novelty
3. Submit to patent attorney to draft claims"""


def extract_info_from_description(description: str) -> dict:
    """Extract key information from technical descriptions
    This is a simplified version, actually done by AI"""
    # default value
    info = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": "A method/device/system of [to be filled in]",
        "domain": "[to be filled in]",
        "sub_domain": "[to be filled in]",
        "prior_art": "[Please describe existing technical solutions]",
        "problems": """1. [Question 1]
2. [Question 2]
3. [Question 3]""",
        "core_problem": "[Please describe the core problem to be solved]",
        "solution": description if description else "[Please describe the technical solution in detail]",
        "benefits": """1. [Effect 1]
2. [Effect 2]
3. [Effect 3]""",
        "implementation": "[Please describe the specific implementation]",
        "figures": """- Figure 1: System architecture diagram
- Figure 2: Flowchart
- Figure 3: Schematic diagram of key modules""",
        "keywords": "[Keyword 1], [Keyword 2], [Keyword 3]"
    }
    
    return info


def generate_disclosure(description: str, output_format: str = "markdown") -> str:
    """Generate disclosure document"""
    info = extract_info_from_description(description)
    
    if output_format == "json":
        return json.dumps(info, ensure_ascii=False, indent=2)
    
    return TEMPLATE.format(**info)


def main():
    parser = argparse.ArgumentParser(description="Patent disclosure document generator")
    parser.add_argument("--input", "-i", help="input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    parser.add_argument("description", nargs="?", help="Technical description (can also be entered via stdin)")
    
    args = parser.parse_args()
    
    # Get input
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            description = f.read()
    elif args.description:
        description = args.description
    elif not sys.stdin.isatty():
        description = sys.stdin.read()
    else:
        print("Please provide a technical description (via parameters, file or stdin)", file=sys.stderr)
        sys.exit(1)
    
    # Generate disclosure document
    result = generate_disclosure(description, args.format)
    
    # output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"saved to: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
