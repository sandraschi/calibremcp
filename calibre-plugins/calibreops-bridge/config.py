"""
config.py — CalibreOps Bridge preferences

JSONConfig-backed preferences with a Calibre ConfigWidget for the
Preferences → Plugins → CalibreOps Bridge → Customize dialog.
"""
from calibre.utils.config import JSONConfig
from calibre.gui2 import QApplication
from calibre.gui2.preferences import ConfigWidgetBase, setting

# Module-level prefs object — import this everywhere you need settings
prefs = JSONConfig('plugins/calibreops_bridge')
prefs.defaults['server_url'] = 'http://localhost:10720'  # calibre-mcp webapp backend
prefs.defaults['timeout']    = 10
prefs.defaults['result_limit'] = 20


class ConfigWidget(ConfigWidgetBase):
    """
    Preferences dialog widget.
    Shown via Preferences → Plugins → CalibreOps Bridge → Customize.
    """

    def setupUi(self, *args):
        # Lazy import Qt to avoid import errors outside Calibre's interpreter
        from calibre.gui2 import QLabel, QLineEdit, QSpinBox, QFormLayout, QWidget

        layout = QFormLayout(self)
        self.setLayout(layout)

        self.url_edit = QLineEdit(self)
        self.url_edit.setText(prefs['server_url'])
        layout.addRow(QLabel('calibreops server URL:'), self.url_edit)

        self.timeout_spin = QSpinBox(self)
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(prefs['timeout'])
        layout.addRow(QLabel('Timeout (seconds):'), self.timeout_spin)

        self.limit_spin = QSpinBox(self)
        self.limit_spin.setRange(1, 100)
        self.limit_spin.setValue(prefs['result_limit'])
        layout.addRow(QLabel('Result limit:'), self.limit_spin)

    def commit(self):
        prefs['server_url']   = self.url_edit.text().strip()
        prefs['timeout']      = self.timeout_spin.value()
        prefs['result_limit'] = self.limit_spin.value()
