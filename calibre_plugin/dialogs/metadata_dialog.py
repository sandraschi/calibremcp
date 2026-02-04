"""
Extended metadata dialog - first_published, translator, user_comments.
"""

from calibre_plugins.calibre_mcp_integration import db_adapter  # noqa: F401 - db_adapter module

try:
    from qt.core import (
        QDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
    )
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
    )


def _get_library_path(db):
    """Get current library path from Calibre db."""
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


class MetadataDialog(QDialog):
    def __init__(self, gui, icon, book_id, book_title):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.icon = icon
        self.book_id = book_id
        self.book_title = book_title or "Unknown"
        self.db = gui.current_db
        self.library_path = _get_library_path(self.db)

        self.setWindowTitle(f"MCP Metadata - {self.book_title[:50]}")
        if icon and not icon.isNull():
            self.setWindowIcon(icon)

        layout = QVBoxLayout(self)

        g1 = QGroupBox("Extended Metadata (stored in CalibreMCP)")
        g1_layout = QVBoxLayout()
        g1_layout.addWidget(QLabel("First Published (e.g. 1599, 44 BC):"))
        self.first_pub_edit = QLineEdit(self)
        self.first_pub_edit.setPlaceholderText("Original publication date")
        g1_layout.addWidget(self.first_pub_edit)

        g1_layout.addWidget(QLabel("Translator:"))
        self.translator_edit = QLineEdit(self)
        self.translator_edit.setPlaceholderText("Translator name")
        g1_layout.addWidget(self.translator_edit)
        g1.setLayout(g1_layout)
        layout.addWidget(g1)

        g2 = QGroupBox("User Comment (personal notes, separate from description)")
        g2_layout = QVBoxLayout()
        self.comment_edit = QTextEdit(self)
        self.comment_edit.setPlaceholderText("Your annotations or notes on this book")
        self.comment_edit.setMinimumHeight(120)
        g2_layout.addWidget(self.comment_edit)
        g2.setLayout(g2_layout)
        layout.addWidget(g2)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._load()

    def _load(self):
        if not self.library_path:
            return
        ext = db_adapter.get_extended_metadata(self.book_id, self.library_path)
        self.first_pub_edit.setText(ext.get("first_published", "") or "")
        self.translator_edit.setText(ext.get("translator", "") or "")
        comment = db_adapter.get_user_comment(self.book_id, self.library_path)
        self.comment_edit.setPlainText(comment or "")

    def save(self):
        if not self.library_path:
            QMessageBox.warning(
                self,
                "No Library",
                "Could not determine library path. Save failed.",
            )
            return
        try:
            translator = self.translator_edit.text().strip()
            first_pub = self.first_pub_edit.text().strip()
            comment = self.comment_edit.toPlainText().strip()

            db_adapter.set_extended_metadata(
                self.book_id,
                self.library_path,
                translator=translator,
                first_published=first_pub,
            )
            db_adapter.set_user_comment(
                self.book_id,
                self.library_path,
                comment,
            )

            QMessageBox.information(self, "Saved", "MCP metadata saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save: {e}",
            )
