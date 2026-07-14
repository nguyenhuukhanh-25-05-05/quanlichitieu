from fastapi import APIRouter
from app.api.v1.endpoints import auth, transactions, budgets, reports, ws, recurring

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(recurring.router, prefix="/recurring", tags=["recurring"])
api_router.include_router(ws.router, prefix="/ws", tags=["ws"])
