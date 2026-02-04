"""
Bulk enrich dialog - placeholder for AI enrichment.
Requires Calibre webapp backend (HTTP). Full implementation pending.
"""

try:
    from qt.core import QDialog, QLabel, QPushButton, QVBoxLayout
except ImportError:
    from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from calibre_plugins.calibre_mcp_integration.mcp_client import is_available


class BulkEnrichDialog(QDialog):
    """Bulk enrich - requires webapp backend. AI integration pending."""

    def __init__(self, gui):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.setWindowTitle("MCP: Bulk Enrich")
        layout = QVBoxLayout(self)
        status = (
            "Backend available"
            if is_available()
            else "Backend not reachable (start webapp on port 13000)"
        )
        layout.addWidget(QLabel(f"Status: {status}"))
        layout.addWidget(
            QLabel(
                "Bulk enrich will AI-fill missing metadata (description, first_published, tags).\n\n"
                "Requires Calibre webapp backend running. Configure URL in Preferences -> Plugins.\n\n"
                "AI enrichment integration coming in a future release."
            )
        )
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
