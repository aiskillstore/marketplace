#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Journal template download module
Automatically download templates from the journal's official website or Overleaf"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.error


class TemplateDownloader:
    """Journal Template Downloader"""

    JOURNAL_SOURCES = {
        "nature": {
            "name": "Nature",
            "url": "https://www.nature.com/documents/nature-subject-index.docx.zip",
            "format": "docx",
        },
        "science": {
            "name": "Science",
            "url": "https://www.sciencemag.org/sites/default/files/Science_Template.dotx",
            "format": "dotx",
        },
        "cell": {
            "name": "Cell Press",
            "url": "https://www.cell.com/cell/templates/Cell_Template.zip",
            "format": "zip",
        },
        "ieee": {
            "name": "IEEE",
            "url": "https://template-selector.ieee.org/validate/templates",
            "format": "tex",
        },
        "acs": {
            "name": "ACS",
            "url": "https://pubs.acs.org/doi/suppl/10.1021/acs.biomac.9b01506/suppl_file/acs.biomac.9b01506-suppl_1.docx",
            "format": "docx",
        },
        "springer": {
            "name": "Springer",
            "url": "https://www.springer.com/gp/authors-editors/book-conference-proceedings/manuscript-preparation",
            "format": "latex",
        },
        "nejm": {
            "name": "NEJM (New England Journal of Medicine)",
            "url": "https://www.nejm.org/doi/suppl/10.1056/NEJMra2025073/suppl_file/NEJMra2025073.pdf",
            "format": "docx",
        },
        "lancet": {
            "name": "The Lancet",
            "url": "https://www.thelancet.com/pb/assets/raw/Lancet/forms/Lancet_Template.docx",
            "format": "docx",
        },
        "nature-medicine": {
            "name": "Nature Medicine",
            "url": "https://www.nature.com/documents/nature-medicine-subject-index.docx.zip",
            "format": "docx",
        },
        "bmj": {
            "name": "BMJ",
            "url": "https://www.bmj.com/sites/default/files/bmj_article_template.docx",
            "format": "docx",
        },
        "jama": {
            "name": "JAMA",
            "url": "https://jamanetwork.ams1.cdn.rainlaworks.com/documents/jama/JAMA_Manuscript_Template.docx",
            "format": "docx",
        },
    }

    OVERLEAF_API = "https://api.overleaf.com/v2"

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or str(
            Path(__file__).parent.parent / "assets" / "templates"
        )
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def download_template(self, journal_name: str, output_path: str = None) -> Dict:
        """Download journal template"""
        journal_key = self._normalize_journal_name(journal_name)

        if journal_key in self.JOURNAL_SOURCES:
            return self._download_from_source(journal_key, output_path)

        return self._search_online(journal_name, output_path)

    def _normalize_journal_name(self, name: str) -> str:
        """Standardized journal title"""
        name = name.lower().strip()

        journal_map = {
            "nature": "nature",
            "nature magazine": "nature",
            "science": "science",
            "science magazine": "science",
            "cell": "cell",
            "cell journal": "cell",
            "ieee": "ieee",
            "acs": "acs",
            "american chemical society": "acs",
            "springer": "springer",
            "elsevier": "elsevier",
            "wiley": "wiley",
            "rsc": "rsc",
        }

        for key, value in journal_map.items():
            if key in name:
                return value

        return name.replace(" ", "-")

    def _download_from_source(self, journal_key: str, output_path: str = None) -> Dict:
        """Download templates from known sources"""
        source = self.JOURNAL_SOURCES.get(journal_key)
        if not source:
            raise ValueError(f"Journal not found {journal_key} template source")

        url = source["url"]
        output_path = output_path or str(
            Path(self.cache_dir) / f"{journal_key}_template.{source['format']}"
        )

        try:
            if url.startswith("http"):
                self._download_file(url, output_path)

            return {
                "journal": source["name"],
                "path": output_path,
                "format": source["format"],
                "status": "success",
            }

        except Exception as e:
            return {
                "journal": source["name"],
                "path": None,
                "format": source["format"],
                "status": "failed",
                "error": str(e),
            }

    def _download_file(self, url: str, output_path: str, timeout: int = 60):
        """Download file"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content = response.read()
                Path(output_path).write_bytes(content)

        except urllib.error.HTTPError as e:
            raise Exception(f"HTTPmistake: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URLmistake: {e.reason}")

    def _search_online(self, journal_name: str, output_path: str = None) -> Dict:
        """Search journal templates online"""
        search_results = {
            "journal": journal_name,
            "path": None,
            "status": "not_found",
            "suggestions": [],
        }

        suggestions = [
            f"Please download the template manually from the journal’s official website，and then use --config Parameter specification",
            "Access to Overleaf template library: https://www.overleaf.com/l/templates",
            "You can visit the Author Center on the journal’s official website to obtain the template.",
        ]

        search_results["suggestions"] = suggestions

        return search_results

    def generate_format_from_template(self, template_path: str) -> Dict:
        """Generate format configuration from template file"""
        path = Path(template_path)

        if not path.exists():
            raise FileNotFoundError(f"English: {template_path}")

        ext = path.suffix.lower()

        if ext in [".docx", ".dotx"]:
            return self._extract_docx_format(template_path)
        elif ext in [".tex", ".cls"]:
            return self._extract_tex_format(template_path)
        else:
            raise ValueError(f"Unsupported template format: {ext}")

    def _extract_docx_format(self, docx_path: str) -> Dict:
        """Extract formatting from Word template"""
        try:
            from docx import Document
            from docx.shared import Pt, Inches

            doc = Document(docx_path)

            format_config = {
                "name": Path(docx_path).stem,
                "version": "1.0",
                "font": {},
                "spacing": {},
                "margins": {},
                "references": {},
                "figures": {},
                "tables": {},
            }

            for paragraph in doc.paragraphs:
                if paragraph.style.name.startswith("Heading"):
                    if "title" not in format_config["font"]:
                        format_config["font"]["title"] = (
                            paragraph.style.font.name or "Times New Roman"
                        )
                        format_config["font"]["title_size"] = (
                            int(paragraph.style.font.size.pt)
                            if paragraph.style.font.size
                            else 14
                        )
                else:
                    if "body" not in format_config["font"]:
                        format_config["font"]["body"] = (
                            paragraph.style.font.name or "Times New Roman"
                        )
                        format_config["font"]["body_size"] = (
                            int(paragraph.style.font.size.pt)
                            if paragraph.style.font.size
                            else 12
                        )

            return format_config

        except ImportError:
            raise ImportError("Need to install python-docx library: pip install python-docx")

    def _extract_tex_format(self, tex_path: str) -> Dict:
        """Extract formatting from LaTeX templates"""
        content = Path(tex_path).read_text(encoding="utf-8")

        format_config = {
            "name": Path(tex_path).stem,
            "version": "1.0",
            "font": {},
            "spacing": {},
            "margins": {},
            "references": {},
            "figures": {},
            "tables": {},
        }

        font_size_match = re.search(r"\\documentclass\[(\d+)pt\]", content)
        if font_size_match:
            format_config["font"]["body_size"] = int(font_size_match.group(1))

        if "\\usepackage{times}" in content or "\\usepackage{txfonts}" in content:
            format_config["font"]["body"] = "Times New Roman"

        if "\\usepackage{setspace}" in content:
            if "\\doublespacing" in content:
                format_config["spacing"]["line_space"] = "double"
            elif "\\onehalfspacing" in content:
                format_config["spacing"]["line_space"] = "1.5"
            else:
                format_config["spacing"]["line_space"] = "single"

        if "\\bibliographystyle{" in content:
            style_match = re.search(r"\\bibliographystyle\{(\w+)\}", content)
            if style_match:
                format_config["references"]["style"] = style_match.group(1)

        return format_config

    def save_format_config(self, config: Dict, output_path: str):
        """Save format configuration to file"""
        path = Path(output_path)

        if path.suffix.lower() == ".json":
            import json

            path.write_text(
                json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        elif path.suffix.lower() in [".yaml", ".yml"]:
            import yaml

            path.write_text(
                yaml.dump(config, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
        else:
            raise ValueError(f"Unsupported configuration format: {path.suffix}")

        return str(path)

    def list_builtin_formats(self) -> List[Dict]:
        """List built-in formats"""
        from format_adjuster import FormatAdjuster

        formats = []
        for key, info in FormatAdjuster.BUILTIN_FORMATS.items():
            formats.append(
                {
                    "key": key,
                    "name": info["name"],
                    "font": info.get("font", {}),
                    "references": info.get("references", {}),
                }
            )

        return formats

    def create_template(self, name: str, config: Dict, output_path: str = None) -> str:
        """Create a custom template configuration file"""
        template = {
            "name": name,
            "version": "1.0",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "font": config.get("font", {}),
            "spacing": config.get("spacing", {}),
            "margins": config.get("margins", {}),
            "references": config.get("references", {}),
            "figures": config.get("figures", {}),
            "tables": config.get("tables", {}),
            "abbreviations": config.get("abbreviations", {}),
        }

        output_path = output_path or str(
            Path(self.cache_dir) / f"{name.lower().replace(' ', '_')}.json"
        )

        import json

        Path(output_path).write_text(
            json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return output_path
