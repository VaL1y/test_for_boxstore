from fastapi import FastAPI
from routers import sales, analytics

app = FastAPI(title="Sales Aggregator")

app.include_router(sales.router)
app.include_router(analytics.router)