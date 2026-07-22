#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import urllib.request
import json
import shutil

def run_command(args):
    """Run a system command and return exit code and output."""
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def install_via_npm():
    """Attempt to install @rollinggo/hotel-global via npm."""
    print("Checking npm environment...")
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    
    # Try global installation
    print("Attempting to install @rollinggo/hotel-global globally via npm...")
    code, stdout, stderr = run_command([npm_cmd, "install", "-g", "@rollinggo/hotel-global@latest"])
    if code == 0:
        print("✅ Successfully installed @rollinggo/hotel-global globally via npm!")
        return True
    
    print("⚠️ npm global installation failed (might need administrator/sudo permissions).")
    print(stderr)
    return False

def download_binary(url, dest_path):
    """Download a file from url to dest_path with progress indication."""
    print(f"Downloading binary from: {url}")
    print(f"Saving to: {dest_path}")
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'RollingGo-Installer/1.0'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            with open(dest_path, 'wb') as out_file:
                shutil_copy(response, out_file)
        print("✅ Download completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def shutil_copy(response, out_file):
    """Helper to copy response to file."""
    block_size = 1024 * 8
    while True:
        buffer = response.read(block_size)
        if not buffer:
            break
        out_file.write(buffer)

def get_latest_release_assets():
    """Query GitHub API for the latest release assets."""
    api_url = "https://api.github.com/repos/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest"
    req = urllib.request.Request(
        api_url,
        headers={'User-Agent': 'RollingGo-Installer/1.0'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('assets', []), data.get('tag_name', 'latest')
    except Exception as e:
        print(f"⚠️ Could not fetch latest release info from GitHub API: {e}")
        return None, None

def main():
    print("==================================================")
    print("      RollingGo Hotel CLI - Install Script        ")
    print("==================================================")
    
    # 1. Try npm first
    # Check if node and npm are available
    has_node = False
    try:
        node_code = subprocess.call(["node", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        npm_code = subprocess.call(["npm" if platform.system() != "Windows" else "npm.cmd", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        has_node = (node_code == 0 and npm_code == 0)
    except Exception:
        has_node = False
        
    if has_node:
        if install_via_npm():
            print("Done! You can run 'rgg' from anywhere.")
            return 0
    else:
        print("Node.js/npm not found. Proceeding with standalone binary installation...")

    # 2. Standalone Binary Fallback
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print(f"Detected System: {platform.system()} ({platform.machine()})")
    
    # Map OS to file name patterns
    asset_keyword = ""
    bin_name = "rgg"
    
    if system == "windows":
        asset_keyword = "win"
        bin_name = "rgg.exe"
    elif system == "darwin":
        asset_keyword = "macos"
    elif system == "linux":
        asset_keyword = "linux"
    else:
        print(f"❌ Unsupported system type: {system}. Please download manually.")
        return 1
        
    # Get local bin directory (self-contained inside skill)
    # Target path: skills/rollinggo-hotel-booking/bin/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    bin_dir = os.path.join(skill_dir, "bin")
    
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
        
    dest_path = os.path.join(bin_dir, bin_name)
    
    # Try fetching from GitHub API
    assets, tag = get_latest_release_assets()
    download_url = None
    
    if assets:
        for asset in assets:
            name = asset.get('name', '').lower()
            # Match keywords (e.g. 'win' or 'windows' for Windows, 'macos' for Mac, 'linux' for Linux)
            if asset_keyword in name:
                download_url = asset.get('browser_download_url')
                print(f"Found matching asset for version {tag}: {asset.get('name')}")
                break
                
    # Fallback to hardcoded URL patterns if API fails or asset not found
    if not download_url:
        print("Using hardcoded fallback download URL...")
        if system == "windows":
            download_url = "https://github.com/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest/download/rgg-win.exe"
        elif system == "darwin":
            download_url = "https://github.com/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest/download/rgg-macos"
        else:
            download_url = "https://github.com/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest/download/rgg-linux"
            
    success = download_binary(download_url, dest_path)
    
    if not success and assets and system == "windows":
        # Extra fallback for windows naming differences (win vs windows)
        print("Retrying with alternative Windows asset name...")
        download_url = "https://github.com/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest/download/rgg-windows.exe"
        success = download_binary(download_url, dest_path)
        
    if success:
        # Chmod on Linux/macOS
        if system != "windows":
            try:
                os.chmod(dest_path, 0o755)
                print("Permissions set to executable.")
            except Exception as e:
                print(f"⚠️ Warning: Failed to set executable permissions: {e}")
                print(f"You may need to run: chmod +x {dest_path}")
                
        print("\n==================================================")
        print("🎉 Standalone binary installed successfully!")
        print(f"Location: {dest_path}")
        print("==================================================")
        print("To run the CLI, use the absolute path or add the bin directory to your PATH:")
        print(f"  {dest_path} --help")
        print("\nNote: The Agent skill is configured to locate rgg at this path automatically.")
        return 0
    else:
        print("\n❌ Installation failed. Please check your internet connection or install manually from:")
        print("https://github.com/RollingGo-AI/oauth-hotel-cli-overseas/releases/latest")
        return 1

if __name__ == "__main__":
    sys.exit(main())
