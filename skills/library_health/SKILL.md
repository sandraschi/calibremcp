# Library Health

**Description:** Analyze Calibre library health: duplicate detection, missing metadata, orphaned records, format coverage, tag consistency, cover completeness, and integrity validation.

## Trigger Phrases

- "Check my library for issues"
- "Find duplicate books"
- "What books are missing covers?"
- "Validate my library integrity"
- "Clean up my metadata"
- "Show me library health report"
- "Find books with missing authors or tags"

## Tools

- `manage_analysis(operation="duplicates")` — Detect duplicate entries by title similarity + author match. Returns grouped duplicate candidates with merge suggestions.
- `manage_analysis(operation="health")` — Full library health report: total books, missing metadata count, format distribution, cover coverage, tag frequency.
- `manage_library_operations(operation="integrity_check")` — Database integrity scan: checks calibre database for orphaned records, broken format links, missing files.
- `manage_metadata(operation="show", book_id=...)` — Inspect individual book metadata for quality assessment.
- `manage_tags(operation="list")` — List all tags in use. Shows frequency; reveals typos and inconsistent capitalization.
- `manage_metadata(operation="update", book_id=..., field=..., value=...)` — Fix individual metadata issues.
- Bulk metadata tools — Apply fixes across multiple books at once.

## Workflow

1. **Duplicate sweep**: Run `manage_analysis(operation="duplicates")` first. Review grouped candidates. Merge or delete duplicates.
2. **Health report**: Run `manage_analysis(operation="health")` for an overview. Note missing covers, authors, or tags.
3. **Tag hygiene**: Run `manage_tags(operation="list")`. Look for variants: "sci-fi" vs "scifi" vs "science-fiction". Normalize via bulk metadata update.
4. **Format audit**: Health report shows format distribution (epub, mobi, pdf, azw3). Identify books missing your preferred format. Use Calibre conversion tools to fill gaps.
5. **Cover recovery**: Books missing covers: use `manage_metadata(operation="download_cover", book_id=...)` for each, or batch via agentic workflow.
6. **Integrity validation**: Run `manage_library_operations(operation="integrity_check")`. Fix any broken format links or dangling orphans.

## Example

"Check my library for duplicates and missing metadata." → `manage_analysis(operation="duplicates")` → merge confirmed dupes → `manage_analysis(operation="health")` → fix 12 missing authors → `manage_tags(operation="list")` → merge "sci-fi"/"scifi" → report results.
