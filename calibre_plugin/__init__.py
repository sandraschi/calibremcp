"""
CalibreMCP Integration - Calibre plugin for extended metadata and MCP features.

Provides:
- Extended metadata panel (translator, first_published, user_comments)
- Direct sync with calibre_mcp_data.db - no MCP process required for basic use
- Configuration for MCP HTTP (future: bulk enrich, AI actions, VL from query)
"""

from calibre.customize import InterfaceActionBase


class CalibreMCPIntegration(InterfaceActionBase):
    name = "CalibreMCP Integration"
    description = "View and edit CalibreMCP extended metadata (translator, first published, user comments). Syncs with calibre_mcp_data.db."
    supported_platforms = ["windows", "osx", "linux"]
    author = "CalibreMCP"
    version = (1, 0, 0)
    minimum_calibre_version = (6, 0, 0)

    actual_plugin = "calibre_plugins.calibre_mcp_integration.ui:CalibreMCPIntegrationAction"

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.calibre_mcp_integration.config_widget import ConfigWidget

        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
