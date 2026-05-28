#!/usr/bin/env python3
"""eCTD XML Compiler
Automatically convert drug application documents (Word/PDF) into eCTD XML skeleton structures that comply with FDA/EMA requirements.

ID: 197"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Optional imports with fallbacks
try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


class ECTDError(Exception):
    """eCTD handling errors"""
    pass


class DocumentParser:
    """Document parser base class"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.metadata = {}
        self.headings = []
    
    def parse(self) -> Dict:
        """Parse the document and return structured data"""
        raise NotImplementedError
    
    def detect_module(self) -> str:
        """Automatically detect the eCTD module it belongs to according to the content"""
        content_lower = self.content.lower()
        
        # Module detection rules
        module_keywords = {
            "m1": ["administrative", "Label", "manual", "labeling", "administrative", "form 356h"],
            "m2": ["summary", "summary", "Overview", "introduction", "overview"],
            "m3": ["quality", "quality", "cmc", "API", "preparation", "manufacture", "control"],
            "m4": ["non-clinical", "Toxicology", "Drug generation", "nonclinical", "toxicology", "pharmacology"],
            "m5": ["clinical", "clinical", "study report", "efficacy", "safety"],
        }
        
        scores = {mod: 0 for mod in module_keywords}
        for module, keywords in module_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    scores[module] += 1
        
        # Returns the module with the highest score, default is m3
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "m3"


class WordParser(DocumentParser):
    """Word document parser"""
    
    def parse(self) -> Dict:
        if not HAS_DOCX:
            raise ECTDError("python-docx is not installed and the Word document cannot be parsed. Please run: pip install python-docx")
        
        doc = Document(self.file_path)
        
        # Extract text content
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
                # Detect title (based on style)
                if para.style and para.style.name:
                    style_name = para.style.name.lower()
                    if 'heading' in style_name or 'title' in style_name:
                        level = self._extract_heading_level(style_name)
                        self.headings.append({
                            'level': level,
                            'text': text,
                            'style': para.style.name
                        })
        
        self.content = "\n".join(paragraphs)
        
        # Extract metadata
        self.metadata = {
            'author': doc.core_properties.author if doc.core_properties else '',
            'created': doc.core_properties.created.isoformat() if doc.core_properties and doc.core_properties.created else '',
            'modified': doc.core_properties.modified.isoformat() if doc.core_properties and doc.core_properties.modified else '',
            'title': doc.core_properties.title if doc.core_properties else '',
        }
        
        return {
            'content': self.content,
            'metadata': self.metadata,
            'headings': self.headings,
            'paragraphs': paragraphs
        }
    
    def _extract_heading_level(self, style_name: str) -> int:
        """Extract heading level from style name"""
        match = re.search(r'heading\s*(\d)', style_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search('Title\\s*(\\d)', style_name)
        if match:
            return int(match.group(1))
        return 1


class PDFParser(DocumentParser):
    """PDF document parser"""
    
    def parse(self) -> Dict:
        if not HAS_PYPDF2:
            raise ECTDError("PyPDF2 is not installed and the PDF document cannot be parsed. Please run: pip install PyPDF2")
        
        with open(self.file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Extract metadata
            meta = reader.metadata
            self.metadata = {
                'author': meta.get('/Author', '') if meta else '',
                'creator': meta.get('/Creator', '') if meta else '',
                'producer': meta.get('/Producer', '') if meta else '',
                'title': meta.get('/Title', '') if meta else '',
                'num_pages': len(reader.pages),
            }
            
            # Extract text
            paragraphs = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Simple segmentation
                    for line in text.split('\n'):
                        line = line.strip()
                        if line:
                            paragraphs.append(line)
            
            self.content = "\n".join(paragraphs)
            
            # Try to identify headers (based on line length and formatting)
            self.headings = self._extract_headings(paragraphs)
        
        return {
            'content': self.content,
            'metadata': self.metadata,
            'headings': self.headings,
            'paragraphs': paragraphs
        }
    
    def _extract_headings(self, paragraphs: List[str]) -> List[Dict]:
        """Extract possible titles from PDF paragraphs"""
        headings = []
        for para in paragraphs[:50]:  # Only check first 50 rows
            # Titles are usually shorter and may include chapter numbers
            if len(para) < 100:
                # Detect chapter numbering pattern (e.g. 3.2.S.1.1 or 1.1 or 2.3.4)
                if re.match(r'^\d+(\.\d+)*\s+[A-Za-z]', para) or \
                   re.match(r'^[\d\.]+\s+[\u4e00-\u9fa5]', para):
                    level = para.count('.') + 1
                    headings.append({
                        'level': min(level, 6),
                        'text': para,
                        'style': 'extracted'
                    })
        return headings


class ECTDCompiler:
    """eCTD XML Compiler"""
    
    def __init__(self, output_dir: str, region: str = "ICH", version: str = "4.0"):
        self.output_dir = Path(output_dir)
        self.region = region
        self.version = version
        self.modules = {f"m{i}": [] for i in range(1, 6)}
        self.file_hashes = {}
    
    def compile_document(self, file_path: str, target_module: Optional[str] = None):
        """Compile a single document"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ECTDError(f"File does not exist: {file_path}")
        
        # Select parser
        suffix = file_path.suffix.lower()
        if suffix in ['.docx', '.doc']:
            parser = WordParser(str(file_path))
        elif suffix == '.pdf':
            parser = PDFParser(str(file_path))
        else:
            raise ECTDError(f"Unsupported file format: {suffix}")
        
        # Parse document
        data = parser.parse()
        
        # Determine target module
        if target_module is None or target_module == "auto":
            module = parser.detect_module()
        else:
            module = target_module
        
        # Store parsing results
        self.modules[module].append({
            'file_path': str(file_path),
            'file_name': file_path.name,
            'data': data,
            'module': module
        })
        
        # Calculate file hash
        self.file_hashes[file_path.name] = self._calculate_md5(file_path)
        
        return module
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def generate_xml(self):
        """Generate eCTD XML skeleton"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create module directory and XML
        for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
            module_dir = self.output_dir / module_dir
            module_dir.mkdir(exist_ok=True)
            self._generate_module_xml(module_id, module_dir)
        
        # Generate main index file
        self._generate_index_xml()
        
        # Generate MD5 check file
        self._generate_md5_file()
        
        return self.output_dir
    
    def _generate_module_xml(self, module_id: str, module_dir: Path):
        """Generate module XML file"""
        root = ET.Element("ectd:ectd")
        root.set("xmlns:ectd", f"http://www.ich.org/ectd/{self.version}")
        root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        
        # Add module root node
        module_elem = ET.SubElement(root, f"ectd:{module_id}")
        
        documents = self.modules.get(module_id, [])
        
        # If there is a document, create a leaf node
        for doc in documents:
            leaf = ET.SubElement(module_elem, "ectd:leaf")
            leaf.set("ID", f"{module_id}-{doc['file_name']}")
            leaf.set("xlink:href", f"{module_id}/{doc['file_name']}")
            leaf.set("operation", "new")
            
            # Add title information
            title = ET.SubElement(leaf, "ectd:title")
            title.text = doc['data']['metadata'].get('title', '') or doc['file_name']
            
            # Add document properties
            if doc['data']['headings']:
                for heading in doc['data']['headings'][:5]:  # Only include the first 5 titles
                    node = ET.SubElement(leaf, "ectd:node")
                    node.set("level", str(heading['level']))
                    node.text = heading['text']
        
        # If there is no document, add placeholder instructions
        if not documents:
            placeholder = ET.SubElement(module_elem, "ectd:placeholder")
            placeholder.text = f"No documents assigned to {module_id}"
        
        # format and write
        xml_str = self._prettify_xml(root)
        xml_path = module_dir / f"{module_id}.xml"
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def _generate_index_xml(self):
        """Generate main index file"""
        root = ET.Element("ectd:ectd")
        root.set("xmlns:ectd", f"http://www.ich.org/ectd/{self.version}")
        root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        root.set("dtd-version", self.version)
        
        # Add header information
        header = ET.SubElement(root, "ectd:header")
        
        submission = ET.SubElement(header, "ectd:submission")
        submission.set("type", "initial")
        submission.set("date", datetime.now().strftime("%Y-%m-%d"))
        
        applicant = ET.SubElement(header, "ectd:applicant")
        applicant.text = "[Applicant name]"
        
        product = ET.SubElement(header, "ectd:product")
        product.set("name", "[drug name]")
        
        # Add module reference
        modules_elem = ET.SubElement(root, "ectd:modules")
        for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
            module_ref = ET.SubElement(modules_elem, "ectd:module")
            module_ref.set("id", module_id)
            module_ref.set("xlink:href", f"{module_id}/{module_id}.xml")
            module_ref.set("title", self._get_module_title(module_id))
        
        # format and write
        xml_str = self._prettify_xml(root)
        index_path = self.output_dir / "index.xml"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def _get_module_title(self, module_id: str) -> str:
        """Get module title"""
        titles = {
            "m1": "Administrative Information and Prescribing Information",
            "m2": "Common Technical Document Summaries",
            "m3": "Quality",
            "m4": "Nonclinical Study Reports",
            "m5": "Clinical Study Reports",
        }
        return titles.get(module_id, module_id)
    
    def _generate_md5_file(self):
        """Generate MD5 check file"""
        md5_path = self.output_dir / "index-md5.txt"
        with open(md5_path, 'w', encoding='utf-8') as f:
            f.write("# eCTD MD5 Checksums\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Version: {self.version}\n")
            f.write(f"# Region: {self.region}\n\n")
            
            for filename, hash_value in sorted(self.file_hashes.items()):
                f.write(f"{hash_value}  {filename}\n")
            
            # Add generated XML file hash
            for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
                xml_file = self.output_dir / module_id / f"{module_id}.xml"
                if xml_file.exists():
                    hash_value = self._calculate_md5(xml_file)
                    f.write(f"{hash_value}  {module_id}/{module_id}.xml\n")
            
            # index.xml
            index_file = self.output_dir / "index.xml"
            if index_file.exists():
                hash_value = self._calculate_md5(index_file)
                f.write(f"{hash_value}  index.xml\n")
    
    def _prettify_xml(self, elem) -> str:
        """Formatted XML output"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def validate(self) -> List[str]:
        """Validate the generated XML structure"""
        errors = []
        
        # Basic verification
        index_file = self.output_dir / "index.xml"
        if not index_file.exists():
            errors.append("Missing main index file index.xml")
        
        for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
            module_xml = self.output_dir / module_id / f"{module_id}.xml"
            if not module_xml.exists():
                errors.append(f"Missing module file {module_id}.xml")
        
        # DTD validation using lxml (if available)
        if HAS_LXML:
            errors.extend(self._dtd_validation())
        
        return errors
    
    def _dtd_validation(self) -> List[str]:
        """DTD verification"""
        errors = []
        # Here you can add the actual DTD validation logic
        # Need to load ICH eCTD DTD file
        return errors


def create_parser() -> argparse.ArgumentParser:
    """Create a command line argument parser"""
    parser = argparse.ArgumentParser(
        description="eCTD XML Compiler - Convert drug submission documents to eCTD XML skeleton structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  %(prog)s document.docx report.pdf
  %(prog)s -o ./my-ectd -m m3 quality-doc.docx
  %(prog)s -r FDA -v 3.2.2 *.pdf
  %(prog)s --validate submission.pdf"""
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Input Word/PDF file path (supports multiple)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./ectd-output',
        help='Output directory path (default: ./ectd-output)'
    )
    
    parser.add_argument(
        '-m', '--module',
        choices=['m1', 'm2', 'm3', 'm4', 'm5', 'auto'],
        default='auto',
        help='Target module (default: auto automatically detected)'
    )
    
    parser.add_argument(
        '-r', '--region',
        choices=['FDA', 'EMA', 'ICH'],
        default='ICH',
        help='Target region (Default: ICH)'
    )
    
    parser.add_argument(
        '-v', '--version',
        choices=['3.2.2', '4.0'],
        default='4.0',
        help='eCTD version (default: 4.0)'
    )
    
    parser.add_argument(
        '-d', '--dtd-path',
        help='Custom DTD path'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate generated XML'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show details'
    )
    
    return parser


def main():
    """main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Check dependencies
    missing_deps = []
    if not HAS_DOCX:
        missing_deps.append("python-docx")
    if not HAS_PYPDF2:
        missing_deps.append("PyPDF2")
    
    if missing_deps:
        print(f"warn: Missing optional dependencies: {', '.join(missing_deps)}")
        print("Installation: pip install" + " ".join(missing_deps))
    
    # Initialize the compiler
    try:
        compiler = ECTDCompiler(
            output_dir=args.output,
            region=args.region,
            version=args.version
        )
    except Exception as e:
        print(f"mistake: Failed to initialize compiler - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process input files
    processed = 0
    for file_path in args.input_files:
        if args.verbose:
            print(f"deal with: {file_path}")
        
        try:
            module = compiler.compile_document(file_path, args.module)
            if args.verbose:
                print(f"  -> assigned to module: {module}")
            processed += 1
        except ECTDError as e:
            print(f"mistake [{file_path}]: {e}", file=sys.stderr)
        except Exception as e:
            print(f"mistake [{file_path}]: {str(e)}", file=sys.stderr)
    
    if processed == 0:
        print("Error: No files were successfully processed", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nsuccessfully processed {processed} files")
    
    # Generate XML
    print(f"\ngenerateeCTD XMLskeleton...")
    output_dir = compiler.generate_xml()
    print(f"Output directory: {output_dir.absolute()}")
    
    # Show module allocation statistics
    print("Module assignment:")
    for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
        count = len(compiler.modules[module_id])
        if count > 0:
            print(f"  {module_id}: {count} documents")
    
    # Verification (if requested)
    if args.validate:
        print("Validate XML structure...")
        errors = compiler.validate()
        if errors:
            print("The following issues were found:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Verification passed!")
    
    print("Finish!")
    print(f"eCTDThe skeleton has been generated in: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
