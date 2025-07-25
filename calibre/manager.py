"""
Calibre Manager - Core Calibre ebook management
Austrian dev efficiency for ebook library operations
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CalibreManagerError(Exception):
    """Base exception for Calibre manager operations"""
    pass

class CalibreManager:
    """Core Calibre ebook management"""
    
    def __init__(self, library_path: str, calibre_bin: str = "calibredb"):
        self.library_path = Path(library_path)
        self.calibre_bin = calibre_bin
        
        if not self.library_path.exists():
            raise CalibreManagerError(f"Library path does not exist: {library_path}")
    
    def run_command(self, args: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Run calibredb command with error handling"""
        try:
            cmd = [self.calibre_bin] + args + ["--library-path", str(self.library_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            raise CalibreManagerError(f"Command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise CalibreManagerError(f"Calibre command not found: {self.calibre_bin}")
        except Exception as e:
            raise CalibreManagerError(f"Command execution failed: {e}")
    
    def test_connection(self) -> bool:
        """Test Calibre installation and library access"""
        try:
            result = self.run_command(["list", "--limit", "1"])
            return result["success"]
        except Exception:
            return False
    
    def get_library_info(self) -> Dict[str, Any]:
        """Get basic library information"""
        try:
            result = self.run_command(["list", "--limit", "0"])
            if result["success"]:
                lines = result["stdout"].strip().split('\n')
                book_count = len([line for line in lines if line.strip()])
                return {
                    "library_path": str(self.library_path),
                    "book_count": book_count,
                    "accessible": True
                }
            else:
                return {"accessible": False, "error": result["stderr"]}
        except Exception as e:
            return {"accessible": False, "error": str(e)}
