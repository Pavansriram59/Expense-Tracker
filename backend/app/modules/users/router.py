"""Users module router."""

from typing import Any, Dict
from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Users Module Status",
)
async def get_users_status() -> Dict[str, Any]:
    """Scaffolded endpoint confirming module availability."""
    return {"module": "users", "status": "scaffolded", "ready": True}
