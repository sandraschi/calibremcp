"""
Enhanced Help System for Calibre MCP

This module provides a comprehensive help system with multiple detail levels,
search functionality, and interactive examples for all available tools.
"""

import logging
from enum import Enum
from typing import Any

from ...server import mcp

logger = logging.getLogger("calibremcp.tools.help")


class HelpLevel(Enum):
    BASIC = "basic"  # Simple usage and basic examples
    ADVANCED = "adv"  # More detailed parameters and examples
    EXPERT = "expert"  # All parameters, edge cases, and advanced usage


# Help documentation with multiple detail levels
HELP_DOCS = {
    "overview": {
        "title": "Calibre MCP Server Help",
        "description": {
            "basic": "Access and manage your Calibre library programmatically.",
            "advanced": (
                "The Calibre MCP Server provides a RESTful API and programmatic interface "
                "to manage your Calibre library. It enables searching, adding, updating, "
                "and organizing ebooks through a simple API."
            ),
            "expert": (
                "A high-performance, extensible server for programmatic access to Calibre "
                "libraries. Features include full-text search, metadata management, format "
                "conversion, and plugin support for custom functionality."
            ),
        },
        "sections": [
            {
                "title": "Getting Started",
                "content": {
                    "basic": (
                        "1. `list_books()` - See what's in your library\n"
                        '2. `search_books(text="your query")` - Search for books\n'
                        "3. `get_book(book_id=123)` - Get book details"
                    ),
                    "advanced": (
                        "1. Start with `list_books(limit=10)` to explore your library\n"
                        '2. Use `search_books(text="science fiction", fields=["title", "tags"])` for targeted searches\n'
                        '3. Add books with `add_book(file_path="book.epub", fetch_metadata=True)`\n'
                        '4. Update metadata with `update_book(book_id=123, metadata={"title": "New Title"})`'
                    ),
                    "expert": (
                        "## Advanced Usage\n"
                        '- Use field boosting: `search_books(text="dune", fields=["title^3", "comments^1"])`\n'
                        '- Fuzzy search: `search_books(text="scifi", operator="FUZZY", fuzziness=1)`\n'
                        "- Phrase search: `search_books(text='\"machine learning\"')`\n"
                        "- Batch operations: Use `bulk_import()` for adding multiple books efficiently"
                    ),
                },
            },
            {
                "title": "Available Tools",
                "content": {
                    "basic": (
                        "- `search_books()` - Search and filter books\n"
                        "- `get_book()` - Get book details\n"
                        "- `add_book()` - Add new books\n"
                        "- `help()` - Show this help\n"
                        "- `agentic_library_workflow()` - Autonomous library orchestration [SEP-1577]"
                    ),
                    "advanced": (
                        "### Core Functions\n"
                        "- `search_books()` - Advanced search with filtering and sorting\n"
                        "- `get_book()` - Get detailed book information\n"
                        "- `add_book()` - Add books with metadata extraction\n"
                        "- `update_book()` - Modify book metadata\n"
                        "- `delete_book()` - Remove books\n\n"
                        "### Agentic & Help\n"
                        "- `agentic_library_workflow()` - Orchestrate complex tasks using sampling\n"
                        "- `help()` - Detailed interactive help system\n\n"
                        "### Utility Functions\n"
                        "- `list_authors()` - List all authors\n"
                        "- `list_series()` - List all book series\n"
                        "- `list_tags()` - List all tags"
                    ),
                    "expert": (
                        "## Core API Endpoints\n"
                        "### Search and Retrieval\n"
                        "- `search_books()` - Full-text search with field boosting, fuzzy matching, and faceting\n"
                        "- `get_book()` - Retrieve complete book record with all metadata and formats\n\n"
                        "### Agentic Orchestration\n"
                        "- `agentic_library_workflow()` - Autonomous library manager with recursive task solving\n"
                        "- `help()` - Multi-level documentation system with examples\n\n"
                        "### CRUD Operations\n"
                        "- `add_book()` - Add books from file, URL, or ISBN with metadata extraction\n"
                        "- `update_book()` - Atomic updates with conflict resolution\n"
                        "- `delete_book()` - Permanent or soft deletion with archiving\n\n"
                        "### Batch Operations\n"
                        "- `bulk_import()` - High-performance bulk import\n"
                        "- `bulk_update()` - Batch metadata updates\n"
                        "- `export_library()` - Export library in various formats"
                    ),
                },
            },
        ],
    },
    "search_books": {
        "title": "Search Books",
        "description": {
            "basic": "Search for books in your library with simple text queries.",
            "advanced": (
                "Advanced search with filtering, sorting, and field-specific queries. "
                "Supports fuzzy matching, phrase search, and field boosting."
            ),
            "expert": (
                "Powerful search functionality built on top of a full-text search engine. "
                "Supports complex queries, relevance scoring, highlighting, and faceted search. "
                "Uses a custom query parser with support for Lucene-like syntax."
            ),
        },
        "examples": {
            "basic": [
                {
                    "title": "Simple search",
                    "code": 'search_books(text="dune")',
                    "description": "Find books containing 'dune' in any field",
                },
                {
                    "title": "Search with filters",
                    "code": 'search_books(text="science fiction", author="Asimov")',
                    "description": "Find science fiction books by Isaac Asimov",
                },
            ],
            "advanced": [
                {
                    "title": "Field-specific search",
                    "code": 'search_books(text="title:dune OR author:herbert")',
                    "description": "Search in specific fields using field:value syntax",
                },
                {
                    "title": "Phrase search",
                    "code": 'search_books(text=""machine learning"", fields=["title", "comments"]',
                    "description": "Find exact phrase matches in title or comments",
                },
            ],
            "expert": [
                {
                    "title": "Advanced query with boosting",
                    "code": """search_books(
    text="((title:dune^2 OR series:dune) AND author:herbert) OR 'frank herbert'",
    operator="AND",
    min_score=0.5,
    highlight=True
)""",
                    "description": "Complex query with field boosting and highlighting",
                },
                {
                    "title": "Fuzzy search with filters",
                    "code": """search_books(
    text="scifi",
    operator="FUZZY",
    fuzziness=1,
    filters={"tags": ["science fiction"], "rating": {"gte": 4}}
)""",
                    "description": "Fuzzy search with tag and rating filters",
                },
            ],
        },
        "parameters": [
            {
                "name": "text",
                "type": "string",
                "required": False,
                "description": {
                    "basic": "Search query text",
                    "advanced": "Search query with optional field specifications and operators",
                    "expert": (
                        "Search query supporting field:value, AND/OR/NOT operators, "
                        'phrase matching with "", and grouping with ()'
                    ),
                },
            },
            {
                "name": "fields",
                "type": "list",
                "default": ["title^3", "authors^2", "tags^2", "series^1.5", "comments"],
                "description": {
                    "basic": "Fields to search in (default: title, authors, tags, series, comments)",
                    "advanced": "Fields to search with optional boosting (e.g., 'title^3' boosts title matches)",
                    "expert": (
                        "List of fields to search with optional boosting. "
                        "Fields are weighted by the boost factor (default: 1.0). "
                        "Special field '_all' searches across all fields."
                    ),
                },
            },
            {
                "name": "operator",
                "type": "string",
                "default": "OR",
                "options": ["AND", "OR", "FUZZY"],
                "description": {
                    "basic": "How to combine search terms: AND (all terms required) or OR (any term matches)",
                    "advanced": "Query logic: AND (all terms), OR (any term), or FUZZY (approximate matching)",
                    "expert": (
                        "Query operator: \n"
                        "- AND: All terms must match (intersection)\n"
                        "- OR: Any term can match (union)\n"
                        "- FUZZY: Enable fuzzy matching with configurable fuzziness"
                    ),
                },
            },
            {
                "name": "fuzziness",
                "type": "int/string",
                "default": "AUTO",
                "description": {
                    "basic": "Fuzzy matching level (0-2, higher is more fuzzy)",
                    "advanced": "Controls the fuzziness of the search (0=exact, 1-2=increasing fuzziness, AUTO=automatic)",
                    "expert": (
                        "Controls the Levenshtein distance for fuzzy matching. \n"
                        "- 0: No fuzzy matching (exact only)\n"
                        "- 1: One character difference allowed\n"
                        "- 2: Two character differences allowed\n"
                        "- AUTO: Automatically determines fuzziness based on term length"
                    ),
                },
            },
            {
                "name": "filters",
                "type": "dict",
                "default": {},
                "description": {
                    "basic": "Additional filters (e.g., {'author': 'Asimov', 'rating': 5})",
                    "advanced": "Field-value filters to narrow results (applied after text search)",
                    "expert": (
                        "Post-filter queries that don't affect relevance scoring. "
                        "Supports range queries (gte, lte), terms, and exists/missing checks. "
                        "Example: {'rating': {'gte': 4}, 'tags': ['scifi', 'classic']}"
                    ),
                },
            },
            {
                "name": "min_score",
                "type": "float",
                "default": 0.1,
                "description": {
                    "basic": "Minimum relevance score (0.0-1.0) for results",
                    "advanced": "Exclude results with relevance scores below this threshold",
                    "expert": (
                        "Exclude documents with a _score less than this value. "
                        "Useful for filtering out low-quality matches. "
                        "Typical values range from 0.1 (very permissive) to 0.7 (very strict)."
                    ),
                },
            },
            {
                "name": "highlight",
                "type": "bool/dict",
                "default": False,
                "description": {
                    "basic": "Whether to highlight matching terms in results",
                    "advanced": "Enable highlighting of matched terms with HTML tags or custom markers",
                    "expert": (
                        "Highlight matches in result snippets. Can be a boolean or a dictionary "
                        "with options: {'fields': {...}, 'pre_tags': ['<em>'], 'post_tags': ['</em>']}"
                    ),
                },
            },
            {
                "name": "suggest",
                "type": "bool/dict",
                "default": False,
                "description": {
                    "basic": "Whether to include search suggestions for typos",
                    "advanced": "Enable 'did you mean' suggestions for misspelled queries",
                    "expert": (
                        "Generate spelling corrections and suggestions. Can be a boolean or a "
                        "dictionary with options: {'text': '...', 'term': {...}}"
                    ),
                },
            },
            {
                "name": "limit",
                "type": "int",
                "default": 20,
                "description": {
                    "basic": "Maximum number of results to return",
                    "advanced": "Number of hits to return (pagination: use with offset)",
                    "expert": "Maximum number of hits to return. Use with offset for pagination. Max 1000.",
                },
            },
            {
                "name": "offset",
                "type": "int",
                "default": 0,
                "description": {
                    "basic": "Number of results to skip (for pagination)",
                    "advanced": "Offset for pagination (use with limit)",
                    "expert": "Number of initial matches to skip. Used with limit for pagination.",
                },
            },
            {
                "name": "sort",
                "type": "str/list",
                "default": "_score:desc",
                "description": {
                    "basic": "Sort order (e.g., 'title:asc' or 'pubdate:desc')",
                    "advanced": "Field(s) to sort by with optional sort order (asc/desc)",
                    "expert": (
                        "Sort specification. Can be a single field (e.g., 'title') or a list of "
                        "fields with sort order (e.g., ['_score:desc', 'title:asc']). "
                        "Special field '_score' sorts by relevance."
                    ),
                },
            },
        ],
        "returns": {
            "basic": "List of matching books with basic metadata",
            "advanced": "Paginated results with metadata including total count and facets",
            "expert": (
                "SearchResults object containing: hits (matching documents), total (total matches), "
                "max_score (highest relevance score), took (search time in ms), and aggregations "
                "if any aggregations were specified."
            ),
        },
    },
    "list_books": {
        "title": "List Books Tool",
        "description": "Search and list books in the library with filtering and pagination.",
        "usage": {
            "basic": "list_books()",
            "with_filters": """list_books(
    query="science fiction",
    author="Asimov",
    tag="sci-fi",
    format="epub",
    limit=10,
    offset=0
)""",
        },
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "default": "",
                "description": "Search query string",
            },
            {
                "name": "author",
                "type": "string",
                "default": "",
                "description": "Filter by author",
            },
            {
                "name": "tag",
                "type": "string",
                "default": "",
                "description": "Filter by tag",
            },
            {
                "name": "format",
                "type": "string",
                "default": "",
                "description": "Filter by book format",
            },
            {
                "name": "status",
                "type": "string",
                "default": "",
                "description": "Filter by reading status",
            },
            {
                "name": "limit",
                "type": "integer",
                "default": 50,
                "description": "Maximum number of results to return",
            },
            {
                "name": "offset",
                "type": "integer",
                "default": 0,
                "description": "Offset for pagination",
            },
            {
                "name": "sort_by",
                "type": "string",
                "default": "title",
                "description": "Field to sort by (title, author, date_added, pubdate, rating)",
            },
            {
                "name": "sort_order",
                "type": "string",
                "default": "asc",
                "description": "Sort order (asc or desc)",
            },
        ],
    },
    "get_book": {
        "title": "Get Book Tool",
        "description": "Get detailed information about a specific book.",
        "usage": {
            "basic": 'get_book(book_id="12345678")',
            "with_format": 'get_book(book_id="12345678", format="epub")',
        },
        "parameters": [
            {
                "name": "book_id",
                "type": "string",
                "required": True,
                "description": "ID of the book to retrieve",
            },
            {
                "name": "format",
                "type": "string",
                "required": False,
                "description": "Specific format to retrieve (if available)",
            },
        ],
    },
    "sampling": {
        "title": "Agentic Workflows & Sampling",
        "description": "Autonomous library management and orchestration using LLM sampling.",
        "usage": {
            "basic": 'agentic_library_workflow(workflow_prompt="Find and organize my IT books")',
        },
    },
}


async def _get_sampling_help(level: str) -> str:
    """Get help documentation for sampling and agentic workflows."""
    if level == "basic":
        return (
            "### Agentic Workflows (SEP-1577)\n"
            "CalibreMCP supports autonomous workflows using LLM sampling. This allows the AI to "
            "perform complex, multi-step tasks by calling multiple tools in sequence.\n\n"
            "**Key Tool:**\n"
            "- `agentic_library_workflow(workflow_prompt)`: Executes a complex library management task.\n\n"
            "**Example:**\n"
            "`agentic_library_workflow(workflow_prompt='Check for duplicate IT books und merge their metadata')`"
        )
    if level == "adv":
        return (
            "### Advanced Agentic Orchestration\n"
            "The `agentic_library_workflow` tool leverages SEP-1577 sampling to empower the AI to "
            "reason about library state and choose the best tools for a given goal.\n\n"
            "**Capabilities:**\n"
            "- Cross-tool orchestration (e.g., search -> analyze -> update)\n"
            "- Automatic error recovery and goal adjustment\n"
            "- Intelligent metadata synthesis from multiple sources\n\n"
            "**Performance Note:**\n"
            "Agentic workflows may take longer as they involve multiple LLM calls. Progress "
            "notifications are provided through the context object."
        )
    # expert
    return (
        "### Expert Sampling & Orchestration Patterns\n"
        "The agentic system uses the `ctx.sample()` API to perform recursive task decomposition.\n\n"
        "**Technical Details:**\n"
        "- **Sampling Engine:** USes the host LLM to generate tool sequences.\n"
        "- **Safety Guard:** Built-in loop detection and iteration limits (default: 10).\n"
        "- **State Management:** Maintains a scratchpad of previous tool results to inform next steps.\n\n"
        "**Integration Example:**\n"
        "```python\n"
        "result = await ctx.sample(\n"
        "    messages=[f'Workflow: {prompt}'],\n"
        "    tools=available_tools,\n"
        "    max_tokens=4096\n"
        ")\n"
        "```"
    )


@mcp.tool()
async def help_tool(
    category: str | None = None,
    tool_name: str | None = None,
    level: str = "basic",
) -> dict[str, Any]:
    """
    Get comprehensive help and documentation for Calibre library tools.

    Args:
        category: Optional category filter (e.g., 'book', 'library', 'sampling')
        tool_name: Optional specific tool to get help for
        level: Detail level: 'basic', 'adv', or 'expert'
    """
    level_enum = HelpLevel.BASIC
    # Mapping level string to level_enum (internal use if needed later)
    if level == "adv":
        level_enum = HelpLevel.ADVANCED
    elif level == "expert":
        level_enum = HelpLevel.EXPERT

    # Use level_enum or just the level string as needed
    _ = level_enum  # Suppress lint warning if still not used directly

    result = {
        "title": "CalibreMCP Help System",
        "level": level,
        "content": {},
    }

    if tool_name and tool_name in HELP_DOCS:
        result["content"] = HELP_DOCS[tool_name]
    elif category == "sampling":
        result["content"] = {
            "title": "Agentic Workflows & Sampling",
            "details": await _get_sampling_help(level),
        }
    else:
        # Default to overview if no specific match
        overview = HELP_DOCS.get("overview", {})
        result["content"] = {
            "title": overview.get("title", "Overview"),
            "description": overview.get("description", {}).get(level, "No description available."),
            "sections": [
                {
                    "title": s["title"],
                    "content": s["content"].get(level, "No content for this level."),
                }
                for s in overview.get("sections", [])
            ],
        }

    # Add sampling mention if in overview and not in basic
    if not category and not tool_name and level != "basic":
        result["sampling_note"] = await _get_sampling_help("basic")

    return result
