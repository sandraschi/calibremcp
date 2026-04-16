"""
CalibreMCP Integration - UI plugin (InterfaceAction).
v2: expanded toolbar menu + right-click context menu with MCP actions.
"""

try:
    from qt.core import QMenu
except ImportError:
    from PyQt5.QtWidgets import QMenu

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.calibre_mcp_integration.dialogs.bulk_enrich_dialog import BulkEnrichDialog
from calibre_plugins.calibre_mcp_integration.dialogs.metadata_dialog import MetadataDialog
from calibre_plugins.calibre_mcp_integration.dialogs.vl_query_dialog import VLQueryDialog
from calibre_plugins.calibre_mcp_integration.dialogs.semantic_search_dialog import SemanticSearchDialog
from calibre_plugins.calibre_mcp_integration.dialogs.research_dialog import ResearchDialog


class CalibreMCPIntegrationAction(InterfaceAction):
    name = "CalibreMCP Integration"
    action_spec = (
        "MCP",
        None,
        "CalibreMCP: metadata, semantic search, research",
        "Ctrl+Shift+M",
    )
    popup_type = 1  # show dropdown arrow on toolbar button

    def genesis(self):
        try:
            icon = get_icons("images/icon.png", "CalibreMCP Integration")  # noqa: F821
            self.qaction.setIcon(icon)
        except Exception:
            pass
        self.qaction.triggered.connect(self.show_metadata_dialog)

        # ── Toolbar dropdown menu ─────────────────────────────────────────────
        self.menu = QMenu()

        m_meta = self.menu.addAction("Edit MCP Metadata")
        m_meta.triggered.connect(self.show_metadata_dialog)

        self.menu.addSeparator()

        m_sem = self.menu.addAction("Semantic Search...")
        m_sem.triggered.connect(self._show_semantic_search)

        m_vl = self.menu.addAction("Create VL from Query...")
        m_vl.triggered.connect(self._show_vl_query)

        self.menu.addSeparator()

        m_res = self.menu.addAction("Research This Book...")
        m_res.triggered.connect(self._show_research)

        self.menu.addSeparator()

        m_enrich = self.menu.addAction("Bulk Enrich...")
        m_enrich.triggered.connect(self._show_bulk_enrich)

        self.qaction.setMenu(self.menu)

        # ── Right-click context menu on book list ─────────────────────────────
        try:
            self.create_menu_action(
                self.gui.library_view.context_menu,
                "mcp_metadata",
                "MCP: Edit Metadata",
                triggered=self.show_metadata_dialog,
            )
            self.create_menu_action(
                self.gui.library_view.context_menu,
                "mcp_research",
                "MCP: Research This Book",
                triggered=self._show_research,
            )
            self.create_menu_action(
                self.gui.library_view.context_menu,
                "mcp_semantic",
                "MCP: Semantic Search",
                triggered=self._show_semantic_search,
            )
        except Exception:
            # context_menu wiring can fail on some Calibre versions — non-fatal
            pass

    def apply_settings(self):
        pass

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _require_single(self):
        """Return (book_id, mi) if exactly one book selected, else warn and return (None, None)."""
        from calibre.gui2 import info_dialog
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows:
            info_dialog(self.gui, "No selection", "Select a book first.", show=True)
            return None, None
        if len(rows) > 1:
            info_dialog(
                self.gui, "Multiple books",
                "This action works on one book at a time. Select a single book.",
                show=True,
            )
            return None, None
        row = rows[0]
        model = self.gui.library_view.model()
        book_id = model.id(row)
        mi = self.gui.current_db.get_metadata(book_id, index_is_id=True)
        return book_id, mi

    # ── Actions ───────────────────────────────────────────────────────────────

    def show_metadata_dialog(self):
        book_id, mi = self._require_single()
        if book_id is None:
            return
        try:
            icon = get_icons("images/icon.png", "CalibreMCP Integration")  # noqa: F821
        except Exception:
            icon = None
        MetadataDialog(self.gui, icon, book_id,
                       mi.title if mi else "Unknown").exec_()

    def _show_semantic_search(self):
        SemanticSearchDialog(self.gui).exec_()

    def _show_vl_query(self):
        VLQueryDialog(self.gui).exec_()

    def _show_research(self):
        book_id, mi = self._require_single()
        if book_id is None:
            return
        ResearchDialog(self.gui, book_id, mi).exec_()

    def _show_bulk_enrich(self):
        BulkEnrichDialog(self.gui).exec_()
