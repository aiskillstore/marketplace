#!/usr/bin/env python3
"""
Get PDF file from Zotero library - tries local first, then downloads from web if needed.

This script first attempts to locate the PDF in local Zotero storage.
If not found locally, it downloads from the Zotero web library using the API.
"""

import sys
import os
import subprocess
from pathlib import Path

def find_local_pdf(attachment_key):
    """
    Try to find PDF in local Zotero storage.

    Args:
        attachment_key: The attachment item key

    Returns:
        Path to PDF if found, None otherwise
    """
    zotero_storage = Path.home() / "Zotero" / "storage"

    if not zotero_storage.exists():
        return None

    storage_folder = zotero_storage / attachment_key

    if not storage_folder.exists():
        return None

    pdf_files = list(storage_folder.glob("*.pdf"))

    if pdf_files:
        return str(pdf_files[0])

    return None

def get_api_key():
    """
    Read Zotero API key from the .env file.

    Returns:
        API key string, or None if not found
    """
    env_file = Path("Notes/.env")

    if not env_file.exists():
        print(f"Error: .env file not found at {env_file}", file=sys.stderr)
        return None

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("ZOTERO_API_KEY="):
                return line.split("=", 1)[1]

    print("Error: ZOTERO_API_KEY not found in .env file", file=sys.stderr)
    return None

def get_library_config():
    """
    Read library configuration from .env file.

    Returns:
        Tuple of (library_type, library_id) or (None, None) if not found
    """
    env_file = Path("Notes/.env")

    if not env_file.exists():
        print(f"Error: .env file not found at {env_file}", file=sys.stderr)
        return None, None

    library_type = "user"  # default
    library_id = None

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("ZOTERO_LIBRARY_TYPE="):
                library_type = line.split("=", 1)[1]
            elif line.startswith("ZOTERO_LIBRARY_ID="):
                library_id = line.split("=", 1)[1]

    if not library_id:
        print("Error: ZOTERO_LIBRARY_ID not found in .env file", file=sys.stderr)
        return None, None

    return library_type, library_id

def get_original_filename(attachment_key):
    """
    Get the original filename from Zotero API.

    Args:
        attachment_key: The attachment item key

    Returns:
        Original filename or None if not found
    """
    api_key = get_api_key()
    if not api_key:
        return None

    library_type, library_id = get_library_config()
    if not library_id:
        return None

    # Construct API URL for item metadata
    if library_type == "group":
        api_url = f"https://api.zotero.org/groups/{library_id}/items/{attachment_key}"
    else:
        api_url = f"https://api.zotero.org/users/{library_id}/items/{attachment_key}"

    # Get metadata with curl
    cmd = [
        "curl", "-s",
        "-H", f"Zotero-API-Key: {api_key}",
        "-H", "Zotero-API-Version: 3",
        api_url
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        filename = data.get("data", {}).get("filename")
        return filename
    except:
        return None

def download_pdf(attachment_key):
    """
    Download PDF from Zotero web library.

    Args:
        attachment_key: The attachment item key

    Returns:
        Path to downloaded file if successful, None otherwise
    """
    api_key = get_api_key()
    if not api_key:
        return None

    library_type, library_id = get_library_config()
    if not library_id:
        return None

    # Get original filename
    original_filename = get_original_filename(attachment_key)
    if not original_filename:
        # Fallback to attachment key if we can't get the filename
        original_filename = f"{attachment_key}.pdf"
        print(f"Warning: Could not get original filename, using {original_filename}", file=sys.stderr)

    output_path = f"/tmp/{original_filename}"

    # Construct API URL
    if library_type == "group":
        api_url = f"https://api.zotero.org/groups/{library_id}/items/{attachment_key}/file"
    else:
        api_url = f"https://api.zotero.org/users/{library_id}/items/{attachment_key}/file"

    # Use curl to download with redirect following
    cmd = [
        "curl", "-L", "-s",
        "-H", f"Zotero-API-Key: {api_key}",
        "-H", "Zotero-API-Version: 3",
        api_url,
        "-o", str(output_path)
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Verify the file was downloaded and is a valid PDF
        # PDFs should be at least 1KB (typical minimum is much larger)
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            if file_size < 1024:
                print(f"Error: Downloaded file is too small ({file_size} bytes), likely an error response", file=sys.stderr)
                return None
            return str(output_path)
        else:
            print(f"Error: Download failed - file not created", file=sys.stderr)
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error downloading PDF: {e}", file=sys.stderr)
        return None

def get_pdf(attachment_key):
    """
    Get PDF file - tries local first, downloads if needed.

    Args:
        attachment_key: The attachment item key

    Returns:
        Path to PDF file (local or downloaded to /tmp)
    """
    # First, try to find locally
    local_path = find_local_pdf(attachment_key)
    if local_path:
        print(f"Found local PDF: {local_path}")
        return local_path

    # If not found locally, download from web
    print("PDF not found locally, downloading from web library...", file=sys.stderr)

    downloaded_path = download_pdf(attachment_key)
    if downloaded_path:
        print(f"Downloaded PDF: {downloaded_path}")
        return downloaded_path
    else:
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_zotero_pdf.py <attachment_key>")
        sys.exit(1)

    attachment_key = sys.argv[1]

    pdf_path = get_pdf(attachment_key)

    if pdf_path:
        print(pdf_path)
        sys.exit(0)
    else:
        print("Error: Could not find or download PDF", file=sys.stderr)
        sys.exit(1)
