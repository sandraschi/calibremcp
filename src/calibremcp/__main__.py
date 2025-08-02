""
Calibre MCP - Command-line entry point.

This module provides the command-line interface for the Calibre MCP server.
"""

import asyncio
import logging
import sys

from calibremcp import CalibreMCPServer


def main() -> int:
    """Run the Calibre MCP server from the command line.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Import here to ensure logging is configured first
    import argparse
    
    parser = argparse.ArgumentParser(description="Calibre MCP Server")
    parser.add_argument(
        "--library",
        type=str,
        help="Path to Calibre library (default: auto-detect)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create and run the server
        server = CalibreMCPServer(
            library_path=args.library,
            host=args.host,
            port=args.port,
            debug=args.debug,
        )
        
        print(f"Starting Calibre MCP server on {args.host}:{args.port}")
        print(f"Library path: {server.library_path}")
        print("Press Ctrl+C to stop")
        
        asyncio.run(server.run())
        return 0
        
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
