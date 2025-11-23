"""
Query parsing utilities for book searches.

Handles parsing of natural language queries to extract:
- Author names (when "by" is used)
- Tags (when "tagged as" or "with tag" is used)
- Publication dates (when "published" is used)
- Content type hints (paper, comic, manga) for library selection
- Time expressions (last month, last week, etc.) for date filtering
- Quoted titles
- Other intelligent patterns
"""

from typing import Tuple, Optional, Dict, Any
import re
from datetime import datetime, timedelta

try:
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


def _parse_time_expression(time_expr: str) -> Optional[Tuple[str, str]]:
    """
    Parse time expressions like "last month", "last week", "last year" into date ranges.
    
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format, or None if not recognized
    """
    time_expr_lower = time_expr.lower().strip()
    now = datetime.now()
    
    # Map time expressions to date ranges
    if HAS_DATEUTIL:
        time_mappings = {
            "last month": (now - relativedelta(months=1)).replace(day=1),
            "last week": now - timedelta(weeks=1),
            "last year": (now - relativedelta(years=1)).replace(month=1, day=1),
            "this month": now.replace(day=1),
            "this week": now - timedelta(days=now.weekday()),
            "this year": now.replace(month=1, day=1),
        }
    else:
        # Fallback without dateutil - approximate with timedelta
        time_mappings = {
            "last month": (now - timedelta(days=30)).replace(day=1),
            "last week": now - timedelta(weeks=1),
            "last year": (now - timedelta(days=365)).replace(month=1, day=1),
            "this month": now.replace(day=1),
            "this week": now - timedelta(days=now.weekday()),
            "this year": now.replace(month=1, day=1),
        }
    
    if time_expr_lower in time_mappings:
        start_date = time_mappings[time_expr_lower]
        if "month" in time_expr_lower:
            if "last" in time_expr_lower:
                # Last month: first day of last month to last day of last month
                if HAS_DATEUTIL:
                    end_date = now.replace(day=1) - timedelta(days=1)
                else:
                    # Approximate: 30 days ago
                    end_date = now - timedelta(days=30)
            else:
                # This month: first day to today
                end_date = now
        elif "week" in time_expr_lower:
            if "last" in time_expr_lower:
                # Last week: 7 days ago to today
                end_date = now
            else:
                # This week: start of week to today
                end_date = now
        elif "year" in time_expr_lower:
            if "last" in time_expr_lower:
                # Last year: Jan 1 to Dec 31 of last year
                if HAS_DATEUTIL:
                    end_date = now.replace(month=12, day=31) - relativedelta(years=1)
                else:
                    # Approximate: 365 days ago
                    end_date = now - timedelta(days=365)
            else:
                # This year: Jan 1 to today
                end_date = now
        else:
            end_date = now
        
        return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    return None


def parse_intelligent_query(query: str) -> Dict[str, Any]:
    """
    Intelligently parse natural language query to extract search parameters.
    
    Recognizes patterns:
    - "books by Author Name" -> author search
    - "books tagged as X" or "books with tag X" -> tag search
    - "published 1987" or "published in 1987" -> pubdate search
    - "rating 4" or "rated 4" -> rating search
    - "series X" -> series search
    - "paper X", "comic X", "manga X" -> content type hint + library selection
    - "from last month" -> date range filter
    - Quoted titles like "attention is all you need"
    
    Args:
        query: The search query string
    
    Returns:
        Dictionary with parsed parameters:
        {
            "text": remaining query text (after extracting structured params),
            "author": author name if found,
            "tag": tag name if found,
            "pubdate": publication year if found,
            "rating": rating if found,
            "series": series name if found,
            "content_type": "manga", "comic", "paper", or None,
            "added_after": date string if time expression found,
            "added_before": date string if time expression found,
        }
    """
    if not query:
        return {
            "text": "", "author": None, "tag": None, "pubdate": None, 
            "rating": None, "series": None, "content_type": None,
            "added_after": None, "added_before": None,
        }
    
    query_lower = query.lower().strip()
    remaining = query
    result = {
        "text": "",
        "author": None,
        "tag": None,
        "pubdate": None,
        "rating": None,
        "series": None,
        "content_type": None,
        "added_after": None,
        "added_before": None,
    }
    
    # Extract quoted titles first (preserve quotes for exact matching)
    quoted_title = None
    quote_match = re.search(r'["\'](.+?)["\']', query)
    if quote_match:
        quoted_title = quote_match.group(1)
        # Remove quotes from remaining but keep the title text
        remaining = re.sub(r'["\']', '', remaining)
    
    # Parse content type hints: "paper", "comic", "manga" (synonyms for "book")
    content_type_patterns = [
        (r"^(paper|papers)\s+(.+)", "paper"),
        (r"^(comic|comics)\s+(.+)", "comic"),
        (r"^(manga|mangas)\s+(.+)", "manga"),
        (r"(.+)\s+(paper|papers)$", "paper"),
        (r"(.+)\s+(comic|comics)$", "comic"),
        (r"(.+)\s+(manga|mangas)$", "manga"),
    ]
    for pattern, content_type in content_type_patterns:
        match = re.match(pattern, query_lower, re.IGNORECASE)
        if match:
            result["content_type"] = content_type
            # Remove content type word from remaining query
            remaining = re.sub(rf"\b({content_type}s?)\b", "", remaining, flags=re.IGNORECASE).strip()
            query_lower = remaining.lower()
            break
    
    # Parse time expressions: "from last month", "added last week", etc.
    time_patterns = [
        r"from\s+(last\s+month|last\s+week|last\s+year|this\s+month|this\s+week|this\s+year)",
        r"added\s+(last\s+month|last\s+week|last\s+year|this\s+month|this\s+week|this\s+year)",
        r"(last\s+month|last\s+week|last\s+year|this\s+month|this\s+week|this\s+year)",
    ]
    for pattern in time_patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            time_expr = match.group(1) if match.lastindex else match.group(0)
            date_range = _parse_time_expression(time_expr)
            if date_range:
                result["added_after"] = date_range[0]
                result["added_before"] = date_range[1]
                # Remove time expression from remaining
                remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE).strip()
                query_lower = remaining.lower()
                break
    
    # Parse author: "by Author Name"
    if " by " in query_lower:
        parts = query.split(" by ", 1)
        if len(parts) == 2:
            remaining = parts[0].strip()
            author = parts[1].strip()
            # Remove common prefixes from remaining
            if remaining.lower() in ("books", "book", "find", "search", "list", "get", "show", "show me"):
                remaining = ""
            result["author"] = author
            query_lower = remaining.lower()
    
    elif query_lower.startswith("by "):
        author = query[3:].strip()
        result["author"] = author
        remaining = ""
        query_lower = ""
    
    # Parse tag: "tagged as X" or "with tag X" or "tag X"
    tag_patterns = [
        r"tagged\s+as\s+(.+)",
        r"with\s+tag\s+(.+)",
        r"tag\s+(.+)",
        r"tags?\s+(.+)",
    ]
    for pattern in tag_patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            tag = match.group(1).strip()
            # Remove the matched pattern from remaining
            remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE).strip()
            result["tag"] = tag
            query_lower = remaining.lower()
            break
    
    # Parse publication date: "published 1987" or "published in 1987"
    pubdate_patterns = [
        r"published\s+in\s+(\d{4})",
        r"published\s+(\d{4})",
        r"pubdate\s+(\d{4})",
        r"from\s+(\d{4})",
        r"year\s+(\d{4})",
    ]
    for pattern in pubdate_patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            year = match.group(1)
            result["pubdate"] = year
            # Remove the matched pattern from remaining
            remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE).strip()
            query_lower = remaining.lower()
            break
    
    # Parse rating: "rating 4" or "rated 4" or "4 stars"
    rating_patterns = [
        r"rating\s+(\d)",
        r"rated\s+(\d)",
        r"(\d)\s+stars?",
    ]
    for pattern in rating_patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            rating = int(match.group(1))
            if 1 <= rating <= 5:
                result["rating"] = rating
                # Remove the matched pattern from remaining
                remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE).strip()
                query_lower = remaining.lower()
                break
    
    # Parse series: "series X" or "in series X"
    series_patterns = [
        r"in\s+series\s+(.+)",
        r"series\s+(.+)",
    ]
    for pattern in series_patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            series = match.group(1).strip()
            result["series"] = series
            # Remove the matched pattern from remaining
            remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE).strip()
            query_lower = remaining.lower()
            break
    
    # Clean up remaining text
    remaining = remaining.strip()
    # Remove common prefixes
    if remaining.lower() in ("books", "book", "find", "search", "list", "get", "show", "show me"):
        remaining = ""
    
    # If we extracted a quoted title, use it as the search text
    if quoted_title and not remaining:
        remaining = quoted_title
    elif quoted_title and remaining:
        # Both quoted title and other text - prioritize quoted title
        remaining = f'"{quoted_title}" {remaining}'
    
    result["text"] = remaining
    return result


def parse_author_from_query(query: str) -> Tuple[str, Optional[str]]:
    """
    Parse author name from query if it contains "by".
    
    When a user says "books by Joe Blow" or "book by Conan Doyle",
    they ALWAYS mean author search. This function extracts the author name.
    
    Examples:
        "books by Conan Doyle" -> ("", "Conan Doyle")
        "book by Joe Blow" -> ("", "Joe Blow")
        "by Conan Doyle" -> ("", "Conan Doyle")
        "Conan Doyle" -> ("Conan Doyle", None)
        "python programming" -> ("python programming", None)
        "mystery books by Agatha Christie" -> ("mystery books", "Agatha Christie")
    
    Args:
        query: The search query string
    
    Returns:
        Tuple of (remaining_query, author_name)
        - remaining_query: Query text after removing author part (empty if only author)
        - author_name: Extracted author name, or None if no "by" pattern found
    """
    if not query:
        return ("", None)
    
    query_lower = query.lower().strip()
    
    # Check for " by " pattern (with spaces)
    if " by " in query_lower:
        parts = query.split(" by ", 1)
        if len(parts) == 2:
            remaining = parts[0].strip()
            author = parts[1].strip()
            # If remaining is empty or just common verbs/nouns, return empty
            if not remaining or remaining.lower() in ("books", "book", "find", "search", "list", "get", "show", "show me"):
                return ("", author)
            return (remaining, author)
    
    # Check for "by " at start (without leading text)
    elif query_lower.startswith("by "):
        author = query[3:].strip()  # Remove "by " prefix
        return ("", author)
    
    # No "by" pattern found - return query as-is
    return (query, None)

