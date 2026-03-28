"""
JSON-serializable Pydantic models for manage_authors responses.

Used to expose explicit outputSchema to MCP clients (ToolBench / LLM planners).
Legacy per-tool classes were removed; use manage_authors(operation=...) only.

Placed at tools/author_schemas.py (not under authors/) so importing schemas does
not execute authors/__init__.py (which loads the full server).
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# --- Success shapes (one per operation) ---
# Author-shaped dicts follow Calibre author rows: id, name, sort, link, book_count, etc.


class AuthorListResult(BaseModel):
    """operation=list: paginated authors matching optional query."""

    items: list[dict[str, Any]] = Field(description="Authors for the current page")
    total: int = Field(description="Total authors matching the query (not just this page)")
    page: int = Field(description="1-based page index derived from offset and limit")
    per_page: int = Field(description="Same as limit for this call")
    total_pages: int = Field(description="Total pages given current limit")


class AuthorBooksResult(BaseModel):
    """operation=get_books: author metadata plus paginated book rows."""

    author: dict[str, Any] | None = Field(
        description="Author record; null only if the author id did not resolve (legacy edge case)"
    )
    books: list[dict[str, Any]] = Field(description="Book records for this page")
    total: int = Field(description="Total books by this author")
    page: int = Field(description="1-based page index")
    per_page: int = Field(description="Page size (limit)")
    total_pages: int = Field(description="Total pages for this author")


class LetterCount(BaseModel):
    letter: str = Field(description="Uppercase first-letter bucket")
    count: int = Field(description="Number of authors in this bucket")


class TopAuthor(BaseModel):
    id: int
    name: str
    book_count: int


class AuthorStatsResult(BaseModel):
    """operation=stats: aggregate statistics for the whole library."""

    total_authors: int = Field(description="Count of author rows in the library")
    authors_by_letter: list[LetterCount] = Field(
        description="Histogram: how many authors start with each letter A–Z (and other buckets)"
    )
    top_authors: list[TopAuthor] = Field(
        description="Up to 10 authors ranked by number of linked books"
    )


class AuthorByLetterResult(BaseModel):
    """operation=by_letter: authors whose sort name starts with the given letter."""

    authors: list[dict[str, Any]] = Field(description="Matching author records")
    letter: str = Field(description="Normalized single uppercase letter")
    count: int = Field(description="len(authors)")


class StandardToolError(BaseModel):
    """Structured failure from format_error_response / handle_tool_error."""

    success: Literal[False] = False
    error: str = Field(description="Human-readable failure message")
    error_code: str = Field(description="Stable machine code, e.g. MISSING_AUTHOR_ID")
    error_type: str = Field(description="Exception class name or category")
    operation: str | None = Field(
        default=None, description="Portmanteau sub-operation if applicable"
    )
    parameters: dict[str, Any] | None = None
    suggestions: list[str] = Field(default_factory=list)
    related_tools: list[str] = Field(default_factory=list)
    diagnostic: dict[str, Any] | None = None
    execution_time_ms: int | None = None
    recommendations: list[str] | None = None


class AuthorDetailResult(BaseModel):
    """operation=get: single author record from Calibre."""

    model_config = ConfigDict(extra="allow")

    id: int = Field(description="authors.id primary key")
    name: str = Field(description="Display name")
    sort: str | None = Field(default=None, description="Sort key as stored in Calibre")
    link: str | None = Field(default=None, description="Author web link if set")
    book_count: int = Field(default=0, description="Number of books linked to this author")


class ManageAuthorsMCPOutput(BaseModel):
    """
    Single object schema for MCP outputSchema (FastMCP rejects root ``anyOf`` unions).

    Which keys appear depends on ``operation`` and success vs error; unspecified keys are
    omitted. Extra provider-specific keys are allowed.
    """

    model_config = ConfigDict(extra="allow")

    # --- list / get_books (pagination) ---
    items: list[dict[str, Any]] | None = Field(
        default=None, description="operation=list: authors for this page"
    )
    total: int | None = Field(
        default=None, description="list or get_books: total row count for the query"
    )
    page: int | None = Field(default=None, description="1-based page index")
    per_page: int | None = Field(default=None, description="Page size (limit)")
    total_pages: int | None = Field(default=None, description="Total pages at current limit")

    # --- get (single author record) ---
    id: int | None = Field(default=None, description="operation=get: authors.id")
    name: str | None = Field(default=None, description="operation=get: display name")
    sort: str | None = Field(default=None, description="operation=get: Calibre sort key")
    link: str | None = Field(default=None, description="operation=get: URL if set")
    book_count: int | None = Field(default=None, description="operation=get: linked books")

    # --- get_books ---
    author: dict[str, Any] | None = Field(
        default=None, description="operation=get_books: author metadata"
    )
    books: list[dict[str, Any]] | None = Field(
        default=None, description="operation=get_books: book rows for this page"
    )

    # --- stats ---
    total_authors: int | None = Field(default=None, description="operation=stats: author count")
    authors_by_letter: list[dict[str, Any]] | None = Field(
        default=None, description="operation=stats: {letter, count} histogram"
    )
    top_authors: list[dict[str, Any]] | None = Field(
        default=None, description="operation=stats: top authors by book count"
    )

    # --- by_letter ---
    authors: list[dict[str, Any]] | None = Field(
        default=None, description="operation=by_letter: matching authors"
    )
    letter: str | None = Field(default=None, description="operation=by_letter: first letter")
    count: int | None = Field(default=None, description="operation=by_letter: len(authors)")

    # --- StandardToolError / handle_tool_error ---
    success: bool | None = Field(
        default=None, description="False on structured errors; may be absent on success"
    )
    error: str | None = Field(default=None, description="Error message when success is false")
    error_code: str | None = Field(default=None, description="Machine-readable error code")
    error_type: str | None = Field(default=None, description="Exception or category name")
    operation: str | None = Field(
        default=None, description="Sub-operation when returned by error helper"
    )
    parameters: dict[str, Any] | None = Field(default=None, description="Echo of bad inputs")
    suggestions: list[str] | None = Field(default=None, description="Recovery hints")
    related_tools: list[str] | None = Field(default=None, description="Suggested follow-up tools")
    diagnostic: dict[str, Any] | None = Field(default=None, description="Debug context")
    execution_time_ms: int | None = None
    recommendations: list[str] | None = None


MANAGE_AUTHORS_OUTPUT_SCHEMA: dict[str, Any] = ManageAuthorsMCPOutput.model_json_schema()

# Type alias for docs / static analysis (not used as MCP root schema)
ManageAuthorsOutput = ManageAuthorsMCPOutput

# --- Input documentation helpers (referenced from manage_authors docstring) ---

OperationLiteral = Annotated[
    str,
    Field(
        description=(
            'Sub-command: "list" | "get" | "get_books" | "stats" | "by_letter". '
            "See tool docstring for required parameters per operation."
        ),
    ),
]

AuthorIdParam = Annotated[
    int,
    Field(
        description=(
            "Calibre database primary key for authors.id. Required when operation is "
            "'get' or 'get_books'. Obtain ids from operation='list' or library UI."
        ),
        ge=1,
    ),
]

PaginationOffset = Annotated[
    int,
    Field(
        ge=0,
        description=(
            "Skip this many rows before returning results. Use together with limit: "
            "page index is (offset // limit) + 1. If offset >= total matches, items may be empty."
        ),
    ),
]

PaginationLimit = Annotated[
    int,
    Field(
        ge=1,
        le=1000,
        description="Maximum rows to return for list/get_books (default 50).",
    ),
]
