"""
CalibreMCP Prompt Templates

Comprehensive prompt templates for CalibreMCP use cases.
These prompts are registered with FastMCP and appear in Claude Desktop and other MCP clients.
"""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompt templates with the FastMCP server."""
    
    # Reading Recommendations
    @mcp.prompt()
    def reading_recommendations() -> str:
        """What should I read next? Get personalized reading recommendations based on library, series progress, and reading habits. Austrian efficiency to eliminate decision paralysis."""
        return """What should I read next? Analyze my Calibre library collection, reading history, and current series progress to provide personalized reading recommendations. Use Austrian efficiency to eliminate decision paralysis - give me specific book suggestions with priority rankings and tell me exactly which book I should read right now. Include any incomplete series I should continue and books that match my interests."""

    # Library Organization
    @mcp.prompt()
    def library_organization() -> str:
        """Analyze library health and organization. Check for duplicates, inconsistent metadata, missing tags, and provide optimization recommendations."""
        return """Analyze my Calibre library health and organization. Check for duplicate books, inconsistent metadata, missing tags, and organizational issues. Provide specific recommendations for improving library structure and suggest actions to clean up and optimize my collection."""

    # Book Discovery
    @mcp.prompt()
    def book_discovery() -> str:
        """Discover unread books in your library. Find similar books, hidden gems, or books in genres you enjoy based on reading history."""
        return """Help me discover books in my library that I haven't read yet. Find books similar to [book title or author], or show me books in genres I enjoy. Use my reading history and preferences to suggest hidden gems in my collection that I might have overlooked."""

    # Series Management
    @mcp.prompt()
    def series_management() -> str:
        """Manage book series. Show incomplete series, missing volumes, reading order, and prioritize which series to complete."""
        return """Show me all incomplete series in my library. Identify which series I should continue reading, which ones are missing volumes, and provide a prioritized list of series to complete. Include reading order recommendations and highlight any series that are nearly complete."""

    # Metadata Cleanup
    @mcp.prompt()
    def metadata_cleanup() -> str:
        """Review and fix library metadata issues. Find missing information, inconsistent data, duplicate tags, and suggest bulk fixes."""
        return """Review my library metadata for issues. Find books with missing or incorrect information, inconsistent author names, duplicate tags, or incomplete series data. Provide a prioritized list of metadata fixes and suggest bulk operations to improve data quality."""

    # Tag Organization
    @mcp.prompt()
    def tag_organization() -> str:
        """Organize and consolidate tags. Find duplicates, unused tags, and suggest a clean tag hierarchy for better organization."""
        return """Analyze my tag usage and organization. Find duplicate or similar tags that should be merged, identify unused tags, and suggest a clean tag hierarchy. Help me consolidate tags for better organization and easier searching."""

    # Duplicate Detection
    @mcp.prompt()
    def duplicate_detection() -> str:
        """Find duplicate books in your library. Check for similar titles, same authors, or matching ISBNs with confidence scores."""
        return """Find duplicate books in my library. Check for books with similar titles, same authors, or matching ISBNs. Provide a list of potential duplicates with confidence scores and suggest which copies to keep or merge."""

    # Reading Statistics
    @mcp.prompt()
    def reading_statistics() -> str:
        """Show comprehensive reading statistics. Analyze reading patterns, favorite genres, authors, ratings, and reading trends."""
        return """Show me comprehensive reading statistics from my library. Analyze my reading patterns, favorite genres, most-read authors, average ratings, and reading trends. Provide insights into my reading habits and suggest areas to explore."""

    # Japanese Books
    @mcp.prompt()
    def japanese_books() -> str:
        """Organize Japanese books (manga, light novels, language learning). Categorize by series, identify reading order, find missing volumes."""
        return """Organize my Japanese books (manga, light novels, language learning materials). Categorize by series, identify reading order, find missing volumes, and provide recommendations for completing series. Use proper Japanese reading order conventions."""

    # IT Books
    @mcp.prompt()
    def it_books() -> str:
        """Curate IT and programming books. Organize by language, identify outdated books, suggest learning paths, and recommend next reads."""
        return """Analyze my IT and programming books. Organize by programming language, identify outdated books, suggest learning paths, and recommend which technical books to read next based on my current collection and skill development goals."""

    # Format Conversion
    @mcp.prompt()
    def format_conversion() -> str:
        """Convert books to different formats. Identify books needing conversion, suggest optimal formats for devices, manage formats efficiently."""
        return """Help me convert books to different formats. Identify books that need format conversion, suggest optimal formats for different devices, and help me manage my book formats efficiently. Check for books missing preferred formats."""

    # Library Search
    @mcp.prompt()
    def library_search() -> str:
        """Advanced library search with filters. Find books by date ranges, file sizes, formats, ratings, publishers, or custom combinations."""
        return """Help me search my library with advanced filters. Find books by specific criteria: publication date ranges, file sizes, formats, ratings, publishers, or custom combinations. Use boolean search operators and filters to find exactly what I'm looking for."""

    # Unread Priority
    @mcp.prompt()
    def unread_priority() -> str:
        """Create prioritized list of unread books. Use Austrian efficiency to rank by rating, series status, purchase date, and tags."""
        return """Create a prioritized list of unread books in my library. Use Austrian efficiency principles to rank books by rating, series status, purchase date, and tags. Eliminate decision paralysis by giving me a clear, prioritized reading queue."""

    # Library Health
    @mcp.prompt()
    def library_health() -> str:
        """Perform comprehensive library health check. Check for missing files, corrupted metadata, orphaned records, database integrity issues."""
        return """Perform a comprehensive health check of my Calibre library. Check for missing files, corrupted metadata, orphaned records, database integrity issues, and other problems. Provide a health score and prioritized list of issues to fix."""

    # Author Analysis
    @mcp.prompt()
    def author_analysis() -> str:
        """Analyze authors in your library. Show most-read authors, incomplete series, new authors to explore, and extensive collections."""
        return """Analyze authors in my library. Show me my most-read authors, authors with incomplete series, authors I haven't read yet, and suggest new authors to explore based on my reading preferences. Identify authors with extensive collections I might want to complete."""

    # Bulk Operations
    @mcp.prompt()
    def bulk_operations() -> str:
        """Perform bulk operations on your library. Update metadata, export books, convert formats, or apply tags to groups of books."""
        return """Help me perform bulk operations on my library. Update metadata for multiple books, export books in batches, convert formats in bulk, or apply tags to groups of books. Identify opportunities for efficient bulk management."""

    # Reading Goals
    @mcp.prompt()
    def reading_goals() -> str:
        """Set and track reading goals. Analyze reading pace, suggest realistic goals, track progress toward completing series or genres."""
        return """Help me set and track reading goals. Analyze my reading pace, suggest realistic goals, track progress toward completing series or reading specific genres, and provide motivation and recommendations to achieve my reading objectives."""

    # Book Comparison
    @mcp.prompt()
    def book_comparison() -> str:
        """Compare books in your library. Find similar books, compare editions, identify related series, or choose between books on same topic."""
        return """Compare books in my library. Find similar books, compare editions, identify related series, or help me choose between multiple books on the same topic. Use metadata, tags, and content analysis to provide intelligent comparisons."""

    # Library Export
    @mcp.prompt()
    def library_export() -> str:
        """Export books from your library. Export specific books, entire series, books by author or tag, or create backups with optimal formats."""
        return """Help me export books from my library. Export specific books, entire series, books by author or tag, or create backups. Suggest optimal export formats and help me organize exported files efficiently."""

    # Smart Collections
    @mcp.prompt()
    def smart_collections() -> str:
        """Create smart collections for your library. Set up dynamic collections based on tags, ratings, dates, or reading status that update automatically."""
        return """Create smart collections for my library. Set up dynamic collections based on criteria like tags, ratings, publication dates, or reading status. Help me organize books into logical groups that update automatically as my library changes."""

