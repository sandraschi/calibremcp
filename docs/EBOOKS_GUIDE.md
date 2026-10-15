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

## Grey libraries ("shadow libraries")

Searchable mega-collections assembled without rightsholder permission. What they
are, factually (status: October 2026):

- **Z-Library** — FBI seized its domains in November 2022; two alleged operators
  arrested. Mirrors keep resurfacing; uptime varies week to week.
- **Anna's Archive** — meta-search over Z-Lib, Sci-Hub, and LibGen dumps
  (~61M books / ~95M papers claimed). Its `.org` domain was put on serverHold in
  January 2026; it resurfaced via mirrors.
- **Library Genesis / Sci-Hub** — the older dumps underneath much of it all;
  Sci-Hub is papers-focused (Elbakyan).
- **[SLUM](https://open-slum.org)** (Shadow Library Uptime Monitor) — independent
  tracker of which mirrors are currently alive.

No mirror URLs are listed here on purpose: they move constantly, and their
legality depends on your jurisdiction. Treat grey-library files as exactly what
they are — convenient, legally grey, and periodically vanishing.

## Copyright basics for library owners

- Owning a **file** is not owning the **rights**. Reading, limited lending, and
  personal format-shifting depend on local law.
- Germany's *Privatkopie* permits private copies from lawful sources; whether
  defeating DRM to make one is lawful is a separate question — check local law.
- **Keep receipts**: store invoices as book notes ("bought at Thalia 2024-03-11").
  If a file's origin ever matters, that ends the discussion.

## The great book gobble (AI training data)

Edited long-form prose is the highest-signal training text available, so books
ended up at the center of AI copyright litigation. Known corpora included
**Books3** (~196k pirated books, via The Pile) and LibGen dumps — which is why
the labs were sued over *where they got the books*, not just how they trained.

| Case | Status (Oct 2026) | The point |
|---|---|---|
| **Bartz v. Anthropic** | $1.5B class settlement, final approval 20 July 2026 (~482k works, ~$3k each) — largest US copyright settlement ever | Training ruled transformative fair use; *pirated sourcing* created the liability |
| **Kadrey v. Meta** | Fair-use win for Meta, 25 June 2025 — on technical grounds (no market-dilution record); judge warned most such training likely infringes; torrenting claim separate | Outcomes turn on evidence, not principle |
| **NYT v. OpenAI/Microsoft** | Filed Dec 2023; core claims survived; at summary judgment, consolidated into multi-district litigation | The marquee training-data case, still running |
| **Authors Guild** | Class counsel in Bartz; claim portal + webinars | Where working authors go for leverage |

Writer side, fairly put: years of work vacuumed into competing products via
unpaid copies (plaintiffs include Sarah Silverman in Kadrey). Lab side: training
is transformative reading, like a human studying books. Courts so far: *how you
learned* can be fair use; *stealing the textbooks* costs $1.5B.

Voices: [Authors Guild](https://authorsguild.org) · [Society of Authors](https://societyofauthors.org) · [EFF on AI and copyright](https://www.eff.org/issues/ai-and-copyright).

## See also

- `docs/ONBOARDING.md` — first import walkthrough
- `docs/CONTENT_SERVER.md` — the server our imports go through
- In-app Help → Guides — import/metadata workflows
