# Rating and Date Range Search Examples

## Query: "What five star books did we add lately in the japanese library?"

Here's how Claude would handle this query:

```python
# Step 1: Switch to the Japanese library
switch_result = switch_library(library_name="japanese")
if not switch_result["success"]:
    print(f"Error: {switch_result.get('message')}")
    # Could also list libraries to find the exact name
    libraries = list_libraries()
    print(f"Available libraries: {[lib['name'] for lib in libraries.get('libraries', [])]}")

# Step 2: Search for 5-star books added recently
from datetime import datetime, timedelta

# "Lately" = last 30 days
month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

results = search_books(
    rating=5,                    # Exactly 5 stars
    added_after=month_ago,       # Added after 30 days ago
    added_before=today,          # Added before today (inclusive)
    format_table=True            # Pretty table output with descriptions
)

print(f"Found {results['total']} five-star books added in the last month")
if results.get('table'):
    print(results['table'])
```

## Query: "Want a detective story with minimum 4 stars, locked room mystery"

This combines multiple filters - tag/genre, rating, and text search:

```python
# Option 1: Search by tag and rating (recommended)
results = search_books(
    tag="detective",             # Detective stories
    min_rating=4,                # Minimum 4 stars (4 or 5 stars)
    text="locked room",          # Contains "locked room" in content/metadata
    format_table=True
)

# Option 2: Search by multiple tags
results = search_books(
    tags=["detective", "mystery"],  # Books with either tag
    min_rating=4,                   # Minimum 4 stars
    text="locked room",             # Contains "locked room"
    format_table=True
)

# Option 3: More specific tag search
results = search_books(
    tag="locked room mystery",   # If you have this as a specific tag
    min_rating=4,
    format_table=True
)

# Option 4: Text search across all fields
results = search_books(
    text="detective locked room mystery",  # Searches title, author, tags, comments
    min_rating=4,
    format_table=True
)
```

**Best Practice**: Use `tag="detective"` for genre filtering (more precise) + `text="locked room"` for content search + `min_rating=4` for quality filter.

## Common Rating and Date Queries

### 5-Star Books Added This Week

```python
from datetime import datetime, timedelta
week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

results = search_books(
    rating=5,
    added_after=week_ago,
    added_before=today,
    format_table=True
)
```

### Highly Rated Books (4-5 Stars) Added Recently

```python
from datetime import datetime, timedelta
month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

results = search_books(
    min_rating=4,        # 4 or 5 stars
    added_after=month_ago,
    format_table=True
)
```

### Books in Rating Range

```python
# Find books rated 3-4 stars
results = search_books(
    min_rating=3,
    max_rating=4,
    format_table=True
)
```

### Books Published in a Specific Year

```python
# Books published in 2023
results = search_books(
    pubdate_start="2023-01-01",
    pubdate_end="2023-12-31",
    format_table=True
)
```

### Books Added Between Two Dates

```python
# Books added in January 2024
results = search_books(
    added_after="2024-01-01",
    added_before="2024-01-31",
    format_table=True
)
```

### Combine Multiple Filters

```python
from datetime import datetime, timedelta
month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# Highly rated mystery books added recently
results = search_books(
    min_rating=4,
    tag="mystery",
    added_after=month_ago,
    format_table=True
)

# 5-star books by specific author added this year
results = search_books(
    rating=5,
    author="Haruki Murakami",
    added_after="2024-01-01",
    format_table=True
)

# Quality detective novels (4+ stars) published in the last 5 years
results = search_books(
    min_rating=4,
    tag="detective",
    pubdate_start="2019-01-01",
    format_table=True
)
```

## Library Switching

Always switch libraries before searching if you need a specific library:

```python
# List available libraries
libraries = list_libraries()
print("Available libraries:")
for lib in libraries.get('libraries', []):
    print(f"  - {lib['name']}: {lib.get('book_count', 0)} books")

# Switch to specific library
result = switch_library(library_name="japanese")
if result["success"]:
    print(f"Switched to: {result['library_name']}")
    # Now all searches operate on this library
else:
    print(f"Failed to switch: {result.get('message')}")
```

## Date Format

All dates use `YYYY-MM-DD` format:
- ✅ `"2024-01-15"`
- ✅ `"2023-12-31"`
- ❌ `"01/15/2024"` (wrong format)
- ❌ `"January 15, 2024"` (wrong format)

## Relative Dates

To calculate relative dates:

```python
from datetime import datetime, timedelta

# Last week
week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# Last month
month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# Last 3 months
three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

# Today
today = datetime.now().strftime("%Y-%m-%d")

# This year
year_start = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")
```

## Why `min_rating` is Important

`min_rating` is **crucial** for finding quality books! Here's why:

1. **Quality Filter**: Ensures you only get books rated 4+ or 5+ stars
2. **Time Saver**: Filters out lower-rated books automatically
3. **Combines Well**: Works perfectly with tags, genres, and text search
4. **Flexible**: Use with `max_rating` for rating ranges (e.g., 3-4 stars)

**Common Use Cases:**
- `min_rating=4` - Only highly-rated books (most common)
- `min_rating=5` - Only the best books (top tier)
- `min_rating=3, max_rating=4` - Mid-range quality books
- `rating=5` - Exactly 5 stars (most selective)

## Real-World Examples

### "Find me a great detective novel"
```python
search_books(tag="detective", min_rating=4, format_table=True)
```

### "What's the best sci-fi book I added last month?"
```python
from datetime import datetime, timedelta
month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
search_books(
    tag="science fiction",
    rating=5,
    added_after=month_ago,
    format_table=True
)
```

### "Show me quality historical fiction from 2023"
```python
search_books(
    tag="historical fiction",
    min_rating=4,
    pubdate_start="2023-01-01",
    pubdate_end="2023-12-31",
    format_table=True
)
```
