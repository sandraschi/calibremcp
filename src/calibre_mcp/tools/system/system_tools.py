"""
System tools for CalibreMCP - Help and Status functionality.

These tools provide comprehensive help system and system status monitoring
following MCP production standards.
"""

import os
import platform
import psutil
import sys
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum

from pydantic import Field

# Import the MCP server instance and helper functions
from ...server import mcp, get_api_client, current_library
from ...logging_config import get_logger, log_operation, log_error
from ...config import CalibreConfig

logger = get_logger("calibremcp.tools.system")


class HelpLevel(str, Enum):
    """Help detail levels"""
    BASIC = "basic"        # Quick overview and essential commands
    INTERMEDIATE = "intermediate"  # Detailed tool descriptions and workflows
    ADVANCED = "advanced"  # Technical details and architecture
    EXPERT = "expert"      # Development and troubleshooting


class StatusLevel(str, Enum):
    """Status detail levels"""
    BASIC = "basic"        # Core system status
    INTERMEDIATE = "intermediate"  # Tool availability and configuration
    ADVANCED = "advanced"  # Performance metrics and system resources
    DIAGNOSTIC = "diagnostic"  # Detailed troubleshooting information


# Help documentation with multiple detail levels
HELP_DOCS = {
    "overview": {
        "title": "CalibreMCP Server Help",
        "description": {
            "basic": "FastMCP 2.12 server for Calibre ebook library management with AI-powered features.",
            "intermediate": (
                "CalibreMCP is a comprehensive Model Context Protocol (MCP) server that seamlessly "
                "integrates Claude AI with your Calibre ebook library. It provides intelligent "
                "assistance for reading, research, and library organization with Austrian efficiency."
            ),
            "advanced": (
                "A high-performance, extensible MCP server built on FastMCP 2.12 framework. "
                "Features include automatic library discovery, multi-library support, advanced search, "
                "metadata management, format conversion, AI-powered recommendations, and comprehensive "
                "analytics. Designed for Austrian efficiency with weeb-friendly Japanese content support."
            ),
            "expert": (
                "Production-ready MCP server with modular architecture, structured logging, "
                "comprehensive error handling, and extensive tooling. Supports both local and remote "
                "Calibre libraries, automatic library discovery via Calibre configuration files, "
                "and advanced features like series analysis, duplicate detection, and reading analytics."
            )
        }
    },
    "tools": {
        "core": {
            "title": "Core Library Operations",
            "description": {
                "basic": "Essential tools for basic library access",
                "intermediate": "Core functionality for listing, searching, and retrieving books",
                "advanced": "Comprehensive library operations with filtering and sorting",
                "expert": "Low-level library access with performance optimization"
            },
            "tools": ["list_books", "get_book_details", "search_books", "test_calibre_connection"]
        },
        "library": {
            "title": "Library Management",
            "description": {
                "basic": "Tools for managing multiple libraries",
                "intermediate": "Multi-library operations and switching",
                "advanced": "Cross-library search and statistics",
                "expert": "Library health monitoring and optimization"
            },
            "tools": ["list_libraries", "switch_library", "get_library_stats", "cross_library_search"]
        },
        "analysis": {
            "title": "Library Analysis",
            "description": {
                "basic": "Basic statistics and health checks",
                "intermediate": "Comprehensive analytics and recommendations",
                "advanced": "Advanced metrics and trend analysis",
                "expert": "Deep analysis with performance profiling"
            },
            "tools": ["get_tag_statistics", "find_duplicate_books", "get_series_analysis", "analyze_library_health", "unread_priority_list", "reading_statistics"]
        },
        "metadata": {
            "title": "Metadata Management",
            "description": {
                "basic": "Basic metadata updates",
                "intermediate": "Bulk metadata operations",
                "advanced": "AI-powered metadata enhancement",
                "expert": "Advanced metadata validation and repair"
            },
            "tools": ["update_book_metadata", "auto_organize_tags", "fix_metadata_issues"]
        },
        "files": {
            "title": "File Operations",
            "description": {
                "basic": "Basic file operations",
                "intermediate": "Format conversion and downloads",
                "advanced": "Bulk file operations",
                "expert": "Advanced file management with optimization"
            },
            "tools": ["convert_book_format", "download_book", "bulk_format_operations"]
        },
        "specialized": {
            "title": "Specialized Features",
            "description": {
                "basic": "Specialized content organization",
                "intermediate": "AI-powered recommendations",
                "advanced": "Advanced content curation",
                "expert": "Expert-level content analysis"
            },
            "tools": ["japanese_book_organizer", "it_book_curator", "reading_recommendations"]
        }
    },
    "examples": {
        "basic": [
            "# List books in your library",
            "list_books()",
            "",
            "# Search for a specific book",
            "search_books(text=\"python programming\")",
            "",
            "# Get details for a specific book",
            "get_book_details(book_id=123)"
        ],
        "intermediate": [
            "# Advanced search with filters",
            "search_books(text=\"machine learning\", fields=[\"title\", \"tags\"], operator=\"AND\")",
            "",
            "# Get library statistics",
            "get_library_stats()",
            "",
            "# Find duplicate books",
            "find_duplicate_books()",
            "",
            "# Analyze series completion",
            "get_series_analysis()"
        ],
        "advanced": [
            "# Cross-library search",
            "cross_library_search(query=\"python\", libraries=[\"IT\", \"Programming\"])",
            "",
            "# Bulk metadata update",
            "update_book_metadata([{\"book_id\": 123, \"tags\": [\"programming\", \"python\"]}])",
            "",
            "# Convert multiple books",
            "convert_book_format([{\"book_id\": 123, \"target_format\": \"PDF\"}])",
            "",
            "# Get reading recommendations",
            "reading_recommendations()"
        ],
        "expert": [
            "# Library health analysis",
            "analyze_library_health()",
            "",
            "# Japanese content organization",
            "japanese_book_organizer()",
            "",
            "# IT book curation",
            "it_book_curator()",
            "",
            "# Advanced reading analytics",
            "reading_statistics()"
        ]
    }
}


@mcp.tool()
async def help(
    level: HelpLevel = Field(HelpLevel.BASIC, description="Help detail level"),
    topic: Optional[str] = Field(None, description="Specific topic to focus on")
) -> str:
    """
    Comprehensive help system with multiple detail levels.
    
    Provides contextual assistance and documentation for CalibreMCP features,
    organized by knowledge levels from basic usage to advanced technical details.
    
    Args:
        level: Help detail level (basic/intermediate/advanced/expert)
        topic: Specific topic to focus on (optional)
        
    Returns:
        Formatted help content with examples and guidance
    """
    try:
        log_operation(logger, "help_requested", level=level.value, topic=topic)
        
        # Build help content
        content = []
        
        # Overview section
        overview = HELP_DOCS["overview"]
        content.append(f"# {overview['title']}")
        content.append("")
        content.append(overview["description"][level.value])
        content.append("")
        
        # Tools section
        if not topic or topic == "tools":
            content.append("## Available Tools")
            content.append("")
            
            for category, info in HELP_DOCS["tools"].items():
                content.append(f"### {info['title']}")
                content.append("")
                content.append(info["description"][level.value])
                content.append("")
                
                if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
                    content.append("**Tools:**")
                    for tool_name in info["tools"]:
                        content.append(f"- `{tool_name}()`")
                    content.append("")
        
        # Examples section
        if level in [HelpLevel.BASIC, HelpLevel.INTERMEDIATE]:
            content.append("## Quick Examples")
            content.append("")
            for example in HELP_DOCS["examples"][level.value]:
                content.append(example)
            content.append("")
        
        # Advanced examples
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Advanced Examples")
            content.append("")
            for example in HELP_DOCS["examples"][level.value]:
                content.append(example)
            content.append("")
        
        # Configuration section
        if level in [HelpLevel.INTERMEDIATE, HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Configuration")
            content.append("")
            content.append("CalibreMCP automatically discovers Calibre libraries:")
            content.append("")
            content.append("```python")
            content.append("from calibre_mcp.config import CalibreConfig")
            content.append("config = CalibreConfig.load_config()")
            content.append("libraries = config.list_libraries()")
            content.append("```")
            content.append("")
        
        # Troubleshooting section
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Troubleshooting")
            content.append("")
            content.append("### Common Issues")
            content.append("")
            content.append("1. **Library not found**: Use `list_libraries()` to see discovered libraries")
            content.append("2. **Connection failed**: Check Calibre server with `test_calibre_connection()`")
            content.append("3. **Performance issues**: Use `analyze_library_health()` for diagnostics")
            content.append("")
        
        return "\n".join(content)
        
    except Exception as e:
        log_error(logger, "help_error", e)
        return f"Error generating help: {str(e)}"


@mcp.tool()
async def status(
    level: StatusLevel = Field(StatusLevel.BASIC, description="Status detail level"),
    focus: Optional[str] = Field(None, description="Focus area: sync, tools, system, projects")
) -> str:
    """
    Comprehensive system status and diagnostic information.
    
    Provides different levels of diagnostic information about the CalibreMCP
    server, library connections, and system health.
    
    Args:
        level: Status detail level (basic/intermediate/advanced/diagnostic)
        focus: Optional focus area for detailed information
        
    Returns:
        Formatted status report with system information
    """
    try:
        log_operation(logger, "status_requested", level=level.value, focus=focus)
        
        # Get system information
        system_info = {
            "platform": platform.system(),
            "python_version": sys.version,
            "calibremcp_version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
        
        # Get library information
        config = CalibreConfig.load_config()
        libraries = config.list_libraries()
        
        # Get Calibre connection status
        try:
            client = await get_api_client()
            connection_test = await client.test_connection()
            calibre_status = "connected"
            calibre_info = connection_test
        except Exception as e:
            calibre_status = "disconnected"
            calibre_info = {"error": str(e)}
        
        # Build status report
        content = []
        
        # Header
        content.append("# CalibreMCP System Status")
        content.append("")
        content.append(f"**Timestamp:** {system_info['timestamp']}")
        content.append(f"**Version:** {system_info['calibremcp_version']}")
        content.append(f"**Platform:** {system_info['platform']}")
        content.append("")
        
        # Basic status
        content.append("## Core Status")
        content.append("")
        content.append(f"**Calibre Connection:** {calibre_status.upper()}")
        content.append(f"**Libraries Discovered:** {len(libraries)}")
        content.append(f"**Current Library:** {current_library}")
        content.append("")
        
        # Library information
        if libraries:
            content.append("## Discovered Libraries")
            content.append("")
            for lib in libraries:
                status_icon = "🟢" if lib['is_active'] else "⚪"
                content.append(f"{status_icon} **{lib['name']}**: {lib['path']}")
            content.append("")
        
        # Intermediate level - Tool information
        if level in [StatusLevel.INTERMEDIATE, StatusLevel.ADVANCED, StatusLevel.DIAGNOSTIC]:
            content.append("## Tool Status")
            content.append("")
            
            # Get tool categories
            tool_categories = {
                "Core Operations": ["list_books", "get_book_details", "search_books", "test_calibre_connection"],
                "Library Management": ["list_libraries", "switch_library", "get_library_stats", "cross_library_search"],
                "Analysis": ["get_tag_statistics", "find_duplicate_books", "get_series_analysis", "analyze_library_health"],
                "Metadata": ["update_book_metadata", "auto_organize_tags", "fix_metadata_issues"],
                "Files": ["convert_book_format", "download_book", "bulk_format_operations"],
                "Specialized": ["japanese_book_organizer", "it_book_curator", "reading_recommendations"]
            }
            
            for category, tools in tool_categories.items():
                content.append(f"### {category}")
                content.append(f"**Tools Available:** {len(tools)}")
                if level == StatusLevel.DIAGNOSTIC:
                    for tool in tools:
                        content.append(f"- `{tool}()` ✅")
                content.append("")
        
        # Advanced level - Performance metrics
        if level in [StatusLevel.ADVANCED, StatusLevel.DIAGNOSTIC]:
            content.append("## Performance Metrics")
            content.append("")
            
            try:
                # System resources
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                content.append(f"**Memory Usage:** {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
                content.append(f"**CPU Usage:** {cpu_percent}%")
                content.append("")
                
                # Python process info
                process = psutil.Process()
                content.append(f"**Python Process Memory:** {process.memory_info().rss // (1024**2)}MB")
                content.append(f"**Python Process CPU:** {process.cpu_percent()}%")
                content.append("")
                
            except Exception as e:
                content.append(f"**Performance Metrics:** Error retrieving - {str(e)}")
                content.append("")
        
        # Diagnostic level - Detailed troubleshooting
        if level == StatusLevel.DIAGNOSTIC:
            content.append("## Diagnostic Information")
            content.append("")
            
            # Calibre connection details
            if calibre_status == "connected":
                content.append("### Calibre Server Details")
                content.append(f"**Server URL:** {calibre_info.get('server_url', 'Unknown')}")
                content.append(f"**Server Version:** {calibre_info.get('version', 'Unknown')}")
                content.append(f"**Total Books:** {calibre_info.get('total_books', 'Unknown')}")
                content.append("")
            else:
                content.append("### Calibre Connection Issues")
                content.append(f"**Error:** {calibre_info.get('error', 'Unknown error')}")
                content.append("")
            
            # Configuration details
            content.append("### Configuration")
            content.append(f"**Auto-discover Libraries:** {config.auto_discover_libraries}")
            content.append(f"**Server URL:** {config.server_url}")
            content.append(f"**Timeout:** {config.timeout}s")
            content.append(f"**Max Retries:** {config.max_retries}")
            content.append("")
            
            # Environment variables
            content.append("### Environment Variables")
            env_vars = ["CALIBRE_SERVER_URL", "CALIBRE_LIBRARY_PATH", "CALIBRE_LIBRARIES"]
            for var in env_vars:
                value = "Set" if var in os.environ else "Not set"
                content.append(f"**{var}:** {value}")
            content.append("")
        
        return "\n".join(content)
        
    except Exception as e:
        log_error(logger, "status_error", e)
        return f"Error generating status: {str(e)}"


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Machine-readable health check for monitoring systems.
    
    Returns structured health information suitable for monitoring
    systems, CI/CD pipelines, and automated health checks.
    
    Returns:
        Dictionary with health status and metrics
    """
    try:
        log_operation(logger, "health_check_requested")
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {}
        }
        
        # Check Calibre connection
        try:
            client = await get_api_client()
            await client.test_connection()
            health_status["checks"]["calibre_connection"] = {
                "status": "healthy",
                "message": "Calibre server accessible"
            }
        except Exception as e:
            health_status["checks"]["calibre_connection"] = {
                "status": "unhealthy",
                "message": f"Calibre connection failed: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        # Check library discovery
        try:
            config = CalibreConfig.load_config()
            libraries = config.list_libraries()
            health_status["checks"]["library_discovery"] = {
                "status": "healthy",
                "message": f"Found {len(libraries)} libraries",
                "libraries_count": len(libraries)
            }
        except Exception as e:
            health_status["checks"]["library_discovery"] = {
                "status": "unhealthy",
                "message": f"Library discovery failed: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        # Check system resources
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            health_status["checks"]["system_resources"] = {
                "status": "healthy" if memory.percent < 90 and cpu_percent < 90 else "warning",
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent
            }
            
            if memory.percent >= 90 or cpu_percent >= 90:
                health_status["status"] = "degraded"
                
        except Exception as e:
            health_status["checks"]["system_resources"] = {
                "status": "unknown",
                "message": f"Could not check system resources: {str(e)}"
            }
        
        # Overall status determination
        unhealthy_checks = [check for check in health_status["checks"].values() 
                           if check["status"] == "unhealthy"]
        if unhealthy_checks:
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        log_error(logger, "health_check_error", e)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
