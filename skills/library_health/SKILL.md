# Library Health

**Description:** Analyze Calibre library health: duplicates, missing metadata, orphaned records, tag consistency.

## Steps

1. Use prompt **library_health** or **library_organization**.
2. Tools: `manage_analysis` (operation=duplicates, health), `manage_library_operations` for integrity checks.
3. Review recommendations and apply fixes via `manage_metadata`, `manage_tags`, or bulk tools.

## Example

"Check my library for duplicates and missing metadata."
