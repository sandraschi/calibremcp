# Calibre-MCP — Roadmap (Next Phase)

**Status:** planning, April 2026
**Author:** Claude Opus 4.7 (Anthropic), in collaboration with Sandra Schipal
**Repository:** `D:\Dev\repos\calibre-mcp`

---

## Where we are

As of v1.7.0 (2026-04-16), calibre-mcp is a mature FastMCP 3.2 server with:

- 15+ portmanteau tools covering libraries, books, metadata, search, RAG, and import
- Simultaneous stdio + HTTP transport (Claude Desktop + webapp on same process)
- LanceDB metadata index with extended-metadata fields (locked-room types, mood,
  read status, original language) — semantically searchable
- Full-text RAG passage retrieval from Calibre FTS data
- `media_research_book` — deep external research fetching Wikipedia, SF Encyclopedia,
  TVTropes, Anime News Network, Open Library, plus local data synthesis
- Calibre GUI plugin with tabbed metadata editor, semantic search dialog,
  research dialog (streaming Ollama synthesis, no Claude Desktop required)
- Next.js webapp (port 10721) with four RAG modes, series analysis, and
  all standard library-browsing features

The library is ~13,000 books across multiple Calibre libraries on L:.

## What's missing

Despite the breadth, there are gaps where the library still can't answer real
questions about how Sandra actually reads. The tooling supports targeted queries
(“locked room mystery” → semantic results). It does not support:

1. **Passive observation of reading behaviour.** Calibre tracks nothing about
   what happens after you open a book. Read status only exists where it has
   been entered manually.
2. **Annotation-level intelligence.** Kindle and Kobo highlights are the
   densest concentration of personal signal about what a reader finds worth
   remembering. They are currently invisible to calibre-mcp.
3. **Serendipity.** Discovery works when you have a target. For 13,000 books
   it does not work when you want to rediscover something you forgot you owned.
4. **Multi-book state.** Most serious readers have 3–5 books in rotation.
   Nothing tracks this.
5. **Listening.** Modern TTS (Gemini 3.1 Pro via speech-mcp) has crossed the
   threshold for genuine audiobook production. Nothing in the fleet turns
   owned books into listenable files.

This roadmap defines five self-contained projects that close these gaps,
ordered by effort-to-value ratio.

---

## The projects

Each project has its own spec in `docs/plans/`. Each is independent —
they can be built in any order, in parallel, or not at all.

| # | Project                        | Spec                              | Effort | Daily-use impact |
|---|--------------------------------|-----------------------------------|--------|------------------|
| 1 | Reading-flow integration       | `READING_FLOW_INTEGRATION.md`     | 2–3 d  | High             |
| 2 | Annotation import & search     | `ANNOTATION_INTELLIGENCE.md`      | 3–4 d  | High             |
| 3 | Book-of-the-day surfacer       | `BOOK_OF_THE_DAY.md`              | 1 d    | Medium, delight  |
| 4 | Duplicate/edition detection    | `DUPLICATE_DETECTION.md`          | 1–2 d  | One-shot value   |
| 5 | Audiobook generator            | `AUDIOBOOK_GENERATOR.md`          | 5–7 d  | High for niche   |

**Recommended order:** 1 → 2 → 3 → 5, with 4 slotted in wherever boring
maintenance work is desired. Rationale is in each spec.

## Why this order

Reading-flow integration (1) is the foundation. Without it the library has
no idea what you're actually reading, which weakens every downstream feature
including recommendations, annotations in context, and audiobook prioritisation
("which unread book should I listen to next?"). It's also the smallest
behaviour change with the biggest daily consequence — once Calibre knows a book
is being actively read, the rest of the UI gets smarter automatically.

Annotation intelligence (2) unlocks what is probably the highest information
density in Sandra's personal data. Thirteen thousand books is a lot. The
subset of passages Sandra has explicitly highlighted over a decade of reading
is a much more concentrated signal about taste, interests, and unresolved
intellectual threads. Semantic search over that corpus is qualitatively
different from semantic search over full book text.

Book-of-the-day (3) is the smallest project with the highest delight-to-effort
ratio. One widget, one endpoint, no schema changes. Takes a day, adds a daily
habit.

Audiobook generator (5) is the most technically ambitious and the one with
the clearest constraints on where it works (see that spec). It earns its slot
because the infrastructure already exists — Gemini 3.1 Pro TTS via speech-mcp,
Sandra's 4090 for local acceleration, a 13k library of source material. The
gap is just the pipeline.

Duplicate detection (4) is unglamorous boring work that pays off once — you
clean up your library, collapse editions, reclaim disk space. Probably done
as a weekend project while ignoring a news cycle.

---

## What's deliberately not in this roadmap

A few things I considered and rejected:

**Cloud sync / multi-device.** Sandra reads on one machine; the server is
on goliath; Calibre libraries are on L:. There is no multi-device problem
to solve. Adding sync infrastructure would be pure complexity.

**Social features.** No. This is a personal library. Recommendations engines,
shared lists, GoodReads integration beyond reading reviews — none of these
improve the daily reading experience.

**Mobile app.** Calibre has official Android support. iOS has third-party
readers. There is no clear win in building a mobile UI for calibre-mcp that
wouldn't be better served by those existing clients.

**More LLM integrations.** The existing tools (research, synopsis, critical
reception, deep-research) already cover the interesting LLM use cases.
Adding more variants would be feature bloat. If something's missing, it's
better expressed as a new portmanteau operation on an existing tool.

**Yet more source fetchers for research.** Wikipedia + SFE + TVTropes + ANN
+ OpenLibrary is already comprehensive. Adding GoodReads scrapers, JSTOR,
individual book-blog parsers — diminishing returns versus what's already there.

---

## Assumptions and constraints

All five projects assume:

- FastMCP 3.2 as the framework (no planned framework migration)
- SQLite for all persistent state (fits naturally alongside calibre_mcp_data.db)
- Ollama as the primary local LLM inference engine (Gemma 3 12B is the default model)
- Plugin code stays in `calibre_plugin/` within calibre-mcp repo (no separate plugin repo)
- Webapp remains on ports 10720/10721
- No new required external dependencies beyond what's already in the venv

Budget constraint: Sandra has stated a ~€100/month AI tools budget. All
projects must work primarily via local models. External API calls (Wikipedia,
TVTropes, etc.) are free and used sparingly. The audiobook project is the
only one where cloud TTS (Gemini 3.1 Pro) is a realistic cost — budget
implications are discussed in that spec.

## Success criteria

This roadmap is successful if, a month after these projects ship:

- Sandra's library view reflects what she's actually reading without manual
  updates (flow integration)
- She can semantically search her highlights across a decade of reading
  (annotation intelligence)
- She has read or started reading at least three books she'd forgotten she
  owned (book-of-the-day)
- She has listened to at least one full book generated entirely locally
  (audiobook generator)
- Library duplicate count is under 50 (detection)

None of these require new metrics infrastructure to measure — Sandra will
just know.

---

*Signed: Claude Opus 4.7 (Anthropic), April 18, 2026.*
