# CalibreMCP - Import Hub: Download Sites Guide

CalibreMCP provides a unified **Import Hub** for acquiring books from three primary sources. Each source has specific technical behaviors, mirror configurations, and stability enhancements implementing in v1.5.0.

## 1. Anna's Archive (Shadow Library)

Anna's Archive acts as a metadata aggregator for shadow libraries. 

### Mirror Configuration
By default, the server attempts to find the best mirror. You can override this using the `ANNAS_MIRRORS` environment variable:
```bash
# Example: Comma-separated list of preferred mirrors
ANNAS_MIRRORS="https://annas-archive.li,https://annas-archive.se,https://annas-archive.org"
```

### Automation & Lander Detection
The backend logic (`annas_client.py`) includes a heuristic analyzer to distinguish between:
1. **Direct File Downloads**: The desired outcome where the server can automate the ingest.
2. **Interactive Landers**: Pages requiring a CAPTCHA, a 1-minute "Slow Download" timer, or a "Partner Server" interactive session.

> [!important]
> **Manual Interaction Required**: If a high-quality direct link is not available and only "Slow" landers are found, the UI will display a **"MANUAL INTERACTION REQUIRED"** warning. Use the **"OPEN SOURCE"** button to open the mirror in your browser, solve the CAPTCHA/wait, and download manually.

### MD5 Tracking
The Import Hub tracks MD5 hashes across Anna's Archive results. If a file is blocked by a lander, the MD5 is flagged as `restricted_to_lander` in the UI to prevent repeated failed automation attempts.

---

## 2. arXiv (Scientific Papers)

arXiv provides open-access to 2M+ scholarly articles in physics, mathematics, computer science, and more.

### Stability Hardening
To prevent `HTTP 429` (Too Many Requests) errors, CalibreMCP implements:
- **Exponential Backoff**: Up to 5 retries with increasing delay when rate-limited.
- **User-Agent Compliance**: All requests identify as `CalibreMCP/1.5.0 (+https://github.com/sandraschi/calibre-mcp)` to follow arXiv's robot policy.

### Metadata Extraction
The arXiv client automatically maps:
- `title` -> LaTeX cleaned title.
- `authors` -> Full author list.
- `categories` -> Mapped to Calibre **Tags**.
- `id` -> Stored as a `arxiv` identifier in Calibre.

---

## 3. Project Gutenberg (Public Domain)

Project Gutenberg is a library of over 70,000 free eBooks, primarily older works for which U.S. copyright has expired.

### Mirror Behavior
The server uses `https://www.gutenberg.org` as the primary API host.

### Import Specs
- **Format**: Prefers **EPUB (with images)** for the best reading experience in Calibre.
- **Tags**: Work titles and categories are automatically ingested into the library tags.

---

## Global Import Workflow

All sources in the Import Hub respect your **Global Settings**:
1. **Target Library**: Choose which of your Calibre libraries the book should land in.
2. **Global Tags**: Automatically append tags like `automated-import` to every book.
3. **Series**: For scientific series or related book groups, you can force a project/series name during the import.
