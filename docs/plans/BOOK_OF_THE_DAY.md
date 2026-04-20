# Book of the Day — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 1 day
**Priority:** 3 of 5 — smallest project, high delight payoff

---

## The idea

Every morning at 6 AM local time, calibre-mcp picks one book from Sandra's
library that satisfies: owned, unread (or forgotten), likely-to-interest.
It generates a short research report and surfaces it as a widget on the
webapp dashboard. Optional: send it as a daily email.

The goal isn't more information in Sandra's life. It's re-surfacing things
she already owns. At 13,000 books, the tail is long and most of it is
forgotten. One a day, over a year, is 365 rediscoveries.

## Why it's small

Almost everything this needs already exists:

- **Selection logic**: query book_extended_metadata + reading_sessions +
  rating info to find candidates. SQL.
- **Research report**: `media_research_book` already exists and produces
  exactly the right output shape.
- **Scheduling**: one cron-style timer (FastMCP has no native scheduling,
  so a simple APScheduler background job does it).
- **Widget**: a Next.js card component on the homepage. Existing patterns.

So it's one SQL query, one scheduled job, one UI card. A day of work.

---

## Selection logic

The quality of Book-of-the-Day depends entirely on picking interesting
candidates. The algorithm:

### Hard filters (book must pass all)

1. `book_extended_metadata.read_status IS NULL` OR `read_status = 'unread'`
2. Not picked as book-of-the-day in the last 180 days
3. Has non-trivial metadata: either a Calibre description OR tags OR series

### Soft scoring (higher = more likely to be picked)

- **Forgotten score**: how long since Calibre's `timestamp` (date added)?
  Books added 5+ years ago score highest, recent additions lowest.
  `score += log(years_since_added + 1) * 3`
- **Completion score**: if part of a series where Sandra has read other
  volumes, boost. `score += 5` if series completion ∈ (0.1, 0.9).
- **Taste adjacency**: for unread books by authors Sandra has rated ≥4★
  on other books, boost. `score += 2 per 5-star book by same author`.
- **Tag diversity**: prefer tags that haven't been surfaced recently.
  Track last-surfaced-date per tag; boost books whose dominant tag hasn't
  been surfaced in 14+ days.
- **Length penalty for the unknown**: if the book has no Calibre description
  AND no Wikipedia page (we don't know this a priori without a fetch) —
  slight penalty because the generated report will be thin. `score -= 3` if
  comments is empty.

### Selection

Take the top 20 scoring candidates. Randomly pick one from the top 20,
weighted by score. This gives variety — the same top book doesn't get picked
every day if other candidates are close in score.

### Fallbacks

If fewer than 20 candidates pass hard filters:

1. Relax the 180-day exclusion to 90 days
2. Allow re-reading-eligible books (read but `date_read > 3 years ago`)
3. Fall back to any book with non-trivial metadata, random weighted by
   `years_since_added`

---

## Data model

One new SQLite table:

```sql
CREATE TABLE book_of_the_day (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL UNIQUE,  -- YYYY-MM-DD
    book_id         INTEGER NOT NULL,
    library_path    TEXT NOT NULL,
    score           REAL,
    report          TEXT,                  -- cached research report
    report_generated_at TIMESTAMP,
    user_action     TEXT,
    -- NULL | 'opened' | 'dismissed' | 'marked_read' | 'marked_abandoned'
    action_at       TIMESTAMP
);
```

Plus a tag surfacing tracker:

```sql
CREATE TABLE tag_last_surfaced (
    tag           TEXT PRIMARY KEY,
    last_date     TEXT NOT NULL
);
```

## Implementation

### Step 1 — Selection function

**File:** `src/calibre_mcp/services/botd.py` (new)

```python
async def select_book_of_the_day(library_path: Path) -> int | None:
    """Pick today's book. Returns book_id or None if nothing suitable."""

    candidates = _find_candidates(library_path)
    scored = [(b, _score_candidate(b)) for b in candidates]
    top = sorted(scored, key=lambda x: -x[1])[:20]
    if not top:
        return None
    pick = _weighted_random(top)
    return pick.book_id
```

### Step 2 — Scheduled job

**File:** `src/calibre_mcp/services/botd_scheduler.py` (new)

Using `apscheduler` (already a transitive dep via fastmcp). On server
startup, register a cron job at 06:00 local time.

```python
def _run_daily():
    """Select today's book, generate report, cache it."""
    today = date.today().isoformat()
    if already_picked(today):
        return  # idempotent
    book_id = select_book_of_the_day(current_library())
    if book_id is None:
        return
    report = generate_report(book_id)  # calls media_research_book
    save_botd(today, book_id, report)
```

Report generation happens in background. If it fails (Ollama down, network
hiccup), we save the book selection without the report and retry the
report every 30 minutes for up to 24 hours.

### Step 3 — MCP tools

New operations on `manage_reading_state` (from `READING_FLOW_INTEGRATION.md`)
or a separate `manage_botd` portmanteau:

| Operation      | Purpose                                    |
|---------------|--------------------------------------------|
| `today`       | Return today's book + report               |
| `history`     | Last N days of picks with user actions    |
| `skip`        | Skip today's pick, pick another            |
| `preview`     | What would be picked if we ran now?       |
| `regenerate_report` | Re-generate report for today's book (e.g., Ollama was down) |

### Step 4 — REST endpoints

**File:** `webapp/backend/app/api/botd.py` (new)

```
GET  /api/botd/today                    → today's book + report + metadata
GET  /api/botd/history?days=30
POST /api/botd/skip                     → skip and pick another
POST /api/botd/action/{date}            body: {action: 'opened'|'dismissed'|...}
```

### Step 5 — Frontend widget

On the homepage (`/`), a new card at the top:

```
┌─ Book of the Day ─────────────────────────────┐
│                                                │
│  [cover]  The Player of Games                  │
│           Iain M. Banks · Culture #2           │
│                                                │
│  ─────────────────────────────────            │
│  A master game-player is recruited to play    │
│  an alien civilization's central game, with   │
│  imperial power as the stakes. The premise   │
│  — games as politics — lets Banks skewer      │
│  [...read more]                                │
│                                                │
│  [Read report]  [Skip]  [Mark read]           │
└────────────────────────────────────────────────┘
```

- Cover from Calibre
- Title, author, series (if applicable)
- First 200 chars of the research report
- Three actions: open full report, skip (picks another), mark-read (if
  already read, archive the pick)
- Click anywhere on title/cover → jumps to `/book/{id}`

### Step 6 — Email (optional)

A simple SMTP send at 07:00 with a rendered HTML email containing the same
information. Configured via webapp settings page. Default off.

Uses `emailjs`-compatible SMTP config or a direct SMTP call. Sandra has
existing email infrastructure; we don't build a mail server.

---

## Tuning

The score weights are guesses and will want tuning. Track `user_action`
in `book_of_the_day`: if Sandra dismisses a book, its tag and author get
a small negative signal for a while. If she marks it read or opens the
report, small positive signal.

Adjustment happens in background: every week, recompute tag/author
priors from the last 30 days of user actions. No ML training — just
simple exponential moving averages.

## Why not ML

At this scale, the signal is thin. Simple heuristics + weekly EMAs will
do as well as any trained model. If after six months the selection feels
stale, we can revisit — but starting with heuristics is the right move.

## Edge cases

**Sandra hasn't used calibre-mcp for a month.** She comes back, opens the
webapp. The card shows today's pick. Previous 30 days are available in
`/botd/history` so she can browse what she missed.

**Empty library.** Card shows "Add some books and check back tomorrow."

**All candidates scored zero.** This shouldn't happen with a 13k library
but if it does, pick any random unread book.

**User hates today's pick.** "Skip" button — picks another immediately,
marks the skipped one as dismissed. Can only skip 3 times per day (to
avoid turning it into a shopping carousel).

---

## Success criteria

One month after install:

- Widget is rendering daily
- Sandra has opened the full research report at least 10 times
- She's read or started reading at least 3 books surfaced this way
- The "skip" button has been used < 50% of the time (i.e., most picks
  feel at least plausibly interesting)

If skip rate stays above 50%, the scoring weights need adjustment —
probably meaning we're picking too many "forgotten but boring" books.

---

*Signed: Claude Opus 4.7 (Anthropic), April 18, 2026.*
