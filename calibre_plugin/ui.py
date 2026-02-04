"""
CalibreMCP Integration - UI plugin (InterfaceAction).
"""

try:
    from qt.core import QMenu
except ImportError:
    from PyQt5.QtWidgets import QMenu

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.calibre_mcp_integration.dialogs.bulk_enrich_dialog import BulkEnrichDialog
from calibre_plugins.calibre_mcp_integration.dialogs.metadata_dialog import MetadataDialog
from calibre_plugins.calibre_mcp_integration.dialogs.vl_query_dialog import VLQueryDialog


class CalibreMCPIntegrationAction(InterfaceAction):
    name = "CalibreMCP Integration"
    action_spec = (
        "MCP Metadata",
        None,
        "Edit MCP extended metadata (translator, first published, user comments)",
        "Ctrl+Shift+M",
    )

    def genesis(self):
        icon = get_icons("images/icon.png", "CalibreMCP Integration")  # noqa: F821
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_metadata_dialog)

        # Submenu for extra actions (Bulk Enrich, VL from Query)
        self.menu = QMenu()
        m1 = self.menu.addAction("MCP Metadata")
        m1.triggered.connect(self.show_metadata_dialog)
        self.menu.addSeparator()
        m2 = self.menu.addAction("Bulk Enrich...")
        m2.triggered.connect(self._show_bulk_enrich)
        m3 = self.menu.addAction("Create VL from Query...")
        m3.triggered.connect(self._show_vl_query)
        self.qaction.setMenu(self.menu)

    def apply_settings(self):
        pass

    def _show_bulk_enrich(self):
        BulkEnrichDialog(self.gui).exec_()

    def _show_vl_query(self):
        VLQueryDialog(self.gui).exec_()

    def show_metadata_dialog(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            from calibre.gui2 import info_dialog

            info_dialog(self.gui, "No selection", "Select a book first.", show=True)
            return
        if len(rows) > 1:
            from calibre.gui2 import info_dialog

            info_dialog(
                self.gui,
                "Multiple books",
                "MCP Metadata edits one book at a time. Select a single book.",
                show=True,
            )
            return

        row = rows[0]
        model = self.gui.library_view.model()
        book_id = model.id(row)
        mi = self.gui.current_db.get_metadata(book_id, index_is_id=True)
        title = mi.title if mi else "Unknown"

        icon = get_icons("images/icon.png", "CalibreMCP Integration")  # noqa: F821
        d = MetadataDialog(self.gui, icon, book_id, title)
        d.exec_()
