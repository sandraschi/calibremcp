# Reading-Flow Integration — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 2–3 days
**Priority:** 1 of 5 — build this first

---

## The problem

Calibre tracks nothing about what happens after a book is opened. The only
state it natively maintains is: added date, last modified (which is file
metadata, not reading state), tags, and ratings — all manually maintained.

calibre-mcp v1.7 adds extended metadata (read_status, date_read, mood) via
the plugin. But these are also manually entered. At 13,000 books, nothing
manual scales. Sandra will not, and should not, update 50 books a year by
hand to mark them read.

The result is a library where 13,000 items all look equally-unread to every
downstream feature. Recommendations can't prioritise unread books because it
doesn't know which are unread. Semantic search surfaces random stuff rather
than unread stuff. Book-of-the-day can't exclude books already consumed.

## The fix

Hook into Calibre's viewer events. When a book is opened, track it. When it
hits enough evidence of completion, auto-mark it as read. When it hasn't
been touched in a while, stop counting it as "currently reading".

Specifically:

- Detect when any book file is opened via Calibre (or externally via
  `manage_viewer(operation='open_file')`)
- Track open sessions: book_id, start timestamp, end timestamp, total duration
- Infer completion signals and update `read_status` automatically
- Maintain a "currently reading" list (multi-book state)
- Expose all of this via MCP tools and webapp widgets

## What's simple and what's hard

**Simple:** Capturing `open_file` events from the MCP side (we control that
tool). Writing sessions to SQLite. Aggregating reading time.

**Hard:** Detecting when a book is "finished." Calibre doesn't communicate
from external viewers (Adobe, Edge, FBReader) back to itself. There is no
"you reached the last page" signal. Heuristics are required.

**Built-in Calibre viewer integration:** The Calibre viewer (used for EPUB
and PDF) does maintain reading position in `metadata.db` under the
`annotations` table for EPUBs and an internal position field. We can read
this to detect progress. Not all of Sandra's reading goes through Calibre
viewer — but enough does.

---

## Data model

New SQLite table in `calibre_mcp_data.db`:

```sql
CREATE TABLE reading_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id         INTEGER NOT NULL,
    library_path    TEXT NOT NULL,
    started_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at        TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    source          TEXT DEFAULT 'manage_viewer',
    -- "manage_viewer" | "calibre_annotations" | "manual"
    file_path       TEXT,
    position_start  TEXT,   -- opaque per-format position
    position_end    TEXT,
    metadata        TEXT    -- JSON blob for format-specific data
);
CREATE INDEX idx_sessions_book ON reading_sessions(book_id, library_path);
CREATE INDEX idx_sessions_time ON reading_sessions(started_at);
```

And a view for convenience:

```sql
CREATE VIEW book_reading_stats AS
SELECT
    book_id, library_path,
    COUNT(*) AS session_count,
    SUM(duration_seconds) AS total_seconds,
    MIN(started_at) AS first_read_at,
    MAX(COALESCE(ended_at, started_at)) AS last_read_at
FROM reading_sessions
GROUP BY book_id, library_path;
```

## The heuristics

Auto-mark as `read` when **any** of these become true:

1. **Calibre viewer final-page signal.** If the source is Calibre's own viewer
   and Calibre's annotations table has `last_read_position` at ≥97% of the
   EPUB spine length or ≥97% of PDF pages, mark read. This is the strongest
   signal — Calibre itself knows the user reached the end.
2. **Cumulative time threshold.** If `total_seconds` exceeds a format-specific
   threshold (see below), and no recent session has occurred in 72 hours,
   mark read. This catches external-viewer cases.
3. **Manual.** User can always mark read via plugin or webapp; this takes
   precedence over all heuristics.

Thresholds for heuristic 2 are conservative — we prefer false negatives
(books genuinely read but not marked) to false positives (short browsing
sessions getting marked as "read"):

| Format       | Minimum session total to auto-mark read |
|--------------|------------------------------------------|
| EPUB         | 3 hours                                  |
| PDF          | 4 hours                                  |
| CBZ / CBR    | 45 minutes                               |
| MOBI / AZW3  | 3 hours                                  |
| Other        | 5 hours                                  |

A session must be at least 60 seconds to count (to exclude accidental opens).
Manga/comics get a much shorter threshold because they read fast.

**Currently reading** is defined as any book with:
- at least one session in the last 14 days, AND
- status is not already `read` or `abandoned`

**Abandoned** is inferred after 90 days of no sessions on a book that
previously had at least 30 minutes of reading time. The user sees these in
a "maybe abandoned" section and can confirm or un-confirm.

---

## Implementation

### Step 1 — Session tracking in `manage_viewer`

The existing `manage_viewer(operation='open_file')` tool is the chokepoint
for launching books. Add session tracking here.

**File:** `src/calibre_mcp/tools/viewer/manage_viewer.py`

Current `open_file` launches the file with the system default application.
We modify it to:

1. Before launch: insert a row into `reading_sessions` with `started_at=now()`
2. After launch: return the session_id in the result
3. On a separate "close session" path, update `ended_at` and
   `duration_seconds`

The hard part: we don't get notified when the external viewer closes.
Solution: poll-based cleanup. A periodic background task (every 5 minutes)
looks for sessions where `ended_at IS NULL` and `started_at > 8 hours ago`
and auto-closes them with an assumed 2-hour duration. Imperfect but OK.

Better solution for Calibre's own viewer: Calibre writes to its annotations
DB in real-time. We can poll that for the active book and know when
position advances. A session whose position hasn't advanced in 10 minutes
is considered ended.

```python
# New tool: manage_viewer(operation='close_session')
async def _close_session(session_id: int, duration_seconds: int | None = None,
                          position_end: str | None = None) -> dict:
    """Explicitly close an open reading session."""
```

### Step 2 — Calibre annotations integration

Calibre maintains `annotations.db` in the library directory, containing
EPUB highlights and reading position. We read this (read-only) to:

- Detect current reading position per book
- Detect completion (position ≥ 97%)
- (Later) import highlights — see `ANNOTATION_INTELLIGENCE.md`

**File:** `src/calibre_mcp/services/calibre_annotations.py` (new)

```python
class CalibreAnnotationsReader:
    """Read-only access to Calibre's annotations.db."""

    def __init__(self, library_path: Path):
        self.db_path = library_path / "annotations.db"
        # Graceful if not present — not every library has it

    def get_position(self, book_id: int, format: str) -> float | None:
        """Return fractional position 0.0–1.0 if known, else None."""

    def get_last_read(self, book_id: int) -> datetime | None:
        """Return timestamp of most recent annotation/position update."""

    def all_positions(self) -> dict[int, float]:
        """For every book with known position, return {book_id: fraction}."""
```

### Step 3 — Background watcher

**File:** `src/calibre_mcp/services/reading_watcher.py` (new)

A daemon started at server boot. Every 5 minutes:

1. Queries `CalibreAnnotationsReader.all_positions()`
2. For each book where position changed since last check, upserts a reading
   session and updates the last-position marker
3. Runs the auto-mark-read heuristics
4. Runs the abandoned-detection heuristic (daily, not every 5 minutes)

The watcher needs to tolerate:

- Library switching — poll the currently-active library only
- Calibre running or not running (annotations.db may be locked; retry)
- Multiple calibre-mcp processes — use a lock file to ensure only one watcher

### Step 4 — MCP tools

New portmanteau tool `manage_reading_state`:

| Operation                  | Purpose                                       |
|---------------------------|------------------------------------------------|
| `current`                 | List currently-reading books                   |
| `finished`                | List books marked read (optional since= filter)|
| `abandoned`               | List books flagged abandoned                   |
| `sessions`                | List sessions for a specific book              |
| `stats`                   | Aggregate stats (books/year, hours/week, etc.) |
| `mark_read`               | Manually mark read (overrides heuristics)      |
| `mark_abandoned`          | Manually mark abandoned                        |
| `start_session`           | Manual session start (for external viewers)    |
| `close_session`           | Manual session end                             |
| `rebuild_from_calibre`    | One-off: seed sessions from Calibre annotations|

### Step 5 — REST endpoints

**File:** `webapp/backend/app/api/reading.py` (new)

```
GET  /api/reading/current          → currently reading
GET  /api/reading/finished?year=   → finished in year
GET  /api/reading/abandoned        → abandoned
GET  /api/reading/stats?period=    → time stats
GET  /api/reading/sessions/{book_id}
POST /api/reading/mark-read/{book_id}
POST /api/reading/mark-abandoned/{book_id}
```

### Step 6 — Frontend

Two new pages:

**`/reading` — Reading Dashboard**

A mini-dashboard with four cards:

- **Currently reading** — list of books with last-session-ago timestamps
- **Finished this year** — count + chart by month
- **Time this week** — total reading time + average per day
- **Maybe abandoned** — flagged books with confirm/unconfirm buttons

**`/book/{id}/reading` — Per-book history**

Lists all sessions for a single book as a timeline. Sparkline of session
durations. Aggregate stats at the top (total time, sessions, first/last
dates, current position if known).

Update the existing book modal to show:

- Read status badge (from extended_metadata)
- Last read date
- Position if mid-book
- Total reading time

### Step 7 — Plugin integration

The Calibre GUI plugin gains one new feature: right-click a book → "Reading
History" opens a dialog showing sessions. No new functionality beyond
displaying what the webapp shows.

---

## Migration & seeding

First-run migration: call `rebuild_from_calibre` to seed the reading_sessions
table from Calibre's existing annotations.db. For every book with a
last-read position in Calibre's DB, insert a synthetic session with:

- `started_at` = position's timestamp minus an estimate (conservative: 30 min
  per 10% position)
- `ended_at` = position's timestamp
- `source` = 'calibre_annotations'
- A flag in metadata indicating this is synthetic

This gives instant value — the "finished" list is populated on day one
from historical reading.

## Edge cases and honest limitations

**External viewers stay invisible.** If Sandra reads a PDF in Acrobat rather
than via manage_viewer, we don't see it. Mitigation: make manage_viewer the
preferred path (plugin defaults to it; documentation points to it). We
accept the blind spot for reading via external tools.

**Re-reads need explicit signal.** If a book is already marked `read` and
gets opened again, we don't auto-change anything. Sandra can explicitly
click "Start re-read" in the book modal to create a new session chain that
doesn't collapse into the historical one.

**Multiple devices.** Not supported — calibre-mcp runs on one machine. If
this ever becomes a problem (e.g. reading on a tablet while library lives
on goliath), we'd need sync, which is explicitly out of scope.

**Abandoned-then-resumed.** If a book flagged abandoned gets a new session,
the flag is auto-cleared. Simple.

**Privacy.** Reading sessions are locally-stored SQLite. Never transmitted.
Personal data.

## Success criteria

The feature is working when, two weeks after install:

- `GET /api/reading/current` returns an accurate list of books Sandra is
  actually reading (multi-book state)
- `GET /api/reading/finished?year=2026` returns books Sandra finished in 2026
  without her having manually marked any of them
- The "maybe abandoned" list surfaces books that look abandoned but gives
  Sandra final say

No automated tests needed — Sandra will know within a week whether the
heuristics feel right.

## Tunable parameters

All thresholds (minimum session seconds, format-specific hours, abandoned
day count, etc.) go in a config table so they can be tuned without code
changes. First values are the ones above; adjust from observation.

---

*Signed: Claude Opus 4.7 (Anthropic), April 18, 2026.*
