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
from .advanced_search import AdvancedSearchTool
from .ai_enhancements import AIEnhancementsTool
from .bulk_operations import BulkOperationsTool
from .content_sync import ContentSyncTool
from .manage_bulk_operations import manage_bulk_operations
from .manage_content_sync import manage_content_sync

# Import portmanteau tools
from .manage_smart_collections import manage_smart_collections
from .reading_analytics import ReadingAnalyticsTool
from .smart_collections import SmartCollectionsTool  # Legacy (deprecated)
from .social_features import SocialFeaturesTool

# List of all available tools
__all__ = [
    "manage_smart_collections",  # Portmanteau tool (recommended)
    "manage_bulk_operations",  # Portmanteau tool
    "manage_content_sync",  # Portmanteau tool
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
    manage_bulk_operations,  # Portmanteau tool
    manage_content_sync,  # Portmanteau tool
    AIEnhancementsTool(),  # TODO: Migrate to portmanteau
    AdvancedSearchTool(),  # TODO: Migrate to portmanteau
    BulkOperationsTool(),  # TODO: Migrate to portmanteau
    ContentSyncTool(),  # TODO: Migrate to portmanteau
    ReadingAnalyticsTool(),  # TODO: Migrate to portmanteau
    SmartCollectionsTool(),  # Legacy (deprecated)
    SocialFeaturesTool(),  # TODO: Migrate to portmanteau
]
