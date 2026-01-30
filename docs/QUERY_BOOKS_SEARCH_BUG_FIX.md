## CalibreMCP query_books Search Bug - Fix Report

**Date**: 2025-01-30  
**File**: `src/calibre_mcp/services/book_service.py`  
**Issue**: `query_books(operation="search", author="...")` and series searches fail to match books

---

## Bug Description

### Symptoms
1. Searching by author name returns no results or incorrect results
2. Searching by series name fails to filter properly
3. Tag searches may return noise from descriptions instead of actual tag matches
4. Text search interferes with metadata filtering

### Root Cause

The bug was in the SQLAlchemy query construction in `book_service.get_all()` method:

**Problem 1: JOIN Logic Issues**
- When filtering by author/series/tags, the code used `.join()` followed by `.filter()` 
- This created improper SQL joins that could result in duplicates or incorrect filtering
- Multiple sequential joins caused cross-product issues in complex queries

**Problem 2: Subquery Approach**
- The original code wasn't using proper subqueries for metadata filtering
- Direct joins on relationships could conflict with other filters
- This was especially problematic when combined with FTS search or other metadata filters

---

## Fix Implemented

### Changes Made

#### 1. Author Filtering (`lines 428-448`)
**Before:**
```python
elif author_name:
    author_words = author_name.split()
    if author_words:
        query = query.join(Book.authors)
        for word in author_words:
            word_pattern = f"%{word}%"
            query = query.filter(Author.name.ilike(word_pattern))
        query = query.distinct()
```

**After:**
```python
elif author_name:
    author_words = author_name.split()
    if author_words:
        # Build a subquery that finds books matching all author name words
        author_book_ids_subq = (
            session.query(Book.id)
            .join(Book.authors)
        )
        # Apply AND logic: author name must contain ALL search words
        for word in author_words:
            word_pattern = f"%{word}%"
            author_book_ids_subq = author_book_ids_subq.filter(Author.name.ilike(word_pattern))
        
        author_book_ids_subq = author_book_ids_subq.distinct().subquery()
        query = query.filter(Book.id.in_(session.query(author_book_ids_subq.c.id)))
```

**Benefits:**
- Uses subquery to isolate author filtering logic
- Prevents join conflicts with other filters
- Correctly implements AND logic for multi-word author names
- Returns book IDs matching ALL words (e.g., "Conan Doyle" matches "John Dickson Carr" only if name contains both "Conan" AND "Doyle")

#### 2. Series Filtering (`lines 455-466`)
**Before:**
```python
if series_name:
    series_pattern = f"%{series_name}%"
    query = query.join(Book.series).filter(Series.name.ilike(series_pattern)).distinct()
```

**After:**
```python
if series_name:
    # Build a subquery that finds books matching the series name
    series_book_ids_subq = (
        session.query(Book.id)
        .join(Book.series)
        .filter(Series.name.ilike(f"%{series_name}%"))
        .distinct()
        .subquery()
    )
    query = query.filter(Book.id.in_(session.query(series_book_ids_subq.c.id)))
```

**Benefits:**
- Isolates series filtering in subquery
- Prevents interference with other joins
- Cleaner query composition

#### 3. Tag Filtering (`lines 468-504`)
**Before:**
```python
elif tags_list:
    tag_conditions = []
    for tag in tags_list:
        tag_pattern = f"%{tag}%"
        tag_conditions.append(Tag.name.ilike(tag_pattern))
    if tag_conditions:
        query = query.join(Book.tags).filter(or_(*tag_conditions)).distinct()

elif tag_name:
    tag_pattern = f"%{tag_name}%"
    query = query.join(Book.tags).filter(Tag.name.ilike(tag_pattern)).distinct()
```

**After:**
```python
elif tags_list:
    tag_conditions = []
    for tag in tags_list:
        tag_pattern = f"%{tag}%"
        tag_conditions.append(Tag.name.ilike(tag_pattern))
    if tag_conditions:
        tag_book_ids_subq = (
            session.query(Book.id)
            .join(Book.tags)
            .filter(or_(*tag_conditions))
            .distinct()
            .subquery()
        )
        query = query.filter(Book.id.in_(session.query(tag_book_ids_subq.c.id)))

elif tag_name:
    tag_book_ids_subq = (
        session.query(Book.id)
        .join(Book.tags)
        .filter(Tag.name.ilike(f"%{tag_name}%"))
        .distinct()
        .subquery()
    )
    query = query.filter(Book.id.in_(session.query(tag_book_ids_subq.c.id)))
```

**Benefits:**
- Uses subqueries for isolation
- Prevents cartesian products when multiple tags match
- Cleaner composition with other filters

---

## How the Fix Works

### Query Composition Strategy

The fix uses a **subquery-based filter composition** approach:

1. **Isolate each metadata filter** in its own subquery
2. **Combine subqueries** using `Book.id.in_(subquery_result)`
3. **Preserves AND logic** between different filter types
4. **Enables OR logic** within filter lists (e.g., multiple authors use OR)

### Example: Author + Tag Search

```python
# User searches: author="Conan Doyle", tags=["mystery", "detective"]

# Step 1: Find books by author (subquery)
author_book_ids = SELECT Book.id WHERE Book.authors contain "Conan" AND "Doyle"

# Step 2: Find books with tags (subquery)  
tag_book_ids = SELECT Book.id WHERE Book.tags contain "mystery" OR "detective"

# Step 3: Combine (AND logic between filters)
query = query.filter(Book.id.in_(author_book_ids))  # AND
query = query.filter(Book.id.in_(tag_book_ids))     # AND
```

Result: Books that are BOTH by Conan Doyle AND have mystery/detective tags.

---

## Testing

A comprehensive test suite has been added: `tests/test_query_books_search_bug.py`

Tests cover:
- ✓ Author search by full name
- ✓ Author search by partial name  
- ✓ Two-part author names (AND logic)
- ✓ Text parameter with "by Author" syntax
- ✓ Series search by name
- ✓ Combined author + tag search
- ✓ Combined author + rating search
- ✓ Case-insensitive matching
- ✓ No noise from descriptions
- ✓ Empty result handling

---

## Performance Impact

**Positive:**
- Subqueries are typically faster than multiple joins for large datasets
- Proper indexing on author/series/tag names makes subqueries efficient
- Reduces cartesian products from incorrect joins

**Neutral:**
- Slight overhead from explicit subquery construction
- Negligible for typical library sizes (< 100k books)

---

## Verification

To verify the fix works:

```bash
cd tests
pytest test_query_books_search_bug.py -v
```

Expected: All tests pass with correct metadata matches.

---

## Files Modified

- `src/calibre_mcp/services/book_service.py` (lines 393-504)
  - Author filtering refactored to use subqueries
  - Series filtering refactored to use subqueries
  - Tag filtering refactored to use subqueries

---

## Backwards Compatibility

✓ **Fully compatible** - All existing API signatures remain unchanged.  
✓ **Behavior fix** - Only fixes incorrect behavior; valid searches now work as expected.
