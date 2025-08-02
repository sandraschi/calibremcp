"""DXT build script for Calibre MCP.

This script handles the packaging of Calibre MCP into a DXT package.
"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any

# Package information
PACKAGE_NAME = "calibremcp"
VERSION = "0.1.0"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)

def validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Validate the DXT manifest file."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ["name", "version", "display_name", "description", "server"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Missing required field in manifest: {field}")
        
        # Ensure server configuration is valid
        server = manifest.get("server", {})
        if "command" not in server or not isinstance(server["command"], list):
            raise ValueError("Invalid or missing 'command' in server configuration")
        
        # Validate prompts
        if "prompts" not in manifest:
            raise ValueError("Missing 'prompts' section in manifest")
            
        for prompt in manifest["prompts"]:
            if not all(key in prompt for key in ["name", "description", "template"]):
                raise ValueError("Prompt is missing required fields (name, description, or template)")
        
        return manifest
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}")

def copy_required_files(temp_dir: Path):
    """Copy required files to the temporary directory."""
    # Create necessary directories
    (temp_dir / PACKAGE_NAME).mkdir(exist_ok=True, parents=True)
    
    # Copy Python package files
    src_dir = Path("src") / PACKAGE_NAME
    if not src_dir.exists():
        src_dir = Path("server")  # Fallback to server directory if src doesn't exist
    
    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")
    
    # Copy all Python files from source directory
    for py_file in src_dir.glob("**/*.py"):
        rel_path = py_file.relative_to(src_dir.parent)
        target_path = temp_dir / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(py_file, target_path)
    
    # Copy the manifest
    shutil.copy2("dxt_manifest.json", temp_dir)
    
    # Copy config directory if it exists
    config_src = Path("config")
    if config_src.exists():
        shutil.copytree(config_src, temp_dir / "config", dirs_exist_ok=True)
    
    # Copy any additional required files
    for extra_file in ["README.md", ".env.example", "pyproject.toml", "requirements.txt"]:
        if Path(extra_file).exists():
            shutil.copy2(extra_file, temp_dir)
    
    # Create __init__.py in package directory if it doesn't exist
    init_file = temp_dir / PACKAGE_NAME / "__init__.py"
    if not init_file.exists():
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.write_text("# Calibre MCP package\n")

def create_dxt_package():
    """Create the DXT package."""
    # Validate the manifest first
    manifest = validate_manifest(Path("dxt_manifest.json"))
    version = manifest.get("version", VERSION)
    
    # Create temporary directory for packaging
    temp_dir = DIST_DIR / f"{PACKAGE_NAME}-{version}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    try:
        # Copy required files
        copy_required_files(temp_dir)
        
        # Create the zip archive
        output_file = DIST_DIR / f"{PACKAGE_NAME}-{version}.dxt"
        if output_file.exists():
            output_file.unlink()
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Successfully created DXT package: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error creating DXT package: {e}", file=sys.stderr)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    if create_dxt_package():
        sys.exit(0)
    else:
        sys.exit(1)
