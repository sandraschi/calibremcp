"""Advanced library organization tools for CalibreMCP."""

from typing import Dict, List, Optional, Any, Union
import os
import re
import shutil
import logging
from datetime import datetime
from collections import defaultdict
import string
import fnmatch

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool
from pydantic import BaseModel, Field


# Models
class OrganizationRule(BaseModel):
    """Rule for organizing library content."""

    name: str
    enabled: bool = True
    priority: int = 0
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)

    def matches(self, book: Dict) -> bool:
        """Check if a book matches this rule's conditions."""
        if not self.enabled:
            return False

        for condition in self.conditions:
            field = condition.get("field")
            operator = condition.get("operator", "equals")
            value = condition.get("value")

            # Get the field value from the book
            book_value = book.get(field)

            # Handle nested fields (e.g., 'identifiers.isbn')
            if "." in field:
                parts = field.split(".")
                book_value = book
                for part in parts:
                    if isinstance(book_value, dict) and part in book_value:
                        book_value = book_value[part]
                    else:
                        book_value = None
                        break

            # Handle different operators
            if operator == "equals":
                if book_value != value:
                    return False
            elif operator == "not_equals":
                if book_value == value:
                    return False
            elif operator == "contains":
                if not (isinstance(book_value, (str, list)) and value in book_value):
                    return False
            elif operator == "not_contains":
                if isinstance(book_value, (str, list)) and value in book_value:
                    return False
            elif operator == "starts_with":
                if not (isinstance(book_value, str) and book_value.startswith(value)):
                    return False
            elif operator == "ends_with":
                if not (isinstance(book_value, str) and book_value.endswith(value)):
                    return False
            elif operator == "matches_regex":
                if not (isinstance(book_value, str) and re.search(value, book_value)):
                    return False
            elif operator == "greater_than":
                if not (isinstance(book_value, (int, float)) and book_value > value):
                    return False
            elif operator == "less_than":
                if not (isinstance(book_value, (int, float)) and book_value < value):
                    return False
            elif operator == "is_set":
                if book_value is None or book_value == "":
                    return False
            elif operator == "is_not_set":
                if book_value is not None and book_value != "":
                    return False
            # Add more operators as needed

        return True


class OrganizationPlan(BaseModel):
    """Plan for organizing the library."""

    name: str
    description: Optional[str] = None
    rules: List[OrganizationRule] = Field(default_factory=list)
    dry_run: bool = True
    backup_before: bool = True

    def add_rule(self, rule: OrganizationRule):
        """Add a rule to this plan."""
        self.rules.append(rule)
        # Sort rules by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def get_matching_rules(self, book: Dict) -> List[OrganizationRule]:
        """Get all rules that match the given book."""
        return [rule for rule in self.rules if rule.matches(book)]


class OrganizationResult(BaseModel):
    """Result of an organization operation."""

    book_id: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    success: bool = True


# Main tool
class LibraryOrganizer(MCPTool):
    """Advanced library organization tools for CalibreMCP."""

    name = "library_organizer"
    description = "Advanced tools for organizing and managing library content"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self._saved_plans: Dict[str, OrganizationPlan] = {}

    # Organization Methods
    async def organize_library(
        self,
        library_path: str,
        plan: Optional[Union[Dict, str]] = None,
        book_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Organize the library according to the specified plan.

        Args:
            library_path: Path to the library
            plan: Either a plan name (str) or a plan definition (dict)
            book_ids: Optional list of book IDs to process (all books if None)

        Returns:
            Dictionary with organization results
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)

        # Load or create the organization plan
        if isinstance(plan, str):
            # Load plan by name
            if plan not in self._saved_plans:
                return {"error": f"No saved plan named '{plan}'", "success": False}
            org_plan = self._saved_plans[plan]
        elif isinstance(plan, dict):
            # Create plan from dict
            org_plan = OrganizationPlan(**plan)
        else:
            # Use default plan
            org_plan = self._create_default_plan()

        # Get books to process
        if book_ids is None:
            books = await storage.get_all_books()
            book_ids = [book["id"] for book in books if "id" in book]

        results = []

        # Create backup if requested
        if org_plan.backup_before and not org_plan.dry_run:
            backup_result = await self._create_backup(library_path, "pre_organization")
            if not backup_result.get("success", False):
                return {
                    "error": f"Failed to create backup: {backup_result.get('error', 'Unknown error')}",
                    "success": False,
                }

        # Process each book
        for book_id in book_ids:
            result = OrganizationResult(book_id=book_id)

            try:
                book = await storage.get_book(book_id)
                if not book:
                    result.errors.append("Book not found")
                    result.success = False
                    results.append(result.dict())
                    continue

                # Get matching rules
                matching_rules = org_plan.get_matching_rules(book)
                if not matching_rules:
                    result.actions.append({"action": "skip", "reason": "No matching rules"})
                    results.append(result.dict())
                    continue

                # Apply each matching rule
                for rule in matching_rules:
                    for action in rule.actions:
                        action_type = action.get("type")
                        action_params = action.get("params", {})

                        try:
                            action_result = await self._apply_action(
                                storage, book, action_type, action_params, org_plan.dry_run
                            )
                            result.actions.append(
                                {
                                    "rule": rule.name,
                                    "action": action_type,
                                    "params": action_params,
                                    "result": action_result,
                                }
                            )

                            # Update the book with any changes made by the action
                            if action_result.get("updated_book"):
                                book = action_result["updated_book"]

                        except Exception as e:
                            error_msg = f"Error applying action {action_type}: {str(e)}"
                            self.logger.error(error_msg, exc_info=True)
                            result.errors.append(error_msg)
                            result.success = False

                # Save changes if not in dry run mode
                if (
                    result.success
                    and not org_plan.dry_run
                    and any(a.get("result", {}).get("modified", False) for a in result.actions)
                ):
                    await storage.update_book(book_id, book)

            except Exception as e:
                error_msg = f"Error processing book {book_id}: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                result.errors.append(error_msg)
                result.success = False

            results.append(result.dict())

        return {
            "success": True,
            "plan": org_plan.dict(),
            "results": results,
            "total_books": len(results),
            "books_modified": sum(
                1
                for r in results
                if any(a.get("result", {}).get("modified", False) for a in r.get("actions", []))
            ),
            "dry_run": org_plan.dry_run,
        }

    async def save_organization_plan(self, plan: Dict) -> Dict:
        """Save an organization plan for future use."""
        try:
            org_plan = OrganizationPlan(**plan)
            self._saved_plans[org_plan.name] = org_plan
            return {"success": True, "plan_name": org_plan.name}
        except Exception as e:
            return {"error": f"Invalid plan: {str(e)}", "success": False}

    async def get_organization_plans(self) -> Dict:
        """Get all saved organization plans."""
        return {
            "success": True,
            "plans": [
                {"name": p.name, "description": p.description} for p in self._saved_plans.values()
            ],
        }

    async def get_organization_plan(self, name: str) -> Dict:
        """Get a specific organization plan by name."""
        if name not in self._saved_plans:
            return {"error": f"No plan named '{name}' found", "success": False}

        return {"success": True, "plan": self._saved_plans[name].dict()}

    async def delete_organization_plan(self, name: str) -> Dict:
        """Delete a saved organization plan."""
        if name in self._saved_plans:
            del self._saved_plans[name]
            return {"success": True, "message": f"Plan '{name}' deleted"}
        else:
            return {"error": f"No plan named '{name}' found", "success": False}

    # File Organization
    async def organize_files(
        self,
        library_path: str,
        pattern: str,
        target_dir: str,
        create_subdirs: bool = True,
        dry_run: bool = True,
    ) -> Dict:
        """
        Organize files in the library based on a pattern.

        Args:
            library_path: Path to the library
            pattern: Glob pattern to match files (e.g., '*.epub', '**/*.pdf')
            target_dir: Base directory to move files to
            create_subdirs: Whether to create subdirectories based on file metadata
            dry_run: If True, only show what would be done without making changes

        Returns:
            Dictionary with results of the operation
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        books = await storage.get_all_books()

        results = {
            "success": True,
            "files_processed": 0,
            "files_moved": 0,
            "errors": [],
            "operations": [],
        }

        # Ensure target directory exists
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)

        # Process each book
        for book in books:
            if "files" not in book:
                continue

            for fmt, file_info in book["files"].items():
                if "path" not in file_info:
                    continue

                file_path = file_info["path"]
                file_name = os.path.basename(file_path)

                # Check if file matches the pattern
                if not fnmatch.fnmatch(file_name, pattern):
                    continue

                results["files_processed"] += 1

                try:
                    # Determine target path
                    if create_subdirs:
                        # Create subdirectory structure based on metadata
                        # Example: {author}/{series}/{series_index} - {title}.{ext}
                        author = self._sanitize_filename(book.get("authors", ["Unknown"])[0])
                        series = self._sanitize_filename(book.get("series", "Unknown"))
                        series_index = book.get("series_index", 0)
                        title = self._sanitize_filename(book.get("title", "Unknown"))

                        # Create subdirectory path
                        subdir = os.path.join(target_dir, author, series)
                        new_filename = f"{series_index:03d} - {title}.{fmt.lower()}"
                        new_path = os.path.join(subdir, new_filename)
                    else:
                        # Just use the original filename in the target directory
                        new_path = os.path.join(target_dir, file_name)

                    # Check if this would be a move or copy
                    if os.path.normpath(file_path) == os.path.normpath(new_path):
                        results["operations"].append(
                            {
                                "file": file_path,
                                "action": "skip",
                                "reason": "Source and destination are the same",
                            }
                        )
                        continue

                    # Record the operation
                    op = {
                        "file": file_path,
                        "new_path": new_path,
                        "action": "move" if not dry_run else "would_move",
                    }
                    results["operations"].append(op)

                    # Perform the actual move if not in dry run mode
                    if not dry_run:
                        # Create target directory if it doesn't exist
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)

                        # Move the file
                        shutil.move(file_path, new_path)

                        # Update the book's file path in the database
                        file_info["path"] = new_path
                        await storage.update_book(book["id"], book)

                        results["files_moved"] += 1

                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    results["errors"].append(error_msg)
                    results["success"] = False

        return results

    # Tag Management
    async def clean_tags(
        self,
        library_path: str,
        book_ids: Optional[List[str]] = None,
        merge_similar: bool = True,
        min_length: int = 2,
        max_length: int = 50,
        remove_empty: bool = True,
        dry_run: bool = True,
    ) -> Dict:
        """
        Clean and standardize tags across the library.

        Args:
            library_path: Path to the library
            book_ids: Optional list of book IDs to process (all books if None)
            merge_similar: Whether to merge similar tags (e.g., 'sci-fi' and 'scifi')
            min_length: Minimum tag length (shorter tags will be removed)
            max_length: Maximum tag length (longer tags will be truncated)
            remove_empty: Whether to remove empty tags
            dry_run: If True, only show what would be changed

        Returns:
            Dictionary with results of the operation
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)

        if book_ids is None:
            books = await storage.get_all_books()
            book_ids = [book["id"] for book in books if "id" in book]

        results = {
            "success": True,
            "books_processed": 0,
            "books_modified": 0,
            "tags_removed": 0,
            "tags_modified": 0,
            "errors": [],
            "changes": [],
        }

        # Build a tag frequency map if we're merging similar tags
        if merge_similar:
            tag_freq = defaultdict(int)
            all_books = await storage.get_all_books()
            for book in all_books:
                if "tags" in book and book["tags"]:
                    for tag in book["tags"]:
                        tag_freq[tag.lower()] += 1

            # Find similar tags
            similar_tags = self._find_similar_tags(list(tag_freq.keys()))
        else:
            similar_tags = {}

        # Process each book
        for book_id in book_ids:
            try:
                book = await storage.get_book(book_id)
                if not book or "tags" not in book or not book["tags"]:
                    continue

                results["books_processed"] += 1
                original_tags = book["tags"].copy()
                new_tags = []

                # Process each tag
                for tag in book["tags"]:
                    modified = False

                    # Skip empty tags if requested
                    if remove_empty and (not tag or not tag.strip()):
                        results["tags_removed"] += 1
                        modified = True
                        continue

                    # Check length constraints
                    if len(tag) < min_length or len(tag) > max_length:
                        results["tags_removed"] += 1
                        modified = True
                        continue

                    # Normalize the tag
                    normalized = self._normalize_tag(tag)

                    # Check for similar tags to merge
                    if merge_similar and normalized.lower() in similar_tags:
                        normalized = similar_tags[normalized.lower()]
                        modified = modified or (normalized != tag)

                    # Add to new tags if not a duplicate
                    if normalized and normalized not in new_tags:
                        new_tags.append(normalized)

                    # Track changes
                    if modified:
                        results["tags_modified"] += 1

                # Check if tags were modified
                if set(original_tags) != set(new_tags):
                    book_changes = {
                        "book_id": book_id,
                        "original_tags": original_tags,
                        "new_tags": new_tags,
                        "modified": True,
                    }
                    results["changes"].append(book_changes)

                    if not dry_run:
                        book["tags"] = new_tags
                        await storage.update_book(book_id, book)
                        results["books_modified"] += 1

            except Exception as e:
                error_msg = f"Error processing book {book_id}: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                results["errors"].append(error_msg)
                results["success"] = False

        return results

    # Helper Methods
    async def _apply_action(
        self, storage, book: Dict, action_type: str, params: Dict, dry_run: bool = True
    ) -> Dict:
        """Apply an organization action to a book."""
        result = {"modified": False}

        if action_type == "add_tag":
            tag = params.get("tag")
            if tag and "tags" in book and tag not in book["tags"]:
                result["modified"] = True
                if not dry_run:
                    book["tags"].append(tag)
                result["message"] = f"Added tag: {tag}"

        elif action_type == "remove_tag":
            tag = params.get("tag")
            if tag and "tags" in book and tag in book["tags"]:
                result["modified"] = True
                if not dry_run:
                    book["tags"].remove(tag)
                result["message"] = f"Removed tag: {tag}"

        elif action_type == "set_field":
            field = params.get("field")
            value = params.get("value")

            if field and field in book and book[field] != value:
                result["modified"] = True
                if not dry_run:
                    book[field] = value
                result["message"] = f"Updated {field}"

        elif action_type == "move_to_series":
            series = params.get("series")
            index = params.get("index")

            if series:
                result["modified"] = True
                if not dry_run:
                    book["series"] = series
                    if index is not None:
                        book["series_index"] = float(index)
                result["message"] = f"Moved to series: {series} ({index if index else 'no index'})"

        elif action_type == "export":
            # Export the book to a different format
            # This is a placeholder - actual implementation would depend on calibre's conversion tools
            result["message"] = "Export action would be performed"
            result["modified"] = False  # Export doesn't modify the book

        else:
            result["error"] = f"Unknown action type: {action_type}"
            result["success"] = False

        result["updated_book"] = book
        return result

    def _create_default_plan(self) -> OrganizationPlan:
        """Create a default organization plan."""
        plan = OrganizationPlan(
            name="default",
            description="Default organization plan",
            dry_run=True,
            backup_before=True,
        )

        # Example rule: Add a "To Read" tag to books without a read status
        plan.add_rule(
            OrganizationRule(
                name="tag_unread_books",
                enabled=True,
                priority=10,
                conditions=[
                    {"field": "tags", "operator": "not_contains", "value": "read"},
                    {"field": "tags", "operator": "not_contains", "value": "to-read"},
                ],
                actions=[{"type": "add_tag", "params": {"tag": "to-read"}}],
            )
        )

        return plan

    async def _create_backup(self, library_path: str, suffix: str = "") -> Dict:
        """Create a backup of the library."""
        # This is a simplified version - in a real implementation, you might want to use
        # the backup functionality from extended_library_ops.py
        backup_dir = os.path.join(library_path, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{suffix}".strip("_") if suffix else f"backup_{timestamp}"
        backup_path = os.path.join(backup_dir, f"{backup_name}.zip")

        try:
            import zipfile

            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add metadata.db
                metadata_db = os.path.join(library_path, "metadata.db")
                if os.path.exists(metadata_db):
                    zipf.write(metadata_db, os.path.basename(metadata_db))

                # Add covers directory if it exists
                covers_dir = os.path.join(library_path, "covers")
                if os.path.isdir(covers_dir):
                    for root, _, files in os.walk(covers_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, library_path)
                            zipf.write(file_path, arcname)

            return {"success": True, "backup_path": backup_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _find_similar_tags(self, tags: List[str], threshold: float = 0.8) -> Dict[str, str]:
        """Find similar tags that should be merged."""
        from difflib import SequenceMatcher

        # Convert to lowercase and remove duplicates
        unique_tags = list({t.lower(): t for t in tags}.items())  # Preserve original case
        similar = {}

        # Compare each pair of tags
        for i, (tag1_lower, tag1_orig) in enumerate(unique_tags):
            for tag2_lower, tag2_orig in unique_tags[i + 1 :]:
                # Skip if one is a substring of the other (handled separately)
                if tag1_lower in tag2_lower or tag2_lower in tag1_lower:
                    continue

                # Calculate similarity
                ratio = SequenceMatcher(None, tag1_lower, tag2_lower).ratio()

                if ratio >= threshold:
                    # Prefer the more common tag (or the shorter one if equal)
                    if len(tag1_lower) <= len(tag2_lower):
                        similar[tag2_lower] = tag1_orig
                    else:
                        similar[tag1_lower] = tag2_orig

        # Also handle substrings (e.g., 'sci-fi' and 'scifi')
        for tag1_lower, tag1_orig in unique_tags:
            for tag2_lower, tag2_orig in unique_tags:
                if tag1_lower == tag2_lower:
                    continue

                if tag1_lower in tag2_lower and tag2_lower not in similar:
                    # Prefer the shorter tag (e.g., 'scifi' over 'science fiction')
                    if len(tag1_lower) <= len(tag2_lower):
                        similar[tag2_lower] = tag1_orig
                    else:
                        similar[tag1_lower] = tag2_orig

        return similar

    def _normalize_tag(self, tag: str) -> str:
        """Normalize a tag by standardizing case and removing extra whitespace."""
        if not tag:
            return tag

        # Trim whitespace
        tag = tag.strip()

        # Convert to title case (first letter of each word capitalized)
        tag = " ".join(word.capitalize() for word in tag.split())

        return tag

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be used as a filename."""
        if not filename:
            return ""

        # Replace invalid characters with underscores
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        sanitized = "".join(c if c in valid_chars else "_" for c in filename)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(". ")

        # Replace multiple spaces/underscores with a single underscore
        sanitized = re.sub(r"[ _]+", "_", sanitized)

        return sanitized
