from fastapi import APIRouter, Query
from typing import List
from datetime import date
from models.sale import Sale
from services.storage import storage

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("")
def create_sales(sales: List[Sale]):
    storage.add(sales)
    return {"added": len(sales)}


@router.get("")
def get_sales(
    marketplace: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
):
    data = storage.list()

    filtered = []
    for s in data:
        if marketplace and s.marketplace != marketplace:
            continue
        if status and s.status != status:
            continue
        if date_from and s.sold_at < date_from:
            continue
        if date_to and s.sold_at > date_to:
            continue
        filtered.append(s)

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "total": len(filtered),
        "items": filtered[start:end],
    }