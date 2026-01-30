# Anna's Archive Integration

**Date**: 2025-01-30

## Overview

CalibreMCP can search Anna's Archive via `manage_import(operation="annas_search")`. Anna's Archive uses multiple mirror domains; if one is down, the client tries the next.

## Configuration

### Environment Variable: ANNAS_MIRRORS

Comma-separated list of base URLs. Default:

```
https://annas-archive.org,https://annas-archive.li,https://annas-archive.se
```

Override in `.env`:

```
ANNAS_MIRRORS=https://annas-archive.org,https://annas-archive.li,https://annas-archive.pm
```

### Mirror Maintenance

Anna's Archive may add or change domains. Check:

- [Anna's Archive Wikipedia](https://en.wikipedia.org/wiki/Anna's_Archive) - lists mirrors
- [ScottBot10 calibre_annas_archive](https://github.com/ScottBot10/calibre_annas_archive) - `constants.py` for `DEFAULT_MIRRORS`
- Anna's official site/blog for domain changes

When a mirror stops working, add the new one to `ANNAS_MIRRORS` and remove the broken one.

## Usage

### Search (MCP)

```
manage_import(operation="annas_search", query="author title", max_results=20)
```

Returns list of matches with `title`, `author`, `formats`, `detail_url`. Open `detail_url` in a browser to download.

### Add from URL

If you have a direct download URL (e.g. from LibGen, Z-Library):

```
manage_import(operation="from_url", url="https://...")
```

### Add from Local File

```
manage_import(operation="from_path", file_path="C:/path/to/book.epub")
```

## HTML Parsing

The client parses Anna's search results page. If Anna's changes their HTML structure, parsing may break. The client uses:

- `table tr` for result rows
- Column indices: 0=cover/link, 1=title, 2=author, 9=formats

Report parsing issues in the CalibreMCP repo; we can update selectors to match Anna's new layout.
