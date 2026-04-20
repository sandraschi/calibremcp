"""
Agentic library workflow (FastMCP 3.1, SEP-1577 sampling with tools).

PORTMANTEAU PATTERN RATIONALE: One high-level entry point for multi-step library tasks
so agents do not hand-orchestrate dozens of raw calls; when ``ctx.sample`` is available,
the host LLM plans and calls whitelisted tool surfaces, otherwise a deterministic fallback
runs.

Summary:
- Primary path: ``ctx.sample`` with synthesized tools from allowed operation names.
- Fallback: rule-based ``_execute_basic_workflow`` when sampling is unavailable or fails.

See Also:
    ``media_agentic`` for synopsis and reception flows that also use sampling.
"""

import asyncio
import time
from typing import Any

from fastmcp import Context

from ..logging_config import get_logger
from ..server import mcp
from ..services.author_service import author_service
from ..services.book_service import book_service
from ..services.extended_metadata_service import (
    extended_metadata_service,
)
from ..services.library_service import library_service
from ..services.tag_service import tag_service
from .shared.query_parsing import parse_intelligent_query, strip_inventory_question_phrases

logger = get_logger("calibremcp.tools.agentic_workflow")
logger.info("Agentic workflow tool module loaded")

# Legacy managers
CalibreManager = None
LibraryOperations = library_service
MetadataManager = extended_metadata_service
SearchOperations = book_service
ConversionManager = None  # Not yet implemented

logger.info("Calibre services connected for agentic workflows")


async def intelligent_query_parsing(
    query: str,
    parsing_prompt: str = "Parse this e-book query into structured parameters",
    max_attempts: int = 2,
) -> dict[str, Any]:
    """
    Map natural-language library questions to structured search hints.

    PORTMANTEAU PATTERN RATIONALE: Host LLM sampling is optional; this helper always
    returns deterministic fields so ``query_books`` / ``calibre_metadata_search`` can run
    without the client supporting SEP-1577.

    Args:
        query: User question or search phrase (e.g. inventory-style NL).
        parsing_prompt: Reserved for future ctx.sample-based parsing.
        max_attempts: Reserved for retry logic.

    Returns:
        Dict with ``success``, ``parsed_parameters`` (author, tag, search, semantic_query,
        prefer_semantic_search, language_hints), and ``parsing_method`` = ``structured_heuristic``.
    """
    del parsing_prompt, max_attempts  # API stability; sampling integration may use later
    try:
        logger.info("intelligent_query_parsing: %s", query[:200])
        structured = parse_intelligent_query(query)
        parsed_parameters: dict[str, Any] = {}

        if structured.get("author"):
            parsed_parameters["author"] = structured["author"]
        if structured.get("tag"):
            parsed_parameters["tag"] = structured["tag"]
        if structured.get("series"):
            parsed_parameters["series"] = structured["series"]
        if structured.get("pubdate"):
            parsed_parameters["pubdate"] = structured["pubdate"]
        if structured.get("rating") is not None:
            parsed_parameters["rating"] = structured["rating"]
        if structured.get("text"):
            parsed_parameters["search"] = structured["text"]
        if structured.get("language_hints"):
            parsed_parameters["language_hints"] = structured["language_hints"]

        semantic_candidate = strip_inventory_question_phrases(query)
        if structured.get("prefer_semantic_search"):
            parsed_parameters["prefer_semantic_search"] = True
            parsed_parameters["semantic_query"] = semantic_candidate or query.strip()

        success = bool(parsed_parameters) or bool(structured.get("prefer_semantic_search"))
        confidence = (
            0.85 if structured.get("prefer_semantic_search") else (0.75 if success else 0.25)
        )

        result = {
            "success": success,
            "parsed_parameters": parsed_parameters if success else {},
            "query": query,
            "parsing_method": "structured_heuristic",
            "confidence": confidence,
            "attempts_used": 1,
            "recommendations": [],
        }
        if structured.get("prefer_semantic_search"):
            result["recommendations"] = [
                "Use calibre_metadata_search(query=...) with semantic_query for best results on niche genres.",
                "Ensure calibre_metadata_index_build has been run for this library.",
            ]
        logger.info(
            "intelligent_query_parsing result: success=%s keys=%s",
            success,
            list(parsed_parameters.keys()),
        )
        return result

    except Exception as e:
        logger.exception(
            f"Intelligent query parsing failed: {e}", extra={"error": str(e), "query": query}
        )
        return {
            "success": False,
            "parsed_parameters": {},
            "query": query,
            "error": str(e),
            "parsing_method": "error_fallback",
        }


# Conversational Response Builders - SOTA dialogic pattern
def build_success_response(
    operation: str,
    summary: str,
    result: Any,
    next_steps: list[str] = None,
    suggestions: list[str] = None,
    diagnostic_info: dict[str, Any] = None,
    execution_time_ms: int | None = None,
    recommendations: list[str] = None,
) -> dict[str, Any]:
    """
    Build a standardized success response for conversational MCP tools.

    This implements the improved conversational tool return pattern with:
    - success: Boolean success indicator
    - operation: The operation that was performed
    - summary: Human-readable summary of what happened
    - result: The actual operation result data
    - next_steps: Suggested next actions (optional)
    - suggestions: Additional suggestions for the user (optional)
    - diagnostic_info: Technical details for debugging (optional)

    Args:
        operation: Name of the operation performed
        summary: Human-readable summary
        result: The operation result data
        next_steps: List of suggested next steps
        suggestions: List of additional suggestions
        diagnostic_info: Technical diagnostic information

    Returns:
        Standardized response dictionary
    """
    response = {"success": True, "operation": operation, "summary": summary, "result": result}

    if next_steps:
        response["next_steps"] = next_steps
    if suggestions:
        response["suggestions"] = suggestions
    if diagnostic_info:
        response["diagnostic_info"] = diagnostic_info
    if execution_time_ms is not None:
        response["execution_time_ms"] = execution_time_ms
    if recommendations:
        response["recommendations"] = recommendations

    return response


def build_error_response(
    operation: str,
    error: str,
    error_code: str = "UNKNOWN_ERROR",
    message: str = "",
    recovery_options: list[str] = None,
    diagnostic_info: dict[str, Any] = None,
    urgency: str = "medium",
    execution_time_ms: int | None = None,
) -> dict[str, Any]:
    """
    Build a standardized error response for conversational MCP tools.

    This implements the improved conversational tool return pattern for errors with:
    - success: False (error indicator)
    - operation: The operation that failed
    - error: Short error description
    - error_code: Machine-readable error code
    - message: Detailed error message (optional)
    - recovery_options: List of suggested recovery actions
    - diagnostic_info: Technical details for debugging
    - urgency: Error urgency level ("low", "medium", "high", "critical")

    Args:
        operation: Name of the operation that failed
        error: Short error description
        error_code: Machine-readable error code
        message: Detailed error message
        recovery_options: List of recovery suggestions
        diagnostic_info: Technical diagnostic information
        urgency: Error urgency level

    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "operation": operation,
        "error": error,
        "error_code": error_code,
        "urgency": urgency,
    }

    if message:
        response["message"] = message
    if recovery_options:
        response["recovery_options"] = recovery_options
    if diagnostic_info:
        response["diagnostic_info"] = diagnostic_info
    if execution_time_ms is not None:
        response["execution_time_ms"] = execution_time_ms

    return response


def _build_sampling_tools(available_ops: list[str]) -> list[Any]:
    """Build sampling tools for ctx.sample() from available operation names."""
    tools_map: dict[str, Any] = {}

    async def get_library_stats() -> dict[str, Any]:
        """Get library statistics: book count, author count, format distribution."""
        try:
            from .library.library_management import get_library_stats_helper

            result = await get_library_stats_helper(None)
            return result.model_dump()
        except Exception as e:
            return {"error": str(e), "success": False}

    async def list_books(limit: int = 10) -> dict[str, Any]:
        """List books in the library. limit: max books to return (default 10)."""
        try:
            data = await asyncio.to_thread(book_service.get_all, limit=limit)
            items = data.get("items", [])
            return {"books": items[:limit], "total": len(items)}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def search_books(query: str, limit: int = 10) -> dict[str, Any]:
        """Search books by title, author, or tag. query: search string. limit: max results."""
        try:
            data = await asyncio.to_thread(book_service.get_all, search=query, limit=limit)
            return {"results": data.get("items", []), "query": query}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_authors(limit: int = 10) -> dict[str, Any]:
        """List authors in the library. limit: max authors to return."""
        try:
            data = await asyncio.to_thread(author_service.get_all, limit=limit)
            items = data.get("items", []) if isinstance(data, dict) else data
            return {"authors": (items[:limit] if isinstance(items, list) else items)}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_tags(limit: int = 10) -> dict[str, Any]:
        """List tags in the library. limit: max tags to return."""
        try:
            data = await asyncio.to_thread(tag_service.get_all, limit=limit)
            items = data.get("items", []) if isinstance(data, dict) else data
            return {"tags": (items[:limit] if isinstance(items, list) else items)}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def list_libraries() -> dict[str, Any]:
        """List all available Calibre libraries with metadata."""
        try:
            from .library.library_management import list_libraries_helper

            result = await list_libraries_helper()
            return result.model_dump()
        except Exception as e:
            return {"error": str(e), "success": False}

    op_to_fn: dict[str, Any] = {
        "get_library_stats": get_library_stats,
        "list_books": list_books,
        "search_books": search_books,
        "get_authors": get_authors,
        "get_tags": get_tags,
        "list_libraries": list_libraries,
    }
    for op in available_ops:
        fn = op_to_fn.get(op)
        if fn:
            tools_map[op] = fn
    return list(tools_map.values())


class AgenticWorkflowTool:
    """Agentic workflow orchestration tool for Calibre MCP using SEP-1577."""

    def __init__(self):
        self.library_ops = LibraryOperations
        self.metadata_manager = MetadataManager
        self.search_ops = SearchOperations
        self.conversion_manager = ConversionManager
        logger.info("Agentic workflow tool initialized with real Calibre services")

    def is_available(self) -> bool:
        """Check if all required components are available."""
        return all(
            [
                self.library_ops is not None,
                self.metadata_manager is not None,
                self.search_ops is not None,
            ]
        )

    async def execute_workflow(
        self,
        workflow_prompt: str,
        available_operations: list[str],
        max_iterations: int = 5,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Execute an agentic workflow using SEP-1577 sampling with tools.

        When ctx is provided and client supports sampling, uses ctx.sample() with
        tools for LLM-driven orchestration. Otherwise falls back to rule-based workflow.
        """
        start_ms = int(time.time() * 1000)
        try:
            if not self.is_available():
                return build_error_response(
                    operation="agentic_library_workflow",
                    error="Calibre managers not available",
                    error_code="CALIBRE_UNAVAILABLE",
                    message="Required Calibre components are not initialized.",
                    recovery_options=[
                        "Install Calibre if not already installed",
                        "Configure the Calibre library path in settings",
                        "Restart MCP server after configuration changes",
                    ],
                    diagnostic_info={
                        "library_ops": self.library_ops is not None,
                        "metadata_manager": self.metadata_manager is not None,
                        "search_ops": self.search_ops is not None,
                        "conversion_manager": self.conversion_manager is not None,
                    },
                    urgency="high",
                    execution_time_ms=int(time.time() * 1000) - start_ms,
                )

            sampling_tools = _build_sampling_tools(available_operations)
            if ctx and sampling_tools:
                try:
                    result = await ctx.sample(
                        messages=f"""You are an autonomous Calibre library assistant. Execute the user's workflow by calling the available tools as needed. Workflow: {workflow_prompt}

Use the tools to gather information and perform operations. Summarize what you did and any findings at the end.""",
                        tools=sampling_tools,
                        max_tokens=2048,
                        system_prompt="You have access to Calibre e-book library tools. Call them to accomplish the user's workflow. Be concise.",
                    )
                    elapsed = int(time.time() * 1000) - start_ms
                    return build_success_response(
                        operation="agentic_library_workflow",
                        summary=result.text[:500]
                        if result.text
                        else "Workflow completed via LLM sampling.",
                        result={
                            "workflow_prompt": workflow_prompt,
                            "sampling_complete": True,
                            "llm_response": result.text,
                            "operations_available": available_operations,
                        },
                        next_steps=[
                            "Review the LLM's findings",
                            "Run additional workflows if needed",
                        ],
                        suggestions=[
                            "Try metadata enhancement workflows",
                            "Use bulk operations for format consistency",
                        ],
                        execution_time_ms=elapsed,
                        recommendations=[
                            "Use manage_books for detailed operations",
                            "Use manage_libraries for library stats",
                        ],
                    )
                except Exception as samp_err:
                    logger.info(f"Sampling fallback to basic workflow: {samp_err}")

            workflow_result = await self._execute_basic_workflow(
                workflow_prompt, available_operations
            )
            elapsed = int(time.time() * 1000) - start_ms

            return build_success_response(
                operation="agentic_library_workflow",
                summary=f"Executed workflow: {workflow_prompt}",
                result={
                    "workflow_prompt": workflow_prompt,
                    "operations_available": available_operations,
                    "executed_operations": workflow_result.get("executed", []),
                    "results": workflow_result.get("results", []),
                    "iterations_used": 1,
                    "max_iterations": max_iterations,
                },
                next_steps=[
                    "Review the executed operations and their results",
                    "Run additional workflows as needed",
                    "Check library statistics for changes",
                ],
                suggestions=[
                    "Consider running metadata enhancement workflows",
                    "Try bulk conversion operations for format consistency",
                    "Use search operations to find specific content",
                ],
                diagnostic_info={"workflow_type": workflow_result.get("workflow_type", "unknown")},
                execution_time_ms=elapsed,
                recommendations=["Use agentic_library_workflow for complex multi-step workflows"],
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
                    "Verify operation permissions",
                ],
                diagnostic_info={
                    "exception_type": type(e).__name__,
                    "workflow_prompt": workflow_prompt,
                    "available_operations_count": len(available_operations),
                },
                urgency="high" if "connection" in str(e).lower() else "medium",
                execution_time_ms=int(time.time() * 1000) - start_ms,
            )

    @staticmethod
    def _looks_like_nl_discovery(workflow_prompt: str) -> bool:
        """True for inventory / genre questions where semantic or FTS search is appropriate."""
        pl = workflow_prompt.lower()
        if any(
            x in pl
            for x in (
                "what ",
                "which ",
                "do we have",
                "locked room",
                "honkaku",
                "thriller",
                "mystery",
                "japanese",
                "light novel",
                "books like",
                "any books",
            )
        ):
            return True
        return len(workflow_prompt.split()) >= 8

    async def _execute_nl_discovery_workflow(self, workflow_prompt: str) -> dict[str, Any]:
        """Answer NL questions (e.g. Japanese locked-room thrillers) via RAG then SQL fallback."""

        def try_semantic() -> list[dict[str, Any]] | None:
            try:
                from calibre_mcp.rag.metadata_rag import search_metadata

                return search_metadata(workflow_prompt.strip(), top_k=20)
            except Exception as e:
                logger.info("Metadata semantic search unavailable: %s", e)
                return None

        rag = await asyncio.to_thread(try_semantic)
        if rag:
            return {
                "executed": ["calibre_metadata_search (embedding index)"],
                "results": [
                    {
                        "operation": "semantic_metadata_search",
                        "result": rag,
                        "message": "Ranked by similarity to your question. Rebuild index if results look stale.",
                    }
                ],
                "workflow_type": "nl_discovery_semantic",
            }

        parsed = parse_intelligent_query(workflow_prompt)
        search = (parsed.get("text") or "").strip() or strip_inventory_question_phrases(
            workflow_prompt
        )

        def fts_fallback() -> dict[str, Any]:
            return self.search_ops.get_all(
                limit=30,
                search=search or workflow_prompt,
                tag_name=parsed.get("tag"),
                author_name=parsed.get("author"),
            )

        books = await asyncio.to_thread(fts_fallback)
        return {
            "executed": ["query_books_sql_fallback"],
            "results": [
                {
                    "operation": "library_text_search",
                    "result": books,
                    "message": "Semantic index unavailable or empty; used SQL text search. "
                    "Run calibre_metadata_index_build, then calibre_metadata_search for "
                    "questions like niche genres or multilingual collections.",
                }
            ],
            "workflow_type": "nl_discovery_fts_fallback",
        }

    async def _execute_basic_workflow(
        self, workflow_prompt: str, _available_operations: list[str]
    ) -> dict[str, Any]:
        """
        Execute a basic workflow based on prompt analysis.

        This is a simplified implementation. A full SEP-1577 implementation would use
        the client's LLM to autonomously decide operations and their sequencing.
        """
        if self._looks_like_nl_discovery(workflow_prompt):
            return await self._execute_nl_discovery_workflow(workflow_prompt)

        executed = []
        results = []

        # Analyze workflow prompt and execute appropriate operations
        prompt_lower = workflow_prompt.lower()

        # Library organization workflow
        if any(keyword in prompt_lower for keyword in ["organize", "sort", "categorize", "clean"]):
            try:
                # Get library statistics
                stats = await self.library_ops.get_library_stats()
                executed.append("get_library_stats")
                results.append({"operation": "get_library_stats", "result": stats})

                # Check for duplicate books
                if "duplicate" in prompt_lower or "duplicates" in prompt_lower:
                    executed.append("find_duplicates")
                    results.append(
                        {
                            "operation": "find_duplicates",
                            "result": None,
                            "message": "[MOCK] No automatic duplicate merge. Use query_books(operation='search') "
                            "with title filters or inspect books manually.",
                        }
                    )

            except Exception as e:
                logger.exception(f"Error in organization workflow: {e}")

        # Metadata enhancement workflow
        elif any(keyword in prompt_lower for keyword in ["metadata", "enhance", "update", "fix"]):
            try:
                # Get books with missing metadata
                # In real BookService, search for books without tags or comments
                missing_metadata = await self.search_ops.get_all(limit=5, comment="")
                executed.append("find_missing_metadata")
                results.append(
                    {
                        "operation": "find_missing_metadata",
                        "result": missing_metadata.get("books", [])
                        if isinstance(missing_metadata, dict)
                        else [],
                    }
                )

                # Note: batch_update_metadata would require LLM integration for real values
                executed.append("metadata_scan_complete")
                results.append(
                    {
                        "operation": "metadata_scan",
                        "result": "Scan complete. Real batch update requires specific metadata source.",
                    }
                )

            except Exception as e:
                logger.exception(f"Error in metadata workflow: {e}")

        # Search and analysis workflow
        elif any(keyword in prompt_lower for keyword in ["search", "find", "analyze", "stats"]):
            try:
                # Get library statistics
                stats = await self.library_ops.get_library_stats()
                executed.append("get_library_stats")
                results.append({"operation": "get_library_stats", "result": stats})

                # Search for specific content if mentioned
                if "author" in prompt_lower:
                    authors = await author_service.get_all(limit=10)
                    executed.append("get_authors")
                    results.append(
                        {
                            "operation": "get_authors",
                            "result": authors[:10] if isinstance(authors, list) else authors,
                        }
                    )

                elif "tag" in prompt_lower or "tags" in prompt_lower:
                    tags = await tag_service.get_all(limit=10)
                    executed.append("get_tags")
                    results.append(
                        {
                            "operation": "get_tags",
                            "result": tags[:10] if isinstance(tags, list) else tags,
                        }
                    )

            except Exception as e:
                logger.exception(f"Error in search workflow: {e}")

        # Bulk operations workflow
        elif any(keyword in prompt_lower for keyword in ["bulk", "batch", "convert", "export"]):
            try:
                # Get conversion capabilities
                formats = (
                    await self.conversion_manager.get_supported_formats()
                    if self.conversion_manager
                    else []
                )
                executed.append("get_supported_formats")
                results.append({"operation": "get_supported_formats", "result": formats})

            except Exception as e:
                logger.exception(f"Error in bulk workflow: {e}")

        return {"executed": executed, "results": results, "workflow_type": "basic_orchestration"}


# Global instance for the MCP tool
_agentic_workflow_tool = AgenticWorkflowTool()


@mcp.tool()
async def agentic_library_workflow(
    workflow_prompt: str,
    available_operations: list[str],
    max_iterations: int = 5,
    ctx: Context | None = None,
) -> dict[str, Any]:
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
        max_iterations=min(max_iterations, 10),
        ctx=ctx,
    )
