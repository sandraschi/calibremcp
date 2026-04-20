"""
Semantic search dialog — queries /api/rag/metadata/search and shows results.
Double-click or "Select in Library" jumps to the book in Calibre.
"""

try:
    from qt.core import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QVBoxLayout,
    )
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QVBoxLayout,
    )

from calibre_plugins.calibre_mcp_integration import mcp_client


class SemanticSearchDialog(QDialog):
    def __init__(self, gui):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.setWindowTitle("MCP: Semantic Book Search")
        self.setMinimumSize(560, 420)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        q_row = QHBoxLayout()
        q_row.addWidget(QLabel("Query:"))
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText(
            "e.g. locked room mystery, orbital megastructures, cosy Japanese fiction"
        )
        self.query_edit.returnPressed.connect(self._search)
        q_row.addWidget(self.query_edit)
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._search)
        q_row.addWidget(self.search_btn)
        layout.addLayout(q_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.status_label)

        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        self.results_list.itemDoubleClicked.connect(self._open_book)
        self.results_list.currentItemChanged.connect(self._show_snippet)
        layout.addWidget(self.results_list)

        self.snippet_label = QLabel("")
        self.snippet_label.setWordWrap(True)
        self.snippet_label.setStyleSheet("color: #94a3b8; font-size: 11px; padding: 2px;")
        self.snippet_label.setMaximumHeight(48)
        layout.addWidget(self.snippet_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.open_btn = QPushButton("Select in Library")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self._open_book)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        if not mcp_client.is_available():
            self.status_label.setText(
                "Backend not reachable (port 10720). "
                "Start calibre-mcp webapp for semantic search."
            )
            self.search_btn.setEnabled(False)

    def _search(self):
        query = self.query_edit.text().strip()
        if not query:
            return
        self.results_list.clear()
        self.snippet_label.setText("")
        self.open_btn.setEnabled(False)
        self.status_label.setText("Searching...")
        self.search_btn.setEnabled(False)
        try:
            results = mcp_client.semantic_search(query, top_k=25)
            if not results:
                self.status_label.setText(
                    "No results. Build the metadata index first "
                    "(webapp -> Semantic Search -> Build index)."
                )
                return
            for hit in results:
                book_id = hit.get("book_id")
                title = hit.get("title", "Unknown")
                score = hit.get("score")
                snippet = hit.get("text", "")
                label = title + (f"  [{score:.3f}]" if score is not None else "")
                item = QListWidgetItem(label)
                item.setData(256, book_id)   # Qt.UserRole
                item.setData(257, snippet)   # UserRole+1
                self.results_list.addItem(item)
            n = len(results)
            self.status_label.setText(f"{n} result{'s' if n != 1 else ''}")
            self.open_btn.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
        finally:
            self.search_btn.setEnabled(True)

    def _show_snippet(self, current, _prev):
        if current:
            self.snippet_label.setText((current.data(257) or "")[:180])

    def _open_book(self, _item=None):
        item = self.results_list.currentItem()
        if not item:
            return
        book_id = item.data(256)
        if book_id is None:
            return
        try:
            self.gui.search.set_search_string(f"id:{book_id}")
            self.gui.search.do_search()
        except Exception:
            pass
        self.accept()
