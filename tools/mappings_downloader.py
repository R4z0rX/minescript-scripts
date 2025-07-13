"""
    Mappings Downloader for Minescript v5
    Version: 0.1
    Author: RazrCraft
    Date: 2025-07-03

    Simple tool to automatically download Mojang and Fabric (Intermediary) 
    mappings directly to the folder where Minescript needs them.

    Usage:
    Place this script in the Minescript folder and simply run it from Minecraft chat
    as any Minescript command, and it will automatically detect the required version.
    Or, you can run it from the console/terminal, but you must specify the version 
    as a parameter. E.g.: python mappings_downloader.py -v 1.21.7
    If the parameter is not passed, the script will prompt you to enter the version.
"""
import os
import sys
import json
import urllib.request
from pathlib import Path


mc_version = ""
mappings_dir = Path("minescript/mappings")
version_manifest_file: str = "version_manifest_v2.json"

# Loaded data
version_manifest_data = None
version_json_file = None
version_data = None
mojang_mappings = None

def detect_environment():
    """Detects the Minecraft version using Minescript if available"""
    global mc_version
    
    try:
        import minescript # pylint: disable=import-outside-toplevel
        environment = "MC"
        mc_version = minescript.version_info().minecraft
        print(f"Minecraft {mc_version} detected")
        
    except (ImportError, AttributeError):
        environment = "CLI"

    return environment

def download_file(url: str, filepath: Path) -> bool:
    """Downloads a file from a URL"""
    try:
        print(f"Downloading: {url}")
        urllib.request.urlretrieve(url, filepath)
        return True
    except Exception as e: # pylint: disable=W0718
        print(f"Error downloading {url}: {e}")
        return False

def load_version_manifest() -> bool:
    """Loads or downloads the version manifest"""
    global version_manifest_data
    
    url: str = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    if not download_file(url, version_manifest_file):
        return False
    
    try:
        with open(version_manifest_file, "r", encoding="utf-8") as f:
            version_manifest_data = json.load(f)
        os.remove(version_manifest_file)
        return True
    except Exception as e: # pylint: disable=W0718
        print(f"Error loading version manifest: {e}")
        return False

def download_mojang_mappings(version: str) -> bool:
    """Downloads the data for a specific version"""
    global version_json_file
    global version_data
    global mojang_mappings

    mojang_mappings_file = mappings_dir / f"{version}/client.txt"
        
    if mojang_mappings_file.exists():
        print(f"{mojang_mappings_file} already exist")
        return True
    
    if not load_version_manifest():
        print("Error downloading version manifest.")
        sys.exit(1)

    if not version_manifest_data:
        print("Error loading version data. Can't find version manifest.")
        return False
    
    # Find the version in the manifest
    version_info = None
    for v in version_manifest_data.get("versions", []): # type: ignore
        if v.get("id") == version:
            version_info = v
            break
    
    if not version_info:
        print(f"Version {version} not found in the manifest")
        return False
    
    # Download the version JSON file
    version_url = version_info.get("url")
    version_json_file = Path(f"{version}.json")
    
    if not version_json_file.exists():
        if not download_file(version_url, version_json_file):
            return False
    
    # Load version data
    try:
        with open(version_json_file, "r", encoding="utf-8") as f:
            version_data = json.load(f)
        os.remove(version_json_file)
    except Exception as e: # pylint: disable=W0718
        print(f"Error loading version data: {e}")
        return False
    
    # Download Mojang mappings
    downloads = version_data.get("downloads", {})
    mojang_mappings = downloads.get("client_mappings")

    if mojang_mappings:
        mappings_url = mojang_mappings.get("url")
        version_dir = Path(mappings_dir / version)
        version_dir.mkdir(exist_ok=True)
        mojang_mappings_file = mappings_dir / f"{version}/client.txt"
        
        if not mojang_mappings_file.exists():
            if not download_file(mappings_url, mojang_mappings_file):
                return False
            return True
    
    return False
    
def download_intermediay_mappings(version: str) -> bool:
    # Download Fabric (Intermediary) mappings
    intermediary_url = f"https://raw.githubusercontent.com/FabricMC/intermediary/master/mappings/{version}.tiny"
    intermediary_file = mappings_dir / f"{version}/{version}.tiny"
    
    if not intermediary_file.exists():
        if not download_file(intermediary_url, intermediary_file):
            return False
    else:
        print(f"{intermediary_file} already exist")
    
    return True


def main():
    global mc_version
    global mappings_dir
    
    if detect_environment() == "CLI":
        if len(sys.argv) == 3 and (sys.argv[1] == "-v" or sys.argv[1] == "--version"):
            mc_version = sys.argv[2]
        else:
            mc_version = input("Enter the Minecraft version (e.g. 1.21.7): ")
            if mc_version == "":
                print("Usage: python mappings_downloader.py -v <version>")
                print("E.g.: python mappings_downloader.py -v 1.21.7")
                sys.exit(0)
        mappings_dir = Path("mappings")
    else:
        mappings_dir = Path("minescript/mappings")
    
    mappings_dir.mkdir(exist_ok=True)
    
    if mc_version == "":
        print("Error: Version not given.")
        sys.exit(1)
        
    print("Searching and downloading mapping data...")
    
    if not download_mojang_mappings(mc_version):
        print("Error downloading Mojang mappings.")
        sys.exit(1)
    
    if not download_intermediay_mappings(mc_version):
        print("Error downloading Fabric (Intermadiary) mappings.")
        sys.exit(1)

    print(f"Mojang and Fabric (Intermediary) mappings downloaded successfully to the /{mappings_dir} folder.")


if __name__ == "__main__":
    main()
