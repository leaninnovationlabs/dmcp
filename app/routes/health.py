from fastapi import APIRouter
from ..core.responses import create_success_response
from ..models.schemas import StandardAPIResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=StandardAPIResponse)
async def health_check():
    """Health check endpoint to verify server status."""
    data = {"status": "healthy", "message": "DMCP server is running"}
    return create_success_response(data=data) 