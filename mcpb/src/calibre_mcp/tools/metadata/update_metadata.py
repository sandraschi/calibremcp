"""Tool for updating book metadata in the Calibre library."""

from pydantic import BaseModel, Field

try:
    from fastmcp import MCPTool, Param
except ImportError:
    from ..compat import MCPTool, Param


class MetadataUpdate(BaseModel):
    """Model for metadata updates."""

    title: str | None = None
    authors: list[str] | None = None
    tags: list[str] | None = None
    series: str | None = None
    series_index: float | None = None
    publisher: str | None = None
    published_date: str | None = None
    description: str | None = None
    identifiers: dict[str, str] | None = None
    languages: list[str] | None = None
    rating: int | None = Field(None, ge=0, le=5)
    cover_path: str | None = None


class UpdateMetadataTool(MCPTool):
    """Update metadata for books in the Calibre library."""

    name = "update_metadata"
    description = "Update metadata for books in the Calibre library"
    parameters = [
        Param("book_ids", list[int | str], "List of book IDs to update"),
        Param("metadata", dict, "Metadata fields to update"),
        Param("library_path", str, "Path to the Calibre library", required=False),
        Param("update_cover", bool, "Whether to update the book cover", default=True),
    ]

    async def _run(
        self,
        book_ids: list[int | str],
        metadata: dict,
        library_path: str | None = None,
        update_cover: bool = True,
    ) -> dict:
        """Update metadata for the specified books."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        results = {"updated": [], "failed": []}

        # Validate and parse metadata
        try:
            update_data = MetadataUpdate(**metadata).dict(exclude_none=True)
        except Exception as e:
            return {"error": f"Invalid metadata format: {str(e)}"}

        for book_id in book_ids:
            try:
                # Get current metadata
                current_meta = await storage.get_metadata(book_id)
                if not current_meta:
                    results["failed"].append({"book_id": book_id, "error": "Book not found"})
                    continue

                # Update metadata
                updated_meta = current_meta.copy(update=update_data)

                # Save updated metadata
                await storage.update_metadata(book_id, updated_meta)

                # Update cover if specified
                if update_cover and update_data.get("cover_path"):
                    await storage.update_cover(book_id, update_data["cover_path"])

                results["updated"].append({"book_id": book_id, "title": updated_meta.title})

            except Exception as e:
                results["failed"].append({"book_id": book_id, "error": str(e)})

        return results
