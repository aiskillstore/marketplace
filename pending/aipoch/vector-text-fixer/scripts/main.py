#!/usr/bin/env python3
"""
Vector Text Fixer - Fix garbled text in PDF/SVG vector graphics
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class TextBlock:
    """Text block data structure"""
    id: str
    bbox: List[float]  # [x0, y0, x1, y1]
    original_text: str
    page_num: int = 1
    font_info: Dict[str, Any] = None
    confidence: float = 1.0
    suggested_fix: str = ""
    is_garbled: bool = False


class GarbledTextDetector:
    """Garbled text detector"""
    
    # Common garbled/replacement characters
    REPLACEMENT_CHARS = {
        '\ufffd',  # replacement character
        '\u25a1',  # white square
        '\u25a0',  # black square
        '\u25af',  # white rectangle
        '\u2588',  # full block
        '\ufffe',  # non-character
        '\uffff',  # non-character
        '?',       # question mark substitute
    }
    
    # Common garbled patterns
    GARBLED_PATTERNS = [
        r'[\u0000-\u0008\u000b-\u000c\u000e-\u001f]',  # Control characters
        r'[\ufffd\u25a1\u25a0\u25af\u2588\ufffe\uffff]',  # Replacement characters
        r'[?]{2,}',  # Consecutive replacement characters
        r'(?:\\x[0-9a-fA-F]{2}){2,}',  # Escape sequences
        r'[\x80-\x9f]',  # C1 control characters
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p) for p in self.GARBLED_PATTERNS]
    
    def is_garbled(self, text: str) -> Tuple[bool, float]:
        """
        Detect whether text is garbled
        Returns: (is_garbled, garbled_confidence 0-1)
        """
        if not text or not isinstance(text, str):
            return False, 1.0
        
        text_len = len(text)
        if text_len == 0:
            return False, 1.0
        
        garbled_score = 0.0
        
        # 1. Check replacement characters
        replacement_count = sum(1 for c in text if c in self.REPLACEMENT_CHARS)
        garbled_score += (replacement_count / text_len) * 0.5
        
        # 2. Check garbled patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                garbled_score += len(matches) / text_len * 0.3
        
        # 3. Check abnormal character distribution
        if self._has_abnormal_distribution(text):
            garbled_score += 0.2
        
        # 4. Check for mixed encoding signs
        if self._has_encoding_mixed(text):
            garbled_score += 0.15
        
        is_garbled = garbled_score > 0.15 or replacement_count > 0
        confidence = max(0.0, 1.0 - min(garbled_score, 1.0))
        
        return is_garbled, confidence
    
    def _has_abnormal_distribution(self, text: str) -> bool:
        """Check whether character distribution is abnormal"""
        if len(text) < 3:
            return False
        
        # Count ratio of non-printable characters
        unprintable = sum(1 for c in text if ord(c) < 32 and c not in '\t\n\r')
        ratio = unprintable / len(text)
        return ratio > 0.3
    
    def _has_encoding_mixed(self, text: str) -> bool:
        """Detect whether mixed encoding signs are present"""
        # Detect signs of UTF-8 multi-byte characters being incorrectly parsed
        # e.g.: Ã© should be é (UTF-8 bytes parsed as Latin-1)
        mixed_patterns = [
            r'Ã[\xa0-\xbf]',  # UTF-8 misread as Latin-1
            r'Â[\x80-\xbf]',
            r'Ã¢',
            r'Ã£',
        ]
        for pattern in mixed_patterns:
            if re.search(pattern, text):
                return True
        return False


class PDFFixer:
    """PDF text fixer"""
    
    def __init__(self, detector: GarbledTextDetector):
        self.detector = detector
        self.text_blocks: List[TextBlock] = []
    
    def fix(self, input_path: str, output_path: str, 
            repair_level: str = "standard") -> Dict[str, Any]:
        """
        Fix garbled text in a PDF file
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return {
                "success": False,
                "error": "PyMuPDF (fitz) is required. Install: pip install PyMuPDF"
            }
        
        try:
            doc = fitz.open(input_path)
        except Exception as e:
            return {"success": False, "error": f"Cannot open PDF: {str(e)}"}
        
        self.text_blocks = []
        repair_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = self._extract_text_blocks(page, page_num + 1)
            
            for block in blocks:
                is_garbled, confidence = self.detector.is_garbled(block.original_text)
                
                if is_garbled:
                    block.is_garbled = True
                    block.confidence = confidence
                    block.suggested_fix = self._suggest_fix(
                        block.original_text, 
                        repair_level
                    )
                    repair_count += 1
                
                self.text_blocks.append(block)
        
        # Generate repair report
        result = {
            "success": True,
            "file_type": "pdf",
            "pages": len(doc),
            "total_blocks": len(self.text_blocks),
            "garbled_blocks": repair_count,
            "text_blocks": [asdict(b) for b in self.text_blocks],
            "output_path": output_path
        }
        
        doc.close()
        return result
    
    def _extract_text_blocks(self, page, page_num: int) -> List[TextBlock]:
        """Extract text blocks from a PDF page"""
        blocks = []
        
        try:
            import fitz
            
            # Get text blocks on the page
            text_dict = page.get_text("dict")
            
            block_id = 0
            for block in text_dict.get("blocks", []):
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if text.strip():
                                bbox = span.get("bbox", [0, 0, 0, 0])
                                font_info = {
                                    "font": span.get("font", "Unknown"),
                                    "size": span.get("size", 0),
                                    "flags": span.get("flags", 0),
                                    "color": span.get("color", 0)
                                }
                                
                                tb = TextBlock(
                                    id=f"p{page_num}_b{block_id}",
                                    bbox=list(bbox),
                                    original_text=text,
                                    page_num=page_num,
                                    font_info=font_info
                                )
                                blocks.append(tb)
                                block_id += 1
        except Exception as e:
            print(f"Warning: Error extracting text: {e}")
        
        return blocks
    
    def _suggest_fix(self, garbled_text: str, repair_level: str) -> str:
        """Suggest repair text based on garbled content"""
        # More complex repair logic can be implemented here
        # Currently returns a placeholder prompting the user to input manually
        
        if repair_level == "minimal":
            # Minimal repair: only remove replacement characters
            return garbled_text.replace('\ufffd', '').strip()
        
        elif repair_level == "aggressive":
            # Deep repair: attempt to decode common encoding errors
            return self._try_decode_fixes(garbled_text)
        
        else:  # standard
            # Standard repair: mark for user confirmation
            if all(c in GarbledTextDetector.REPLACEMENT_CHARS for c in garbled_text):
                return f"[Manual input required - original: {len(garbled_text)} garbled characters]"
            else:
                return garbled_text.replace('\ufffd', '[?]').strip()
    
    def _try_decode_fixes(self, text: str) -> str:
        """Attempt multiple encoding repairs"""
        # Common encoding error pattern fixes
        fixes = []
        
        # UTF-8 parsed as Latin-1
        try:
            fixed = text.encode('latin-1').decode('utf-8')
            fixes.append(fixed)
        except:
            pass
        
        # GBK/GB2312 issue
        try:
            fixed = text.encode('latin-1').decode('gbk', errors='ignore')
            fixes.append(fixed)
        except:
            pass
        
        # Return the first reasonable fix
        for fix in fixes:
            if not self.detector.is_garbled(fix)[0]:
                return fix
        
        return f"[Manual input required]"


class SVGFixer:
    """SVG text fixer"""
    
    def __init__(self, detector: GarbledTextDetector):
        self.detector = detector
        self.text_elements: List[TextBlock] = []
    
    def fix(self, input_path: str, output_path: str,
            repair_level: str = "standard") -> Dict[str, Any]:
        """
        Fix garbled text in an SVG file
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return {
                "success": False,
                "error": "BeautifulSoup4 is required. Install: pip install beautifulsoup4"
            }
        
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"success": False, "error": f"Cannot read SVG: {str(e)}"}
        
        soup = BeautifulSoup(content, 'xml')
        
        # Extract all text elements
        self.text_elements = []
        repair_count = 0
        
        text_tags = soup.find_all(['text', 'tspan', 'textPath'])
        
        for idx, tag in enumerate(text_tags):
            text_content = tag.get_text()
            if not text_content.strip():
                continue
            
            is_garbled, confidence = self.detector.is_garbled(text_content)
            
            # Get position and font information
            x = tag.get('x', '0')
            y = tag.get('y', '0')
            font_family = tag.get('font-family', 'default')
            font_size = tag.get('font-size', '12')
            
            tb = TextBlock(
                id=f"text_{idx}",
                bbox=[float(x) if x else 0, float(y) if y else 0, 0, 0],
                original_text=text_content,
                font_info={
                    "font_family": font_family,
                    "font_size": font_size
                },
                page_num=1
            )
            
            if is_garbled:
                tb.is_garbled = True
                tb.confidence = confidence
                tb.suggested_fix = self._suggest_fix(text_content, repair_level)
                repair_count += 1
            
            self.text_elements.append(tb)
        
        # Get SVG basic information
        svg_tag = soup.find('svg')
        svg_info = {
            "width": svg_tag.get('width', 'unknown') if svg_tag else 'unknown',
            "height": svg_tag.get('height', 'unknown') if svg_tag else 'unknown',
            "viewBox": svg_tag.get('viewBox', '') if svg_tag else ''
        }
        
        result = {
            "success": True,
            "file_type": "svg",
            "svg_info": svg_info,
            "total_elements": len(self.text_elements),
            "garbled_elements": repair_count,
            "text_elements": [asdict(t) for t in self.text_elements],
            "output_path": output_path
        }
        
        return result
    
    def _suggest_fix(self, garbled_text: str, repair_level: str) -> str:
        """Suggest SVG text repair"""
        if repair_level == "minimal":
            return garbled_text.replace('\ufffd', '').strip()
        elif repair_level == "aggressive":
            return self._try_xml_entity_fix(garbled_text)
        else:
            if '\ufffd' in garbled_text:
                return f"[Manual input required - original: {len(garbled_text)} garbled characters]"
            return garbled_text
    
    def _try_xml_entity_fix(self, text: str) -> str:
        """Attempt to fix XML entity encoding issues"""
        import html
        # Decode HTML entities
        decoded = html.unescape(text)
        if not self.detector.is_garbled(decoded)[0]:
            return decoded
        return f"[Manual input required]"


class VectorTextFixer:
    """Vector text fixer main class"""
    
    def __init__(self):
        self.detector = GarbledTextDetector()
        self.pdf_fixer = PDFFixer(self.detector)
        self.svg_fixer = SVGFixer(self.detector)
    
    def fix_file(self, input_path: str, output_path: str,
                 repair_level: str = "standard") -> Dict[str, Any]:
        """
        Automatically select repair method based on file type
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            return {"success": False, "error": f"File not found: {input_path}"}
        
        suffix = input_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.pdf_fixer.fix(str(input_path), output_path, repair_level)
        elif suffix == '.svg':
            return self.svg_fixer.fix(str(input_path), output_path, repair_level)
        else:
            return {"success": False, "error": f"Unsupported file format: {suffix}"}
    
    def batch_fix(self, input_folder: str, output_folder: str,
                  repair_level: str = "standard") -> List[Dict[str, Any]]:
        """
        Batch repair PDF/SVG files in a folder
        """
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for file_path in input_folder.iterdir():
            if file_path.suffix.lower() in ['.pdf', '.svg']:
                output_path = output_folder / f"fixed_{file_path.name}"
                result = self.fix_file(str(file_path), str(output_path), repair_level)
                results.append(result)
        
        return results
    
    def export_editable_json(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Export editable JSON format for manual repair in AI tools
        """
        result = self.fix_file(input_path, "", repair_level="standard")
        
        if not result.get("success"):
            return result
        
        # Add editable markers
        editable_data = {
            "file_info": {
                "original_path": input_path,
                "exported_at": self._get_timestamp(),
                "tool": "Vector Text Fixer v1.0.0"
            },
            "repair_data": result
        }
        
        # Add user-editable fields
        if result["file_type"] == "pdf":
            for block in editable_data["repair_data"]["text_blocks"]:
                block["user_editable"] = block.get("suggested_fix", "")
        elif result["file_type"] == "svg":
            for elem in editable_data["repair_data"]["text_elements"]:
                elem["user_editable"] = elem.get("suggested_fix", "")
        
        # Save JSON
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(editable_data, f, ensure_ascii=False, indent=2)
            editable_data["export_success"] = True
        except Exception as e:
            editable_data["export_success"] = False
            editable_data["export_error"] = str(e)
        
        return editable_data
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(
        description='Vector Text Fixer - Fix garbled text in PDF/SVG vector graphics'
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', '-i', help='Input file path (PDF or SVG)')
    input_group.add_argument('--batch', '-b', help='Batch process input folder')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output file/folder path')
    parser.add_argument('--export-json', '-j', help='Export editable JSON format')
    
    # Repair options
    parser.add_argument('--repair-level', '-r', 
                       choices=['minimal', 'standard', 'aggressive'],
                       default='standard',
                       help='Repair level (default: standard)')
    parser.add_argument('--interactive', action='store_true',
                       help='Enable interactive repair mode')
    
    args = parser.parse_args()
    
    # Create fixer instance
    fixer = VectorTextFixer()
    
    # Export JSON mode
    if args.export_json:
        if not args.input:
            print("Error: --export-json requires --input to be specified")
            sys.exit(1)
        
        result = fixer.export_editable_json(args.input, args.export_json)
        
        if result.get("export_success"):
            print(f"✓ JSON export successful: {args.export_json}")
            print(f"  File type: {result['repair_data'].get('file_type')}")
            print(f"  Detected text blocks: {result['repair_data'].get('total_blocks') or result['repair_data'].get('total_elements')}")
            print(f"  Garbled text blocks: {result['repair_data'].get('garbled_blocks') or result['repair_data'].get('garbled_elements')}")
        else:
            print(f"✗ Export failed: {result.get('export_error', 'Unknown error')}")
            sys.exit(1)
        return
    
    # Batch processing mode
    if args.batch:
        if not args.output:
            print("Error: Batch processing requires --output to be specified")
            sys.exit(1)
        
        print(f"Starting batch processing: {args.batch}")
        results = fixer.batch_fix(args.batch, args.output, args.repair_level)
        
        success_count = sum(1 for r in results if r.get("success"))
        total_count = len(results)
        
        print(f"\nProcessing complete: {success_count}/{total_count} files succeeded")
        for r in results:
            if r.get("success"):
                garbled = r.get("garbled_blocks") or r.get("garbled_elements", 0)
                print(f"  ✓ {r.get('output_path')} (garbled: {garbled})")
            else:
                print(f"  ✗ {r.get('error', 'Unknown error')}")
        return
    
    # Single file processing mode
    if args.input:
        print(f"Processing file: {args.input}")
        
        result = fixer.fix_file(args.input, args.output or "", args.repair_level)
        
        if result.get("success"):
            print(f"✓ Analysis complete")
            print(f"  File type: {result.get('file_type')}")
            
            if result.get('file_type') == 'pdf':
                print(f"  Pages: {result.get('pages')}")
                print(f"  Text blocks: {result.get('total_blocks')}")
                print(f"  Garbled blocks: {result.get('garbled_blocks')}")
            else:
                print(f"  Text elements: {result.get('total_elements')}")
                print(f"  Garbled elements: {result.get('garbled_elements')}")
            
            # Show garbled text details
            blocks = result.get('text_blocks') or result.get('text_elements', [])
            garbled_blocks = [b for b in blocks if b.get('is_garbled')]
            
            if garbled_blocks:
                print(f"\nDetected garbled text:")
                for i, block in enumerate(garbled_blocks[:5], 1):
                    orig = block.get('original_text', '')[:50]
                    sugg = block.get('suggested_fix', '')[:50]
                    print(f"  {i}. ID: {block.get('id')}")
                    print(f"     Original: {orig}")
                    print(f"     Suggested: {sugg}")
                    print(f"     Confidence: {block.get('confidence', 0):.2f}")
                
                if len(garbled_blocks) > 5:
                    print(f"  ... and {len(garbled_blocks) - 5} more garbled text items")
            
            if args.output:
                print(f"\nOutput path: {args.output}")
                print("Tip: Use --export-json to export editable format for manual repair")
        else:
            print(f"✗ Processing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
