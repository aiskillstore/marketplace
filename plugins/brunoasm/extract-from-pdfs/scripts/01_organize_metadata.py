#!/usr/bin/env python3
"""
Organize PDFs and metadata from various sources (BibTeX, RIS, directory, DOI list).
Standardizes file naming and creates a unified metadata JSON for downstream processing.
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import re

try:
    from pybtex.database.input import bibtex
    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False
    print("Warning: pybtex not installed. BibTeX support disabled.")

try:
    import rispy
    RIS_AVAILABLE = True
except ImportError:
    RIS_AVAILABLE = False
    print("Warning: rispy not installed. RIS support disabled.")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Organize PDFs and metadata from various sources'
    )
    parser.add_argument(
        '--source-type',
        choices=['bibtex', 'ris', 'directory', 'doi_list'],
        required=True,
        help='Type of source data'
    )
    parser.add_argument(
        '--source',
        required=True,
        help='Path to source file (BibTeX/RIS file, directory, or DOI list)'
    )
    parser.add_argument(
        '--pdf-dir',
        help='Directory containing PDFs (for bibtex/ris with relative paths)'
    )
    parser.add_argument(
        '--output',
        default='metadata.json',
        help='Output metadata JSON file'
    )
    parser.add_argument(
        '--organize-pdfs',
        action='store_true',
        help='Copy PDFs to standardized directory structure'
    )
    parser.add_argument(
        '--pdf-output-dir',
        default='organized_pdfs',
        help='Directory for organized PDFs'
    )
    return parser.parse_args()


def load_bibtex_metadata(bib_path: Path, pdf_base_dir: Optional[Path] = None) -> List[Dict]:
    """Load metadata from BibTeX file"""
    if not BIBTEX_AVAILABLE:
        raise ImportError("pybtex is required for BibTeX support. Install with: pip install pybtex")

    parser = bibtex.Parser()
    bib_data = parser.parse_file(str(bib_path))

    metadata = []
    for key, entry in bib_data.entries.items():
        record = {
            'id': key,
            'type': entry.type,
            'title': entry.fields.get('title', ''),
            'year': entry.fields.get('year', ''),
            'doi': entry.fields.get('doi', ''),
            'abstract': entry.fields.get('abstract', ''),
            'journal': entry.fields.get('journal', ''),
            'authors': ', '.join(
                [' '.join([p for p in person.last_names + person.first_names])
                 for person in entry.persons.get('author', [])]
            ),
            'keywords': entry.fields.get('keywords', ''),
            'pdf_path': None
        }

        # Extract PDF path from file field
        if 'file' in entry.fields:
            file_field = entry.fields['file']
            if file_field.startswith('{') and file_field.endswith('}'):
                file_field = file_field[1:-1]

            for file_entry in file_field.split(';'):
                parts = file_entry.strip().split(':')
                if len(parts) >= 3 and parts[2].lower() == 'application/pdf':
                    pdf_path = parts[1].strip()
                    if pdf_base_dir:
                        pdf_path = str(pdf_base_dir / pdf_path)
                    record['pdf_path'] = pdf_path
                    break

        metadata.append(record)

    print(f"Loaded {len(metadata)} entries from BibTeX file")
    return metadata


def load_ris_metadata(ris_path: Path, pdf_base_dir: Optional[Path] = None) -> List[Dict]:
    """Load metadata from RIS file"""
    if not RIS_AVAILABLE:
        raise ImportError("rispy is required for RIS support. Install with: pip install rispy")

    with open(ris_path, 'r', encoding='utf-8') as f:
        entries = rispy.load(f)

    metadata = []
    for i, entry in enumerate(entries):
        # Generate ID from first author and year or use index
        first_author = entry.get('authors', [None])[0] or 'Unknown'
        year = entry.get('year', 'NoYear')
        entry_id = f"{first_author.split()[-1]}{year}_{i}"

        record = {
            'id': entry_id,
            'type': entry.get('type_of_reference', 'article'),
            'title': entry.get('title', ''),
            'year': str(entry.get('year', '')),
            'doi': entry.get('doi', ''),
            'abstract': entry.get('abstract', ''),
            'journal': entry.get('journal_name', ''),
            'authors': '; '.join(entry.get('authors', [])),
            'keywords': '; '.join(entry.get('keywords', [])),
            'pdf_path': None
        }

        # Try to find PDF in standard locations
        if pdf_base_dir:
            # Common patterns: FirstAuthorYear.pdf, doi_cleaned.pdf, etc.
            pdf_candidates = [
                f"{entry_id}.pdf",
                f"{first_author.split()[-1]}_{year}.pdf"
            ]
            if record['doi']:
                safe_doi = re.sub(r'[^\w\-_]', '_', record['doi'])
                pdf_candidates.append(f"{safe_doi}.pdf")

            for candidate in pdf_candidates:
                pdf_path = pdf_base_dir / candidate
                if pdf_path.exists():
                    record['pdf_path'] = str(pdf_path)
                    break

        metadata.append(record)

    print(f"Loaded {len(metadata)} entries from RIS file")
    return metadata


def load_directory_metadata(dir_path: Path) -> List[Dict]:
    """Load metadata by scanning directory for PDFs"""
    pdf_files = list(dir_path.glob('**/*.pdf'))

    metadata = []
    for pdf_path in pdf_files:
        # Generate ID from filename
        entry_id = pdf_path.stem

        record = {
            'id': entry_id,
            'type': 'article',
            'title': entry_id.replace('_', ' '),
            'year': '',
            'doi': '',
            'abstract': '',
            'journal': '',
            'authors': '',
            'keywords': '',
            'pdf_path': str(pdf_path)
        }

        # Try to extract DOI from filename if present
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', entry_id)
        if doi_match:
            record['doi'] = doi_match.group(0)

        metadata.append(record)

    print(f"Found {len(metadata)} PDFs in directory")
    return metadata


def load_doi_list_metadata(doi_list_path: Path) -> List[Dict]:
    """Load metadata from a list of DOIs (will need to fetch metadata separately)"""
    with open(doi_list_path, 'r') as f:
        dois = [line.strip() for line in f if line.strip()]

    metadata = []
    for doi in dois:
        safe_doi = re.sub(r'[^\w\-_]', '_', doi)
        record = {
            'id': safe_doi,
            'type': 'article',
            'title': '',
            'year': '',
            'doi': doi,
            'abstract': '',
            'journal': '',
            'authors': '',
            'keywords': '',
            'pdf_path': None
        }
        metadata.append(record)

    print(f"Loaded {len(metadata)} DOIs")
    print("Note: You'll need to fetch full metadata and PDFs separately")
    return metadata


def organize_pdfs(metadata: List[Dict], output_dir: Path) -> List[Dict]:
    """Copy and rename PDFs to standardized directory structure"""
    output_dir.mkdir(parents=True, exist_ok=True)

    organized_metadata = []
    stats = {'copied': 0, 'missing': 0, 'total': len(metadata)}

    for record in metadata:
        if record['pdf_path'] and Path(record['pdf_path']).exists():
            source_path = Path(record['pdf_path'])
            dest_path = output_dir / f"{record['id']}.pdf"

            try:
                shutil.copy2(source_path, dest_path)
                record['pdf_path'] = str(dest_path)
                stats['copied'] += 1
            except Exception as e:
                print(f"Error copying {source_path}: {e}")
                stats['missing'] += 1
        else:
            if record['pdf_path']:
                print(f"PDF not found: {record['pdf_path']}")
            stats['missing'] += 1

        organized_metadata.append(record)

    print(f"\nPDF Organization Summary:")
    print(f"  Total entries: {stats['total']}")
    print(f"  PDFs copied: {stats['copied']}")
    print(f"  PDFs missing: {stats['missing']}")

    return organized_metadata


def save_metadata(metadata: List[Dict], output_path: Path):
    """Save metadata to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {output_path}")


def main():
    args = parse_args()

    source_path = Path(args.source)
    pdf_base_dir = Path(args.pdf_dir) if args.pdf_dir else None
    output_path = Path(args.output)

    # Load metadata based on source type
    if args.source_type == 'bibtex':
        metadata = load_bibtex_metadata(source_path, pdf_base_dir)
    elif args.source_type == 'ris':
        metadata = load_ris_metadata(source_path, pdf_base_dir)
    elif args.source_type == 'directory':
        metadata = load_directory_metadata(source_path)
    elif args.source_type == 'doi_list':
        metadata = load_doi_list_metadata(source_path)
    else:
        raise ValueError(f"Unknown source type: {args.source_type}")

    # Organize PDFs if requested
    if args.organize_pdfs:
        pdf_output_dir = Path(args.pdf_output_dir)
        metadata = organize_pdfs(metadata, pdf_output_dir)

    # Save metadata
    save_metadata(metadata, output_path)

    # Print summary statistics
    total = len(metadata)
    with_pdfs = sum(1 for r in metadata if r['pdf_path'])
    with_abstracts = sum(1 for r in metadata if r['abstract'])
    with_dois = sum(1 for r in metadata if r['doi'])

    print(f"\nMetadata Summary:")
    print(f"  Total entries: {total}")
    print(f"  With PDFs: {with_pdfs}")
    print(f"  With abstracts: {with_abstracts}")
    print(f"  With DOIs: {with_dois}")


if __name__ == '__main__':
    main()
