"""
Advanced feature tools for Calibre MCP server.

This module provides advanced features including:
- AI-powered enhancements
- Advanced search capabilities
- Bulk operations
- Content synchronization
- Reading analytics
- Smart collections
- Social features
"""

# Import all tool classes
from .ai_enhancements import AIEnhancementsTool
from .advanced_search import AdvancedSearchTool
from .bulk_operations import BulkOperationsTool
from .content_sync import ContentSyncTool
from .reading_analytics import ReadingAnalyticsTool
from .smart_collections import SmartCollectionsTool  # Legacy (deprecated)
from .social_features import SocialFeaturesTool

# Import portmanteau tools
from .manage_smart_collections import manage_smart_collections

# List of all available tools
__all__ = [
    "manage_smart_collections",  # Portmanteau tool (recommended)
    "AIEnhancementsTool",
    "AdvancedSearchTool",
    "BulkOperationsTool",
    "ContentSyncTool",
    "ReadingAnalyticsTool",
    "SmartCollectionsTool",  # Legacy (deprecated - use manage_smart_collections)
    "SocialFeaturesTool",
]

# Expose tools list for automatic registration
tools = [
    manage_smart_collections,  # Portmanteau tool (recommended)
    AIEnhancementsTool(),  # TODO: Migrate to portmanteau
    AdvancedSearchTool(),  # TODO: Migrate to portmanteau
    BulkOperationsTool(),  # TODO: Migrate to portmanteau
    ContentSyncTool(),  # TODO: Migrate to portmanteau
    ReadingAnalyticsTool(),  # TODO: Migrate to portmanteau
    SmartCollectionsTool(),  # Legacy (deprecated)
    SocialFeaturesTool(),  # TODO: Migrate to portmanteau
]
