#!/usr/bin/env python3
"""
SEO Page Generator - Gera múltiplas páginas SEO de uma vez
Parte da skill seo-copywriter-pro

Uso:
    python generate-batch.py --config pages.json --output ./src/app
"""

import json
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Templates base para diferentes tipos de página
TEMPLATES = {
    "technique": '''---
title: "{title}"
description: "{description}"
keywords: {keywords}
---

export const metadata = {{
  title: "{title}",
  description: "{description}",
}}

# {h1}

{intro}

## O Que É {name}?

{what_is}

## Como Funciona

{how_it_works}

## Indicações

{indications}

## Resultados

{results}

## FAQ

{faq}

## Próximos Passos

{cta}
''',

    "blog": '''---
title: "{title}"
description: "{description}"
date: "{date}"
author: "{author}"
category: "{category}"
keywords: {keywords}
---

export const metadata = {{
  title: "{title}",
  description: "{description}",
}}

# {h1}

{intro}

{sections}

## FAQ

{faq}

## Conclusão

{conclusion}
''',

    "location": '''---
title: "{service} em {location} | {brand}"
description: "{service} em {location}. {differentiator}. {cta_text}."
keywords: ["{service} {location}", "{service}", "{location}"]
---

export const metadata = {{
  title: "{service} em {location} | {brand}",
  description: "{service} em {location}. {differentiator}. {cta_text}.",
}}

# {service} em {location}

{intro_location}

## Por Que Escolher {brand} em {location}

{why_choose}

## Nossos Serviços em {location}

{services_list}

## Áreas Atendidas em {location}

{areas}

## FAQ - {service} em {location}

{faq}

## Entre em Contato

{contact_cta}
'''
}

def generate_faq(questions: List[Dict[str, str]]) -> str:
    """Gera seção FAQ formatada"""
    faq_md = ""
    for q in questions:
        faq_md += f"### {q['question']}\n\n{q['answer']}\n\n"
    return faq_md

def generate_page(config: Dict[str, Any], template_type: str) -> str:
    """Gera uma página baseada na configuração"""
    template = TEMPLATES.get(template_type, TEMPLATES["blog"])
    
    # Processar FAQ se existir
    if "faq" in config and isinstance(config["faq"], list):
        config["faq"] = generate_faq(config["faq"])
    
    # Adicionar data se não existir
    if "date" not in config:
        config["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Processar keywords para JSON
    if "keywords" in config and isinstance(config["keywords"], list):
        config["keywords"] = json.dumps(config["keywords"])
    
    return template.format(**config)

def save_page(content: str, output_path: str) -> None:
    """Salva a página no caminho especificado"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Criado: {output_path}")

def process_batch(config_file: str, output_dir: str) -> None:
    """Processa arquivo de configuração e gera todas as páginas"""
    with open(config_file, "r", encoding="utf-8") as f:
        configs = json.load(f)
    
    total = len(configs.get("pages", []))
    print(f"🚀 Gerando {total} páginas...")
    
    for i, page_config in enumerate(configs.get("pages", []), 1):
        template_type = page_config.pop("template", "blog")
        output_path = page_config.pop("output", f"{output_dir}/page-{i}/page.tsx")
        
        content = generate_page(page_config, template_type)
        save_page(content, output_path)
    
    print(f"\n✨ Concluído! {total} páginas geradas.")

def main():
    parser = argparse.ArgumentParser(description="Gerador de páginas SEO em batch")
    parser.add_argument("--config", required=True, help="Arquivo JSON de configuração")
    parser.add_argument("--output", default="./output", help="Diretório de saída")
    
    args = parser.parse_args()
    process_batch(args.config, args.output)

if __name__ == "__main__":
    main()

# ============================================================
# EXEMPLO DE ARQUIVO DE CONFIGURAÇÃO (pages.json)
# ============================================================
"""
{
  "pages": [
    {
      "template": "technique",
      "output": "./src/app/tecnicas/endomidface/page.mdx",
      "title": "Endomidface por Visão Direta | Dr. Robério Brandão",
      "description": "Técnica Endomidface por Visão Direta. 0% lesão nervosa em 212 casos.",
      "keywords": ["endomidface", "visão direta", "midface lift"],
      "h1": "Endomidface por Visão Direta: O Guia Definitivo",
      "name": "Endomidface",
      "intro": "O Endomidface por Visão Direta é...",
      "what_is": "É uma técnica de rejuvenescimento...",
      "how_it_works": "O procedimento é realizado...",
      "indications": "- Queda do terço médio\\n- Sulco nasojugal...",
      "results": "Taxa de 0% lesão nervosa permanente...",
      "faq": [
        {"question": "O que é Endomidface?", "answer": "É uma técnica..."},
        {"question": "Qual a recuperação?", "answer": "7 dias..."}
      ],
      "cta": "Domine a técnica em 30 casos..."
    },
    {
      "template": "blog",
      "output": "./src/content/blog/anatomia-smas.mdx",
      "title": "Anatomia do SMAS: Fundamentos para Cirurgia Facial",
      "description": "Entenda a anatomia do SMAS...",
      "author": "Dr. Robério Brandão",
      "category": "anatomia",
      "keywords": ["anatomia SMAS", "SMAS móvel", "SMAS fixo"],
      "h1": "Anatomia do SMAS: O Guia Completo",
      "intro": "O SMAS é uma estrutura fundamental...",
      "sections": "## SMAS Móvel vs Fixo\\n\\n...\\n\\n## Importância Cirúrgica\\n\\n...",
      "faq": [
        {"question": "O que é SMAS?", "answer": "Sistema Músculo-Aponeurótico..."}
      ],
      "conclusion": "Compreender a anatomia do SMAS é essencial..."
    },
    {
      "template": "location",
      "output": "./src/app/localizacao/sao-paulo/page.mdx",
      "brand": "Dr. Robério Brandão",
      "service": "Cirurgia Facial",
      "location": "São Paulo",
      "differentiator": "18+ anos de experiência",
      "cta_text": "Agende sua consulta",
      "intro_location": "Se você busca cirurgia facial de excelência em São Paulo...",
      "why_choose": "Com 18+ anos de experiência e mais de 1500 procedimentos...",
      "services_list": "- Endomidface\\n- Browlift\\n- Deep Neck...",
      "areas": "Atendemos pacientes de toda a Grande São Paulo...",
      "faq": [
        {"question": "Onde fica a clínica?", "answer": "Nossa clínica está localizada..."}
      ],
      "contact_cta": "Entre em contato para agendar..."
    }
  ]
}
"""
