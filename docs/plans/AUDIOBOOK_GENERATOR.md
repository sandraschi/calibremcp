# Audiobook Generator — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 5–7 days
**Priority:** 5 of 5 — build after the reading-flow and annotation work

---

## What this is and isn't

**What it is:** A pipeline that takes an owned book from Sandra's Calibre
library and produces an M4B audiobook with chapter markers, playable in
any audiobook app, generated entirely using existing fleet infrastructure
(speech-mcp for Gemini 3.1 Pro TTS or local Kokoro/Piper, local LLM for
prosody analysis, pymupdf/ebooklib for text extraction).

**What it isn't:** A replacement for professionally narrated audiobooks of
literary fiction. A human narrator brings interpretive choices that
emotion-tag-sprinkling can't replicate. See "Where this works and where
it doesn't" below.

Sandra should listen to the first 30 minutes of an output and evaluate
honestly whether the result is listenable for that book. For some books
the answer will be yes; for others, no, and she should buy the Audible
version.

## Where this works and where it doesn't

**Works well:**

- Non-fiction, essays, popular-science — narrative voice is already
  explanatory; emotional range is narrow; pacing is steady
- Genre fiction with straightforward third-person narration — SF/F where
  the prose is functional, not virtuosic
- Technical books, manuals, reference material
- Light novels and most manga-adjacent prose (translated Japanese fiction
  often reads cleanly)

**Works poorly:**

- Literary fiction where prose is the point (Woolf, Nabokov, anything
  McCarthy wrote after 1985)
- Heavy dialogue with many distinct speakers, especially if characters
  have distinct speech patterns
- Poetry (skip entirely)
- Plays, screenplays (skip)
- Heavy formatting: equations, code blocks, tables, footnotes
- Books with extensive non-English text that requires pronunciation
  different from the dominant language

For books in the "works poorly" set, the system refuses to generate and
explains why, rather than producing something that would waste compute and
disappoint Sandra.

## Quality ceiling honesty

The best output from this pipeline will not equal a good human narrator.
It will be:

- Consistent pacing without fatigue
- Correct pronunciation of most words (TTS is good at this now)
- Detectable emotion at the paragraph level (via tag insertion)
- Consistent narrator voice across the book
- Character voices limited to 2-3 consistent choices if implemented

It will not be:

- Interpretive. The narrator cannot decide that *this* word in *this*
  sentence gets slightly stressed because of what's happening 50 pages
  later. Human narrators do this all the time.
- Character-acting. Giving the villain a genuinely menacing voice rather
  than just "male voice #2".
- Spontaneous. Great narrators sometimes sound like they're thinking about
  what they're saying. TTS cannot fake that.

Set expectations accordingly. This is a tool for books where you want
to listen while doing something else, not a replacement for narration as
an art form.

---

## Budget considerations

Sandra has a ~€100/month AI budget. Two paths:

**Path A — Local-only (free after electricity).** Use Kokoro or Piper
for TTS locally on the 4090. Quality is good but below Gemini 3.1 Pro.
Sentiment analysis via Ollama (already paid for). Zero per-book marginal
cost.

**Path B — Gemini 3.1 Pro TTS (paid).** Via speech-mcp. Much better
emotional range. Cost estimation: a 300-page novel is ~80,000 words ≈
600,000 characters. Gemini TTS is priced per character; at ~$4 per 1M
characters in April 2026, that's ~$2.40 per novel. At 2-3 books per
month Sandra's busy commute, roughly €10/month — well within budget.

**Recommendation:** Build Path A first. Add Path B as an option behind a
config flag. Sandra picks per-book. Non-fiction gets Path A (quality is
fine); important fiction gets Path B.

## Storage

Per-book audio files are significant. An 80,000-word book at 200 words
per minute is ~400 minutes of audio. At 64kbps mono M4B (plenty for
speech), that's ~190 MB per book.

At 2-3 books per month, 30 books per year × 200 MB = 6 GB/year. Sandra has
plenty of disk. Not a constraint.

The audio files are stored next to the source book in Calibre format folder
structure, so Calibre treats them as another format. Playing the audiobook
from Calibre's UI "just works" — clicking the M4B launches the default
audiobook app.

---

## Architecture

```
    ┌──────────────────────────────────────────────────────────────┐
    │                    audiobook_generator                       │
    │                                                              │
    │  ┌────────┐   ┌─────────┐   ┌─────────┐   ┌──────┐   ┌─────┐ │
    │  │Extract │──▶│  Clean  │──▶│Annotate │──▶│  TTS │──▶│Stitch│ │
    │  └────────┘   └─────────┘   └─────────┘   └──────┘   └─────┘ │
    │      │              │             │            │         │    │
    │  pymupdf/        chapter     Ollama         speech-    ffmpeg │
    │  ebooklib        detect      sampling       mcp /              │
    │                                             Kokoro             │
    │                                                              │
    │  Output: {book_title}.m4b with chapters and ID3 tags        │
    └──────────────────────────────────────────────────────────────┘
```

Five stages, each independently testable:

### Stage 1 — Extract

**File:** `src/calibre_mcp/audiobook/extract.py` (new)

For each supported format:

- **EPUB**: `ebooklib` (already a dep). Walk spine, extract XHTML per
  chapter, strip tags, preserve paragraph breaks.
- **PDF**: `pymupdf` (already a dep). Page by page; detect chapter breaks
  via font-size heuristics or TOC.
- **MOBI/AZW3**: convert to EPUB via Calibre's `ebook-convert` first.
- **TXT, HTML**: trivial.

Output: list of chapter objects, each with title and ordered paragraphs.

```python
@dataclass
class Chapter:
    index: int
    title: str
    paragraphs: list[str]

@dataclass
class ExtractedBook:
    book_id: int
    title: str
    authors: list[str]
    chapters: list[Chapter]
    word_count: int
    rejected_sections: list[str]  # e.g., "chapter 5 had 200 lines of code"
```

### Stage 2 — Clean

Decide what to skip, what to keep, what to warn about:

- **Code blocks** → skip (replaced with "code block omitted; see text")
- **Tables** → skip (same)
- **Equations** → skip (noted)
- **Footnotes** → inline at paragraph end in brackets
- **Non-dominant language** → detected via language detection per paragraph;
  if >30% of a paragraph isn't the dominant language, either skip or read
  literally and flag
- **URLs** → read as "link to [domain]"
- **Images** → skipped (we note alt text if present)

Output: cleaned chapters.

### Stage 3 — Annotate (the interesting part)

This is where LLM sampling earns its keep. For each chapter, pass the full
text to Ollama with a structured prompt:

> You are preparing a book for TTS audio production. For each paragraph,
> analyze emotion/tone and mark any dialogue. Return JSON with one entry
> per paragraph: {paragraph_index, dominant_emotion, pace, emphasis_words,
> speakers}. Emotions: neutral, reflective, tense, urgent, melancholy,
> warm, humorous, ominous. Pace: normal, slow, fast. Speakers: list of
> character names in order if dialogue, else empty.

The annotation is done at chapter granularity (not paragraph) because
the LLM benefits from context — an ominous mood carries across a scene.

Output: annotated paragraphs with metadata.

```python
@dataclass
class AnnotatedParagraph:
    text: str
    emotion: str                    # see list above
    pace: str                       # "normal" | "slow" | "fast"
    speakers: list[str]             # character names in spoken order, [] if pure narration
    emphasis_words: list[str]
    is_dialogue: bool
    is_chapter_heading: bool
```

Character voice assignment is deferred to stage 4 — stage 3 just
identifies who's speaking, not what voice they get.

### Stage 4 — TTS

**File:** `src/calibre_mcp/audiobook/tts.py` (new)

The critical path. Two backends:

**Backend A — Gemini 3.1 Pro via speech-mcp**

Gemini 3.1 Pro accepts SSML-like prosody hints inline:

```ssml
<speak>
  <prosody rate="slow" pitch="-2st">
    She looked at the horizon,
    <break time="500ms"/>
    and for the first time in years, she felt nothing.
  </prosody>
</speak>
```

We translate the annotated paragraph metadata into these tags. The emotion
→ prosody mapping:

| Emotion     | Rate | Pitch shift | Other                       |
|-------------|------|-------------|------------------------------|
| neutral     | 1.0  | 0           | —                            |
| reflective  | 0.9  | -1st        | longer pauses between sentences |
| tense       | 1.1  | +1st        | shorter pauses                |
| urgent      | 1.2  | +2st        | very short pauses             |
| melancholy  | 0.85 | -2st        | longer pauses                 |
| warm        | 0.95 | -1st        | —                             |
| humorous    | 1.05 | +1st        | slight emphasis on key words |
| ominous     | 0.9  | -2st        | longer pauses; occasional whisper tags |

Emphasis words get `<emphasis level="strong">...</emphasis>` wrapping.

Dialogue gets a different voice (voice_id) than narration.

**Backend B — Kokoro / Piper (local)**

Kokoro is SOTA open-source TTS as of early 2026. Runs on CUDA. Supports
multi-voice. No SSML but accepts per-chunk voice selection and basic
speed control.

Less emotion nuance than Gemini. But free and private.

**Character voices:**

Assign voices deterministically from a pool. First speaker encountered
gets voice 1, second gets voice 2, etc., up to a ceiling of 3 distinct
voices. Pool of voices is:

- Narrator (voice 0): baseline
- Character voice A (voice 1): different pitch/rate from narrator
- Character voice B (voice 2): different again
- All subsequent characters: cycle through A/B

Simple, consistent, not trying to be clever.

Output: one audio file per paragraph (short) or per N paragraphs (longer,
cheaper per request). Stored in a per-book workdir.

### Stage 5 — Stitch

**File:** `src/calibre_mcp/audiobook/stitch.py` (new)

Using `ffmpeg` (external dependency — document in README):

1. Concatenate paragraph audio files in order with silence between them
   (300ms between paragraphs, 1.5s between chapters)
2. Generate chapter metadata file in FFmpeg format
3. Mux into M4B container with chapter markers
4. Embed ID3 tags from Calibre metadata (title, author, cover image,
   album=series, track=series_index if applicable)
5. Add the M4B back to Calibre as a new format for the book

```python
def stitch(
    paragraph_files: list[Path],
    chapter_breaks: list[int],
    metadata: BookMetadata,
    cover_image: Path | None,
    output_path: Path,
) -> Path:
    """Run ffmpeg to produce the final M4B."""
```

---

## Data model

```sql
CREATE TABLE audiobook_jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id         INTEGER NOT NULL,
    library_path    TEXT NOT NULL,
    status          TEXT NOT NULL,
    -- 'queued' | 'extracting' | 'annotating' | 'synthesising' | 'stitching'
    --  | 'done' | 'failed' | 'cancelled'
    backend         TEXT NOT NULL,    -- 'gemini' | 'kokoro'
    voice_count     INTEGER DEFAULT 1,
    word_count      INTEGER,
    progress_pct    REAL DEFAULT 0,
    output_path     TEXT,
    error_message   TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at      TIMESTAMP,
    finished_at     TIMESTAMP,
    duration_seconds INTEGER
);
CREATE INDEX idx_jobs_status ON audiobook_jobs(status);
CREATE INDEX idx_jobs_book ON audiobook_jobs(book_id);
```

## Implementation

### MCP tool

```python
@mcp.tool()
async def manage_audiobook(
    operation: Literal["generate", "status", "cancel", "list_jobs",
                       "preview_first_chapter", "eligibility_check"],
    book_id: int | None = None,
    job_id: int | None = None,
    backend: Literal["gemini", "kokoro"] = "kokoro",
    voice_count: int = 1,
) -> dict:
    """Manage audiobook generation for Calibre books."""
```

Operations:

- `eligibility_check(book_id)` — analyse the book's content and report
  whether it's a good candidate. Returns:

  ```json
  {
    "eligible": true,
    "confidence": "high" | "medium" | "low",
    "reasons": ["non-fiction", "steady pacing", "minimal code blocks"],
    "warnings": ["chapter 5 contains 3 pages of equations"],
    "estimated_runtime_minutes": 420,
    "estimated_generation_minutes": 45,
    "estimated_cost_usd": 2.40  // null for local backend
  }
  ```

- `preview_first_chapter(book_id)` — quick generation of just chapter 1,
  ~30-45 minutes of audio, so Sandra can evaluate quality before committing
  to the full book

- `generate(book_id, backend)` — queue a full-book job; returns job_id

- `status(job_id)` — current progress, ETA, errors

- `cancel(job_id)` — stop an in-progress job

- `list_jobs(status?)` — list all jobs, optionally filtered

### REST endpoints

```
POST /api/audiobook/eligibility/{book_id}
POST /api/audiobook/preview/{book_id}
POST /api/audiobook/generate/{book_id}    body: {backend, voice_count}
GET  /api/audiobook/job/{job_id}
POST /api/audiobook/job/{job_id}/cancel
GET  /api/audiobook/jobs                   ?status=
```

### Frontend

New page `/audiobook`:

- Queue: in-progress jobs with live progress bars
- History: completed jobs with "download M4B" links
- Per-book: from any book modal, an "Audiobook" tab with:
  - Eligibility check result (auto-run on open)
  - "Generate preview" button (chapter 1 only)
  - "Generate full audiobook" button (with backend picker)
  - Existing audiobook (if any) with player

### Progress reporting

Generation is slow. The UI needs to feel alive:

- Server-sent events from job progress endpoint
- Progress expressed as (chunks_completed / total_chunks), updated per chunk
- ETA computed from elapsed time and remaining chunks
- Last-completed-chunk preview audio clip (30 seconds) playable from UI
  so Sandra can confirm quality early

---

## Pipeline performance

For an 80,000-word novel:

- Extract: seconds
- Clean: seconds
- Annotate: ~5 minutes (one Ollama call per chapter, ~30 chapters)
- TTS (Kokoro, 4090): ~30-45 minutes for generation
- TTS (Gemini Pro, API): ~15-25 minutes depending on rate limits
- Stitch: 1-2 minutes

Total: 45-60 minutes of real time per novel on the 4090.

Running overnight for a batch of 3-5 books is reasonable.

## Edge cases

**Book has no clear chapter structure.** Fall back to splitting by
manuscript percentage — 12-15 equal "chapters" for navigation.

**Book is in a language other than English.** Detect dominant language;
require explicit confirmation that the TTS backend supports it. Kokoro
has limited language support; Gemini Pro has broader.

**Book has copyright restrictions.** calibre-mcp operates on locally owned
books. We don't enforce anything — if Sandra has a book in her Calibre
library, we assume she has the right to produce a personal-use audiobook
of it. This is a grey area of copyright law but produces no files that
leave the machine.

**TTS backend fails mid-generation.** Each paragraph is independently
synthesised; failures are retried 3× with backoff. If a paragraph
permanently fails, it's replaced with a short beep + "[generation error]"
spoken. The job completes with a warning rather than aborting.

**User cancels mid-generation.** Cancel flag checked between chunks; next
chunk sees the flag and exits cleanly. Already-generated audio is
discarded (no half-books).

**Storage runs out.** Jobs check disk space before starting; refuse if
less than 2x estimated output size is free.

## Privacy

With the local (Kokoro) backend: nothing leaves the machine.

With Gemini backend: text chunks go to Google via the speech-mcp client.
Sandra should know this and toggle consciously.

---

## Success criteria

Two weeks after release:

- Sandra has listened to at least one full generated audiobook end-to-end
  and judged it listenable
- The eligibility check has correctly identified at least one book as
  "not a good candidate" that she agreed with
- The preview-first-chapter flow is the primary entry point (not "go
  straight to full generation") — because listening to 30 minutes is the
  only reliable way to evaluate quality before committing to hours of
  compute

## What's deferred

**Voice cloning.** Sandra trains the TTS on her own voice, or a family
member's, etc. Interesting but way out of scope.

**Re-narration.** If Sandra has an existing Audible file, compare and
regenerate just the worst parts. Too complex.

**Interactive reading.** "Read me chapter 3" via voice command. Belongs
in a separate speech-mcp-centric spec.

**Synchronisation with ebook reading position.** Reading flow captures
position; audiobook player could pick up where the ebook left off. Nice
but requires audiobook-app integration, which is outside this repo.

**Multiple narrator voices for heavy-dialogue books.** Capped at 3 voices
in v1. If Sandra says "please give Zakalwe a different voice," that's a v2
project.

---

*Signed: Claude Opus 4.7 (Anthropic), April 18, 2026.*
