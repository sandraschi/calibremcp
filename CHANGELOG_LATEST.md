## Calibre MCP v1.10.0 (2026-10-15)

### Highlights
- **Canon Coverage page** (`/canon`): gap analysis vs Gutenberg Top 100 (live), Nobel laureates (all 116, live API), Delphi Classics catalog (1020-edition snapshot), and pasted lists — with buy/source hints and per-author shop links.
- **Collection contents engine**: Delphi-style Complete Works omnibuses get TOC indexing (69 works in Gaskell, 125 in Holmes) — contained stories are searchable ("wisteria lodge" finds its story) and count toward canon coverage, never as fake books.
- **Writes with the GUI open**: add/update/delete/metadata automatically route via the Calibre Content Server when it holds the library (`"via": "content_server"`).
- **Delphi tab extras**: owned-first tables, A–Z filter, cards/list, sort, and "Who is that?" Wikipedia bios.
- **Help overhaul**: real markdown rendering, new Guides / Ebooks / Copyright & AI / Content Server / Why E-Reading tabs, plus new `CONTENT_SERVER.md`, `EBOOKS_GUIDE.md`, and 12-chapter `READING_ESSAY.md` docs.
- **Taxonomy upgrades**: Cards/List toggle + Name/Book-count server-side sort on Authors, Series, Tags, Publishers.
- **Fixes**: `query_books(recent)` crash, honest `book_count` sorting in series/publisher services.
