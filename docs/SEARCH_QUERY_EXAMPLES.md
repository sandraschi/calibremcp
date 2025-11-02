# Search Query Examples - How Claude Calls search_books

**Actual parameter examples showing how queries are constructed**

---

## 📋 Basic Tag Searches

### **Single Tag (Multi-word tag like "crime novel")**

```python
# Claude calls:
search_books(tag="crime novel")

# SQL Generated:
# SELECT * FROM books
# JOIN books_tags_link ON books.id = books_tags_link.book
# JOIN tags ON books_tags_link.tag = tags.id
# WHERE tags.name ILIKE '%crime novel%'
# DISTINCT
```

**Result**: Books with tag containing "crime novel" (case-insensitive partial match)

---

### **Multiple Tags (OR logic within list)**

```python
# Claude calls:
search_books(tags=["crime", "thriller", "mystery"])

# SQL Generated:
# SELECT * FROM books
# JOIN books_tags_link ON books.id = books_tags_link.book
# JOIN tags ON books_tags_link.tag = tags.id
# WHERE (
#     tags.name ILIKE '%crime%' OR
#     tags.name ILIKE '%thriller%' OR
#     tags.name ILIKE '%mystery%'
# )
# DISTINCT
```

**Result**: Books with **ANY** of these tags (crime OR thriller OR mystery)

---

## 🔍 Complex Combinations

### **Tag AND Author (different filter types = AND)**

```python
# Claude calls:
search_books(tag="crime novel", author="Conan Doyle")

# SQL Generated:
# SELECT * FROM books
# JOIN books_tags_link ON books.id = books_tags_link.book
# JOIN tags ON books_tags_link.tag = tags.id
# JOIN books_authors_link ON books.id = books_authors_link.book
# JOIN authors ON books_authors_link.author = authors.id
# WHERE 
#     tags.name ILIKE '%crime novel%'
#     AND authors.name ILIKE '%Conan Doyle%'
# DISTINCT
```

**Result**: Books with tag "crime novel" **AND** author "Conan Doyle"

---

### **Multiple Tags (OR) AND Author (AND logic between filter types)**

```python
# Claude calls:
search_books(tags=["crime", "thriller"], author="Mick Herron")

# SQL Generated:
# SELECT * FROM books
# JOIN books_tags_link ON books.id = books_tags_link.book
# JOIN tags ON books_tags_link.tag = tags.id
# JOIN books_authors_link ON books.id = books_authors_link.book
# JOIN authors ON books_authors_link.author = authors.id
# WHERE 
#     (tags.name ILIKE '%crime%' OR tags.name ILIKE '%thriller%')
#     AND authors.name ILIKE '%Mick Herron%'
# DISTINCT
```

**Result**: Books with **(crime tag OR thriller tag) AND Mick Herron as author**

---

### **Tag AND Rating AND Exclude Tags (NOT logic)**

```python
# Claude calls:
search_books(tag="crime novel", min_rating=4, exclude_tags=["young adult"])

# SQL Generated:
# Step 1: Find books with tag and rating
# SELECT * FROM books
# JOIN books_tags_link ON books.id = books_tags_link.book
# JOIN tags ON books_tags_link.tag = tags.id
# JOIN ratings ON books.id = ratings.book
# WHERE 
#     tags.name ILIKE '%crime novel%'
#     AND ratings.rating >= 4

# Step 2: Exclude books with excluded tags (subquery)
# SELECT book_id FROM books_tags_link
# JOIN tags ON books_tags_link.tag = tags.id
# WHERE tags.name ILIKE '%young adult%'

# Step 3: Final query excludes books from step 2
# ... WHERE books.id NOT IN (excluded_book_ids)
```

**Result**: Books with tag "crime novel" **AND** rating >= 4 **AND NOT** tag "young adult"

---

### **Multiple Authors (OR) AND Multiple Tags (OR) AND Exclude**

```python
# Claude calls:
search_books(
    authors=["Mick Herron", "John le Carré"],
    tags=["spy", "thriller"],
    exclude_tags=["non-fiction"],
    min_rating=4
)

# SQL Generated:
# Books where:
#   (author = 'Mick Herron' OR author = 'John le Carré')
#   AND (tag = 'spy' OR tag = 'thriller')
#   AND rating >= 4
#   AND NOT (tag = 'non-fiction')
```

**Result**: Books by **(Mick Herron OR John le Carré)** with **(spy tag OR thriller tag)**, rating >= 4, **excluding** non-fiction tag

---

## 🎯 Query Logic Summary

### **OR Logic (within same parameter type)**
- `tags=["crime", "thriller"]` → crime **OR** thriller
- `authors=["Author1", "Author2"]` → Author1 **OR** Author2
- `publishers=["Pub1", "Pub2"]` → Pub1 **OR** Pub2

### **AND Logic (between different parameter types)**
- `tag="crime", author="Doyle"` → crime tag **AND** Doyle author
- `tags=["crime"], min_rating=4` → (crime tag) **AND** (rating >= 4)
- `author="Herron", tag="spy", min_rating=4` → all three combined with **AND**

### **NOT Logic (exclusions)**
- `exclude_tags=["non-fiction"]` → **NOT** non-fiction tag
- `exclude_authors=["King"]` → **NOT** King author
- Exclusions are applied **after** inclusions (AND NOT)

---

## 📝 Complete Example Query

### **Complex Search: "Find crime novels by Conan Doyle or Agatha Christie, rated 4+ stars, not young adult, published after 1900"**

```python
search_books(
    authors=["Conan Doyle", "Agatha Christie"],  # OR logic within list
    tag="crime novel",                           # AND with authors
    min_rating=4,                                # AND with rating
    exclude_tags=["young adult"],                # AND NOT exclusion
    pubdate_start="1900-01-01"                  # AND with date
)
```

**SQL Structure**:
```sql
SELECT books.* FROM books
JOIN books_authors_link ON books.id = books_authors_link.book
JOIN authors ON books_authors_link.author = authors.id
JOIN books_tags_link ON books.id = books_tags_link.book
JOIN tags ON books_tags_link.tag = tags.id
JOIN ratings ON books.id = ratings.book
WHERE
    -- Authors: OR logic within list
    (authors.name ILIKE '%Conan Doyle%' OR authors.name ILIKE '%Agatha Christie%')
    -- Tags: AND logic with other filters
    AND tags.name ILIKE '%crime novel%'
    -- Rating: AND logic
    AND ratings.rating >= 4
    -- Date: AND logic
    AND books.pubdate >= '1900-01-01'
    -- Exclusion: AND NOT logic (subquery)
    AND books.id NOT IN (
        SELECT book_id FROM books_tags_link
        JOIN tags ON books_tags_link.tag = tags.id
        WHERE tags.name ILIKE '%young adult%'
    )
DISTINCT
```

---

## 🔑 Key Points

1. **Single tag parameter** (`tag="crime novel"`):
   - Searches for exact tag name (partial match with `ILIKE '%crime novel%'`)
   - Works with multi-word tags

2. **Multiple tags** (`tags=["crime", "novel"]`):
   - Uses **OR logic** - matches books with **any** of these tags
   - Note: This finds books with tag "crime" **OR** tag "novel"
   - To find books with **BOTH** tags, use separate searches or check results client-side

3. **Different filter types** (`tag="crime", author="Doyle"`):
   - Always combined with **AND logic**
   - Both conditions must match

4. **Exclusions** (`exclude_tags=["young adult"]`):
   - Applied with **AND NOT logic**
   - Removes books matching excluded criteria

5. **Case-insensitive**: All tag/author searches use `ILIKE` (case-insensitive)

6. **Partial matching**: All text searches use `%pattern%` (matches anywhere in the name)

---

## 🚨 Important Limitations

### **Cannot do "AND" logic for tags in single query**

**Not possible**:
```python
# This does NOT work - there's no way to require BOTH tags
search_books(tags=["crime", "novel"])  # Returns crime OR novel
```

**Workaround** (requires two queries or client-side filtering):
```python
# Option 1: Search for one tag, filter results
results = search_books(tag="crime")
# Filter client-side for books that also have "novel" tag

# Option 2: Use text search (searches across all fields)
search_books(text="crime novel")  # Might match in titles/comments too
```

### **Tag name matching is partial**

```python
search_books(tag="crime")
# Matches: "crime", "crime novel", "true crime", "crime fiction"
# Uses ILIKE '%crime%' pattern
```

To match exact tag name, you'd need to query tags first to get exact names.

---

## 📚 Common Query Patterns

### **Pattern 1: Single Tag**
```python
search_books(tag="crime novel")
```

### **Pattern 2: Multiple Tags (any)**
```python
search_books(tags=["crime", "thriller", "mystery"])
```

### **Pattern 3: Tag + Author**
```python
search_books(tag="crime novel", author="Conan Doyle")
```

### **Pattern 4: Tag + Rating**
```python
search_books(tag="crime novel", min_rating=4)
```

### **Pattern 5: Tag + Exclude**
```python
search_books(tag="crime novel", exclude_tags=["young adult"])
```

### **Pattern 6: Complex AND/OR/NOT**
```python
search_books(
    authors=["Author1", "Author2"],  # OR
    tags=["tag1", "tag2"],           # OR (ANDed with authors)
    exclude_tags=["exclude1"],       # NOT
    min_rating=4                     # AND
)
```

---

**Last Updated**: 2025-01-XX

