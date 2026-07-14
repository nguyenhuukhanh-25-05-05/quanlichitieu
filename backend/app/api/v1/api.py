from fastapi import APIRouter, Request
import httpx

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(recurring.router, prefix="/recurring", tags=["recurring"])
api_router.include_router(ws.router, prefix="/ws", tags=["ws"])

@api_router.get("/ip-geo", include_in_schema=False)
async def ip_geo():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("https://ip-api.com/json/")
            data = resp.json()
            return {"lat": data.get("lat", 10.8231), "lon": data.get("lon", 106.6297)}
    except Exception:
        return {"lat": 10.8231, "lon": 106.6297}
