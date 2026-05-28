from drugbank_downloader import download_drugbank
import sys

def download(version='5.1.10'):
    """
    Downloads the DrugBank XML database.
    Authentication is handled by the library (env vars or interactive).
    """
    print(f"Downloading DrugBank version {version}...")
    try:
        path = download_drugbank(version=version)
        print(f"Successfully downloaded to: {path}")
        return path
    except Exception as e:
        print(f"Error downloading DrugBank: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    download()
