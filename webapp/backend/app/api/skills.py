"""Skills API: list CalibreMCP skills and workflows."""

from fastapi import APIRouter

router = APIRouter()

# Skills defined in repo skills/; exposed for webapp
SKILLS = [
    {"id": "reading_recommendations", "name": "Reading Recommendations", "prompt": "reading_recommendations"},
    {"id": "library_health", "name": "Library Health", "prompt": "library_health"},
    {"id": "semantic_search", "name": "Semantic Search (Metadata RAG)", "prompt": "calibre_semantic_search"},
    {"id": "agentic_workflow", "name": "Agentic Workflow", "prompt": "calibre_mcp_guide"},
]


@router.get("/")
async def list_skills():
    """List available CalibreMCP skills and their associated prompts."""
    return {"skills": SKILLS}
