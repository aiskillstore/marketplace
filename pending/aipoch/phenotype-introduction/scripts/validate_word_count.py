#!/usr/bin/env python3
"""
Word count validation script for phenotype introduction skill.
Validates that each section meets minimum word count requirements.
"""

def count_chinese_words(text):
    """Count words in Chinese text (approximate based on character count)."""
    # For Chinese text, we use character count as word count approximation
    # Remove punctuation and count Chinese characters
    import re
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars)

def validate_section_word_count(content, section_name, min_words):
    """Validate that a section meets minimum word count requirement."""
    word_count = count_chinese_words(content)
    
    if word_count >= min_words:
        return {
            'valid': True,
            'word_count': word_count,
            'min_required': min_words,
            'message': f"{section_name} section meets word count requirement ({word_count}/{min_words})"
        }
    else:
        return {
            'valid': False,
            'word_count': word_count,
            'min_required': min_words,
            'message': f"{section_name} section too short ({word_count}/{min_words})"
        }

def extract_sections(content):
    """Extract sections from the formatted output."""
    sections = {}
    
    # Split by section headers
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.strip() == '1. Concept':
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'concept'
            current_content = []
        elif line.strip() == '2. Mechanism and occurrence process':
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'mechanism'
            current_content = []
        elif line.strip() == '3. Regulation':
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'regulation'
            current_content = []
        elif line.strip() == '4.Markers and detection methods':
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'markers'
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def validate_phenotype_content(content):
    """Main validation function for phenotype introduction content."""
    sections = extract_sections(content)
    
    validation_results = {
        'overall_valid': True,
        'section_results': {},
        'marker_count': 0
    }
    
    # Validate word counts
    section_requirements = [
        ('concept', 800),
        ('mechanism', 800), 
        ('regulation', 800),
        ('markers', 500)
    ]
    
    for section_name, min_words in section_requirements:
        if section_name in sections:
            result = validate_section_word_count(sections[section_name], section_name, min_words)
            validation_results['section_results'][section_name] = result
            if not result['valid']:
                validation_results['overall_valid'] = False
        else:
            validation_results['section_results'][section_name] = {
                'valid': False,
                'message': f"{section_name} section missing"
            }
            validation_results['overall_valid'] = False
    
    # Count markers in markers section
    if 'markers' in sections:
        marker_lines = [line for line in sections['markers'].split('\n') 
                       if 'molecular:' in line and 'principle:' in line and 'Detection method:' in line]
        validation_results['marker_count'] = len(marker_lines)
        
        if validation_results['marker_count'] < 5:
            validation_results['overall_valid'] = False
            validation_results['section_results']['markers'] = {
                'valid': False,
                'message': f"Only {validation_results['marker_count']}/5 markers found"
            }
    
    return validation_results

if __name__ == "__main__":
    # Example usage
    sample_content = """1. Concept

Pyroptosis is a form of programmed cell death...

2. Mechanism and occurrence process

The mechanism of pyroptosis involves...

3. Regulation

Regulation: Cell pyroptosis is regulated by multiple signaling pathways...

Phenotype nesting: There is crosstalk between pyroptosis and other cell death modes such as apoptosis and necrosis...

4.Markers and detection methods

Molecule: GSDMD; Principle: GSDMD is a key execution protein of pyroptosis; Detection method: Western blot
Molecule: Caspase-1; Principle: Caspase-1 activation is a sign of pyroptosis; Detection method: Immunofluorescence
Molecule: IL-1β; Principle: IL-1β is an inflammatory factor product of pyroptosis; Detection method: ELISA
Molecule: IL-18; Principle: IL-18 is another inflammatory factor in pyroptosis; Detection method: ELISA
Molecule: PI staining; Principle: PI can mark dead cell membranes; Detection method: Flow cytometry"""
    
    result = validate_phenotype_content(sample_content)
    print("Validation Results:")
    print(f"Overall Valid: {result['overall_valid']}")
    print(f"Marker Count: {result['marker_count']}")
    for section, res in result['section_results'].items():
        print(f"{section}: {res}")