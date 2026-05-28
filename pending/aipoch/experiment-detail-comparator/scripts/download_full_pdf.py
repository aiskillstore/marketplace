#!/usr/bin/env python3
"""
Download and parse full text from PDF URLs.
Supports multiple languages and various PDF sources.
"""

import sys
import json
import subprocess
import requests
from pathlib import Path
from urllib.parse import urlparse

def check_dependencies():
    """
    Check if required dependencies are installed.
    
    Returns:
        Dictionary of dependency status
    """
    deps = {
        "requests": False,
        "PyPDF2": False,
        "pdfminer": False,
    }
    
    try:
        import requests
        deps["requests"] = True
    except ImportError:
        print("Installing requests...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        deps["requests"] = True
    
    try:
        import PyPDF2
        deps["PyPDF2"] = True
    except ImportError:
        print("Installing PyPDF2...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2"], check=True)
        deps["PyPDF2"] = True
    
    # Try alternative pdfminer
    try:
        import pdfminer
        deps["pdfminer"] = True
    except ImportError:
        pass
    
    return deps

def download_pdf(url, output_path, timeout=30):
    """
    Download PDF from URL with error handling.
    
    Args:
        url: URL to download from
        output_path: Path to save PDF
        timeout: Download timeout in seconds
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Downloading from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,application/octet-stream',
            'Accept-Language': 'en-US,en;q=0.9,*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type:
            print(f"Warning: Content type is {content_type}, not PDF", file=sys.stderr)
        
        # Save file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✓ Downloaded to: {output_path}")
        return True
        
    except requests.exceptions.Timeout:
        print(f"Error: Download timeout after {timeout} seconds", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading: {e}", file=sys.stderr)
        return False

def parse_pdf_fulltext(pdf_path, output_path):
    """
    Extract full text from PDF using PyPDF2.
    
    Args:
        pdf_path: Path to PDF file
        output_path: Path to save extracted text
    
    Returns:
        Dictionary with text extraction results
    """
    try:
        import PyPDF2
    except ImportError:
        print("Error: PyPDF2 is not installed", file=sys.stderr)
        return {}
    
    result = {
        "pdf_path": str(pdf_path),
        "full_text": "",
        "pages": 0,
        "language": "unknown",
        "extraction_method": "PyPDF2",
        "metadata": {},
    }
    
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            # Get metadata
            if pdf_reader.metadata:
                result["metadata"] = pdf_reader.metadata
            
            # Extract text from all pages
            full_text = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        full_text.append(text)
                except Exception as e:
                    print(f"Warning: Error extracting page {page_num}: {e}", file=sys.stderr)
                    full_text.append(f"[Page {page_num} extraction error]")
            
            result["full_text"] = "\n\n".join(full_text)
            result["pages"] = len(pdf_reader.pages)
            
            # Try to detect language
            sample_text = result["full_text"][:1000]
            language = detect_language(sample_text)
            result["language"] = language
    
    except Exception as e:
        print(f"Error parsing PDF: {e}", file=sys.stderr)
        result["error"] = str(e)
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Also save as plain text
    text_path = output_path.with_suffix('.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(result["full_text"])
    
    return result

def detect_language(text):
    """
    Simple language detection based on character sets.
    
    Args:
        text: Sample text to analyze
    
    Returns:
        Language code
    """
    if not text:
        return "unknown"
    
    # Check for Chinese
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    chinese_ratio = chinese_chars / len(text)
    
    # Check for Japanese
    japanese_chars = len([c for c in text if '\u3040' <= c <= '\u309f'])
    japanese_ratio = japanese_chars / len(text)
    
    # Check for Korean
    korean_chars = len([c for c in text if '\uac00' <= c <= '\ud7af'])
    korean_ratio = korean_chars / len(text)
    
    # Check for Cyrillic (Russian, etc.)
    cyrillic_chars = len([c for c in text if '\u0400' <= c <= '\u04ff'])
    cyrillic_ratio = cyrillic_chars / len(text)
    
    # Determine language
    if chinese_ratio > 0.3:
        return "zh-CN" if simplified_chinese_check(text) else "zh-TW"
    elif japanese_ratio > 0.3:
        return "ja-JP"
    elif korean_ratio > 0.3:
        return "ko-KR"
    elif cyrillic_ratio > 0.3:
        return "ru-RU"
    else:
        return "en-US"

def simplified_chinese_check(text):
    """
    Check if text is likely Simplified Chinese.
    
    Args:
        text: Sample text
    
    Returns:
        True if simplified, False if traditional
    """
    # Simplified Chinese specific characters
    simplified_chars = "This is right"
    # Traditional Chinese specific characters
    traditional_chars = "This is right"
    
    s_count = sum(1 for c in simplified_chars if c in text)
    t_count = sum(1 for c in traditional_chars if c in text)
    
    return s_count > t_count

def extract_doi_from_text(text):
    """
    Extract DOI from text.
    
    Args:
        text: Full text
    
    Returns:
        DOI string or None
    """
    import re
    
    doi_patterns = [
        r'DOI:\s*(10\.\d+/\S+)',
        r'doi\.org/\d+\.\d+/\S+',
        r'https://doi\.org/\d+\.\d+/\S+',
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def save_extraction_report(results, report_path):
    """
    Save a comprehensive extraction report.
    
    Args:
        results: List of extraction results
        report_path: Path to save report
    """
    report = {
        "total_papers": len(results),
        "successful": sum(1 for r in results if r.get("success", False)),
        "papers": results
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 3:
        print("Usage: python download_full_pdf.py <url_or_file> <output_dir>")
        print("\nExamples:")
        print("  # Download from URL")
        print("  python download_full_pdf.py https://example.com/paper.pdf ./downloads")
        print("\n  # Parse existing PDF")
        print("  python download_full_pdf.py ./local/paper.pdf ./parsed")
        sys.exit(1)
    
    # Check and install dependencies
    deps = check_dependencies()
    if not all(deps.values()):
        print("Warning: Some dependencies could not be installed", file=sys.stderr)
    
    input_arg = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Check if input is URL or file path
    input_str = str(input_arg)
    if input_str.startswith(('http://', 'https://', 'ftp://')):
        # Download from URL
        pdf_filename = Path(urlparse(input_str).path).name
        if not pdf_filename.endswith('.pdf'):
            pdf_filename = 'downloaded_paper.pdf'
        output_path = output_dir / pdf_filename
        
        print(f"Mode: Download from URL")
        print(f"URL: {input_str}")
        
        success = download_pdf(input_str, output_path)
        
        if success:
            # Parse the downloaded PDF
            text_output = output_dir / f"{pdf_filename}_parsed.json"
            text_file = output_dir / f"{pdf_filename}_text.txt"
            parse_result = parse_pdf_fulltext(output_path, text_output)
            
            result = {
                "pdf_url": input_str,
                "pdf_path": str(output_path),
                "text_path": str(text_file),
                "json_path": str(text_output),
                "success": True,
                **parse_result,
            }
            results.append(result)
        else:
            results.append({
                "pdf_url": input_str,
                "success": False,
                "error": "Download failed",
            })
    
    else:
        # Parse existing PDF file
        if not input_arg.exists():
            print(f"Error: File not found: {input_arg}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Mode: Parse existing PDF")
        print(f"Input file: {input_arg}")
        
        text_output = output_dir / f"{input_arg.stem}_parsed.json"
        text_file = output_dir / f"{input_arg.stem}_text.txt"
        parse_result = parse_pdf_fulltext(input_arg, text_output)
        
        result = {
            "pdf_path": str(input_arg),
            "text_path": str(text_file),
            "json_path": str(text_output),
            "success": True,
            **parse_result,
        }
        results.append(result)
    
    # Save report
    report_path = output_dir / "download_report.json"
    save_extraction_report(results, report_path)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Download/Parse Summary")
    print(f"{'='*60}")
    print(f"Total papers processed: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r.get('success', False))}")
    print(f"Failed: {sum(1 for r in results if not r.get('success', False))}")
    print(f"\nReport saved to: {report_path}")
    print(f"{'='*60}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
