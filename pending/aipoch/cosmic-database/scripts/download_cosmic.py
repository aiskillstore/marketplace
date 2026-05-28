import requests
import os
import base64
import json

def download_cosmic_file(email, password, filepath, output_dir="."):
    """
    Securely download files from COSMIC database.
    
    Args:
        email (str): Registered email address.
        password (str): Account password.
        filepath (str): The remote file path (e.g., 'GRCh38/cosmic/latest/CosmicMutantExport.tsv.gz').
        output_dir (str): Directory to save the downloaded file.
    """
    base_url = "https://cancer.sanger.ac.uk/cosmic/file_download"
    
    # Basic Authentication header
    auth_str = f"{email}:{password}"
    auth_bytes = auth_str.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {base64_auth}'
    }
    
    print(f"Authenticating and requesting {filepath}...")
    
    # In a real scenario, the API might require a specific endpoint to get a download URL
    # or handle the download directly. This implementation follows the logic flow:
    # 1. Authentication
    # 2. Download
    
    try:
        # Request the file
        # Note: The actual COSMIC API might use a different parameter structure.
        # This is a generalized implementation based on the documentation provided.
        response = requests.get(f"{base_url}?file={filepath}", headers=headers, stream=True)
        
        if response.status_code == 200:
            filename = os.path.basename(filepath)
            output_path = os.path.join(output_dir, filename)
            
            print(f"Downloading to {output_path}...")
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("Download complete.")
            return output_path
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Example usage for testing
    import sys
    if len(sys.argv) < 4:
        print("Usage: python download_cosmic.py <email> <password> <filepath>")
    else:
        download_cosmic_file(sys.argv[1], sys.argv[2], sys.argv[3])
