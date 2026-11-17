"""Transactions module router."""

from typing import Any, Dict
from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Transactions Module Status",
)
async def get_transactions_status() -> Dict[str, Any]:
    """Scaffolded endpoint confirming module availability."""
    return {"module": "transactions", "status": "scaffolded", "ready": True}
