"""
Rag Context - API Router
Presentation Layer (Clean Architecture)
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_items():
    """List items endpoint - To be implemented"""
    return {"message": "Rag list endpoint"}


@router.post("/")
async def create_item():
    """Create item endpoint - To be implemented"""
    return {"message": "Rag create endpoint"}
