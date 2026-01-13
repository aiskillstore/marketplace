#!/usr/bin/env python3
"""
SEO Validator - Valida páginas criadas contra checklist SEO
Parte da skill seo-copywriter-pro

Uso:
    python validate-seo.py --path ./src/app
    python validate-seo.py --file ./src/app/page.tsx
"""

import os
import re
import argparse
from typing import Dict, List, Tuple
from pathlib import Path

# Regras de validação
RULES = {
    "title": {
        "min_length": 30,
        "max_length": 60,
        "required": True,
        "message": "Title deve ter entre 30-60 caracteres"
    },
    "description": {
        "min_length": 120,
        "max_length": 160,
        "required": True,
        "message": "Description deve ter entre 120-160 caracteres"
    },
    "h1": {
        "count": 1,
        "required": True,
        "message": "Deve haver exatamente 1 H1 por página"
    },
    "content_length": {
        "min_words": 1500,
        "message": "Conteúdo deve ter no mínimo 1500 palavras"
    },
    "internal_links": {
        "min_count": 5,
        "message": "Deve haver no mínimo 5 links internos"
    },
    "images": {
        "require_alt": True,
        "message": "Todas as imagens devem ter alt text"
    },
    "faq": {
        "min_questions": 5,
        "message": "FAQ deve ter no mínimo 5 perguntas"
    }
}

def extract_frontmatter(content: str) -> Dict[str, str]:
    """Extrai frontmatter YAML do conteúdo"""
    frontmatter = {}
    match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
    return frontmatter

def count_words(content: str) -> int:
    """Conta palavras no conteúdo (excluindo código e frontmatter)"""
    # Remove frontmatter
    content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
    # Remove blocos de código
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # Remove tags HTML/JSX
    content = re.sub(r'<[^>]+>', '', content)
    # Conta palavras
    words = re.findall(r'\b\w+\b', content)
    return len(words)

def count_h1s(content: str) -> int:
    """Conta tags H1 no conteúdo"""
    md_h1s = len(re.findall(r'^#\s+[^#]', content, re.MULTILINE))
    html_h1s = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
    return md_h1s + html_h1s

def count_internal_links(content: str) -> int:
    """Conta links internos"""
    # Links markdown internos
    md_links = len(re.findall(r'\[.*?\]\(/[^)]+\)', content))
    # Links JSX/HTML internos
    href_links = len(re.findall(r'href=["\']/?(?!http)[^"\']+["\']', content))
    return md_links + href_links

def check_images_alt(content: str) -> Tuple[int, int]:
    """Verifica imagens com e sem alt text"""
    # Imagens markdown
    md_with_alt = len(re.findall(r'!\[[^\]]+\]', content))
    md_without_alt = len(re.findall(r'!\[\]', content))
    
    # Imagens HTML/JSX
    html_imgs = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
    html_with_alt = sum(1 for img in html_imgs if 'alt=' in img and 'alt=""' not in img)
    html_without_alt = len(html_imgs) - html_with_alt
    
    total_with = md_with_alt + html_with_alt
    total_without = md_without_alt + html_without_alt
    
    return total_with, total_without

def count_faq_questions(content: str) -> int:
    """Conta perguntas no FAQ"""
    # Padrão: ### Pergunta? ou **Pergunta?**
    questions = len(re.findall(r'###\s+.*\?', content))
    questions += len(re.findall(r'\*\*.*\?\*\*', content))
    # Padrão em JSON-LD FAQ
    questions += len(re.findall(r'"@type":\s*"Question"', content))
    return questions

def validate_file(filepath: str) -> Dict[str, any]:
    """Valida um arquivo contra todas as regras"""
    results = {
        "file": filepath,
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter = extract_frontmatter(content)
    
    # Validar Title
    title = frontmatter.get('title', '')
    if len(title) >= RULES['title']['min_length'] and len(title) <= RULES['title']['max_length']:
        results['passed'].append(f"✅ Title OK ({len(title)} chars)")
    else:
        results['failed'].append(f"❌ Title: {len(title)} chars ({RULES['title']['message']})")
    
    # Validar Description
    desc = frontmatter.get('description', '')
    if len(desc) >= RULES['description']['min_length'] and len(desc) <= RULES['description']['max_length']:
        results['passed'].append(f"✅ Description OK ({len(desc)} chars)")
    else:
        results['failed'].append(f"❌ Description: {len(desc)} chars ({RULES['description']['message']})")
    
    # Validar H1
    h1_count = count_h1s(content)
    if h1_count == 1:
        results['passed'].append("✅ H1 único")
    else:
        results['failed'].append(f"❌ H1: encontrado {h1_count} ({RULES['h1']['message']})")
    
    # Validar comprimento do conteúdo
    word_count = count_words(content)
    if word_count >= RULES['content_length']['min_words']:
        results['passed'].append(f"✅ Conteúdo OK ({word_count} palavras)")
    else:
        results['warnings'].append(f"⚠️ Conteúdo curto: {word_count} palavras ({RULES['content_length']['message']})")
    
    # Validar links internos
    internal_links = count_internal_links(content)
    if internal_links >= RULES['internal_links']['min_count']:
        results['passed'].append(f"✅ Links internos OK ({internal_links})")
    else:
        results['warnings'].append(f"⚠️ Poucos links internos: {internal_links} ({RULES['internal_links']['message']})")
    
    # Validar imagens
    imgs_with_alt, imgs_without_alt = check_images_alt(content)
    if imgs_without_alt == 0:
        results['passed'].append(f"✅ Imagens com alt ({imgs_with_alt} imagens)")
    else:
        results['failed'].append(f"❌ {imgs_without_alt} imagens sem alt text")
    
    # Validar FAQ
    faq_count = count_faq_questions(content)
    if faq_count >= RULES['faq']['min_questions']:
        results['passed'].append(f"✅ FAQ OK ({faq_count} perguntas)")
    elif faq_count > 0:
        results['warnings'].append(f"⚠️ FAQ com poucas perguntas: {faq_count} ({RULES['faq']['message']})")
    else:
        results['warnings'].append("⚠️ FAQ não encontrado")
    
    return results

def print_results(results: Dict[str, any]) -> None:
    """Imprime resultados de forma formatada"""
    print(f"\n📄 {results['file']}")
    print("-" * 50)
    
    for item in results['passed']:
        print(f"  {item}")
    
    for item in results['warnings']:
        print(f"  {item}")
    
    for item in results['failed']:
        print(f"  {item}")
    
    total = len(results['passed']) + len(results['failed'])
    score = (len(results['passed']) / total * 100) if total > 0 else 0
    print(f"\n  📊 Score: {score:.0f}% ({len(results['passed'])}/{total})")

def validate_directory(path: str) -> None:
    """Valida todos os arquivos em um diretório"""
    extensions = ['.tsx', '.mdx', '.md', '.jsx']
    files = []
    
    for ext in extensions:
        files.extend(Path(path).rglob(f'*{ext}'))
    
    print(f"🔍 Validando {len(files)} arquivos em {path}...")
    
    all_results = []
    for file in files:
        results = validate_file(str(file))
        all_results.append(results)
        print_results(results)
    
    # Resumo geral
    total_passed = sum(len(r['passed']) for r in all_results)
    total_failed = sum(len(r['failed']) for r in all_results)
    total_warnings = sum(len(r['warnings']) for r in all_results)
    
    print("\n" + "=" * 50)
    print("📊 RESUMO GERAL")
    print("=" * 50)
    print(f"  ✅ Passou: {total_passed}")
    print(f"  ⚠️ Avisos: {total_warnings}")
    print(f"  ❌ Falhou: {total_failed}")
    
    overall = total_passed / (total_passed + total_failed) * 100 if (total_passed + total_failed) > 0 else 0
    print(f"\n  🎯 Score Geral: {overall:.0f}%")

def main():
    parser = argparse.ArgumentParser(description="Validador SEO para páginas")
    parser.add_argument("--path", help="Diretório para validar")
    parser.add_argument("--file", help="Arquivo específico para validar")
    
    args = parser.parse_args()
    
    if args.file:
        results = validate_file(args.file)
        print_results(results)
    elif args.path:
        validate_directory(args.path)
    else:
        print("Uso: python validate-seo.py --path ./src/app")
        print("  ou: python validate-seo.py --file ./src/app/page.tsx")

if __name__ == "__main__":
    main()
