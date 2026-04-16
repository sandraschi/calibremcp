"""
Extended metadata dialog — v3, tabbed layout.

Tab 1 — Details:   first_published, original_language, translator, edition_notes,
                   read_status, date_read, mood
Tab 2 — Spoilers & Notes:  culprit, locked_room_type, personal notes
"""

from calibre_plugins.calibre_mcp_integration import db_adapter

try:
    from qt.core import (
        QComboBox,
        QDialog,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PyQt5.QtWidgets import (
        QComboBox,
        QDialog,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )


READ_STATUSES = ["", "unread", "reading", "read", "abandoned", "re-reading"]

LOCKED_ROOM_TYPES = [
    "",
    "sealed room",
    "impossible crime",
    "alibi problem",
    "vanishing",
    "apparent suicide",
    "no footprints",
    "other",
]


def _get_library_path(db):
    if hasattr(db, "backend") and db.backend is not None:
        if hasattr(db.backend, "library_path"):
            return db.backend.library_path
        if hasattr(db.backend, "dbpath"):
            from pathlib import Path
            return str(Path(db.backend.dbpath).parent)
    if hasattr(db, "library_path"):
        return db.library_path
    if hasattr(db, "dbpath"):
        from pathlib import Path
        return str(Path(db.dbpath).parent)
    return ""


def _form_widget() -> tuple[QWidget, QFormLayout]:
    """Return a widget with a QFormLayout ready to use."""
    w = QWidget()
    fl = QFormLayout(w)
    fl.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
    fl.setContentsMargins(12, 12, 12, 12)
    fl.setSpacing(8)
    return w, fl


class MetadataDialog(QDialog):
    def __init__(self, gui, icon, book_id, book_title):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.book_id = book_id
        self.book_title = book_title or "Unknown"
        self.db = gui.current_db
        self.library_path = _get_library_path(self.db)

        self.setWindowTitle(f"MCP Metadata — {self.book_title[:50]}")
        self.setMinimumWidth(440)
        if icon and not icon.isNull():
            self.setWindowIcon(icon)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(6)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tabs = QTabWidget(self)

        # ── Tab 1: Details ────────────────────────────────────────────────────
        tab1, fl1 = _form_widget()

        self.first_pub_edit = QLineEdit()
        self.first_pub_edit.setPlaceholderText("e.g. 1935, 44 BC")
        fl1.addRow("First published:", self.first_pub_edit)

        self.orig_lang_edit = QLineEdit()
        self.orig_lang_edit.setPlaceholderText("e.g. Japanese, French, Latin")
        fl1.addRow("Original language:", self.orig_lang_edit)

        self.translator_edit = QLineEdit()
        self.translator_edit.setPlaceholderText("Translator name")
        fl1.addRow("Translator:", self.translator_edit)

        self.edition_edit = QLineEdit()
        self.edition_edit.setPlaceholderText("e.g. Penguin Classics 1984 ed.")
        fl1.addRow("Edition notes:", self.edition_edit)

        fl1.addRow(QLabel(""))  # spacer row

        self.status_combo = QComboBox()
        for s in READ_STATUSES:
            self.status_combo.addItem(s.capitalize() if s else "— not set —", s)
        fl1.addRow("Read status:", self.status_combo)

        self.date_read_edit = QLineEdit()
        self.date_read_edit.setPlaceholderText("YYYY-MM-DD or just year")
        fl1.addRow("Date read:", self.date_read_edit)

        self.mood_edit = QLineEdit()
        self.mood_edit.setPlaceholderText("e.g. cosy, bleak, funny, terrifying")
        fl1.addRow("Mood / vibe:", self.mood_edit)

        tabs.addTab(tab1, "Details")

        # ── Tab 2: Spoilers & Notes ───────────────────────────────────────────
        tab2 = QWidget()
        v2 = QVBoxLayout(tab2)
        v2.setContentsMargins(12, 12, 12, 4)
        v2.setSpacing(8)

        spoiler_box = QGroupBox("⚠  Spoilers")
        spoiler_box.setStyleSheet(
            "QGroupBox { color: #d97706; border: 1px solid #d97706; "
            "border-radius: 4px; margin-top: 6px; padding-top: 4px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 8px; }"
        )
        fl2 = QFormLayout(spoiler_box)
        fl2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        fl2.setSpacing(8)

        self.culprit_edit = QLineEdit()
        self.culprit_edit.setPlaceholderText("Who did it? (butler, inspector, the demon…)")
        fl2.addRow("Who did it:", self.culprit_edit)

        self.locked_room_combo = QComboBox()
        for t in LOCKED_ROOM_TYPES:
            self.locked_room_combo.addItem(t.capitalize() if t else "— not set —", t)
        fl2.addRow("Locked room type:", self.locked_room_combo)

        v2.addWidget(spoiler_box)

        notes_label = QLabel("Personal notes")
        notes_label.setStyleSheet("font-weight: bold; margin-top: 4px;")
        v2.addWidget(notes_label)

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Your annotations, reactions, quotes…")
        self.comment_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        v2.addWidget(self.comment_edit)

        tabs.addTab(tab2, "Spoilers & Notes")

        outer.addWidget(tabs)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        outer.addLayout(btn_row)

        self._load()

    # ── Load ──────────────────────────────────────────────────────────────────

    def _load(self):
        if not self.library_path:
            return
        ext = db_adapter.get_extended_metadata(self.book_id, self.library_path)

        self.first_pub_edit.setText(ext.get("first_published", ""))
        self.orig_lang_edit.setText(ext.get("original_language", ""))
        self.translator_edit.setText(ext.get("translator", ""))
        self.edition_edit.setText(ext.get("edition_notes", ""))

        idx = self.status_combo.findData(ext.get("read_status", ""))
        self.status_combo.setCurrentIndex(max(idx, 0))

        self.date_read_edit.setText(ext.get("date_read", ""))
        self.mood_edit.setText(ext.get("mood", ""))
        self.culprit_edit.setText(ext.get("culprit", ""))

        lr_idx = self.locked_room_combo.findData(ext.get("locked_room_type", ""))
        self.locked_room_combo.setCurrentIndex(max(lr_idx, 0))

        self.comment_edit.setPlainText(
            db_adapter.get_user_comment(self.book_id, self.library_path)
        )

    # ── Save ──────────────────────────────────────────────────────────────────

    def save(self):
        if not self.library_path:
            QMessageBox.warning(self, "No Library",
                                "Could not determine library path. Save failed.")
            return
        try:
            db_adapter.set_extended_metadata(
                self.book_id,
                self.library_path,
                first_published=self.first_pub_edit.text().strip(),
                original_language=self.orig_lang_edit.text().strip(),
                translator=self.translator_edit.text().strip(),
                edition_notes=self.edition_edit.text().strip(),
                read_status=self.status_combo.currentData() or "",
                date_read=self.date_read_edit.text().strip(),
                mood=self.mood_edit.text().strip(),
                culprit=self.culprit_edit.text().strip(),
                locked_room_type=self.locked_room_combo.currentData() or "",
            )
            db_adapter.set_user_comment(
                self.book_id,
                self.library_path,
                self.comment_edit.toPlainText().strip(),
            )
            QMessageBox.information(self, "Saved", "MCP metadata saved.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
