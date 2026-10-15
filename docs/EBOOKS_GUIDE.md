# Ebooks: sources, communities & bibliography tools

Where books come from, where readers talk, and where metadata lives — with
notes on how each maps to importing into Calibre.

> Status notes (legal/shop availability) were correct in October 2026 and drift;
> treat vendor lists as a starting map, not a directory. No piracy instructions
> live here — only what things are and how they relate to your library.

## Free & public-domain ebook sources

| Source | What | Import note |
|---|---|---|
| [Project Gutenberg](https://www.gutenberg.org) | 70k+ public-domain ebooks (US law), mostly EPUB/Kindle/TXT | Clean files, import directly |
| [Standard Ebooks](https://standardebooks.org) | Hand-polished Gutenberg editions, modern typography | Best-quality public domain EPUBs |
| [Internet Archive texts](https://archive.org/details/texts) | Millions of scans + OCR, lending library | Quality varies; check before importing |
| [Open Library](https://openlibrary.org) | Borrowable scans + edition metadata | Great for metadata even when you own the file |
| [Wikisource](https://wikisource.org) | Proofread transcriptions, multilingual | Good for DE/FR classics |
| [Projekt Gutenberg-DE](https://www.projekt-gutenberg.org) | German-language public domain texts | The DE counterpart that matters locally |
| [Zeno.org](http://www.zeno.org) | German literature + reference works | Older interface, solid texts |

Our **Import page** fetches Gutenberg books directly — paste a Gutenberg ebook
number or URL and the file lands in your library with metadata attached.

## Commercial stores (where to buy)

| Store | Notes for Calibre users |
|---|---|
| Amazon Kindle | Largest catalog; files carry Kindle DRM — official path in is USB transfer + import where lawful |
| Kobo / Rakuten | EPUB-based ecosystem, friendlier files than Kindle |
| Google Play Books | EPUB/PDF, account-tied |
| Apple Books | Apple-siloid, hardest to get files out of |
| Thalia / Hugendubel / ebook.de | The German high-street options (Adobe-DRM EPUBs) |
| O'Reilly, No Starch, Manning, Leanpub | Tech publishers; largely **DRM-free** — buy, download, import, done |
| Smashwords / Draft2Digital | Indie/authors-direct; usually DRM-free |
| Tor/Forge (Macmillan) | Major SFF publisher selling DRM-free ebooks since ~2012 |

Rule of thumb: DRM-free stores import in one step; DRM-locked stores add
friction by design. Prefer DRM-free when you have the choice.

## Communities & discovery

- **MobileRead Forums** — the Calibre nerve center (Kovid himself posts there); device + format + conversion expertise
- **r/ebooks** — deals, news, store gossip
- **Goodreads** — biggest review/social catalog (Amazon-owned; export your shelves periodically)
- **LibraryThing** — older, cataloguer-minded community, TinyCat for small libraries
- **BookWyrm** — federated Goodreads alternative (ActivityPub)
- **Hardcover.app** — modern tracker with good list features
- **ISFDB** (Internet Speculative Fiction Database) — the bibliography for SF/F, unmatched for series/order data
- **Grand Comics Database / Comic Vine** — the same for comics (pairs with Komga/Kavita below)

## Bibliography & metadata services

Use these when files arrive with bad metadata (the "Download metadata" button
and `media_research_book` query several of them):

- **Open Library API** — editions, covers, author records; free, no key
- **Google Books API** — ISBN lookup, generous free quota
- **WorldCat** (OCLC) — library-union catalog; the "does this edition exist?" oracle
- **DNB** (Deutsche Nationalbibliothek) — authoritative for German-language publishing
- **Library of Congress** — US authority records
- **VIAF** — links author identities across national libraries
- **Crossref / DOI** — papers and non-fiction with DOIs (pairs with arXiv imports)
- **ISBNdb** — commercial ISBN database (free tier limited)

## Formats refresher

EPUB (reflowable, first choice) · KEPUB (Kobo tweaks) · AZW3/KFX (Kindle) ·
PDF (fixed layout, poor on e-ink) · CBZ/CBR (comics) · TXT/HTML (universal fallback).
Calibre converts between nearly all of them; keep the original file on import
and convert copies for devices.

## See also

- `docs/ONBOARDING.md` — first import walkthrough
- `docs/CONTENT_SERVER.md` — the server our imports go through
- In-app Help → Guides — import/metadata workflows
