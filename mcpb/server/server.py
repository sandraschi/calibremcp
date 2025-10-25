"""
CalibreMCP MCPB Entry Point

Standard MCPB-conformant entry point for CalibreMCP server.
Handles Python path setup and launches the FastMCP 2.12 server.
"""

import sys
from pathlib import Path

# Add parent/src directory to Python path
repo_root = Path(__file__).parent.parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

# Initialize structured logging
from calibre_mcp.logging_config import setup_logging, get_logger, log_operation

# Setup logging
setup_logging(
    level="INFO",
    log_file=Path("logs/calibremcp.log"),
    enable_console=True
)

logger = get_logger("calibremcp.mcpb")

# Now import and run the server
from calibre_mcp.server import main

if __name__ == "__main__":
    log_operation(logger, "mcpb_startup", level="INFO",
                 repo_root=str(repo_root), src_path=str(src_path),
                 version="MCPB", collection_size="1000+ books")
    
    try:
        main()
    except KeyboardInterrupt:
        log_operation(logger, "server_shutdown", level="INFO", reason="user_interrupt")
    except Exception as e:
        log_operation(logger, "server_error", level="ERROR", error=str(e))
        sys.exit(1)
