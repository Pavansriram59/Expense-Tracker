"""Categories module router."""

from typing import Any, Dict
from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Categories Module Status",
)
async def get_categories_status() -> Dict[str, Any]:
    """Scaffolded endpoint confirming module availability."""
    return {"module": "categories", "status": "scaffolded", "ready": True}
