# Duplicate & Edition Detection — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 1–2 days
**Priority:** 4 of 5 — slot in when other work is blocking

---

## The problem

At 13,000 books over many years of collecting, the library inevitably has:

- **True duplicates**: same book, same format, added twice via different sources
- **Format variants**: same book in EPUB and PDF and MOBI (often wanted!)
- **Edition variants**: same work in different translations, different
  publishers, different years — which may or may not be wanted
- **Near-misses**: same book with slightly different titles, metadata
  drift from Calibre's auto-enrichment, OCR-ish artefacts in titles

None of these are currently visible as duplicates. Calibre has built-in
duplicate detection but it's conservative (exact title + author match).

This spec adds fuzzy detection with UI for triage.

## Design principles

**Never auto-delete.** Everything surfaces as a suggestion. Sandra reviews.

**Distinguish intentional duplicates from clutter.** A book owned in EPUB
and PDF is often deliberate. A book added twice with metadata drift is
clutter. The UI must let Sandra express this per-cluster.

**Idempotent and re-runnable.** Sandra marks clusters as "keep all" or
"merged"; those decisions persist so re-running doesn't re-surface
previously-handled clusters.

---

## Clustering strategy

Build clusters by combining multiple signals:

### Signal 1 — ISBN match

Strongest. Books with the same ISBN are the same edition of the same work.
Trivial SQL query over `identifiers` table.

### Signal 2 — OCLC match

Same as ISBN but for library records. Sandra's Calibre may have these
from Amazon/OpenLibrary lookups. Secondary.

### Signal 3 — Normalised-title + primary-author match

Normalise:
- Lowercase
- Strip subtitles after first `:` or `-` or `—`
- Strip articles (`the`, `a`, `an`) at start
- Strip edition qualifiers: `(unabridged)`, `(revised)`, `(2nd ed.)`
- Collapse whitespace
- Remove diacritics

Then exact match on normalised title + exact match on first author's
surname. Catches most re-imports.

### Signal 4 — Fuzzy title + author match

Levenshtein ratio ≥ 0.88 on normalised title AND exact surname match on
any author. Catches OCR drift, typos, and translation-title variations.

### Signal 5 — Content-hash match (optional, expensive)

For files of the same format (both EPUB or both PDF), compute a
structural hash — XHTML-text-only for EPUB, text-content-by-page for PDF.
Identical hashes = byte-level duplicate regardless of metadata.

Skip this in v1; add if the clustering from signals 1-4 leaves obvious
gaps.

## Cluster types

After building raw clusters from signals, classify:

| Cluster type           | Criteria                                          | Default action |
|-----------------------|---------------------------------------------------|----------------|
| `exact_duplicate`     | Same ISBN + same format + same file size (±5%)    | Suggest delete |
| `format_variants`     | Same ISBN + different formats                     | Keep all       |
| `edition_variants`    | Same work, different ISBNs (or no ISBN) + different publishers | Review |
| `translation_variants`| Same work, different translator in metadata       | Keep all       |
| `metadata_drift`      | Same ISBN + same format + different Calibre metadata (e.g. title/author drift) | Suggest merge |
| `uncertain`           | Fuzzy match, can't confidently classify           | Review         |

"Suggest delete" means propose deleting extras but keeping the one with
richest metadata. User confirms.

"Suggest merge" means propose consolidating metadata fields across the
cluster, keeping the most complete values. User confirms per-field.

"Keep all" means mark the cluster as reviewed; don't resurface it.

"Review" means show them to Sandra with no default action.

---

## Data model

One new table, one new view:

```sql
CREATE TABLE dupe_clusters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    library_path    TEXT NOT NULL,
    cluster_key     TEXT NOT NULL,   -- deterministic hash of member book IDs
    cluster_type    TEXT NOT NULL,
    member_book_ids TEXT NOT NULL,   -- JSON array
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP,
    resolution      TEXT,
    -- NULL | 'kept_all' | 'merged' | 'deleted_extras' | 'reviewed_no_action'
    resolution_data TEXT             -- JSON: what was deleted/merged
);
CREATE INDEX idx_clusters_library ON dupe_clusters(library_path);
CREATE UNIQUE INDEX idx_clusters_key ON dupe_clusters(library_path, cluster_key);
```

`cluster_key` is deterministic (sorted book IDs hashed). Re-running the
detection finds the same cluster and skips it if already resolved.

## Implementation

### Step 1 — Clustering service

**File:** `src/calibre_mcp/services/dupes.py` (new)

```python
def find_duplicate_clusters(library_path: Path) -> list[DupeCluster]:
    """Run all detection signals and return clusters."""

    clusters = []
    clusters.extend(_cluster_by_isbn(library_path))
    clusters.extend(_cluster_by_normalised_title(library_path))
    clusters.extend(_cluster_by_fuzzy(library_path))
    return _dedup_and_classify(clusters)


def _normalise_title(title: str) -> str:
    """Canonical form for matching."""

def _classify_cluster(books: list[Book]) -> ClusterType:
    """Determine cluster type based on member differences."""
```

### Step 2 — Resolution actions

```python
def merge_cluster(cluster_id: int, keep_book_id: int,
                   field_choices: dict[str, int]) -> MergeResult:
    """Merge cluster: keep one book, apply chosen metadata from others,
    optionally delete the rest."""

def delete_extras(cluster_id: int, keep_book_id: int,
                   delete_files: bool = False) -> DeleteResult:
    """Delete all non-kept members of cluster."""

def mark_kept_all(cluster_id: int) -> None:
    """Mark cluster as resolved with no action."""
```

All destructive operations go through Calibre's own delete API (via the
existing `manage_books(operation='delete')` tool) so Calibre's book
folder cleanup happens correctly.

### Step 3 — MCP tools

New portmanteau `manage_duplicates`:

| Operation        | Purpose                                         |
|-----------------|-------------------------------------------------|
| `scan`          | Run detection, upsert clusters                  |
| `list`          | List unresolved clusters                        |
| `get`           | Details of one cluster (member metadata diff)   |
| `merge`         | Execute a merge                                  |
| `delete_extras` | Delete non-kept members                         |
| `keep_all`      | Mark cluster as resolved (ignore)               |
| `stats`         | Total clusters, by type                         |

### Step 4 — REST endpoints

```
POST /api/duplicates/scan
GET  /api/duplicates
GET  /api/duplicates/{cluster_id}
POST /api/duplicates/{cluster_id}/merge    body: {keep_id, field_choices}
POST /api/duplicates/{cluster_id}/delete   body: {keep_id}
POST /api/duplicates/{cluster_id}/keep_all
GET  /api/duplicates/stats
```

### Step 5 — Frontend

**`/duplicates` — new page**

Split view:

Left: cluster list, grouped by type. Badge count per type.

Right: selected cluster shows each member side-by-side as cards:

```
┌─ The Player of Games (Banks) ──── 3 variants ────┐
│                                                   │
│  ┌─ #1234 (EPUB) ─┐  ┌─ #5678 (EPUB) ─┐  ┌─ #9012 (PDF) ─┐
│  │ Cover          │  │ Cover          │  │ Cover          │
│  │ EPUB · 512 KB  │  │ EPUB · 498 KB  │  │ PDF · 2.1 MB   │
│  │ Publisher: Orbit│  │ Publisher:     │  │ Publisher:     │
│  │ Pubdate: 2008  │  │ Pubdate: 1989  │  │ Pubdate: 2008  │
│  │ ★★★★☆          │  │ (no rating)    │  │ ★★★★☆          │
│  └────────────────┘  └────────────────┘  └────────────────┘
│                                                   │
│  Cluster type: metadata_drift                     │
│  Suggested: merge, keep #1234, use richer metadata│
│  from #5678 (Pubdate 1989).                       │
│                                                   │
│  [Keep all]  [Merge into #1234]  [Delete extras]  │
└───────────────────────────────────────────────────┘
```

Field-level merge UI: checkbox per field per member to select which value
wins. Live-preview shows resulting metadata. Confirm → action.

### Step 6 — Safe defaults

- Delete operations NEVER remove files by default; they only remove Calibre
  records (the files stay on disk, just not referenced by Calibre). Sandra
  explicitly ticks "also delete files from disk" to include the file
  removal step.
- Before any destructive action, show a final confirm with the exact list
  of book IDs and file paths that will be affected.

---

## Performance

13,000 books with this clustering:

- ISBN clustering: O(n) single query — milliseconds
- Normalised title: O(n log n) for sort + group — under a second
- Fuzzy match: O(n²) worst case, but we partition by first letter of
  surname first, bringing it down to something tractable. Estimate
  ~30 seconds for full scan.

Not fast enough to run on every request; run on-demand (button click in
webapp) and cache the cluster table.

## One-shot vs ongoing

This is primarily a one-shot cleanup tool. After initial resolution, new
duplicates arrive slowly (only when Sandra adds books). A scheduled weekly
rescan catches new clutter without pestering her daily.

## Success criteria

After one full pass:

- Cluster count below 50 unresolved clusters
- Library size reduced by 2–5% (typical for unmaintained libraries)
- No accidental deletions (this is the bar that matters)

---

*Signed: Claude Opus 4.7 (Anthropic), April 18, 2026.*
