# Tag Weeding Guide

## Overview

Tag weeding helps maintain a clean and organized tag structure by:
- Finding duplicate/similar tags
- Merging duplicate tags
- Removing unused tags
- Normalizing tag names

## Complete Tag Weeding Workflow

### Step 1: Get Tag Statistics

```python
# See overall tag health
stats = get_tag_statistics()
print(f"Total tags: {stats['total_tags']}")
print(f"Unused tags: {stats['unused_tags_count']}")
print(f"Top tags: {stats['top_tags'][:5]}")
```

### Step 2: Find Duplicate Tags

```python
# Find similar tags (default: 80% similarity threshold)
duplicates = find_duplicate_tags()

# Review each duplicate group
for group in duplicates['duplicate_groups']:
    print(f"Similar tags: {[t['name'] for t in group['tags']]}")
    print(f"  Suggested name: {group['suggested_name']}")
    print(f"  Total books: {group['total_books']}")
```

**Adjust similarity threshold:**
```python
# More strict (only very similar - 90%+)
duplicates = find_duplicate_tags(similarity_threshold=0.9)

# Less strict (catch more variations - 70%+)
duplicates = find_duplicate_tags(similarity_threshold=0.7)
```

### Step 3: Merge Duplicate Tags

```python
# Merge duplicate tags into the most popular one
# Example: Merge "scifi" and "science fiction" into "sci-fi"

# First, find the target tag (most popular)
target_tag_id = 1  # The "sci-fi" tag (most books)
source_tag_ids = [2, 3]  # The "scifi" and "science fiction" tags

result = merge_tags(
    source_tag_ids=source_tag_ids,
    target_tag_id=target_tag_id
)

print(f"Merged {len(result['merged_tags'])} tags into {result['target_tag']['name']}")
print(f"Affected {result['books_affected']} books")
```

### Step 4: Find and Delete Unused Tags

```python
# First, review unused tags
unused = get_unused_tags()
print(f"Found {unused['count']} unused tags:")
for tag in unused['unused_tags'][:10]:  # Show first 10
    print(f"  - {tag['name']}")

# Then delete them (safe - they're not used by any books)
result = delete_unused_tags()
print(f"Deleted {result['deleted_count']} unused tags")
```

### Step 5: List and Review Tags

```python
# List all tags sorted by usage
all_tags = list_tags(
    sort_by="book_count",
    sort_order="desc",
    limit=50
)

# Find tags with specific patterns
mystery_tags = list_tags(search="mystery")

# Find rarely used tags (1-5 books)
rare_tags = list_tags(
    min_book_count=1,
    max_book_count=5,
    sort_by="book_count"
)
```

## Tag CRUD Operations

### Create Tags

```python
# Create a new tag (auto-normalizes name)
result = create_tag(name="locked room mystery")
# Returns: {"id": 123, "name": "Locked Room Mystery", "book_count": 0}
```

### Update Tags (Rename)

```python
# Rename a tag
result = update_tag(tag_id=123, name="detective fiction")
# All books with the old tag now have the new tag name
```

### Delete Tags

```python
# Delete a tag (removes it from all books)
result = delete_tag(tag_id=123)
# Tag is removed from all books and deleted
```

### Get Tag Details

```python
# Get by ID
tag = get_tag(tag_id=123)

# Get by name
tag = get_tag(tag_name="mystery")
```

## Advanced Filtering

### Find Popular Tags

```python
# Tags used by 20+ books
popular = list_tags(
    min_book_count=20,
    sort_by="book_count",
    sort_order="desc"
)
```

### Find Orphaned Tags

```python
# Tags not assigned to any books
orphaned = list_tags(unused_only=True)
```

### Search Tags

```python
# Search for tags containing "detective"
detective_tags = list_tags(search="detective")

# Case-insensitive partial match
mystery_tags = list_tags(search="myst")
```

## Example: Complete Tag Cleanup

```python
# 1. Get statistics
stats = get_tag_statistics()
print(f"Starting cleanup: {stats['total_tags']} tags, {stats['unused_tags_count']} unused")

# 2. Find duplicates
duplicates = find_duplicate_tags(similarity_threshold=0.8)
print(f"Found {duplicates['total_duplicates']} duplicate groups")

# 3. Merge duplicates (example - do this for each group)
for group in duplicates['duplicate_groups']:
    tags = group['tags']
    if len(tags) > 1:
        target = tags[0]  # Most popular
        sources = [t['id'] for t in tags[1:]]
        merge_tags(source_tag_ids=sources, target_tag_id=target['id'])
        print(f"Merged {len(sources)} tags into '{target['name']}'")

# 4. Delete unused tags
unused = get_unused_tags()
if unused['count'] > 0:
    result = delete_unused_tags()
    print(f"Deleted {result['deleted_count']} unused tags")

# 5. Final statistics
final_stats = get_tag_statistics()
print(f"After cleanup: {final_stats['total_tags']} tags")
```

## Tag Normalization

Tags are automatically normalized when created or updated:
- Whitespace trimmed
- Title case applied (first letter of each word capitalized)

Example:
- Input: `"locked room mystery"` → Output: `"Locked Room Mystery"`
- Input: `"  sci-fi  "` → Output: `"Sci-Fi"`

## Best Practices

1. **Regular Weeding**: Run `find_duplicate_tags()` monthly
2. **Review Before Merging**: Always review duplicate groups before merging
3. **Keep Popular Tags**: When merging, keep the tag used by most books
4. **Clean Unused Tags**: Periodically delete unused tags
5. **Consistent Naming**: Use consistent tag naming conventions

## Tools Available

- `list_tags()` - List all tags with filtering
- `get_tag()` - Get tag by ID or name
- `create_tag()` - Create a new tag
- `update_tag()` - Rename a tag
- `delete_tag()` - Delete a tag
- `find_duplicate_tags()` - Find similar/duplicate tags
- `merge_tags()` - Merge multiple tags into one
- `get_unused_tags()` - List unused tags
- `delete_unused_tags()` - Delete all unused tags
- `get_tag_statistics()` - Get tag statistics

