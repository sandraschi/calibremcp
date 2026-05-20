from calibre.customize import InterfaceActionBase


class CalibreOpsBridgePlugin(InterfaceActionBase):
    """
    CalibreOps Bridge — surfaces calibreops MCP server capabilities in Calibre GUI.
    Provides RAG search, semantic metadata search, series analysis, and synopsis
    generation backed by the calibreops MCP server (http://localhost:10720).
    """
    name                    = 'CalibreOps Bridge'
    description             = ('Surface calibreops MCP semantic search, RAG, '
                                'and series analysis in the Calibre GUI.')
    supported_platforms     = ['windows', 'osx', 'linux']
    author                  = 'sandraschi'
    version                 = (0, 1, 0)
    minimum_calibre_version = (6, 0, 0)
    actual_plugin           = 'calibre_plugins.calibreops_bridge.action:CalibreOpsBridgeAction'
    can_be_disabled         = True

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.calibreops_bridge.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.commit()
