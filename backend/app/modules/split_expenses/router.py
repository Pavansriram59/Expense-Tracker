"""Split Expenses module router."""

from typing import Any, Dict
from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Split Expenses Module Status",
)
async def get_split_expenses_status() -> Dict[str, Any]:
    """Scaffolded endpoint confirming module availability."""
    return {"module": "split_expenses", "status": "scaffolded", "ready": True}
