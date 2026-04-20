"""
Research dialog — deep book research using:
  1. Wikipedia API (plain urllib)
  2. SF Encyclopedia (plain urllib, genre fiction only)
  3. calibre-mcp webapp: /api/rag/retrieve for local passages
  4. Local calibre_mcp_data.db for personal notes / extended metadata
  5. Ollama for LLM synthesis (streaming into the text area)

No Claude Desktop required. Fully self-contained.
"""

import threading

try:
    from qt.core import (
        QApplication,
        QDialog,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
    )
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
    )

from calibre_plugins.calibre_mcp_integration import mcp_client, ollama_client
from calibre_plugins.calibre_mcp_integration.db_adapter import (
    get_extended_metadata,
    get_user_comment,
)

# Tags that indicate genre fiction worth querying SF Encyclopedia
_SF_TAGS = {
    "science fiction", "sf", "fantasy", "space opera", "cyberpunk",
    "hard sf", "new weird", "speculative fiction", "alternate history",
    "horror", "dark fantasy", "steampunk",
}


def _get_library_path(db) -> str:
    if hasattr(db, "backend") and db.backend is not None:
        if hasattr(db.backend, "library_path"):
            return db.backend.library_path
        if hasattr(db.backend, "dbpath"):
            from pathlib import Path
            return str(Path(db.backend.dbpath).parent)
    return getattr(db, "library_path", "") or ""


def _tags_from_mi(mi) -> list[str]:
    try:
        return [t.lower().strip() for t in (mi.tags or [])]
    except Exception:
        return []


class ResearchDialog(QDialog):
    """Stream a research report about the selected book into a text area."""

    def __init__(self, gui, book_id: int, mi):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.book_id = book_id
        self.mi = mi
        self.title = mi.title or "Unknown"
        self.authors = list(mi.authors or [])
        self.primary_author = self.authors[0] if self.authors else ""
        self.tags = _tags_from_mi(mi)
        self.library_path = _get_library_path(gui.current_db)
        self._worker: threading.Thread | None = None
        self._cancelled = False

        self.setWindowTitle(f"Research — {self.title[:55]}")
        self.setMinimumSize(640, 520)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Status line
        self.status_label = QLabel("Gathering sources…")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.status_label)

        # Output area
        self.text_area = QPlainTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(
            "QPlainTextEdit { background: #0f172a; color: #e2e8f0; "
            "font-family: 'Segoe UI', sans-serif; font-size: 12px; "
            "border: 1px solid #334155; border-radius: 4px; padding: 8px; }"
        )
        layout.addWidget(self.text_area)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.close_btn)
        layout.addLayout(btn_row)

        # Start immediately
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    # ── Background worker ─────────────────────────────────────────────────────

    def _run(self):
        """Fetch sources and stream synthesis. Runs in background thread."""
        try:
            sections: list[str] = []

            # ── Book header ───────────────────────────────────────────────────
            series_str = ""
            if getattr(self.mi, "series", None):
                idx = getattr(self.mi, "series_index", None)
                series_str = (f"{self.mi.series} #{idx}"
                               if idx else self.mi.series)

            sections.append(f"BOOK: {self.title}")
            if self.primary_author:
                sections.append(f"AUTHOR: {self.primary_author}")
            if series_str:
                sections.append(f"SERIES: {series_str}")
            if self.tags:
                sections.append(f"GENRES/TAGS: {', '.join(self.tags[:12])}")

            # Calibre description
            desc = getattr(self.mi, "comments", "") or ""
            if desc:
                import re
                desc = re.sub(r"<[^>]+>", " ", desc)
                desc = re.sub(r"\s+", " ", desc).strip()
                sections.append(f"\n--- CALIBRE DESCRIPTION ---\n{desc[:800]}")

            # ── Wikipedia ────────────────────────────────────────────────────
            self._set_status("Fetching Wikipedia…")
            wiki = mcp_client.wikipedia_summary(self.title, self.primary_author)
            if wiki:
                sections.append(f"\n--- WIKIPEDIA ---\n{wiki[:1500]}")

            # ── SF Encyclopedia (genre fiction only) ─────────────────────────
            if set(self.tags) & _SF_TAGS:
                self._set_status("Fetching SF Encyclopedia…")
                sfe = mcp_client.sf_encyclopedia(self.title)
                if sfe:
                    sections.append(f"\n--- SF ENCYCLOPEDIA ---\n{sfe}")

            # ── Local RAG passages ────────────────────────────────────────────
            if mcp_client.is_available():
                self._set_status("Fetching local RAG passages…")
                hits = mcp_client.passage_search(
                    f"themes setting premise of {self.title}", top_k=5
                )
                book_hits = [h for h in hits
                             if h.get("book_id") == self.book_id][:4]
                if book_hits:
                    raw = "\n\n".join(
                        h.get("snippet", h.get("content", ""))
                        for h in book_hits
                    )
                    # Strip any <mark> tags from snippets
                    import re
                    raw = re.sub(r"</?mark>", "", raw)
                    sections.append(
                        f"\n--- PASSAGES FROM YOUR COPY ---\n{raw[:1800]}"
                    )

            # ── Extended metadata + personal notes ───────────────────────────
            if self.library_path:
                ext = get_extended_metadata(self.book_id, self.library_path)
                ext_parts = []
                if ext.get("original_language"):
                    ext_parts.append(f"Original language: {ext['original_language']}")
                if ext.get("mood"):
                    ext_parts.append(f"Mood: {ext['mood']}")
                if ext.get("read_status"):
                    ext_parts.append(f"Read status: {ext['read_status']}")
                if ext.get("date_read"):
                    ext_parts.append(f"Date read: {ext['date_read']}")
                if ext.get("locked_room_type"):
                    ext_parts.append(
                        f"Locked room type: {ext['locked_room_type']}"
                    )
                if ext.get("edition_notes"):
                    ext_parts.append(f"Edition: {ext['edition_notes']}")
                if ext_parts:
                    sections.append(
                        "\n--- YOUR METADATA ---\n" + "\n".join(ext_parts)
                    )

                notes = get_user_comment(self.book_id, self.library_path)
                if notes:
                    sections.append(f"\n--- YOUR NOTES ---\n{notes[:600]}")

            if self._cancelled:
                return

            # ── Check Ollama ──────────────────────────────────────────────────
            if not ollama_client.is_available():
                self._append(
                    "\n\n── Source material gathered ──\n\n"
                    + "\n\n".join(sections)
                    + "\n\n[Ollama not running — showing raw sources only.\n"
                    "Start Ollama and retry for synthesised report.]"
                )
                self._finish()
                return

            # ── Build synthesis prompt ────────────────────────────────────────
            source_text = "\n".join(sections)
            prompt = f"""You are an expert literary researcher and critic.
Write a comprehensive research report about this book using all the source
material provided below.

Format in clean readable prose with these sections (omit any with no data):

## Overview
What the book is, its place in literary history, why it matters.

## The Author
Relevant biography and where this book sits in their career.

## Plot & Content
What the book is about. Do not over-spoil unless notes indicate it's been read.

## Critical Reception & Legacy
How it was received, awards, cultural impact.

## Themes & Style
Major themes, motifs, structural or stylistic choices.

## Adaptations & Related Works
Films, TV, sequels, related titles worth knowing.

## Your Library
Personalise based on the reader's metadata, notes, and read status.
Be specific — mention their rating, notes, edition if present.

---
SOURCE MATERIAL:
{source_text}
---

Write the report now. Be authoritative and interesting.
Omit sections where you have no meaningful content."""

            system = ("You are an expert literary researcher, critic, "
                       "and bibliographer. Write in clear, engaging prose.")

            # ── Stream response ───────────────────────────────────────────────
            self._set_status("Synthesising with local LLM…")
            self._append("\n")

            for token in ollama_client.generate_streaming(prompt, system=system):
                if self._cancelled:
                    break
                self._append(token)

        except Exception as e:
            self._append(f"\n\n[Error: {e}]")
        finally:
            self._finish()

    # ── Thread-safe UI helpers ────────────────────────────────────────────────

    def _set_status(self, msg: str):
        """Update status label from any thread."""
        try:
            from qt.core import Q_ARG, QMetaObject, Qt
            QMetaObject.invokeMethod(
                self.status_label, "setText",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, msg),
            )
        except Exception:
            try:
                from PyQt5.QtCore import Q_ARG, QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG("QString", msg),
                )
            except Exception:
                pass

    def _append(self, text: str):
        """Append text to the output area from any thread."""
        try:
            from qt.core import Q_ARG, QMetaObject, Qt
            QMetaObject.invokeMethod(
                self.text_area, "insertPlainText",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, text),
            )
        except Exception:
            try:
                from PyQt5.QtCore import Q_ARG, QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self.text_area, "insertPlainText",
                    Qt.QueuedConnection,
                    Q_ARG("QString", text),
                )
            except Exception:
                pass

    def _finish(self):
        """Called when worker is done — re-enable buttons."""
        self._set_status("Done.")
        try:
            from qt.core import QMetaObject, Qt
            QMetaObject.invokeMethod(
                self.close_btn, "setEnabled",
                Qt.ConnectionType.QueuedConnection,
            )
            QMetaObject.invokeMethod(
                self.cancel_btn, "setEnabled",
                Qt.ConnectionType.QueuedConnection,
            )
        except Exception:
            pass
        # Simpler fallback — just set enabled directly via close_btn
        try:
            self.close_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
        except Exception:
            pass

    def _cancel(self):
        self._cancelled = True
        self.cancel_btn.setEnabled(False)
        self._set_status("Cancelled.")
        self.close_btn.setEnabled(True)
