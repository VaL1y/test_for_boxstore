from pydantic import BaseModel
from typing import List, Literal, Any


class SummaryResponse(BaseModel):
    total_revenue: float
    total_cost: float
    gross_profit: float
    margin_percent: float
    total_orders: int
    avg_order_value: float
    return_rate: float


class TopProductItem(BaseModel):
    product_name: str
    total_quantity: int
    total_revenue: float
    total_cost: float
    total_profit: float


SortByTopProducts = Literal["revenue", "quantity", "profit"]


class TopProductsResponse(BaseModel):
    items: List[TopProductItem]


GroupByType = Literal["marketplace", "date", "status"]


class GroupedSummaryItem(BaseModel):
    group: Any
    metrics: SummaryResponse


class GroupedSummaryResponse(BaseModel):
    groups: List[GroupedSummaryItem]


class CSVUploadError(BaseModel):
    row: int
    errors: list[str]


class CSVUploadResponse(BaseModel):
    total_rows: int
    success_rows: int
    error_rows: int
    errors: list[CSVUploadError]
