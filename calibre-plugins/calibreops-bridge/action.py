"""
action.py — CalibreOps Bridge InterfaceAction

Wires the plugin into Calibre's toolbar and context menus.
The actual UI lives in ui/search_dialog.py.

Phase 0 stub: loads cleanly, shows a placeholder dialog on click.
"""
from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import info_dialog


class CalibreOpsBridgeAction(InterfaceAction):
    name = 'CalibreOps Bridge'
    action_spec = (
        'CalibreOps',        # toolbar label
        None,                 # icon resource path — set in genesis()
        'Search library via calibreops MCP',  # tooltip
        None,                 # keyboard shortcut
    )
    popup_type = 0            # 0 = plain button, 1 = menu button
    action_add_menu = False

    def genesis(self):
        """Called once after plugin is loaded. Set up icon and connect signals."""
        # TODO: replace with actual icon once images/calibreops.png exists
        # self.qaction.setIcon(get_icons('images/calibreops.png'))
        self.qaction.triggered.connect(self.show_search_dialog)

    def show_search_dialog(self):
        """Open the main CalibreOps search dialog."""
        # Phase 0 stub — replace with real SearchDialog in Phase 1
        info_dialog(
            self.gui,
            'CalibreOps Bridge',
            'Plugin loaded successfully.\n\n'
            'SearchDialog not yet implemented — Phase 1 work.\n\n'
            f'calibreops endpoint: {self._get_server_url()}',
            show=True,
        )

    def _get_server_url(self):
        from calibre_plugins.calibreops_bridge.config import prefs
        return prefs['server_url']

    def library_changed(self, db):
        """Called when the user switches libraries."""
        pass

    def shutting_down(self):
        """Called when Calibre is closing."""
        pass
