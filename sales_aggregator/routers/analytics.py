from datetime import date

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from models.analytics import TopProductsResponse, CSVUploadResponse
from services.storage import storage
from services.aggregation import to_df, calculate_summary, calculate_top_products, process_csv
from services.currency import get_usd_rate
from services.aggregation import calculate_grouped_summary
router = APIRouter(prefix="/analytics", tags=["analytics"])


def filter_df(date_from: date, date_to: date, marketplace: str | None):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from не может быть больше date_to")

    sales = storage.list()
    df = to_df(sales)

    if df.empty:
        return df

    df = df[
        (df["sold_at"] >= date_from) &
        (df["sold_at"] <= date_to)
    ]

    if marketplace:
        df = df[df["marketplace"] == marketplace]

    return df


@router.get("/summary")
def summary(
    date_from: date,
    date_to: date,
    marketplace: str | None = None,
    group_by: str | None = Query(
        default=None,
        pattern="^(marketplace|date|status)$"
    ),
):
    df = filter_df(date_from, date_to, marketplace)

    if group_by:
        groups = calculate_grouped_summary(df, group_by)
        return {"groups": groups}

    return calculate_summary(df)


@router.get("/summary-usd")
async def summary_usd(
    date_from: date,
    date_to: date,
    marketplace: str | None = None,
    group_by: str | None = Query(
        default=None,
        pattern="^(marketplace|date|status)$"
    ),
):
    try:
        rate = await get_usd_rate()
    except Exception:
        raise HTTPException(status_code=503, detail="Курс валют недоступен")

    df = filter_df(date_from, date_to, marketplace)

    def convert(metrics):
        for key in ["total_revenue", "total_cost", "gross_profit", "avg_order_value"]:
            metrics[key] = round(metrics[key] / rate, 2)
        return metrics

    if group_by:
        groups = calculate_grouped_summary(df, group_by)

        for g in groups:
            g["metrics"] = convert(g["metrics"])

        return {"groups": groups}

    result = calculate_summary(df)
    return convert(result)


@router.get("/top-products", response_model=TopProductsResponse)
def top_products(
    date_from: date,
    date_to: date,
    sort_by: str = Query(default="revenue", pattern="^(revenue|quantity|profit)$"),
    limit: int = Query(default=10, ge=1, le=100),
):
    df = filter_df(date_from, date_to, marketplace=None)

    items = calculate_top_products(
        df=df,
        sort_by=sort_by,
        limit=limit,
    )

    return {"items": items}

@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    try:
        result = process_csv(file.file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid_sales = result["valid_sales"]
    errors = result["errors"]

    if valid_sales:
        storage.add(valid_sales)

    return {
        "total_rows": result["total"],
        "success_rows": len(valid_sales),
        "error_rows": len(errors),
        "errors": errors,
    }