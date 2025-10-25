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
from typing import List

# Import all tool classes
from .ai_enhancements import AIEnhancementsTool
from .advanced_search import AdvancedSearchTool
from .bulk_operations import BulkOperationsTool
from .content_sync import ContentSyncTool
from .reading_analytics import ReadingAnalyticsTool
from .smart_collections import SmartCollectionsTool
from .social_features import SocialFeaturesTool

# List of all available tools
__all__ = [
    'AIEnhancementsTool',
    'AdvancedSearchTool',
    'BulkOperationsTool',
    'ContentSyncTool',
    'ReadingAnalyticsTool',
    'SmartCollectionsTool',
    'SocialFeaturesTool'
]

# Expose tools list for automatic registration
tools = [
    AIEnhancementsTool(),
    AdvancedSearchTool(),
    BulkOperationsTool(),
    ContentSyncTool(),
    ReadingAnalyticsTool(),
    SmartCollectionsTool(),
    SocialFeaturesTool()
]
