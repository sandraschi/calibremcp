"""
Virtual library from MCP query.
Calls Calibre webapp backend /api/search, creates Calibre saved search.
"""

try:
    from qt.core import QDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout
except ImportError:
    from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from calibre_plugins.calibre_mcp_integration.mcp_client import call_search, is_available


class VLQueryDialog(QDialog):
    """Create virtual library from search query via webapp backend."""

    def __init__(self, gui):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.setWindowTitle("MCP: Create Virtual Library from Query")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Search query (e.g. 'fiction', 'author:Smith'):"))
        self.query_edit = QLineEdit(self)
        self.query_edit.setPlaceholderText("Enter search text")
        layout.addWidget(self.query_edit)

        layout.addWidget(QLabel("VL name:"))
        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("My VL")
        layout.addWidget(self.name_edit)

        create_btn = QPushButton("Create Virtual Library")
        create_btn.clicked.connect(self._create)
        layout.addWidget(create_btn)

        if not is_available():
            layout.addWidget(
                QLabel(
                    "Backend not running. Start Calibre webapp backend (port 13000)\n"
                    "and configure URL in Preferences -> Plugins."
                )
            )

    def _create(self):
        query = self.query_edit.text().strip()
        name = self.name_edit.text().strip() or "MCP Query VL"
        if not query:
            QMessageBox.warning(self, "No Query", "Enter a search query.")
            return
        if not is_available():
            QMessageBox.warning(
                self,
                "Backend Unavailable",
                "Calibre webapp backend is not reachable. Start it on port 13000.",
            )
            return
        result = call_search(query=query, limit=500)
        books = result.get("items") or result.get("results") or result.get("books") or []
        if not result or not books:
            QMessageBox.information(
                self,
                "No Results",
                f"No books found for: {query}",
            )
            return
        ids = []
        for b in books:
            bid = b.get("id") or b.get("book_id")
            if bid is not None:
                ids.append(bid)
        if not ids:
            QMessageBox.information(self, "No Results", "Could not extract book IDs.")
            return
        ids = ids[:200]  # Cap for search expr length
        search_expr = " or ".join(f"id:{i}" for i in ids)
        try:
            self.gui.current_db.saved_search_add(name, search_expr)
            self.gui.search.set_search_string(f"search:{name}")
            self.gui.search.do_search()
            QMessageBox.information(
                self,
                "Done",
                f"Created VL '{name}' with {len(ids)} books.",
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create saved search: {e}",
            )
