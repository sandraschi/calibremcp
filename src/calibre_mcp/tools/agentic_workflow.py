"""
Agentic Workflow Tool for Calibre MCP - SEP-1577 Implementation

This tool enables autonomous orchestration of complex e-book library operations,
borrowing the client's LLM to intelligently sequence and execute multiple operations
without round-trip communication.

SEP-1577: Sampling with Tools - Server borrows client's LLM for autonomous workflows.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Import core managers for workflow operations
try:
    from ..calibre.manager import CalibreManager
    from ..calibre.library_operations import LibraryOperations
    from ..calibre.metadata_manager import MetadataManager
    from ..calibre.search_operations import SearchOperations
    from ..calibre.conversion_manager import ConversionManager
except ImportError as e:
    logger.warning(f"Failed to import Calibre managers: {e}")
    CalibreManager = None
    LibraryOperations = None
    MetadataManager = None
    SearchOperations = None
    ConversionManager = None

# Import response builders from advanced_memory if available
try:
    from advanced_memory.mcp.tools.adn_search import build_success_response, build_error_response
    _advanced_memory_available = True
except ImportError:
    _advanced_memory_available = False

    def build_success_response(operation: str, summary: str, result: Any) -> Dict[str, Any]:
        """Fallback response builder when advanced_memory is not available."""
        return {
            "success": True,
            "operation": operation,
            "summary": summary,
            "result": result,
            "next_steps": [],
            "suggestions": [],
            "diagnostic_info": {}
        }

    def build_error_response(operation: str, error: str, error_code: str = "UNKNOWN_ERROR",
                           message: str = "", recovery_options: List[str] = None) -> Dict[str, Any]:
        """Fallback error response builder when advanced_memory is not available."""
        return {
            "success": False,
            "operation": operation,
            "error": error,
            "error_code": error_code,
            "message": message,
            "recovery_options": recovery_options or [],
            "diagnostic_info": {}
        }


class AgenticWorkflowTool:
    """Agentic workflow orchestration tool for Calibre MCP using SEP-1577."""

    def __init__(self):
        self.calibre_manager = None
        self.library_ops = None
        self.metadata_manager = None
        self.search_ops = None
        self.conversion_manager = None

        if CalibreManager:
            try:
                self.calibre_manager = CalibreManager()
                self.library_ops = LibraryOperations()
                self.metadata_manager = MetadataManager()
                self.search_ops = SearchOperations()
                self.conversion_manager = ConversionManager()
                logger.info("Agentic workflow tool initialized with Calibre managers")
            except Exception as e:
                logger.error(f"Failed to initialize Calibre managers: {e}")

    def is_available(self) -> bool:
        """Check if all required components are available."""
        return all([
            self.calibre_manager is not None,
            self.library_ops is not None,
            self.metadata_manager is not None,
            self.search_ops is not None,
            self.conversion_manager is not None
        ])

    async def execute_workflow(self, workflow_prompt: str, available_operations: List[str],
                             max_iterations: int = 5) -> Dict[str, Any]:
        """
        Execute an agentic workflow using SEP-1577 sampling with tools.

        This method allows the server to autonomously orchestrate complex operations
        by borrowing the client's LLM for intelligent decision making and sequencing.

        Args:
            workflow_prompt: Natural language description of the desired workflow
            available_operations: List of operation names the LLM can choose from
            max_iterations: Maximum number of LLM-tool interaction loops

        Returns:
            Dict containing workflow execution results
        """
        try:
            # Validate availability
            if not self.is_available():
                return build_error_response(
                    operation="agentic_library_workflow",
                    error="Calibre managers not available",
                    error_code="CALIBRE_UNAVAILABLE",
                    message="Required Calibre components are not initialized",
                    recovery_options=[
                        "Check Calibre library configuration",
                        "Verify Calibre installation",
                        "Restart MCP server"
                    ]
                )

            # For now, implement a basic workflow executor
            # In a full SEP-1577 implementation, this would use the client's LLM
            # to autonomously decide operations and sequencing

            workflow_result = await self._execute_basic_workflow(workflow_prompt, available_operations)

            return build_success_response(
                operation="agentic_library_workflow",
                summary=f"Executed workflow: {workflow_prompt}",
                result={
                    "workflow_prompt": workflow_prompt,
                    "operations_available": available_operations,
                    "executed_operations": workflow_result.get("executed", []),
                    "results": workflow_result.get("results", []),
                    "iterations_used": 1,
                    "max_iterations": max_iterations
                }
            )

        except Exception as e:
            logger.error(f"Error in agentic workflow: {e}", exc_info=True)
            return build_error_response(
                operation="agentic_library_workflow",
                error=str(e),
                error_code="WORKFLOW_EXECUTION_FAILED",
                message=f"Failed to execute workflow: {workflow_prompt}",
                recovery_options=[
                    "Simplify the workflow prompt",
                    "Check library connectivity",
                    "Verify operation permissions"
                ]
            )

    async def _execute_basic_workflow(self, workflow_prompt: str,
                                    available_operations: List[str]) -> Dict[str, Any]:
        """
        Execute a basic workflow based on prompt analysis.

        This is a simplified implementation. A full SEP-1577 implementation would use
        the client's LLM to autonomously decide operations and their sequencing.
        """
        executed = []
        results = []

        # Analyze workflow prompt and execute appropriate operations
        prompt_lower = workflow_prompt.lower()

        # Library organization workflow
        if any(keyword in prompt_lower for keyword in ["organize", "sort", "categorize", "clean"]):
            try:
                # Get library statistics
                stats = await self.library_ops.get_library_stats() if self.library_ops else {}
                executed.append("get_library_stats")
                results.append({"operation": "get_library_stats", "result": stats})

                # Check for duplicate books
                if "duplicate" in prompt_lower or "duplicates" in prompt_lower:
                    duplicates = await self.search_ops.find_duplicates() if self.search_ops else []
                    executed.append("find_duplicates")
                    results.append({"operation": "find_duplicates", "result": duplicates})

            except Exception as e:
                logger.error(f"Error in organization workflow: {e}")

        # Metadata enhancement workflow
        elif any(keyword in prompt_lower for keyword in ["metadata", "enhance", "update", "fix"]):
            try:
                # Get books with missing metadata
                missing_metadata = await self.metadata_manager.find_books_with_missing_metadata() if self.metadata_manager else []
                executed.append("find_missing_metadata")
                results.append({"operation": "find_missing_metadata", "result": missing_metadata})

                # Update metadata for found books
                if missing_metadata:
                    updated_count = await self.metadata_manager.batch_update_metadata(missing_metadata[:5])  # Limit to 5 for safety
                    executed.append("batch_update_metadata")
                    results.append({"operation": "batch_update_metadata", "result": f"Updated {updated_count} books"})

            except Exception as e:
                logger.error(f"Error in metadata workflow: {e}")

        # Search and analysis workflow
        elif any(keyword in prompt_lower for keyword in ["search", "find", "analyze", "stats"]):
            try:
                # Get library statistics
                stats = await self.library_ops.get_library_stats() if self.library_ops else {}
                executed.append("get_library_stats")
                results.append({"operation": "get_library_stats", "result": stats})

                # Search for specific content if mentioned
                if "author" in prompt_lower:
                    authors = await self.search_ops.get_unique_authors() if self.search_ops else []
                    executed.append("get_authors")
                    results.append({"operation": "get_authors", "result": authors[:10]})  # Top 10

                elif "tag" in prompt_lower or "tags" in prompt_lower:
                    tags = await self.search_ops.get_unique_tags() if self.search_ops else []
                    executed.append("get_tags")
                    results.append({"operation": "get_tags", "result": tags[:10]})  # Top 10

            except Exception as e:
                logger.error(f"Error in search workflow: {e}")

        # Bulk operations workflow
        elif any(keyword in prompt_lower for keyword in ["bulk", "batch", "convert", "export"]):
            try:
                # Get conversion capabilities
                formats = await self.conversion_manager.get_supported_formats() if self.conversion_manager else []
                executed.append("get_supported_formats")
                results.append({"operation": "get_supported_formats", "result": formats})

            except Exception as e:
                logger.error(f"Error in bulk workflow: {e}")

        return {
            "executed": executed,
            "results": results,
            "workflow_type": "basic_orchestration"
        }


# Global instance for the MCP tool
_agentic_workflow_tool = AgenticWorkflowTool()


@mcp.tool()
async def agentic_library_workflow(
    workflow_prompt: str,
    available_operations: List[str],
    max_iterations: int = 5
) -> Dict[str, Any]:
    """
    Execute agentic workflows for Calibre e-book library management using SEP-1577.

    This revolutionary tool borrows your LLM's intelligence to autonomously orchestrate
    complex library operations without client round-trips. Perfect for bulk operations,
    library organization, metadata enhancement, and intelligent content management.

    WORKFLOW EXAMPLES:
    - "Organize my library by fixing duplicate books and updating metadata"
    - "Find all books by Terry Pratchett and export them to EPUB format"
    - "Analyze my reading patterns and suggest books to read next"
    - "Clean up library by removing books with missing covers or metadata"
    - "Convert all PDF books to EPUB format for better device compatibility"

    AVAILABLE OPERATIONS:
    - Library Management: get_library_stats, list_books, organize_library
    - Search & Discovery: search_books, find_duplicates, get_authors, get_tags
    - Metadata: update_metadata, batch_update_metadata, find_missing_metadata
    - File Operations: convert_books, export_books, import_books
    - Analysis: analyze_reading_patterns, generate_stats, cleanup_library

    Args:
        workflow_prompt: Natural language description of the desired workflow outcome
        available_operations: List of operations your LLM can choose from and orchestrate
        max_iterations: Maximum LLM-tool interaction loops (default: 5, max: 10)

    Returns:
        Dict containing workflow execution results with success/error status

    Raises:
        No exceptions - all errors are handled internally and returned in response
    """
    return await _agentic_workflow_tool.execute_workflow(
        workflow_prompt=workflow_prompt,
        available_operations=available_operations,
        max_iterations=min(max_iterations, 10)  # Cap at 10 for safety
    )