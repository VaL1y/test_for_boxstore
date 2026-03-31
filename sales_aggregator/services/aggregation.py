import pandas as pd
from typing import List
from models.sale import Sale


def to_df(sales: List[Sale]) -> pd.DataFrame:
    return pd.DataFrame([s.model_dump() for s in sales])


def calculate_summary(df: pd.DataFrame):
    if df.empty:
        return {
            "total_revenue": 0,
            "total_cost": 0,
            "gross_profit": 0,
            "margin_percent": 0,
            "total_orders": 0,
            "avg_order_value": 0,
            "return_rate": 0,
        }

    delivered = df[df["status"] == "delivered"]

    revenue = (delivered["price"] * delivered["quantity"]).sum()
    cost = (delivered["cost_price"] * delivered["quantity"]).sum()

    orders = df["order_id"].nunique()

    returned = df[df["status"] == "returned"].shape[0]
    delivered_cnt = delivered.shape[0]

    return {
        "total_revenue": float(revenue),
        "total_cost": float(cost),
        "gross_profit": float(revenue - cost),
        "margin_percent": float((revenue - cost) / revenue * 100) if revenue else 0,
        "total_orders": int(orders),
        "avg_order_value": float(revenue / orders) if orders else 0,
        "return_rate": float(
            returned / (returned + delivered_cnt) * 100
        ) if (returned + delivered_cnt) else 0,
    }


def calculate_top_products(
    df: pd.DataFrame,
    sort_by: str = "revenue",
    limit: int = 10,
):
    if df.empty:
        return []

    delivered = df[df["status"] == "delivered"].copy()

    if delivered.empty:
        return []

    delivered["revenue"] = delivered["price"] * delivered["quantity"]
    delivered["cost"] = delivered["cost_price"] * delivered["quantity"]
    delivered["profit"] = delivered["revenue"] - delivered["cost"]

    grouped = (
        delivered.groupby("product_name", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            total_profit=("profit", "sum"),
        )
    )

    sort_mapping = {
        "revenue": "total_revenue",
        "quantity": "total_quantity",
        "profit": "total_profit",
    }

    sort_column = sort_mapping[sort_by]

    grouped = grouped.sort_values(by=sort_column, ascending=False).head(limit)

    records = grouped.to_dict(orient="records")

    result = []
    for row in records:
        result.append(
            {
                "product_name": row["product_name"],
                "total_quantity": int(row["total_quantity"]),
                "total_revenue": float(row["total_revenue"]),
                "total_cost": float(row["total_cost"]),
                "total_profit": float(row["total_profit"]),
            }
        )

    return result

def calculate_grouped_summary(df, group_by: str):
    if df.empty:
        return []

    if group_by == "date":
        df["group"] = df["sold_at"]
    else:
        df["group"] = df[group_by]

    result = []

    for group_value, group_df in df.groupby("group"):
        metrics = calculate_summary(group_df)

        result.append({
            "group": str(group_value),
            "metrics": metrics
        })

    return result

def process_csv(file) -> dict:
    df = pd.read_csv(file)

    required_columns = {
        "order_id",
        "marketplace",
        "product_name",
        "quantity",
        "price",
        "cost_price",
        "status",
        "sold_at",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Отсутствуют колонки: {', '.join(missing)}")

    valid_sales = []
    errors = []

    for idx, row in df.iterrows():
        row_number = idx + 2  # +2 потому что header + 0-index

        try:
            sale = Sale(**row.to_dict())
            valid_sales.append(sale)
        except Exception as e:
            errors.append({
                "row": row_number,
                "errors": [str(e)]
            })

    return {
        "valid_sales": valid_sales,
        "errors": errors,
        "total": len(df),
    }

