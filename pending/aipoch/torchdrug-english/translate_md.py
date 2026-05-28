import os
import re
from translate import Translator

def translate_text(text):
    """Translate text from Chinese to English"""
    try:
        translator = Translator(to_lang='en', from_lang='zh-CN')
        result = translator.translate(text)
        if result and result != text:
            return result
    except Exception as e:
        print(f"Translation failed: {e}")
    
    return text

def is_chinese(text):
    """Check if text contains Chinese characters"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))

def translate_file(input_path, output_path):
    """Translate a markdown file while preserving format"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    translated_lines = []
    
    for line in lines:
        # Skip code blocks and special lines
        if line.strip().startswith('```') or line.strip().startswith('#') or line.strip().startswith('|') or line.strip() == '':
            translated_lines.append(line)
            continue
        
        # Check if line contains Chinese
        if is_chinese(line):
            translated_line = translate_text(line)
            if translated_line != line:
                translated_lines.append(translated_line)
                print(f"Translated: {line[:50]}... -> {translated_line[:50]}...")
            else:
                translated_lines.append(line)
        else:
            translated_lines.append(line)
    
    translated_content = '\n'.join(translated_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)
    
    print(f"Translated {input_path} -> {output_path}")

# List of files to translate
files = [
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\retrosynthesis.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\protein_modeling.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\molecular_generation.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\molecular_property_prediction.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\models_architectures.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\datasets.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\core_concepts.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\SKILL.md",
    r"C:\Users\29707\Desktop\skil11\torchdrug\references\knowledge_graphs.md"
]

for file in files:
    if os.path.exists(file):
        translate_file(file, file)
    else:
        print(f"File not found: {file}")

print("All files translated!")
