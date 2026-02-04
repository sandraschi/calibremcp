"""
API endpoints for managing libraries in the Calibre MCP application.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.library import LibraryCreate, LibraryResponse, LibraryStats, LibraryUpdate
from ..services.base_service import NotFoundError, ValidationError
from ..services.library_service import library_service

router = APIRouter(
    prefix="/api/v1/libraries",
    tags=["libraries"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=dict,
    summary="List all libraries",
    description="Get a paginated list of libraries with optional filtering and sorting.",
    response_description="A dictionary containing the list of libraries and pagination info",
)
async def list_libraries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: str | None = Query(None, description="Search term to filter libraries by name or path"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    sort_by: str = Query(
        "name", description="Field to sort by (name, book_count, author_count, created_at)"
    ),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Retrieve a paginated list of libraries with optional filtering and sorting.
    """
    return library_service.get_all(
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=LibraryResponse,
    summary="Create a new library",
    description="Create a new library with the given details.",
    response_description="The created library",
)
async def create_library(library: LibraryCreate, db: Session = Depends(get_db)) -> dict:
    """
    Create a new library.
    """
    try:
        return library_service.create(library)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{library_id}",
    response_model=LibraryResponse,
    summary="Get a library by ID",
    description="Retrieve a specific library by its ID.",
    responses={404: {"description": "Library not found"}},
)
async def get_library(library_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Get a library by ID.
    """
    try:
        return library_service.get_by_id(library_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{library_id}",
    response_model=LibraryResponse,
    summary="Update a library",
    description="Update an existing library's details.",
    responses={404: {"description": "Library not found"}, 400: {"description": "Invalid input"}},
)
async def update_library(
    library_id: int, library: LibraryUpdate, db: Session = Depends(get_db)
) -> dict:
    """
    Update a library's details.
    """
    try:
        return library_service.update(library_id, library)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{library_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a library",
    description="Delete a library by its ID. The library must be empty.",
    responses={
        204: {"description": "Library deleted successfully"},
        404: {"description": "Library not found"},
        400: {"description": "Cannot delete non-empty library"},
    },
)
async def delete_library(library_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a library by ID.
    """
    try:
        success = library_service.delete(library_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete library"
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{library_id}/stats",
    response_model=LibraryStats,
    summary="Get library statistics",
    description="Get detailed statistics for a specific library.",
    responses={404: {"description": "Library not found"}},
)
async def get_library_stats(library_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Get statistics for a specific library.
    """
    try:
        return library_service.get_library_stats(library_id=library_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/stats/overview",
    response_model=dict,
    summary="Get library statistics overview",
    description="Get an overview of statistics across all libraries.",
)
async def get_libraries_overview(db: Session = Depends(get_db)) -> dict:
    """
    Get an overview of statistics across all libraries.
    """
    return library_service.get_library_stats()


@router.get(
    "/{library_id}/search",
    response_model=dict,
    summary="Search within a library",
    description="Search for books and authors within a specific library.",
    responses={404: {"description": "Library not found"}},
)
async def search_library(
    library_id: int,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search for content within a specific library.
    """
    try:
        return library_service.search_across_library(
            library_id=library_id, query=query, limit=limit, offset=offset
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
