# Reading Recommendations

**Description:** Get personalized reading recommendations from your Calibre library using series progress, ratings, tags, reading history, and collaborative filtering across similar books.

## Trigger Phrases

- "What should I read next?"
- "Recommend a book like [title]"
- "What's good in my unread [genre]?"
- "Suggest something from my TBR pile"
- "Find my next series to start"
- "What have I been neglecting?"

## Tools

- `query_books(sort="rating", unread=True, tags=[...], limit=20)` — Find top-rated unread books in a genre.
- `manage_analysis(operation="reading_stats")` — Reading statistics: completion rate, genre distribution, pages read, author diversity.
- `manage_analysis(operation="series_progress")` — Series tracking: which series are started but unfinished, next-in-series ordering.
- `manage_metadata(operation="show", book_id=...)` — Get full metadata for a candidate book: description, rating, tags, series position.
- `calibre_metadata_search(query="similar to [title]")` — Semantic similarity search using LanceDB embeddings.

## Workflow

1. **Profile the reader**: Call `manage_analysis(operation="reading_stats")` to understand reading patterns, preferred genres, and completion behavior.
2. **Surface candidates**: Use `query_books(unread=True, sort="rating", tags=[preferred_genre])` to get top-rated unread books. Combine multiple tag filters for precision.
3. **Series catch-up**: Call `manage_analysis(operation="series_progress")` to find series with book 1 read but book 2+ unread — these are high-confidence recommendations.
4. **Similarity match**: For "like this book" queries, use `calibre_metadata_search()` with a descriptive query of the source book's themes.
5. **Rank and present**: Score candidates by (rating + recency + series_position). Present top 3-5 with reasoning: why this matches the reader's taste, what tags overlap.

## Example

"Recommend my next read from unread fantasy with high ratings." → `query_books(tags=["fantasy"], unread=True, sort="rating", limit=30)` → filter top 5 → `manage_analysis(operation="series_progress")` to prioritize continuations → present with per-book reasoning.
