"""
Configuration widget for CalibreMCP Integration plugin.
"""

from calibre_plugins.calibre_mcp_integration.config import prefs

try:
    from qt.core import QGroupBox, QLabel, QLineEdit, QVBoxLayout, QWidget
except ImportError:
    from PyQt5.Qt import QGroupBox, QLabel, QLineEdit, QVBoxLayout, QWidget


class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        g1 = QGroupBox("MCP User Data Directory (optional)")
        g1_layout = QVBoxLayout()
        self.dir_edit = QLineEdit(self)
        self.dir_edit.setPlaceholderText("Leave empty for default (APPDATA/calibre-mcp)")
        self.dir_edit.setText(prefs.get("mcp_user_data_dir", ""))
        g1_layout.addWidget(QLabel("Override location of calibre_mcp_data.db:"))
        g1_layout.addWidget(self.dir_edit)
        g1.setLayout(g1_layout)
        layout.addWidget(g1)

        g2 = QGroupBox("MCP HTTP URL (for AI features)")
        g2_layout = QVBoxLayout()
        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText("http://127.0.0.1:13000")
        self.url_edit.setText(prefs.get("mcp_http_url", "http://127.0.0.1:13000"))
        g2_layout.addWidget(QLabel("CalibreMCP HTTP endpoint (when running):"))
        g2_layout.addWidget(self.url_edit)
        g2.setLayout(g2_layout)
        layout.addWidget(g2)

        layout.addStretch()

    def save_settings(self):
        prefs["mcp_user_data_dir"] = self.dir_edit.text().strip()
        prefs["mcp_http_url"] = self.url_edit.text().strip() or "http://127.0.0.1:13000"
