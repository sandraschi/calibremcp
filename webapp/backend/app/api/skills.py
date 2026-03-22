"""HTTP catalog of bundled MCP skills and related prompts (webapp UI).

For MCP-native discovery, clients should list resources (``skill://...``) from the server.
"""

from fastapi import APIRouter

router = APIRouter()

# Mirrors bundled MCP skills (src/calibre_mcp/skills) and prompts; for webapp UI only.
SKILLS = [
    {
        "id": "calibre-expert",
        "name": "Calibre expert (bundled)",
        "resource": "skill://calibre-expert/SKILL.md",
        "prompt": "calibre_mcp_guide",
    },
    {"id": "reading_recommendations", "name": "Reading Recommendations", "prompt": "reading_recommendations"},
    {"id": "library_health", "name": "Library Health", "prompt": "library_health"},
    {"id": "semantic_search", "name": "Semantic Search (Metadata RAG)", "prompt": "calibre_semantic_search"},
    {"id": "agentic_workflow", "name": "Agentic Workflow", "prompt": "calibre_mcp_guide"},
]


@router.get("/")
async def list_skills():
    """List available CalibreMCP skills and their associated prompts."""
    return {"skills": SKILLS}
