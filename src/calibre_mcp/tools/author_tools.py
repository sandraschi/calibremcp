"""
Legacy module: author operations are exposed only via ``manage_authors``.

The previous ``AuthorTools`` class carried ``@mcp_tool`` definitions that static
analyzers (e.g. ToolBench) treated as duplicate live tools. Schemas live in
``tools.author_schemas`` and are attached to ``manage_authors`` as MCP
``outputSchema`` — use that portmanteau exclusively.

Migration:
    list_authors / get_author / get_author_books / get_author_stats /
    get_authors_by_letter  →  manage_authors(operation="list"|"get"|...)
"""

from .author_schemas import (  # noqa: F401
    MANAGE_AUTHORS_OUTPUT_SCHEMA,
    AuthorBooksResult,
    AuthorByLetterResult,
    AuthorDetailResult,
    AuthorIdParam,
    AuthorListResult,
    AuthorStatsResult,
    ManageAuthorsOutput,
    OperationLiteral,
    PaginationLimit,
    PaginationOffset,
    StandardToolError,
)

# Back-compat names used in older docs / forks
AuthorSearchOutput = AuthorListResult
AuthorBooksOutput = AuthorBooksResult
AuthorStats = AuthorStatsResult

__all__ = [
    "MANAGE_AUTHORS_OUTPUT_SCHEMA",
    "AuthorByLetterResult",
    "AuthorBooksResult",
    "AuthorDetailResult",
    "AuthorListResult",
    "AuthorSearchOutput",
    "AuthorBooksOutput",
    "AuthorStats",
    "AuthorIdParam",
    "ManageAuthorsOutput",
    "OperationLiteral",
    "PaginationLimit",
    "PaginationOffset",
    "StandardToolError",
]
