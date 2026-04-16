"""
Configuration widget for CalibreMCP Integration plugin.
"""

from calibre_plugins.calibre_mcp_integration.config import prefs
from calibre_plugins.calibre_mcp_integration import ollama_client

try:
    from qt.core import (
        QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QVBoxLayout, QWidget,
    )
except ImportError:
    from PyQt5.Qt import (
        QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QVBoxLayout, QWidget,
    )


class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        # ── calibre-mcp backend ───────────────────────────────────────────────
        g1 = QGroupBox("calibre-mcp Webapp Backend")
        g1l = QVBoxLayout(g1)
        g1l.addWidget(QLabel("URL (semantic search, series analysis, RAG passages):"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("http://127.0.0.1:10720")
        self.url_edit.setText(prefs.get("mcp_http_url", "http://127.0.0.1:10720"))
        g1l.addWidget(self.url_edit)
        layout.addWidget(g1)

        # ── Ollama ────────────────────────────────────────────────────────────
        g2 = QGroupBox("Ollama (local LLM for Research synthesis)")
        g2l = QVBoxLayout(g2)

        g2l.addWidget(QLabel("Ollama URL:"))
        self.ollama_url_edit = QLineEdit()
        self.ollama_url_edit.setPlaceholderText("http://127.0.0.1:11434")
        self.ollama_url_edit.setText(prefs.get("ollama_url", "http://127.0.0.1:11434"))
        g2l.addWidget(self.ollama_url_edit)

        g2l.addWidget(QLabel("Model (used for Research synthesis):"))
        self.ollama_model_edit = QLineEdit()
        self.ollama_model_edit.setPlaceholderText("gemma3:12b")
        self.ollama_model_edit.setText(prefs.get("ollama_model", "gemma3:12b"))
        g2l.addWidget(self.ollama_model_edit)

        probe_row = QHBoxLayout()
        probe_btn = QPushButton("Test Ollama")
        probe_btn.clicked.connect(self._test_ollama)
        self.probe_label = QLabel("")
        probe_row.addWidget(probe_btn)
        probe_row.addWidget(self.probe_label)
        probe_row.addStretch()
        g2l.addLayout(probe_row)
        layout.addWidget(g2)

        # ── Data dir ──────────────────────────────────────────────────────────
        g3 = QGroupBox("MCP User Data Directory (optional override)")
        g3l = QVBoxLayout(g3)
        g3l.addWidget(QLabel("Override location of calibre_mcp_data.db:"))
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Leave empty for default (%APPDATA%/calibre-mcp)")
        self.dir_edit.setText(prefs.get("mcp_user_data_dir", ""))
        g3l.addWidget(self.dir_edit)
        layout.addWidget(g3)

        layout.addStretch()

    def _test_ollama(self):
        if ollama_client.is_available():
            models = ollama_client.list_models()
            preview = ", ".join(models[:3]) + (" …" if len(models) > 3 else "")
            self.probe_label.setText(f"OK — {len(models)} model(s): {preview}")
            self.probe_label.setStyleSheet("color: green;")
        else:
            self.probe_label.setText("Not reachable")
            self.probe_label.setStyleSheet("color: red;")

    def save_settings(self):
        prefs["mcp_http_url"] = (
            self.url_edit.text().strip() or "http://127.0.0.1:10720"
        )
        prefs["ollama_url"] = (
            self.ollama_url_edit.text().strip() or "http://127.0.0.1:11434"
        )
        prefs["ollama_model"] = (
            self.ollama_model_edit.text().strip() or "gemma3:12b"
        )
        prefs["mcp_user_data_dir"] = self.dir_edit.text().strip()
