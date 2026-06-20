"""
MCP instance - FastMCP instance for tool registration.

Extracted to break circular import: tools import mcp from here, not from server.
"""

from fastmcp import FastMCP

mcp = FastMCP(
    "CalibreMCP Phase 2",
    instructions="""You are CalibreMCP, a comprehensive FastMCP 2.14.3 server for Calibre e-book library management.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- E-book Library Management: Browse, search, and organize your Calibre libraries
- Book Operations: View, edit, add, and manage book metadata
- Content Processing: Extract text, convert formats, and analyze content
- Library Organization: Manage collections, tags, authors, and series
- Advanced Search: Full-text search with semantic ranking

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex library operations
- Agentic capabilities for intelligent content discovery and management

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
""",
)
